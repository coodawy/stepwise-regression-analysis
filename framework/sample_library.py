"""
Sample Spectral Library Generator for Testing

Author: Abdulrahman Hussein
Supervisor: Dr. Joseph D. Ortiz
Institution: Kent State University, Department of Earth Sciences

This module creates synthetic spectral library data for testing the
VPCA → Stepwise regression workflow when real spectral library is not available.

The sample spectra are based on typical spectral characteristics of:
- Pure water
- Cyanobacteria pigments (chlorophyll, phycocyanin)
- Common minerals (clays, basalt)
- Degradation products

These are NOT accurate reference spectra - use only for testing workflow!
"""

import numpy as np
import pandas as pd
from typing import List


# Sentinel-2 band center wavelengths
SENTINEL2_BANDS = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B8A']
SENTINEL2_WAVELENGTHS = [443.9, 496.6, 560.0, 664.5, 703.9, 740.2, 782.5, 835.1, 864.8]


def create_sample_spectral_library(bands: List[str] = None,
                                   environment: str = 'freshwater',
                                   include_minerals: bool = True,
                                   include_degradation: bool = True) -> pd.DataFrame:
    """
    Create a sample spectral library for testing.
    
    Parameters
    ----------
    bands : list, optional
        Band names. Default: Sentinel-2 B1-B8A
    environment : str
        'freshwater' or 'marine' - affects which spectra are included
    include_minerals : bool
        Whether to include mineral spectra
    include_degradation : bool
        Whether to include pigment degradation products
    
    Returns
    -------
    pd.DataFrame
        Sample spectral library (bands as index, materials as columns)
    
    Notes
    -----
    These are SYNTHETIC spectra for testing only!
    Real analysis should use actual measured reference spectra.
    """
    if bands is None:
        bands = SENTINEL2_BANDS
    
    n_bands = len(bands)
    wavelengths = np.array(SENTINEL2_WAVELENGTHS[:n_bands])
    
    # Normalize wavelengths for shape functions
    wl_norm = (wavelengths - wavelengths.min()) / (wavelengths.max() - wavelengths.min())
    
    spectra = {}
    
    # Pure water - low reflectance, decreasing with wavelength
    spectra['Water'] = 0.02 * np.exp(-2 * wl_norm)
    
    # === PIGMENTS (Freshwater) ===
    
    # Chlorophyll-a: absorption at ~440nm (B1) and ~665nm (B4)
    chl_a = 0.1 * np.ones(n_bands)
    chl_a[0] = 0.02  # B1 absorption
    chl_a[3] = 0.03  # B4 absorption  
    chl_a[2] = 0.15  # B3 green peak
    spectra['Chlorophyll_A'] = chl_a
    
    # Chlorophyll-b: similar to Chl-a, shifted slightly
    chl_b = 0.1 * np.ones(n_bands)
    chl_b[0] = 0.03
    chl_b[1] = 0.02  # B2 absorption
    chl_b[2] = 0.12
    spectra['Chlorophyll_B'] = chl_b
    
    # Chlorophyll-c: found in diatoms
    chl_c = 0.08 * np.ones(n_bands)
    chl_c[0] = 0.02
    chl_c[1] = 0.03
    chl_c[2] = 0.1
    spectra['Chlorophyll_C'] = chl_c
    
    # Phycocyanin: cyanobacteria, absorption ~620nm (between B3 and B4)
    phyco = 0.08 * np.ones(n_bands)
    phyco[2] = 0.04  # absorption near 560nm
    phyco[3] = 0.06
    phyco[4] = 0.12  # reflectance peak in red edge
    spectra['Phycocyanin'] = phyco
    
    # Diatoms (Bacillariophyceae) - brown algae signature
    diatoms = 0.08 * np.ones(n_bands)
    diatoms[0] = 0.04
    diatoms[1] = 0.06
    diatoms[2] = 0.10
    diatoms[3] = 0.05
    spectra['Diatoms'] = diatoms
    
    # Carotenoids - absorption in blue, peak in green-yellow
    carot = 0.1 * np.ones(n_bands)
    carot[0] = 0.03
    carot[1] = 0.04
    carot[2] = 0.12
    carot[3] = 0.11
    spectra['Carotenoids'] = carot
    
    # Zeaxanthin (cyanobacterial carotenoid)
    zeax = 0.09 * np.ones(n_bands)
    zeax[0] = 0.02
    zeax[1] = 0.03
    zeax[2] = 0.11
    spectra['Zeaxanthin'] = zeax
    
    # Diadinoxanthin
    diadin = 0.08 * np.ones(n_bands)
    diadin[0] = 0.03
    diadin[1] = 0.04
    diadin[2] = 0.10
    spectra['Diadinoxanthin'] = diadin
    
    # === DEGRADATION PRODUCTS ===
    if include_degradation:
        # Pheophytin-a (chlorophyll-a without Mg)
        pheo_a = chl_a.copy() * 0.8
        pheo_a[3] = 0.05  # shifted absorption
        spectra['Pheophytin_A'] = pheo_a
        
        # Pheophytin-b
        pheo_b = chl_b.copy() * 0.8
        spectra['Pheophytin_B'] = pheo_b
        
        # Pheorbide (no phytol tail)
        pheorb = chl_a.copy() * 0.7
        pheorb[4] = 0.08
        spectra['Pheorbide_A'] = pheorb
        
        # Chlorophyllide
        chlide = chl_a.copy() * 0.75
        spectra['Chlorophyllide_A'] = chlide
    
    # === MINERALS ===
    if include_minerals:
        # Clay minerals - high in NIR
        clay = 0.2 * np.ones(n_bands)
        clay[0:3] = [0.10, 0.12, 0.15]
        clay[6:] = [0.25, 0.30, 0.32]
        spectra['Clay'] = clay
        
        # Pyrolousite (MnO2) - dark, low reflectance
        pyrol = 0.05 * np.ones(n_bands)
        pyrol[6:] = [0.03, 0.02, 0.02]
        spectra['Pyrolousite'] = pyrol
        
        # Dolomite - bright, relatively flat
        dolo = 0.35 * np.ones(n_bands)
        dolo[0] = 0.30
        dolo[7:] = [0.38, 0.40]
        spectra['Dolomite'] = dolo
        
        # Basalt - dark, increasing in NIR
        basalt = 0.08 * np.ones(n_bands)
        basalt[6:] = [0.10, 0.12, 0.14]
        spectra['Basalt'] = basalt
        
        # Weathered basalt
        weath_basalt = basalt * 1.3
        weath_basalt[0:3] = basalt[0:3] * 1.5
        spectra['Weathered_Basalt'] = weath_basalt
        
        # Sulfate minerals
        sulfate = 0.40 * np.ones(n_bands)
        sulfate[0:2] = [0.35, 0.38]
        spectra['Sulfate'] = sulfate
    
    # === MARINE-ONLY (exclude for freshwater) ===
    if environment.lower() == 'marine':
        # Karenia brevis (red tide)
        kbrevis = 0.07 * np.ones(n_bands)
        kbrevis[0] = 0.02
        kbrevis[2] = 0.09
        kbrevis[3] = 0.04
        spectra['Karenia_brevis'] = kbrevis
        
        # Sargassum (seaweed)
        sarg = 0.12 * np.ones(n_bands)
        sarg[0:2] = [0.05, 0.07]
        sarg[2] = 0.08
        sarg[4:] = [0.15, 0.18, 0.20, 0.22, 0.24]
        spectra['Sargassum'] = sarg
    
    # Create DataFrame
    library = pd.DataFrame(spectra, index=bands)
    
    return library


