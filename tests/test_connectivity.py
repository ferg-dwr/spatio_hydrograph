"""Tests for spatio_hydrograph.connectivity module."""

import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import LineString

from spatio_hydrograph.config import Config
from spatio_hydrograph.connectivity import ConnectivityAnalyzer


class TestConnectivityAnalyzer:
    """Tests for ConnectivityAnalyzer class."""

    def test_analyzer_initialization(self, sample_config: Config) -> None:
        """Test ConnectivityAnalyzer initialization."""
        analyzer = ConnectivityAnalyzer(sample_config)
        assert analyzer.config == sample_config


class TestAnalyzeConnectivity:
    """Tests for analyze_connectivity method."""

    def test_analyze_connectivity_basic(
        self, sample_config: Config, sample_water_polygons, temp_data_dir
    ) -> None:
        """Test basic connectivity analysis."""
        # Create transect lines

        transects = gpd.GeoDataFrame(
            {
                "transect_id": [0, 1, 2],
                "geometry": [
                    LineString([(0, 20), (40, 20)]),  # Horizontal through polygons
                    LineString([(20, 0), (20, 40)]),  # Vertical through polygons
                    LineString([(50, 50), (60, 60)]),  # Outside polygons
                ],
            },
            crs="EPSG:32610",
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        result = analyzer.analyze_connectivity(sample_water_polygons, transects)

        assert isinstance(result, pd.DataFrame)
        assert "transect_id" in result.columns
        assert "connectivity_m" in result.columns
        assert "num_intersections" in result.columns
        assert "percent_connected" in result.columns
        assert len(result) == 3

    def test_analyze_connectivity_no_water(self, sample_config: Config) -> None:
        """Test error when water_polygons is empty."""
        empty_water = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:32610")
        transects = gpd.GeoDataFrame(
            {"geometry": [LineString([(0, 0), (10, 10)])]}, crs="EPSG:32610"
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="water_polygons"):
            analyzer.analyze_connectivity(empty_water, transects)

    def test_analyze_connectivity_no_transects(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test error when transect_lines is empty."""
        empty_transects = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:32610")

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="transect_lines"):
            analyzer.analyze_connectivity(sample_water_polygons, empty_transects)

    def test_analyze_connectivity_no_intersections(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test connectivity when transects don't intersect water."""
        # Transects far from water
        transects = gpd.GeoDataFrame(
            {
                "geometry": [
                    LineString([(100, 100), (110, 110)]),
                    LineString([(200, 200), (210, 210)]),
                ]
            },
            crs="EPSG:32610",
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        result = analyzer.analyze_connectivity(sample_water_polygons, transects)

        # All should have zero connectivity
        assert (result["connectivity_m"] == 0).all()
        assert (result["num_intersections"] == 0).all()


class TestCalculateConnectivityEndpoints:
    """Tests for calculate_connectivity_endpoints method."""

    def test_calculate_connectivity_endpoints_basic(
        self, sample_config: Config
    ) -> None:
        """Test basic endpoint extraction."""
        transects = gpd.GeoDataFrame(
            {
                "transect_id": [0, 1],
                "geometry": [
                    LineString([(0, 0), (10, 10)]),
                    LineString([(5, 5), (15, 15)]),
                ],
            },
            crs="EPSG:32610",
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        result = analyzer.calculate_connectivity_endpoints(transects)

        assert isinstance(result, pd.DataFrame)
        assert "start_x" in result.columns
        assert "start_y" in result.columns
        assert "end_x" in result.columns
        assert "end_y" in result.columns
        assert len(result) == 2

    def test_calculate_connectivity_endpoints_coordinates(
        self, sample_config: Config
    ) -> None:
        """Test that endpoint coordinates are correct."""
        transects = gpd.GeoDataFrame(
            {"geometry": [LineString([(0, 0), (10, 20)])]}, crs="EPSG:32610"
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        result = analyzer.calculate_connectivity_endpoints(transects)

        assert result.iloc[0]["start_x"] == 0.0
        assert result.iloc[0]["start_y"] == 0.0
        assert result.iloc[0]["end_x"] == 10.0
        assert result.iloc[0]["end_y"] == 20.0

    def test_calculate_connectivity_endpoints_empty(
        self, sample_config: Config
    ) -> None:
        """Test error on empty transect_lines."""
        empty_transects = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:32610")

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="transect_lines"):
            analyzer.calculate_connectivity_endpoints(empty_transects)


class TestCalculateConnectivityStatistics:
    """Tests for calculate_connectivity_statistics method."""

    def test_calculate_connectivity_statistics_basic(
        self, sample_config: Config
    ) -> None:
        """Test basic connectivity statistics calculation."""
        connectivity_data = pd.DataFrame(
            {
                "transect_id": [0, 1, 2, 3, 4],
                "connectivity_m": [10.0, 20.0, 30.0, 40.0, 50.0],
            }
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        stats = analyzer.calculate_connectivity_statistics(connectivity_data)

        assert "mean_connectivity_m" in stats
        assert "sd_connectivity_m" in stats
        assert "min_connectivity_m" in stats
        assert "max_connectivity_m" in stats
        assert "median_connectivity_m" in stats

    def test_calculate_connectivity_statistics_values(
        self, sample_config: Config
    ) -> None:
        """Test that statistics values are correct."""
        connectivity_data = pd.DataFrame(
            {
                "connectivity_m": [10.0, 20.0, 30.0, 40.0, 50.0],
            }
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        stats = analyzer.calculate_connectivity_statistics(connectivity_data)

        assert stats["mean_connectivity_m"] == pytest.approx(30.0)
        assert stats["min_connectivity_m"] == pytest.approx(10.0)
        assert stats["max_connectivity_m"] == pytest.approx(50.0)
        assert stats["median_connectivity_m"] == pytest.approx(30.0)

    def test_calculate_connectivity_statistics_empty(
        self, sample_config: Config
    ) -> None:
        """Test error on empty connectivity_data."""
        empty_data = pd.DataFrame({"connectivity_m": []})

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="connectivity_data is empty"):
            analyzer.calculate_connectivity_statistics(empty_data)

    def test_calculate_connectivity_statistics_missing_column(
        self, sample_config: Config
    ) -> None:
        """Test error when connectivity_m column is missing."""
        bad_data = pd.DataFrame({"other_col": [1, 2, 3]})

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="connectivity_m"):
            analyzer.calculate_connectivity_statistics(bad_data)


class TestIdentifyBottlenecks:
    """Tests for identify_bottlenecks method."""

    def test_identify_bottlenecks_basic(self, sample_config: Config) -> None:
        """Test basic bottleneck identification."""
        connectivity_data = pd.DataFrame(
            {
                "transect_id": [0, 1, 2, 3, 4],
                "connectivity_m": [5.0, 10.0, 15.0, 20.0, 100.0],
            }
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        bottlenecks = analyzer.identify_bottlenecks(
            connectivity_data, threshold_percentile=40.0
        )

        # Should identify transects in bottom 40%
        assert len(bottlenecks) >= 1
        assert bottlenecks["connectivity_m"].max() <= 16.0  # 40th percentile

    def test_identify_bottlenecks_all_high(self, sample_config: Config) -> None:
        """Test when all connectivity values are high."""
        connectivity_data = pd.DataFrame(
            {
                "transect_id": [0, 1, 2],
                "connectivity_m": [100.0, 100.0, 100.0],
            }
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        bottlenecks = analyzer.identify_bottlenecks(
            connectivity_data, threshold_percentile=10.0
        )

        # All should be below 10th percentile (which is 100)
        assert len(bottlenecks) == 3

    def test_identify_bottlenecks_invalid_percentile(
        self, sample_config: Config
    ) -> None:
        """Test error on invalid percentile."""
        connectivity_data = pd.DataFrame(
            {
                "connectivity_m": [1, 2, 3, 4, 5],
            }
        )

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="between 0 and 100"):
            analyzer.identify_bottlenecks(connectivity_data, threshold_percentile=150.0)

    def test_identify_bottlenecks_empty(self, sample_config: Config) -> None:
        """Test error on empty connectivity_data."""
        empty_data = pd.DataFrame({"connectivity_m": []})

        analyzer = ConnectivityAnalyzer(sample_config)
        with pytest.raises(ValueError, match="connectivity_data is empty"):
            analyzer.identify_bottlenecks(empty_data)


class TestConnectivityWorkflow:
    """Integration tests for connectivity analysis workflow."""

    def test_full_connectivity_workflow(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test complete connectivity analysis workflow."""
        # Create transect lines
        transects = gpd.GeoDataFrame(
            {
                "geometry": [
                    LineString([(0, 20), (40, 20)]),
                    LineString([(20, 0), (20, 40)]),
                    LineString([(50, 50), (60, 60)]),
                    LineString([(10, 10), (30, 30)]),
                    LineString([(5, 35), (35, 5)]),
                ]
            },
            crs="EPSG:32610",
        )

        analyzer = ConnectivityAnalyzer(sample_config)

        # Step 1: Analyze connectivity
        connectivity = analyzer.analyze_connectivity(sample_water_polygons, transects)
        assert len(connectivity) == 5

        # Step 2: Calculate endpoints
        endpoints = analyzer.calculate_connectivity_endpoints(transects)
        assert len(endpoints) == 5

        # Step 3: Calculate statistics
        stats = analyzer.calculate_connectivity_statistics(connectivity)
        assert stats["mean_connectivity_m"] >= 0

        # Step 4: Identify bottlenecks
        bottlenecks = analyzer.identify_bottlenecks(
            connectivity, threshold_percentile=50.0
        )
        assert len(bottlenecks) >= 0
        assert len(bottlenecks) <= len(connectivity)
