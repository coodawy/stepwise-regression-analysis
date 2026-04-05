# Stepwise Regression Framework

This folder contains the core Python framework for bidirectional stepwise regression analysis with VIF control.

## 📁 Core Modules

### `stepwise_vif.py`
Main stepwise regression algorithm with:
- Bidirectional variable selection (forward + backward)
- VIF-based multicollinearity control
- History tracking for incremental model building
- Configurable p-value thresholds

### `preprocessing.py`
Data preprocessing utilities:
- Z-score standardization (population std, ddof=0)
- Data validation and quality checks
- Missing value handling

### `vif_utils.py`
Variance Inflation Factor calculations:
- VIF computation for multicollinearity detection
- Automatic high-VIF variable removal
- VIF threshold configuration

### `vpca_integration.py`
VPCA data loading and integration:
- Robust CSV loading with wavelength alignment
- Column name standardization (VPC1-VPC6)
- Legacy format support

### `sample_library.py`
Spectral library management:
- Library data loading and validation
- Material name handling
- Wavelength matching

### `plots.py`
Visualization utilities:
- Regression diagnostic plots
- VIF visualization
- Model comparison plots

### `__init__.py`
Package initialization and exports

## 🚀 Usage

```python
from framework.stepwise_vif import stepwise_bidirectional
from framework.preprocessing import zscore_dataframe
import pandas as pd

# Load data
loadings = pd.read_csv('vpca_loadings.csv', index_col='Wavelength')
library = pd.read_csv('spectral_library.csv', index_col='Wavelength')

# Standardize
z_loadings = zscore_dataframe(loadings)
z_library = zscore_dataframe(library)

# Run stepwise regression
selected_vars, history = stepwise_bidirectional(
    y=z_loadings['VPC1'],
    X=z_library,
    p_enter=0.05,
    p_remove=0.10,
    vif_threshold=2.0,
    verbose=True
)

print(f"Selected variables: {selected_vars}")
```

## 🔧 Configuration

Key parameters:
- **p_enter**: Threshold for adding variables (default: 0.05)
- **p_remove**: Threshold for removing variables (default: 0.10)
- **vif_threshold**: Maximum VIF allowed (default: 2.0)
- **verbose**: Print step-by-step progress (default: False)

## 📊 Output

The framework generates:
- List of selected variables
- Step-by-step history with actions (ADD/REMOVE)
- Statistical metrics (R², p-values, VIF)
- Publication-ready tables (Model Summary, ANOVA, Coefficients)

## 🔬 Methodology

Based on bidirectional stepwise selection:
1. **Forward step**: Add variable with lowest p-value < p_enter
2. **Backward step**: Remove variables with p-value > p_remove
3. **VIF check**: Remove variables with VIF > threshold
4. Repeat until convergence

## ⚠️ Important Notes

- All variables must be z-scored before analysis
- Uses population standard deviation (ddof=0) for standardization
- VIF threshold of 2.0 is conservative; adjust based on your needs
- History tracking enables incremental model table generation

## 📚 See Also

- `../learning/`: Development and testing notebooks
- `../docs/`: Complete documentation
- Main README.md for project overview
