"""Tests for spatio_hydrograph.landscape_metrics module."""

import numpy as np
import pandas as pd
import pytest
import xarray as xr

from spatio_hydrograph.config import Config
from spatio_hydrograph.landscape_metrics import LandscapeMetrics


class TestLandscapeMetrics:
    """Tests for LandscapeMetrics class."""

    def test_landscape_metrics_initialization(self, sample_config: Config) -> None:
        """Test LandscapeMetrics initialization."""
        metrics = LandscapeMetrics(sample_config)
        assert metrics.config == sample_config


class TestCalculatePercentiles:
    """Tests for calculate_percentiles helper method."""

    def test_calculate_percentiles_default(self, sample_config: Config) -> None:
        """Test percentile calculation with default percentiles."""
        metrics = LandscapeMetrics(sample_config)
        values = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        result = metrics.calculate_percentiles(values)

        assert "p10" in result
        assert "p50" in result
        assert "p90" in result
        assert isinstance(result["p10"], float)

    def test_calculate_percentiles_custom(self, sample_config: Config) -> None:
        """Test percentile calculation with custom percentiles."""
        metrics = LandscapeMetrics(sample_config)
        values = np.array([0, 25, 50, 75, 100])

        result = metrics.calculate_percentiles(values, percentiles=[25, 75])

        assert "p25" in result
        assert "p75" in result
        assert result["p25"] == pytest.approx(25.0)
        assert result["p75"] == pytest.approx(75.0)

    def test_calculate_percentiles_empty_array(self, sample_config: Config) -> None:
        """Test error on empty array."""
        metrics = LandscapeMetrics(sample_config)
        values = np.array([])

        with pytest.raises(ValueError, match="Cannot calculate percentiles"):
            metrics.calculate_percentiles(values)

    def test_calculate_percentiles_invalid_percentiles(
        self, sample_config: Config
    ) -> None:
        """Test error on invalid percentiles."""
        metrics = LandscapeMetrics(sample_config)
        values = np.array([1, 2, 3, 4, 5])

        with pytest.raises(ValueError, match="between 0 and 100"):
            metrics.calculate_percentiles(values, percentiles=[150])


