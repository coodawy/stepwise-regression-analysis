"""
VIF utilities: calculate_vif, fit_ols, get_model_metrics.

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
"""

from __future__ import annotations

from typing import Dict, Tuple

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor


def calculate_vif(X: pd.DataFrame) -> pd.DataFrame:
    """Variance Inflation Factor for each column in X.

    Returns a DataFrame with columns ['Variable', 'VIF'].
    """
    if X.shape[1] < 2:
        return pd.DataFrame({"Variable": list(X.columns), "VIF": [1.0] * X.shape[1]})

    Xc = sm.add_constant(X)
    rows = []
    for i, col in enumerate(Xc.columns):
        if col == "const":
            continue
        try:
            vif = variance_inflation_factor(Xc.values, i)
        except Exception:
            vif = np.inf
        rows.append({"Variable": col, "VIF": round(float(vif), 3)})
    return pd.DataFrame(rows)


def fit_ols(X: pd.DataFrame, y: pd.Series):
    """Fit an OLS model with an intercept added."""
    return sm.OLS(y, sm.add_constant(X, has_constant="add")).fit()


def get_model_metrics(model) -> Dict[str, float]:
    """Extract a small set of standard metrics from a fitted OLS result."""
    return {
        "r2": float(model.rsquared),
        "adj_r2": float(model.rsquared_adj),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "f_statistic": float(model.fvalue) if model.fvalue is not None else np.nan,
        "f_pvalue": float(model.f_pvalue) if model.f_pvalue is not None else np.nan,
        "n_obs": int(model.nobs),
    }


def check_vif_threshold(X: pd.DataFrame, threshold: float = 5.0) -> Tuple[bool, pd.DataFrame]:
    """Check whether all VIF values are below the given threshold."""
    if X.shape[1] == 0:
        return True, pd.DataFrame()
    vif_df = calculate_vif(X)
    return bool((vif_df["VIF"] < threshold).all()), vif_df


def get_highest_vif_variable(X: pd.DataFrame) -> Tuple[str, float]:
    """Return (variable_name, vif_value) for the variable with the highest VIF."""
    vif_df = calculate_vif(X)
    idx = vif_df["VIF"].idxmax()
    return str(vif_df.loc[idx, "Variable"]), float(vif_df.loc[idx, "VIF"])
