# Dataset Quality Report

## Validation summary

The reported validation run produced the following results for
`pune_rooftop_solar_clean.csv`:

-   Rows: 241,079.
-   Columns: 23.
-   Unique building IDs: 241,079.
-   Exact duplicate rows: 0.
-   `roof_area_m2`: 241,079 non-missing values.
-   NDVI missing: 65.
-   Elevation missing: 132.
-   Terrain slope missing: 531.
-   Terrain aspect missing: 531.
-   Roof orientation missing: 241,079.
-   `area_quality_flag`: 240,755 `normal`; 324 `large_building`.

Coordinate ranges reported: - Latitude: 18.419981 to 18.650602. -
Longitude: 73.749749 to 73.980412.

Roof-area summary reported: - Minimum: 0.688560 m². - Median: 133.148474
m². - Mean: 247.395057 m². - Maximum: 151,371.286106 m².

## Interpretation

The reported checks indicate stable record counts and unique building
identifiers. Missing roof metadata are expected given incomplete OSM
tagging. The 324 large footprints should be reviewed for plausibility,
but should not be removed solely because they exceed the threshold.

The cleaning script converted `building_levels`, `height_m`, and
`roof_orientation` to numeric columns using coercion. The reported
missing counts increased slightly for `building_levels` and `height_m`,
which indicates that some non-numeric values became missing. If the
original tag strings are important, preserve them in an archival
source-derived file or rerun the pipeline to retain raw OSM tag values
alongside parsed numeric fields.

## Recommended release checks

Before upload: 1. Re-run validation against the exact CSV that will be
uploaded. 2. Confirm the file's SHA-256 checksum and record it in
release metadata. 3. Confirm the final filename and schema match the
data dictionary. 4. Review the largest footprints on a map or against
their OSM records. 5. Record data retrieval dates, dependency versions,
and the exact source product identifiers. 6. Verify licensing and
attribution for every source. 7. Ensure no credentials, `.env` files, or
authentication tokens are included.
