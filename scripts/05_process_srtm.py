from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import (
    calculate_default_transform,
    reproject,
    Resampling,
)


INPUT = Path("data/raw/srtm/pune_srtm.tif")
OUTPUT = Path("data/processed/pune_srtm_utm43.tif")

TARGET_CRS = "EPSG:32643"
NODATA_VALUE = -9999.0


# Validate input

if not INPUT.exists():
    raise FileNotFoundError(f"SRTM file not found: {INPUT}")


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)


print("Loading SRTM DEM...")

with rasterio.open(INPUT) as src:

    print(f"Original CRS: {src.crs}")
    print(f"Original resolution: {src.res}")
    print(
        f"Original size: "
        f"{src.width} x {src.height}"
    )
    print(f"Original NoData value: {src.nodata}")

    # Calculate target raster geometry

    transform, width, height = (
        calculate_default_transform(
            src.crs,
            TARGET_CRS,
            src.width,
            src.height,
            *src.bounds
        )
    )

    print("\nReprojecting to UTM Zone 43N...")
    print(f"Target CRS: {TARGET_CRS}")
    print(
        f"Target size: "
        f"{width} x {height}"
    )

    # Create destination raster

    destination = np.full(
        (height, width),
        NODATA_VALUE,
        dtype=np.float32
    )

    # Reproject while preserving NoData

    reproject(
        source=rasterio.band(src, 1),
        destination=destination,
        src_transform=src.transform,
        src_crs=src.crs,
        src_nodata=src.nodata,
        dst_transform=transform,
        dst_crs=TARGET_CRS,
        dst_nodata=NODATA_VALUE,
        resampling=Resampling.bilinear
    )

    # Update metadata

    profile = src.profile.copy()

    profile.update(
        {
            "crs": TARGET_CRS,
            "transform": transform,
            "width": width,
            "height": height,
            "dtype": "float32",
            "count": 1,
            "nodata": NODATA_VALUE,
            "compress": "lzw",
        }
    )

# Save reprojected DEM

print("\nSaving reprojected DEM...")

with rasterio.open(
    OUTPUT,
    "w",
    **profile
) as dst:

    dst.write(
        destination,
        1
    )


# Calculate valid elevation statistics

valid = destination[
    destination != NODATA_VALUE
]

print("\n========================================")
print("SRTM REPROJECTION COMPLETE")
print("========================================")

print(f"Output: {OUTPUT}")

print(
    f"Elevation minimum: "
    f"{valid.min():.2f} m"
)

print(
    f"Elevation maximum: "
    f"{valid.max():.2f} m"
)

print(
    f"Elevation mean: "
    f"{valid.mean():.2f} m"
)

print(
    f"Valid cells: "
    f"{len(valid):,}"
)

print(
    f"NoData cells: "
    f"{destination.size - len(valid):,}"
)