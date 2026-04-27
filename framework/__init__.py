"""
Stepwise Regression Analysis Framework

A bidirectional stepwise regression framework with joint p-value and VIF
stopping criteria, designed for VPCA loadings vs. spectral library analysis.

Author:      Abdulrahman Hussein
Supervisor:  Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences
License:     MIT

Quick start
-----------
    from framework import VPCAStepwiseAnalysis

    analyzer = VPCAStepwiseAnalysis(p_enter=0.05, p_remove=0.10, vif_threshold=2.0)
    analyzer.load_data("loadings.csv", "library.csv")
    summary, detailed = analyzer.run_analysis()
    analyzer.export_results("output/")
"""

from .vif_utils import (
    calculate_vif,
    fit_ols,
    get_model_metrics,
    check_vif_threshold,
    get_highest_vif_variable,
)
from .stepwise_vif import StepwiseVIFRegression, IterationLog
from .regression_tables import build_regression_tables
from .vpca_integration import VPCAStepwiseAnalysis, run_vpca_stepwise
from .plots import (
    plot_iteration_history,
    plot_vif,
    plot_coefficients,
    plot_component,
    plot_all_components,
    plot_actual_vs_predicted,
)

__all__ = [
    # Core class
    "StepwiseVIFRegression",
    "IterationLog",
    # VPCA workflow
    "VPCAStepwiseAnalysis",
    "run_vpca_stepwise",
    # SPSS tables
    "build_regression_tables",
    # VIF utilities
    "calculate_vif",
    "fit_ols",
    "get_model_metrics",
    "check_vif_threshold",
    "get_highest_vif_variable",
    # Plotting
    "plot_iteration_history",
    "plot_vif",
    "plot_coefficients",
    "plot_component",
    "plot_all_components",
    "plot_actual_vs_predicted",
]

__version__ = "1.2.0"
__author__ = "Abdulrahman Hussein"
