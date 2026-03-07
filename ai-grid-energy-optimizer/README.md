# ⚡ Grid Energy Optimizer

> **A hackathon project for renewable energy management in power grids**

## 🎯 Project Overview

This project implements a system that:
- **Predicts** electricity demand and solar generation using statistical models
- **Optimizes** energy distribution across multiple sources (solar, battery, grid)
- **Visualizes** energy metrics through interactive dashboards
- **Recommends** real-time grid actions to minimize costs and maximize renewable usage

Built by a team of 4 students in 18 hours for a renewable energy hackathon. ✨

---

## 🚀 Quick Start (5 minutes)

```bash
# 1. Clone and navigate
git clone https://github.com/yourusername/grid-energy-optimizer.git
cd grid-energy-optimizer

# 2. Create Python environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train models (first time only)
python scripts/data_processing.py
python scripts/train_models.py

# 5. Launch dashboard
streamlit run app.py
```

**Opens automatically at:** `http://localhost:8501`

---

## 📖 Documentation

- **[SETUP.md](SETUP.md)** — Detailed installation & troubleshooting guide
- **[API.md](API.md)** — Complete Flask API documentation
- **[TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md)** — Full technical analysis and best practices

---

## 🏗️ Architecture

```
grid-energy-optimizer/
├── data/                            # Data directory
│   ├── energy_data.csv             # Raw historical data
│   └── processed_energy_data.csv   # Processed (created)
├── models/                          # ML models
│   ├── demand_model.pkl            # Linear Regression
│   └── solar_model.pkl             # Random Forest
├── scripts/
│   ├── data_processing.py          # ETL pipeline
│   └── train_models.py             # Model training
├── frontend/                        # React UI (optional)
│   ├── src/
│   ├── public/
│   └── package.json
├── app.py                          # Streamlit dashboard
├── api_server.py                   # Flask REST API
├── energy_optimizer.py             # Optimization logic
└── requirements.txt                # Python dependencies
```

### 📊 Data Pipeline

```
Raw CSV
  ↓
[Data Processing]
  ↓
Processed Features
  ↓
[Model Training]
  ↓
Trained Models
  ↓
[Live Predictions]
  ↓
[Grid Optimization]
  ↓
Dashboard
```

---

## 🖥️ Running All Components

### **Option 1: Dashboard Only** (Easiest)
```bash
python scripts/data_processing.py
python scripts/train_models.py
streamlit run app.py   # http://localhost:8501
```

### **Option 2: Full Stack** (Backend + Dashboard)

**Terminal 1 - Flask API:**
```bash
python api_server.py   # http://localhost:5000/api
```

**Terminal 2 - Streamlit:**
```bash
streamlit run app.py   # http://localhost:8501
```

### **Option 3: Complete** (All 3 services)

**Terminal 1:**
```bash
python api_server.py
```

**Terminal 2:**
```bash
streamlit run app.py
```

**Terminal 3:**
```bash
cd frontend
npm install
npm start   # http://localhost:3000
```

---

## 🎮 Using the Dashboard

### Input Parameters (Left Panel)
- 🌡️ **Temperature** (-10 to 45°C)
- ☁️ **Cloud Cover** (0 = clear, 1 = overcast)
- 💧 **Humidity** (0-100%)
- 🕐 **Hour** (0-23)

### Outputs (Right Panel)
- ⚡ **Predicted Demand** (MW)
- ☀️ **Predicted Solar** (MW)
- 🎯 **Recommendation** with confidence

### Actions
1. Adjust sliders for your scenario
2. **Auto-fetch weather data** by city name (optional)
3. Click "📊 Generate Prediction"
4. View results and recommendations
5. **Execute Energy Plan** to simulate plant control
6. Download results as CSV

---

## 📈 Prediction Models

| Model | Algorithm | Features | Target | Accuracy |
|-------|-----------|----------|--------|----------|
| **Demand** | Linear Regression | Temp, clouds, humidity, hour | Electricity demand | R² ≈ 0.97 |
| **Solar** | Random Forest (100 trees) | Temp, clouds, humidity, hour | Solar generation | R² ≈ 0.57 |

