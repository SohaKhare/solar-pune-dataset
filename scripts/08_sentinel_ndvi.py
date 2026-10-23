
import ee

# Replace this with your actual Google Cloud Project ID.
PROJECT_ID = "copycat-507015"

# Pune study-area bounds, matching the existing OSM/SRTM pipeline.
WEST, SOUTH, EAST, NORTH = 73.75, 18.42, 73.98, 18.65

START_DATE = "2025-01-01"
END_DATE = "2026-01-01"  # End date is exclusive.
MAX_SCENE_CLOUD = 80

ee.Initialize(project=PROJECT_ID)

region = ee.Geometry.Rectangle(
    [WEST, SOUTH, EAST, NORTH],
    proj="EPSG:4326",
    geodesic=False,
)

# Load and filter Sentinel-2 surface reflectance imagery.
collection = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(region)
    .filterDate(START_DATE, END_DATE)
    .filter(
        ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", MAX_SCENE_CLOUD)
    )
)

image_count = collection.size().getInfo()
print(f"Sentinel-2 scenes found: {image_count}")

if image_count == 0:
    raise RuntimeError("No Sentinel-2 scenes found for the study area.")

def mask_clouds(image):
    # SCL classes: 3 = cloud shadow, 8/9 = clouds,
    # 10 = cirrus, 11 = snow/ice.
    scl = image.select("SCL")

    clear = (
        scl.neq(3)
        .And(scl.neq(8))
        .And(scl.neq(9))
        .And(scl.neq(10))
        .And(scl.neq(11))
    )

    return image.updateMask(clear)

def calculate_ndvi(image):
    # B8 = near-infrared; B4 = red.
    ndvi = image.normalizedDifference(
        ["B8", "B4"]
    ).rename("NDVI")

    return ndvi.copyProperties(
        image, ["system:time_start"]
    )

# Mask clouds in each scene, calculate NDVI,
# then create a per-pixel annual median composite.
ndvi_collection = (
    collection
    .map(mask_clouds)
    .map(calculate_ndvi)
)

annual_ndvi = ndvi_collection.median().clip(region)

# Export a GeoTIFF to Google Drive.
task = ee.batch.Export.image.toDrive(
    image=annual_ndvi,
    description="Pune_Sentinel2_NDVI_2025",
    folder="solar_pune_sentinel2",
    fileNamePrefix="pune_ndvi_2025",
    region=region,
    crs="EPSG:32643",
    scale=10,
    maxPixels=1e13,
    fileFormat="GeoTIFF",
)

task.start()

print("Export task submitted.")
print("Task ID:", task.id)
print("Open https://code.earthengine.google.com/tasks")
print("Wait for the export status to become COMPLETED.")
