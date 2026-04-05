# PowerShell Script to Organize Stepwise Regression Project Files
# Run this script to copy files from old structure to new professional structure

# Set base paths
$oldBase = "c:\Users\ahusse12\OneDrive - Kent State University\Documents\Windsurf-Projects\Chloe+Abdulrahman"
$newBase = "c:\Users\ahusse12\OneDrive - Kent State University\Documents\Windsurf-Projects\Stepwise-Regression-Analysis"

# Create directory structure
Write-Host "Creating directory structure..." -ForegroundColor Green
New-Item -Path "$newBase\src" -ItemType Directory -Force | Out-Null
New-Item -Path "$newBase\examples" -ItemType Directory -Force | Out-Null
New-Item -Path "$newBase\docs" -ItemType Directory -Force | Out-Null
New-Item -Path "$newBase\tests" -ItemType Directory -Force | Out-Null

# Copy source code files
Write-Host "Copying source code files..." -ForegroundColor Green
$sourceFiles = @(
    "stepwise_vif.py",
    "preprocessing.py",
    "vif_utils.py",
    "vpca_integration.py",
    "sample_library.py",
    "plots.py",
    "__init__.py"
)

foreach ($file in $sourceFiles) {
    $sourcePath = Join-Path "$oldBase\stepwise" $file
    $destPath = Join-Path "$newBase\src" $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "  Copied: $file" -ForegroundColor Cyan
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

# Copy example notebooks
Write-Host "`nCopying example notebooks..." -ForegroundColor Green
$exampleFiles = @(
    "Stepwise-learning-Code Writing-v2.ipynb",
    "complete_tutorial.ipynb"
)

foreach ($file in $exampleFiles) {
    $sourcePath = Join-Path "$oldBase\Stepwise Regrission\Learning" $file
    $destPath = Join-Path "$newBase\examples" $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "  Copied: $file" -ForegroundColor Cyan
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

# Copy test data
Write-Host "`nCopying test data..." -ForegroundColor Green
$testFiles = @(
    "test_loadings.csv",
    "test_library.csv"
)

foreach ($file in $testFiles) {
    $sourcePath = Join-Path "$oldBase\Stepwise Regrission\Learning" $file
    $destPath = Join-Path "$newBase\tests" $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "  Copied: $file" -ForegroundColor Cyan
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

# Copy documentation
Write-Host "`nCopying documentation..." -ForegroundColor Green
$docFiles = @(
    "SPSS_Testing_Guide.md"
)

foreach ($file in $docFiles) {
    $sourcePath = Join-Path "$oldBase\Stepwise Regrission\Learning" $file
    $destPath = Join-Path "$newBase\docs" $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $destPath -Force
        Write-Host "  Copied: $file" -ForegroundColor Cyan
    } else {
        Write-Host "  Not found: $file" -ForegroundColor Yellow
    }
}

# Summary
Write-Host "`n" + "="*60 -ForegroundColor Green
Write-Host "File organization complete!" -ForegroundColor Green
Write-Host "="*60 -ForegroundColor Green

Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Review copied files in: $newBase" -ForegroundColor White
Write-Host "2. Update source code headers (see SETUP_INSTRUCTIONS.md)" -ForegroundColor White
Write-Host "3. Initialize Git repository" -ForegroundColor White
Write-Host "4. Push to GitHub" -ForegroundColor White
Write-Host "5. Create first release" -ForegroundColor White

Write-Host "`nFor detailed instructions, see:" -ForegroundColor Yellow
Write-Host "  $newBase\SETUP_INSTRUCTIONS.md" -ForegroundColor Cyan
