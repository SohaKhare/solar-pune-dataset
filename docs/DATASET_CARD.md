# Dataset Card

## Title

City-Scale Rooftop Solar Potential Dataset for Pune Using OpenStreetMap,
NASA POWER, Sentinel-2, and SRTM

## Summary

A building-level geospatial dataset for Pune, Maharashtra, India,
containing mapped building-footprint attributes and contextual
solar-resource, weather, terrain, and vegetation features.

## Intended uses

-   Exploratory city-scale rooftop solar resource assessment.
-   Geospatial feature engineering and visualization.
-   Studying the availability and limitations of open geospatial data
    for urban solar analysis.
-   Educational and research workflows where feature provenance and
    uncertainty are explicitly considered.

## Out-of-scope uses

-   Treating estimated footprint area as surveyed usable roof area.
-   Treating terrain slope/aspect as roof slope/orientation.
-   Treating repeated NASA POWER values as building-specific
    measurements.
-   Treating centroid NDVI as a direct measurement of roof vegetation or
    shading.
-   Claiming validated building-level energy generation or solar
    suitability from this dataset alone.

## Geographic coverage

Pune, Maharashtra, India; approximate input bounds: 73.75--73.98° E and
18.42--18.65° N.

## Temporal coverage

-   Sentinel-2 NDVI composite: calendar year 2025.
-   NASA POWER: climatological annual values retrieved for a
    representative Pune coordinate. Record the exact API endpoint and
    retrieval date in the release metadata.
-   OSM and SRTM: source retrieval dates should be recorded from project
    logs before publication.

## Dataset size

-   241,079 building records.
-   23 columns in the cleaned CSV.

## Unit of observation

One retained OpenStreetMap building feature, identified by `building_id`
and linked to its source element using `osm_element` and `osm_id`.

## Sources

-   OpenStreetMap building features and footprint geometry.
-   NASA POWER solar and meteorological climatology.
-   SRTM elevation data.
-   Sentinel-2 Level-2A surface reflectance via Google Earth Engine.

## Known quality issues

-   `roof_orientation` is fully missing.
-   `roof_shape`, `height_m`, and `building_levels` are sparse.
-   A small number of terrain and NDVI samples are missing.
-   Large footprint polygons exist; 324 records exceed 5,000 m² and are
    flagged.
-   `roof_area_m2` is derived from mapped footprint geometry and is only
    a proxy for roof area.

## Processing

The pipeline downloads/loads source data, filters OSM polygonal building
features, calculates footprint area and representative coordinates,
processes SRTM terrain rasters, creates a cloud-masked 2025 Sentinel-2
NDVI composite, samples raster features at building representative
points, adds NASA POWER city-level context, and validates the merged
CSV.

## Missing data

Missing values are preserved as missing rather than replaced with zero.
Optional OSM roof/building metadata are not imputed in the published
cleaned dataset.

## Ethical and privacy considerations

The dataset is based on public geospatial/environmental sources and
describes building features. Before publication, check for any source
terms, licensing conditions, or sensitive locations that may require
special handling. Do not include API keys or account credentials.

## Licensing

OpenStreetMap-derived database content is subject to ODbL terms. Review
obligations for the combined dataset and identify licenses/terms for
each external source before assigning a license to the entire package.
Do not claim that all components are public domain without checking
their terms.

## Citation

Add the final IEEE DataPort citation and DOI after publication.
