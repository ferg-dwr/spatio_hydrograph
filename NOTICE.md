# NOTICE.md

## Attribution and Acknowledgments

This project builds upon and integrates with several foundational works and institutions. We are grateful for their contributions to water resource science and management.

---

## Original Research

**Goertler et al. (2017)** - Scientific Foundation

The inundation analysis methodology implemented in this package is based on ecological research in the Yolo Bypass:

> Goertler, P. A. L., Sommer, T., Satterthwaite, W. H., & Schreier, B. M. (2017). Ecological patterns of species dominance in Yolo Bypass, California. *Ecology of Freshwater Fish*, 26(3), 415–426. https://doi.org/10.1111/eff.12372

This seminal work established the foundation for understanding inundation dynamics and their ecological significance in the Yolo Bypass.

---

## Original R Package

**inundation R Package** - Python Translation Source

The Python implementation of the inundation calculation algorithms is translated from the original R package:

**Authors:** Jeanette Clark and Pascale A.L. Goertler (2022)  
**Repository:** https://github.com/goertler/inundation  
**Zenodo:** https://doi.org/10.5281/zenodo.6450272  
**License:** Apache License 2.0

The original R package provided the calculation methodology and algorithms that this Python package implements and extends.

---

## Principal Investigator

**Erin L. Hestir** (University of California, Davis)

Dr. Hestir is the Principal Investigator for the spatio-temporal inundation mapping research and provides scientific direction for this work.

---

## Original Analysis & Development

**Shruti Khanna** (University of California, Davis)

Conducted the original analysis of Yolo Bypass inundation patterns and water resource dynamics that inform this package.

---

## Python Translation & Package Development

**Fernando E. Romero Galvan** (California Department of Water Resources)

Translated the R `inundation` package to Python, developed the `spatio-hydrograph` package for satellite-based water mapping and landscape analysis, and integrated both packages for comprehensive inundation monitoring.

---

## Data Sources

### California Department of Water Resources (CDEC)

**Fremont Weir Data:** Hourly stage height measurements of the Sacramento River  
**Source:** https://cdec.water.ca.gov/  
**Data Used:** Water level measurements from January 1, 1984 to present  
**Contact:** California Department of Water Resources

### California Natural Resources Agency (CNRA)

**Dayflow Data:** Daily modeled flow data for Sacramento River and Yolo Bypass  
**Source:** https://data.cnra.ca.gov/dataset/dayflow  
**Data Used:** Flow measurements from October 1, 1955 to present  
**Contact:** California Natural Resources Agency

### European Commission - Copernicus Programme

**Sentinel-1 Synthetic Aperture Radar (SAR)**  
**Sentinel-2 Multispectral Imagery**  
**Source:** https://www.copernicus.eu/  
**License:** Open Access  
**Data Used:** Water classification maps for Yolo Bypass region

---

## Scientific Foundation

### Related Work & References

1. **Landscape Metrics** - R package `landscapemetrics`
   - Hesselbarth, M. H. K., Sciaini, M., With, K. A., Wiegand, K., & Nowosad, J. (2019).
   - https://r-spatialecology.github.io/landscapemetrics/

2. **Sentinel-1 SAR for Water Detection**
   - Twele, A., Cao, W., Plank, S., & Martinis, S. (2016)
   - SAR-based remote sensing of water surfaces and wetlands
   - https://doi.org/10.1016/j.rse.2015.10.014

3. **MODIS Vegetation Indices**
   - Fensholt, R., & Sandholt, I. (2012)
   - Index-based melt modeling for hydrological applications
   - https://doi.org/10.1016/j.rse.2012.02.009

---

## AI Assistance

This package was developed with assistance from **Anthropic's Claude** AI for:
- Code translation and refactoring
- Documentation generation
- Test development and debugging
- Type hint annotation
- Code quality improvements and optimization

The final code, architecture, and scientific accuracy were reviewed and verified by human developers.

---

## California State Government

**Funding & Support:**

Development of this package was supported by the California Department of Water Resources (DWR) as part of ongoing research into Yolo Bypass water resource management and ecological monitoring.

---

## Open Source Community

This project relies on the excellent open-source Python ecosystem:

- **GeoPandas** - Spatial data analysis
- **Rasterio** - Raster I/O
- **Pandas** - Data manipulation
- **NumPy & SciPy** - Numerical computing
- **Matplotlib & Seaborn** - Visualization
- **Xarray & RioXArray** - Multi-dimensional arrays
- **scikit-image** - Image processing

---

## License Compatibility

**spatio-hydrograph:** MIT License  
**inundation:** Apache License 2.0  
**Original R inundation:** Apache License 2.0  

All licenses are compatible and this project respects the terms of all dependencies.

---

## Citation

If you use this package in your research, please cite:

### Primary Citation

```bibtex
@software{khanna_spatio_hydrograph_2026,
  author = {Khanna, Shruti and Romero Galvan, Fernando E. and Hestir, Erin L.},
  title = {Spatio-Hydrograph: Python Package for Yolo Bypass Inundation Analysis},
  year = {2026},
  url = {https://github.com/ferg-dwr/spatio_hydrograph},
  version = {1.0.0}
}
```

### If Using Inundation Data

```bibtex
@software{dwr_inundation_2026,
  author = {Romero Galvan, Fernando E. and Clark, Jeanette and Goertler, Pascale A.L.},
  title = {inundation: Python Package for Yolo Bypass Inundation Duration},
  year = {2026},
  url = {https://github.com/ferg-dwr/inundation},
  version = {0.2.0}
}

@software{clark_goertler_2022,
  title = {inundation},
  author = {Clark, Jeanette and Goertler, Pascale A.L.},
  year = {2022},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.6450272}
}
```

### If Using Original Research

```bibtex
@article{goertler_2017,
  author = {Goertler, P. A. L. and Sommer, T. and Satterthwaite, W. H. and Schreier, B. M.},
  year = {2017},
  title = {Ecological patterns of species dominance in {Y}olo {B}ypass, {C}alifornia},
  journal = {Ecology of Freshwater Fish},
  volume = {26},
  number = {3},
  pages = {415--426},
  doi = {10.1111/eff.12372}
}
```

---

## Questions or Corrections

If you believe something is missing or inaccurate in this attribution document, please:

1. Open an issue on GitHub: https://github.com/ferg-dwr/spatio_hydrograph/issues
2. Contact the maintainers: See MAINTAINERS.md
3. Follow the process in CONTRIBUTING.md

We take attribution seriously and will promptly address any corrections.

---

## Version History

- **v1.0.0** (2026-04-30) - Initial release with comprehensive attribution
- **Created:** 2026-05-11

Last updated: 2026-05-11
