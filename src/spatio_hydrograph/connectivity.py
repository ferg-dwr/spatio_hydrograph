"""
Lateral connectivity analysis.

Measures lateral connectivity of flooded areas using transect lines
and water level measurements at endpoints.
"""

import geopandas as gpd
import numpy as np
import pandas as pd

from .config import Config


class ConnectivityAnalyzer:
    """Analyze lateral connectivity of water features."""

    def __init__(self, config: Config) -> None:
        """
        Initialize connectivity analyzer.

        Parameters
        ----------
        config : Config
            Configuration object
        """
        self.config = config

    def analyze_connectivity(
        self,
        water_polygons: gpd.GeoDataFrame,
        transect_lines: gpd.GeoDataFrame,
    ) -> pd.DataFrame:
        """
        Measure lateral connectivity along transect lines.

        Connectivity is measured as the length of wet (flooded) segments
        along each transect line.

        Parameters
        ----------
        water_polygons : GeoDataFrame
            Water features (must have geometry column)
        transect_lines : GeoDataFrame
            Transect lines for connectivity measurement
            Should have 'transect_id' or index as identifier

        Returns
        -------
        DataFrame
            Columns: transect_id, connectivity_m, num_intersections, percent_connected

        Raises
        ------
        ValueError
            If input GeoDataFrames are empty or invalid

        Notes
        -----
        Calculates the total length of transect lines that intersect with water.
        Useful for measuring lateral extent of floodwaters.
        """
        if len(water_polygons) == 0:
            raise ValueError("water_polygons GeoDataFrame is empty")
        if len(transect_lines) == 0:
            raise ValueError("transect_lines GeoDataFrame is empty")

        # Ensure transect_lines have an ID column
        transect_copy = transect_lines.copy()
        if "transect_id" not in transect_copy.columns:
            transect_copy["transect_id"] = range(len(transect_copy))

        results = []

        for idx, transect_row in transect_copy.iterrows():
            transect_geom = transect_row.geometry
            transect_id = transect_row.get("transect_id", idx)
            total_length = transect_geom.length

            # Find intersections with water polygons
            intersecting_water = water_polygons[
                water_polygons.geometry.intersects(transect_geom)
            ]

            if len(intersecting_water) == 0:
                # No water intersections
                connectivity_m = 0.0
                num_intersections = 0
            else:
                # Calculate total length of transect within water
                wet_length = 0.0
                for water_geom in intersecting_water.geometry:
                    intersection = transect_geom.intersection(water_geom)
                    if not intersection.is_empty:
                        # Get length (works for LineString and MultiLineString)
                        if hasattr(intersection, "length"):
                            wet_length += intersection.length
                        elif hasattr(intersection, "geoms"):
                            # MultiLineString
                            for geom in intersection.geoms:
                                wet_length += geom.length

                connectivity_m = wet_length
                num_intersections = len(intersecting_water)

            # Calculate percent connected
            percent_connected = (
                (connectivity_m / total_length * 100) if total_length > 0 else 0.0
            )

            results.append(
                {
                    "transect_id": transect_id,
                    "connectivity_m": connectivity_m,
                    "num_intersections": num_intersections,
                    "percent_connected": percent_connected,
                }
            )

        result_df = pd.DataFrame(results)
        return result_df

    def calculate_connectivity_endpoints(
        self,
        transect_lines: gpd.GeoDataFrame,
        water_raster: object | None = None,
    ) -> pd.DataFrame:
        """
        Calculate water levels at transect endpoints.

        Parameters
        ----------
        transect_lines : GeoDataFrame
            Transect line geometries
            Should have 'transect_id' or index as identifier
        water_raster : optional
            Water height/level raster (if available)
            Not required - returns endpoint coordinates for now

        Returns
        -------
        DataFrame
            Columns: transect_id, start_x, start_y, end_x, end_y

        Raises
        ------
        ValueError
            If transect_lines GeoDataFrame is empty

        Notes
        -----
        Extracts start and end coordinates of each transect line.
        Can be used to determine water presence at endpoints.
        """
        if len(transect_lines) == 0:
            raise ValueError("transect_lines GeoDataFrame is empty")

        transect_copy = transect_lines.copy()
        if "transect_id" not in transect_copy.columns:
            transect_copy["transect_id"] = range(len(transect_copy))

        results = []

        for idx, transect_row in transect_copy.iterrows():
            geom = transect_row.geometry
            transect_id = transect_row.get("transect_id", idx)

            # Get coordinates
            coords = list(geom.coords)

            if len(coords) < 2:
                continue

            # Start point
            start_x, start_y = coords[0][0], coords[0][1]
            # End point
            end_x, end_y = coords[-1][0], coords[-1][1]

            results.append(
                {
                    "transect_id": transect_id,
                    "start_x": start_x,
                    "start_y": start_y,
                    "end_x": end_x,
                    "end_y": end_y,
                }
            )

        result_df = pd.DataFrame(results)
        return result_df

    def calculate_connectivity_statistics(
        self, connectivity_data: pd.DataFrame
    ) -> dict:
        """
        Calculate mean and SD of connectivity across transects.

        Parameters
        ----------
        connectivity_data : DataFrame
            Connectivity measurements from analyze_connectivity()
            Must have 'connectivity_m' column

        Returns
        -------
        dict
            Statistics dictionary with keys:
            mean_connectivity_m, sd_connectivity_m, min_connectivity_m,
            max_connectivity_m, median_connectivity_m

        Raises
        ------
        ValueError
            If connectivity_data is empty or missing required columns

        Notes
        -----
        Computes basic statistics of lateral connectivity across all transects.
        Useful for summarizing overall connectivity conditions.
        """
        if len(connectivity_data) == 0:
            raise ValueError("connectivity_data is empty")

        if "connectivity_m" not in connectivity_data.columns:
            raise ValueError("connectivity_data must have 'connectivity_m' column")

        connectivity_values = np.asarray(
            connectivity_data["connectivity_m"].values, dtype=float
        )

        # Calculate statistics
        stats = {
            "mean_connectivity_m": float(np.mean(connectivity_values)),  # type: ignore
            "sd_connectivity_m": float(np.std(connectivity_values)),  # type: ignore
            "min_connectivity_m": float(np.min(connectivity_values)),  # type: ignore
            "max_connectivity_m": float(np.max(connectivity_values)),  # type: ignore
            "median_connectivity_m": float(np.median(connectivity_values)),  # type: ignore
        }

        return stats

    def identify_bottlenecks(
        self, connectivity_data: pd.DataFrame, threshold_percentile: float = 10.0
    ) -> pd.DataFrame:
        """
        Identify transects with low connectivity (potential bottlenecks).

        Parameters
        ----------
        connectivity_data : DataFrame
            Connectivity measurements from analyze_connectivity()
            Must have 'connectivity_m' column
        threshold_percentile : float
            Percentile threshold for low connectivity (default: 10.0)
            Transects below this percentile are considered bottlenecks

        Returns
        -------
        DataFrame
            Transects with connectivity below threshold
            Columns: all original columns from connectivity_data

        Raises
        ------
        ValueError
            If connectivity_data is empty or invalid percentile provided

        Notes
        -----
        Low connectivity transects may indicate narrow passages or
        areas where water flow is constrained.
        Useful for identifying critical habitat corridors.
        """
        if len(connectivity_data) == 0:
            raise ValueError("connectivity_data is empty")

        if not (0 <= threshold_percentile <= 100):
            raise ValueError("threshold_percentile must be between 0 and 100")

        if "connectivity_m" not in connectivity_data.columns:
            raise ValueError("connectivity_data must have 'connectivity_m' column")

        connectivity_values = np.asarray(
            connectivity_data["connectivity_m"].values, dtype=float
        )

        # Calculate threshold value
        threshold_value = np.percentile(connectivity_values, threshold_percentile)  # type: ignore

        # Identify bottlenecks
        bottlenecks = connectivity_data[
            connectivity_data["connectivity_m"] <= threshold_value
        ].copy()

        return bottlenecks
