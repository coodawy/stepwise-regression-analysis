# Learning Materials

This folder contains educational notebooks and test data used during the development and testing of the stepwise regression framework.

## 📁 Contents

### `notebooks/`
Learning and testing notebooks:
- **Stepwise-learning-Code Writing-v2.ipynb**: Latest version of the stepwise regression implementation with full z-score tables and incremental model building
- **complete_tutorial.ipynb**: Complete tutorial demonstrating the full workflow

### `test-data/`
Sample datasets for testing:
- **test_loadings.csv**: Sample VPCA loadings data (5 wavelengths × 6 components)
- **test_library.csv**: Sample spectral library data (5 wavelengths × 148 materials)

### `spss-files/`
SPSS output files for validation and comparison:
- Various `.spv` files containing SPSS regression results for validation

## 🎯 Purpose

These materials were used to:
1. Develop and test the stepwise regression algorithm
2. Validate results against SPSS output
3. Refine statistical table generation
4. Document the learning process

## 📚 How to Use

1. Start with the notebooks to understand the methodology
2. Use test data to run your own analyses
3. Compare results with SPSS files for validation
4. Refer to `../docs/SPSS_Testing_Guide.md` for validation procedures

## ⚠️ Note

These are development/learning materials. For production use, refer to the main framework in the `framework/` directory.
