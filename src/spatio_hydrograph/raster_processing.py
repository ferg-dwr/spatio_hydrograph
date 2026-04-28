"""
Raster-to-vector conversion and polygon processing.

Handles conversion of water classification rasters to vector polygons,
filtering by area, and intersection with habitat polygons.
"""

from pathlib import Path

import geopandas as gpd
import rioxarray  # noqa: F401

from .config import Config


class RasterProcessor:
    """Process raster water classification maps to vector polygons."""

    def __init__(self, config: Config) -> None:
        """
        Initialize raster processor.

        Parameters
        ----------
        config : Config
            Configuration object
        """
        self.config = config
        self.habitat_gdf: gpd.GeoDataFrame | None = None

    def load_habitat_polygons(self) -> gpd.GeoDataFrame:
        """
        Load habitat polygons from shapefile.

        Returns
        -------
        GeoDataFrame
            Habitat polygons with attributes
        """
        if self.config.shapefiles is None:
            raise ValueError("Shapefiles configuration not provided")

        self.habitat_gdf = gpd.read_file(self.config.shapefiles.habitat_polygons)
        return self.habitat_gdf

    def raster_to_polygons(self, raster_path: str | Path) -> gpd.GeoDataFrame:
        """
        Convert water classification raster to polygons.

        Parameters
        ----------
        raster_path : str or Path
            Path to water classification raster (TIF)

        Returns
        -------
        GeoDataFrame
            Polygons of water features with area (m²)
        """
        # TODO: Implement raster-to-vector conversion
        raise NotImplementedError("raster_to_polygons not yet implemented")

    def filter_by_area(
        self,
        polygons: gpd.GeoDataFrame,
        min_area_m2: float | None = None,
    ) -> gpd.GeoDataFrame:
        """
        Filter polygons by minimum area.

        Parameters
        ----------
        polygons : GeoDataFrame
            Input polygons
        min_area_m2 : float, optional
            Minimum area in square meters (uses config if not provided)

        Returns
        -------
        GeoDataFrame
            Filtered polygons
        """
        # TODO: Implement area filtering
        raise NotImplementedError("filter_by_area not yet implemented")

    def intersect_with_habitats(self, polygons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Intersect water polygons with habitat polygons.

        Parameters
        ----------
        polygons : GeoDataFrame
            Water polygons to intersect

        Returns
        -------
        GeoDataFrame
            Intersected polygons with habitat attributes
        """
        # TODO: Implement polygon intersection
        raise NotImplementedError("intersect_with_habitats not yet implemented")

    def get_polygon_centroids(self, polygons: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Get centroids of polygons.

        Parameters
        ----------
        polygons : GeoDataFrame
            Input polygons

        Returns
        -------
        GeoDataFrame
            Point geometries at polygon centroids
        """
        # TODO: Implement centroid extraction
        raise NotImplementedError("get_polygon_centroids not yet implemented")
