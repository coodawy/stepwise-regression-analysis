"""
Stepwise Regression with Joint VIF and P-Value Stopping Criterion

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module implements stepwise regression with a joint stopping criterion
based on both statistical significance (p-values) and multicollinearity (VIF).
"""

import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

from .vif_utils import check_vif_threshold, get_highest_vif_variable
from .plots import plot_selection_history, plot_vif, plot_coefficients


@dataclass
class IterationLog:
    """Data class to store information about each iteration of stepwise selection."""
    step: int
    action: str
    variable: str
    p_value: float
    vif: float
    r2: float
    adj_r2: float
    aic: float
    bic: float
    r2_change: float  # Track R² change from previous step
    max_vif: float    # Track maximum VIF in model at this step
    variables_in_model: List[str]
    
    def to_dict(self) -> Dict:
        return {
            'step': self.step, 'action': self.action, 'variable': self.variable,
            'p_value': self.p_value, 'vif': self.vif, 'r2': self.r2,
            'adj_r2': self.adj_r2, 'aic': self.aic, 'bic': self.bic,
            'r2_change': self.r2_change, 'max_vif': self.max_vif,
            'n_variables': len(self.variables_in_model),
            'variables': ', '.join(self.variables_in_model)
        }


def fit_ols_model(X: pd.DataFrame, y: pd.Series, add_const: bool = True):
    """Fit an OLS model and return the results."""
    X_fit = sm.add_constant(X, has_constant='add') if add_const else X
    return sm.OLS(y, X_fit).fit()


def get_model_metrics(model) -> Dict:
    """Extract key metrics from a fitted OLS model."""
    return {
        'r2': model.rsquared, 'adj_r2': model.rsquared_adj,
        'aic': model.aic, 'bic': model.bic,
        'f_statistic': model.fvalue, 'f_pvalue': model.f_pvalue,
        'n_obs': int(model.nobs), 'df_model': int(model.df_model),
        'df_resid': int(model.df_resid)
    }


