# Contributing to spatio-hydrograph

Thank you for your interest in contributing to spatio-hydrograph! This document provides guidance for developers, testers, and contributors.

---

## Code of Conduct

Please review our [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to abide by its terms.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Virtual environment (venv or conda)

### Development Setup

1. **Fork the repository**
   ```bash
   # On GitHub, click "Fork"
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR-USERNAME/spatio_hydrograph.git
   cd spatio_hydrograph
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

5. **Install pre-commit hooks (recommended)**
   ```bash
   pip install pre-commit
   pre-commit install
   ```
   
   This automatically runs linting, formatting, and type checks before each commit.

6. **Verify installation**
   ```bash
   pytest tests/ -v
   ```

---

## Development Workflow

### Creating a Feature Branch

```bash
# Create a descriptive branch name
git checkout -b feature/my-amazing-feature
# or
git checkout -b bugfix/issue-description
# or
git checkout -b docs/improve-readme
```

**Branch naming conventions:**
- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation improvements
- `test/` - Test additions
- `refactor/` - Code refactoring
- `perf/` - Performance improvements

### Making Changes

1. **Write code** following the [Code Style](#code-style) guidelines
2. **Add tests** for new functionality
3. **Update documentation** if needed
4. **Run local checks** (see below)

### Running Local Checks

Before committing, run these checks locally:

```bash
# Lint and auto-fix issues
ruff check src/ tests/ --fix

# Format code
black src/ tests/

# Type checking
mypy src/spatio_hydrograph/

# Run tests
pytest tests/ -v --cov

# Run only non-integration tests (faster)
pytest tests/ -v -m "not integration"
```

Or run all at once:
```bash
pre-commit run --all-files
```

### Committing Changes

Write clear, descriptive commit messages:

```bash
# Good commit message
git commit -m "feat: add landscape metrics calculation

- Implement patch metrics (area, shape index)
- Add core area statistics
- Include percentile calculations
- Add comprehensive tests"

# Reference issues in commit message
git commit -m "fix: resolve Windows cleanup issue (#42)

Fixes rasterio file handle issue on Windows by using
contextlib.suppress() for graceful cleanup."
```

**Commit message format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

- **type**: feat, fix, docs, style, refactor, test, chore
- **scope**: module affected (config, raster_processing, etc)
- **subject**: brief, imperative (add not added, fix not fixed)
- **body**: detailed explanation if needed
- **footer**: references to issues (Fixes #123)

### Pushing and Creating a Pull Request

```bash
# Push to your fork
git push origin feature/my-amazing-feature

# On GitHub, click "Compare & pull request"
```

**Pull Request guidelines:**
- Write a clear title and description
- Reference related issues (#123)
- Explain your changes and why they're needed
- Ensure all CI checks pass
- Be responsive to review feedback

---

## Code Style

### General Principles

- **PEP 8** compliance via Ruff
- **Type hints** on all public functions
- **Docstrings** in Google style
- **Lines** under 100 characters
- **Imports** organized (isort)

### Example Function

```python
def calculate_habitat_areas(
    water_polygons: geopandas.GeoDataFrame,
    habitat_polygons: geopandas.GeoDataFrame,
) -> pd.DataFrame:
    """Calculate inundated area per habitat type.
    
    Parameters
    ----------
    water_polygons : geopandas.GeoDataFrame
        Polygons representing water extent
    habitat_polygons : geopandas.GeoDataFrame
        Polygons representing habitat types
    
    Returns
    -------
    pd.DataFrame
        Habitat name and inundated area in hectares
    
    Raises
    ------
    ValueError
        If required columns are missing
    
    Examples
    --------
    >>> areas = calculate_habitat_areas(water_gdf, habitat_gdf)
    >>> print(areas)
    """
    # Implementation
    pass
```

### Type Hints

```python
# Good
def process_raster(path: str, config: Config) -> np.ndarray:
    pass

# Also good
from typing import Optional
def get_data(refresh: bool = False) -> Optional[pd.DataFrame]:
    pass
```

### Docstring Template

```python
def my_function(param1: str, param2: int) -> dict:
    """One-line summary of what the function does.
    
    Longer description if needed. Explain the purpose,
    special considerations, and any gotchas.
    
    Parameters
    ----------
    param1 : str
        Description of param1
    param2 : int
        Description of param2
    
    Returns
    -------
    dict
        Description of return value
    
    Raises
    ------
    ValueError
        When something is invalid
    
    See Also
    --------
    related_function : Description
    
    Examples
    --------
    >>> result = my_function("test", 42)
    >>> print(result)
    """
    pass
```

---

## Testing

### Writing Tests

- **Location**: `tests/test_<module>.py`
- **Class naming**: `Test<FunctionName>`
- **Method naming**: `test_<scenario>`
- **Coverage target**: 80%+

### Test Structure

```python
import pytest
from spatio_hydrograph.config import Config

class TestCalculateHabitatAreas:
    """Tests for calculate_habitat_areas function."""
    
    def test_basic_calculation(self, sample_config: Config) -> None:
        """Test basic habitat area calculation."""
        # Arrange
        habitat_gdf = create_sample_habitat_polygons()
        water_gdf = create_sample_water_polygons()
        
        # Act
        result = calculate_habitat_areas(water_gdf, habitat_gdf)
        
        # Assert
        assert len(result) > 0
        assert "area_ha" in result.columns
    
    def test_missing_columns_raises_error(self) -> None:
        """Test that missing required columns raise ValueError."""
        bad_gdf = geopandas.GeoDataFrame()
        
        with pytest.raises(ValueError, match="Missing required"):
            calculate_habitat_areas(bad_gdf, bad_gdf)
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_habitat_analysis.py -v

# Run specific test class
pytest tests/test_habitat_analysis.py::TestCalculateHabitatAreas -v

# Run with coverage report
pytest tests/ -v --cov=src/spatio_hydrograph --cov-report=html

# Run excluding slow tests
pytest tests/ -v -m "not slow"
```

---

## Documentation

### Updating README

The README is the first thing users see. If you make significant changes:
1. Update relevant sections
2. Ensure examples still work
3. Check links are valid
4. Review formatting

### Writing Examples

Keep examples:
- **Simple** - focus on common use cases
- **Working** - test them to ensure they run
- **Commented** - explain what's happening
- **Self-contained** - don't require external files

### Docstring Examples

```python
def my_function(x: int) -> int:
    """Calculate something.
    
    Parameters
    ----------
    x : int
        Input value
    
    Returns
    -------
    int
        Result
    
    Examples
    --------
    >>> result = my_function(5)
    >>> print(result)
    10
    """
    return x * 2
```

---

## Reporting Issues

### Bug Reports

Include:
- Clear title and description
- Python version and OS
- Minimal code to reproduce
- Expected vs actual behavior
- Error messages and traceback
- Steps to reproduce

**Example:**
```markdown
## Bug: Raster loading fails on Windows

**Environment:**
- Python 3.12.1
- Windows 11
- spatio-hydrograph v1.0.0

**Reproduction:**
```python
from spatio_hydrograph import RasterProcessor
processor = RasterProcessor(config)
processor.raster_to_polygons("path/to/file.tif")
```

**Error:**
```
FileNotFoundError: Cannot find C:\Users\...
```

**Expected:** Should load the raster file
**Actual:** Throws FileNotFoundError

**Steps:**
1. Create a config pointing to a tif file on Windows
2. Call raster_to_polygons()
3. See error
```

### Feature Requests

Include:
- Clear description of desired behavior
- Use cases and benefits
- Alternative approaches considered
- Links to related issues/PRs

---

## Review Process

### What Happens After You Submit a PR

1. **Automated Checks** - CI/CD pipeline runs tests and linting
2. **Code Review** - Maintainers review your code
3. **Discussion** - Address feedback and make changes
4. **Approval** - PR is approved
5. **Merge** - Your contribution is merged! 🎉

### Responding to Feedback

- Be open to suggestions
- Ask questions if unclear
- Don't take criticism personally
- Update your PR with requested changes
- Ask for re-review once updated

---

## Release Process

The maintainers handle releases, but here's the process:

1. **Version bump** in `pyproject.toml`
2. **Update CHANGELOG.md** with changes
3. **Create GitHub release** with version tag
4. **Build distributions** (wheel + sdist)
5. **Publish to PyPI** (when approved)

---

## Getting Help

### Resources

- **Documentation**: Check the README and CONTRIBUTING.md
- **Issues**: Search existing issues for answers
- **Discussions**: Open a discussion for questions
- **Code Examples**: See `examples/` directory

### Asking Questions

If stuck:
1. Check documentation and examples
2. Search existing issues/discussions
3. Open a new issue with `[QUESTION]` in title
4. Include what you've tried and what failed

---

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Project README
- Release notes
- CHANGELOG.md

---

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).

---

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

## Questions?

- Check [MAINTAINERS.md](MAINTAINERS.md) for contact info
- Open an issue on GitHub
- Review existing issues and discussions

Thank you for contributing!
