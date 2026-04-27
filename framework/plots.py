"""
Matplotlib plotting helpers for stepwise regression results.

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
"""

from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

# Best-effort plot style
for _style in ("seaborn-v0_8-whitegrid", "seaborn-whitegrid", "ggplot", "default"):
    try:
        plt.style.use(_style)
        break
    except Exception:
        continue


def plot_iteration_history(model, figsize=(12, 5)):
    """Plot R^2 across steps and # variables in model per step.

    Parameters
    ----------
    model : StepwiseVIFRegression
        A fitted StepwiseVIFRegression instance.
    """
    h = model.get_iteration_history()
    if h.empty:
        print("No iteration history to plot.")
        return
    fig, axes = plt.subplots(1, 2, figsize=figsize)

    axes[0].plot(h["step"], h["r2"], "b-o", linewidth=2, markersize=6)
    axes[0].set_xlabel("Step")
    axes[0].set_ylabel("R^2")
    axes[0].set_title("R^2 across selection steps")
    axes[0].grid(alpha=0.3)

    colors = {"ADD": "green", "REMOVE_P": "red", "REMOVE_VIF": "orange"}
    bar_colors = [colors.get(a, "gray") for a in h["action"]]
    axes[1].bar(h["step"], h["n_variables"], color=bar_colors, alpha=0.75)
    axes[1].set_xlabel("Step")
    axes[1].set_ylabel("# variables in model")
    axes[1].set_title("Variables in model (green=ADD, red=REMOVE_P, orange=REMOVE_VIF)")
    axes[1].grid(alpha=0.3, axis="y")
    plt.tight_layout()
    return fig


def plot_vif(model, figsize=(10, 6)):
    """Horizontal bar chart of final VIF values vs threshold."""
    if model.vif_final_ is None or model.vif_final_.empty:
        print("No VIF to plot.")
        return
    df = model.vif_final_.sort_values("VIF")
    fig, ax = plt.subplots(figsize=figsize)
    cols = ["green" if v < model.vif_threshold else "red" for v in df["VIF"]]
    ax.barh(df["Variable"], df["VIF"], color=cols, alpha=0.75)
    ax.axvline(model.vif_threshold, color="red", linestyle="--",
               label=f"VIF threshold = {model.vif_threshold}")
    ax.axvline(1, color="gray", linestyle=":", label="VIF = 1")
    ax.set_xlabel("VIF")
    ax.set_title("VIF for selected features")
    ax.legend()
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    return fig


def plot_coefficients(model, figsize=(10, 6)):
    """Coefficient bar chart with 95% CIs."""
    if model.model_ is None:
        print("No model fitted.")
        return
    coefs = model.model_.params.drop("const", errors="ignore")
    ci = model.model_.conf_int().drop("const", errors="ignore")
    fig, ax = plt.subplots(figsize=figsize)
    errors = [(coefs.values - ci[0].values), (ci[1].values - coefs.values)]
    cols = ["blue" if c > 0 else "red" for c in coefs.values]
    ax.barh(range(len(coefs)), coefs.values, xerr=errors,
            color=cols, alpha=0.75, capsize=4)
    ax.axvline(0, color="black", linewidth=1)
    ax.set_yticks(range(len(coefs)))
    ax.set_yticklabels(coefs.index)
    ax.set_xlabel("Coefficient")
    ax.set_title("Coefficients with 95% CI")
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    return fig


def plot_component(analyzer, component: str, figsize=(12, 8)):
    """Std_Beta + Sig_p bars for one VPC component (uses analyzer.detailed_results_)."""
    if analyzer.detailed_results_ is None:
        raise ValueError("Run analysis first.")
    d = analyzer.detailed_results_
    d = d[d["Component"] == component]
    if d.empty:
        print(f"No selected variables for {component}.")
        return
    fig, axes = plt.subplots(2, 1, figsize=figsize)
    cols = ["blue" if v > 0 else "red" for v in d["Std_Beta"]]
    axes[0].barh(d["Material"], d["Std_Beta"], color=cols, alpha=0.75)
    axes[0].axvline(0, color="black", linewidth=0.5)
    axes[0].set_xlabel("Std_Beta")
    axes[0].set_title(f"{component} - Standardized Coefficients")
    axes[0].grid(alpha=0.3, axis="x")

    axes[1].barh(d["Material"], d["Sig_p"], color="green", alpha=0.75)
    axes[1].axvline(analyzer.p_enter, color="red", linestyle="--",
                    label=f"p_enter={analyzer.p_enter}")
    axes[1].set_xlabel("Sig_p (entry p-value)")
    axes[1].set_title(f"{component} - Entry p-values")
    axes[1].legend()
    axes[1].grid(alpha=0.3, axis="x")
    plt.tight_layout()
    return fig


def plot_all_components(analyzer, figsize=(14, 6)):
    """R^2 and N_Materials per component side-by-side."""
    if analyzer.summary_results_ is None:
        raise ValueError("Run analysis first.")
    s = analyzer.summary_results_
    fig, axes = plt.subplots(1, 2, figsize=figsize)
    axes[0].bar(s["Component"], s["R_squared"], color="steelblue", alpha=0.85)
    axes[0].set_ylabel("R^2")
    axes[0].set_title("R^2 per component")
    axes[0].grid(alpha=0.3, axis="y")
    axes[0].tick_params(axis="x", rotation=30)

    axes[1].bar(s["Component"], s["N_Materials"], color="darkorange", alpha=0.85)
    axes[1].set_ylabel("# materials selected")
    axes[1].set_title("Selected materials per component")
    axes[1].grid(alpha=0.3, axis="y")
    axes[1].tick_params(axis="x", rotation=30)
    plt.tight_layout()
    return fig


def plot_actual_vs_predicted(model, X, y, figsize=(8, 8)):
    """Scatter of actual vs predicted with 1:1 line."""
    if model.model_ is None:
        print("No model fitted.")
        return
    y_pred = model.predict(X)
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(y, y_pred, alpha=0.7)
    lo = float(min(np.min(y), np.min(y_pred)))
    hi = float(max(np.max(y), np.max(y_pred)))
    ax.plot([lo, hi], [lo, hi], "r--", label="1:1")
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.set_title("Actual vs Predicted")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    return fig
