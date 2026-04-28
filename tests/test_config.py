"""Tests for spatio_hydrograph.config module."""

from pathlib import Path

import pytest
import yaml

from spatio_hydrograph.config import (
    Config,
    LandscapeMetricsConfig,
    ShapefileConfig,
    load_config,
    save_config,
)


class TestConfig:
    """Tests for Config dataclass."""

    def test_config_initialization(self, sample_config: Config) -> None:
        """Test Config object initialization."""
        assert sample_config.water_year == 2023
        assert sample_config.analysis_version == "_v1"
        assert isinstance(sample_config.output_dir, Path)

    def test_config_output_dir_creation(self, sample_config: Config) -> None:
        """Test that output directory is created."""
        assert sample_config.output_dir.exists()

    def test_config_string_path_conversion(self) -> None:
        """Test that string paths are converted to Path objects."""
        config = Config(water_year=2023, data_dir=Path("./data"))
        assert isinstance(config.data_dir, Path)
        assert config.data_dir == Path("./data")

    def test_config_default_landscape_metrics(self, sample_config: Config) -> None:
        """Test that default landscape metrics config is created."""
        assert sample_config.landscape_metrics is not None
        assert "area" in sample_config.landscape_metrics.patch_metrics
        assert "clumpiness" in sample_config.landscape_metrics.class_metrics

    def test_config_flood_trigger_habitats(self, sample_config: Config) -> None:
        """Test flood trigger habitats configuration."""
        assert "First" in sample_config.flood_trigger_habitats
        assert "Last" in sample_config.flood_trigger_habitats

    def test_config_min_polygon_area(self, sample_config: Config) -> None:
        """Test minimum polygon area parameter."""
        assert sample_config.min_polygon_area_m2 == 5000.0


class TestShapefileConfig:
    """Tests for ShapefileConfig dataclass."""

    def test_shapefile_config_with_habitat_only(
        self, sample_habitat_polygons, temp_data_dir: Path
    ) -> None:
        """Test ShapefileConfig with only habitat polygons."""
        habitat_path = temp_data_dir / "habitat.shp"
        habitat_path.touch()

        shp_config = ShapefileConfig(habitat_polygons=habitat_path)
        assert shp_config.habitat_polygons == habitat_path
        assert shp_config.connectivity_lines is None

    def test_shapefile_config_missing_habitat_raises_error(
        self, temp_data_dir: Path
    ) -> None:
        """Test that missing habitat polygons raises FileNotFoundError."""
        missing_path = temp_data_dir / "nonexistent.shp"

        with pytest.raises(FileNotFoundError):
            ShapefileConfig(habitat_polygons=missing_path)

    def test_shapefile_config_with_all_files(self, temp_data_dir: Path) -> None:
        """Test ShapefileConfig with all optional files."""
        habitat = temp_data_dir / "habitat.shp"
        lines = temp_data_dir / "lines.shp"
        slices = temp_data_dir / "slices.shp"

        for f in [habitat, lines, slices]:
            f.touch()

        shp_config = ShapefileConfig(
            habitat_polygons=habitat,
            connectivity_lines=lines,
            volume_slices=slices,
        )
        assert shp_config.connectivity_lines == lines
        assert shp_config.volume_slices == slices


