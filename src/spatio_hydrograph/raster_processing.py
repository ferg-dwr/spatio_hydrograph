"""
Raster-to-vector conversion and polygon processing.

Handles conversion of water classification rasters to vector polygons,
filtering by area, and intersection with habitat polygons.
"""

from pathlib import Path

import geopandas as gpd
import numpy as np
import rioxarray  # noqa: F401
import xarray as xr
from rasterio.features import shapes
from shapely.geometry import shape

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

        Raises
        ------
        FileNotFoundError
            If raster file does not exist
        ValueError
            If raster has no valid data or CRS

        Notes
        -----
        Converts raster pixels with value 1 (water) to polygons.
        Calculates area in square meters for each polygon.
        """
        raster_path = Path(raster_path)

        if not raster_path.exists():
            raise FileNotFoundError(f"Raster file not found: {raster_path}")

        # Open raster with rioxarray
        raster = xr.open_dataarray(raster_path)

        # Get CRS if available
        crs = raster.rio.crs
        if crs is None:
            raise ValueError(f"Raster {raster_path} has no CRS defined")

        # Get the data as numpy array
        data = raster.values

        if data.size == 0:
            raise ValueError(f"Raster {raster_path} has no data")

        # Convert raster to polygons (water pixels = 1)
        # Use rasterio.features.shapes which yields (geom, value) tuples
        polygon_list = []
        for geom, value in shapes(
            data.astype(np.uint8), transform=raster.rio.transform()
        ):
            # Only keep water features (value == 1)
            if value == 1:
                polygon_list.append(shape(geom))

        if not polygon_list:
            # Return empty GeoDataFrame with proper schema
            return gpd.GeoDataFrame(
                {"water_pixel": [], "geometry": []},
                crs=crs,
            )

        # Create GeoDataFrame from polygons
        gdf = gpd.GeoDataFrame(
            {"water_pixel": [1] * len(polygon_list), "geometry": polygon_list},
            crs=crs,
        )

        # Calculate area in square meters
        gdf["area_m2"] = gdf.geometry.area

        return gdf

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
            Filtered polygons with only those >= min_area_m2

        Raises
        ------
        ValueError
            If min_area_m2 is invalid or polygons has no 'area_m2' column

        Notes
        -----
        Removes small polygons that are below the minimum area threshold.
        Useful for removing noise/artifacts from water classification.
        """
        # Use config value if not provided
        if min_area_m2 is None:
            min_area_m2 = self.config.min_polygon_area_m2

        if min_area_m2 <= 0:
            raise ValueError(f"min_area_m2 must be positive, got {min_area_m2}")

        # Check if area column exists, if not calculate it
        if "area_m2" not in polygons.columns:
            polygons = polygons.copy()
            polygons["area_m2"] = polygons.geometry.area

        # Filter polygons
        filtered = polygons[polygons["area_m2"] >= min_area_m2].copy()

        return filtered

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
            Intersected polygons with habitat attributes (habitat name, etc.)

        Raises
        ------
        ValueError
            If shapefiles configuration not provided or habitat CRS is None
        RuntimeError
            If habitat polygons not loaded

        Notes
        -----
        Uses spatial intersection to determine which habitat each water
        polygon overlaps. Returns only the intersection geometries.
        Preserves habitat attributes from the habitat polygons.
        """
        # Load habitat polygons if not already loaded
        if self.habitat_gdf is None:
            self.load_habitat_polygons()

        assert self.habitat_gdf is not None  # For type checker

        # Validate habitat CRS
        if self.habitat_gdf.crs is None:
            raise ValueError("Habitat polygons have no CRS defined")

        # Ensure both GeoDataFrames have same CRS
        if polygons.crs != self.habitat_gdf.crs:
            polygons = polygons.to_crs(self.habitat_gdf.crs)

        # Perform spatial join (intersection)
        # sjoin finds all polygons that intersect with habitats
        intersected = gpd.sjoin(
            polygons,
            self.habitat_gdf,
            how="inner",
            predicate="intersects",
        )

        # Remove the index_right column (from spatial join)
        if "index_right" in intersected.columns:
            intersected = intersected.drop(columns=["index_right"])

        return intersected

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
            Point geometries at polygon centroids with original attributes

        Notes
        -----
        Converts polygon geometries to their centroid points.
        Preserves all other columns/attributes from input GeoDataFrame.
        Useful for visualization or as representative points for polygons.
        """
        centroids = polygons.copy()
        centroids.geometry = centroids.geometry.centroid

        return centroids
