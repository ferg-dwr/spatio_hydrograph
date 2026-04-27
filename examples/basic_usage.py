#!/usr/bin/env python3
"""
Example usage of the spatio-hydrograph package.

This script demonstrates the basic workflow for analyzing satellite-derived
water classification maps to quantify inundation dynamics.
"""

from pathlib import Path

from spatio_hydrograph.config import Config
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer
from spatio_hydrograph.landscape_metrics import LandscapeMetrics
from spatio_hydrograph.raster_processing import RasterProcessor
from spatio_hydrograph.visualization import Visualizer


def example_basic_configuration() -> None:
    """Example 1: Create and work with configuration."""
    print("=" * 70)
    print("EXAMPLE 1: Configuration Management")
    print("=" * 70)

    # Create a configuration object
    config = Config(
        water_year=2023,
        analysis_version="_v1",
        data_dir=Path("./data"),
        s1_input_dir=Path("./data/S1_WY2023"),
        s2_input_dir=Path("./data/S2_WY2023"),
        output_dir=Path("./output"),
        min_polygon_area_m2=5000.0,
        flood_trigger_habitats=["First", "Last"],
    )

    print(f"Water Year: {config.water_year}")
    print(f"Analysis Version: {config.analysis_version}")
    print(f"Output Directory: {config.output_dir}")
    print(f"Minimum Polygon Area: {config.min_polygon_area_m2} m²")
    print()


def example_raster_processing(config: Config) -> None:
    """Example 2: Raster-to-vector conversion."""
    print("=" * 70)
    print("EXAMPLE 2: Raster-to-Vector Processing")
    print("=" * 70)

    # Initialize raster processor
    processor = RasterProcessor(config)

    print("RasterProcessor initialized")
    print("Available methods:")
    print("  - load_habitat_polygons()")
    print("  - raster_to_polygons(raster_path)")
    print("  - filter_by_area(polygons, min_area_m2)")
    print("  - intersect_with_habitats(polygons)")
    print()

    # Example workflow (not executable without data):
    print("Typical workflow:")
    print("  1. Load habitat polygons from shapefile")
    print("  2. Convert water classification raster to polygons")
    print("  3. Filter polygons smaller than minimum area")
    print("  4. Intersect with habitat boundaries")
    print()


def example_habitat_analysis(config: Config) -> None:
    """Example 3: Habitat-specific inundation analysis."""
    print("=" * 70)
    print("EXAMPLE 3: Habitat Inundation Analysis")
    print("=" * 70)

    analyzer = HabitatAnalyzer(config)

    print("HabitatAnalyzer initialized")
    print("Available methods:")
    print("  - calculate_habitat_areas(water_polygons)")
    print("  - calculate_percent_inundated(habitat_areas)")
    print("  - identify_flood_status(habitat_areas)")
    print("  - aggregate_by_water_year(habitat_time_series)")
    print()

    print("Output format: DataFrame with columns")
    print("  - date: Observation date")
    print("  - habitat: Habitat name (e.g., 'First', 'Middle', 'Last')")
    print("  - inundated_area_ha: Inundated area in hectares")
    print("  - percent_water: Percent of habitat that is inundated")
    print()


def example_landscape_metrics(config: Config) -> None:
    """Example 4: Landscape ecology metrics."""
    print("=" * 70)
    print("EXAMPLE 4: Landscape Metrics Calculation")
    print("=" * 70)

    metrics = LandscapeMetrics(config)

    print("LandscapeMetrics initialized")
    print("Available methods:")
    print("  - calculate_patch_metrics(classified_raster)")
    print("  - calculate_class_metrics(classified_raster)")
    print("  - calculate_area_statistics(patches)")
    print("  - calculate_core_area_statistics(patches)")
    print("  - calculate_para_statistics(patches)")
    print("  - calculate_percentiles(values)")
    print()

    print("Computed metrics:")
    print("  Patch-level:")
    print("    - Area (mean, sd, p10, p50, p90, max)")
    print("    - Core Area (excluding 10m edge)")
    print("    - Perimeter-Area Ratio")
    print("  Class-level:")
    print("    - Clumpiness")
    print("    - Cohesion")
    print()


def example_visualization(config: Config) -> None:
    """Example 5: Visualization and figure generation."""
    print("=" * 70)
    print("EXAMPLE 5: Visualization")
    print("=" * 70)

    viz = Visualizer(config, figsize=(12, 8), dpi=300)

    print("Visualizer initialized")
    print("Available plotting methods:")
    print("  - plot_habitat_time_series(habitat_data)")
    print("  - plot_percent_water(habitat_data)")
    print("  - plot_lateral_connectivity(connectivity_data)")
    print("  - plot_patch_size_distribution(landscape_metrics)")
    print("  - plot_core_area_distribution(landscape_metrics)")
    print("  - plot_comparative_sensors(s1_data, s2_data)")
    print()

    print("Figures are saved to: {output_dir}/figures/")
    print()


def main() -> None:
    """Run all examples."""
    print()
    print("=" * 70)
    print("SPATIO-HYDROGRAPH PACKAGE EXAMPLES")
    print("=" * 70)
    print()

    # Create a sample configuration
    config = Config(
        water_year=2023,
        analysis_version="_v1",
        data_dir=Path("./data"),
        s1_input_dir=Path("./data/S1_WY2023"),
        s2_input_dir=Path("./data/S2_WY2023"),
        output_dir=Path("./output"),
    )

    # Run examples
    example_basic_configuration()
    example_raster_processing(config)
    example_habitat_analysis(config)
    example_landscape_metrics(config)
    example_visualization(config)

    print("=" * 70)
    print("For detailed documentation, see README.md")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
