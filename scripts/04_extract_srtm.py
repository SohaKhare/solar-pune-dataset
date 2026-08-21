import os
from pathlib import Path

import requests
import rasterio
from dotenv import load_dotenv


# Configuration

WEST = 73.75
SOUTH = 18.42
EAST = 73.98
NORTH = 18.65

OUTPUT_DIR = Path("data/raw/srtm")
OUTPUT_FILE = OUTPUT_DIR / "pune_srtm.tif"

# OpenTopography Global DEM API
API_URL = "https://portal.opentopography.org/API/globaldem"



# Load API key

load_dotenv()

API_KEY = os.getenv(
    "OPENTOPOGRAPHY_API_KEY"
)

if not API_KEY:
    raise RuntimeError(
        "OPENTOPOGRAPHY_API_KEY not found. "
        "Add it to your .env file."
    )


# Create output directory

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Request parameters

params = {
    "demtype": "SRTMGL1",
    "south": SOUTH,
    "north": NORTH,
    "west": WEST,
    "east": EAST,
    "outputFormat": "GTiff",
    "API_Key": API_KEY,
}


print("Downloading SRTM DEM...")
print(
    f"Bounds: "
    f"{WEST}, {SOUTH} → {EAST}, {NORTH}"
)


# Download

response = requests.get(
    API_URL,
    params=params,
    timeout=300
)

response.raise_for_status()


# Save GeoTIFF

with open(
    OUTPUT_FILE,
    "wb"
) as file:

    file.write(
        response.content
    )


print(
    f"\nSaved SRTM DEM to:"
)
print(OUTPUT_FILE)


# Validate raster

with rasterio.open(
    OUTPUT_FILE
) as src:

    print("\n========================================")
    print("SRTM VALIDATION")
    print("========================================")

    print(f"CRS: {src.crs}")

    print(f"Width: {src.width}")

    print(f"Height: {src.height}")

    print(f"Resolution: {src.res}")

    print(f"Bands: {src.count}")

    print(f"Bounds: {src.bounds}")

    print(f"Data type: {src.dtypes[0]}")