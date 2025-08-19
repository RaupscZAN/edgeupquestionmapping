@echo off
echo Setting up Question Tagging Tool...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python is installed.
echo.

REM Install pip if needed
python -m ensurepip --upgrade

REM Install requirements
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo Setup complete! You can now run the app with:
echo python -m streamlit run app_with_persistence.py
echo.
echo Or use the included run.bat file.
pause