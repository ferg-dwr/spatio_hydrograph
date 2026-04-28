"""Tests for spatio_hydrograph.connectivity module."""

import geopandas as gpd
import pandas as pd
import pytest

from spatio_hydrograph.config import Config
from spatio_hydrograph.connectivity import ConnectivityAnalyzer


class TestConnectivityAnalyzer:
    """Tests for ConnectivityAnalyzer class."""

    def test_connectivity_analyzer_initialization(self, sample_config: Config) -> None:
        """Test ConnectivityAnalyzer initialization."""
        analyzer = ConnectivityAnalyzer(sample_config)
        assert analyzer.config == sample_config

    @pytest.mark.skip(reason="Not yet implemented")
    def test_analyze_connectivity(
        self,
        sample_config: Config,
        sample_water_polygons: gpd.GeoDataFrame,
    ) -> None:
        """Test connectivity analysis."""
        ConnectivityAnalyzer(sample_config)
        # TODO: Create sample transect lines and implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_calculate_connectivity_statistics(self, sample_config: Config) -> None:
        """Test connectivity statistics calculation."""
        ConnectivityAnalyzer(sample_config)
        # TODO: Implement test
        pass

    @pytest.mark.skip(reason="Not yet implemented")
    def test_identify_bottlenecks(
        self, sample_config: Config, sample_landscape_metrics: pd.DataFrame
    ) -> None:
        """Test bottleneck identification."""
        ConnectivityAnalyzer(sample_config)
        # TODO: Implement test
        pass
