#!/usr/bin/env python3
"""
Test script for the Sankey diagram function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import plot_energy_flow_sankey

# Test data
recommendation = {
    "energy_balance": 10.0,  # Surplus
    "grid_energy_used": 0.0,
    "battery_level": 50.0,
    "renewable_contribution": 1.0
}

predicted_solar = 120.0
predicted_demand = 110.0
battery_capacity = 100.0

print("Testing Sankey diagram with surplus scenario...")
try:
    fig = plot_energy_flow_sankey(predicted_solar, predicted_demand, recommendation, battery_capacity)
    print("✅ Sankey diagram created successfully!")
    print(f"Figure type: {type(fig)}")
except Exception as e:
    print(f"❌ Error creating Sankey diagram: {e}")

# Test deficit scenario
recommendation_deficit = {
    "energy_balance": -20.0,  # Deficit
    "grid_energy_used": 15.0,
    "battery_level": 80.0,
    "renewable_contribution": 0.5
}

print("\nTesting Sankey diagram with deficit scenario...")
try:
    fig2 = plot_energy_flow_sankey(predicted_solar, predicted_demand, recommendation_deficit, battery_capacity)
    print("✅ Sankey diagram created successfully!")
    print(f"Figure type: {type(fig2)}")
except Exception as e:
    print(f"❌ Error creating Sankey diagram: {e}")

print("\n🎉 All tests completed!")