---

## 💡 Energy Optimization Logic

The system recommends one of four actions:

| Scenario | Action | Icon | Color |
|----------|--------|------|-------|
| Solar > Demand + 10 MW | Store in Battery | 🔋 | Green |
| Solar < Demand - 10 MW (battery OK) | Use Battery Backup | 🔌 | Orange |
| Insufficient (battery low) | Use Grid Backup | 🏭 | Red |
| Balanced | Monitor Grid | ⚖️ | Blue |

### Strategy
1. Maximize renewable energy usage
2. Use battery as buffer
3. Minimize grid dependency
4. Reduce energy costs

---

## 🛠️ API Endpoints

All endpoints at `http://localhost:5000/api`:

```bash
GET  /health              # Check API status
POST /predict             # Get predictions
GET  /hourly-patterns    # 24-hour patterns
GET  /model-info         # Model details
GET  /settings           # System settings
POST /auth/register      # Register user
POST /auth/login         # Login user
POST /energy-plan        # Generate smart energy plan
POST /execute-plan       # Execute energy plan simulation
```

See [API.md](API.md) for complete documentation.

---

## 📋 Project Features

✅ **Data Pipeline**
- CSV data loading and validation
- Automatic feature engineering
- Train/test splitting

✅ **Machine Learning**
- Two prediction models (demand & solar)
- Model evaluation metrics
- Pickle serialization

✅ **Optimization**
- Decision logic based on energy balance
- Battery management
- Grid load optimization

✅ **Dashboards**
- Interactive Streamlit UI
- Real-time predictions
- Energy visualizations
- Download results

✅ **API**
- RESTful Flask backend
- User authentication
- CORS enabled
- Error handling

✅ **Frontend** (Optional)
- React with React Router
- Tailwind CSS styling
- API integration
- Responsive design

---

## 🔧 Requirements

- **Python:** 3.8+ (tested on 3.9, 3.10, 3.11)
- **Node.js:** 14+ (for React frontend, optional)
- **RAM:** 2+ GB
- **Disk:** 500 MB (with models)

**Python Packages:**
- pandas, numpy, scikit-learn
- streamlit, flask
- plotly, matplotlib

See [requirements.txt](requirements.txt) for full list.

---

## 🚨 Troubleshooting

**Models not loading?**
```bash
python scripts/data_processing.py
python scripts/train_models.py
```

**Port already in use?**
```bash
streamlit run app.py --server.port 8502
python api_server.py --port 5001
```

**API not found?**
```bash
# Ensure backend is running
python api_server.py
# Check: http://localhost:5000/api/health
```

See [SETUP.md](SETUP.md) for more troubleshooting tips.

---

## 📊 Project Statistics

- **Lines of Code:** 2,000+
- **Core Models:** 2 (demand, solar)
- **API Endpoints:** 8
- **Dashboard Visualizations:** 3
- **Data Features:** 10+
- **Development Time:** 18 hours

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the MIT License.

---

## 👥 Team

Built during a renewable energy hackathon by a team of 4 students.

---

## 🙏 Acknowledgments

- Real-world energy data concepts
- scikit-learn for ML models
- Streamlit for rapid UI prototyping
- Flask for backend API
- React + Tailwind for frontend

---

## 📞 Support

- **Issues:** Open a GitHub issue
- **Documentation:** See [SETUP.md](SETUP.md) and [API.md](API.md)
- **Technical Details:** See [TECHNICAL_REVIEW.md](TECHNICAL_REVIEW.md)

---

**Last Updated:** March 7, 2026  
**Status:** ✅ Production Ready
   - Energy balance chart
   - 24-hour forecast pattern

---

## 📈 Prediction Models

### Demand Prediction
- **Algorithm**: Linear Regression
- **Features**: Temperature, Cloud Cover, Humidity, Hour
- **Target**: Electricity Demand (MW)
- **R² Score**: ~0.97 (excellent fit!)