class TestCalculateAreaStatistics:
    """Tests for calculate_area_statistics method."""

    def test_calculate_area_statistics_basic(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test basic area statistics calculation."""
        metrics = LandscapeMetrics(sample_config)
        stats = metrics.calculate_area_statistics(sample_water_polygons)

        assert "mean_m2" in stats
        assert "sd_m2" in stats
        assert "min_m2" in stats
        assert "max_m2" in stats
        assert "p10_m2" in stats
        assert "p50_m2" in stats
        assert "p90_m2" in stats

    def test_calculate_area_statistics_values(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test that statistics values are reasonable."""
        metrics = LandscapeMetrics(sample_config)
        stats = metrics.calculate_area_statistics(sample_water_polygons)

        # All test polygons are 1600 m²
        assert stats["mean_m2"] == pytest.approx(1600.0)
        assert stats["min_m2"] == pytest.approx(1600.0)
        assert stats["max_m2"] == pytest.approx(1600.0)

    def test_calculate_area_statistics_empty(self, sample_config: Config) -> None:
        """Test error on empty patches."""
        import geopandas as gpd

        empty_gdf = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:32610")
        metrics = LandscapeMetrics(sample_config)

        with pytest.raises(ValueError, match="Cannot calculate area statistics"):
            metrics.calculate_area_statistics(empty_gdf)


class TestCalculateCoreAreaStatistics:
    """Tests for calculate_core_area_statistics method."""

    def test_calculate_core_area_statistics_basic(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test basic core area calculation."""
        metrics = LandscapeMetrics(sample_config)
        stats = metrics.calculate_core_area_statistics(
            sample_water_polygons, edge_distance=10.0
        )

        assert "mean_m2" in stats
        assert "sd_m2" in stats
        assert "p50_m2" in stats

    def test_calculate_core_area_statistics_no_edge(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test core area with no edge (distance=0)."""
        metrics = LandscapeMetrics(sample_config)
        stats = metrics.calculate_core_area_statistics(
            sample_water_polygons, edge_distance=0.0
        )

        # With edge_distance=0, core area should equal total area
        total_stats = metrics.calculate_area_statistics(sample_water_polygons)
        assert stats["mean_m2"] == pytest.approx(total_stats["mean_m2"])

    def test_calculate_core_area_statistics_negative_distance(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test error on negative edge distance."""
        metrics = LandscapeMetrics(sample_config)

        with pytest.raises(ValueError, match="edge_distance must be non-negative"):
            metrics.calculate_core_area_statistics(
                sample_water_polygons, edge_distance=-10.0
            )


class TestCalculateParaStatistics:
    """Tests for calculate_para_statistics method."""

    def test_calculate_para_statistics_basic(
        self, sample_config: Config, sample_water_polygons
    ) -> None:
        """Test basic PARA calculation."""
        metrics = LandscapeMetrics(sample_config)
        stats = metrics.calculate_para_statistics(sample_water_polygons)

        assert "mean" in stats
        assert "sd" in stats
        assert "p10" in stats
        assert "p50" in stats
        assert "p90" in stats
        assert all(v >= 0 for v in stats.values())

    def test_calculate_para_statistics_empty(self, sample_config: Config) -> None:
        """Test error on empty patches."""
        import geopandas as gpd

        empty_gdf = gpd.GeoDataFrame({"geometry": []}, crs="EPSG:32610")
        metrics = LandscapeMetrics(sample_config)

        with pytest.raises(ValueError, match="Cannot calculate PARA"):
            metrics.calculate_para_statistics(empty_gdf)


class TestCalculatePatchMetrics:
    """Tests for calculate_patch_metrics method."""

    def test_calculate_patch_metrics_basic(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test basic patch metrics calculation."""
        metrics = LandscapeMetrics(sample_config)
        result = metrics.calculate_patch_metrics(sample_raster)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "total_patches" in result.columns
        assert "total_area_m2" in result.columns
        assert "mean_area_m2" in result.columns
        assert "mean_para" in result.columns

    def test_calculate_patch_metrics_has_percentiles(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test that patch metrics include percentiles."""
        metrics = LandscapeMetrics(sample_config)
        result = metrics.calculate_patch_metrics(sample_raster)

        percentile_cols = [
            col
            for col in result.columns
            if "p10" in col or "p50" in col or "p90" in col
        ]
        assert len(percentile_cols) > 0

    def test_calculate_patch_metrics_empty_raster(self, sample_config: Config) -> None:
        """Test error on empty raster."""
        empty_raster = xr.DataArray(
            np.zeros((10, 10)),
            dims=["y", "x"],
            coords={"y": np.arange(10), "x": np.arange(10)},
        )
        empty_raster.rio.write_crs("EPSG:32610", inplace=True)

        metrics = LandscapeMetrics(sample_config)

        with pytest.raises(ValueError, match="No water features"):
            metrics.calculate_patch_metrics(empty_raster)


class TestCalculateClassMetrics:
    """Tests for calculate_class_metrics method."""

    def test_calculate_class_metrics_basic(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test basic class metrics calculation."""
        metrics = LandscapeMetrics(sample_config)
        result = metrics.calculate_class_metrics(sample_raster)

        assert isinstance(result, pd.DataFrame)
        assert "clumpiness" in result.columns
        assert "cohesion" in result.columns
        assert len(result) == 1

    def test_calculate_class_metrics_value_range(
        self, sample_config: Config, sample_raster
    ) -> None:
        """Test that metrics are in valid range [0, 1]."""
        metrics = LandscapeMetrics(sample_config)
        result = metrics.calculate_class_metrics(sample_raster)

        clumpiness = result.iloc[0]["clumpiness"]
        cohesion = result.iloc[0]["cohesion"]

        assert 0 <= clumpiness <= 1
        assert 0 <= cohesion <= 1

    def test_calculate_class_metrics_no_water(self, sample_config: Config) -> None:
        """Test error when no water features."""
        dry_raster = xr.DataArray(
            np.zeros((10, 10)),
            dims=["y", "x"],
            coords={"y": np.arange(10), "x": np.arange(10)},
        )
        dry_raster.rio.write_crs("EPSG:32610", inplace=True)

        metrics = LandscapeMetrics(sample_config)

        with pytest.raises(ValueError, match="No water features"):
            metrics.calculate_class_metrics(dry_raster)


class TestLandscapeMetricsWorkflow:
    """Integration tests for landscape metrics workflow."""

    def test_full_metrics_workflow(
        self, sample_config: Config, sample_raster, sample_water_polygons
    ) -> None:
        """Test complete landscape metrics workflow."""
        metrics = LandscapeMetrics(sample_config)

        # Step 1: Calculate patch metrics from raster
        patch_metrics = metrics.calculate_patch_metrics(sample_raster)
        assert patch_metrics is not None

        # Step 2: Calculate class metrics from raster
        class_metrics = metrics.calculate_class_metrics(sample_raster)
        assert class_metrics is not None

        # Step 3: Calculate individual polygon statistics
        area_stats = metrics.calculate_area_statistics(sample_water_polygons)
        assert area_stats is not None

        core_stats = metrics.calculate_core_area_statistics(sample_water_polygons)
        assert core_stats is not None

        para_stats = metrics.calculate_para_statistics(sample_water_polygons)
        assert para_stats is not None

        # All should complete without error
        assert len(patch_metrics) == 1
        assert len(class_metrics) == 1
