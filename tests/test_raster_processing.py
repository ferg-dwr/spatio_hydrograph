"""Tests for spatio_hydrograph.raster_processing module."""

from pathlib import Path

import geopandas as gpd
import pytest

from spatio_hydrograph.config import Config, ShapefileConfig
from spatio_hydrograph.raster_processing import RasterProcessor


class TestRasterProcessor:
    """Tests for RasterProcessor class."""

    def test_processor_initialization(self, sample_config: Config) -> None:
        """Test RasterProcessor initialization."""
        processor = RasterProcessor(sample_config)
        assert processor.config == sample_config
        assert processor.habitat_gdf is None

    def test_load_habitat_polygons_no_config(self, sample_config: Config) -> None:
        """Test error when shapefiles configuration not provided."""
        config = Config(water_year=2023, output_dir=sample_config.output_dir)
        processor = RasterProcessor(config)

        with pytest.raises(ValueError, match="Shapefiles configuration not provided"):
            processor.load_habitat_polygons()

    def test_load_habitat_polygons_success(
        self,
        sample_config: Config,
        sample_habitat_polygons: gpd.GeoDataFrame,
        temp_data_dir: Path,
    ) -> None:
        """Test loading habitat polygons from shapefile."""
        # Save sample polygons to shapefile
        habitat_path = temp_data_dir / "habitat.shp"
        sample_habitat_polygons.to_file(habitat_path)

        # Create config with shapefiles
        shp_config = ShapefileConfig(habitat_polygons=habitat_path)
        config = Config(
            water_year=2023, output_dir=temp_data_dir / "output", shapefiles=shp_config
        )

        processor = RasterProcessor(config)
        habitat_gdf = processor.load_habitat_polygons()

        assert habitat_gdf is not None
        assert len(habitat_gdf) == len(sample_habitat_polygons)
        assert processor.habitat_gdf is not None


class TestRasterToPolygons:
    """Tests for raster_to_polygons method."""

    def test_raster_to_polygons_file_not_found(self, sample_config: Config) -> None:
        """Test error when raster file doesn't exist."""
        processor = RasterProcessor(sample_config)

        with pytest.raises(FileNotFoundError):
            processor.raster_to_polygons("nonexistent.tif")

    def test_raster_to_polygons_creates_gdf(
        self, sample_config: Config, sample_raster, temp_data_dir: Path
    ) -> None:
        """Test raster-to-vector conversion creates valid GeoDataFrame."""
        # Save sample raster to file
        raster_path = temp_data_dir / "water.tif"
        sample_raster.rio.to_raster(raster_path)

        processor = RasterProcessor(sample_config)
        polygons = processor.raster_to_polygons(raster_path)

        # Check result is GeoDataFrame
        assert isinstance(polygons, gpd.GeoDataFrame)
        assert "area_m2" in polygons.columns
        assert polygons.crs is not None

    def test_raster_to_polygons_has_area(
        self, sample_config: Config, sample_raster, temp_data_dir: Path
    ) -> None:
        """Test that output polygons have area calculated."""
        raster_path = temp_data_dir / "water.tif"
        sample_raster.rio.to_raster(raster_path)

        processor = RasterProcessor(sample_config)
        polygons = processor.raster_to_polygons(raster_path)

        # Check areas are positive
        if len(polygons) > 0:
            assert (polygons["area_m2"] > 0).all()


