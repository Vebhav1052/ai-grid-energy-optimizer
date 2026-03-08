#!/usr/bin/env python3
"""
Flask API Server for Grid Energy Optimizer

Provides REST endpoints for energy predictions and recommendations.
This backend serves the React frontend and integrates with the prediction models.
"""

import os
import pickle
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
from energy_optimizer import EnergyOptimizer, create_visualization_data
from weather_utils import get_weather_data, validate_weather_data
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================================
# FLASK APP INITIALIZATION
# ============================================================================

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_models():
    """Load pre-trained demand and solar generation models."""
    try:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        
        with open(os.path.join(model_dir, "demand_model.pkl"), "rb") as f:
            demand_model = pickle.load(f)
        
        with open(os.path.join(model_dir, "solar_model.pkl"), "rb") as f:
            solar_model = pickle.load(f)
        
        return demand_model, solar_model
    except FileNotFoundError as e:
        print(f"❌ Models not found: {e}")
        return None, None


# Load models on startup
DEMAND_MODEL, SOLAR_MODEL = load_models()

# ============================================================================
# USER JSON DATABASE
# ============================================================================

USERS_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")

def ensure_users_file():
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    if not os.path.isfile(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_users():
    ensure_users_file()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f)

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    models_loaded = DEMAND_MODEL is not None and SOLAR_MODEL is not None
    return jsonify({
        "status": "healthy" if models_loaded else "unhealthy",
        "models_loaded": models_loaded
    })

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    if "@" not in email or "." not in email:
        return jsonify({"success": False, "error": "Invalid email"}), 400
    users = load_users()
    if any(u.get("email") == email for u in users):
        return jsonify({"success": False, "error": "User already exists"}), 409
    hashed = generate_password_hash(password)
    users.append({"email": email, "password": hashed})
    save_users(users)
    return jsonify({"success": True})

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    data = request.json or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", "")).strip()
    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400
    users = load_users()
    user = next((u for u in users if u.get("email") == email), None)
    if not user or not check_password_hash(user.get("password", ""), password):
        return jsonify({"success": False, "error": "Invalid credentials"}), 401
    return jsonify({"success": True})


