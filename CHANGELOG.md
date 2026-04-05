# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-15

### Added
- Initial release of Stepwise Regression Analysis framework
- Bidirectional stepwise selection algorithm with VIF control
- Z-score standardization with validation
- Publication-ready statistical tables (Model Summary, ANOVA, Coefficients)
- Incremental model building with step-by-step statistics
- Excel output with multiple sheets per component
- Comprehensive descriptive statistics validation
- Support for VPCA loadings and spectral library data
- Example notebooks demonstrating complete workflows
- SPSS validation guide for result verification
- Professional documentation (README, CITATION, CONTRIBUTING)
- MIT License for open-source distribution

### Features
- Configurable p-value thresholds (p_enter, p_remove)
- Configurable VIF threshold for multicollinearity control
- Automatic history tracking of variable selection steps
- Zero-order correlation calculation
- R², Adjusted R², F-statistics, and significance testing
- Support for multiple dependent variables (VPCs)
- Robust data loading with automatic wavelength alignment
- Population standard deviation (ddof=0) for z-scores

### Documentation
- Complete README with quick start guide
- CITATION.cff for academic citation
- SPSS Testing Guide for validation
- Code examples and tutorials
- Methodology documentation

### Initial Contributors
- Abdulrahman Hussein (Kent State University)

---

## Future Releases

### [1.1.0] - Planned
- Add weighted regression support
- Implement cross-validation
- Add model diagnostic visualizations
- Performance optimizations

### [1.2.0] - Planned
- Support for categorical predictors
- Integration with scikit-learn pipelines
- Additional statistical tests
- Enhanced plotting capabilities
