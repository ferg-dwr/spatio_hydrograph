# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Integration example with `inundation` package (`examples/integration_with_inundation.py`)
- NOTICE.md with full attribution and acknowledgments
- CODE_OF_CONDUCT.md for community guidelines
- CONTRIBUTING.md with developer guidelines
- CHANGELOG.md with version history
- Pre-commit hooks configuration (.pre-commit-config.yaml)
- ISSUES_AND_MILESTONES.md document for project roadmap

### Changed
- Updated GitHub Actions to Node.js 24 compatible versions:
  - `actions/checkout@v4.2.0` (from v4)
  - `actions/setup-python@v5.0.0` (from v4)
- Enhanced README.md with inundation package integration instructions
- Improved error messages in integration example
- Better handling of missing configuration files in integration workflow

### Fixed
- Fixed matplotlib backend issue on headless Windows systems
  - Added `matplotlib.use('Agg')` in test_visualization.py
  - Ensures tests pass on CI/CD runners without display
- Fixed Windows file cleanup issue in test conftest.py
  - Replaced try-except-pass with `contextlib.suppress()`
  - Added graceful handling of rasterio file handles
  - Resolves ruff SIM105 linting warning
- Fixed unbound variable warnings in integration_with_inundation.py
  - Added stub functions for conditional imports
  - Prevents IDE type checker warnings

### Improved
- Integration example now works without config.yaml
- Better error messages when satellite data not available
- More informative demo mode output in integration workflow

---

## [1.0.0] - 2026-04-30

### Added
- Initial release of spatio-hydrograph package
- 6 core modules:
  - `config.py` - Configuration management (23 tests)
  - `raster_processing.py` - Raster I/O and processing (20+ tests)
  - `habitat_analysis.py` - Per-habitat water statistics (15+ tests)
  - `landscape_metrics.py` - Landscape ecology metrics (20+ tests)
  - `connectivity.py` - Lateral connectivity analysis (15+ tests)
  - `visualization.py` - Publication-ready plots (10+ tests)
- Comprehensive test suite with 108 tests
- Full type hints and mypy compliance
- Code quality tools: ruff, black, mypy
- GitHub Actions CI/CD pipeline:
  - Tests on Python 3.10, 3.11, 3.12
  - Tests on Ubuntu, macOS, Windows
  - Code coverage reporting to Codecov
- README.md with comprehensive documentation
- CITATION.cff and CITATION.bib for scientific citation
- MIT License
- Basic integration capability with `inundation` package

### Features

#### Configuration Management
- YAML-based configuration
- Support for Sentinel-1 and Sentinel-2 water maps
- Customizable habitat and transect shapefiles
- Landscape metrics configuration options
- Automatic output directory creation

#### Raster Processing
- Convert water classification rasters to vector polygons
- Filter polygons by minimum area threshold
- Intersect water polygons with habitat boundaries
- Extract polygon centroids
- Support for multiple CRS and automatic reprojection

#### Habitat Analysis
- Calculate inundated area per habitat type
- Compute percent inundated statistics
- Identify flood status (dry/partial/flooded)
- Aggregate statistics by water year
- Handle missing data gracefully

#### Landscape Metrics
- Patch-level metrics:
  - Area statistics (mean, sd, percentiles)
  - Core area statistics (with configurable edge distance)
  - Perimeter-area ratio (PARA) statistics
  - Patch shape metrics
- Class-level metrics:
  - Clumpiness index
  - Cohesion index
  - Both clamped to valid range [0, 1]
- Percentile-based statistics (p10, p50, p90)

#### Connectivity Analysis
- Transect-based connectivity measurement
- Lateral connectivity calculation
- Connectivity statistics and bottleneck identification
- Endpoint calculation for spatial analysis
- Percentile-based threshold detection

#### Visualization
- Time series plots (habitat inundation over time)
- Percent water distribution by habitat
- Lateral connectivity trends
- Patch size distribution analysis
- Core area distribution analysis
- Multi-sensor comparison plots
- Support for error bands in time series
- High-resolution output (300 dpi)

### Technical Achievements
- 100% test coverage for core functionality
- Full mypy compliance (0 errors)
- Ruff linting passes (0 errors)
- Works on Windows, macOS, and Linux
- Compatible with Python 3.10, 3.11, 3.12
- Non-blocking visualization by default (show=False)
- Proper error handling and user feedback

### Documentation
- Comprehensive README with quick start
- Google-style docstrings on all public functions
- Type hints on all functions and methods
- Usage examples in docstrings
- Integration example Jupyter notebook

### CI/CD Infrastructure
- GitHub Actions workflow for continuous integration
- Multi-platform testing (Ubuntu, macOS, Windows)
- Multi-version Python testing (3.10-3.12)
- Code coverage reporting
- Automated linting and type checking
- PR checks for code quality

---

## Release Notes

### Version 1.0.0 Key Features
- ✅ Complete spatio-temporal water mapping
- ✅ Habitat-specific inundation analysis
- ✅ Landscape ecological metrics
- ✅ Lateral connectivity assessment
- ✅ Publication-ready visualizations
- ✅ Integration with water level sensors
- ✅ Multi-platform support

### Known Limitations
- Sentinel-2 cloud cover requires pre-processing
- Landscape metrics require sufficient water extent
- Connectivity analysis limited to transect lines
- Some Windows-specific file handling quirks (addressed in updates)

---

## Future Roadmap

### Version 1.1.0 (Planned)
- Community documentation (NOTICE.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md)
- Enhanced README
- Pre-commit hooks setup
- Better error messages

### Version 1.2.0 (Planned)
- Sphinx documentation setup
- ReadTheDocs integration
- API documentation generation
- User guides and tutorials

### Version 1.3.0 (Planned)
- Expanded integration tests
- Scientific correctness validation
- Caching system for large datasets
- Performance optimizations

### Version 1.5.0+ (Future)
- PyPI publishing (pending DWR approval)
- Real-time data streaming capability
- Advanced visualization (interactive maps)
- Statistical modeling of inundation patterns
- Climate change impact analysis

---

## Migration Guides

### From 0.x to 1.0.0
Complete rewrite. No breaking changes, first stable release.

---

## Deprecated Features

None yet. All features are production-ready.

---

## Security

For security issues, please see [SECURITY.md](SECURITY.md).

---

## Attribution

This project builds on:
- Original R `inundation` package (Clark & Goertler, 2022)
- Original research (Goertler et al., 2017)
- Landscape metrics methodology (Hesselbarth et al., 2019)

See [NOTICE.md](NOTICE.md) for full attribution.

---

## Contributors

### v1.0.0
- Shruti Khanna (UC Davis) - Original analysis
- Erin L. Hestir (UC Davis) - Principal Investigator
- Fernando E. Romero Galvan (California DWR) - Python implementation
- Jeanette Clark - Original R package author
- Pascale A.L. Goertler - Original R package author

---

## How to Read This Changelog

- **[Unreleased]** - Changes in development, not yet released
- **[X.Y.Z]** - Released versions with dates
- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Features that will be removed soon
- **Removed** - Features that were removed
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes

---

## Release Schedule

Releases follow semantic versioning:
- **Major** (X.0.0) - Breaking changes
- **Minor** (0.X.0) - New features (backward compatible)
- **Patch** (0.0.X) - Bug fixes (backward compatible)

---

## Questions?

For questions about the changelog or release process, see:
- [MAINTAINERS.md](MAINTAINERS.md) - Project maintainers
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [GitHub Issues](https://github.com/ferg-dwr/spatio_hydrograph/issues) - Project issues

---

Last updated: 2026-05-11
