import os
import time

import geopandas as gpd
import osmnx as ox
from shapely.geometry import box

# Pune bounding box
# west, south, east, north
PUNE_BOUNDS = (73.75, 18.42, 73.98, 18.65)

OUTPUT_DIR = "data/raw/osm"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Number of rows and columns in the grid
ROWS = 2
COLS = 2

west, south, east, north = PUNE_BOUNDS

lon_step = (east - west) / COLS
lat_step = (north - south) / ROWS

for row in range(ROWS):
    for col in range(COLS):

        tile_id = f"tile_{row}_{col}"

        tile_west = west + col * lon_step
        tile_east = west + (col + 1) * lon_step

        tile_south = south + row * lat_step
        tile_north = south + (row + 1) * lat_step

        polygon = box(
            tile_west,
            tile_south,
            tile_east,
            tile_north
        )

        print(
            f"\nDownloading {tile_id}: "
            f"{tile_west:.4f}, {tile_south:.4f} → "
            f"{tile_east:.4f}, {tile_north:.4f}"
        )

        try:
            buildings = ox.features_from_polygon(
                polygon,
                tags={"building": True}
            )

            output_path = os.path.join(
                OUTPUT_DIR,
                f"{tile_id}.geojson"
            )

            buildings.to_file(
                output_path,
                driver="GeoJSON"
            )

            print(
                f"Downloaded {len(buildings):,} features."
            )

            print(f"Saved: {output_path}")

        except Exception as e:
            print(f"FAILED: {tile_id}")
            print(e)

        # Avoid hammering the Overpass API
        time.sleep(5)

print("\nFinished downloading all tiles.")