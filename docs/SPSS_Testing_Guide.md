# SPSS Testing Guide for Stepwise Regression Validation

## Purpose
This guide helps you run the same stepwise regression analysis in SPSS to validate that our Python implementation produces identical results.

---

## Prerequisites

1. **SPSS Software** (Version 20 or higher recommended)
2. **Data Files**:
   - `test_loadings.csv` - VPCA loadings (already z-scored in Python)
   - `test_library.csv` - Spectral library (already z-scored in Python)

---

## Step 1: Prepare Data in SPSS

### Import CSV Files

**Option A: Import Both Files Separately (Recommended)**

1. Open SPSS
2. Go to **File → Open → Data**
3. Select `test_loadings.csv`
4. In the import wizard:
   - Check "First row contains variable names"
   - Click OK
5. Save as SPSS file: **File → Save As → test_loadings.sav**

6. Open new instance of SPSS or go to **File → New → Data**
7. Go to **File → Open → Data**
8. Select `test_library.csv`
9. In the import wizard:
   - Check "First row contains variable names"
   - Click OK
10. Save as SPSS file: **File → Save As → test_library.sav**

### Merge Library Data

1. With `test_loadings.sav` open
2. Go to **Data → Merge Files → Add Variables**
3. Select `test_library.sav` (now it will show .sav files)
4. Match by `Wavelength` column
5. Click OK

**Option B: Combine in Excel First (Alternative)**

1. Open both CSV files in Excel
2. Copy all columns from library.csv (except Wavelength)
3. Paste into loadings.csv matching by Wavelength
4. Save as combined CSV
5. Import combined CSV into SPSS

---

## Step 2: Standardize Variables (Z-Scores)

**IMPORTANT**: Our Python code uses **population standard deviation (ddof=0)**. SPSS uses **sample standard deviation (ddof=1)** by default.

### Create Z-Scores in SPSS

1. Go to **Analyze → Descriptive Statistics → Descriptives**
2. Select all VPC columns (VPC1, VPC2, ..., VPC6)
3. Select all library material columns
4. Check **"Save standardized values as variables"**
5. Click OK

This creates new variables with `Z` prefix (e.g., `ZVPC1`, `ZPure_Water`)

### Verify Z-Scores

1. Go to **Analyze → Descriptive Statistics → Descriptives**
2. Select all Z-scored variables
3. Click **Options** → Check "Mean" and "Std. deviation"
4. Verify:
   - All means ≈ 0.000
   - All std deviations = 1.000

---

## Step 3: Run Stepwise Regression

### For Each VPC Component (e.g., ZVPC1)

1. Go to **Analyze → Regression → Linear**

2. **Dependent Variable**: Select `ZVPC1` (or whichever component you're testing)

3. **Independent Variables**: Select ALL z-scored library materials (all variables starting with `Z`)

4. Click **Method** dropdown → Select **"Stepwise"**

5. Click **Statistics** button:
   - Check: ☑ Estimates
   - Check: ☑ Model fit
   - Check: ☑ R squared change
   - Check: ☑ Descriptives
   - Check: ☑ Collinearity diagnostics (for VIF)
   - Click Continue

6. Click **Options** button:
   - **Stepping Method Criteria**:
     - Entry: Probability of F ≤ **0.05**
     - Removal: Probability of F ≥ **0.10**
   - Check: ☑ Include constant in equation
   - Click Continue

7. Click **OK** to run

---

## Step 4: Compare Results

### Tables to Compare

#### 1. **Model Summary Table**
Compare these columns:
- Model number (1, 2, 3, ...)
- R
- R Square
- Adjusted R Square
- Std. Error of the Estimate
- R Square Change
- F Change
- df1, df2
- Sig. F Change

#### 2. **ANOVA Table**
Compare for each model:
- Sum of Squares (Regression, Residual, Total)
- df (degrees of freedom)
- Mean Square
- F statistic
- Sig. (p-value)

#### 3. **Coefficients Table**
Compare for each variable in each model:
- Standardized Beta coefficient
- Std. Error
- t statistic
- Sig. (p-value)
- Zero-order correlation
- VIF (Variance Inflation Factor)

---

## Step 5: Troubleshooting Differences

### If Results Don't Match:

#### A. Check Z-Score Method
- **Python uses**: Population std (ddof=0) → `std = sqrt(sum((x-mean)²) / n)`
- **SPSS uses**: Sample std (ddof=1) → `std = sqrt(sum((x-mean)²) / (n-1))`

**Solution**: In Python, change `ddof=0` to `ddof=1` in the `zscore_dataframe` function.

#### B. Check VIF Threshold
- Our Python code: VIF threshold = 100.0 (effectively disabled)
- SPSS: No VIF filtering during stepwise selection

**Solution**: Already set to 100.0 in Python to match SPSS behavior.

#### C. Check Entry/Removal Criteria
- Python: p_enter=0.05, p_remove=0.10
- SPSS: Should match (verify in Options)

#### D. Check Variable Order
- SPSS may select variables in different order if p-values are very close
- Check if the **final model** has the same variables (order doesn't matter)

---

## Step 6: Export SPSS Results

### Save Output Tables

1. Right-click on each table in SPSS Output window
2. Select **Export**
3. Choose **Excel** format
4. Save as:
   - `SPSS_ModelSummary_VPC1.xlsx`
   - `SPSS_ANOVA_VPC1.xlsx`
   - `SPSS_Coefficients_VPC1.xlsx`

### Compare with Python Output

Python saves to: `regression_analysis_results.xlsx`

Open both files side-by-side and compare:
- Number of models
- R² values (should match to 4 decimal places)
- Variable selection order
- Coefficients (should match to 4 decimal places)
- VIF values (should match to 2 decimal places)

---

## Expected Behavior

### What Should Match:
✓ Number of variables selected  
✓ Final R² and Adjusted R²  
✓ F statistics and p-values  
✓ Standardized coefficients (Beta)  
✓ VIF values  
✓ Variable significance (p-values)

### What Might Differ Slightly:
⚠ Rounding differences in 4th+ decimal place  
⚠ Variable entry order if p-values are extremely close  
⚠ Exact t-statistics due to floating-point precision

---

## Quick Validation Checklist

- [ ] Z-scores calculated (mean=0, std=1)
- [ ] Stepwise method selected
- [ ] Entry criterion: p ≤ 0.05
- [ ] Removal criterion: p ≥ 0.10
- [ ] VIF statistics enabled
- [ ] Same dependent variable (e.g., ZVPC1)
- [ ] Same independent variables (all z-scored library materials)
- [ ] Results exported to Excel
- [ ] Compared with Python output

---

## Notes

1. **Run for all 6 VPCs**: Repeat Step 3 for ZVPC1, ZVPC2, ..., ZVPC6
2. **Document differences**: Note any discrepancies in a comparison spreadsheet
3. **Check sample size**: Ensure SPSS and Python use same number of observations (wavelengths)
4. **Missing data**: Verify no missing values in either dataset

---

## Contact & Support

If results differ significantly:
1. Check the z-score calculation method (ddof parameter)
2. Verify entry/removal p-value thresholds
3. Ensure VIF threshold is high enough (100.0) to not interfere
4. Compare intermediate steps (which variable was added at each step)

---

## File Locations

- **Python Output**: `C:/Users/ahusse12/OneDrive - Kent State University/Documents/Stepwise-Learning/output/regression_analysis_results.xlsx`
- **SPSS Data**: `C:/Users/ahusse12/OneDrive - Kent State University/Documents/Stepwise-Learning/data/test/`
- **This Guide**: `Stepwise Regrission/Learning/SPSS_Testing_Guide.md`
