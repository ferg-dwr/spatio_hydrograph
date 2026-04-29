"""Tests for spatio_hydrograph.visualization module."""

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend before importing pyplot

from pathlib import Path

import pandas as pd
import pytest

from spatio_hydrograph.config import Config
from spatio_hydrograph.visualization import Visualizer


class TestVisualizer:
    """Tests for Visualizer class."""

    def test_visualizer_initialization(self, sample_config: Config) -> None:
        """Test Visualizer initialization with default parameters."""
        viz = Visualizer(sample_config)
        assert viz.config == sample_config
        assert viz.figsize == (10, 6)
        assert viz.dpi == 300
        assert viz.show is False

    def test_visualizer_initialization_custom(self, sample_config: Config) -> None:
        """Test Visualizer initialization with custom parameters."""
        viz = Visualizer(sample_config, figsize=(12, 8), dpi=150, show=True)
        assert viz.figsize == (12, 8)
        assert viz.dpi == 150
        assert viz.show is True


class TestPlotHabitatTimeSeries:
    """Tests for plot_habitat_time_series method."""

    def test_plot_habitat_time_series_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic habitat time series plot."""
        # Create sample data
        dates = pd.date_range("2023-10-01", periods=10, freq="D")
        habitat_data = pd.DataFrame(
            {
                "date": list(dates) * 3,
                "habitat": ["First"] * 10 + ["Middle"] * 10 + ["Last"] * 10,
                "inundated_area_ha": [5.0, 10.0, 15.0, 20.0, 15.0, 10.0, 5.0, 0, 0, 0]
                * 3,
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "habitat_timeseries.png"

        # Should not raise error
        viz.plot_habitat_time_series(habitat_data, output_file)

        # File should be created
        assert output_file.exists()

    def test_plot_habitat_time_series_missing_columns(
        self, sample_config: Config
    ) -> None:
        """Test error on missing required columns."""
        habitat_data = pd.DataFrame(
            {
                "date": ["2023-10-01"],
                # Missing 'habitat' and 'inundated_area_ha'
            }
        )

        viz = Visualizer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            viz.plot_habitat_time_series(habitat_data)


class TestPlotPercentWater:
    """Tests for plot_percent_water method."""

    def test_plot_percent_water_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic percent water plot."""
        habitat_data = pd.DataFrame(
            {
                "habitat": ["First", "Middle", "Last"],
                "percent_inundated": [50.0, 75.0, 25.0],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "percent_water.png"

        viz.plot_percent_water(habitat_data, output_file)

        assert output_file.exists()

    def test_plot_percent_water_missing_columns(self, sample_config: Config) -> None:
        """Test error on missing required columns."""
        habitat_data = pd.DataFrame(
            {
                "habitat": ["First", "Middle"],
                # Missing 'percent_inundated'
            }
        )

        viz = Visualizer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            viz.plot_percent_water(habitat_data)


class TestPlotLateralConnectivity:
    """Tests for plot_lateral_connectivity method."""

    def test_plot_lateral_connectivity_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic lateral connectivity plot."""
        dates = pd.date_range("2023-10-01", periods=10, freq="D")
        connectivity_data = pd.DataFrame(
            {
                "date": dates,
                "mean_connectivity_m": [
                    10.0,
                    15.0,
                    20.0,
                    25.0,
                    30.0,
                    25.0,
                    20.0,
                    15.0,
                    10.0,
                    5.0,
                ],
                "sd_connectivity_m": [2.0, 2.5, 3.0, 3.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.0],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "connectivity_timeseries.png"

        viz.plot_lateral_connectivity(connectivity_data, output_file)

        assert output_file.exists()

    def test_plot_lateral_connectivity_no_sd(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test plot without SD column."""
        dates = pd.date_range("2023-10-01", periods=5, freq="D")
        connectivity_data = pd.DataFrame(
            {
                "date": dates,
                "mean_connectivity_m": [10.0, 15.0, 20.0, 15.0, 10.0],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "connectivity_no_sd.png"

        viz.plot_lateral_connectivity(connectivity_data, output_file)

        assert output_file.exists()


class TestPlotPatchSizeDistribution:
    """Tests for plot_patch_size_distribution method."""

    def test_plot_patch_size_distribution_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic patch size distribution plot."""
        dates = pd.date_range("2023-10-01", periods=5, freq="D")
        landscape_data = pd.DataFrame(
            {
                "date": dates,
                "mean_area_m2": [1000, 1500, 2000, 1500, 1000],
                "p10_area_m2": [500, 750, 1000, 750, 500],
                "p50_area_m2": [1000, 1500, 2000, 1500, 1000],
                "p90_area_m2": [2000, 3000, 4000, 3000, 2000],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "patch_size_distribution.png"

        viz.plot_patch_size_distribution(landscape_data, output_file)

        assert output_file.exists()

    def test_plot_patch_size_distribution_missing_columns(
        self, sample_config: Config
    ) -> None:
        """Test error on missing required columns."""
        landscape_data = pd.DataFrame(
            {
                "date": ["2023-10-01"],
                "mean_area_m2": [1000],
                # Missing percentile columns
            }
        )

        viz = Visualizer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            viz.plot_patch_size_distribution(landscape_data)


class TestPlotCoreAreaDistribution:
    """Tests for plot_core_area_distribution method."""

    def test_plot_core_area_distribution_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic core area distribution plot."""
        dates = pd.date_range("2023-10-01", periods=5, freq="D")
        landscape_data = pd.DataFrame(
            {
                "date": dates,
                "mean_core_area_m2": [500, 750, 1000, 750, 500],
                "p10_core_area_m2": [200, 300, 400, 300, 200],
                "p50_core_area_m2": [500, 750, 1000, 750, 500],
                "p90_core_area_m2": [1000, 1500, 2000, 1500, 1000],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "core_area_distribution.png"

        viz.plot_core_area_distribution(landscape_data, output_file)

        assert output_file.exists()


class TestPlotComparativeSensors:
    """Tests for plot_comparative_sensors method."""

    def test_plot_comparative_sensors_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test basic comparative sensors plot."""
        dates = pd.date_range("2023-10-01", periods=5, freq="D")
        s1_data = pd.DataFrame(
            {
                "date": dates,
                "inundated_area_ha": [10.0, 15.0, 20.0, 15.0, 10.0],
            }
        )
        s2_data = pd.DataFrame(
            {
                "date": dates,
                "inundated_area_ha": [12.0, 16.0, 22.0, 16.0, 11.0],
            }
        )

        viz = Visualizer(sample_config)
        output_file = temp_data_dir / "sentinel_comparison.png"

        viz.plot_comparative_sensors(s1_data, s2_data, output_file)

        assert output_file.exists()

    def test_plot_comparative_sensors_missing_columns_s1(
        self, sample_config: Config
    ) -> None:
        """Test error on missing columns in S1 data."""
        s1_data = pd.DataFrame({"other_col": [1, 2, 3]})
        s2_data = pd.DataFrame(
            {
                "date": ["2023-10-01"],
                "inundated_area_ha": [10.0],
            }
        )

        viz = Visualizer(sample_config)
        with pytest.raises(ValueError, match="s1_data"):
            viz.plot_comparative_sensors(s1_data, s2_data)


class TestVisualizerWorkflow:
    """Integration tests for visualization workflow."""

    def test_full_visualization_workflow(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test complete visualization workflow."""
        viz = Visualizer(sample_config)

        # Create sample data
        dates = pd.date_range("2023-10-01", periods=10, freq="D")

        # Habitat time series
        habitat_data = pd.DataFrame(
            {
                "date": list(dates) * 2,
                "habitat": ["First"] * 10 + ["Last"] * 10,
                "inundated_area_ha": [5.0, 10.0, 15.0, 20.0, 15.0, 10.0, 5.0, 0, 0, 0]
                * 2,
            }
        )

        # Percent water
        percent_data = pd.DataFrame(
            {
                "habitat": ["First", "Last"],
                "percent_inundated": [50.0, 75.0],
            }
        )

        # Connectivity
        connectivity_data = pd.DataFrame(
            {
                "date": dates,
                "mean_connectivity_m": [10.0] * 10,
            }
        )

        # Landscape metrics
        landscape_data = pd.DataFrame(
            {
                "date": dates,
                "mean_area_m2": [1000] * 10,
                "p10_area_m2": [500] * 10,
                "p50_area_m2": [1000] * 10,
                "p90_area_m2": [2000] * 10,
                "mean_core_area_m2": [500] * 10,
                "p10_core_area_m2": [200] * 10,
                "p50_core_area_m2": [500] * 10,
                "p90_core_area_m2": [1000] * 10,
            }
        )

        # Sentinel comparison
        s1_data = pd.DataFrame(
            {
                "date": dates,
                "inundated_area_ha": [10.0] * 10,
            }
        )
        s2_data = pd.DataFrame(
            {
                "date": dates,
                "inundated_area_ha": [12.0] * 10,
            }
        )

        # Create all plots
        viz.plot_habitat_time_series(habitat_data, temp_data_dir / "habitat.png")
        viz.plot_percent_water(percent_data, temp_data_dir / "percent.png")
        viz.plot_lateral_connectivity(
            connectivity_data, temp_data_dir / "connectivity.png"
        )
        viz.plot_patch_size_distribution(
            landscape_data, temp_data_dir / "patch_size.png"
        )
        viz.plot_core_area_distribution(landscape_data, temp_data_dir / "core_area.png")
        viz.plot_comparative_sensors(s1_data, s2_data, temp_data_dir / "sensors.png")

        # All files should exist
        assert (temp_data_dir / "habitat.png").exists()
        assert (temp_data_dir / "percent.png").exists()
        assert (temp_data_dir / "connectivity.png").exists()
        assert (temp_data_dir / "patch_size.png").exists()
        assert (temp_data_dir / "core_area.png").exists()
        assert (temp_data_dir / "sensors.png").exists()