class TestFilterByArea:
    """Tests for filter_by_area method."""

    def test_filter_by_area_with_config(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test filtering using config min_area."""
        processor = RasterProcessor(sample_config)

        # All sample polygons have area 1600 m2, config min is 5000
        filtered = processor.filter_by_area(sample_water_polygons)

        assert len(filtered) == 0

    def test_filter_by_area_with_parameter(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test filtering using provided min_area parameter."""
        processor = RasterProcessor(sample_config)

        # Filter with lower threshold
        filtered = processor.filter_by_area(sample_water_polygons, min_area_m2=1000.0)

        assert len(filtered) == 3  # All should pass
        assert (filtered["area_m2"] >= 1000.0).all()

    def test_filter_by_area_negative_raises_error(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test error on negative min_area."""
        processor = RasterProcessor(sample_config)

        with pytest.raises(ValueError, match="min_area_m2 must be positive"):
            processor.filter_by_area(sample_water_polygons, min_area_m2=-100.0)

    def test_filter_by_area_calculates_missing_area(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test that area column is calculated if missing."""
        # Remove area column
        polygons_no_area = sample_water_polygons.drop(columns=["area_m2"])

        processor = RasterProcessor(sample_config)
        filtered = processor.filter_by_area(polygons_no_area, min_area_m2=1000.0)

        assert "area_m2" in filtered.columns


class TestIntersectWithHabitats:
    """Tests for intersect_with_habitats method."""

    def test_intersect_with_habitats_no_config(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test error when shapefiles not configured."""
        config = Config(water_year=2023, output_dir=sample_config.output_dir)
        processor = RasterProcessor(config)

        with pytest.raises(ValueError):
            processor.intersect_with_habitats(sample_water_polygons)

    def test_intersect_with_habitats_success(
        self,
        sample_config: Config,
        sample_water_polygons: gpd.GeoDataFrame,
        sample_habitat_polygons: gpd.GeoDataFrame,
        temp_data_dir: Path,
    ) -> None:
        """Test successful spatial intersection."""
        # Save habitat polygons
        habitat_path = temp_data_dir / "habitat.shp"
        sample_habitat_polygons.to_file(habitat_path)

        # Create config
        shp_config = ShapefileConfig(habitat_polygons=habitat_path)
        config = Config(
            water_year=2023, output_dir=temp_data_dir / "output", shapefiles=shp_config
        )

        processor = RasterProcessor(config)
        intersected = processor.intersect_with_habitats(sample_water_polygons)

        assert isinstance(intersected, gpd.GeoDataFrame)
        # Should have water polygon columns + habitat columns
        assert "area_m2" in intersected.columns

    def test_intersect_handles_crs_mismatch(
        self,
        sample_config: Config,
        sample_water_polygons: gpd.GeoDataFrame,
        sample_habitat_polygons: gpd.GeoDataFrame,
        temp_data_dir: Path,
    ) -> None:
        """Test that CRS mismatch is handled."""
        # Save habitat polygons in different CRS
        habitat_path = temp_data_dir / "habitat.shp"
        habitat_reproject = sample_habitat_polygons.to_crs("EPSG:4326")
        habitat_reproject.to_file(habitat_path)

        # Water polygons in different CRS
        water_reproject = sample_water_polygons.to_crs("EPSG:32611")

        # Create config
        shp_config = ShapefileConfig(habitat_polygons=habitat_path)
        config = Config(
            water_year=2023, output_dir=temp_data_dir / "output", shapefiles=shp_config
        )

        processor = RasterProcessor(config)
        # Should not raise error - CRS should be aligned
        intersected = processor.intersect_with_habitats(water_reproject)

        assert intersected.crs is not None


class TestGetPolygonCentroids:
    """Tests for get_polygon_centroids method."""

    def test_get_polygon_centroids_basic(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test centroid extraction."""
        processor = RasterProcessor(sample_config)
        centroids = processor.get_polygon_centroids(sample_water_polygons)

        assert len(centroids) == len(sample_water_polygons)
        assert all(geom.geom_type == "Point" for geom in centroids.geometry)

    def test_get_polygon_centroids_preserves_attributes(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test that attributes are preserved."""
        processor = RasterProcessor(sample_config)
        centroids = processor.get_polygon_centroids(sample_water_polygons)

        # Check that all original columns are preserved
        for col in sample_water_polygons.columns:
            if col != "geometry":
                assert col in centroids.columns

    def test_get_polygon_centroids_within_polygons(
        self, sample_config: Config, sample_water_polygons: gpd.GeoDataFrame
    ) -> None:
        """Test that centroids are within original polygons."""
        processor = RasterProcessor(sample_config)
        centroids = processor.get_polygon_centroids(sample_water_polygons)

        # Each centroid should be within its original polygon
        for idx, (poly_geom, centroid_geom) in enumerate(
            zip(sample_water_polygons.geometry, centroids.geometry, strict=False)
        ):
            assert poly_geom.contains(centroid_geom), f"Centroid {idx} not in polygon"


class TestRasterProcessingWorkflow:
    """Integration tests for full raster processing workflow."""

    def test_full_workflow(
        self,
        sample_config: Config,
        sample_raster,
        sample_habitat_polygons: gpd.GeoDataFrame,
        temp_data_dir: Path,
    ) -> None:
        """Test complete workflow: raster -> polygons -> filter -> intersect."""
        # Save raster and habitat shapefiles
        raster_path = temp_data_dir / "water.tif"
        habitat_path = temp_data_dir / "habitat.shp"

        sample_raster.rio.to_raster(raster_path)
        sample_habitat_polygons.to_file(habitat_path)

        # Create config
        shp_config = ShapefileConfig(habitat_polygons=habitat_path)
        config = Config(
            water_year=2023,
            output_dir=temp_data_dir / "output",
            shapefiles=shp_config,
            min_polygon_area_m2=1000.0,
        )

        processor = RasterProcessor(config)

        # Run workflow
        polygons = processor.raster_to_polygons(raster_path)
        filtered = processor.filter_by_area(polygons)
        intersected = processor.intersect_with_habitats(filtered)

        # Should have gone through entire workflow
        assert isinstance(intersected, gpd.GeoDataFrame)
