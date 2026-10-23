
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform

# Project paths
ROOT = Path(__file__).resolve().parents[1]

INPUT_CSV = ROOT / "data" / "processed" / "pune_buildings_srtm.csv"
NDVI_RASTER = ROOT / "data" / "processed" / "pune_ndvi_2025.tif"
OUTPUT_CSV = ROOT / "data" / "processed" / "pune_buildings_ndvi.csv"

def main():
    # Validate input files
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Building CSV not found: {INPUT_CSV}")

    if not NDVI_RASTER.exists():
        raise FileNotFoundError(f"NDVI raster not found: {NDVI_RASTER}")

    # Load building records
    df = pd.read_csv(INPUT_CSV)

    required_columns = {"latitude", "longitude"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    print(f"Buildings loaded: {len(df):,}")

    # Initialize NDVI output with missing values
    ndvi_values = np.full(len(df), np.nan, dtype=float)

    valid_coords = (
        df["latitude"].notna()
        & df["longitude"].notna()
        & df["latitude"].between(-90, 90)
        & df["longitude"].between(-180, 180)
    )

    valid_indices = np.flatnonzero(valid_coords.to_numpy())

    with rasterio.open(NDVI_RASTER) as src:
        print(f"Raster CRS: {src.crs}")
        print(f"Raster resolution: {src.res}")
        print(f"Raster NoData value: {src.nodata}")

        if src.crs is None:
            raise ValueError("The NDVI raster has no CRS.")

        # Convert building coordinates from WGS84 to raster CRS.
        longitudes = df.loc[valid_coords, "longitude"].astype(float).tolist()
        latitudes = df.loc[valid_coords, "latitude"].astype(float).tolist()

        xs, ys = transform(
            "EPSG:4326",
            src.crs,
            longitudes,
            latitudes,
        )

        coordinates = list(zip(xs, ys))

        # Sample NDVI at each building centroid.
        for index, sample in zip(
            valid_indices,
            src.sample(coordinates, indexes=1, masked=True),
        ):
            value = sample[0]

            if np.ma.is_masked(value):
                continue

            value = float(value)

            if np.isfinite(value) and -1.0 <= value <= 1.0:
                ndvi_values[index] = value

    # Add NDVI without removing any building records.
    df["ndvi_2025"] = ndvi_values

    # Save the enriched building dataset.
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    # Report quality checks.
    valid_count = int(df["ndvi_2025"].notna().sum())
    missing_count = int(df["ndvi_2025"].isna().sum())

    print("\nNDVI EXTRACTION COMPLETE")
    print(f"Total buildings: {len(df):,}")
    print(f"Valid NDVI values: {valid_count:,}")
    print(f"Missing NDVI values: {missing_count:,}")
    print(f"Output saved to: {OUTPUT_CSV}")

    if valid_count:
        print("\nNDVI statistics:")
        print(df["ndvi_2025"].describe())

if __name__ == "__main__":
    main()
