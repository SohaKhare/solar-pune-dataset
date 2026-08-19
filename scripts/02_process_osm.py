from pathlib import Path

import geopandas as gpd
import pandas as pd

INPUT_DIR = Path("data/raw/osm")
OUTPUT = Path("data/processed/pune_buildings.csv")

print("Loading OSM tiles...")

files = sorted(INPUT_DIR.glob("tile_*.geojson"))

if not files:
    raise FileNotFoundError("No OSM tile files found.")

frames = []

for file in files:
    print(f"Loading {file}...")

    gdf = gpd.read_file(file)

    print(f"  {len(gdf):,} features")

    frames.append(gdf)

# Combine all tiles
buildings = gpd.GeoDataFrame(
    pd.concat(frames, ignore_index=True),
    crs=frames[0].crs
)

print(f"\nTotal features before filtering: {len(buildings):,}")

# 1. Keep only polygon geometries

buildings = buildings[
    buildings.geometry.geom_type.isin(
        ["Polygon", "MultiPolygon"]
    )
].copy()

print(
    f"Polygon/MultiPolygon features: "
    f"{len(buildings):,}"
)


# 2. Remove duplicate OSM objects
#
# A building lying exactly on a tile boundary may
# appear in more than one downloaded tile.
#
# OSMnx provides the object type in `element`
# and the OSM object ID in `id`.

if "element" in buildings.columns and "id" in buildings.columns:

    before = len(buildings)

    buildings = buildings.drop_duplicates(
        subset=["element", "id"],
        keep="first"
    )

    removed = before - len(buildings)

    print(
        f"Removed {removed:,} duplicate OSM objects."
    )

else:
    print(
        "Warning: OSM element/id columns not found. "
        "Duplicate removal skipped."
    )

# 3. Reproject to UTM Zone 43N

print("\nReprojecting to UTM Zone 43N...")

buildings = buildings.to_crs(epsg=32643)


# 4. Calculate footprint area

print("Calculating building footprint areas...")

buildings["roof_area_m2"] = buildings.geometry.area

# Remove zero/negative areas
buildings = buildings[
    buildings["roof_area_m2"] > 0
].copy()

# 5. Calculate centroids

print("Calculating building centroids...")

centroids = buildings.geometry.centroid

# Create a GeoDataFrame containing the centroids
centroid_gdf = gpd.GeoDataFrame(
    geometry=centroids,
    crs="EPSG:32643"
)

# Convert centroid coordinates back to WGS84
centroid_gdf = centroid_gdf.to_crs(epsg=4326)

buildings["longitude"] = centroid_gdf.geometry.x
buildings["latitude"] = centroid_gdf.geometry.y

# 6. Generate our own dataset ID

buildings.insert(
    0,
    "building_id",
    range(1, len(buildings) + 1)
)

# 7. Building type

if "building" in buildings.columns:

    building_type = buildings["building"].fillna(
        "unknown"
    )

else:

    building_type = pd.Series(
        "unknown",
        index=buildings.index
    )

# 8. Create final processed table

result = pd.DataFrame({
    "building_id": buildings["building_id"],
    "osm_element": buildings["element"],
    "osm_id": buildings["id"],
    "latitude": buildings["latitude"],
    "longitude": buildings["longitude"],
    "roof_area_m2": buildings["roof_area_m2"],
    "building_type": building_type,
})

# Preserve useful OSM attributes when available
if "building:levels" in buildings.columns:
    result["building_levels"] = buildings["building:levels"]
else:
    result["building_levels"] = pd.NA

if "height" in buildings.columns:
    result["height_m"] = buildings["height"]
else:
    result["height_m"] = pd.NA

if "roof:shape" in buildings.columns:
    result["roof_shape"] = buildings["roof:shape"]
else:
    result["roof_shape"] = pd.NA

if "roof:orientation" in buildings.columns:
    result["roof_orientation"] = buildings["roof:orientation"]
else:
    result["roof_orientation"] = pd.NA

# Flag unusually large footprints rather than deleting them
result["area_quality_flag"] = result["roof_area_m2"].apply(
    lambda area: (
        "large_building"
        if area > 5000
        else "normal"
    )
)

# Remove records without coordinates
result = result.dropna(
    subset=["latitude", "longitude"]
)

# 9. Save

OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)

result.to_csv(
    OUTPUT,
    index=False
)

# 10. Summary

print("\n========================================")
print("OSM PROCESSING COMPLETE")
print("========================================")

print(
    f"Final building records: "
    f"{len(result):,}"
)

print(
    f"Output: {OUTPUT}"
)

print("\nArea statistics:")

print(
    result["roof_area_m2"].describe()
)

print("\nTop building types:")

print(
    result["building_type"]
    .value_counts()
    .head(15)
)