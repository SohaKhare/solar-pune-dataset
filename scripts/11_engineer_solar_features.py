
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_FILE = ROOT / "data" / "processed" / "pune_rooftop_solar_master.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "pune_rooftop_solar_features.csv"

# Explicit baseline assumptions
USABLE_ROOF_FRACTION = 0.70
ROOF_AREA_PER_KW_M2 = 5.0
PERFORMANCE_RATIO = 0.75
DAYS_PER_YEAR = 365


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    # Avoid pandas' mixed-type chunk inference warning.
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    required = ["building_id", "roof_area_m2", "ghi_kwh_m2_day"]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Required columns missing: {sorted(missing)}")

    # Normalize optional numeric OSM attributes.
    # Unparseable values become NaN; they are not treated as zero.
    for column in ["building_levels", "height_m"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    for column in [
        "roof_area_m2",
        "ghi_kwh_m2_day",
        "dni_kwh_m2_day",
        "temperature_c",
        "relative_humidity_pct",
        "wind_speed_m_s",
        "elevation_m",
        "terrain_slope_deg",
        "terrain_aspect_deg",
        "ndvi_2025",
    ]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    # Validate the core inputs.
    valid_roof = df["roof_area_m2"].notna() & (df["roof_area_m2"] > 0)
    valid_ghi = (
        df["ghi_kwh_m2_day"].notna()
        & (df["ghi_kwh_m2_day"] >= 0)
    )
    valid_inputs = valid_roof & valid_ghi

    # Initialize as missing so invalid inputs do not generate false estimates.
    df["usable_roof_area_m2"] = np.nan
    df["estimated_pv_capacity_kw"] = np.nan
    df["estimated_annual_generation_kwh"] = np.nan

    # 1. Estimate roof area available for PV panels.
    df.loc[valid_roof, "usable_roof_area_m2"] = (
        df.loc[valid_roof, "roof_area_m2"]
        * USABLE_ROOF_FRACTION
    )

    # 2. Estimate installed PV capacity.
    df.loc[valid_roof, "estimated_pv_capacity_kw"] = (
        df.loc[valid_roof, "usable_roof_area_m2"]
        / ROOF_AREA_PER_KW_M2
    )

    # 3. Estimate annual energy from average daily GHI.
    # kW × peak-sun-hours/day × days/year × performance ratio = kWh/year.
    df.loc[valid_inputs, "estimated_annual_generation_kwh"] = (
        df.loc[valid_inputs, "estimated_pv_capacity_kw"]
        * df.loc[valid_inputs, "ghi_kwh_m2_day"]
        * DAYS_PER_YEAR
        * PERFORMANCE_RATIO
    )

    # Store assumptions alongside the calculated features.
    df["assumed_usable_roof_fraction"] = USABLE_ROOF_FRACTION
    df["assumed_roof_area_m2_per_kw"] = ROOF_AREA_PER_KW_M2
    df["assumed_performance_ratio"] = PERFORMANCE_RATIO
    df["generation_estimate_method"] = "GHI_capacity_performance_ratio_v1"

    df.to_csv(OUTPUT_FILE, index=False)

    print("\nSOLAR FEATURE ENGINEERING COMPLETE")
    print(f"Output: {OUTPUT_FILE}")
    print(f"Building records: {len(df):,}")
    print(f"Valid roof areas: {int(valid_roof.sum()):,}")
    print(f"Valid energy estimates: {int(valid_inputs.sum()):,}")
    print(f"Missing energy estimates: {int((~valid_inputs).sum()):,}")

    print("\nDerived feature statistics:")
    print(
        df[
            [
                "usable_roof_area_m2",
                "estimated_pv_capacity_kw",
                "estimated_annual_generation_kwh",
            ]
        ].describe().round(2).to_string()
    )

    print("\nLargest estimated systems (inspect for footprint anomalies):")
    columns = [
        "building_id",
        "roof_area_m2",
        "area_quality_flag",
        "estimated_pv_capacity_kw",
        "estimated_annual_generation_kwh",
    ]
    print(
        df.nlargest(5, "estimated_pv_capacity_kw")[columns]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
