"""Tests for spatio_hydrograph.habitat_analysis module."""

import geopandas as gpd
import pandas as pd
import pytest

from spatio_hydrograph.config import Config
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer


class TestHabitatAnalyzer:
    """Tests for HabitatAnalyzer class."""

    def test_analyzer_initialization(self, sample_config: Config) -> None:
        """Test HabitatAnalyzer initialization."""
        analyzer = HabitatAnalyzer(sample_config)
        assert analyzer.config == sample_config


class TestCalculateHabitatAreas:
    """Tests for calculate_habitat_areas method."""

    def test_calculate_habitat_areas_basic(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test basic habitat area calculation."""
        # Add habitat column to water polygons
        water_with_habitat = sample_water_polygons.copy()
        water_with_habitat["habitat"] = ["First", "Middle", "Last"]

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.calculate_habitat_areas(water_with_habitat)

        # Check result structure
        assert isinstance(result, pd.DataFrame)
        assert "habitat" in result.columns
        assert "inundated_area_ha" in result.columns
        assert "num_features" in result.columns
        assert len(result) == 3

    def test_calculate_habitat_areas_aggregation(self, sample_config: Config) -> None:
        """Test that areas are properly aggregated by habitat."""
        # Create test data with multiple polygons per habitat
        from shapely.geometry import Polygon

        polygon = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        data = {
            "habitat": ["First", "First", "Middle"],
            "area_m2": [10000, 15000, 20000],  # First: 25000 m² = 2.5 ha
            "geometry": [polygon, polygon, polygon],
        }
        water_df = gpd.GeoDataFrame(data, crs="EPSG:32610")

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.calculate_habitat_areas(water_df)

        # Check aggregation
        first_row = result[result["habitat"] == "First"].iloc[0]
        assert first_row["inundated_area_ha"] == pytest.approx(2.5)
        assert first_row["num_features"] == 2

    def test_calculate_habitat_areas_missing_columns(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test error on missing required columns."""
        # Remove area_m2 column
        water_no_area = sample_water_polygons.drop(columns=["area_m2"])

        analyzer = HabitatAnalyzer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer.calculate_habitat_areas(water_no_area)

    def test_calculate_habitat_areas_m2_to_ha_conversion(
        self, sample_config: Config
    ) -> None:
        """Test that conversion from m² to ha is correct."""
        from shapely.geometry import Polygon

        polygon = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        data = {
            "habitat": ["Test"],
            "area_m2": [100000],  # 10 hectares
            "geometry": [polygon],
        }
        water_df = gpd.GeoDataFrame(data, crs="EPSG:32610")

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.calculate_habitat_areas(water_df)

        assert result.iloc[0]["inundated_area_ha"] == pytest.approx(10.0)


class TestCalculatePercentInundated:
    """Tests for calculate_percent_inundated method."""

    def test_calculate_percent_inundated_no_config(self, sample_config: Config) -> None:
        """Test percent calculation without habitat area config."""
        habitat_areas = pd.DataFrame(
            {
                "habitat": ["First", "Middle"],
                "inundated_area_ha": [5.0, 10.0],
            }
        )

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.calculate_percent_inundated(habitat_areas)

        # Should return data with percent_inundated as NA
        assert "percent_inundated" in result.columns
        assert result["percent_inundated"].isna().all()

    def test_calculate_percent_inundated_missing_columns(
        self, sample_config: Config
    ) -> None:
        """Test error on missing required columns."""
        habitat_areas = pd.DataFrame({"habitat": ["First"]})

        analyzer = HabitatAnalyzer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer.calculate_percent_inundated(habitat_areas)


class TestIdentifyFloodStatus:
    """Tests for identify_flood_status method."""

    def test_identify_flood_status_all_dry(self, sample_config: Config) -> None:
        """Test flood status when no habitats are flooded."""
        habitat_areas = pd.DataFrame(
            {
                "habitat": ["First", "Middle", "Last"],
                "inundated_area_ha": [0.0, 0.0, 0.0],
            }
        )

        analyzer = HabitatAnalyzer(sample_config)
        status = analyzer.identify_flood_status(habitat_areas)

        assert isinstance(status, dict)
        assert all(not v for v in status.values())

    def test_identify_flood_status_mixed(self, sample_config: Config) -> None:
        """Test flood status with mixed flooded/dry habitats."""
        habitat_areas = pd.DataFrame(
            {
                "habitat": ["First", "Middle", "Last"],
                "inundated_area_ha": [5.0, 0.0, 10.0],
            }
        )

        analyzer = HabitatAnalyzer(sample_config)
        status = analyzer.identify_flood_status(habitat_areas)

        assert status["First"] is True
        assert status["Middle"] is False
        assert status["Last"] is True

    def test_identify_flood_status_all_flooded(self, sample_config: Config) -> None:
        """Test flood status when all habitats are flooded."""
        habitat_areas = pd.DataFrame(
            {
                "habitat": ["First", "Middle", "Last"],
                "inundated_area_ha": [5.0, 10.0, 15.0],
            }
        )

        analyzer = HabitatAnalyzer(sample_config)
        status = analyzer.identify_flood_status(habitat_areas)

        assert all(v for v in status.values())

    def test_identify_flood_status_missing_columns(self, sample_config: Config) -> None:
        """Test error on missing required columns."""
        habitat_areas = pd.DataFrame({"habitat": ["First"]})

        analyzer = HabitatAnalyzer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer.identify_flood_status(habitat_areas)


class TestAggregateByWaterYear:
    """Tests for aggregate_by_water_year method."""

    def test_aggregate_by_water_year_basic(self, sample_config: Config) -> None:
        """Test basic water year aggregation."""
        # Create time series data
        dates = pd.date_range("2023-10-01", periods=30, freq="D")
        data = {
            "date": dates,
            "habitat": ["First"] * 30,
            "inundated_area_ha": [0.0] * 10 + [5.0] * 15 + [0.0] * 5,  # 15 days flooded
        }
        time_series = pd.DataFrame(data)

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.aggregate_by_water_year(time_series)

        # Check result structure
        assert isinstance(result, pd.DataFrame)
        assert "habitat" in result.columns
        assert "max_inundated_area_ha" in result.columns
        assert "mean_inundated_area_ha" in result.columns
        assert "num_inundation_days" in result.columns
        assert "first_flood_date" in result.columns
        assert "last_flood_date" in result.columns

    def test_aggregate_by_water_year_statistics(self, sample_config: Config) -> None:
        """Test that statistics are calculated correctly."""
        dates = pd.date_range("2023-10-01", periods=20, freq="D")
        data = {
            "date": dates,
            "habitat": ["First"] * 20,
            "inundated_area_ha": [0.0] * 5 + [5.0, 10.0, 15.0, 10.0, 5.0] + [0.0] * 10,
        }
        time_series = pd.DataFrame(data)

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.aggregate_by_water_year(time_series)

        row = result.iloc[0]
        assert row["max_inundated_area_ha"] == pytest.approx(15.0)
        assert row["num_inundation_days"] == 5
        assert row["first_flood_date"] == pd.Timestamp("2023-10-06")
        assert row["last_flood_date"] == pd.Timestamp("2023-10-10")

    def test_aggregate_by_water_year_multiple_habitats(
        self, sample_config: Config
    ) -> None:
        """Test aggregation with multiple habitats."""
        dates = pd.date_range("2023-10-01", periods=10, freq="D")
        data = {
            "date": list(dates) * 2,
            "habitat": ["First"] * 10 + ["Middle"] * 10,
            "inundated_area_ha": [5.0] * 10 + [0.0] * 10,
        }
        time_series = pd.DataFrame(data)

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.aggregate_by_water_year(time_series)

        assert len(result) == 2
        assert result.iloc[0]["num_inundation_days"] == 10
        assert result.iloc[1]["num_inundation_days"] == 0

    def test_aggregate_by_water_year_missing_columns(
        self, sample_config: Config
    ) -> None:
        """Test error on missing required columns."""
        time_series = pd.DataFrame({"date": ["2023-10-01"]})

        analyzer = HabitatAnalyzer(sample_config)
        with pytest.raises(ValueError, match="Missing required columns"):
            analyzer.aggregate_by_water_year(time_series)

    def test_aggregate_by_water_year_no_flood_days(self, sample_config: Config) -> None:
        """Test aggregation with no flooding days."""
        dates = pd.date_range("2023-10-01", periods=30, freq="D")
        data = {
            "date": dates,
            "habitat": ["Dry"] * 30,
            "inundated_area_ha": [0.0] * 30,
        }
        time_series = pd.DataFrame(data)

        analyzer = HabitatAnalyzer(sample_config)
        result = analyzer.aggregate_by_water_year(time_series)

        row = result.iloc[0]
        assert row["num_inundation_days"] == 0
        assert pd.isna(row["first_flood_date"])
        assert pd.isna(row["last_flood_date"])


class TestHabitatAnalysisWorkflow:
    """Integration tests for habitat analysis workflow."""

    def test_full_habitat_analysis_workflow(self, sample_config: Config) -> None:
        """Test complete habitat analysis workflow."""
        # Create test water polygons
        from shapely.geometry import Polygon

        polygon = Polygon([(0, 0), (100, 0), (100, 100), (0, 100)])
        water_data = {
            "habitat": ["First", "First", "Middle", "Last"],
            "area_m2": [10000, 15000, 20000, 25000],
            "geometry": [polygon, polygon, polygon, polygon],
        }
        water_polygons = gpd.GeoDataFrame(water_data, crs="EPSG:32610")

        analyzer = HabitatAnalyzer(sample_config)

        # Step 1: Calculate habitat areas
        habitat_areas = analyzer.calculate_habitat_areas(water_polygons)
        assert len(habitat_areas) == 3

        # Step 2: Identify flood status
        flood_status = analyzer.identify_flood_status(habitat_areas)
        assert all(flood_status.values())  # All should be flooded

        # Step 3: Create time series
        dates = pd.date_range("2023-10-01", periods=10, freq="D")
        time_series_data = {
            "date": list(dates) * 3,
            "habitat": ["First"] * 10 + ["Middle"] * 10 + ["Last"] * 10,
            "inundated_area_ha": [2.5] * 10 + [2.0] * 10 + [2.5] * 10,
        }
        time_series = pd.DataFrame(time_series_data)

        # Step 4: Aggregate by water year
        wy_summary = analyzer.aggregate_by_water_year(time_series)
        assert len(wy_summary) == 3
