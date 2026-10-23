
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "processed"

BUILDINGS_FILE = DATA_DIR / "pune_buildings_ndvi.csv"
NASA_FILE = DATA_DIR / "pune_nasa_power.csv"
OUTPUT_FILE = DATA_DIR / "pune_rooftop_solar_master.csv"


def main():
    # 1. Load the building-level dataset and NASA POWER summary.
    buildings = pd.read_csv(BUILDINGS_FILE)
    nasa = pd.read_csv(NASA_FILE)

    print(f"Building records loaded: {len(buildings):,}")
    print(f"NASA POWER records loaded: {len(nasa):,}")

    # 2. Validate the inputs before combining them.
    if len(nasa) != 1:
        raise ValueError(
            "Expected exactly one annual NASA POWER climatology row."
        )

    if "building_id" not in buildings.columns:
        raise ValueError("building_id column is missing.")

    if buildings["building_id"].duplicated().any():
        raise ValueError("Duplicate building_id values found.")

    climate_columns = [
        "ghi_kwh_m2_day",
        "dni_kwh_m2_day",
        "temperature_c",
        "relative_humidity_pct",
        "wind_speed_m_s",
    ]

    missing = set(climate_columns) - set(nasa.columns)
    if missing:
        raise ValueError(
            f"Missing NASA POWER columns: {sorted(missing)}"
        )

    # 3. Attach city-level climate context to each building.
    # Do not join using coordinates: NASA POWER represents Pune
    # using a single reference point, not individual building points.
    for column in climate_columns:
        buildings[column] = nasa[column].iloc[0]

    # 4. Add dataset metadata.
    buildings["study_area"] = "Pune, Maharashtra, India"
    buildings["ndvi_source_year"] = 2025

    # 5. Save the master dataset.
    buildings.to_csv(OUTPUT_FILE, index=False)

    # 6. Run basic quality checks.
    result = pd.read_csv(OUTPUT_FILE)

    print("\nMASTER DATASET CREATED")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows: {len(result):,}")
    print(f"Columns: {len(result.columns)}")
    print(f"Unique building IDs: {result['building_id'].nunique():,}")
    print(
        "Duplicate rows by building ID:",
        int(result["building_id"].duplicated().sum()),
    )

    print("\nMissing values in important features:")
    check_columns = [
        "roof_area_m2",
        "elevation_m",
        "terrain_slope_deg",
        "terrain_aspect_deg",
        "ndvi_2025",
    ]
    print(result[check_columns].isna().sum().to_string())

    print("\nNASA POWER values attached to buildings:")
    print(result[climate_columns].nunique().to_string())

    print("\nFirst five rows:")
    print(result.head().to_string(index=False))


if __name__ == "__main__":
    main()
