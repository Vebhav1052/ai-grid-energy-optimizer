# 🔌 API Documentation

**Base URL:** `http://localhost:5000/api`

---

## 📊 Endpoints

### 1. **Health Check**

```
GET /api/health
```

**Description:** Check if the API is running and models are loaded.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

**Status Codes:**
- `200`: API is healthy and ready
- `503`: API is running but models not loaded

---

### 2. **Energy Prediction**

```
POST /api/predict
Content-Type: application/json
```

**Description:** Get energy predictions and optimization recommendations.

**Request Body:**
```json
{
  "temperature": 20.5,
  "cloud_cover": 0.6,
  "humidity": 65,
  "hour": 14
}
```

**Parameters:**
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `temperature` | float | -10 to 45 | Temperature in Celsius |
| `cloud_cover` | float | 0 to 1 | Cloud cover (0=clear, 1=overcast) |
| `humidity` | float | 0 to 100 | Relative humidity % |
| `hour` | int | 0 to 23 | Hour of day |

**Response:**
```json
{
  "success": true,
  "predicted_demand": 185.5,
  "predicted_solar": 120.3,
  "recommendation": {
    "action": "🔌 Use Battery Backup",
    "explanation": "Demand (185.5 MW) exceeds solar (120.3 MW). Battery at 60%. Use 65.2 MW from battery.",
    "energy_balance": -65.2,
    "confidence": 0.90,
    "color": "orange",
    "emoji": "🔋"
  },
  "energy_balance": -65.2,
  "surplus_or_deficit": "deficit"
}
```

**Error Responses:**
```json
// Models not loaded
{
  "error": "Models not loaded"
}
// Status: 503

// Invalid input
{
  "error": "Temperature out of range (-10 to 45°C)"
}
// Status: 400

// Server error
{
  "error": "Internal server error"
}
// Status: 500
```

---

### 3. **Hourly Patterns**

```
GET /api/hourly-patterns
```

**Description:** Get typical 24-hour energy generation and demand patterns.

**Response:**
```json
{
  "success": true,
  "hours": [0, 1, 2, ..., 23],
  "solar_pattern": [0.0, 0.0, 0.0, ..., 50.2],
  "demand_pattern": [100.0, 95.0, 90.0, ..., 120.5],
  "description": "Typical 24-hour energy patterns..."
}
```

---

### 4. **Recommendations Guide**

```
GET /api/recommendations-guide
```

**Description:** Get explanation of all possible recommendations.

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "emoji": "🔋",
      "action": "Store in Battery",
      "scenario": "Solar > Demand + 10 MW",
      "rationale": "Capture excess renewable energy for later use",
      "color": "green"
    },
    ...
  ]
}
```

---

### 5. **Model Information**

```
GET /api/model-info
```

**Description:** Get details about the trained ML models.

**Response:**
```json
{
  "success": true,
  "models": {
    "demand": {
      "algorithm": "Linear Regression",
      "features": ["Temperature", "Cloud Cover", "Humidity", "Hour"],
      "target": "Electricity Demand (MW)",
      "expected_r2": 0.97,
      "training_samples": "Historical energy data"
    },
    "solar": {
      "algorithm": "Random Forest (100 trees)",
      "features": ["Temperature", "Cloud Cover", "Humidity", "Hour"],
      "target": "Solar Generation (MW)",
      "expected_r2": 0.57,
      "training_samples": "Historical solar data"
    }
  }
}
```

---

### 6. **System Settings**

```
GET /api/settings
```

**Description:** Get system configuration and limits.

**Response:**
```json
{
  "success": true,
  "settings": {
    "battery_capacity": 500,
    "temperature_range": [-10, 45],
    "cloud_cover_range": [0, 1],
    "humidity_range": [0, 100],
    "hours_range": [0, 23],
    "energy_surplus_threshold": 10,
    "energy_deficit_threshold": -10,
    "minimum_battery_for_backup": 20
  }
}
```

---

### 7. **User Registration**

```
POST /api/auth/register
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true
}
```

**Error Cases:**
```json
{
  "success": false,
  "error": "Email and password are required"
}
// Status: 400

{
  "success": false,
  "error": "Invalid email"
}
// Status: 400

{
  "success": false,
  "error": "User already exists"
}
// Status: 409
```

---

### 8. **User Login**

```
POST /api/auth/login
Content-Type: application/json
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "success": true
}
```

**Error Cases:**
```json
{
  "success": false,
  "error": "Invalid credentials"
}
// Status: 401
```

---

## 📞 Usage Examples

### Using cURL

```bash
# Check API health
curl http://localhost:5000/api/health

# Make a prediction
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"temperature": 20, "cloud_cover": 0.5, "humidity": 60, "hour": 14}'

# Get hourly patterns
curl http://localhost:5000/api/hourly-patterns
```

### Using Python

```python
import requests
import json

API_BASE = "http://localhost:5000/api"

# Check health
response = requests.get(f"{API_BASE}/health")
print(response.json())

# Make prediction
data = {
    "temperature": 20,
    "cloud_cover": 0.5,
    "humidity": 60,
    "hour": 14
}
response = requests.post(f"{API_BASE}/predict", json=data)
result = response.json()
print(json.dumps(result, indent=2))
```

### Using JavaScript/Fetch

```javascript
const API_BASE = "http://localhost:5000/api";

// Make prediction
const data = {
  temperature: 20,
  cloud_cover: 0.5,
  humidity: 60,
  hour: 14
};

fetch(`${API_BASE}/predict`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(data)
})
.then(res => res.json())
.then(result => console.log(result));
```

---

## ⚠️ Error Handling

All errors include appropriate HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad Request (invalid input) |
| 401 | Unauthorized (invalid credentials) |
| 404 | Endpoint not found |
| 409 | Conflict (user already exists) |
| 500 | Server error |
| 503 | Service unavailable (models not loaded) |

---

## 🔒 CORS Configuration

The API enables CORS for the following origins by default:
- `http://localhost:3000` (React development)
- `http://localhost:8501` (Streamlit)

To add more origins, modify `api_server.py`:
```python
CORS(app, origins=['http://localhost:3000', 'http://yourdomain.com'])
```

---

## 📈 Rate Limiting

Currently **not implemented**. For production, add rate limiting:
```python
from flask_limiter import Limiter
limiter = Limiter(app, key_func=lambda: request.remote_addr)
@app.route('/api/predict')
@limiter.limit("10 per minute")
def predict_energy():
    # ...
```

---

## 🔑 Authentication

Currently using **basic email/password authentication** stored in JSON.

**⚠️ For production:**
- Use JWT tokens
- Implement proper password hashing (argon2 or bcrypt)
- Use a database (PostgreSQL or SQLite)
- Add token expiration and refresh

---

## 📊 Data Validation

All inputs are validated before processing:

```python
# Temperature: -10 to 45°C
# Cloud Cover: 0 to 1
# Humidity: 0 to 100%
# Hour: 0 to 23
```

---

**Last Updated:** March 7, 2026
