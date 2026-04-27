# Stepwise Regression Analysis for Spectral Data

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> A Python-based bidirectional stepwise regression framework for spectral analysis with VIF control, designed to replace traditional statistical software workflows.

## 🌟 Impact Statement

This tool enables researchers to perform rigorous stepwise regression analysis on spectral data using open-source Python, eliminating dependency on proprietary statistical software. The framework implements bidirectional variable selection with Variance Inflation Factor (VIF) control, generating publication-ready statistical tables including Model Summary, ANOVA, and Coefficients tables with incremental model building.

Developed for hyperspectral remote sensing applications, this tool has been validated against traditional statistical software outputs, ensuring reproducibility and transparency in spectral unmixing and component analysis workflows.

## ✨ Key Features

- **Bidirectional Stepwise Selection**: Forward and backward variable selection with configurable p-value thresholds
- **VIF Control**: Automatic multicollinearity detection and removal using Variance Inflation Factor
- **Incremental Model Tables**: Generates step-by-step model building statistics
- **Publication-Ready Output**: Excel files with Model Summary, ANOVA, and Coefficients tables
- **Z-Score Standardization**: Built-in data standardization with validation
- **Flexible Data Input**: Handles VPCA loadings and spectral library data
- **Comprehensive Validation**: Descriptive statistics and quality checks

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/abdulrahman-R-A-hussein/stepwise-regression-analysis.git
cd stepwise-regression-analysis

# Install dependencies
pip install -r requirements.txt
```

### Three ways to use it

#### 1. Desktop app (Streamlit) - easiest

```bash
streamlit run app.py
```

A local web UI opens in your browser with drag-and-drop CSV upload, sliders for `p_enter` / `p_remove` / `vif_threshold`, interactive results tabs (Summary, VIF, Iteration History, Plots), and one-click Excel/CSV download.

#### 2. Notebook (slim orchestrator)

Open `framework/StepwiseRegressionVIF.ipynb` and run the 5 cells top-to-bottom. All heavy logic is imported from the `framework/` package; the notebook itself is just configuration + 4 calls.

#### 3. Python API

```python
from framework import VPCAStepwiseAnalysis

analyzer = VPCAStepwiseAnalysis(
    p_enter=0.05, p_remove=0.10, vif_threshold=2.0, verbose=1,
)
analyzer.load_data("loadings.csv", "library.csv")
summary, detailed = analyzer.run_analysis()
analyzer.export_results("output/")
```

See `learning/notebooks/` for tutorial materials and `framework/StepwiseRegressionVIF.ipynb` for the canonical workflow.

## 📊 Methodology

### Bidirectional Stepwise Selection

The algorithm implements a two-stage selection process:

1. **Forward Step**: Adds the variable with the lowest p-value (< p_enter threshold)
2. **Backward Step**: Removes variables with p-values > p_remove threshold
3. **VIF Check**: Removes variables exceeding VIF threshold to control multicollinearity

### Statistical Output

Generates three comprehensive tables for each model:

- **Model Summary**: R, R², Adjusted R², Standard Error, R² Change, F Change, Significance
- **ANOVA**: Regression, Residual, and Total sum of squares with F-statistics
- **Coefficients**: Standardized Beta, Standard Error, t-values, p-values, Zero-order correlations, VIF

### Z-Score Standardization

All variables are standardized using population standard deviation (ddof=0):

```
z = (x - μ) / σ
```

This ensures mean = 0 and standard deviation = 1 for all variables.

## 📁 Project Structure

```
stepwise-regression-analysis/
├── README.md                           # This file
├── LICENSE                             # MIT License
├── CITATION.cff                        # Citation metadata
├── CONTRIBUTING.md                     # Contribution guidelines
├── CHANGELOG.md                        # Version history
├── requirements.txt                    # Python dependencies
│
├── app.py                              # Streamlit desktop app
│
├── framework/                          # Core Python framework
│   ├── stepwise_vif.py                # StepwiseVIFRegression class (bidirectional)
│   ├── regression_tables.py           # SPSS-style Model Summary / ANOVA / Coefficients
│   ├── vpca_integration.py            # VPCAStepwiseAnalysis (high-level wrapper)
│   ├── preprocessing.py               # Z-score standardization
│   ├── vif_utils.py                   # VIF calculations
│   ├── sample_library.py              # Synthetic spectra (testing only)
│   ├── plots.py                       # Matplotlib visualization helpers
│   ├── StepwiseRegressionVIF.ipynb    # Slim 5-step orchestrator notebook
│   └── __init__.py                    # Package exports
│
├── learning/                           # Development & testing materials
│   ├── notebooks/                     # Learning notebooks
│   │   ├── Stepwise-learning-Code Writing-v2.ipynb
│   │   └── complete_tutorial.ipynb
│   ├── test-data/                     # Sample datasets
│   │   ├── test_loadings.csv
│   │   └── test_library.csv
│   └── spss-files/                    # SPSS validation files
│
└── docs/                               # Documentation
    └── SPSS_Testing_Guide.md          # Validation guide
```

## 📚 Citation

If you use this software in your research, please cite it as:

```bibtex
@software{Hussein_Stepwise_Regression_2026,
  author = {Hussein, Abdulrahman},
  title = {Stepwise Regression Analysis for Spectral Data},
  year = {2026},
  url = {https://github.com/abdulrahman-R-A-hussein/stepwise-regression-analysis},
  version = {1.2.0}
}
```

## 🔬 Development Status

**Current Version**: 1.2.0 - rewritten notebook, bidirectional-only, Streamlit desktop app

**Roadmap**:
- [ ] Add support for weighted regression
- [ ] Implement cross-validation
- [ ] Add visualization tools for model diagnostics
- [ ] Support for categorical predictors
- [ ] Integration with scikit-learn pipelines
- [ ] Package the desktop app as a standalone `.exe` (PyInstaller)

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ways to contribute**:
- Report bugs via GitHub Issues
- Suggest new features
- Submit pull requests
- Improve documentation
- Share your use cases

## 📧 Contact

**Abdulrahman Hussein**  
PhD Student, Department of Earth Sciences  
Kent State University  

**ORCID**: [0009-0003-0401-9219](https://orcid.org/0009-0003-0401-9219)  
**Website**: [www.climtawy.com](https://www.climtawy.com)  
**Email**: ahusse12@kent.edu

**Social**:
- [LinkedIn](https://www.linkedin.com/in/climatawy/)
- [GitHub](https://github.com/coodawy)
- [Google Scholar](https://scholar.google.com/citations?user=TQEmmAoAAAAJ)
- [ResearchGate](https://www.researchgate.net/profile/Abdulrahman-Hussein-5)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

This research was conducted at the **Department of Earth Sciences, Kent State University** under the supervision of **Dr. Joseph D. Ortiz**.

Special thanks to the open-source community for the foundational libraries: pandas, numpy, statsmodels, and scipy.

---

**Keywords**: stepwise regression, spectral analysis, VIF, multicollinearity, hyperspectral, remote sensing, VPCA, statistical modeling, Python
