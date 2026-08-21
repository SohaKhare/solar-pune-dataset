from pathlib import Path

import numpy as np
import rasterio


INPUT = Path(
    "data/processed/pune_srtm_utm43.tif"
)

OUTPUT = Path(
    "data/processed/pune_terrain.tif"
)


# Open DEM

print("Loading reprojected SRTM DEM...")

with rasterio.open(INPUT) as src:

    elevation = src.read(1).astype(
        np.float32
    )

    profile = src.profile.copy()

    transform = src.transform

    nodata = src.nodata


# Identify valid cells

valid = elevation != nodata

print(
    f"Valid DEM cells: "
    f"{valid.sum():,}"
)

print(
    f"NoData cells: "
    f"{(~valid).sum():,}"
)


# Calculate terrain gradients

# Pixel dimensions in metres
pixel_width = abs(transform.a)
pixel_height = abs(transform.e)

print(
    f"\nPixel size: "
    f"{pixel_width:.2f} m × "
    f"{pixel_height:.2f} m"
)


# Replace NoData temporarily with NaN
dem = elevation.copy()

dem[~valid] = np.nan


# Calculate elevation gradients
dz_dy, dz_dx = np.gradient(
    dem,
    pixel_height,
    pixel_width
)


# Calculate slope

slope = np.degrees(
    np.arctan(
        np.sqrt(
            dz_dx ** 2 +
            dz_dy ** 2
        )
    )
)


# Calculate aspect

aspect = np.degrees(
    np.arctan2(
        -dz_dx,
        dz_dy
    )
)

# Convert to compass degrees
aspect = (
    90.0 - aspect
) % 360.0


# Handle NoData

slope[~valid] = np.nan
aspect[~valid] = np.nan


# Save terrain raster

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

terrain = np.stack(
    [
        elevation,
        slope.astype(np.float32),
        aspect.astype(np.float32),
    ]
)


profile.update(
    {
        "count": 3,
        "dtype": "float32",
        "nodata": np.nan,
        "compress": "lzw",
    }
)


with rasterio.open(
    OUTPUT,
    "w",
    **profile
) as dst:

    dst.write(terrain)

    dst.set_band_description(1, "elevation_m")

    dst.set_band_description(2, "terrain_slope_deg")

    dst.set_band_description(3, "terrain_aspect_deg")


# Statistics

print("\n========================================")
print("TERRAIN DERIVATION COMPLETE")
print("========================================")

print(
    f"Output: {OUTPUT}"
)

valid_elevation = elevation[valid]

print("\nElevation:")
print(f"  Min: {valid_elevation.min():.2f} m")
print(f"  Max: {valid_elevation.max():.2f} m")
print(f"  Mean: {valid_elevation.mean():.2f} m")
print("\nSlope:")
print(f"  Min: {np.nanmin(slope):.2f}°")
print(f"  Max: {np.nanmax(slope):.2f}°")
print(f"  Mean: {np.nanmean(slope):.2f}°")

print("\nAspect:")
print(f"  Min: {np.nanmin(aspect):.2f}°")
print(f"  Max: {np.nanmax(aspect):.2f}°")
print(f"  Mean: {np.nanmean(aspect):.2f}°")