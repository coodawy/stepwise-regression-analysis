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

## [1.2.0] - 2026-04-27

### Changed
- Complete rewrite of `StepwiseRegressionVIF.ipynb` for clarity and maintainability
- Removed redundant forward-only and backward-only methods; framework is now strictly bidirectional
- Replaced absolute file paths in examples with repo-relative paths

### Added
- SPSS-style incremental regression tables (Model Summary, ANOVA, Coefficients) exported per VPC component
- `IterationHistory` sheet in Excel output tracking every ADD / REMOVE_P / REMOVE_VIF step
- `Descriptive_Stats` sheet for z-score sanity checking
- `score()` method on `StepwiseVIFRegression` for sklearn-compatible model evaluation
- `plot_all_components()` for R² and material-count overview across all VPCs
- Input validation warnings (`n_features > n_samples`, `p_remove < p_enter`, `vif_threshold <= 1`)
- VIF-removed variables are returned to the candidate pool (matches v3 learning-notebook logic)
- `StepwiseRegressionVIF_pre_rewrite.ipynb` preserved as backup

### Fixed
- VIF-skip bug: if a candidate's VIF exceeded the threshold, it was permanently skipped instead of trying the next best candidate
- Removed unused `seaborn` import that caused `ModuleNotFoundError` on fresh environments
- Unified cell numbering and clear section titles throughout the notebook

---

## Future Releases

### [1.3.0] - Planned
- Add weighted regression support
- Implement cross-validation
- Add model diagnostic visualizations
- Performance optimizations

### [1.4.0] - Planned
- Support for categorical predictors
- Integration with scikit-learn pipelines
- Additional statistical tests
- Enhanced plotting capabilities
