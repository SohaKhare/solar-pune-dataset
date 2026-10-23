
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "pune_rooftop_solar_master.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "pune_rooftop_solar_clean.csv"

def main():
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    original_rows = len(df)

    # Normalize optional numeric attributes.
    numeric_columns = [
        "building_levels",
        "height_m",
        "roof_orientation",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Validate core identifiers and coordinates.
    assert df["building_id"].notna().all(), "Missing building IDs"
    assert df["building_id"].is_unique, "Duplicate building IDs"
    assert df["latitude"].between(-90, 90).all(), "Invalid latitude"
    assert df["longitude"].between(-180, 180).all(), "Invalid longitude"
    assert (df["roof_area_m2"] > 0).all(), "Non-positive roof areas"

    # Flag unusually large footprints; retain them.
    df["area_quality_flag"] = "normal"
    df.loc[df["roof_area_m2"] > 5000, "area_quality_flag"] = "large_building"

    # Save a cleaned copy without changing the master CSV.
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nDATASET VALIDATION COMPLETE")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Rows before cleaning: {original_rows:,}")
    print(f"Rows after cleaning:  {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Unique building IDs: {df['building_id'].nunique():,}")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    print("\nNumeric column types:")
    print(df[numeric_columns].dtypes.to_string())

    print("\nMissing values:")
    print(df.isna().sum().to_string())

    print("\nArea quality flags:")
    print(df["area_quality_flag"].value_counts().to_string())

    print("\nLargest 10 footprints for manual inspection:")
    print(
        df.nlargest(10, "roof_area_m2")[
            ["building_id", "osm_element", "osm_id",
             "building_type", "roof_area_m2", "area_quality_flag"]
        ].to_string(index=False)
    )

if __name__ == "__main__":
    main()
