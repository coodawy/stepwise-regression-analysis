"""
Stepwise Regression Visualization Functions

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module provides plotting functions for stepwise regression analysis.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings('ignore')

# Set plot style
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except OSError:
    try:
        plt.style.use('seaborn-whitegrid')
    except OSError:
        plt.style.use('default')


def plot_selection_history(history_df: pd.DataFrame, figsize: tuple = (14, 10), 
                           save_path: str = None):
    """
    Plot the selection history showing metrics over iterations.
    
    Parameters
    ----------
    history_df : pd.DataFrame
        DataFrame from get_iteration_history()
    figsize : tuple
        Figure size (width, height)
    save_path : str, optional
        Path to save the figure
    """
    if history_df.empty:
        print("No iteration history to plot.")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    
    # Plot 1: R-squared over steps
    ax1 = axes[0, 0]
    ax1.plot(history_df['step'], history_df['r2'], 'b-o', linewidth=2, markersize=6)
    ax1.set_xlabel('Step', fontsize=11)
    ax1.set_ylabel('R-squared', fontsize=11)
    ax1.set_title('R-squared Over Selection Steps', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Adjusted R-squared over steps
    ax2 = axes[0, 1]
    ax2.plot(history_df['step'], history_df['adj_r2'], 'g-o', linewidth=2, markersize=6)
    ax2.set_xlabel('Step', fontsize=11)
    ax2.set_ylabel('Adjusted R-squared', fontsize=11)
    ax2.set_title('Adjusted R-squared Over Selection Steps', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: AIC/BIC over steps
    ax3 = axes[1, 0]
    ax3.plot(history_df['step'], history_df['aic'], 'r-o', linewidth=2, markersize=6, label='AIC')
    ax3.plot(history_df['step'], history_df['bic'], 'm-s', linewidth=2, markersize=6, label='BIC')
    ax3.set_xlabel('Step', fontsize=11)
    ax3.set_ylabel('Information Criterion', fontsize=11)
    ax3.set_title('AIC and BIC Over Selection Steps', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Number of variables over steps
    ax4 = axes[1, 1]
    colors = ['green' if a == 'add' else 'red' if a == 'remove' else 'orange' 
              for a in history_df['action']]
    ax4.bar(history_df['step'], history_df['n_variables'], color=colors, alpha=0.7)
    ax4.set_xlabel('Step', fontsize=11)
    ax4.set_ylabel('Number of Variables', fontsize=11)
    ax4.set_title('Variables in Model (Green=Add, Red=Remove, Orange=VIF Remove)', 
                  fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.show()


def plot_vif(vif_df: pd.DataFrame, vif_threshold: float = 5.0, 
             figsize: tuple = (10, 6), save_path: str = None):
    """
    Plot VIF values for selected features.
    
    Parameters
    ----------
    vif_df : pd.DataFrame
        DataFrame with 'feature' and 'VIF' columns
    vif_threshold : float
        Threshold line to display
    figsize : tuple
        Figure size (width, height)
    save_path : str, optional
        Path to save the figure
    """
    if vif_df is None or vif_df.empty:
        print("No VIF data to plot.")
        return
    
    vif_sorted = vif_df.sort_values('VIF', ascending=True)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = ['green' if v < vif_threshold else 'red' for v in vif_sorted['VIF']]
    bars = ax.barh(vif_sorted['feature'], vif_sorted['VIF'], color=colors, alpha=0.7)
    
    ax.axvline(x=vif_threshold, color='red', linestyle='--', linewidth=2, 
               label=f'VIF Threshold = {vif_threshold}')
    ax.axvline(x=1, color='gray', linestyle=':', linewidth=1, label='VIF = 1 (No collinearity)')
    
    ax.set_xlabel('Variance Inflation Factor (VIF)', fontsize=11)
    ax.set_ylabel('Feature', fontsize=11)
    ax.set_title('VIF Values for Selected Features', fontsize=12, fontweight='bold')
    ax.legend(loc='lower right')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for bar, vif in zip(bars, vif_sorted['VIF']):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{vif:.2f}', va='center', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.show()


def plot_coefficients(model, figsize: tuple = (10, 6), save_path: str = None):
    """
    Plot coefficient values with confidence intervals.
    
    Parameters
    ----------
    model : statsmodels RegressionResultsWrapper
        Fitted OLS model
    figsize : tuple
        Figure size (width, height)
    save_path : str, optional
        Path to save the figure
    """
    if model is None:
        print("No model to plot.")
        return
    
    # Get coefficients (excluding intercept)
    coefs = model.params.drop('const', errors='ignore')
    conf_int = model.conf_int().drop('const', errors='ignore')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    y_pos = range(len(coefs))
    errors = [(coefs.values - conf_int[0].values), (conf_int[1].values - coefs.values)]
    
    colors = ['blue' if c > 0 else 'red' for c in coefs.values]
    ax.barh(y_pos, coefs.values, xerr=errors, color=colors, alpha=0.7, capsize=4)
    
    ax.axvline(x=0, color='black', linestyle='-', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(coefs.index)
    ax.set_xlabel('Coefficient Value', fontsize=11)
    ax.set_ylabel('Feature', fontsize=11)
    ax.set_title('Regression Coefficients with 95% Confidence Intervals', 
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.show()


def plot_actual_vs_predicted(y_actual, y_pred, figsize: tuple = (8, 6), 
                              save_path: str = None):
    """
    Plot actual vs predicted values.
    
    Parameters
    ----------
    y_actual : array-like
        Actual target values
    y_pred : array-like
        Predicted values
    figsize : tuple
        Figure size (width, height)
    save_path : str, optional
        Path to save the figure
    """
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.scatter(y_actual, y_pred, alpha=0.5, edgecolors='none')
    
    # Perfect prediction line
    min_val = min(np.min(y_actual), np.min(y_pred))
    max_val = max(np.max(y_actual), np.max(y_pred))
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, 
            label='Perfect Prediction')
    
    ax.set_xlabel('Actual Values', fontsize=11)
    ax.set_ylabel('Predicted Values', fontsize=11)
    ax.set_title('Actual vs Predicted Values', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    plt.show()