def create_sample_vpca_loadings(n_components: int = 6,
                                bands: List[str] = None) -> pd.DataFrame:
    """
    Create sample VPCA loadings for testing.
    
    Parameters
    ----------
    n_components : int
        Number of VPC components (default 6)
    bands : list
        Band names
    
    Returns
    -------
    pd.DataFrame
        Sample loadings (bands as rows, VPCs as columns)
    """
    if bands is None:
        bands = SENTINEL2_BANDS
    
    n_bands = len(bands)
    np.random.seed(42)  # Reproducible
    
    # Create realistic-looking loadings
    # VPC1 typically captures overall brightness
    vpc1 = np.ones(n_bands) * 0.3 + np.random.randn(n_bands) * 0.1
    
    # VPC2 often captures blue-red contrast
    vpc2 = np.linspace(-0.4, 0.4, n_bands) + np.random.randn(n_bands) * 0.05
    
    # VPC3 captures green peak
    vpc3 = np.zeros(n_bands)
    vpc3[2] = 0.5  # B3 green
    vpc3[0] = -0.3
    vpc3[3] = -0.2
    vpc3 += np.random.randn(n_bands) * 0.05
    
    # VPC4-6 capture finer spectral features
    vpc4 = np.random.randn(n_bands) * 0.2
    vpc5 = np.random.randn(n_bands) * 0.15
    vpc6 = np.random.randn(n_bands) * 0.1
    
    loadings = np.column_stack([vpc1, vpc2, vpc3, vpc4, vpc5, vpc6])[:, :n_components]
    
    component_names = [f'VPC{i+1}' for i in range(n_components)]
    
    return pd.DataFrame(loadings, index=bands, columns=component_names)


def save_sample_data(output_folder: str = '.'):
    """
    Save sample spectral library and VPCA loadings to CSV files.
    
    Parameters
    ----------
    output_folder : str
        Folder to save files
    
    Returns
    -------
    dict
        Paths to created files
    """
    from pathlib import Path
    
    folder = Path(output_folder)
    folder.mkdir(parents=True, exist_ok=True)
    
    # Create and save spectral library
    library = create_sample_spectral_library()
    library_path = folder / 'sample_spectral_library.csv'
    library.to_csv(library_path)
    
    # Create and save VPCA loadings
    loadings = create_sample_vpca_loadings()
    loadings_path = folder / 'sample_vpca_loadings.csv'
    loadings.to_csv(loadings_path)
    
    print(f"✓ Created sample spectral library: {library_path}")
    print(f"✓ Created sample VPCA loadings: {loadings_path}")
    
    return {
        'library': str(library_path),
        'loadings': str(loadings_path)
    }
