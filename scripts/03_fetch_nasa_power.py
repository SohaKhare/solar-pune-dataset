import json
from pathlib import Path

import pandas as pd
import requests


# Configuration

LATITUDE = 18.5204
LONGITUDE = 73.8567

OUTPUT_DIR = Path("data/raw/nasa")
OUTPUT_JSON = OUTPUT_DIR / "pune_nasa_power_climatology.json"
OUTPUT_CSV = Path("data/processed/pune_nasa_power.csv")

BASE_URL = (
    "https://power.larc.nasa.gov/api/temporal/"
    "climatology/point"
)


# NASA POWER parameters

PARAMETERS = [
    "ALLSKY_SFC_SW_DWN",
    "ALLSKY_SFC_SW_DNI",
    "T2M",
    "RH2M",
    "WS10M",
]


# Month mapping

MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
    "ANN": 13,
}


# Create output directories

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

OUTPUT_CSV.parent.mkdir(
    parents=True,
    exist_ok=True
)


# Build API request

params = {
    "parameters": ",".join(PARAMETERS),
    "community": "RE",
    "longitude": LONGITUDE,
    "latitude": LATITUDE,
    "format": "JSON",
}

print("Requesting NASA POWER climatology...")
print(f"Latitude:  {LATITUDE}")
print(f"Longitude: {LONGITUDE}")
print(
    f"Parameters: {', '.join(PARAMETERS)}"
)


# --------------------------------------------------
# Make API request
# --------------------------------------------------

response = requests.get(
    BASE_URL,
    params=params,
    timeout=60
)

response.raise_for_status()

data = response.json()


# --------------------------------------------------
# Save raw response
# --------------------------------------------------

with open(
    OUTPUT_JSON,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        data,
        f,
        indent=2
    )

print("\nRaw response saved to:")
print(OUTPUT_JSON)


# --------------------------------------------------
# Extract parameter data
# --------------------------------------------------

parameter_data = (
    data["properties"]["parameter"]
)

print("\nParameters returned:")

for parameter in parameter_data:
    print(f"  {parameter}")


# --------------------------------------------------
# Convert API response to records
# --------------------------------------------------

records = []

for parameter_name, monthly_values in parameter_data.items():

    for month_name, value in monthly_values.items():

        month_key = month_name.upper()

        if month_key not in MONTHS:
            print(
                f"Warning: unexpected period "
                f"'{month_name}' for "
                f"'{parameter_name}'"
            )
            continue

        records.append({
            "month": MONTHS[month_key],
            "month_name": month_key,
            "parameter": parameter_name,
            "value": value,
        })


df_long = pd.DataFrame(records)


# --------------------------------------------------
# Convert to wide format
# --------------------------------------------------

df = df_long.pivot(
    index=["month", "month_name"],
    columns="parameter",
    values="value"
).reset_index()


# --------------------------------------------------
# Sort chronologically
# --------------------------------------------------

df = df.sort_values(
    "month"
).reset_index(drop=True)

# --------------------------------------------------
# Save monthly climatology
# --------------------------------------------------

MONTHLY_OUTPUT = (
    Path("data/processed")
    / "pune_nasa_power_monthly.csv"
)

monthly_df = df[
    df["month_name"] != "ANN"
].copy()

monthly_df = monthly_df.rename(
    columns={
        "ALLSKY_SFC_SW_DWN":
            "ghi_kwh_m2_day",

        "ALLSKY_SFC_SW_DNI":
            "dni_kwh_m2_day",

        "RH2M":
            "relative_humidity_pct",

        "T2M":
            "temperature_c",

        "WS10M":
            "wind_speed_m_s",
    }
)

monthly_df = monthly_df[
    [
        "month",
        "month_name",
        "ghi_kwh_m2_day",
        "dni_kwh_m2_day",
        "temperature_c",
        "relative_humidity_pct",
        "wind_speed_m_s",
    ]
]

monthly_df.to_csv(
    MONTHLY_OUTPUT,
    index=False
)

print(
    f"\nMonthly climatology saved to:"
)
print(MONTHLY_OUTPUT)

# --------------------------------------------------
# Extract NASA POWER annual values
# --------------------------------------------------

annual_rows = df[
    df["month_name"] == "ANN"
]

if annual_rows.empty:
    raise ValueError(
        "NASA POWER response did not contain "
        "an ANN annual record."
    )

annual_row = annual_rows.iloc[0]


# --------------------------------------------------
# Build annual dataset
# --------------------------------------------------

annual = {
    "latitude": LATITUDE,
    "longitude": LONGITUDE,

    "ghi_kwh_m2_day": annual_row[
        "ALLSKY_SFC_SW_DWN"
    ],

    "dni_kwh_m2_day": annual_row[
        "ALLSKY_SFC_SW_DNI"
    ],

    "temperature_c": annual_row[
        "T2M"
    ],

    "relative_humidity_pct": annual_row[
        "RH2M"
    ],

    "wind_speed_m_s": annual_row[
        "WS10M"
    ],
}


annual_df = pd.DataFrame(
    [annual]
)


# --------------------------------------------------
# Save processed annual dataset
# --------------------------------------------------

annual_df.to_csv(
    OUTPUT_CSV,
    index=False
)


# --------------------------------------------------
# Display results
# --------------------------------------------------

print("\n========================================")
print("NASA POWER PROCESSING COMPLETE")
print("========================================")

print("\nAnnual climatological values:")

print(
    annual_df.to_string(
        index=False
    )
)

print("\nMonthly values:")

print(
    df.to_string(
        index=False
    )
)

print("\nProcessed output saved to:")
print(OUTPUT_CSV)