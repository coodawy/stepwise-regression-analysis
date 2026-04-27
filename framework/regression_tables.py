"""
SPSS-style incremental regression tables (Model Summary, ANOVA, Coefficients).

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
"""

from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import f as f_dist

from .vif_utils import calculate_vif, fit_ols
from .stepwise_vif import IterationLog


def build_regression_tables(
    vpc_name: str,
    y: pd.Series,
    X: pd.DataFrame,
    selected: List[str],
    history: List[IterationLog],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Build SPSS-style Model Summary, ANOVA, and Coefficients tables.

    Each model adds one more variable, in the order the variables entered
    (extracted from the iteration history).
    """
    n = len(y)
    zero_order = {col: round(float(y.corr(X[col])), 4) for col in selected}

    # Order = order in which variables were ADDed
    add_order = [h.variable for h in history if h.action == "ADD"]
    seen = set()
    sel_ordered: List[str] = []
    for v in add_order:
        if v in selected and v not in seen:
            sel_ordered.append(v)
            seen.add(v)
    # Append any selected vars that didn't show up in history (defensive)
    for v in selected:
        if v not in seen:
            sel_ordered.append(v)

    summary_rows, anova_rows, coef_rows = [], [], []
    prev_r2 = 0.0

    for i, _ in enumerate(sel_ordered):
        vars_in = sel_ordered[: i + 1]
        k = len(vars_in)
        m = fit_ols(X[vars_in], y)
        r2 = float(m.rsquared)
        r2chg = r2 - prev_r2
        df1, df2 = 1, n - k - 1
        if df2 > 0 and (1 - r2) > 0:
            f_chg = (r2chg / df1) / ((1 - r2) / df2)
            sig_f = round(float(f_dist.sf(f_chg, df1, df2)), 4)
        else:
            f_chg, sig_f = None, None

        summary_rows.append({
            "Dependent": vpc_name,
            "Model": i + 1,
            "R": round(float(np.sqrt(r2)), 4),
            "R Square": round(r2, 4),
            "Adj R Square": round(float(m.rsquared_adj), 4),
            "Std Error": round(float(np.sqrt(m.mse_resid)), 4),
            "R Sq Change": round(r2chg, 4),
            "F Change": round(f_chg, 3) if f_chg is not None else None,
            "df1": df1,
            "df2": df2,
            "Sig F Change": sig_f,
        })

        ms_reg = float(m.ess) / k
        ms_res = float(m.ssr) / (n - k - 1) if (n - k - 1) > 0 else np.nan
        anova_rows += [
            {"Model": i + 1, "Dependent": vpc_name, "Source": "Regression",
             "Sum of Squares": round(float(m.ess), 4), "df": k,
             "Mean Square": round(ms_reg, 4),
             "F": round(float(m.fvalue), 3), "Sig": round(float(m.f_pvalue), 4)},
            {"Model": i + 1, "Dependent": vpc_name, "Source": "Residual",
             "Sum of Squares": round(float(m.ssr), 4), "df": n - k - 1,
             "Mean Square": round(ms_res, 4), "F": None, "Sig": None},
            {"Model": i + 1, "Dependent": vpc_name, "Source": "Total",
             "Sum of Squares": round(float(m.centered_tss), 4), "df": n - 1,
             "Mean Square": None, "F": None, "Sig": None},
        ]

        vif_map = {
            r["Variable"]: r["VIF"]
            for _, r in (
                calculate_vif(X[vars_in])
                if k > 1
                else pd.DataFrame([{"Variable": vars_in[0], "VIF": 1.0}])
            ).iterrows()
        }

        for var in vars_in:
            coef_rows.append({
                "Dependent": vpc_name,
                "Model": i + 1,
                "Variable": var,
                "Std Beta": round(float(m.params[var]), 4),
                "Std Error": round(float(m.bse[var]), 4),
                "t": round(float(m.tvalues[var]), 3),
                "Sig": round(float(m.pvalues[var]), 4),
                "Zero-order r": zero_order.get(var),
                "VIF": round(float(vif_map.get(var, 1.0)), 3),
            })

        prev_r2 = r2

    return (
        pd.DataFrame(summary_rows),
        pd.DataFrame(anova_rows),
        pd.DataFrame(coef_rows),
    )
