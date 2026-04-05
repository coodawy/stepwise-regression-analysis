"""
Stepwise Regression with VIF Module

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

A comprehensive stepwise regression implementation with joint P-value 
and VIF (Variance Inflation Factor) stopping criterion.

Key Features:
- Joint stopping criterion: p-value AND VIF thresholds
- Default VIF threshold of 2.0 (optimal for principal components)
- R² change tracking for overfitting detection
- Z-score standardization for component loadings

Usage:
    from stepwise import StepwiseVIFRegression, standardize_to_zscore
    
    # Standardize VPCA loadings before regression
    z_loadings = standardize_to_zscore(loadings, axis=1)
    
    # Run stepwise regression (default VIF=2.0)
    model = StepwiseVIFRegression(method='bidirectional')
    model.fit(X, y)
    print(model.summary())
"""

from .stepwise_vif import StepwiseVIFRegression, IterationLog
from .vif_utils import calculate_vif, calculate_vif_manual, check_vif_threshold
from .plots import (plot_selection_history, plot_vif, plot_coefficients, 
                    plot_actual_vs_predicted)
from .preprocessing import (standardize_to_zscore, standardize_loadings_for_regression,
                            prepare_spectral_library, validate_band_alignment,
                            merge_loadings_with_library)
from .vpca_integration import (load_vpca_loadings, load_spectral_library,
                               align_to_sentinel2_bands, run_stepwise_identification,
                               create_identification_summary, print_identification_report,
                               VPCAResults, StepwiseResult)
from .sample_library import (create_sample_spectral_library, create_sample_vpca_loadings,
                             save_sample_data)

__all__ = [
    # Core regression
    'StepwiseVIFRegression',
    'IterationLog',
    # VIF utilities
    'calculate_vif',
    'calculate_vif_manual', 
    'check_vif_threshold',
    # Preprocessing
    'standardize_to_zscore',
    'standardize_loadings_for_regression',
    'prepare_spectral_library',
    'validate_band_alignment',
    'merge_loadings_with_library',
    # VPCA Integration
    'load_vpca_loadings',
    'load_spectral_library',
    'align_to_sentinel2_bands',
    'run_stepwise_identification',
    'create_identification_summary',
    'print_identification_report',
    'VPCAResults',
    'StepwiseResult',
    # Sample data for testing
    'create_sample_spectral_library',
    'create_sample_vpca_loadings',
    'save_sample_data',
    # Plotting
    'plot_selection_history',
    'plot_vif',
    'plot_coefficients',
    'plot_actual_vs_predicted'
]

__version__ = '1.1.0'
__author__ = 'Abdulrahman Hussein'
