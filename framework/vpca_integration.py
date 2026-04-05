"""
VPCA to Stepwise Regression Integration Module

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module provides functions to connect VPCA outputs to stepwise regression inputs,
automating the workflow that was previously done manually in Excel/SPSS.

Workflow:
1. Load VPCA loadings (from vpca_loadings.csv)
2. Convert loadings to z-scores (remove amplitude weighting)
3. Load/prepare spectral library (reference spectra for materials)
4. Run stepwise regression for each VPC component
5. Identify materials contributing to each component
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass

from .preprocessing import standardize_to_zscore
from .stepwise_vif import StepwiseVIFRegression


# Sentinel-2 band wavelengths (nm) - center wavelengths
SENTINEL2_WAVELENGTHS = {
    'B1': 443.9,   # Coastal aerosol
    'B2': 496.6,   # Blue
    'B3': 560.0,   # Green
    'B4': 664.5,   # Red
    'B5': 703.9,   # Red Edge 1
    'B6': 740.2,   # Red Edge 2
    'B7': 782.5,   # Red Edge 3
    'B8': 835.1,   # NIR
    'B8A': 864.8,  # NIR Narrow
}

# Default band order for VPCA
DEFAULT_BAND_ORDER = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A']


@dataclass
class VPCAResults:
    """Container for VPCA analysis results."""
    loadings: pd.DataFrame       # (bands × components) - raw loadings
    z_loadings: pd.DataFrame     # (bands × components) - z-scored loadings
    eigenvalues: Optional[pd.Series] = None
    variance_explained: Optional[pd.Series] = None
    communalities: Optional[pd.DataFrame] = None
    band_names: List[str] = None
    component_names: List[str] = None
    
    def __post_init__(self):
        if self.band_names is None:
            self.band_names = self.loadings.index.tolist()
        if self.component_names is None:
            self.component_names = self.loadings.columns.tolist()


@dataclass 
class StepwiseResult:
    """Container for stepwise regression result for one VPC."""
    component: str
    model: StepwiseVIFRegression
    selected_materials: List[str]
    r2: float
    adj_r2: float
    coefficients: pd.DataFrame
    vif_values: pd.DataFrame


def load_vpca_loadings(loadings_path: Union[str, Path],
                       eigenvalues_path: Optional[Union[str, Path]] = None,
                       variance_path: Optional[Union[str, Path]] = None,
                       band_col: str = 'band') -> VPCAResults:
    """
    Load VPCA loadings from CSV file and prepare for stepwise regression.
    
    Parameters
    ----------
    loadings_path : str or Path
        Path to VPCA loadings CSV file. Expected format:
        - Rows: spectral bands (B1, B2, ..., B8A)
        - Columns: VPC1, VPC2, ..., VPC6
    eigenvalues_path : str or Path, optional
        Path to eigenvalues CSV
    variance_path : str or Path, optional
        Path to variance explained CSV
    band_col : str
        Name of column containing band names (or use index)
    
    Returns
    -------
    VPCAResults
        Container with raw and z-scored loadings
    
    Example
    -------
    >>> results = load_vpca_loadings('vpca_results/vpca_loadings.csv')
    >>> print(results.z_loadings)  # Ready for stepwise regression
    """
    # Load loadings
    loadings_df = pd.read_csv(loadings_path)
    
    # Handle band names - could be in first column or index
    if band_col in loadings_df.columns:
        loadings_df = loadings_df.set_index(band_col)
    elif loadings_df.columns[0] in ['band', 'Band', 'wavelength', 'Wavelength', 'Wavelengths']:
        loadings_df = loadings_df.set_index(loadings_df.columns[0])
    
    # Filter out metadata rows (Eigenvalues, Frac Var, Extracted Frac Var)
    # These rows have non-numeric index values
    if loadings_df.index.dtype == object:
        numeric_mask = pd.to_numeric(loadings_df.index, errors='coerce').notna()
        loadings_df = loadings_df[numeric_mask]
        loadings_df.index = pd.to_numeric(loadings_df.index)
    
    # Identify component columns (VPC1, VPC2, etc. or PC1, PC2, etc.)
    component_cols = [c for c in loadings_df.columns 
                      if c.upper().startswith(('VPC', 'PC', 'COMP'))]
    if not component_cols:
        # Try columns starting with 'component' (legacy VPCA output)
        component_cols = [c for c in loadings_df.columns
                          if c.lower().startswith('component')]
    if not component_cols:
        # Assume all numeric columns except Comm_* are components
        component_cols = [c for c in loadings_df.select_dtypes(include=[np.number]).columns
                          if not c.startswith('Comm')]
    
    loadings = loadings_df[component_cols]
    
    # Rename legacy 'component N' format to 'VPCN' for consistency
    rename_map = {}
    for col in loadings.columns:
        if col.lower().startswith('component'):
            num = col.replace('component', '').replace('Component', '').strip()
            rename_map[col] = f'VPC{num}'
    if rename_map:
        loadings = loadings.rename(columns=rename_map)
    
    # Compute z-scores (across bands for each component)
    z_loadings = standardize_to_zscore(loadings.T, axis=1).T
    
    # Load optional files
    eigenvalues = None
    variance_explained = None
    
    if eigenvalues_path and Path(eigenvalues_path).exists():
        eigen_df = pd.read_csv(eigenvalues_path)
        eigenvalues = eigen_df.iloc[:, -1] if len(eigen_df.columns) > 1 else eigen_df.iloc[:, 0]
    
    if variance_path and Path(variance_path).exists():
        var_df = pd.read_csv(variance_path)
        variance_explained = var_df.iloc[:, -1] if len(var_df.columns) > 1 else var_df.iloc[:, 0]
    
    return VPCAResults(
        loadings=loadings,
        z_loadings=z_loadings,
        eigenvalues=eigenvalues,
        variance_explained=variance_explained
    )


def load_spectral_library(library_path: Union[str, Path],
                          wavelength_col: str = 'wavelength',
                          environment: str = 'freshwater') -> pd.DataFrame:
    """
    Load spectral library and filter for environment type.
    
    Parameters
    ----------
    library_path : str or Path
        Path to spectral library CSV. Expected format:
        - First column: wavelength or band name
        - Other columns: reference spectra (water, pigments, minerals)
    wavelength_col : str
        Name of wavelength/band column
    environment : str
        Environment type for filtering: 'freshwater', 'marine', or 'all'
    
    Returns
    -------
    pd.DataFrame
        Spectral library with bands as index, spectra as columns
    
    Notes
    -----
    For freshwater (Lake Erie), marine-only spectra are excluded:
    - Sargassum, Halodule, Syringodium, Thalassia (seagrasses)
    - Karenia brevis, K. brevis (red tide)
    - Aragonite (typically marine carbonate)
    """
    library = pd.read_csv(library_path)
    
    # Set wavelength/band as index
    if wavelength_col in library.columns:
        library = library.set_index(wavelength_col)
    else:
        library = library.set_index(library.columns[0])
    
    # Filter columns based on environment
    if environment.lower() == 'freshwater':
        # Exclude marine-only spectra
        marine_only = [
            'sargassum', 'halodule', 'syringodium', 'thalassia',
            'karenia', 'k_brevis', 'kbrevis', 'k. brevis',
            'aragonite', 'coral'
        ]
        cols_to_keep = []
        for col in library.columns:
            col_lower = col.lower()
            if not any(marine in col_lower for marine in marine_only):
                cols_to_keep.append(col)
        library = library[cols_to_keep]
    
    elif environment.lower() == 'marine':
        pass  # Keep all spectra for marine
    
    # else 'all' - keep everything
    
    return library


def align_to_sentinel2_bands(library: pd.DataFrame,
                             target_bands: List[str] = None) -> pd.DataFrame:
    """
    Resample/align spectral library to Sentinel-2 band wavelengths.
    
    Parameters
    ----------
    library : pd.DataFrame
        Spectral library with wavelengths as index (in nm)
    target_bands : list
        Target Sentinel-2 bands. Default: B1-B8A
    
    Returns
    -------
    pd.DataFrame
        Library resampled to Sentinel-2 bands
    
    Notes
    -----
    If library has hyperspectral resolution (e.g., 10nm), this function
    interpolates to the Sentinel-2 band center wavelengths.
    If library already has Sentinel-2 bands, returns as-is.
    """
    if target_bands is None:
        target_bands = DEFAULT_BAND_ORDER
    
    target_wavelengths = [SENTINEL2_WAVELENGTHS[b] for b in target_bands]
    
    # Check if library index is numeric (wavelengths) or band names
    try:
        lib_wavelengths = library.index.astype(float)
        is_numeric = True
    except (ValueError, TypeError):
        is_numeric = False
    
    if is_numeric:
        # Interpolate to target wavelengths
        from scipy import interpolate
        
        resampled = pd.DataFrame(index=target_bands)
        for col in library.columns:
            f = interpolate.interp1d(lib_wavelengths, library[col].values,
                                     kind='linear', fill_value='extrapolate')
            resampled[col] = f(target_wavelengths)
        return resampled
    else:
        # Already has band names - filter to target
        available = [b for b in target_bands if b in library.index]
        return library.loc[available]


def run_stepwise_identification(vpca_results: VPCAResults,
                                spectral_library: pd.DataFrame,
                                components: List[str] = None,
                                method: str = 'forward',
                                p_enter: float = 0.05,
                                p_remove: float = 0.10,
                                vif_threshold: float = 2.0,
                                r2_change_threshold: float = None,
                                verbose: int = 1) -> Dict[str, StepwiseResult]:
    """
    Run stepwise regression to identify materials for each VPC component.
    
    This automates the SPSS workflow shown in the meeting:
    1. Take z-scored VPC loadings (Y variable)
    2. Regress against spectral library (X variables)
    3. Use joint p-value + VIF stopping criterion
    
    Parameters
    ----------
    vpca_results : VPCAResults
        VPCA results with z-scored loadings
    spectral_library : pd.DataFrame
        Reference spectra (bands as rows, materials as columns)
    components : list, optional
        Which components to analyze. Default: all VPCs
    method : str
        Stepwise method: 'forward', 'backward', or 'bidirectional'
    p_enter : float
        P-value threshold for entry (default 0.05)
    p_remove : float
        P-value threshold for removal (default 0.10)
    vif_threshold : float
        VIF threshold (default 2.0 for principal components)
    r2_change_threshold : float, optional
        Minimum R² change to continue adding variables
    verbose : int
        Verbosity level
    
    Returns
    -------
    Dict[str, StepwiseResult]
        Results for each component
    
    Example
    -------
    >>> results = run_stepwise_identification(vpca, library)
    >>> for comp, result in results.items():
    ...     print(f"{comp}: {result.selected_materials}, R²={result.r2:.3f}")
    """
    if components is None:
        components = vpca_results.component_names
    
    # Ensure alignment between loadings and library
    common_bands = list(set(vpca_results.z_loadings.index) & 
                        set(spectral_library.index))
    if len(common_bands) == 0:
        raise ValueError("No common bands between VPCA loadings and spectral library. "
                         "Check band names/wavelengths alignment.")
    
    z_loadings = vpca_results.z_loadings.loc[common_bands]
    library = spectral_library.loc[common_bands]
    
    # Standardize library spectra
    library_z = standardize_to_zscore(library.T, axis=1).T
    
    results = {}
    
    for comp in components:
        if comp not in z_loadings.columns:
            print(f"Warning: Component {comp} not found in loadings")
            continue
        
        if verbose >= 1:
            print(f"\n{'='*60}")
            print(f"Identifying materials for {comp}")
            print(f"{'='*60}")
        
        # Y = z-scored VPC loadings for this component
        y = z_loadings[comp]
        
        # X = z-scored spectral library
        X = library_z
        
        # Run stepwise regression
        model = StepwiseVIFRegression(
            method=method,
            p_enter=p_enter,
            p_remove=p_remove,
            vif_threshold=vif_threshold,
            r2_change_threshold=r2_change_threshold,
            verbose=verbose
        )
        model.fit(X, y)
        
        # Extract results
        if model.model_ is not None:
            coef_df = pd.DataFrame({
                'material': ['const'] + model.selected_features_,
                'coefficient': model.model_.params.values,
                'std_error': model.model_.bse.values,
                'p_value': model.model_.pvalues.values
            })
            r2 = model.model_.rsquared
            adj_r2 = model.model_.rsquared_adj
        else:
            coef_df = pd.DataFrame()
            r2 = 0.0
            adj_r2 = 0.0
        
        results[comp] = StepwiseResult(
            component=comp,
            model=model,
            selected_materials=model.selected_features_,
            r2=r2,
            adj_r2=adj_r2,
            coefficients=coef_df,
            vif_values=model.vif_final_ if model.vif_final_ is not None else pd.DataFrame()
        )
    
    return results


def create_identification_summary(results: Dict[str, StepwiseResult]) -> pd.DataFrame:
    """
    Create summary table of material identifications for all components.
    
    Parameters
    ----------
    results : Dict[str, StepwiseResult]
        Results from run_stepwise_identification
    
    Returns
    -------
    pd.DataFrame
        Summary with columns: Component, Materials, N_Materials, R2, Adj_R2, Max_VIF
    """
    summary_rows = []
    
    for comp, result in results.items():
        max_vif = result.vif_values['VIF'].max() if not result.vif_values.empty else 0.0
        
        summary_rows.append({
            'Component': comp,
            'Materials': ', '.join(result.selected_materials),
            'N_Materials': len(result.selected_materials),
            'R2': result.r2,
            'Adj_R2': result.adj_r2,
            'Max_VIF': max_vif
        })
    
    return pd.DataFrame(summary_rows)


def print_identification_report(results: Dict[str, StepwiseResult]):
    """Print formatted identification report."""
    print("\n" + "=" * 70)
    print("MATERIAL IDENTIFICATION REPORT")
    print("=" * 70)
    
    for comp, result in results.items():
        print(f"\n{comp}:")
        print(f"  R² = {result.r2:.4f}, Adj R² = {result.adj_r2:.4f}")
        print(f"  Materials identified ({len(result.selected_materials)}):")
        for mat in result.selected_materials:
            coef_row = result.coefficients[result.coefficients['material'] == mat]
            if not coef_row.empty:
                coef = coef_row['coefficient'].values[0]
                pval = coef_row['p_value'].values[0]
                print(f"    - {mat}: coef={coef:.4f}, p={pval:.4f}")
        
        if not result.vif_values.empty:
            max_vif = result.vif_values['VIF'].max()
            print(f"  Max VIF: {max_vif:.2f}")
    
    print("\n" + "=" * 70)
