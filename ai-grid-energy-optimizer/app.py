#!/usr/bin/env python3
"""
Grid Energy Optimizer - Interactive Dashboard

This is the main entry point for the hackathon prototype.

Features:
- Input weather and time parameters
- Predict electricity demand and solar generation
- Get recommended grid actions
- View energy balance visualizations

Built with Streamlit for rapid prototyping with minimal dependencies.
Perfect for demo presentations and quick iterations!
"""

import os
import sys
import subprocess
import pickle
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import json
import requests
from energy_optimizer import EnergyOptimizer, create_visualization_data
from weather_utils import get_weather_data, validate_weather_data

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title=" AI Grid Energy Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None

# Load users from JSON
def load_users():
    users_file = os.path.join(os.path.dirname(__file__), "data", "users.json")
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
            if not users:  # If empty, add default admin
                users = [{"username": "admin", "password": "admin", "role": "admin"}]
                save_users(users)
            return users
    return [{"username": "admin", "password": "admin", "role": "admin"}]

def save_users(users):
    users_file = os.path.join(os.path.dirname(__file__), "data", "users.json")
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=4)

# st.markdown("""
#     <style>
#         :root { --accent:#6b7cff; --bg1:#0f1223; --bg2:#1b1f3b; }
#         html, body { background: linear-gradient(120deg, var(--bg1), var(--bg2)); animation: bgShift 18s ease-in-out infinite alternate; }
#         @keyframes bgShift { 0%{background-position:0% 50%} 100%{background-position:100% 50%} }
#         .gradient-text { background: linear-gradient(90deg,#66f,#9cf,#6cf,#59f); -webkit-background-clip:text; background-clip:text; color: transparent; animation: hue 12s linear infinite; }
#         @keyframes hue { 0%{filter:hue-rotate(0deg)} 100%{filter:hue-rotate(360deg)} }
#         .recommendation-card { 
#             border-radius: 14px; 
#             padding: 18px; 
#             color: white; 
#             background: radial-gradient(120% 120% at 0% 0%, rgba(255,255,255,0.08), transparent), linear-gradient(135deg, var(--accent), rgba(255,255,255,0.05));
#             box-shadow: 0 0 0 0 rgba(255,255,255,0.2);
#             animation: pulseGlow 3s ease-in-out infinite;
#         }
#         @keyframes pulseGlow {
#             0% { box-shadow: 0 0 0 0 rgba(255,255,255,0.18); transform: translateZ(0); }
#             50% { box-shadow: 0 0 24px 6px rgba(255,255,255,0.25); transform: translateZ(0.0001px); }
#             100% { box-shadow: 0 0 0 0 rgba(255,255,255,0.18); transform: translateZ(0); }
#         }
#         .stButton>button { 
#             transition: transform .2s ease, box-shadow .2s ease, background .3s ease; 
#             background: linear-gradient(135deg,#4f46e5,#7c3aed);
#             color: #fff;
#         }
#         .stButton>button:hover { transform: translateY(-2px) scale(1.01); box-shadow: 0 10px 24px rgba(0,0,0,0.25); }
#         .stProgress>div>div { background: repeating-linear-gradient(135deg, #22c55e, #22c55e 10px, #16a34a 10px, #16a34a 20px); }
#         .panel { border-radius: 12px; padding: 16px; background: rgba(255,255,255,0.06); backdrop-filter: blur(6px); }
#     </style>
# """, unsafe_allow_html=True)

# ============================================================================
# AUTHENTICATION FUNCTIONS
# ============================================================================

def show_login():
    st.title("🔐 Login to Grid Energy Optimizer")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            users = load_users()
            for user in users:
                if user['username'] == username and user['password'] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.role = user.get('role', 'user')
                    st.success("Login successful! Redirecting to dashboard...")
                    st.rerun()
            st.error("Invalid username or password")
    
    with tab2:
        st.subheader("Sign Up")
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.button("Sign Up", key="signup_btn"):
            if new_password != confirm_password:
                st.error("Passwords do not match")
                return
            if not new_username or not new_password:
                st.error("Please fill all fields")
                return
            
            users = load_users()
            if any(user['username'] == new_username for user in users):
                st.error("Username already exists")
                return
            
            new_user = {
                "username": new_username,
                "password": new_password,
                "role": "user"
            }
            users.append(new_user)
            save_users(users)
            st.success("Account created successfully! Please login.")
            st.rerun()
    
    return