class TestLandscapeMetricsConfig:
    """Tests for LandscapeMetricsConfig dataclass."""

    def test_landscape_metrics_defaults(self) -> None:
        """Test default landscape metrics configuration."""
        metrics = LandscapeMetricsConfig()
        assert metrics.patch_metrics == ["area", "core_area", "perimeter_area_ratio"]
        assert metrics.class_metrics == ["clumpiness", "cohesion"]
        assert metrics.percentiles == [10, 50, 90]

    def test_landscape_metrics_custom(self) -> None:
        """Test custom landscape metrics configuration."""
        metrics = LandscapeMetricsConfig(
            patch_metrics=["area"],
            class_metrics=["clumpiness"],
            percentiles=[25, 75],
        )
        assert metrics.patch_metrics == ["area"]
        assert metrics.class_metrics == ["clumpiness"]
        assert metrics.percentiles == [25, 75]


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_file_not_found(self) -> None:
        """Test error when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    def test_load_valid_config(self, temp_data_dir: Path) -> None:
        """Test loading valid configuration from YAML."""
        config_file = temp_data_dir / "config.yaml"
        config_data = {
            "water_year": 2023,
            "analysis_version": "_v1",
            "data_dir": "./data",
            "s1_input_dir": "./data/S1",
            "s2_input_dir": "./data/S2",
            "output_dir": str(temp_data_dir / "output"),
            "min_polygon_area_m2": 5000.0,
            "flood_trigger_habitats": ["First", "Last"],
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(config_file)
        assert config.water_year == 2023
        assert config.analysis_version == "_v1"

    def test_load_config_empty_file(self, temp_data_dir: Path) -> None:
        """Test error when config file is empty."""
        config_file = temp_data_dir / "empty.yaml"
        config_file.write_text("")

        with pytest.raises(ValueError, match="Configuration file is empty"):
            load_config(config_file)

    def test_load_config_invalid_yaml(self, temp_data_dir: Path) -> None:
        """Test error when config file has invalid YAML."""
        config_file = temp_data_dir / "invalid.yaml"
        config_file.write_text("invalid: yaml: syntax:")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_config(config_file)

    def test_load_config_with_shapefiles(self, temp_data_dir: Path) -> None:
        """Test loading config with shapefiles."""
        config_file = temp_data_dir / "config.yaml"
        habitat_shp = temp_data_dir / "habitat.shp"
        habitat_shp.touch()

        config_data = {
            "water_year": 2023,
            "output_dir": str(temp_data_dir / "output"),
            "shapefiles": {
                "habitat_polygons": str(habitat_shp),
                "connectivity_lines": None,
            },
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(config_file)
        assert config.shapefiles is not None
        assert config.shapefiles.habitat_polygons == habitat_shp

    def test_load_config_with_landscape_metrics(self, temp_data_dir: Path) -> None:
        """Test loading config with landscape metrics."""
        config_file = temp_data_dir / "config.yaml"
        config_data = {
            "water_year": 2023,
            "output_dir": str(temp_data_dir / "output"),
            "landscape_metrics": {
                "patch_metrics": ["area", "core_area"],
                "class_metrics": ["clumpiness"],
                "percentiles": [25, 75],
            },
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_config(config_file)
        assert config.landscape_metrics is not None
        assert config.landscape_metrics.patch_metrics == ["area", "core_area"]
        assert config.landscape_metrics.percentiles == [25, 75]

    def test_load_config_invalid_params(self, temp_data_dir: Path) -> None:
        """Test error with invalid configuration parameters."""
        config_file = temp_data_dir / "config.yaml"
        config_data = {
            "invalid_param": "value",
        }

        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        with pytest.raises(ValueError, match="Invalid configuration parameters"):
            load_config(config_file)


class TestSaveConfig:
    """Tests for save_config function."""

    def test_save_config_basic(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test saving configuration to YAML file."""
        output_file = temp_data_dir / "saved_config.yaml"
        save_config(sample_config, output_file)

        assert output_file.exists()

        # Load it back and verify
        with open(output_file) as f:
            saved_data = yaml.safe_load(f)

        assert saved_data["water_year"] == 2023
        assert saved_data["analysis_version"] == "_v1"

    def test_save_and_load_roundtrip(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test saving and loading config produces same result."""
        output_file = temp_data_dir / "roundtrip.yaml"
        save_config(sample_config, output_file)
        loaded_config = load_config(output_file)

        assert loaded_config.water_year == sample_config.water_year
        assert loaded_config.analysis_version == sample_config.analysis_version
        assert loaded_config.min_polygon_area_m2 == sample_config.min_polygon_area_m2

    def test_save_config_creates_parent_dirs(
        self, sample_config: Config, temp_data_dir: Path
    ) -> None:
        """Test that save_config creates parent directories."""
        output_file = temp_data_dir / "nested" / "deep" / "config.yaml"
        save_config(sample_config, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()

    def test_save_config_with_shapefiles(self, temp_data_dir: Path) -> None:
        """Test saving config with shapefiles."""
        habitat_shp = temp_data_dir / "habitat.shp"
        habitat_shp.touch()

        shp_config = ShapefileConfig(habitat_polygons=habitat_shp)
        config = Config(
            water_year=2023, shapefiles=shp_config, output_dir=temp_data_dir / "output"
        )

        output_file = temp_data_dir / "with_shapefiles.yaml"
        save_config(config, output_file)

        with open(output_file) as f:
            saved_data = yaml.safe_load(f)

        assert "shapefiles" in saved_data
        assert "habitat_polygons" in saved_data["shapefiles"]

    def test_save_config_with_landscape_metrics(self, temp_data_dir: Path) -> None:
        """Test saving config with landscape metrics."""
        metrics = LandscapeMetricsConfig(
            patch_metrics=["area"],
            class_metrics=["clumpiness"],
            percentiles=[50],
        )
        config = Config(
            water_year=2023,
            landscape_metrics=metrics,
            output_dir=temp_data_dir / "output",
        )

        output_file = temp_data_dir / "with_metrics.yaml"
        save_config(config, output_file)

        with open(output_file) as f:
            saved_data = yaml.safe_load(f)

        assert "landscape_metrics" in saved_data
        assert saved_data["landscape_metrics"]["patch_metrics"] == ["area"]
