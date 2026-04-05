"""
VIF (Variance Inflation Factor) Calculation Utilities

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module provides functions for calculating VIF to detect multicollinearity.
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from typing import Tuple


def calculate_vif(X: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate Variance Inflation Factor for all features in X.
    
    VIF = 1 / (1 - R²) where R² is from regressing each feature against all others.
    
    Parameters
    ----------
    X : pd.DataFrame
        DataFrame containing only the predictor variables (no intercept)
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['feature', 'VIF']
    """
    if X.shape[1] < 2:
        return pd.DataFrame({'feature': X.columns, 'VIF': [1.0] * X.shape[1]})
    
    vif_data = pd.DataFrame()
    vif_data['feature'] = X.columns
    
    vif_values = []
    for i in range(X.shape[1]):
        try:
            vif = variance_inflation_factor(X.values, i)
            vif_values.append(vif)
        except (np.linalg.LinAlgError, ValueError):
            vif_values.append(np.inf)
    
    vif_data['VIF'] = vif_values
    return vif_data


def calculate_vif_manual(X: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate VIF manually using the R² method.
    
    For each feature Xi, regress it against all other features and compute:
    VIF_i = 1 / (1 - R²_i)
    
    Parameters
    ----------
    X : pd.DataFrame
        DataFrame containing predictor variables
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns ['feature', 'VIF', 'R2']
    """
    if X.shape[1] < 2:
        return pd.DataFrame({'feature': X.columns, 'VIF': [1.0], 'R2': [0.0]})
    
    vif_list = []
    columns = X.columns.tolist()
    
    for col in columns:
        other_cols = [c for c in columns if c != col]
        y_temp = X[col].values
        X_temp = sm.add_constant(X[other_cols].values)
        
        try:
            model = sm.OLS(y_temp, X_temp).fit()
            r2 = model.rsquared
            vif = 1.0 / (1.0 - r2) if r2 < 1.0 else np.inf
        except (np.linalg.LinAlgError, ValueError):
            r2 = np.nan
            vif = np.inf
        
        vif_list.append({'feature': col, 'VIF': vif, 'R2': r2})
    
    return pd.DataFrame(vif_list)


def check_vif_threshold(X: pd.DataFrame, threshold: float = 5.0) -> Tuple[bool, pd.DataFrame]:
    """
    Check if all VIF values are below the threshold.
    
    Parameters
    ----------
    X : pd.DataFrame
        Predictor variables currently in the model
    threshold : float
        Maximum acceptable VIF value
    
    Returns
    -------
    Tuple[bool, pd.DataFrame]
        (all_below_threshold, vif_dataframe)
    """
    if X.shape[1] == 0:
        return True, pd.DataFrame()
    
    vif_df = calculate_vif(X)
    all_below = (vif_df['VIF'] < threshold).all()
    return all_below, vif_df


def get_highest_vif_variable(X: pd.DataFrame) -> Tuple[str, float]:
    """
    Find the variable with the highest VIF.
    
    Parameters
    ----------
    X : pd.DataFrame
        Predictor variables
    
    Returns
    -------
    Tuple[str, float]
        (variable_name, vif_value)
    """
    vif_df = calculate_vif(X)
    idx = vif_df['VIF'].idxmax()
    return vif_df.loc[idx, 'feature'], vif_df.loc[idx, 'VIF']
