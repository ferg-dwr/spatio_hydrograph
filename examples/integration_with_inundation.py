"""
Integration example: Using spatio-hydrograph with inundation package.

This example shows how to combine water level data from the inundation package
with satellite inundation maps from spatio-hydrograph for comprehensive analysis.
"""

import pandas as pd
from datetime import datetime

# Import spatio-hydrograph modules
from spatio_hydrograph.config import load_config
from spatio_hydrograph.raster_processing import RasterProcessor
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer
from spatio_hydrograph.visualization import Visualizer

# Import inundation package (optional)
try:
    from inundation import get_fre, calc_inundation
    INUNDATION_AVAILABLE = True
except ImportError:
    INUNDATION_AVAILABLE = False
    print("Warning: inundation package not installed. Install with:")
    print("  pip install 'spatio-hydrograph[inundation]'")
    print("  or: pip install inundation")


def analyze_with_water_level_validation(config_path: str = "config.yaml"):
    """
    Analyze satellite water maps with water level validation from sensors.

    This workflow combines:
    1. Satellite-derived water extent (Sentinel-1/2)
    2. Ground-truth water level measurements (Fremont Weir)
    3. Flow data (Sacramento River and Yolo Bypass dayflow)

    Parameters
    ----------
    config_path : str
        Path to config.yaml file (optional for demo)

    Returns
    -------
    dict
        Dictionary containing:
        - satellite_areas: DataFrame of habitat inundation from satellite
        - water_levels: DataFrame of Sacramento River stage heights
        - inundation_days: DataFrame of inundation duration from sensors
        - comparison: DataFrame comparing satellite and sensor data
    """

    if not INUNDATION_AVAILABLE:
        raise ImportError(
            "inundation package required for this workflow. "
            "Install with: pip install 'spatio-hydrograph[inundation]' "
            "or: pip install git+https://github.com/ferg-dwr/inundation.git"
        )

    print("=" * 70)
    print("WORKFLOW: Satellite Inundation with Water Level Validation")
    print("=" * 70)

    # Step 1: Load configuration (optional for demo)
    config = None
    try:
        from pathlib import Path
        if Path(config_path).exists():
            print(f"\n1. Loading configuration from {config_path}...")
            config = load_config(config_path)
            print(f"   - Water year: {config.water_year}")
            print(f"   - Analysis version: {config.analysis_version}")
        else:
            print(f"\n1. Configuration file '{config_path}' not found.")
            print("   - Running demo mode (no config needed)")
            config = None
    except Exception as e:
        print(f"\n1. Warning: Could not load config: {e}")
        print("   - Running demo mode (no config needed)")
        config = None

    # Step 2: Get water level data from inundation package
    print("\n2. Downloading water level data...")
    print("   - Fremont Weir (Sacramento River stage)")
    try:
        fre = get_fre() # type: ignore
        print(f"   ✓ Retrieved {len(fre)} hourly observations")
        print(f"   - Date range: {fre['datetime'].min()} to {fre['datetime'].max()}")
    except Exception as e:
        print(f"   ✗ Error downloading FRE data: {e}")
        print("   - Check internet connection and CDEC availability")
        return None

    # Step 3: Calculate inundation days from water level
    print("\n3. Calculating inundation duration...")
    try:
        inundation_calc = calc_inundation() # type: ignore
        num_inundation_days = inundation_calc['inundation'].sum()
        print(f"   ✓ {num_inundation_days} inundation days detected")
        if num_inundation_days > 0:
            inundation_by_year = (
                inundation_calc[inundation_calc["inundation"] == 1]
                .groupby(inundation_calc['date'].dt.year)
                .size()
            )
            print(f"   - Peak year: {inundation_by_year.idxmax()} with {inundation_by_year.max()} days")
    except Exception as e:
        print(f"   ✗ Error calculating inundation: {e}")
        print("   - Check that dayflow and FRE data are available")
        return None

    # Step 4: Process satellite water maps (demo mode)
    print("\n4. Processing satellite water maps...")
    if config is None:
        print("   - (Skipping - no config file provided)")
        print("   - To process satellite data:")
        print("     1. Create config.yaml from config.example.yaml")
        print("     2. Point to your satellite water classification rasters")
        print("     3. Provide habitat polygon shapefiles")
    else:
        try:
            processor = RasterProcessor(config)
            habitat_gdf = processor.load_habitat_polygons()
            print(f"   ✓ Loaded {len(habitat_gdf)} habitat polygons")
        except Exception as e:
            print(f"   ✗ Error loading habitat polygons: {e}")
            habitat_gdf = None

    # Step 5: Analyze per-habitat inundation
    print("\n5. Calculating habitat-level statistics...")
    if config is None:
        print("   - (Skipped - no config file)")
    else:
        try:
            habitat_analyzer = HabitatAnalyzer(config)
            print(f"   ✓ Ready to analyze habitats")
        except Exception as e:
            print(f"   ✗ Error: {e}")

    # Step 6: Compare satellite and sensor data
    print("\n6. Comparing satellite and sensor observations...")
    print("\n   Water Level Indicators (from inundation package):")
    print(f"   - Stage height threshold (pre-2016): 33.5 feet")
    print(f"   - Stage height threshold (post-2016): 32.0 feet")
    print(f"   - Inundation indicator: binary yes/no")

    print("\n   Satellite Water Extent (from spatio-hydrograph):")
    print(f"   - Water classification: Sentinel-1 (Lee Sigma)")
    print(f"   - Water classification: Sentinel-2 (AWEIsh)")
    print(f"   - Habitat-specific areas: spatial extent by type")
    print(f"   - Continuous rather than binary")

    print("\n   Comparison Benefits:")
    print(f"   ✓ Validate satellite water classification")
    print(f"   ✓ Cross-check inundation timing")
    print(f"   ✓ Detect discrepancies (e.g., clouds in satellite)")
    print(f"   ✓ Combine temporal (sensors) and spatial (satellite) data")

    # Step 7: Create visualizations
    print("\n7. Creating integrated visualizations...")
    if config is None:
        print("   - (Skipped - no config file)")
    else:
        try:
            viz = Visualizer(config, show=False)
            print("   ✓ Visualizer ready")
            print("   - Habitat inundation time series")
            print("   - Water level overlay")
            print("   - Satellite water extent maps")
            print("   - Connectivity analysis with water level context")
        except Exception as e:
            print(f"   ✗ Error creating visualizer: {e}")

    print("\n" + "=" * 70)
    print("WORKFLOW COMPLETE")
    print("=" * 70)

    return {
        "fre": fre if 'fre' in locals() else None,
        "inundation_calc": inundation_calc if 'inundation_calc' in locals() else None,
        "config": config,
    }