# ============================================================================
# ADMIN DASHBOARD
# ============================================================================

def show_admin_dashboard():
    st.markdown("---")
    st.subheader("👑 Admin Dashboard")
    st.markdown("### User Management")
    
    users = load_users()
    
    if users:
        st.write("Current Users:")
        for i, user in enumerate(users):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{user['username']}** ({user.get('role', 'user')})")
            with col2:
                if user['username'] != 'admin':  # Prevent deleting admin
                    if st.button(f"Delete {user['username']}", key=f"delete_{i}"):
                        users.pop(i)
                        save_users(users)
                        st.success(f"Deleted user {user['username']}")
                        # st.rerun()  # Commented out to prevent crash
            with col3:
                if user['username'] != 'admin':
                    new_role = st.selectbox(f"Role for {user['username']}", ['user', 'admin'], index=0 if user.get('role', 'user') == 'user' else 1, key=f"role_{i}")
                    if new_role != user.get('role', 'user'):
                        user['role'] = new_role
                        save_users(users)
                        st.success(f"Updated role for {user['username']}")
    else:
        st.write("No users found.")

# ============================================================================
# LOAD MODEL FUNCTIONS
# ============================================================================

@st.cache_resource
def load_models():
    """
    Load pre-trained demand and solar generation models.
    
    The models were trained on historical weather data and energy usage.
    Cached to avoid reloading on every interaction.
    """
    try:
        model_dir = os.path.join(os.path.dirname(__file__), "models")
        
        with open(os.path.join(model_dir, "demand_model.pkl"), "rb") as f:
            demand_model = pickle.load(f)
        
        with open(os.path.join(model_dir, "solar_model.pkl"), "rb") as f:
            solar_model = pickle.load(f)
        
        return demand_model, solar_model
    except FileNotFoundError:
        try:
            scripts_dir = os.path.join(os.path.dirname(__file__), "scripts")
            data_path = os.path.join(os.path.dirname(__file__), "data", "energy_data.csv")
            
            # Check if input data exists
            if not os.path.exists(data_path):
                st.error(f"❌ Input data not found at: {data_path}\n"
                        "Please ensure 'data/energy_data.csv' exists.")
                st.stop()
            
            st.info("🔄 Training models (this may take a minute)...")
            
            result = subprocess.run(
                [sys.executable, os.path.join(scripts_dir, "data_processing.py")],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                st.error(f"❌ Data processing failed:\n{result.stderr}")
                st.stop()
            
            result = subprocess.run(
                [sys.executable, os.path.join(scripts_dir, "train_models.py")],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode != 0:
                st.error(f"❌ Model training failed:\n{result.stderr}")
                st.stop()
            
            model_dir = os.path.join(os.path.dirname(__file__), "models")
            with open(os.path.join(model_dir, "demand_model.pkl"), "rb") as f:
                demand_model = pickle.load(f)
            with open(os.path.join(model_dir, "solar_model.pkl"), "rb") as f:
                solar_model = pickle.load(f)
            
            st.success("✅ Models trained and loaded successfully!")
            return demand_model, solar_model
            
        except subprocess.TimeoutExpired:
            st.error("❌ Model training timed out (exceeded 5 minutes). "
                    "Check your data or system resources.")
            st.stop()
        except Exception as ex:
            st.error(f"❌ Failed to load or train models: {ex}\n\n"
                    "Troubleshooting:\n"
                    "1. Ensure energy_data.csv exists in /data\n"
                    "2. Check that all required columns exist\n"
                    "3. Try running scripts manually:\n"
                    "   python scripts/data_processing.py\n"
                    "   python scripts/train_models.py")
            st.stop()


# ============================================================================
# PREDICTION FUNCTIONS
# ============================================================================

def predict_energy(temperature, cloud_cover, humidity, hour, models):
    """
    Make predictions for electricity demand and solar generation.
    
    Args:
        temperature: Temperature in Celsius
        cloud_cover: Cloud cover percentage (0-1)
        humidity: Humidity percentage (0-100)
        hour: Hour of day (0-23)
        models: Tuple of (demand_model, solar_model)
    
    Returns:
        Tuple of (predicted_demand, predicted_solar)
    """
    demand_model, solar_model = models
    
    # Prepare features in the same order used during training
    features = np.array([[temperature, cloud_cover, humidity, hour]])
    
    # Make predictions
    predicted_demand = demand_model.predict(features)[0]
    predicted_solar = solar_model.predict(features)[0]
    
    # Ensure non-negative values
    predicted_demand = max(0, predicted_demand)
    predicted_solar = max(0, predicted_solar)
    
    return predicted_demand, predicted_solar


# ============================================================================
# VISUALIZATION FUNCTIONS
# ============================================================================

def plot_energy_flow_sankey(predicted_solar, predicted_demand, recommendation, battery_capacity=100.0):
    """
    Create a Sankey diagram showing energy flow between sources and demand.

    Args:
        predicted_solar: Predicted solar generation (MW)
        predicted_demand: Predicted electricity demand (MW)
        recommendation: Dictionary with optimization results
        battery_capacity: Maximum battery capacity (MW)
    """
    # Calculate energy flows based on recommendation
    energy_balance = recommendation["energy_balance"]
    grid_energy_used = recommendation["grid_energy_used"]
    battery_level = recommendation["battery_level"]
    renewable_contribution = recommendation["renewable_contribution"]

    # Calculate flows
    solar_to_demand = 0.0
    solar_to_battery = 0.0
    battery_to_demand = 0.0
    grid_to_demand = grid_energy_used
    solar_to_grid = 0.0

    if energy_balance > 0:
        # Surplus: Solar charges battery, excess goes to grid
        battery_capacity_remaining = battery_capacity - battery_level
        solar_to_battery = min(energy_balance, battery_capacity_remaining)
        solar_to_grid = energy_balance - solar_to_battery
        solar_to_demand = predicted_solar - solar_to_battery - solar_to_grid
    elif energy_balance < 0:
        # Deficit: Battery discharges first, then grid
        deficit = -energy_balance
        battery_to_demand = min(deficit, battery_level)
        grid_to_demand = deficit - battery_to_demand
        solar_to_demand = predicted_solar
    else:
        # Balanced: Solar directly meets demand
        solar_to_demand = predicted_solar

    # Define nodes
    nodes = [
        {"label": "Solar Generation", "color": "#FFD700"},
        {"label": "Battery Storage", "color": "#4CAF50"},
        {"label": "Grid Supply", "color": "#FF6B6B"},
        {"label": "Electricity Demand", "color": "#9C27B0"}
    ]

    # Define links
    links = []
    if solar_to_demand > 0:
        links.append({"source": 0, "target": 3, "value": solar_to_demand, "color": "rgba(255, 215, 0, 0.6)"})
    if solar_to_battery > 0:
        links.append({"source": 0, "target": 1, "value": solar_to_battery, "color": "rgba(255, 215, 0, 0.6)"})
    if battery_to_demand > 0:
        links.append({"source": 1, "target": 3, "value": battery_to_demand, "color": "rgba(76, 175, 80, 0.6)"})
    if grid_to_demand > 0:
        links.append({"source": 2, "target": 3, "value": grid_to_demand, "color": "rgba(255, 107, 107, 0.6)"})

    # Add solar to grid if there's excess
    if solar_to_grid > 0:
        nodes.append({"label": "Grid Export", "color": "#FF9800"})
        links.append({"source": 0, "target": 4, "value": solar_to_grid, "color": "rgba(255, 152, 0, 0.6)"})

    # Create Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=[node["label"] for node in nodes],
            color=[node["color"] for node in nodes]
        ),
        link=dict(
            source=[link["source"] for link in links],
            target=[link["target"] for link in links],
            value=[link["value"] for link in links],
            color=[link["color"] for link in links],
            hovertemplate='%{source.label} → %{target.label}<br>Energy: %{value:.1f} MW<extra></extra>'
        )
    )])

    fig.update_layout(
        template="plotly_dark",
        title="Energy Flow Diagram",
        font=dict(size=12),
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig


def plot_energy_balance(solar, demand):
    fig = go.Figure()
    fig.add_bar(x=["Solar Generation", "Electricity Demand"], y=[solar, demand], marker=dict(color=["#FFD700", "#FF6B6B"]), text=[f"{solar:.1f} MW", f"{demand:.1f} MW"], textposition="outside")
    fig.update_layout(template="plotly_dark", yaxis_title="Energy (MW)", title="Energy Generation vs Demand", margin=dict(l=20, r=20, t=50, b=20), yaxis=dict(range=[0, max(solar, demand) * 1.2]), bargap=0.3)
    return fig


def plot_hourly_forecast(hour):
    hours = np.arange(0, 24)
    solar_pattern = np.maximum(0, 200 * np.sin((hours - 6) * np.pi / 12))
    demand_pattern = 100 + 50 * np.cos((hours - 12) * np.pi / 12) + 30 * np.sin((hours - 18) * np.pi / 6)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=solar_pattern, mode="lines+markers", name="Solar Pattern", line=dict(color="#FFD700", width=3), marker=dict(size=6)))
    fig.add_trace(go.Scatter(x=hours, y=demand_pattern, mode="lines+markers", name="Demand Pattern", line=dict(color="#FF6B6B", width=3), marker=dict(size=6)))
    fig.add_vline(x=hour, line_width=2, line_dash="dash", line_color="green")
    fig.update_layout(template="plotly_dark", xaxis_title="Hour of Day", yaxis_title="Energy (MW)", title="24-Hour Energy Pattern (Forecast)", margin=dict(l=20, r=20, t=50, b=20), xaxis=dict(range=[-0.5, 23.5], tickmode="linear", dtick=2))
    return fig


