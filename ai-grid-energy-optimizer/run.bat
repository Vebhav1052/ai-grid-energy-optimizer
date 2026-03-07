@echo off
REM =========================================================
REM Grid Energy Optimizer - Windows Quick Start
REM =========================================================
REM This script sets up and runs the dashboard
REM =========================================================

echo.
echo    ========================================
echo    Grid Energy Optimizer
echo    Quick Start Script
echo    ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from python.org
    pause
    exit /b 1
)

echo [STEP 1] Checking dependencies...
python -m pip install -q -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [STEP 2] Checking for trained models...
if not exist "models\demand_model.pkl" (
    echo ⚠ Models not found. Training new models...
    python scripts\data_processing.py
    python scripts\train_models.py
    echo ✓ Models trained successfully
) else (
    echo ✓ Models found
)

echo.
echo [STEP 3] Launching dashboard...
echo.
echo    Opening http://localhost:8501 in your browser
echo    Press Ctrl+C to stop the server
echo.

python -m streamlit run app.py

pause
