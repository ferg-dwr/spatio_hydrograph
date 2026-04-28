"""
Configuration management for spatio-hydrograph analysis.

Handles loading, validation, and management of analysis parameters from
YAML configuration files.

Example:
    >>> from spatio_hydrograph.config import load_config
    >>> config = load_config("config.yaml")
    >>> print(config.water_year)
    2023
"""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class ShapefileConfig:
    """Configuration for shapefiles used in analysis."""

    habitat_polygons: Path
    connectivity_lines: Path | None = None
    volume_slices: Path | None = None

    def __post_init__(self) -> None:
        """Validate shapefiles exist."""
        if not self.habitat_polygons.exists():
            raise FileNotFoundError(
                f"Habitat polygons not found: {self.habitat_polygons}"
            )


@dataclass
class LandscapeMetricsConfig:
    """Configuration for landscape metrics calculations."""

    patch_metrics: list = field(
        default_factory=lambda: ["area", "core_area", "perimeter_area_ratio"]
    )
    class_metrics: list = field(default_factory=lambda: ["clumpiness", "cohesion"])
    percentiles: list = field(default_factory=lambda: [10, 50, 90])


@dataclass
class Config:
    """Main configuration class for spatio-hydrograph analysis."""

    # Analysis parameters
    water_year: int
    analysis_version: str = "_v1"

    # Data directories
    data_dir: Path = field(default_factory=lambda: Path("./data"))
    s1_input_dir: Path = field(default_factory=lambda: Path("./data/S1"))
    s2_input_dir: Path = field(default_factory=lambda: Path("./data/S2"))
    output_dir: Path = field(default_factory=lambda: Path("./output"))

    # Shapefiles
    shapefiles: ShapefileConfig | None = None

    # Processing parameters
    min_polygon_area_m2: float = 5000.0
    flood_trigger_habitats: list = field(default_factory=list)

    # Landscape metrics
    landscape_metrics: LandscapeMetricsConfig | None = None

    def __post_init__(self) -> None:
        """Convert string paths to Path objects and create output directories."""
        if isinstance(self.data_dir, str):
            self.data_dir = Path(self.data_dir)
        if isinstance(self.s1_input_dir, str):
            self.s1_input_dir = Path(self.s1_input_dir)
        if isinstance(self.s2_input_dir, str):
            self.s2_input_dir = Path(self.s2_input_dir)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create landscape metrics config if not provided
        if self.landscape_metrics is None:
            self.landscape_metrics = LandscapeMetricsConfig()


def load_config(config_path: str | Path) -> Config:
    """
    Load configuration from YAML file.

    Parameters
    ----------
    config_path : str or Path
        Path to YAML configuration file

    Returns
    -------
    Config
        Configuration object

    Raises
    ------
    FileNotFoundError
        If configuration file does not exist
    ValueError
        If configuration is invalid

    Example
    -------
    >>> config = load_config("config.yaml")
    >>> print(config.water_year)
    2023
    """
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in configuration file: {e}") from e

    if config_dict is None:
        raise ValueError("Configuration file is empty")

    # Handle nested shapefiles configuration
    if "shapefiles" in config_dict and config_dict["shapefiles"] is not None:
        shapefiles_dict = config_dict["shapefiles"]
        # Convert string paths to Path objects
        shapefiles_dict = {
            k: Path(v) if isinstance(v, str) else v for k, v in shapefiles_dict.items()
        }
        config_dict["shapefiles"] = ShapefileConfig(**shapefiles_dict)

    # Handle nested landscape_metrics configuration
    if (
        "landscape_metrics" in config_dict
        and config_dict["landscape_metrics"] is not None
    ):
        metrics_dict = config_dict["landscape_metrics"]
        config_dict["landscape_metrics"] = LandscapeMetricsConfig(**metrics_dict)

    try:
        return Config(**config_dict)
    except TypeError as e:
        raise ValueError(f"Invalid configuration parameters: {e}") from e


def save_config(config: Config, output_path: str | Path) -> None:
    """
    Save configuration to YAML file.

    Parameters
    ----------
    config : Config
        Configuration object to save
    output_path : str or Path
        Path to save configuration file

    Example
    -------
    >>> config = Config(water_year=2023)
    >>> save_config(config, "config.yaml")
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    config_dict = {
        "water_year": config.water_year,
        "analysis_version": config.analysis_version,
        "data_dir": str(config.data_dir),
        "s1_input_dir": str(config.s1_input_dir),
        "s2_input_dir": str(config.s2_input_dir),
        "output_dir": str(config.output_dir),
        "min_polygon_area_m2": config.min_polygon_area_m2,
        "flood_trigger_habitats": config.flood_trigger_habitats,
    }

    # Add shapefiles configuration if present
    if config.shapefiles is not None:
        config_dict["shapefiles"] = {
            "habitat_polygons": str(config.shapefiles.habitat_polygons),
            "connectivity_lines": (
                str(config.shapefiles.connectivity_lines)
                if config.shapefiles.connectivity_lines is not None
                else None
            ),
            "volume_slices": (
                str(config.shapefiles.volume_slices)
                if config.shapefiles.volume_slices is not None
                else None
            ),
        }

    # Add landscape_metrics configuration if present
    if config.landscape_metrics is not None:
        config_dict["landscape_metrics"] = {
            "patch_metrics": config.landscape_metrics.patch_metrics,
            "class_metrics": config.landscape_metrics.class_metrics,
            "percentiles": config.landscape_metrics.percentiles,
        }

    try:
        with open(output_path, "w") as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
    except OSError as e:
        raise OSError(f"Failed to write configuration to {output_path}: {e}") from e
