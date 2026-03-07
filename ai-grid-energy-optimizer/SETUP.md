# 🚀 Setup & Installation Guide

## 📋 Prerequisites

- **Python 3.8+** (tested on 3.9, 3.10, 3.11)
- **Node.js 14+** (for React frontend, optional)
- **pip** (Python package manager)
- **git** (for cloning repository)

---

## ⚡ Quick Start (5 minutes)

### Option 1: Dashboard Only (Easiest)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/grid-energy-optimizer.git
cd grid-energy-optimizer

# 2. Create Python virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 5. Process data and train models
python scripts/data_processing.py
python scripts/train_models.py

# 6. Start the dashboard
streamlit run app.py
```

Your dashboard will open at: **http://localhost:8501**

---

## 🔧 Full Stack Setup (All Components)

### Step 1: Python Environment Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/grid-energy-optimizer.git
cd grid-energy-optimizer

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Verify Python version
python --version  # Should be 3.8+
```

### Step 2: Install Python Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install project dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, numpy, sklearn, streamlit, flask; print('✅ All packages installed')"
```

### Step 3: Data Processing & Model Training

```bash
# Process the raw data
python scripts/data_processing.py
# Output: data/processed_energy_data.csv

# Train the ML models
python scripts/train_models.py
# Output: models/demand_model.pkl, models/solar_model.pkl
```

**What these scripts do:**
- `data_processing.py`: Loads CSV, cleans data, engineers features
- `train_models.py`: Trains Linear Regression and Random Forest models

### Step 4: Start Services

You'll need **3 terminal windows**:

**Terminal 1 - Flask API:**
```bash
python api_server.py
# Runs on http://localhost:5000
# Check http://localhost:5000/api/health
```

**Terminal 2 - Streamlit Dashboard:**
```bash
streamlit run app.py
# Runs on http://localhost:8501
# Opens browser automatically
```

**Terminal 3 - React Frontend (Optional but Recommended):**
```bash
cd frontend
npm install
npm start
# Runs on http://localhost:3000
# Make sure backend is running on port 5000!
```

---

## 🛠️ Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pandas'"

**Solution:**
```bash
# Ensure virtual environment is activated
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Problem: "FileNotFoundError: data/energy_data.csv not found"

**Solution:**
```bash
# Check if file exists
ls data/
# or on Windows: dir data\

# If missing, the CSV should be in the repo
# If still missing, check GitHub issues or re-clone
```

### Problem: "Address already in use" on port 5000

**Solution:**
```bash
# Find what's using port 5000
# Windows: netstat -ano | findstr :5000
# Linux/Mac: lsof -i :5000

# Kill the process or use a different port:
python api_server.py --port 5001
```

### Problem: "Address already in use" on port 8501 (Streamlit)

**Solution:**
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

### Problem: Node modules installation fails in frontend

**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install --force
npm start
```

### Problem: "React components not showing up"

**Solution:**
1. Ensure backend (Flask) is running on `http://localhost:5000`
2. Create `frontend/.env` with:
   ```
   REACT_APP_API_BASE_URL=http://localhost:5000/api
   ```
3. Restart React: `npm start`

---

## 📊 Verifying Installation

Run this checklist to confirm everything works:

```bash
# 1. Check Python version
python --version
# Expected: Python 3.8 or higher

# 2. Check packages
python -c "import pandas, numpy, sklearn, streamlit, flask; print('✅')"

# 3. Check data files
ls -la data/
# Should see: energy_data.csv

# 4. Check model directory
ls -la models/
# Should be empty initially (created during training)

# 5. Try running data processing
python scripts/data_processing.py
# Should create: data/processed_energy_data.csv

# 6. Try training models
python scripts/train_models.py
# Should create: models/demand_model.pkl, models/solar_model.pkl

# 7. Test API
python api_server.py
# Check http://localhost:5000/api/health
# Expected: {"status": "healthy", "models_loaded": true}
```

---

## 🔄 Running Tests (if available)

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_data_processing.py

# With coverage
pytest --cov=. tests/
```

---

## 📁 Project Structure

```
grid-energy-optimizer/
├── data/                    # Data directory
│   ├── energy_data.csv     # Raw input data
│   └── processed_energy_data.csv  # Processed data (created by script)
├── models/                  # ML model directory
│   ├── demand_model.pkl    # Linear Regression model (created)
│   └── solar_model.pkl     # Random Forest model (created)
├── scripts/                # Python scripts
│   ├── data_processing.py
│   └── train_models.py
├── frontend/               # React frontend
│   ├── src/
│   ├── public/
│   └── package.json
├── app.py                  # Streamlit dashboard
├── api_server.py           # Flask API
├── energy_optimizer.py     # Optimization logic
├── requirements.txt        # Python dependencies
└── README.md              # Main documentation
```

---

## 🌐 Environment Variables

### Python Backend

Create `.env` in root:
```
FLASK_ENV=development
FLASK_DEBUG=False
FLASK_PORT=5000
CORS_ORIGINS=http://localhost:3000,http://localhost:8501
```

### React Frontend

Create `frontend/.env`:
```
REACT_APP_API_BASE_URL=http://localhost:5000/api
REACT_APP_ENV=development
```

---

## 🚀 Deployment

### For Production

1. Change environment variables
2. Use WSGI server instead of Flask dev server (e.g., Gunicorn)
3. Set up proper database for user management
4. Enable HTTPS
5. Use environment-specific configurations

---

## 📞 Support

- Check `TECHNICAL_REVIEW.md` for detailed issue analysis
- See `README.md` for project overview
- Check GitHub issues for common problems

---

**Last Updated:** March 7, 2026
