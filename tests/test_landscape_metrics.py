"""Tests for spatio_hydrograph.landscape_metrics module."""

import geopandas as gpd
import pandas as pd
import pytest

from spatio_hydrograph.config import Config
from spatio_hydrograph.landscape_metrics import LandscapeMetrics


class TestLandscapeMetrics:
    """Tests for LandscapeMetrics class."""

    def test_landscape_metrics_initialization(self, sample_config: Config) -> None:
        """Test LandscapeMetrics initialization."""
        metrics = LandscapeMetrics(sample_config)
        assert metrics.config == sample_config

    @pytest.mark.skip(reason="Not yet implemented")
    def test_calculate_patch_metrics(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test patch metrics calculation."""
        metrics = LandscapeMetrics(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_calculate_class_metrics(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test class metrics calculation."""
        metrics = LandscapeMetrics(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_calculate_area_statistics(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test area statistics calculation."""
        metrics = LandscapeMetrics(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_calculate_percentiles(self, sample_config: Config) -> None:
        """Test percentile calculation."""
        metrics = LandscapeMetrics(sample_config)
        # TODO: Implement test
        pass
