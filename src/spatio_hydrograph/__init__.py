"""
Spatio-Temporal Hydrographic Analysis of Yolo Bypass Inundation.

A Python package for analyzing satellite-derived water classification maps
to calculate landscape metrics, habitat-specific inundation, and lateral
connectivity in the Yolo Bypass, California.

Main modules:
    - config: Configuration management for analysis parameters
    - raster_processing: Raster-to-vector conversion and polygon processing
    - landscape_metrics: Landscape ecology metrics calculations
    - connectivity: Lateral connectivity analysis
    - habitat_analysis: Per-habitat inundation area calculations
    - visualization: Plotting and output generation

Example:
    >>> from spatio_hydrograph import SpatioHydrographAnalysis
    >>> analysis = SpatioHydrographAnalysis(
    ...     config_file="config.yaml",
    ...     water_year=2023
    ... )
    >>> results = analysis.run()
"""

__version__ = "0.1.0"
__author__ = "Shruti Khanna, Fernando E. Romero Galvan"
__email__ = "fernando.romerogalvan@water.ca.gov"

__all__ = [
    "config",
    "raster_processing",
    "landscape_metrics",
    "connectivity",
    "habitat_analysis",
    "visualization",
]
