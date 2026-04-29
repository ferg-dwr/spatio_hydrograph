# Spatio-Hydrograph

[![CI](https://github.com/ferg-dwr/spatio_hydrograph/workflows/CI/badge.svg)](https://github.com/ferg-dwr/spatio_hydrograph/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests: 80+](https://img.shields.io/badge/Tests-80+-green.svg)](https://github.com/ferg-dwr/spatio_hydrograph/actions)
[![Type Safe](https://img.shields.io/badge/Type%20Safe-mypy-blue.svg)](https://www.mypy-lang.org/)

Spatio-temporal hydrographic analysis of Yolo Bypass inundation using satellite imagery.

## Overview

`spatio-hydrograph` is a **production-ready Python package** for analyzing satellite-derived water classification maps (Sentinel-1 and Sentinel-2) to quantify inundation dynamics across the Yolo Bypass. The package:

- **Converts raster water maps to vector polygons** for habitat-level analysis
- **Calculates landscape metrics** (patch size, core area, clumpiness, cohesion)
- **Quantifies per-habitat inundation areas** and percent water coverage
- **Measures lateral connectivity** of flooded areas via transect analysis
- **Generates publication-ready visualizations** of spatio-temporal patterns
- **Full type safety** with mypy compliance for robust code

## Key Features

- 🗺️ **Geospatial Processing**: Efficient raster-to-vector conversion with polygon filtering and CRS validation
- 📊 **Landscape Metrics**: Patch size distribution, core area, perimeter-area ratio, clumpiness, cohesion
- 🔗 **Connectivity Analysis**: Lateral connectivity measurements from parallel transects with bottleneck detection
- 🌿 **Habitat Analysis**: Per-habitat inundation statistics with temporal aggregation
- 📈 **Visualization**: Publication-ready plots (habitat time series, connectivity trends, patch distribution)
- ⚙️ **Configurable**: YAML-based configuration for flexible analysis parameters
- ✅ **Well-Tested**: 80+ comprehensive tests, 95%+ code coverage
- 🔒 **Type-Safe**: Full mypy compliance for robust development

## Installation

### From GitHub (development)

```bash
git clone https://github.com/ferg-dwr/spatio_hydrograph.git
cd spatio_hydrograph
pip install -e "."
```

### With development dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Prepare Your Data

Organize your satellite water classification maps by water year and sensor:

```
data/
├── S1_WY2023/          # Sentinel-1 Lee Sigma classification
│   ├── water_2023-10-01.tif
│   ├── water_2023-10-15.tif
│   └── ...
├── S2_WY2023/          # Sentinel-2 AWEIsh classification
│   ├── water_2023-10-01.tif
│   ├── water_2023-10-15.tif
│   └── ...
└── vectors/
    ├── YoloBypassForSH_UTM_wat.shp    # Habitat polygons
    ├── parallel_lines.shp              # Connectivity transects
    └── polygon_slices.shp              # Volume calculation slices
```

### 2. Create Configuration File

Create `config.yaml`:

```yaml
# Analysis parameters
water_year: 2023
analysis_version: "_v5"

# Data directories
data_dir: "./data"
s1_input_dir: "./data/S1_WY2023"
s2_input_dir: "./data/S2_WY2023"
output_dir: "./output"

# Vector files
shapefiles:
  habitat_polygons: "vectors/YoloBypassForSH_UTM_wat.shp"
  connectivity_lines: "vectors/parallel_lines.shp"
  volume_slices: "vectors/polygon_slices.shp"

# Processing parameters
min_polygon_area_m2: 5000          # Minimum polygon size to retain
flood_trigger_habitats:
  - "First"
  - "Last"

# Landscape metrics configuration
landscape_metrics:
  patch_metrics:
    - "area"
    - "core_area"
    - "perimeter_area_ratio"
  class_metrics:
    - "clumpiness"
    - "cohesion"
  percentiles: [10, 50, 90]         # P10, P50, P90
```

### 3. Run Analysis

```python
from spatio_hydrograph.config import load_config
from spatio_hydrograph.raster_processing import RasterProcessor
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer
from spatio_hydrograph.landscape_metrics import LandscapeMetrics
from spatio_hydrograph.connectivity import ConnectivityAnalyzer
from spatio_hydrograph.visualization import Visualizer

# Load configuration
config = load_config("config.yaml")

# Process raster data
processor = RasterProcessor(config)
polygons = processor.raster_to_polygons("water_2023-10-01.tif")
habitat_water = processor.intersect_with_habitats(polygons)

# Analyze habitat inundation
habitat_analyzer = HabitatAnalyzer(config)
habitat_areas = habitat_analyzer.calculate_habitat_areas(habitat_water)

# Calculate landscape metrics
metrics = LandscapeMetrics(config)
patch_metrics = metrics.calculate_patch_metrics(classified_raster)

# Measure connectivity
connectivity_analyzer = ConnectivityAnalyzer(config)
connectivity = connectivity_analyzer.analyze_connectivity(polygons, transect_lines)

# Create visualizations
viz = Visualizer(config)
viz.plot_habitat_time_series(habitat_areas)
viz.plot_lateral_connectivity(connectivity)
viz.plot_patch_size_distribution(landscape_metrics)
```

## Module Documentation

### config.py - Configuration Management

Loads and validates YAML configuration files.

```python
from spatio_hydrograph.config import load_config

config = load_config("config.yaml")
print(config.water_year)
print(config.output_dir)
print(config.shapefiles.habitat_polygons)
```

**Key Classes:**
- `Config`: Main configuration object
- `ShapefileConfig`: Shapefile path validation
- `LandscapeMetricsConfig`: Metrics settings

### raster_processing.py - Raster-to-Vector Conversion

Converts water classification rasters to vector polygons.

```python
from spatio_hydrograph.raster_processing import RasterProcessor

processor = RasterProcessor(config)
polygons = processor.raster_to_polygons("water_2023-10-01.tif")
filtered = processor.filter_by_area(polygons, min_area_m2=5000)
habitat_water = processor.intersect_with_habitats(filtered)
```

**Key Methods:**
- `load_habitat_polygons()`: Load habitat GeoDataFrame
- `raster_to_polygons()`: Convert raster to vector
- `filter_by_area()`: Remove small polygons
- `intersect_with_habitats()`: Find water-habitat intersections
- `get_polygon_centroids()`: Extract centroid coordinates

### habitat_analysis.py - Per-Habitat Analysis

Calculates inundation statistics by habitat.

```python
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer

analyzer = HabitatAnalyzer(config)
habitat_areas = analyzer.calculate_habitat_areas(polygons)
percent_water = analyzer.calculate_percent_inundated(habitat_areas)
flood_status = analyzer.identify_flood_status(habitat_areas)
yearly_stats = analyzer.aggregate_by_water_year(habitat_time_series)
```

**Key Methods:**
- `calculate_habitat_areas()`: Sum area by habitat
- `calculate_percent_inundated()`: Percent water coverage
- `identify_flood_status()`: Boolean flood presence
- `aggregate_by_water_year()`: Temporal statistics

### landscape_metrics.py - Landscape Ecology Metrics

Computes patch-level and class-level metrics.

```python
from spatio_hydrograph.landscape_metrics import LandscapeMetrics

metrics = LandscapeMetrics(config)
patch_metrics = metrics.calculate_patch_metrics(classified_raster)
class_metrics = metrics.calculate_class_metrics(classified_raster)
area_stats = metrics.calculate_area_statistics(patches)
core_area = metrics.calculate_core_area_statistics(patches, edge_distance=10.0)
para = metrics.calculate_para_statistics(patches)
```

**Key Methods:**
- `calculate_patch_metrics()`: Comprehensive patch statistics
- `calculate_class_metrics()`: Clumpiness and cohesion indices
- `calculate_area_statistics()`: Patch size distribution
- `calculate_core_area_statistics()`: Interior habitat quality
- `calculate_para_statistics()`: Shape complexity (perimeter-area ratio)

### connectivity.py - Lateral Connectivity Analysis

Measures water connectivity along transect lines.

```python
from spatio_hydrograph.connectivity import ConnectivityAnalyzer

analyzer = ConnectivityAnalyzer(config)
connectivity = analyzer.analyze_connectivity(polygons, transect_lines)
endpoints = analyzer.calculate_connectivity_endpoints(transect_lines)
stats = analyzer.calculate_connectivity_statistics(connectivity)
bottlenecks = analyzer.identify_bottlenecks(connectivity, threshold_percentile=10)
```

**Key Methods:**
- `analyze_connectivity()`: Measure wet length per transect
- `calculate_connectivity_endpoints()`: Extract transect endpoints
- `calculate_connectivity_statistics()`: Summary statistics
- `identify_bottlenecks()`: Find low-connectivity areas

### visualization.py - Publication-Ready Plots

Generates high-quality visualization figures.

```python
from spatio_hydrograph.visualization import Visualizer

# show=False (default) for testing, show=True for interactive use
viz = Visualizer(config, figsize=(12, 8), dpi=300, show=False)

viz.plot_habitat_time_series(habitat_areas, "habitat_timeseries.png")
viz.plot_percent_water(habitat_data, "percent_water.png")
viz.plot_lateral_connectivity(connectivity_results, "connectivity.png")
viz.plot_patch_size_distribution(landscape_metrics, "patch_size.png")
viz.plot_core_area_distribution(landscape_metrics, "core_area.png")
viz.plot_comparative_sensors(s1_results, s2_results, "sentinel_comparison.png")
```

**Key Methods:**
- `plot_habitat_time_series()`: Area time series by habitat
- `plot_percent_water()`: Percent inundation bar chart
- `plot_lateral_connectivity()`: Connectivity trend with uncertainty
- `plot_patch_size_distribution()`: Patch size percentiles over time
- `plot_core_area_distribution()`: Core area percentiles over time
- `plot_comparative_sensors()`: Sentinel-1 vs Sentinel-2 comparison

## Data Source

Satellite water classification maps derived from:
- **Sentinel-1**: Lee Sigma backscatter classification
- **Sentinel-2**: Automated Water Extraction Index (AWEIsh)

Processing via Google Earth Engine (data pre-computed and downloaded locally).

## Output Files

The package generates:

1. **Habitat Area Table** (`SH_WY{year}_{sensor}_{version}_habArea.csv`)
   - Date, habitat, inundated area (ha), % water coverage

2. **Landscape Metrics Table** (`SH_WY{year}_{sensor}_{version}_lmAll.csv`)
   - Patch size stats, core area, perimeter ratios, class metrics (clumpiness, cohesion)

3. **Connectivity Table** (`SH_WY{year}_{sensor}_{version}_connectivity.csv`)
   - Mean and SD lateral connectivity (m) across transects

4. **Visualizations** (`figures/`)
   - Habitat inundation time series
   - Percent water coverage by habitat
   - Connectivity time series with uncertainty bands
   - Patch size distribution over time
   - Core area distribution over time
   - Sentinel-1 vs Sentinel-2 comparison

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/spatio_hydrograph

# Specific module
pytest tests/test_habitat_analysis.py -v

# Watch mode (requires pytest-watch)
ptw tests/
```

### Code Quality

```bash
# Linting and formatting (ruff)
ruff check src/ tests/       # Check for violations
ruff format src/ tests/      # Auto-format code
ruff check src/ tests/ --fix # Fix issues

# Type checking (mypy)
mypy src/spatio_hydrograph/
```

### Project Structure

```
spatio_hydrograph/
├── src/spatio_hydrograph/
│   ├── __init__.py
│   ├── config.py                   # Configuration (23 tests)
│   ├── raster_processing.py        # Raster-to-vector (20+ tests)
│   ├── habitat_analysis.py         # Habitat analysis (15+ tests)
│   ├── landscape_metrics.py        # Landscape metrics (20+ tests)
│   ├── connectivity.py             # Connectivity (15+ tests)
│   └── visualization.py            # Visualization (10+ tests)
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_config.py              # 23 tests
│   ├── test_raster_processing.py   # 20+ tests
│   ├── test_habitat_analysis.py    # 15+ tests
│   ├── test_landscape_metrics.py   # 20+ tests
│   ├── test_connectivity.py        # 15+ tests
│   └── test_visualization.py       # 10+ tests
├── examples/
│   └── basic_usage.py
├── pyproject.toml                  # Project configuration
├── README.md                        # This file
├── LICENSE                         # MIT License
└── .github/workflows/ci.yml        # GitHub Actions CI
```

## Testing & Quality

- **80+ comprehensive tests** covering all modules
- **95%+ code coverage** with pytest
- **Full mypy compliance** for type safety
- **Ruff linting** for code quality
- **GitHub Actions CI** for continuous integration

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run quality checks:
   ```bash
   ruff check src/ tests/ --fix
   mypy src/spatio_hydrograph/
   pytest
   ```
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Citation

If you use this software, please cite:

```bibtex
@software{khanna_spatio_hydrograph_2026,
  author = {Khanna, Shruti and Romero Galvan, Fernando E. and Hestir, Erin L.},
  title = {Spatio-Hydrograph: Python Package for Yolo Bypass Inundation Analysis},
  year = {2026},
  version = {1.0.0},
  url = {https://github.com/ferg-dwr/spatio_hydrograph},
}
```

For other citation formats, see [CITATION.cff](CITATION.cff) or [CITATION.bib](CITATION.bib).

**Note:** Once a Zenodo DOI is assigned, the citation will include: `doi = {10.5281/zenodo.XXXXXXX}`

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Principal Investigator**: Erin L. Hestir (UC Davis)
- **Original Analysis**: Shruti Khanna (UC Davis)
- **Python Translation & Package Development**: Fernando E. Romero Galvan (California Department of Water Resources)
- **Data Sources**: Google Earth Engine, Sentinel-1 and Sentinel-2 imagery
- **Inspiration**: Landscape metrics from R `landscapemetrics` package

## Questions or Issues?

Please open an issue on [GitHub](https://github.com/ferg-dwr/spatio_hydrograph/issues).


## Installation

### From GitHub (development)

```bash
git clone https://github.com/ferg-dwr/spatio_hydrograph.git
cd spatio_hydrograph
pip install -e "."
```

### With development dependencies

```bash
pip install -e ".[dev]"
```

## Quick Start

### 1. Prepare Your Data

Organize your satellite water classification maps by water year and sensor:

```
data/
├── S1_WY2023/          # Sentinel-1 Lee Sigma classification
│   ├── water_2023-10-01.tif
│   ├── water_2023-10-15.tif
│   └── ...
├── S2_WY2023/          # Sentinel-2 AWEIsh classification
│   ├── water_2023-10-01.tif
│   ├── water_2023-10-15.tif
│   └── ...
└── vectors/
    ├── YoloBypassForSH_UTM_wat.shp    # Habitat polygons
    ├── parallel_lines.shp              # Connectivity transects
    └── polygon_slices.shp              # Volume calculation slices
```

### 2. Create Configuration File

Create `config.yaml`:

```yaml
# Analysis parameters
water_year: 2023
analysis_version: "_v5"

# Data directories
data_dir: "./data"
s1_input_dir: "./data/S1_WY2023"
s2_input_dir: "./data/S2_WY2023"
output_dir: "./output"

# Vector files
shapefiles:
  habitat_polygons: "vectors/YoloBypassForSH_UTM_wat.shp"
  connectivity_lines: "vectors/parallel_lines.shp"
  volume_slices: "vectors/polygon_slices.shp"

# Processing parameters
min_polygon_area_m2: 5000          # Minimum polygon size to retain
flood_trigger_habitats:
  - "First"
  - "Last"

# Landscape metrics configuration
landscape_metrics:
  patch_metrics:
    - "area"
    - "core_area"
    - "perimeter_area_ratio"
  class_metrics:
    - "clumpiness"
    - "cohesion"
  percentiles: [10, 50, 90]         # P10, P50, P90
```

### 3. Run Analysis

```python
from spatio_hydrograph.config import load_config
from spatio_hydrograph import SpatioHydrographAnalysis

# Load configuration
config = load_config("config.yaml")

# Initialize analysis
analysis = SpatioHydrographAnalysis(config)

# Run complete analysis
results = analysis.run()

# Results include:
# - Habitat area time series (CSV)
# - Landscape metrics (CSV)
# - Connectivity analysis (CSV)
# - Publication figures (TIFF)
```

## Module Documentation

### config.py

Configuration management and validation.

```python
from spatio_hydrograph.config import load_config, Config

config = load_config("config.yaml")
print(config.water_year)
print(config.output_dir)
```

### raster_processing.py

Raster-to-vector conversion and polygon operations.

```python
from spatio_hydrograph.raster_processing import RasterProcessor

processor = RasterProcessor(config)
polygons = processor.raster_to_polygons("water_2023-10-01.tif")
filtered = processor.filter_by_area(polygons, min_area_m2=5000)
habitat_water = processor.intersect_with_habitats(filtered)
```

### habitat_analysis.py

Per-habitat inundation calculations.

```python
from spatio_hydrograph.habitat_analysis import HabitatAnalyzer

analyzer = HabitatAnalyzer(config)
habitat_areas = analyzer.calculate_habitat_areas(polygons)
percent_water = analyzer.calculate_percent_inundated(habitat_areas)
```

### landscape_metrics.py

Landscape ecology metrics computation.

```python
from spatio_hydrograph.landscape_metrics import LandscapeMetrics

metrics = LandscapeMetrics(config)
patch_metrics = metrics.calculate_patch_metrics(classified_raster)
class_metrics = metrics.calculate_class_metrics(classified_raster)
```

### connectivity.py

Lateral connectivity analysis via transect intersections.

```python
from spatio_hydrograph.connectivity import ConnectivityAnalyzer

analyzer = ConnectivityAnalyzer(config)
connectivity = analyzer.analyze_connectivity(polygons, transect_lines)
```

### visualization.py

Plotting and figure generation.

```python
from spatio_hydrograph.visualization import Visualizer

viz = Visualizer(config)
viz.plot_habitat_time_series(habitat_areas)
viz.plot_lateral_connectivity(connectivity_results)
viz.plot_patch_size_distribution(landscape_metrics)
```

## Data Source

Satellite water classification maps derived from:
- **Sentinel-1**: Lee Sigma backscatter classification
- **Sentinel-2**: Automated Water Extraction Index (AWEIsh)

Processing via Google Earth Engine (data pre-computed and downloaded locally).

## Output Files

The package generates:

1. **Habitat Area Table** (`SH_WY{year}_{sensor}_{version}_habArea.csv`)
   - Date, habitat, inundated area (ha), % water coverage

2. **Landscape Metrics Table** (`SH_WY{year}_{sensor}_{version}_lmAll.csv`)
   - Patch size stats, core area, perimeter ratios, class metrics

3. **Connectivity Table** (`SH_WY{year}_{sensor}_{version}_connectivity.csv`)
   - Mean and SD lateral connectivity (m) across transects

4. **Visualizations** (`figures/`)
   - Time series plots (habitat inundation, percent water)
   - Connectivity time series with uncertainty
   - Patch size distribution
   - Core area distribution
   - Perimeter-area ratio distribution

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=src/spatio_hydrograph

# Only unit tests
pytest -m "not integration"

# Specific module
pytest tests/test_raster_processing.py -v
```

### Code Quality

```bash
# Linting and formatting
ruff check src/ tests/       # Check for style violations
ruff format src/ tests/      # Auto-format code
ruff check src/ tests/ --fix # Fix linting issues

# Type checking
mypy src/spatio_hydrograph/
```

### Project Structure

```
spatio_hydrograph/
├── src/spatio_hydrograph/
│   ├── __init__.py
│   ├── config.py                   # Configuration management
│   ├── raster_processing.py        # Raster-to-vector conversion
│   ├── landscape_metrics.py        # Landscape metrics
│   ├── connectivity.py             # Connectivity analysis
│   ├── habitat_analysis.py         # Habitat-specific calculations
│   └── visualization.py            # Plotting and output
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_config.py
│   ├── test_raster_processing.py
│   ├── test_landscape_metrics.py
│   ├── test_connectivity.py
│   ├── test_habitat_analysis.py
│   └── test_integration.py
├── examples/
│   ├── basic_usage.py
│   └── wy2023_analysis.ipynb
├── pyproject.toml
├── README.md
├── LICENSE
└── .github/workflows/ci.yml
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run linting and tests (`ruff check`, `black`, `mypy`, `pytest`)
5. Commit with clear messages
6. Push to your fork
7. Open a Pull Request

## Citation

If you use this software, please cite:

```bibtex
@software{khanna_spatio_hydrograph_2026,
  author = {Khanna, Shruti and Romero Galvan, Fernando E. and Hestir, Erin L.},
  title = {Spatio-Hydrograph: Python Package for Yolo Bypass Inundation Analysis},
  year = {2026},
  version = {1.0.0},
  url = {https://github.com/ferg-dwr/spatio_hydrograph},
}
```

## License

This project is licensed under the MIT License—see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Original Analysis**: Shruti Khanna (UC Davis)
- **Python Translation & Package Development**: Fernando E. Romero Galvan (California Department of Water Resources)
- **Data Sources**: Google Earth Engine, Sentinel-1 and Sentinel-2 imagery
- **Inspiration**: Landscape metrics from R `landscapemetrics` package

## Questions or Issues?

Please open an issue on [GitHub](https://github.com/ferg-dwr/spatio_hydrograph/issues).