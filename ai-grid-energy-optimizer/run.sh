#!/bin/bash

# =========================================================
# Grid Energy Optimizer - Linux/Mac Quick Start
# =========================================================
# This script sets up and runs the dashboard
# =========================================================

echo ""
echo "    ========================================"
echo "    Grid Energy Optimizer"
echo "    Quick Start Script"
echo "    ========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ from python.org"
    exit 1
fi

echo "[STEP 1] Checking dependencies..."
python3 -m pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✓ Dependencies installed"

echo ""
echo "[STEP 2] Checking for trained models..."
if [ ! -f "models/demand_model.pkl" ]; then
    echo "⚠ Models not found. Training new models..."
    python3 scripts/data_processing.py
    python3 scripts/train_models.py
    echo "✓ Models trained successfully"
else
    echo "✓ Models found"
fi

echo ""
echo "[STEP 3] Launching dashboard..."
echo ""
echo "    Opening http://localhost:8501 in your browser"
echo "    Press Ctrl+C to stop the server"
echo ""

python3 -m streamlit run app.py
