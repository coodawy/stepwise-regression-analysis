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
git clone https://github.com/coodawy/stepwise-regression-analysis.git
cd stepwise-regression-analysis

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import pandas as pd
from stepwise import stepwise_bidirectional, build_regression_tables

# Load your data
loadings = pd.read_csv('vpca_loadings.csv', index_col='Wavelength')
library = pd.read_csv('spectral_library.csv', index_col='Wavelength')

# Run stepwise regression
selected_vars, history = stepwise_bidirectional(
    y=loadings['VPC1'],
    X=library,
    p_enter=0.05,
    p_remove=0.10,
    vif_threshold=2.0
)

# Generate statistical tables
summary_df, anova_df, coef_df = build_regression_tables(
    vpc_name='VPC1',
    y=loadings['VPC1'],
    X=library,
    selected=selected_vars,
    history=history
)
```

See `examples/` for complete workflows.

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
├── src/                                # Source code
│   ├── stepwise_vif.py                # Core stepwise algorithm
│   ├── preprocessing.py               # Data preprocessing utilities
│   ├── vif_utils.py                   # VIF calculation functions
│   └── vpca_integration.py            # VPCA data loading
│
├── examples/                           # Example notebooks
│   ├── Stepwise-learning-Code Writing-v2.ipynb
│   └── complete_tutorial.ipynb
│
├── docs/                               # Documentation
│   ├── METHODOLOGY.md                 # Detailed methodology
│   ├── USAGE_GUIDE.md                 # User guide
│   └── SPSS_Testing_Guide.md          # Validation guide
│
└── tests/                              # Test data
    ├── test_loadings.csv
    └── test_library.csv
```

## 📚 Citation

If you use this software in your research, please cite it as:

```bibtex
@software{Hussein_Stepwise_Regression_2025,
  author = {Hussein, Abdulrahman},
  title = {Stepwise Regression Analysis for Spectral Data},
  year = {2025},
  url = {https://github.com/coodawy/stepwise-regression-analysis},
  version = {1.0.0}
}
```

## 🔬 Development Status

**Current Version**: 1.0.0 (Initial Release)

**Roadmap**:
- [ ] Add support for weighted regression
- [ ] Implement cross-validation
- [ ] Add visualization tools for model diagnostics
- [ ] Support for categorical predictors
- [ ] Integration with scikit-learn pipelines

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
PhD Student, Department of Geography  
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

This research was conducted at the **Department of Geography, Kent State University** under the supervision of **Dr. Scott Sheridan**.

**Funding**: This work was supported by Kent State University Graduate Student Senate Research Grant.

Special thanks to the open-source community for the foundational libraries: pandas, numpy, statsmodels, and scipy.

---

**Keywords**: stepwise regression, spectral analysis, VIF, multicollinearity, hyperspectral, remote sensing, VPCA, statistical modeling, Python
