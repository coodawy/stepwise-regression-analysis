"""
Preprocessing Utilities for Stepwise Regression

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module provides preprocessing functions for preparing data for stepwise regression,
including z-score standardization of VPCA component loadings.
"""

import numpy as np
import pandas as pd
from typing import Union, Tuple, Optional


def standardize_to_zscore(data: Union[pd.DataFrame, pd.Series, np.ndarray],
                          axis: int = 1) -> Union[pd.DataFrame, pd.Series, np.ndarray]:
    """
    Convert data to z-scores (standardized values).
    
    Z-score = (value - mean) / standard_deviation
    
    This removes amplitude/abundance weighting from component loadings,
    converting values to units of standard deviations from the mean.
    
    Parameters
    ----------
    data : pd.DataFrame, pd.Series, or np.ndarray
        Input data to standardize. For VPCA loadings, rows are typically
        components and columns are spectral bands.
    axis : int, default=1
        Axis along which to compute mean and std:
        - axis=1: Standardize across columns (across spectral bands for each component)
        - axis=0: Standardize across rows
    
    Returns
    -------
    Same type as input
        Z-score standardized data
    
    Notes
    -----
    For VPCA component loadings:
    - Component loadings = eigenvectors × singular values
    - Singular value = sqrt(variance explained by component)
    - Z-score standardization removes this variance scaling
    
    Interpretation of z-scores:
    - z = 0: Value equals the mean
    - z = 1: Value is one standard deviation above the mean
    - z = -1: Value is one standard deviation below the mean
    - z = 2: Value is two standard deviations above the mean
    
    Example
    -------
    >>> loadings = pd.DataFrame({'B1': [0.5, 0.2], 'B2': [0.8, 0.3], 'B3': [0.6, 0.25]})
    >>> z_loadings = standardize_to_zscore(loadings, axis=1)
    """
    if isinstance(data, pd.DataFrame):
        mean = data.mean(axis=axis)
        std = data.std(axis=axis)
        # Handle zero std (constant values)
        std = std.replace(0, 1)
        if axis == 1:
            return data.sub(mean, axis=0).div(std, axis=0)
        else:
            return data.sub(mean, axis=1).div(std, axis=1)
    
    elif isinstance(data, pd.Series):
        mean = data.mean()
        std = data.std()
        if std == 0:
            std = 1
        return (data - mean) / std
    
    else:  # numpy array
        mean = np.mean(data, axis=axis, keepdims=True)
        std = np.std(data, axis=axis, keepdims=True)
        std[std == 0] = 1  # Handle zero std
        return (data - mean) / std


def standardize_loadings_for_regression(loadings: pd.DataFrame,
                                        transpose: bool = True) -> pd.DataFrame:
    """
    Prepare VPCA loadings for stepwise regression by standardizing to z-scores.
    
    This is the key preprocessing step before using component loadings
    with a spectral library in stepwise regression.
    
    Parameters
    ----------
    loadings : pd.DataFrame
        VPCA component loadings matrix. Typically:
        - Rows: Components (VPC1, VPC2, ...)
        - Columns: Spectral bands
    transpose : bool, default=True
        If True, transpose so that:
        - Rows: Spectral bands (observations for regression)
        - Columns: Components (predictors for regression)
    
    Returns
    -------
    pd.DataFrame
        Z-score standardized loadings ready for regression.
        Each component is standardized across spectral bands.
    
    Example
    -------
    >>> # Load VPCA results
    >>> loadings = pd.read_csv('vpca_loadings.csv', index_col=0)
    >>> # Standardize for regression
    >>> z_loadings = standardize_loadings_for_regression(loadings)
    >>> # Now use z_loadings as X in stepwise regression
    """
    # Standardize across spectral bands (axis=1)
    z_scored = standardize_to_zscore(loadings, axis=1)
    
    if transpose:
        return z_scored.T
    return z_scored


def prepare_spectral_library(library: pd.DataFrame,
                             bands: Optional[list] = None,
                             standardize: bool = True) -> pd.DataFrame:
    """
    Prepare a spectral library for use in stepwise regression.
    
    Parameters
    ----------
    library : pd.DataFrame
        Spectral library with:
        - Rows: Spectral bands (wavelengths)
        - Columns: Library spectra (water, pigments, minerals, etc.)
    bands : list, optional
        List of band names/wavelengths to include. If None, uses all bands.
    standardize : bool, default=True
        If True, standardize each spectrum to z-scores.
    
    Returns
    -------
    pd.DataFrame
        Prepared spectral library
    
    Notes
    -----
    The spectral library should contain reference spectra for:
    - Pure water
    - Pigments (chlorophyll, carotenoids, phycocyanin, etc.)
    - Degradation products (pheophytin, pheorbid, chlorophyllide)
    - Minerals (clays, sulfides, sulfates, siliciclastics)
    
    For freshwater environments (lakes), exclude:
    - Marine seagrasses (Sargassum, Halodule, Syringodium, Thalassia)
    - Marine-only algae (Karenia brevis, etc.)
    """
    # Filter bands if specified
    if bands is not None:
        library = library.loc[bands]
    
    if standardize:
        # Standardize each spectrum (column) across bands
        return standardize_to_zscore(library.T, axis=1).T
    
    return library


def validate_band_alignment(component_loadings: pd.DataFrame,
                            spectral_library: pd.DataFrame) -> Tuple[bool, list]:
    """
    Check if component loadings and spectral library have matching bands.
    
    Parameters
    ----------
    component_loadings : pd.DataFrame
        Z-scored component loadings (bands as rows after transpose)
    spectral_library : pd.DataFrame
        Spectral library (bands as rows)
    
    Returns
    -------
    Tuple[bool, list]
        (all_match, common_bands) - Whether all bands match and list of common bands
    """
    loading_bands = set(component_loadings.index)
    library_bands = set(spectral_library.index)
    
    common = loading_bands.intersection(library_bands)
    all_match = loading_bands == library_bands
    
    return all_match, sorted(list(common))


def merge_loadings_with_library(z_loadings: pd.DataFrame,
                                spectral_library: pd.DataFrame,
                                align_bands: bool = True) -> pd.DataFrame:
    """
    Merge z-scored component loadings with spectral library for regression.
    
    Parameters
    ----------
    z_loadings : pd.DataFrame
        Z-scored component loadings (bands as rows, components as columns)
    spectral_library : pd.DataFrame
        Spectral library (bands as rows, spectra as columns)
    align_bands : bool, default=True
        If True, align on common bands only
    
    Returns
    -------
    pd.DataFrame
        Merged DataFrame with bands as rows, all spectra as columns
    
    Notes
    -----
    The z-scored loadings become the dependent variable (Y) in regression,
    while the spectral library provides the independent variables (X).
    """
    if align_bands:
        _, common_bands = validate_band_alignment(z_loadings, spectral_library)
        z_loadings = z_loadings.loc[common_bands]
        spectral_library = spectral_library.loc[common_bands]
    
    # Merge horizontally
    return pd.concat([z_loadings, spectral_library], axis=1)