def calculate_peak_demand(solar_model, demand_model, temperature, cloud_cover, humidity):
    """
    FEATURE 3: Peak Demand Prediction
    
    Generate 24-hour demand predictions and identify peak demand hour.
    
    Args:
        solar_model: Trained solar generation model
        demand_model: Trained demand prediction model
        temperature: Temperature in Celsius
        cloud_cover: Cloud cover (0-1)
        humidity: Humidity (0-100)
    
    Returns:
        Dict with peak_hour, peak_demand, and hourly predictions
    """
    hours = np.arange(0, 24)
    demand_predictions = []
    
    for h in hours:
        # Create feature vector for each hour
        features = np.array([[temperature, cloud_cover, humidity, h]])
        demand_pred = demand_model.predict(features)[0]
        demand_predictions.append(max(0, demand_pred))  # Ensure non-negative
    
    peak_hour = int(np.argmax(demand_predictions))
    peak_demand = demand_predictions[peak_hour]
    
    return {
        "peak_hour": peak_hour,
        "peak_demand": peak_demand,
        "hourly_predictions": demand_predictions,
        "hours": hours
    }


def plot_peak_demand_forecast(peak_data):
    """
    FEATURE 3: Visualize 24-hour demand forecast with peak indicator.
    """
    hours = peak_data["hours"]
    predictions = peak_data["hourly_predictions"]
    peak_hour = peak_data["peak_hour"]
    peak_demand = peak_data["peak_demand"]
    
    fig = go.Figure()
    
    # Add demand line
    fig.add_trace(go.Scatter(
        x=hours,
        y=predictions,
        mode="lines+markers",
        name="Predicted Demand",
        line=dict(color="#FF6B6B", width=3),
        marker=dict(size=8),
        fill="tozeroy",
        fillcolor="rgba(255, 107, 107, 0.2)",
        hovertemplate="Hour %{x}: %{y:.1f} MW<extra></extra>"
    ))
    
    # Highlight peak demand
    fig.add_vline(
        x=peak_hour,
        line_width=3,
        line_dash="dash",
        line_color="orange",
        annotation_text=f"⚠️ Peak: {peak_demand:.1f} MW",
        annotation_position="top right"
    )
    
    fig.update_layout(
        template="plotly_dark",
        title="24-Hour Peak Demand Forecast",
        xaxis_title="Hour of Day",
        yaxis_title="Demand (MW)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20),
        xaxis=dict(range=[-0.5, 23.5], tickmode="linear", dtick=2)
    )
    
    return fig


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main Streamlit application logic."""
    
    st.title("⚡ Grid Energy Optimizer ⚡")
    st.markdown("Renewable energy management for smart grids")
    st.markdown("---")
    
    models = load_models()
    optimizer = EnergyOptimizer()
    
    with st.sidebar:
        st.subheader("⚙️ Settings")
        st.write(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.success("Logged out successfully! Redirecting to login...")
            st.rerun()
        battery_level_percent = st.slider("🔋 Battery Level (%)", 0, 100, 50, 1)
        battery_level_mw = (battery_level_percent / 100) * optimizer.battery_capacity
        st.caption(f"Battery: {battery_level_mw:.1f} / {optimizer.battery_capacity:.1f} MW")
        
        # ====== WEATHER INTEGRATION ======
        st.markdown("---")
        st.subheader("🌍 Weather Data")
        use_weather_api = st.checkbox(
            "📍 Auto-fetch weather data",
            value=False,
            help="Automatically fetch real weather data by city name"
        )
        
        if use_weather_api:
            city_name = st.text_input(
                "🏙️ Enter City Name",
                value="London",
                placeholder="e.g., London, New York, Tokyo",
                help="Weather data will be fetched from this city"
            )
            if st.button("🔄 Fetch Weather Data", use_container_width=True):
                with st.spinner(f"🌍 Fetching weather for {city_name}..."):
                    weather_data = get_weather_data(city_name)
                    if weather_data and validate_weather_data(weather_data):
                        st.session_state.weather_data = weather_data
                        st.success(f"✅ Weather loaded for {weather_data['city']}, {weather_data['country']}")
                    else:
                        st.error(f"❌ Could not fetch weather for {city_name}")
                        st.session_state.weather_data = None
    
    # Create two-column layout: inputs and outputs
    col1, col2 = st.columns([1, 1], gap="medium")
    
    # ====================================================================
    # LEFT COLUMN: INPUT PARAMETERS
    # ====================================================================
    with col1:
        st.subheader("📊 Input Parameters")
        st.markdown("Provide current weather conditions and time to get predictions.")
        
        # ====== FEATURE 1: Temperature Unit Selection ======
        temp_unit = st.radio(
            "🌡️ Temperature Unit",
            options=["Celsius", "Fahrenheit", "Kelvin"],
            horizontal=True,
            help="Select temperature unit. Value will be converted to Celsius for prediction."
        )
        
        # Check if weather data is available
        weather_data = st.session_state.get("weather_data", None)
        
        # Set defaults from weather data if available
        if weather_data and validate_weather_data(weather_data):
            temp_default_celsius = weather_data["temperature"]
            cloud_cover_default = weather_data["cloud_cover"] / 100.0  # Convert 0-100 to 0-1
            humidity_default = weather_data["humidity"]
            
            st.info(f"📍 Using live weather from: {weather_data['city']}, {weather_data['country']}")
        else:
            temp_default_celsius = 20.0
            cloud_cover_default = 0.5
            humidity_default = 60.0
        
        # Set slider range based on selected unit
        if temp_unit == "Celsius":
            temp_min, temp_max = -10.0, 50.0
            unit_label = "°C"
            temp_default = temp_default_celsius
        elif temp_unit == "Fahrenheit":
            temp_min, temp_max = 14.0, 122.0
            unit_label = "°F"
            temp_default = (temp_default_celsius * 9/5) + 32  # Convert to Fahrenheit
        else:  # Kelvin
            temp_min, temp_max = 263.0, 323.0
            unit_label = "K"
            temp_default = temp_default_celsius + 273.15  # Convert to Kelvin
        
        # Temperature input slider
        temperature_input = st.slider(
            f"Temperature ({unit_label})",
            min_value=float(temp_min),
            max_value=float(temp_max),
            value=float(round(temp_default, 1)),
            step=0.5,
            help="Current ambient temperature" + (" [from weather API]" if weather_data else "")
        )
        
        # Convert to Celsius for ML model
        if temp_unit == "Fahrenheit":
            temperature = (temperature_input - 32) * 5 / 9  # F to C
        elif temp_unit == "Kelvin":
            temperature = temperature_input - 273.15  # K to C
        else:
            temperature = temperature_input  # Already in C
        
        st.caption(f"📊 Model receives: {temperature:.2f}°C")
        
        cloud_cover = st.slider(
            "☁️ Cloud Cover (0-1)",
            min_value=0.0,
            max_value=1.0,
            value=float(round(cloud_cover_default, 2)),
            step=0.05,
            help="0 = Clear sky, 1 = Overcast" + (" [from weather API]" if weather_data else "")
        )
        
        humidity = st.slider(
            "💧 Humidity (%)",
            min_value=0.0,
            max_value=100.0,
            value=float(round(humidity_default, 1)),
            step=1.0,
            help="Relative humidity percentage" + (" [from weather API]" if weather_data else "")
        )
        
        hour = st.selectbox(
            "🕐 Hour of Day",
            options=list(range(24)),
            index=12,
            help="0 = Midnight, 12 = Noon, 23 = 11 PM"
        )
        
        # Prediction button
        if st.button("� Generate Prediction", use_container_width=True, type="primary"):
            st.session_state.show_results = True
        
        # Display input summary
        st.markdown("---")
        st.markdown("**📝 Current Input Summary:**")
        st.write(f"- Temperature: **{temperature}°C**")
        st.write(f"- Cloud Cover: **{cloud_cover:.0%}**")
        st.write(f"- Humidity: **{humidity:.0f}%**")
        st.write(f"- Time: **{hour:02d}:00**")
    
    # ====================================================================
    # RIGHT COLUMN: PREDICTIONS & RECOMMENDATIONS
    # ====================================================================
    with col2:
        # Check if we should show results
        if st.session_state.get("show_results", False):
            # Make predictions
            predicted_demand, predicted_solar = predict_energy(
                temperature, cloud_cover, humidity, hour, models
            )
            
            # ====== FEATURE 3: Calculate Peak Demand ======
            solar_model, demand_model = models
            peak_data = calculate_peak_demand(
                solar_model, demand_model, temperature, cloud_cover, humidity
            )
            
            st.subheader("🎯 Predictions & Recommendations")
            
            # Display prediction metrics in 3 columns
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric(
                    "⚡ Predicted Demand",
                    f"{predicted_demand:.1f} MW",
                    delta=None,
                    delta_color="off"
                )
            
            with metric_col2:
                st.metric(
                    "☀️ Predicted Solar",
                    f"{predicted_solar:.1f} MW",
                    delta=None,
                    delta_color="off"
                )
            
            with metric_col3:
                st.metric(
                    "📊 Peak Demand Hour",
                    f"{peak_data['peak_hour']:02d}:00",
                    f"{peak_data['peak_demand']:.1f} MW"
                )
            
            recommendation = optimizer.get_recommendation(predicted_solar, predicted_demand, battery_level_mw)
            
            # Display recommendation with color coding
            action = recommendation["action"]
            explanation = recommendation["explanation"]
            confidence = recommendation["confidence"]
            color = recommendation["color"]
            
            st.markdown(f"""
                <div class="recommendation-card" style="--accent:{color}">
                    <h3 style="margin:0">{action}</h3>
                    <p style="margin:.25rem 0 0">{explanation}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Confidence Level:**")
            st.progress(confidence)
            st.caption(f"{confidence:.0%} confidence in this recommendation")
            
            # New metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                battery_percent = (recommendation["battery_level"] / optimizer.battery_capacity) * 100
                st.metric("🔋 Battery Level", f"{battery_percent:.1f}%", f"{recommendation['battery_level']:.1f} MW")
            with col2:
                st.metric("🌱 Renewable Contribution", f"{recommendation['renewable_contribution']:.1%}")
            with col3:
                st.metric("💨 CO2 Emitted", f"{recommendation['co2_emitted']:.1f} kg")
            
            grid_status = optimizer.get_grid_status(predicted_solar, predicted_demand)
            if grid_status == "Balanced":
                st.info(f"⚖️ **Grid Status:** {grid_status}")
            elif grid_status == "Surplus":
                st.success(f"⚖️ **Grid Status:** {grid_status}")
            else:
                st.warning(f"⚖️ **Grid Status:** {grid_status}")
            
            # Energy balance indicator
            balance = recommendation["energy_balance"]
            if balance > 0:
                st.success(f"✅ **Surplus Energy:** +{balance:.1f} MW available")
                st.balloons()
            elif balance < 0:
                st.warning(f"⚠️ **Energy Deficit:** {balance:.1f} MW shortfall")
                st.snow()
            else:
                st.info(f"⚖️ **Grid Balanced:** {balance:.1f} MW")
            
            st.download_button(
                "⬇️ Download Results (CSV)",
                data=pd.DataFrame({
                    "temperature":[temperature],
                    "cloud_cover":[cloud_cover],
                    "humidity":[humidity],
                    "hour":[hour],
                    "battery_level":[battery_level_mw],
                    "predicted_demand":[predicted_demand],
                    "predicted_solar":[predicted_solar],
                    "energy_balance":[balance],
                    "action":[action],
                    "confidence":[confidence]
                }).to_csv(index=False),
                file_name="energy_optimizer_results.csv",
                mime="text/csv"
            )
            
            # Execute Energy Plan Button
            st.markdown("---")
            if st.button("🚀 Execute Energy Plan", use_container_width=True, type="secondary"):
                with st.spinner("Sending commands to plant controllers..."):
                    import requests
                    
                    # Prepare execution data based on recommendation
                    execution_data = {
                        "solar": predicted_solar,
                        "battery": recommendation["battery_level"] - battery_level_mw if recommendation["energy_balance"] > 0 else min(-recommendation["energy_balance"], battery_level_mw),
                        "grid": recommendation["grid_energy_used"]
                    }
                    
                    # Get API URL from environment variable, default to localhost for development
                    API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:5000")
                    
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/execute-plan",
                            json=execution_data,
                            timeout=5
                        )
                        
                        if response.status_code == 200:
                            execution_result = response.json()
                            
                            st.success("✅ **Energy Plan Executed Successfully!**")
                            
                            # Display execution status
                            status_col1, status_col2, status_col3 = st.columns(3)
                            
                            with status_col1:
                                solar_icon = "☀️" if execution_result["solar_generation"] == "Activated" else "⏸️"
                                st.metric(
                                    f"{solar_icon} Solar Generation",
                                    execution_result["solar_generation"],
                                    f"{execution_result['targets']['solar_target']:.1f} MW target"
                                )
                            
                            with status_col2:
                                battery_icon = "🔋" if execution_result["battery_storage"] == "Charging" else "⏸️"
                                st.metric(
                                    f"{battery_icon} Battery Storage",
                                    execution_result["battery_storage"],
                                    f"{execution_result['targets']['battery_target']:.1f} MW target"
                                )
                            
                            with status_col3:
                                grid_icon = "🏭" if execution_result["grid_backup"] == "Active" else "⏸️"
                                st.metric(
                                    f"{grid_icon} Grid Backup",
                                    execution_result["grid_backup"],
                                    f"{execution_result['targets']['grid_target']:.1f} MW target"
                                )
                            
                            st.info(f"📋 **Execution ID:** {execution_result['execution_id']}")
                            st.caption(f"⏰ Executed at: {execution_result['timestamp']}")
                            
                        else:
                            st.error(f"❌ Failed to execute plan: {response.text}")
                            
                    except requests.exceptions.RequestException as e:
                        st.error(f"❌ Connection error: Could not connect to plant controller API. {str(e)}")
                        st.info(f"💡 **Note:** Make sure the API server is running on {API_BASE_URL}")
        
        else:
            st.info("👈 Set parameters and click 'Generate Prediction' to see results.")
    
    # ====================================================================
    # VISUALIZATIONS
    # ====================================================================
    st.markdown("---")
    
    if st.session_state.get("show_results", False):
        st.subheader("📈 Energy Visualizations")
        
        tab1, tab2, tab3 = st.tabs(["Energy Flow", "24-Hour Pattern", "Peak Demand"])
        
        with tab1:
            fig_balance = plot_energy_flow_sankey(predicted_solar, predicted_demand, recommendation, optimizer.battery_capacity)
            st.plotly_chart(fig_balance, width='stretch')
        
        with tab2:
            fig_hourly = plot_hourly_forecast(hour)
            st.plotly_chart(fig_hourly, width='stretch')
        
        with tab3:
            # ====== FEATURE 3: Display Peak Demand Forecast ======
            peak_fig = plot_peak_demand_forecast(peak_data)
            st.plotly_chart(peak_fig, width='stretch')
            
            # Additional peak demand insights
            col_peak1, col_peak2 = st.columns(2)
            with col_peak1:
                st.info(f"⚠️ **Peak Demand Hour:** {peak_data['peak_hour']:02d}:00 (2:00 PM in 24h format)" if peak_data['peak_hour'] == 14 else f"⚠️ **Peak Demand Hour:** {peak_data['peak_hour']:02d}:00")
            with col_peak2:
                st.warning(f"📊 **Peak Demand Value:** {peak_data['peak_demand']:.1f} MW")
    
    # ====================================================================
    # ABOUT SECTION
    # ====================================================================
    with st.expander("ℹ️ About This Project"):
        st.markdown("""
        **Grid Energy Optimizer** is a hackathon prototype designed to optimize 
        renewable energy distribution in smart grids.
        
        ### Features:
        - **Statistical Predictions**: Uses Linear Regression (demand) and Random Forest (solar)
        - **Smart Recommendations**: Optimizes battery usage and grid load
        - **Real-time Dashboard**: Interactive interface for energy operators
        
        ### How It Works:
        1. Input current weather and time conditions
        2. Statistical models predict demand and solar generation
        3. Optimizer recommends best energy source
        4. Battery storage is prioritized to reduce grid strain
        
        ### Data Flow:
        `Raw Data → Data Processing → Model Training → Live Predictions → Grid Optimization`
        
        **Built by:** Team of 4 students in 18 hours ⏱️🚀
        """)

    # 24-Hour Forecast Simulation
    st.header("24-Hour Forecast Simulation")
    st.markdown("Simulate energy predictions and battery management for the next 24 hours using current weather conditions.")
    
    if st.button("Run 24-Hour Simulation"):
        with st.spinner("Simulating 24-hour forecast..."):
            # Generate predictions for 24 hours
            demand_preds = []
            solar_preds = []
            for h in range(24):
                d, s = predict_energy(temperature, cloud_cover, humidity, h, models)
                demand_preds.append(d)
                solar_preds.append(s)
            
            # Run simulation
            sim = optimizer.simulate_24_hour_forecast(demand_preds, solar_preds, battery_level_mw)
            
            # Display results
            st.subheader("Simulation Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Grid Energy Used", f"{sim['total_grid_energy']:.1f} MW")
            with col2:
                st.metric("Total CO2 Emitted", f"{sim['total_co2']:.1f} kg")
            with col3:
                st.metric("Avg Renewable Contribution", f"{sim['avg_renewable_contribution']:.1%}")
            
            # Plot
            hours = list(range(24))
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hours, y=demand_preds, mode='lines+markers', name='Demand (MW)', line=dict(color='#FF6B6B')))
            fig.add_trace(go.Scatter(x=hours, y=solar_preds, mode='lines+markers', name='Solar (MW)', line=dict(color='#FFD700')))
            fig.add_trace(go.Scatter(x=hours, y=sim['battery_levels'], mode='lines+markers', name='Battery Level (MW)', line=dict(color='#4CAF50'), yaxis='y2'))
            
            fig.update_layout(
                template="plotly_dark",
                title="24-Hour Energy Forecast & Battery Simulation",
                xaxis_title="Hour of Day",
                yaxis_title="Energy (MW)",
                yaxis2=dict(title="Battery Level (MW)", overlaying='y', side='right'),
                margin=dict(l=20, r=20, t=50, b=20)
            )
            st.plotly_chart(fig)
    
    # Feature Importance Analysis
    st.header("Feature Importance Analysis")
    st.markdown("Understanding which features most influence the ML predictions.")
    
    demand_model, solar_model = models
    features = ['Temperature (°C)', 'Cloud Cover', 'Humidity (%)', 'Hour']
    
    # ---------- Solar feature importance (Random Forest) ----------
    imp = solar_model.feature_importances_
    df_solar = pd.DataFrame({"feature": features, "importance": imp})
    df_solar = df_solar.sort_values("importance", ascending=True)
    
    fig = px.bar(
        df_solar,
        x="importance",
        y="feature",
        orientation="h",
        color="importance",
        color_continuous_scale="Viridis",
        title="Solar Model Feature Importance",
    )
    fig.update_layout(
        template="plotly_dark",
        xaxis_title="Importance",
        yaxis_title="Feature",
        margin=dict(l=60, r=20, t=50, b=20),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
    fig.update_yaxes(showgrid=False)
    fig.update_traces(marker=dict(showscale=True, line=dict(width=0)))
    st.plotly_chart(fig, width='stretch')
    
    # ---------- Demand coefficients (Linear Regression) ----------
    coeff = demand_model.coef_
    df_demand = pd.DataFrame({"feature": features, "coefficient": coeff})
    df_demand = df_demand.sort_values("coefficient", ascending=False)
    
    fig2 = px.bar(
        df_demand,
        x="feature",
        y="coefficient",
        color="coefficient",
        color_continuous_scale=px.colors.diverging.RdYlGn,
        title="Demand Model Coefficients",
    )
    fig2.update_layout(
        template="plotly_dark",
        xaxis_title="Feature",
        yaxis_title="Coefficient",
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig2.update_xaxes(showgrid=False)
    fig2.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.1)")
    st.plotly_chart(fig2, width='stretch')
    
    # Admin Dashboard
    if st.session_state.role == 'admin':
        show_admin_dashboard()


# ============================================================================
# INITIALIZE SESSION STATE & RUN APP
# ============================================================================

if "show_results" not in st.session_state:
    st.session_state.show_results = False

if __name__ == "__main__":
    if st.session_state.logged_in:
        main()
    else:
        show_login()
