#!/usr/bin/env python3
"""
Test script for the Plant Control Simulation System

This script demonstrates the new /execute-plan endpoint that simulates
sending commands to power plant controllers after generating an energy plan.
"""

import requests
import json
import time

def test_plant_control_simulation():
    """Test the complete plant control simulation flow."""

    print("=" * 70)
    print("PLANT CONTROL SIMULATION SYSTEM TEST")
    print("=" * 70)

    # Test scenarios
    scenarios = [
        {
            "name": "High Solar Generation",
            "data": {"solar": 150, "battery": 20, "grid": 10}
        },
        {
            "name": "Battery Heavy Usage",
            "data": {"solar": 50, "battery": 120, "grid": 30}
        },
        {
            "name": "Grid Backup Mode",
            "data": {"solar": 10, "battery": 5, "grid": 180}
        },
        {
            "name": "Standby Mode",
            "data": {"solar": 0, "battery": 0, "grid": 0}
        }
    ]

    base_url = "http://localhost:5000/execute-plan"

    for scenario in scenarios:
        print(f"\n🧪 Testing: {scenario['name']}")
        print("-" * 50)

        try:
            print(f"Input: {json.dumps(scenario['data'], indent=2)}")

            response = requests.post(base_url, json=scenario['data'], timeout=10)

            if response.status_code == 200:
                result = response.json()

                print("✅ Success!")
                print(f"   Status: {result['status']}")
                print(f"   Execution ID: {result['execution_id']}")
                print(f"   Solar: {result['solar_generation']}")
                print(f"   Battery: {result['battery_storage']}")
                print(f"   Grid: {result['grid_backup']}")
                print(f"   Timestamp: {result['timestamp']}")

            else:
                error_data = response.json()
                print(f"❌ Error (Status {response.status_code}): {error_data.get('error', 'Unknown error')}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {str(e)}")

        time.sleep(0.5)  # Brief pause between tests

    print("\n" + "=" * 70)
    print("STREAMLIT DASHBOARD INTEGRATION:")
    print("=" * 70)
    print("1. Start the dashboard: streamlit run app.py")
    print("2. Login with admin/admin")
    print("3. Set weather parameters and click 'Generate Prediction'")
    print("4. Scroll down and click '🚀 Execute Energy Plan'")
    print("5. Watch the plant control simulation in action!")
    print()
    print("API ENDPOINT: POST /execute-plan")
    print("Content-Type: application/json")
    print()
    print("Example Request:")
    print("{")
    print('    "solar": 130,')
    print('    "battery": 60,')
    print('    "grid": 30')
    print("}")
    print()
    print("Example Response:")
    print("{")
    print('    "success": true,')
    print('    "status": "Execution Started",')
    print('    "solar_generation": "Activated",')
    print('    "battery_storage": "Charging",')
    print('    "grid_backup": "Active",')
    print('    "execution_id": "EXEC-1772914213",')
    print('    "timestamp": "2026-03-08 01:39:12"')
    print("}")

if __name__ == "__main__":
    test_plant_control_simulation()</content>
<parameter name="filePath">c:\Users\divya\OneDrive\Desktop\Projects\Vebhav\ai-grid-energy-optimizer\test_plant_control.py