@app.route('/api/predict', methods=['POST'])
def predict_energy():
    """
    Make energy predictions based on weather conditions.
    
    Expected JSON payload:
    {
        "temperature": float,
        "cloud_cover": float (0-1),
        "humidity": float (0-100),
        "hour": int (0-23)
    }
    
    Returns:
    {
        "predicted_demand": float,
        "predicted_solar": float,
        "recommendation": {
            "action": str,
            "explanation": str,
            "energy_balance": float,
            "confidence": float,
            "color": str
        },
        "energy_balance": float,
        "surplus_or_deficit": str
    }
    """
    try:
        if DEMAND_MODEL is None or SOLAR_MODEL is None:
            return jsonify({"error": "Models not loaded"}), 503
        
        # Get input data
        data = request.json
        temperature = float(data.get('temperature', 20))
        cloud_cover = float(data.get('cloud_cover', 0.5))
        humidity = float(data.get('humidity', 60))
        hour = int(data.get('hour', 12))
        
        # Validate inputs
        if not (-10 <= temperature <= 45):
            return jsonify({"error": "Temperature out of range (-10 to 45°C)"}), 400
        if not (0 <= cloud_cover <= 1):
            return jsonify({"error": "Cloud cover must be between 0 and 1"}), 400
        if not (0 <= humidity <= 100):
            return jsonify({"error": "Humidity must be between 0 and 100"}), 400
        if not (0 <= hour <= 23):
            return jsonify({"error": "Hour must be between 0 and 23"}), 400
        
        # Prepare features
        features = np.array([[temperature, cloud_cover, humidity, hour]])
        
        # Make predictions
        predicted_demand = float(DEMAND_MODEL.predict(features)[0])
        predicted_solar = float(SOLAR_MODEL.predict(features)[0])
        
        # Ensure non-negative values
        predicted_demand = max(0, predicted_demand)
        predicted_solar = max(0, predicted_solar)
        
        # Get optimization recommendation
        optimizer = EnergyOptimizer()
        recommendation = optimizer.get_recommendation(predicted_solar, predicted_demand)
        
        # Prepare response
        energy_balance = predicted_solar - predicted_demand
        
        return jsonify({
            "success": True,
            "predicted_demand": round(predicted_demand, 2),
            "predicted_solar": round(predicted_solar, 2),
            "recommendation": {
                "action": recommendation["action"],
                "explanation": recommendation["explanation"],
                "confidence": recommendation["confidence"],
                "battery_level": round(recommendation["battery_level"], 2),
                "grid_energy_used": round(recommendation["grid_energy_used"], 2),
                "co2_emitted": round(recommendation["co2_emitted"], 2),
                "renewable_contribution": round(recommendation["renewable_contribution"], 4),
                "color": recommendation["color"]
            },
            "energy_balance": round(energy_balance, 2),
            "surplus_or_deficit": "surplus" if energy_balance > 10 else "deficit" if energy_balance < -10 else "balanced",
            "grid_status": optimizer.get_grid_status(predicted_solar, predicted_demand)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/hourly-patterns', methods=['GET'])
def get_hourly_patterns():
    """
    Get 24-hour energy patterns for visualization.
    
    Returns:
    {
        "hours": [0, 1, 2, ...],
        "solar_pattern": [values...],
        "demand_pattern": [values...],
        "description": "Description of typical daily patterns"
    }
    """
    try:
        hours = np.arange(0, 24)
        
        # Create realistic hourly patterns
        # Solar generation peaks around noon
        solar_pattern = np.maximum(0, 200 * np.sin((hours - 6) * np.pi / 12))
        # Demand has two peaks (morning and evening)
        demand_pattern = 100 + 50 * np.cos((hours - 12) * np.pi / 12) + 30 * np.sin((hours - 18) * np.pi / 6)
        
        return jsonify({
            "success": True,
            "hours": [int(h) for h in hours],
            "solar_pattern": [float(round(v, 2)) for v in solar_pattern],
            "demand_pattern": [float(round(v, 2)) for v in demand_pattern],
            "description": "Typical 24-hour energy patterns: Solar peaks at midday (11 AM - 3 PM); Demand peaks in morning (7-9 AM) and evening (6-8 PM)"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/recommendations-guide', methods=['GET'])
def get_recommendations_guide():
    """Get explanation of all possible recommendations."""
    return jsonify({
        "success": True,
        "recommendations": [
            {
                "emoji": "🔋",
                "action": "Store in Battery",
                "scenario": "Solar > Demand + 10 MW",
                "rationale": "Capture excess renewable energy for later use",
                "color": "green"
            },
            {
                "emoji": "🔌",
                "action": "Use Battery Backup",
                "scenario": "Solar < Demand - 10 MW, Battery OK",
                "rationale": "Minimize grid strain, use stored clean energy",
                "color": "orange"
            },
            {
                "emoji": "🏭",
                "action": "Use Grid Backup",
                "scenario": "Insufficient Solar & Low Battery",
                "rationale": "Draw from grid when no other option available",
                "color": "red"
            },
            {
                "emoji": "⚖️",
                "action": "Balanced Grid",
                "scenario": "Solar ≈ Demand",
                "rationale": "Monitor and maintain steady state",
                "color": "blue"
            }
        ]
    })


@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """Get information about the ML models."""
    return jsonify({
        "success": True,
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
    })


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get system settings and limits."""
    return jsonify({
        "success": True,
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
    })


@app.route('/energy-plan', methods=['POST'])
def generate_energy_plan():
    """
    Generate a smart energy plan based on city and required energy.

    Expected JSON payload:
    {
        "city": str (e.g., "Delhi", "London", "New York"),
        "required_energy": float (MW) - target energy requirement
    }

    Returns:
    {
        "success": bool,
        "predicted_demand": float,
        "solar_generation": float,
        "battery_usage": float,
        "grid_usage": float,
        "status": str,
        "weather_data": dict,
        "recommendation": dict
    }
    """
    try:
        if DEMAND_MODEL is None or SOLAR_MODEL is None:
            return jsonify({
                "success": False,
                "error": "ML models not loaded. Please ensure models are trained and available."
            }), 503

        # Get input data
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400

        city = data.get('city', '').strip()
        required_energy = data.get('required_energy', 0)

        # Validate inputs
        if not city:
            return jsonify({
                "success": False,
                "error": "City name is required"
            }), 400

        if not isinstance(required_energy, (int, float)) or required_energy <= 0:
            return jsonify({
                "success": False,
                "error": "Required energy must be a positive number"
            }), 400

        # Step 1: Fetch weather data
        weather_data = get_weather_data(city)
        if not weather_data or not validate_weather_data(weather_data):
            return jsonify({
                "success": False,
                "error": f"Could not fetch weather data for city: {city}"
            }), 400

        # Extract weather parameters
        temperature = weather_data["temperature"]
        cloud_cover = weather_data["cloud_cover"] / 100.0  # Convert to 0-1 scale
        humidity = weather_data["humidity"]

        # Use current hour (simplified - in production, you'd get actual current hour)
        # For demo purposes, we'll use a reasonable hour like 14 (2 PM)
        current_hour = 14

        # Step 2: Make ML predictions
        features = np.array([[temperature, cloud_cover, humidity, current_hour]])

        predicted_demand = float(DEMAND_MODEL.predict(features)[0])
        predicted_solar = float(SOLAR_MODEL.predict(features)[0])

        # Ensure non-negative values
        predicted_demand = max(0, predicted_demand)
        predicted_solar = max(0, predicted_solar)

        # Step 3: Run EnergyOptimizer logic
        optimizer = EnergyOptimizer()
        recommendation = optimizer.get_recommendation(predicted_solar, predicted_demand)

        # Step 4: Calculate energy plan components
        energy_balance = predicted_solar - predicted_demand
        grid_energy_used = recommendation["grid_energy_used"]

        # Calculate battery usage
        battery_usage = 0.0
        if energy_balance > 0:
            # Surplus: charging battery
            battery_usage = min(energy_balance, optimizer.battery_capacity - recommendation["battery_level"])
        elif energy_balance < 0:
            # Deficit: using battery
            deficit = -energy_balance
            battery_usage = min(deficit, recommendation["battery_level"])

        # Prepare response
        energy_plan = {
            "success": True,
            "predicted_demand": round(predicted_demand, 2),
            "solar_generation": round(predicted_solar, 2),
            "battery_usage": round(battery_usage, 2),
            "grid_usage": round(grid_energy_used, 2),
            "status": "Energy Plan Ready",
            "weather_data": {
                "city": weather_data["city"],
                "country": weather_data["country"],
                "temperature": round(temperature, 1),
                "humidity": humidity,
                "cloud_cover": weather_data["cloud_cover"]
            },
            "recommendation": {
                "action": recommendation["action"],
                "explanation": recommendation["explanation"],
                "confidence": round(recommendation["confidence"], 2),
                "energy_balance": round(energy_balance, 2),
                "renewable_contribution": round(recommendation["renewable_contribution"], 4),
                "co2_emitted": round(recommendation["co2_emitted"], 2)
            },
            "optimization_details": {
                "battery_level_after": round(recommendation["battery_level"], 2),
                "battery_capacity": optimizer.battery_capacity,
                "energy_surplus_deficit": round(energy_balance, 2)
            }
        }

        return jsonify(energy_plan), 200

    except Exception as e:
        print(f"Error generating energy plan: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route('/execute-plan', methods=['POST'])
def execute_energy_plan():
    """
    Simulate execution of an energy plan by sending commands to power plant controllers.

    Expected JSON payload:
    {
        "solar": float (MW) - Solar generation target,
        "battery": float (MW) - Battery usage target,
        "grid": float (MW) - Grid backup target
    }

    Returns:
    {
        "success": bool,
        "status": str,
        "solar_generation": str,
        "battery_storage": str,
        "grid_backup": str,
        "execution_id": str,
        "timestamp": str
    }
    """
    try:
        # Get input data
        data = request.json
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400

        solar = data.get('solar', 0)
        battery = data.get('battery', 0)
        grid = data.get('grid', 0)

        # Validate inputs
        if not isinstance(solar, (int, float)) or solar < 0:
            return jsonify({
                "success": False,
                "error": "Solar value must be a non-negative number"
            }), 400

        if not isinstance(battery, (int, float)) or battery < 0:
            return jsonify({
                "success": False,
                "error": "Battery value must be a non-negative number"
            }), 400

        if not isinstance(grid, (int, float)) or grid < 0:
            return jsonify({
                "success": False,
                "error": "Grid value must be a non-negative number"
            }), 400

        # Simulate plant control commands
        import time
        execution_id = f"EXEC-{int(time.time())}"

        # Determine status based on values
        solar_status = "Activated" if solar > 0 else "Standby"
        battery_status = "Charging" if battery > 0 else "Standby"
        grid_status = "Active" if grid > 0 else "Standby"

        # Simulate some processing time (for realism)
        time.sleep(0.5)

        execution_result = {
            "success": True,
            "status": "Execution Started",
            "solar_generation": solar_status,
            "battery_storage": battery_status,
            "grid_backup": grid_status,
            "execution_id": execution_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "targets": {
                "solar_target": round(solar, 2),
                "battery_target": round(battery, 2),
                "grid_target": round(grid, 2)
            },
            "message": f"Energy plan execution initiated. Commands sent to plant controllers."
        }

        return jsonify(execution_result), 200

    except Exception as e:
        print(f"Error executing energy plan: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Grid Energy Optimizer - API Server")
    print("=" * 70)
    
    if DEMAND_MODEL and SOLAR_MODEL:
        print("✅ Models loaded successfully")
    else:
        print("⚠️ Warning: Models not loaded. Run: python scripts/train_models.py")
    
    print("\n🚀 Starting API server on http://localhost:5000")
    print("📚 API Documentation: http://localhost:5000/api/")
    print("\nAvailable endpoints:")
    print("  GET  /api/health                 - Health check")
    print("  POST /api/auth/register          - Register user")
    print("  POST /api/auth/login             - Login user")
    print("  POST /api/predict                - Make predictions")
    print("  GET  /api/hourly-patterns        - Get 24-hour patterns")
    print("  GET  /api/recommendations-guide - Get recommendation info")
    print("  GET  /api/model-info             - Get model details")
    print("  GET  /api/settings               - Get system settings")
    print("  POST /energy-plan                - Generate smart energy plan")
    print("  POST /execute-plan               - Execute energy plan simulation")
    print("=" * 70 + "\n")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
