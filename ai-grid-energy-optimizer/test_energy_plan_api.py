#!/usr/bin/env python3
"""
Test script for the /energy-plan API endpoint

This script demonstrates how to use the new energy plan generation endpoint
that combines weather data, ML predictions, and optimization logic.
"""

import requests
import json

def test_energy_plan_api():
    """Test the energy plan API with various scenarios."""

    base_url = "http://localhost:5000/energy-plan"

    test_cases = [
        {
            "name": "Delhi - High Demand",
            "data": {"city": "Delhi", "required_energy": 220}
        },
        {
            "name": "London - Moderate Demand",
            "data": {"city": "London", "required_energy": 150}
        },
        {
            "name": "New York - Peak Demand",
            "data": {"city": "New York", "required_energy": 300}
        }
    ]

    print("=" * 60)
    print("ENERGY PLAN API TEST RESULTS")
    print("=" * 60)

    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['name']}")
        print("-" * 40)

        try:
            response = requests.post(base_url, json=test_case['data'], timeout=10)

            if response.status_code == 200:
                result = response.json()

                print("✅ Success!")
                print(f"   City: {result['weather_data']['city']}, {result['weather_data']['country']}")
                print(f"   Weather: {result['weather_data']['temperature']}°C, {result['weather_data']['humidity']}% humidity, {result['weather_data']['cloud_cover']}% cloud cover")
                print(f"   Predicted Demand: {result['predicted_demand']} MW")
                print(f"   Solar Generation: {result['solar_generation']} MW")
                print(f"   Battery Usage: {result['battery_usage']} MW")
                print(f"   Grid Usage: {result['grid_usage']} MW")
                print(f"   Recommendation: {result['recommendation']['action']}")
                print(f"   Status: {result['status']}")

            else:
                error_data = response.json()
                print(f"❌ Error (Status {response.status_code}): {error_data.get('error', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")

    print("\n" + "=" * 60)
    print("API ENDPOINT USAGE:")
    print("=" * 60)
    print("POST /energy-plan")
    print("Content-Type: application/json")
    print()
    print("Body:")
    print("{")
    print('    "city": "Delhi",')
    print('    "required_energy": 220')
    print("}")
    print()
    print("Response:")
    print("{")
    print('    "success": true,')
    print('    "predicted_demand": 150.61,')
    print('    "solar_generation": 5.6,')
    print('    "battery_usage": 129.99,')
    print('    "grid_usage": 0.0,')
    print('    "status": "Energy Plan Ready",')
    print('    "weather_data": {...},')
    print('    "recommendation": {...},')
    print('    "optimization_details": {...}')
    print("}")

if __name__ == "__main__":
    test_energy_plan_api()</content>
<parameter name="filePath">c:\Users\divya\OneDrive\Desktop\Projects\Vebhav\ai-grid-energy-optimizer\test_energy_plan_api.py