
# installed requests pandas using " py -m pip install requests pandas "
import requests
import pandas as pd

import os
import json

# BLS API url endpoint
url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# sectors I selected and their BLS seriesIDs
series = {
    "Manufacturing": "CES3000000001",
    "Information": "CES5000000001",
    "Leisure & Hospitality": "CES7000000001",
    "Construction": "CES2000000001"
}

# last two decades
apidata = {
    "seriesid": list(series.values()),
    "startyear": "2006",
    "endyear": "2025"
}

# Create data directories if they don't exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# actual request to the BLS API, serializes apidata dictionary into JSON string
response = requests.post(url, json=apidata)
response.raise_for_status()

data = response.json()

# Check if the API request was successful
if data["status"] != "REQUEST_SUCCEEDED":
    raise Exception(data["message"])

# Save original, unmodified API response
with open("data/raw/employment_data.json", "w") as file:
    json.dump(data, file, indent=4)

employment_data = []

for result in data["Results"]["series"]:
    series_id = result["seriesID"]

    # find the sector associated with the seriesID
    sector = None
    for name, sid in series.items():
        if sid == series_id:
            sector = name
            break

    for item in result["data"]:

        # keep monthly data and ignore annual averages
        if item["period"].startswith("M") and item["period"] != "M13":
            employment_data.append({
                "Date": f'{item["year"]}-{item["period"][1:]}',
                "Sector": sector,
                "Series_ID": series_id,
                "Employment_Thousands": float(item["value"])
            })

# Convert data into a Pandas DataFrame
df = pd.DataFrame(employment_data)

# Sort by date and sector
df["Date"] = pd.to_datetime(df["Date"])
df = df.sort_values(["Date", "Sector"])

# Export cleaned data to CSV
df.to_csv("data/processed/employment_data.csv", index=False)

print(df.head())
print("\nOriginal API data saved to data/raw/employment_data.json")
print("Processed data saved to data/processed/employment_data.csv")
print("Total records:", len(df))
