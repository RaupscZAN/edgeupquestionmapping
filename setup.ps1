# PowerShell setup script for Question Tagging Tool

Write-Host "Setting up Question Tagging Tool..." -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Installing required packages..." -ForegroundColor Yellow

# Install pip and upgrade
python -m ensurepip --upgrade
python -m pip install --upgrade pip

# Install requirements
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app with session persistence:" -ForegroundColor Cyan
Write-Host "  python -m streamlit run app_with_persistence.py" -ForegroundColor White
Write-Host ""
Write-Host "Or double-click run.bat" -ForegroundColor Cyan
Write-Host ""
Read-Host "Press Enter to continue"