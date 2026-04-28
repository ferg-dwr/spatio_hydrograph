"""Tests for spatio_hydrograph.raster_processing module."""

import geopandas as gpd
import pytest

from spatio_hydrograph.config import Config
from spatio_hydrograph.raster_processing import RasterProcessor


class TestRasterProcessor:
    """Tests for RasterProcessor class."""

    def test_processor_initialization(self, sample_config: Config) -> None:
        """Test RasterProcessor initialization."""
        processor = RasterProcessor(sample_config)
        assert processor.config == sample_config
        assert processor.habitat_gdf is None

    @pytest.mark.skip(reason="Requires shapefiles")
    def test_load_habitat_polygons(
        self, sample_config: Config, sample_habitat_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test loading habitat polygons."""
        # TODO: Create test shapefile and implement
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_raster_to_polygons(self, sample_config: Config, sample_raster) -> None:
        """Test raster-to-vector conversion."""
        RasterProcessor(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_filter_by_area(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test polygon area filtering."""
        RasterProcessor(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_intersect_with_habitats(
        self,
        sample_config: Config,
        sample_water_polygons: gpd.GeoDataFrame,
        sample_habitat_polygons: gpd.GeoDataFrame,
    ) -> None:
        """Test polygon intersection."""
        RasterProcessor(sample_config)
        # TODO: Implement test
        pass
