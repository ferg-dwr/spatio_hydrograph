"""
Habitat-specific inundation analysis.

Calculates per-habitat inundated area, percent water coverage,
and flood duration metrics.
"""

from typing import Dict, Optional

import geopandas as gpd
import pandas as pd

from .config import Config


class HabitatAnalyzer:
    """Analyze inundation per habitat unit."""

    def __init__(self, config: Config) -> None:
        """
        Initialize habitat analyzer.

        Parameters
        ----------
        config : Config
            Configuration object
        """
        self.config = config

    def calculate_habitat_areas(
        self, water_polygons: gpd.GeoDataFrame
    ) -> pd.DataFrame:
        """
        Calculate inundated area per habitat.

        Parameters
        ----------
        water_polygons : GeoDataFrame
            Water polygons with habitat attributes

        Returns
        -------
        DataFrame
            Habitat name, total inundated area (ha), percent water
        """
        # TODO: Implement habitat area calculation
        raise NotImplementedError("calculate_habitat_areas not yet implemented")

    def calculate_percent_inundated(self, habitat_areas: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate percent of each habitat that is inundated.

        Parameters
        ----------
        habitat_areas : DataFrame
            Habitat areas from calculate_habitat_areas

        Returns
        -------
        DataFrame
            Habitat name, percent inundated (%)
        """
        # TODO: Implement percent calculation
        raise NotImplementedError("calculate_percent_inundated not yet implemented")

    def identify_flood_status(self, habitat_areas: pd.DataFrame) -> Dict[str, bool]:
        """
        Identify which habitats are currently flooded.

        Parameters
        ----------
        habitat_areas : DataFrame
            Habitat areas

        Returns
        -------
        dict
            Mapping of habitat names to flood status (True/False)
        """
        # TODO: Implement flood status detection
        raise NotImplementedError("identify_flood_status not yet implemented")

    def aggregate_by_water_year(
        self, habitat_time_series: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Aggregate habitat metrics by water year.

        Parameters
        ----------
        habitat_time_series : DataFrame
            Daily habitat area time series

        Returns
        -------
        DataFrame
            Water year summary statistics
        """
        # TODO: Implement water year aggregation
        raise NotImplementedError("aggregate_by_water_year not yet implemented")
