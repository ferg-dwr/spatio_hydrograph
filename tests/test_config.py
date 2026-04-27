"""Tests for spatio_hydrograph.config module."""

from pathlib import Path

import pytest

from spatio_hydrograph.config import Config, load_config, save_config


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

    def test_config_string_path_conversion(self, sample_config: Config) -> None:
        """Test that string paths are converted to Path objects."""
        config = Config(water_year=2023, data_dir="./data")
        assert isinstance(config.data_dir, Path)


class TestConfigLoading:
    """Tests for configuration loading from YAML."""

    def test_load_config_file_not_found(self) -> None:
        """Test error when config file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            load_config("nonexistent.yaml")

    @pytest.mark.skip(reason="Requires YAML fixture")
    def test_load_valid_config(self, temp_data_dir: Path) -> None:
        """Test loading valid configuration."""
        # TODO: Create and load valid YAML config
        pass


class TestConfigSaving:
    """Tests for configuration saving."""

    @pytest.mark.skip(reason="Not yet implemented")
    def test_save_config(self, sample_config: Config, temp_data_dir: Path) -> None:
        """Test saving configuration to file."""
        output_path = temp_data_dir / "config.yaml"
        save_config(sample_config, output_path)
        assert output_path.exists()
