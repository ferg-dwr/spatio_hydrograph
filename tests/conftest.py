"""Shared pytest fixtures for spatio-hydrograph tests."""

from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
import xarray as xr
from shapely.geometry import Polygon

from spatio_hydrograph.config import Config


@pytest.fixture
def temp_data_dir():
    """Provide a temporary directory for test data.

    Handles Windows file cleanup issues by ignoring errors when
    rasterio keeps file handles open.
    """
    import contextlib
    import sys
    import time

    tmpdir = TemporaryDirectory()
    try:
        yield Path(tmpdir.name)
    finally:
        # On Windows, rasterio may keep file handles open briefly
        # Wait a moment and retry cleanup
        if sys.platform == "win32":
            try:
                tmpdir.cleanup()
            except (PermissionError, OSError, NotADirectoryError):
                # File still in use, wait and let OS clean up
                time.sleep(0.1)
                with contextlib.suppress(Exception):
                    tmpdir.cleanup()
        else:
            # On Unix systems, use normal cleanup
            tmpdir.cleanup()


@pytest.fixture
def sample_config(temp_data_dir: Path) -> Config:
    """Provide a sample configuration for testing."""
    return Config(
        water_year=2023,
        analysis_version="_v1",
        data_dir=temp_data_dir,
        s1_input_dir=temp_data_dir / "S1",
        s2_input_dir=temp_data_dir / "S2",
        output_dir=temp_data_dir / "output",
        min_polygon_area_m2=5000.0,
        flood_trigger_habitats=["First", "Last"],
    )


@pytest.fixture
def sample_habitat_polygons(temp_data_dir: Path) -> gpd.GeoDataFrame:
    """Create sample habitat polygons for testing."""
    # Create simple square polygons
    polygons = [
        Polygon([(0, 0), (100, 0), (100, 100), (0, 100)]),
        Polygon([(100, 0), (200, 0), (200, 100), (100, 100)]),
        Polygon([(200, 0), (300, 0), (300, 100), (200, 100)]),
    ]

    habitats = ["First", "Middle", "Last"]

    gdf = gpd.GeoDataFrame(
        {"habitat": habitats, "geometry": polygons}, crs="EPSG:32610"
    )

    return gdf


@pytest.fixture
def sample_water_polygons(temp_data_dir: Path) -> gpd.GeoDataFrame:
    """Create sample water polygons for testing."""
    polygons = [
        Polygon([(10, 10), (50, 10), (50, 50), (10, 50)]),
        Polygon([(110, 10), (150, 10), (150, 50), (110, 50)]),
        Polygon([(210, 10), (250, 10), (250, 50), (210, 50)]),
    ]

    areas_m2 = [1600, 1600, 1600]

    gdf = gpd.GeoDataFrame(
        {"area_m2": areas_m2, "geometry": polygons}, crs="EPSG:32610"
    )

    return gdf


@pytest.fixture
def sample_raster() -> xr.DataArray:
    """Create a sample classified raster for testing."""
    data = np.random.randint(0, 2, size=(100, 100))
    da = xr.DataArray(
        data,
        dims=["y", "x"],
        coords={
            "y": np.arange(0, 100),
            "x": np.arange(0, 100),
        },
        name="water_class",
    )
    da.attrs["crs"] = "EPSG:32610"
    return da


@pytest.fixture
def sample_habitat_time_series() -> pd.DataFrame:
    """Create sample habitat time series for testing."""
    dates = pd.date_range("2023-10-01", periods=30, freq="D")
    habitats = ["First", "Middle", "Last"]

    data = []
    for habitat in habitats:
        for date in dates:
            data.append(
                {
                    "date": date,
                    "habitat": habitat,
                    "inundated_area_ha": np.random.uniform(100, 1000),
                    "percent_water": np.random.uniform(0, 100),
                }
            )

    return pd.DataFrame(data)


@pytest.fixture
def sample_landscape_metrics() -> pd.DataFrame:
    """Create sample landscape metrics for testing."""
    dates = pd.date_range("2023-10-01", periods=30, freq="D")

    data = []
    for date in dates:
        data.append(
            {
                "date": date,
                "total_area_ha": np.random.uniform(1000, 5000),
                "area_mean_m2": np.random.uniform(1000, 5000),
                "area_sd_m2": np.random.uniform(500, 2000),
                "area_p10_m2": np.random.uniform(100, 500),
                "area_p50_m2": np.random.uniform(1000, 5000),
                "area_p90_m2": np.random.uniform(5000, 10000),
                "core_area_mean_m2": np.random.uniform(500, 3000),
                "clumpiness": np.random.uniform(0, 1),
                "cohesion": np.random.uniform(0, 100),
            }
        )

    return pd.DataFrame(data)
