"""
Landscape ecology metrics calculations.

Computes patch metrics (area, core area, perimeter), class metrics
(clumpiness, cohesion), and percentile distributions.
"""

from typing import Optional

import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from scipy import ndimage

from .config import Config


class LandscapeMetrics:
    """Calculate landscape ecology metrics from classified rasters."""

    def __init__(self, config: Config) -> None:
        """
        Initialize landscape metrics calculator.

        Parameters
        ----------
        config : Config
            Configuration object with metric settings
        """
        self.config = config

    def calculate_patch_metrics(
        self, classified_raster: xr.DataArray
    ) -> pd.DataFrame:
        """
        Calculate patch-level metrics (area, core area, PARA).

        Parameters
        ----------
        classified_raster : DataArray
            Water classification raster (binary or multi-class)

        Returns
        -------
        DataFrame
            Summary of patch metrics with keys:
            total_patches, total_area_m2, mean_area_m2, mean_core_area_m2,
            mean_para, area_sd_m2, core_area_sd_m2, para_sd_m2,
            and percentiles (p10, p50, p90) for each metric

        Raises
        ------
        ValueError
            If raster has no water features or is invalid

        Notes
        -----
        Converts raster to vector polygons using rasterio.features.shapes.
        Computes area, core area, and shape complexity metrics.
        Useful for characterizing inundation patches at a given time.
        """
        from rasterio.features import shapes
        from shapely.geometry import shape

        # Get the data
        data = classified_raster.values

        if data.size == 0:
            raise ValueError("Raster has no data")

        # Convert raster to polygons
        polygon_list = []
        for geom, value in shapes(data.astype(np.uint8), transform=classified_raster.rio.transform()):
            # Only keep water features (value == 1)
            if value == 1:
                polygon_list.append(shape(geom))

        if not polygon_list:
            raise ValueError("No water features found in raster")

        # Create GeoDataFrame from polygons
        gdf = gpd.GeoDataFrame(
            {"water_pixel": [1] * len(polygon_list), "geometry": polygon_list},
            crs=classified_raster.rio.crs,
        )

        # Calculate area
        gdf["area_m2"] = gdf.geometry.area

        # Calculate individual metrics
        area_stats = self.calculate_area_statistics(gdf)
        core_stats = self.calculate_core_area_statistics(gdf)
        para_stats = self.calculate_para_statistics(gdf)

        # Compile results into DataFrame
        result = pd.DataFrame({
            "total_patches": [len(gdf)],
            "total_area_m2": [gdf["area_m2"].sum()],
            "mean_area_m2": [area_stats["mean_m2"]],
            "sd_area_m2": [area_stats["sd_m2"]],
            "min_area_m2": [area_stats["min_m2"]],
            "max_area_m2": [area_stats["max_m2"]],
            "p10_area_m2": [area_stats["p10_m2"]],
            "p50_area_m2": [area_stats["p50_m2"]],
            "p90_area_m2": [area_stats["p90_m2"]],
            "mean_core_area_m2": [core_stats["mean_m2"]],
            "sd_core_area_m2": [core_stats["sd_m2"]],
            "p10_core_area_m2": [core_stats["p10_m2"]],
            "p50_core_area_m2": [core_stats["p50_m2"]],
            "p90_core_area_m2": [core_stats["p90_m2"]],
            "mean_para": [para_stats["mean"]],
            "sd_para": [para_stats["sd"]],
            "p10_para": [para_stats["p10"]],
            "p50_para": [para_stats["p50"]],
            "p90_para": [para_stats["p90"]],
        })

        return result

    def calculate_class_metrics(
        self, classified_raster: xr.DataArray
    ) -> pd.DataFrame:
        """
        Calculate class-level metrics (clumpiness, cohesion).

        Parameters
        ----------
        classified_raster : DataArray
            Water classification raster (binary or multi-class)

        Returns
        -------
        DataFrame
            Class metrics with columns:
            clumpiness (0-1, higher = more clumped),
            cohesion (0-1, higher = more cohesive/connected)

        Raises
        ------
        ValueError
            If raster has no water features or is invalid

        Notes
        -----
        Clumpiness = measure of patch aggregation/clustering.
        Cohesion = measure of spatial connectivity of class patches.
        Both range from 0 (dispersed) to 1 (perfectly clumped/cohesive).
        
        Based on standard landscape ecology definitions.
        """
        data = classified_raster.values

        if data.size == 0:
            raise ValueError("Raster has no data")

        # Get water pixels (value == 1)
        water_pixels = (data == 1).astype(int)
        total_pixels = np.sum(water_pixels)

        if total_pixels == 0:
            raise ValueError("No water features found in raster")

        # Calculate Clumpiness Index
        # Clumpiness = (G_obs - G_exp) / (G_max - G_exp)
        # where G = number of joins between like cells
        
        # Count joins (cells sharing edges)
        gx = water_pixels[:, :-1] * water_pixels[:, 1:]  # Horizontal joins
        gy = water_pixels[:-1, :] * water_pixels[1:, :]  # Vertical joins
        g_obs = np.sum(gx) + np.sum(gy)

        # Expected joins (random distribution)
        if total_pixels > 0:
            p = total_pixels / water_pixels.size
            a_cells = water_pixels.size
            n_horiz = a_cells - water_pixels.shape[0]
            n_vert = a_cells - water_pixels.shape[1]
            g_exp = 2 * p * (1 - p) * (n_horiz + n_vert)
        else:
            g_exp = 0

        # Maximum joins (all clustered)
        g_max = total_pixels - 1

        if g_max > g_exp:
            clumpiness = (g_obs - g_exp) / (g_max - g_exp)
        else:
            clumpiness = 0.0

        # Clamp to [0, 1]
        clumpiness = np.clip(clumpiness, 0.0, 1.0)

        # Calculate Cohesion Index
        # Cohesion = (1 - (number of disjunct parts) / (number of patches)) * 100
        # Simplified: use connectivity of largest component
        
        # Label connected components
        labeled_array, num_features = ndimage.label(water_pixels)  # type: ignore
        
        if num_features == 0:
            cohesion = 0.0
        else:
            # Simple cohesion: ratio of largest component to total
            component_sizes = ndimage.sum(water_pixels, labeled_array, range(num_features + 1))
            largest_component = np.max(component_sizes[1:]) if num_features > 0 else 0
            cohesion = largest_component / total_pixels if total_pixels > 0 else 0.0

        # Clamp to [0, 1]
        cohesion = np.clip(cohesion, 0.0, 1.0)

        # Return as DataFrame
        result = pd.DataFrame({
            "clumpiness": [float(clumpiness)],
            "cohesion": [float(cohesion)],
        })

        return result

    def calculate_area_statistics(self, patches: gpd.GeoDataFrame) -> dict:
        """
        Calculate patch area statistics.

        Parameters
        ----------
        patches : GeoDataFrame
            Water patch polygons with 'area_m2' or calculated area column

        Returns
        -------
        dict
            Statistics dictionary with keys:
            mean_m2, sd_m2, min_m2, max_m2, p10_m2, p50_m2, p90_m2

        Raises
        ------
        ValueError
            If patches GeoDataFrame is empty

        Notes
        -----
        Calculates area in square meters from patch geometries.
        Returns comprehensive statistics including mean, std dev, and percentiles.
        """
        if len(patches) == 0:
            raise ValueError("Cannot calculate area statistics for empty patches")

        # Get area in square meters
        if "area_m2" in patches.columns:
            areas = np.asarray(patches["area_m2"].values, dtype=float)
        else:
            areas = np.asarray(patches.geometry.area.values, dtype=float)

        # Calculate statistics
        stats = {
            "mean_m2": float(np.mean(areas)),  # type: ignore
            "sd_m2": float(np.std(areas)),  # type: ignore
            "min_m2": float(np.min(areas)),  # type: ignore
            "max_m2": float(np.max(areas)),  # type: ignore
        }

        # Add percentiles
        percentile_dict = self.calculate_percentiles(areas)
        # Rename keys from p10, p50, p90 to p10_m2, p50_m2, p90_m2
        for key, value in percentile_dict.items():
            stats[f"{key}_m2"] = value

        return stats

    def calculate_core_area_statistics(
        self, patches: gpd.GeoDataFrame, edge_distance: float = 10.0
    ) -> dict:
        """
        Calculate core area statistics (excluding edge pixels).

        Parameters
        ----------
        patches : GeoDataFrame
            Water patch polygons
        edge_distance : float
            Distance (m) to consider as edge (default: 10 m)

        Returns
        -------
        dict
            Statistics dictionary with keys:
            mean_m2, sd_m2, min_m2, max_m2, p10_m2, p50_m2, p90_m2

        Raises
        ------
        ValueError
            If patches GeoDataFrame is empty or edge_distance invalid

        Notes
        -----
        Core area = patch area - edge buffer area.
        Uses shapely.geometry.buffer to create inset polygons.
        Useful for analyzing interior habitat vs. edge effects.
        """
        if len(patches) == 0:
            raise ValueError("Cannot calculate core area statistics for empty patches")

        if edge_distance < 0:
            raise ValueError("edge_distance must be non-negative")

        # Calculate core area for each patch
        core_areas: list[float] = []

        for geom in patches.geometry:
            if edge_distance == 0:
                # No edge to remove
                core_area = geom.area
            else:
                # Create inset buffer (negative distance)
                try:
                    core_geom = geom.buffer(-edge_distance)
                    core_area = core_geom.area if core_geom.is_valid else 0.0
                except Exception:
                    # If buffer fails, use 0
                    core_area = 0.0

            core_areas.append(core_area)

        core_areas_arr = np.asarray(core_areas, dtype=float)

        # Filter out negative or zero core areas
        valid_core_areas = core_areas_arr[core_areas_arr > 0]

        if len(valid_core_areas) == 0:
            # All patches have no core area
            return {
                "mean_m2": 0.0,
                "sd_m2": 0.0,
                "min_m2": 0.0,
                "max_m2": 0.0,
                "p10_m2": 0.0,
                "p50_m2": 0.0,
                "p90_m2": 0.0,
            }

        # Calculate statistics
        stats = {
            "mean_m2": float(np.mean(valid_core_areas)),
            "sd_m2": float(np.std(valid_core_areas)),
            "min_m2": float(np.min(valid_core_areas)),
            "max_m2": float(np.max(valid_core_areas)),
        }

        # Add percentiles
        percentile_dict = self.calculate_percentiles(valid_core_areas)
        for key, value in percentile_dict.items():
            stats[f"{key}_m2"] = value

        return stats

    def calculate_para_statistics(self, patches: gpd.GeoDataFrame) -> dict:
        """
        Calculate Perimeter-Area Ratio statistics.

        Parameters
        ----------
        patches : GeoDataFrame
            Water patch polygons

        Returns
        -------
        dict
            Statistics dictionary with keys:
            mean, sd, min, max, p10, p50, p90

        Raises
        ------
        ValueError
            If patches GeoDataFrame is empty

        Notes
        -----
        PARA = Perimeter / Area (ratio, unitless).
        Higher PARA indicates more complex/elongated shapes.
        Useful for analyzing patch shape complexity.
        """
        if len(patches) == 0:
            raise ValueError("Cannot calculate PARA statistics for empty patches")

        # Calculate PARA for each patch
        para_values: list[float] = []

        for geom in patches.geometry:
            area = geom.area
            perimeter = geom.length

            if area > 0:
                para = perimeter / area
                para_values.append(para)

        para_values_arr = np.asarray(para_values, dtype=float)

        if len(para_values_arr) == 0:
            raise ValueError("No valid patches to calculate PARA")

        # Calculate statistics
        stats = {
            "mean": float(np.mean(para_values_arr)),  # type: ignore
            "sd": float(np.std(para_values_arr)),  # type: ignore
            "min": float(np.min(para_values_arr)),  # type: ignore
            "max": float(np.max(para_values_arr)),  # type: ignore
        }

        # Add percentiles
        percentile_dict = self.calculate_percentiles(para_values_arr)
        stats.update(percentile_dict)

        return stats

    def calculate_percentiles(
        self, values: np.ndarray | list | tuple, percentiles: Optional[list] = None
    ) -> dict:
        """
        Calculate percentile values for an array.

        Parameters
        ----------
        values : array-like
            Input values (numpy array, list, or tuple)
        percentiles : list, optional
            Percentiles to compute (default: [10, 50, 90])

        Returns
        -------
        dict
            Percentile values with keys like 'p10', 'p50', 'p90'

        Raises
        ------
        ValueError
            If values array is empty or invalid percentiles provided

        Notes
        -----
        Uses numpy.percentile for calculation.
        Percentiles should be between 0 and 100.
        """
        if percentiles is None:
            percentiles = [10, 50, 90]

        # Convert to numpy array
        arr = np.asarray(values, dtype=float)

        if len(arr) == 0:
            raise ValueError("Cannot calculate percentiles for empty array")

        # Validate percentiles
        if not all(0 <= p <= 100 for p in percentiles):
            raise ValueError("Percentiles must be between 0 and 100")

        # Calculate percentiles
        result = {}
        for p in percentiles:
            result[f"p{int(p)}"] = float(np.percentile(arr, p))  # type: ignore

        return result
