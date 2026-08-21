from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio

import pandas as pd

BUILDINGS_INPUT = Path(
    "data/processed/pune_buildings.csv"
)

TERRAIN_RASTER = Path(
    "data/processed/pune_terrain.tif"
)

OUTPUT = Path(
    "data/processed/pune_buildings_srtm.csv"
)


# Load buildings

print("Loading building dataset...")

buildings = pd.read_csv(
    BUILDINGS_INPUT
)

print(
    f"Buildings loaded: "
    f"{len(buildings):,}"
)


# Create building points

geometry = gpd.points_from_xy(
    buildings["longitude"],
    buildings["latitude"]
)

points = gpd.GeoDataFrame(
    buildings,
    geometry=geometry,
    crs="EPSG:4326"
)


# Reproject to SRTM CRS

print(
    "Reprojecting building coordinates..."
)

points = points.to_crs(
    "EPSG:32643"
)


# Open terrain raster

print(
    "Opening terrain raster..."
)

with rasterio.open(
    TERRAIN_RASTER
) as src:

    print(
        f"Raster CRS: {src.crs}"
    )

    print(
        f"Raster bands: {src.count}"
    )

    # Generate coordinates for sampling

    coordinates = [
        (point.x, point.y)
        for point in points.geometry
    ]

    # Sample all three bands

    print(
        "Sampling terrain values..."
    )

    sampled = list(
        src.sample(
            coordinates
        )
    )


# Convert samples to array

sampled = np.asarray(
    sampled,
    dtype=np.float32
)


# Add terrain features

points["elevation_m"] = sampled[:, 0]

points["terrain_slope_deg"] = sampled[:, 1]

points["terrain_aspect_deg"] = sampled[:, 2]


# Remove geometry

result = pd.DataFrame(
    points.drop(
        columns="geometry"
    )
)


# Handle NoData

nodata_mask = (
    result["elevation_m"] == -9999
)

result.loc[
    nodata_mask,
    [
        "elevation_m",
        "terrain_slope_deg",
        "terrain_aspect_deg",
    ]
] = np.nan


# Save

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    OUTPUT,
    index=False
)


# Validation

print("\n========================================")
print("BUILDING SRTM EXTRACTION COMPLETE")
print("========================================")

print(
    f"Output: {OUTPUT}"
)

print(
    f"Building records: "
    f"{len(result):,}"
)

print("\nMissing terrain values:")

print(
    result[
        [
            "elevation_m",
            "terrain_slope_deg",
            "terrain_aspect_deg",
        ]
    ].isna().sum()
)

print("\nTerrain statistics:")

print(
    result[
        [
            "elevation_m",
            "terrain_slope_deg",
            "terrain_aspect_deg",
        ]
    ].describe()
)