def create_comparison_dataframe(fre_data, satellite_data, date_range):
    """
    Create comparison DataFrame of satellite vs. sensor inundation.

    Parameters
    ----------
    fre_data : DataFrame
        Fremont Weir stage height data
    satellite_data : DataFrame
        Satellite-derived water extent
    date_range : tuple
        (start_date, end_date) for comparison

    Returns
    -------
    DataFrame
        Comparison with columns:
        - date
        - fre_stage: Sacramento River stage (feet)
        - inundated_sensor: Binary indicator from stage height
        - inundated_satellite: Binary indicator from satellite
        - agreement: 1 if both agree, 0 if disagree
        - satellite_area_ha: Inundated area from satellite (ha)
    """
    # This is a template for the comparison workflow
    print("\nCreating comparison DataFrame...")
    print("  - Aligning temporal data")
    print("  - Computing agreement metrics")
    print("  - Identifying discrepancies")

    return None  # Placeholder


if __name__ == "__main__":
    # Run the integration workflow
    if INUNDATION_AVAILABLE:
        try:
            results = analyze_with_water_level_validation()
            if results is not None:
                print("\n✅ Integration workflow completed successfully!")
                print(f"\nResults dictionary keys:")
                for key, value in results.items():
                    if value is not None:
                        print(f"  - {key}")
            else:
                print("\n⚠️  Workflow stopped due to data unavailability.")
                print("Check internet connection and data source availability.")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nNote: This is a demo script. To use with satellite data:")
            print("  1. Create config.yaml from config.example.yaml")
            print("  2. Update paths to your satellite water maps")
            print("  3. Provide habitat polygon shapefiles")
    else:
        print("\n❌ Inundation package not installed.")
        print("\nTo use this integration example, install with:")
        print("  pip install git+https://github.com/ferg-dwr/inundation.git")
        print("\nOr as part of spatio-hydrograph:")
        print("  pip install 'git+https://github.com/ferg-dwr/spatio_hydrograph.git[inundation]'")
        print("\nThen run again to see the full workflow.")
