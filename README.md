# City-Scale Rooftop Solar Potential Dataset for Pune

## Overview

This dataset combines building-footprint attributes and
geospatial/environmental context for a study area in Pune, Maharashtra,
India. It was assembled from OpenStreetMap (OSM), NASA POWER, Shuttle
Radar Topography Mission (SRTM) elevation data, and Sentinel-2 satellite
imagery accessed through Google Earth Engine.

The current cleaned building-level CSV contains **241,079 records and 23
columns**. Each row represents one mapped OSM building feature retained
by the processing pipeline.

> **Important scope statement:** This release is a geospatial feature
> dataset intended to support exploratory rooftop-solar resource
> assessment. It does not contain measured rooftop PV installations,
> measured electricity generation, or validated building-specific
> solar-suitability labels. It does not include an ML model.

## Primary file

- `data/processed/pune_rooftop_solar_clean.csv` --- cleaned
  building-level dataset.

If distributing only the final data product, include this CSV together
with the data dictionary, dataset card, quality report, source
attribution, and license information.

## Data sources and processing

### OpenStreetMap

OSM building features were collected over a rectangular study area
approximately bounded by longitude 73.75--73.98 and latitude
18.42--18.65. To manage request size, the area was downloaded in smaller
spatial tiles. Polygon and multipolygon building features were
processed, duplicate OSM objects were removed, and footprint area and
representative coordinates were calculated.

The `roof_area_m2` field is the mapped footprint area used as a proxy
for roof area. It is not a direct survey of roof surface area or usable
panel area.

### NASA POWER

NASA POWER climatological solar and weather variables were retrieved for
a representative Pune coordinate (latitude 18.5204, longitude 73.8567).
Annual values were attached to each building row as **city-level
contextual variables**. The same values are repeated across buildings;
they must not be interpreted as individual building observations.

Variables: global horizontal irradiance (GHI), direct normal irradiance
(DNI), temperature, relative humidity, and wind speed.

### SRTM

SRTM elevation data was processed into a projected raster in WGS 84 /
UTM zone 43N (EPSG:32643). Elevation, terrain slope, and terrain aspect
were sampled at building representative points. These are
terrain-context measurements, not roof slope or roof orientation.

### Sentinel-2

Sentinel-2 Level-2A surface-reflectance imagery was accessed through
Google Earth Engine for calendar year 2025. Cloud/shadow masking was
applied using the scene classification layer, NDVI was calculated from
near-infrared band B8 and red band B4, and an annual median composite
was exported at 10 m resolution. The composite was sampled at building
representative points.

NDVI is a vegetation-context feature. A sampled pixel may represent
vegetation or another nearby surface and is not guaranteed to represent
the roof itself.

## Data quality summary

- Records: 241,079.
- Columns: 23.
- Unique `building_id` values: 241,079.
- Exact duplicate rows: 0 in the reported validation.
- Missing NDVI: 65 records in the reported extraction.
- Missing elevation: 132 records in the reported extraction.
- Missing terrain slope/aspect: 531 records each in the reported
  extraction.
- `roof_orientation` is missing for all records.
- `roof_shape`, `height_m`, and `building_levels` are sparsely
  populated.
- 324 footprints have area greater than 5,000 m² and are flagged
  `large_building`; these records are retained.

See `docs/QUALITY_REPORT.md` for additional details.

## Files and reproducibility

The repository's `scripts/` directory contains the processing scripts
used to collect, process, sample, merge, and validate the source data.
Review script constants and paths before rerunning them. Some stages
require network access and credentials, including Google Earth Engine
authorization and an OpenTopography API key for SRTM acquisition.

Do not publish `.env` files, API keys, authentication tokens, or the
`.venv` directory.

For reproducibility, record the exact versions of Python and
dependencies used for the release, along with the date on which source
data were retrieved. A `uv.lock` file should be retained if present and
appropriate.

## Limitations

1.  **Footprint proxy:** mapped building footprint area is used as a
    proxy for roof area. It does not account for roof geometry,
    obstructions, setbacks, or usable surface area.
2.  **Incomplete roof metadata:** roof shape and roof orientation are
    largely unavailable; roof orientation is entirely missing in this
    release.
3.  **City-level climate context:** NASA POWER variables are drawn from
    one representative coordinate and repeated across records. They do
    not capture building-scale spatial variation.
4.  **Terrain versus roof geometry:** SRTM slope and aspect describe
    surrounding terrain and must not be interpreted as roof pitch or
    roof orientation.
5.  **Centroid-based NDVI:** a 10 m Sentinel-2 pixel sampled at a
    building representative point may not fall on the roof and may
    include nearby land cover.
6.  **Large footprints:** unusually large footprints may be valid
    complexes or mapping artefacts. They are flagged for inspection, not
    automatically excluded.
7.  **No ground-truth energy labels:** the dataset does not contain
    measured PV capacity or electricity production and does not itself
    validate a solar-generation prediction model.

## Citation and attribution

When using OpenStreetMap-derived data, provide attribution such as:

> © OpenStreetMap contributors. Data available under the Open Database
> License (ODbL).

See https://www.openstreetmap.org/copyright for attribution and license
information. Review ODbL obligations for the combined/derived database
before selecting a license for the complete release.

NASA POWER and the relevant SRTM and Sentinel-2 data products should
also be cited according to their official provider guidance. Add the
exact product pages, retrieval dates, and version details used for the
release before publication.

## Contact and citation

A formal citation can be added after the IEEE DataPort record is
published and has a DOI. Until then, cite the repository and dataset
title, and include the DOI once assigned.
