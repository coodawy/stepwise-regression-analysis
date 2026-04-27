"""
StepwiseVIFRegression: bidirectional stepwise regression with joint p-value
and VIF stopping criteria.

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import statsmodels.api as sm

from .vif_utils import calculate_vif, fit_ols


@dataclass
class IterationLog:
    """One row of the stepwise iteration history."""
    step: int
    action: str            # "ADD", "REMOVE_P", "REMOVE_VIF"
    variable: str
    p_value: Optional[float]
    vif: Optional[float]
    r2: float
    n_variables: int
    variables: str         # comma-joined list

    def to_dict(self) -> Dict:
        return {
            "step": self.step,
            "action": self.action,
            "variable": self.variable,
            "p_value": self.p_value,
            "vif": self.vif,
            "r2": self.r2,
            "n_variables": self.n_variables,
            "variables": self.variables,
        }


class StepwiseVIFRegression:
    """Bidirectional stepwise regression with joint p-value and VIF stopping criteria.

    Parameters
    ----------
    p_enter : float, default 0.05
        Maximum p-value for ADDING a variable.
    p_remove : float, default 0.10
        Minimum p-value to REMOVE an already-selected variable.
    vif_threshold : float, default 2.0
        Maximum acceptable VIF for any selected variable.
    max_iter : int, default 100
        Hard cap on number of bidirectional iterations.
    verbose : int, default 1
        0 = silent, 1 = step-by-step, 2 = detailed.
    """

    def __init__(self, p_enter: float = 0.05, p_remove: float = 0.10,
                 vif_threshold: float = 2.0, max_iter: int = 100, verbose: int = 1):
        if not (0 < p_enter < 1):
            raise ValueError("p_enter must be in (0, 1)")
        if not (0 < p_remove < 1):
            raise ValueError("p_remove must be in (0, 1)")
        if p_remove < p_enter:
            warnings.warn(
                "p_remove < p_enter is unusual: variables may be removed immediately after entering."
            )
        if vif_threshold <= 1:
            raise ValueError("vif_threshold must be > 1")

        self.p_enter = p_enter
        self.p_remove = p_remove
        self.vif_threshold = vif_threshold
        self.max_iter = max_iter
        self.verbose = verbose

        self.selected_features_: List[str] = []
        self.model_ = None
        self.iteration_history_: List[IterationLog] = []
        self.vif_final_: Optional[pd.DataFrame] = None
        self.feature_names_: List[str] = []
        self.entry_pvalues_: Dict[str, float] = {}
        self.standardized_coefs_: Dict[str, float] = {}
        self._is_fitted = False

    # --- internal helpers ---
    def _print(self, msg, level=1):
        if self.verbose >= level:
            print(msg)

    def _validate(self, X: pd.DataFrame, y: pd.Series):
        if not isinstance(X, pd.DataFrame):
            raise ValueError("X must be a pandas DataFrame")
        if len(X) != len(y):
            raise ValueError("X and y must have the same number of rows")
        if X.isnull().any().any():
            raise ValueError("X contains NaN values")
        if pd.Series(y).isnull().any():
            raise ValueError("y contains NaN values")
        if X.shape[1] > X.shape[0]:
            warnings.warn(
                f"n_features ({X.shape[1]}) > n_samples ({X.shape[0]}). "
                "Stepwise regression with high-dim data is well-defined but be cautious about overfitting."
            )

    def _log(self, step, action, var, p, vif, current):
        if current:
            r2 = float(fit_ols(self.X_[current], self.y_).rsquared)
        else:
            r2 = 0.0
        self.iteration_history_.append(IterationLog(
            step=step, action=action, variable=var,
            p_value=(round(float(p), 4) if p is not None else None),
            vif=(round(float(vif), 3) if vif is not None else None),
            r2=round(r2, 4),
            n_variables=len(current),
            variables=", ".join(current),
        ))

    # --- public API ---
    def fit(self, X: pd.DataFrame, y: pd.Series) -> "StepwiseVIFRegression":
        self._validate(X, y)
        self.X_ = X
        self.y_ = y
        self.feature_names_ = list(X.columns)

        selected: List[str] = []
        remaining: List[str] = list(X.columns)
        self.iteration_history_ = []
        self.entry_pvalues_ = {}
        self.standardized_coefs_ = {}
        step = 0

        self._print(
            f"Bidirectional Stepwise | p_enter<{self.p_enter} | "
            f"p_remove>{self.p_remove} | VIF<{self.vif_threshold}"
        )

        for _ in range(self.max_iter):
            changed = False

            # ---- FORWARD: best p-value among remaining ----
            best_p, best_var, best_r2 = 1.0, None, 0.0
            for var in remaining:
                try:
                    m = fit_ols(X[selected + [var]], y)
                    p = float(m.pvalues[var])
                    if p < best_p:
                        best_p, best_var, best_r2 = p, var, float(m.rsquared)
                except Exception:
                    continue

            if best_var is not None and best_p < self.p_enter:
                test = selected + [best_var]
                vif_ok = True
                max_vif = 1.0
                if len(test) > 1:
                    vifs = calculate_vif(X[test])["VIF"]
                    max_vif = float(vifs.max())
                    vif_ok = max_vif <= self.vif_threshold

                if vif_ok:
                    step += 1
                    selected.append(best_var)
                    remaining.remove(best_var)
                    self.entry_pvalues_[best_var] = best_p
                    changed = True
                    self._log(step, "ADD", best_var, best_p, max_vif, selected)
                    self._print(
                        f"Step {step}: + ADD    {best_var:<35} | "
                        f"p={best_p:.4f} | R2={best_r2:.4f} | VIF={max_vif:.2f}"
                    )
                else:
                    # Permanently drop this candidate (matches v3 behaviour)
                    remaining.remove(best_var)
                    self._print(
                        f"  SKIP   {best_var:<35} | p={best_p:.4f} but "
                        f"VIF={max_vif:.2f} > {self.vif_threshold}",
                        level=2,
                    )

            # ---- BACKWARD by p-value ----
            if selected:
                m = fit_ols(X[selected], y)
                pvals = m.pvalues.drop("const", errors="ignore")
                if len(pvals) > 0:
                    worst_var = pvals.idxmax()
                    worst_p = float(pvals.max())
                    if worst_p > self.p_remove:
                        step += 1
                        selected.remove(worst_var)
                        remaining.append(worst_var)
                        self.entry_pvalues_.pop(worst_var, None)
                        changed = True
                        self._log(step, "REMOVE_P", worst_var, worst_p, None, selected)
                        self._print(
                            f"Step {step}: - REMOVE {worst_var:<35} | "
                            f"p={worst_p:.4f} > {self.p_remove}"
                        )

            # ---- BACKWARD by VIF ----
            if len(selected) > 1:
                vif_df = calculate_vif(X[selected])
                worst = vif_df.loc[vif_df["VIF"].idxmax()]
                if float(worst["VIF"]) > self.vif_threshold:
                    step += 1
                    var = worst["Variable"]
                    selected.remove(var)
                    remaining.append(var)
                    self.entry_pvalues_.pop(var, None)
                    changed = True
                    self._log(step, "REMOVE_VIF", var, None, float(worst["VIF"]), selected)
                    self._print(
                        f"Step {step}: - REMOVE {var:<35} | "
                        f"VIF={float(worst['VIF']):.2f} > {self.vif_threshold}"
                    )

            if not changed:
                self._print("Converged.")
                break

        self.selected_features_ = selected
        if selected:
            self.model_ = fit_ols(X[selected], y)
            self.vif_final_ = (
                calculate_vif(X[selected])
                if len(selected) > 1
                else pd.DataFrame([{"Variable": selected[0], "VIF": 1.0}])
            )
            self.standardized_coefs_ = {
                v: float(self.model_.params[v])
                for v in selected
                if v in self.model_.params.index
            }
        else:
            self.model_ = None
            self.vif_final_ = pd.DataFrame()
        self._is_fitted = True

        self._print(f"\nFinal: {len(selected)} variable(s) selected.")
        if selected:
            self._print(
                f"  R2={self.model_.rsquared:.4f} | "
                f"Adj R2={self.model_.rsquared_adj:.4f}"
            )
        return self

    # --- prediction & scoring ---
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        if self.model_ is None:
            raise ValueError("No features were selected; cannot predict.")
        Xs = sm.add_constant(X[self.selected_features_], has_constant="add")
        return self.model_.predict(Xs)

    def score(self, X: pd.DataFrame, y: pd.Series) -> float:
        """R^2 on (X, y)."""
        self._check_fitted()
        if self.model_ is None:
            return 0.0
        y_pred = self.predict(X)
        ss_res = float(np.sum((y - y_pred) ** 2))
        ss_tot = float(np.sum((y - np.mean(y)) ** 2))
        return 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0

    # --- accessors ---
    def get_iteration_history(self) -> pd.DataFrame:
        return pd.DataFrame([log.to_dict() for log in self.iteration_history_])

    def get_vif(self) -> pd.DataFrame:
        self._check_fitted()
        return self.vif_final_.copy() if self.vif_final_ is not None else pd.DataFrame()

    def get_entry_pvalues(self) -> pd.Series:
        self._check_fitted()
        return pd.Series(self.entry_pvalues_)

    def get_standardized_coefs(self) -> pd.Series:
        self._check_fitted()
        return pd.Series(self.standardized_coefs_)

    def _check_fitted(self):
        if not self._is_fitted:
            raise ValueError("Model has not been fitted. Call .fit() first.")

    # --- text summary ---
    def summary(self) -> str:
        self._check_fitted()
        if self.model_ is None:
            return "No features were selected."
        m = self.model_
        out = []
        out.append("=" * 78)
        out.append("STEPWISE REGRESSION (BIDIRECTIONAL)  -  MODEL SUMMARY")
        out.append("=" * 78)
        out.append(
            f"p_enter={self.p_enter}  p_remove={self.p_remove}  "
            f"vif_threshold={self.vif_threshold}"
        )
        out.append("")
        out.append(f"Selected features ({len(self.selected_features_)}):")
        for f in self.selected_features_:
            out.append(f"  - {f}")
        out.append("")
        out.append("-" * 78)
        out.append(f"R-squared        : {m.rsquared:.6f}")
        out.append(f"Adj R-squared    : {m.rsquared_adj:.6f}")
        out.append(f"AIC              : {m.aic:.2f}")
        out.append(f"BIC              : {m.bic:.2f}")
        out.append(f"F-statistic      : {m.fvalue:.4f}")
        out.append(f"F p-value        : {m.f_pvalue:.4e}")
        out.append(f"Observations     : {int(m.nobs)}")
        out.append("-" * 78)
        out.append(
            f"{'Variable':<28} {'Coef':>10} {'StdErr':>10} {'t':>8} "
            f"{'P>|t|':>10} {'VIF':>8} {'EntryP':>10}"
        )
        out.append("-" * 78)
        for v in ["const"] + self.selected_features_:
            if v not in m.params.index:
                continue
            coef = float(m.params[v])
            se = float(m.bse[v])
            t = float(m.tvalues[v])
            p = float(m.pvalues[v])
            if v == "const":
                vif_str, ep_str = "N/A", "N/A"
            else:
                vif_row = self.vif_final_[self.vif_final_["Variable"] == v]
                vif_str = (
                    f"{float(vif_row['VIF'].values[0]):.2f}"
                    if not vif_row.empty else "N/A"
                )
                ep_str = (
                    f"{self.entry_pvalues_.get(v, float('nan')):.4f}"
                    if v in self.entry_pvalues_ else "N/A"
                )
            out.append(
                f"{v:<28} {coef:>10.4f} {se:>10.4f} {t:>8.3f} "
                f"{p:>10.4f} {vif_str:>8} {ep_str:>10}"
            )
        out.append("=" * 78)
        return "\n".join(out)