### Solar Generation Prediction
- **Algorithm**: Random Forest (100 trees)
- **Features**: Temperature, Cloud Cover, Humidity, Hour
- **Target**: Solar Generation (MW)
- **R² Score**: ~0.57 (room for improvement with more data)

---

## 💡 Optimization Logic

The `EnergyOptimizer` recommends one of four actions:

| Scenario | Action | Rationale |
|----------|--------|-----------|
| Solar > Demand + 10 MW | 🔋 Store in Battery | Capture excess renewable energy |
| Solar < Demand - 10 MW, Battery OK | 🔌 Use Battery Backup | Minimize grid strain, use stored clean energy |
| Insufficient Solar & Low Battery | 🏭 Use Grid Backup | Draw from grid when no other option |
| Balanced | ⚖️ Balanced Grid | Monitor & maintain steady state |

---

## 📈 Key Insights

- **Peak Solar Hours**: Generation highest 11 AM - 3 PM
- **Peak Demand Hours**: Morning (7-9 AM) and Evening (6-8 PM)
- **Battery Critical**: During evening peak when solar generation drops
- **Grid Balance**: Hour of day is the most important predictor

---

## 📁 File Descriptions

### `scripts/data_processing.py`
Handles raw data → model-ready data transformation:
- Loads CSV energy data
- Handles missing values
- Engineers temporal features (hour, day, month)
- Splits data train/test
- Saves processed data

### `scripts/train_models.py`
Trains two separate prediction models:
- Linear Regression for demand forecasting
- Random Forest for solar generation
- Evaluates with MAE, RMSE, R²
- Saves trained models as pickle files

### `energy_optimizer.py`
Core optimization engine:
- `EnergyOptimizer` class with decision logic
- `get_recommendation()` method for grid actions
- Returns action, explanation, confidence, and energy balance

### `app.py`
Interactive dashboard built with Streamlit:
- User input interface
- Model loading and prediction
- Real-time recommendations
- Energy visualizations
- Session state management

---

## 🔧 Technologies Used

| Component | Technology |
|-----------|-----------|
| **Prediction Algorithms** | scikit-learn |
| **Data Processing** | pandas, numpy |
| **Visualization** | matplotlib |
| **Dashboard** | Streamlit |
| **Model Storage** | pickle |

---

## 📊 Example Output

```
Input: Temperature 25°C, Cloud Cover 50%, Humidity 60%, Hour 12 (noon)

Output:
├─ Predicted Demand: 145.2 MW
├─ Predicted Solar: 182.5 MW
├─ Surplus Energy: +37.3 MW
├─ Recommendation: 🔋 Store in Battery
└─ Confidence: 95%
```

---

## 🎓 What We Learned

1. **Time Management**: Cut features to essentials, kept code simple
2. **Feature Selection**: Hour of day > weather for grid optimization
3. **Model Choice**: Linear models fast, Random Forest flexible (but slower)
4. **Dashboard Design**: Streamlit = minimal code, maximum impact
5. **Hackathon Tip**: Focus on core logic, not perfect engineering

---

## 🚀 Future Improvements

- [ ] Add weather forecasting API integration
- [ ] Include real electricity price data
- [ ] Implement neural networks for better solar prediction
- [ ] Add battery degradation modeling
- [ ] Deploy as web API for grid operators
- [ ] Real-time notifications for grid stress events
- [ ] Historical performance analytics

---

## 👥 Team Credits

**Built by**: 4 students  
**Time**: 18 hours  
**Event**: Renewable Energy Hackathon  
**Focus**: Speed, simplicity, and impact

---

## 📝 License

Open source for educational and hackathon use.

---

## 🤝 How to Contribute

1. Add more training data (historical energy records)
2. Improve model accuracy
3. Add more optimization strategies
4. Enhance dashboard UI/UX
5. Deploy to cloud platform

**Questions?** Check the code comments - they explain the workflow!

---

**Made with ❤️ by the renewable energy team**