class StepwiseVIFRegression:
    """
    Stepwise Regression with Joint VIF and P-Value Stopping Criterion.
    
    Based on methodology from Dr. Joseph D. Ortiz, Kent State University.
    Uses dual stopping criteria: p-value significance AND variance inflation factor.
    
    Parameters
    ----------
    method : str, default='bidirectional'
        Selection method: 'forward', 'backward', or 'bidirectional'
    p_enter : float, default=0.05
        P-value threshold for adding a variable (5% significance level)
    p_remove : float, default=0.10
        P-value threshold for removing a variable (10% level)
    vif_threshold : float, default=2.0
        Maximum acceptable VIF value. Default is 2.0 (recommended for principal
        components which are already partitioned). Traditional threshold is 5.0.
    r2_change_threshold : float, default=None
        Optional minimum R² change to continue adding variables. If a variable
        adds less than this threshold to R², selection stops. Set to None to disable.
    criteria : str, default='pvalue'
        Selection criteria: 'pvalue', 'aic', 'bic', or 'adjr2'
    max_iter : int, default=100
        Maximum number of iterations
    verbose : int, default=1
        Verbosity level: 0=silent, 1=progress, 2=detailed
    tolerance : float, default=0.001
        Convergence tolerance for numerical stability
    
    Notes
    -----
    The joint stopping criterion ensures:
    1. All coefficients have p-value < p_enter (statistically significant)
    2. All VIF values < vif_threshold (no multicollinearity)
    3. Optionally, R² change > r2_change_threshold (meaningful contribution)
    
    A VIF of 2 means the variance is doubled due to collinearity. For principal
    components that have been orthogonalized, a lower threshold is appropriate.
    """
    
    def __init__(self, method: str = 'bidirectional', p_enter: float = 0.05,
                 p_remove: float = 0.10, vif_threshold: float = 2.0,
                 r2_change_threshold: Optional[float] = None,
                 criteria: str = 'pvalue', max_iter: int = 100, verbose: int = 1,
                 tolerance: float = 0.001):
        self.method = method.lower()
        self.p_enter = p_enter
        self.p_remove = p_remove
        self.vif_threshold = vif_threshold
        self.r2_change_threshold = r2_change_threshold
        self.criteria = criteria.lower()
        self.max_iter = max_iter
        self.verbose = verbose
        self.tolerance = tolerance
        
        self.selected_features_: List[str] = []
        self.model_ = None
        self.iteration_history_: List[IterationLog] = []
        self.vif_final_: Optional[pd.DataFrame] = None
        self.feature_names_: List[str] = []
        self._is_fitted = False
        self._prev_r2 = 0.0  # Track previous R² for change calculation
    
    def _print(self, message: str, level: int = 1):
        if self.verbose >= level:
            print(message)
    
    def _validate_inputs(self, X: pd.DataFrame, y: pd.Series):
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame")
        if len(X) != len(y):
            raise ValueError("X and y must have the same number of samples")
        if X.isnull().any().any() or pd.Series(y).isnull().any():
            raise ValueError("Data contains missing values")
    
    def _get_candidate_pvalues(self, X: pd.DataFrame, y: pd.Series,
                               current: List[str], candidates: List[str]) -> pd.DataFrame:
        results = []
        for var in candidates:
            try:
                model = fit_ols_model(X[current + [var]], y)
                metrics = get_model_metrics(model)
                results.append({'feature': var, 'pvalue': model.pvalues[var],
                               'aic': metrics['aic'], 'bic': metrics['bic'],
                               'adj_r2': metrics['adj_r2']})
            except Exception:
                continue
        return pd.DataFrame(results)
    
    def _remove_high_vif(self, X: pd.DataFrame, y: pd.Series,
                         features: List[str], step: int) -> Tuple[List[str], int]:
        while len(features) > 1:
            vif_ok, _ = check_vif_threshold(X[features], self.vif_threshold)
            if vif_ok:
                break
            var, max_vif = get_highest_vif_variable(X[features])
            self._print(f"  VIF Removal: {var} (VIF={max_vif:.2f})", 1)
            features.remove(var)
            step += 1
            
            if features:
                model = fit_ols_model(X[features], y)
                metrics = get_model_metrics(model)
            else:
                metrics = {'r2': 0, 'adj_r2': 0, 'aic': np.inf, 'bic': np.inf}
            
            r2_change = metrics['r2'] - self._prev_r2
            self._prev_r2 = metrics['r2']
            _, vif_check = check_vif_threshold(X[features], self.vif_threshold) if features else (True, pd.DataFrame())
            current_max_vif = vif_check['VIF'].max() if not vif_check.empty else 0.0
            
            self.iteration_history_.append(IterationLog(
                step=step, action='vif_remove', variable=var, p_value=np.nan,
                vif=max_vif, r2=metrics['r2'], adj_r2=metrics['adj_r2'],
                aic=metrics['aic'], bic=metrics['bic'], r2_change=r2_change,
                max_vif=current_max_vif, variables_in_model=features.copy()
            ))
        return features, step
    
    def _forward_step(self, X: pd.DataFrame, y: pd.Series, current: List[str],
                      remaining: List[str], step: int) -> Tuple[List[str], List[str], int, bool]:
        if not remaining:
            return current, remaining, step, False
        
        df = self._get_candidate_pvalues(X, y, current, remaining)
        if df.empty:
            return current, remaining, step, False
        
        # Select best based on criteria
        if self.criteria == 'pvalue':
            df = df.sort_values('pvalue')
            best = df.iloc[0]
            if best['pvalue'] >= self.p_enter:
                return current, remaining, step, False
        elif self.criteria == 'aic':
            best = df.sort_values('aic').iloc[0]
        elif self.criteria == 'bic':
            best = df.sort_values('bic').iloc[0]
        else:  # adjr2
            best = df.sort_values('adj_r2', ascending=False).iloc[0]
        
        # Check VIF before adding - with look-ahead recovery
        test = current + [best['feature']]
        if len(test) > 1:
            vif_ok, _ = check_vif_threshold(X[test], self.vif_threshold)
            if not vif_ok:
                # Look-ahead: try other candidates that pass VIF threshold
                self._print(f"  VIF too high with {best['feature']}, trying alternatives...", 2)
                found_alternative = False
                for _, row in df.iterrows():
                    if row['feature'] == best['feature']:
                        continue
                    if self.criteria == 'pvalue' and row['pvalue'] >= self.p_enter:
                        continue
                    alt_test = current + [row['feature']]
                    alt_vif_ok, _ = check_vif_threshold(X[alt_test], self.vif_threshold)
                    if alt_vif_ok:
                        best = row
                        found_alternative = True
                        self._print(f"  Found alternative: {best['feature']}", 2)
                        break
                
                if not found_alternative:
                    remaining.remove(best['feature'])
                    return current, remaining, step, False
        
        var = best['feature']
        current.append(var)
        remaining.remove(var)
        step += 1
        self._print(f"  + Added: {var} (p={best['pvalue']:.4f})", 1)
        
        model = fit_ols_model(X[current], y)
        metrics = get_model_metrics(model)
        _, vif_df = check_vif_threshold(X[current], self.vif_threshold)
        vif_val = vif_df[vif_df['feature'] == var]['VIF'].values[0] if not vif_df.empty else np.nan
        
        r2_change = metrics['r2'] - self._prev_r2
        self._prev_r2 = metrics['r2']
        max_vif_current = vif_df['VIF'].max() if not vif_df.empty else 1.0
        
        self._print(f"    R²={metrics['r2']:.4f}, ΔR²={r2_change:.4f}, max_VIF={max_vif_current:.2f}", 2)
        
        # Check R² change threshold if specified
        if self.r2_change_threshold is not None and r2_change < self.r2_change_threshold and len(current) > 1:
            self._print(f"  R² change ({r2_change:.4f}) below threshold ({self.r2_change_threshold}). Reverting.", 1)
            current.remove(var)
            remaining.append(var)
            self._prev_r2 = metrics['r2'] - r2_change  # Restore previous R²
            return current, remaining, step - 1, False
        
        self.iteration_history_.append(IterationLog(
            step=step, action='add', variable=var, p_value=best['pvalue'],
            vif=vif_val, r2=metrics['r2'], adj_r2=metrics['adj_r2'],
            aic=metrics['aic'], bic=metrics['bic'], r2_change=r2_change,
            max_vif=max_vif_current, variables_in_model=current.copy()
        ))
        return current, remaining, step, True
    
    def _backward_step(self, X: pd.DataFrame, y: pd.Series,
                       current: List[str], step: int) -> Tuple[List[str], int, bool]:
        if len(current) <= 1:
            return current, step, False
        
        model = fit_ols_model(X[current], y)
        pvals = model.pvalues.drop('const', errors='ignore')
        max_var, max_p = pvals.idxmax(), pvals.max()
        
        if max_p <= self.p_remove:
            return current, step, False
        
        current.remove(max_var)
        step += 1
        self._print(f"  - Removed: {max_var} (p={max_p:.4f})", 1)
        
        if current:
            model = fit_ols_model(X[current], y)
            metrics = get_model_metrics(model)
        else:
            metrics = {'r2': 0, 'adj_r2': 0, 'aic': np.inf, 'bic': np.inf}
        
        r2_change = metrics['r2'] - self._prev_r2
        self._prev_r2 = metrics['r2']
        _, vif_check = check_vif_threshold(X[current], self.vif_threshold) if current else (True, pd.DataFrame())
        max_vif_current = vif_check['VIF'].max() if not vif_check.empty else 0.0
        
        self.iteration_history_.append(IterationLog(
            step=step, action='remove', variable=max_var, p_value=max_p,
            vif=np.nan, r2=metrics['r2'], adj_r2=metrics['adj_r2'],
            aic=metrics['aic'], bic=metrics['bic'], r2_change=r2_change,
            max_vif=max_vif_current, variables_in_model=current.copy()
        ))
        return current, step, True
    
    def fit(self, X: pd.DataFrame, y: pd.Series) -> 'StepwiseVIFRegression':
        """Fit the stepwise regression model."""
        self._validate_inputs(X, y)
        self.feature_names_ = X.columns.tolist()
        self.iteration_history_ = []
        self._prev_r2 = 0.0  # Reset R² tracking for new fit
        
        if self.method == 'forward':
            self._fit_forward(X, y)
        elif self.method == 'backward':
            self._fit_backward(X, y)
        else:
            self._fit_bidirectional(X, y)
        
        if self.selected_features_:
            self.model_ = fit_ols_model(X[self.selected_features_], y)
            _, self.vif_final_ = check_vif_threshold(X[self.selected_features_], self.vif_threshold)
        
        self._is_fitted = True
        self._print(f"\nFinal features ({len(self.selected_features_)}): {self.selected_features_}", 1)
        return self
    
    def _fit_forward(self, X: pd.DataFrame, y: pd.Series):
        self._print(f"\n{'='*50}\nFORWARD SELECTION\np_enter={self.p_enter}, vif={self.vif_threshold}\n{'='*50}\n", 1)
        current, remaining, step = [], self.feature_names_.copy(), 0
        
        for i in range(self.max_iter):
            self._print(f"Iteration {i+1}:", 1)
            current, remaining, step, added = self._forward_step(X, y, current, remaining, step)
            if not added:
                self._print("  No variable added. Stopping.", 1)
                break
            current, step = self._remove_high_vif(X, y, current, step)
        
        self.selected_features_ = current
    
    def _fit_backward(self, X: pd.DataFrame, y: pd.Series):
        self._print(f"\n{'='*50}\nBACKWARD ELIMINATION\np_remove={self.p_remove}, vif={self.vif_threshold}\n{'='*50}\n", 1)
        current, step = self.feature_names_.copy(), 0
        
        self._print("Step 1: Removing high VIF variables...", 1)
        current, step = self._remove_high_vif(X, y, current, step)
        
        self._print("\nStep 2: Backward elimination...", 1)
        for i in range(self.max_iter):
            self._print(f"Iteration {i+1}:", 1)
            current, step, removed = self._backward_step(X, y, current, step)
            if not removed:
                self._print("  No variable removed. Stopping.", 1)
                break
            current, step = self._remove_high_vif(X, y, current, step)
        
        self.selected_features_ = current
    
    def _fit_bidirectional(self, X: pd.DataFrame, y: pd.Series):
        self._print(f"\n{'='*50}\nBIDIRECTIONAL STEPWISE\np_enter={self.p_enter}, p_remove={self.p_remove}, vif={self.vif_threshold}\n{'='*50}\n", 1)
        current, remaining, step, no_change = [], self.feature_names_.copy(), 0, 0
        
        for i in range(self.max_iter):
            self._print(f"Iteration {i+1}:", 1)
            before = current.copy()
            
            current, remaining, step, added = self._forward_step(X, y, current, remaining, step)
            if added:
                current, step = self._remove_high_vif(X, y, current, step)
            
            if len(current) > 1:
                current, step, removed = self._backward_step(X, y, current, step)
                if removed:
                    removed_var = [v for v in before if v not in current and v not in remaining]
                    remaining.extend(removed_var)
            
            if set(current) == set(before):
                no_change += 1
                if no_change >= 2:
                    self._print("  Converged.", 1)
                    break
            else:
                no_change = 0
        
        self.selected_features_ = current
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict using the fitted model."""
        if not self._is_fitted or self.model_ is None:
            raise ValueError("Model not fitted or no features selected.")
        X_sel = sm.add_constant(X[self.selected_features_], has_constant='add')
        return self.model_.predict(X_sel)
    
    def get_iteration_history(self) -> pd.DataFrame:
        """Get iteration history as DataFrame."""
        if not self.iteration_history_:
            return pd.DataFrame()
        return pd.DataFrame([log.to_dict() for log in self.iteration_history_])
    
    def get_vif(self) -> pd.DataFrame:
        """Get VIF values for selected features."""
        return self.vif_final_
    
    def summary(self) -> str:
        """Return model summary string."""
        if not self._is_fitted or self.model_ is None:
            return "Model not fitted or no features selected."
        
        m = get_model_metrics(self.model_)
        r2_thresh_str = f"R² change threshold: {self.r2_change_threshold}" if self.r2_change_threshold else "R² change threshold: None (disabled)"
        
        lines = [
            "=" * 70, "STEPWISE REGRESSION WITH VIF - MODEL SUMMARY", "=" * 70, "",
            f"Method: {self.method.upper()}", f"P-enter: {self.p_enter}  P-remove: {self.p_remove}",
            f"VIF threshold: {self.vif_threshold}", r2_thresh_str, "",
            f"Selected Features ({len(self.selected_features_)}):",
            *[f"  - {f}" for f in self.selected_features_], "",
            "-" * 70, "MODEL STATISTICS", "-" * 70,
            f"R-squared:          {m['r2']:.6f}", f"Adjusted R-squared: {m['adj_r2']:.6f}",
            f"AIC:                {m['aic']:.2f}", f"BIC:                {m['bic']:.2f}",
            f"F-statistic:        {m['f_statistic']:.4f}", f"F p-value:          {m['f_pvalue']:.2e}",
            f"Observations:       {m['n_obs']}", "",
            "-" * 70, "COEFFICIENTS", "-" * 70,
            f"{'Variable':<20} {'Coef':>12} {'Std Err':>12} {'t':>10} {'P>|t|':>12} {'VIF':>10}",
            "-" * 70
        ]
        
        for var in ['const'] + self.selected_features_:
            if var in self.model_.params.index:
                coef = self.model_.params[var]
                se = self.model_.bse[var]
                t = self.model_.tvalues[var]
                p = self.model_.pvalues[var]
                vif = "N/A" if var == 'const' else f"{self.vif_final_[self.vif_final_['feature']==var]['VIF'].values[0]:.2f}"
                lines.append(f"{var:<20} {coef:>12.4f} {se:>12.4f} {t:>10.3f} {p:>12.4f} {vif:>10}")
        
        lines.append("=" * 70)
        return "\n".join(lines)
    
    def selection_summary(self) -> str:
        """Return detailed selection history summary showing R² changes at each step."""
        if not self.iteration_history_:
            return "No selection history available."
        
        lines = [
            "=" * 80,
            "STEPWISE SELECTION HISTORY",
            "=" * 80,
            f"{'Step':<6} {'Action':<12} {'Variable':<20} {'R²':>8} {'ΔR²':>8} {'Max VIF':>8} {'P-value':>10}",
            "-" * 80
        ]
        
        for log in self.iteration_history_:
            r2_str = f"{log.r2:.4f}" if not np.isnan(log.r2) else "N/A"
            r2_chg = f"{log.r2_change:+.4f}" if not np.isnan(log.r2_change) else "N/A"
            max_vif = f"{log.max_vif:.2f}" if not np.isnan(log.max_vif) else "N/A"
            pval = f"{log.p_value:.4f}" if not np.isnan(log.p_value) else "N/A"
            lines.append(f"{log.step:<6} {log.action:<12} {log.variable:<20} {r2_str:>8} {r2_chg:>8} {max_vif:>8} {pval:>10}")
        
        lines.append("=" * 80)
        return "\n".join(lines)
    
    def plot_selection_history(self, figsize=(14, 10), save_path=None):
        """Plot selection history."""
        plot_selection_history(self.get_iteration_history(), figsize, save_path)
    
    def plot_vif(self, figsize=(10, 6), save_path=None):
        """Plot VIF values."""
        plot_vif(self.vif_final_, self.vif_threshold, figsize, save_path)
    
    def plot_coefficients(self, figsize=(10, 6), save_path=None):
        """Plot coefficients."""
        plot_coefficients(self.model_, figsize, save_path)
