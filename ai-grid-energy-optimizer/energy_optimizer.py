"""
Energy Optimization Logic Module

This module contains the core logic for making optimal grid decisions
based on solar generation and electricity demand predictions.

The optimizer evaluates energy sources and recommends the best strategy
to minimize grid stress and maximize renewable energy usage.
"""

import json
from typing import Dict, Tuple, List


class EnergyOptimizer:
    """
    Evaluates energy production vs. demand and recommends grid actions.
    
    Strategy:
    1. If solar > demand: Store excess energy in battery
    2. If solar < demand and battery available: Use stored battery energy
    3. Otherwise: Draw from grid backup
    """
    
    # Default battery capacity in MW
    DEFAULT_BATTERY_CAPACITY = 550
    # CO2 emission factor: kg CO2 per MWh
    EMISSION_FACTOR = 0.5  # Typical grid emission factor
    
    def __init__(self, battery_capacity: float = None):
        """
        Initialize the optimizer with battery capacity.
        
        Args:
            battery_capacity: Maximum battery capacity in MW
        """
        self.battery_capacity = battery_capacity or self.DEFAULT_BATTERY_CAPACITY
        self.current_battery_level = self.battery_capacity * 0.5  # Start at 50%
    
    def get_recommendation(
        self,
        solar_generation: float,
        electricity_demand: float,
        battery_level: float = None
    ) -> Dict:
        """
        Determine the optimal energy strategy for current conditions.
        
        Args:
            solar_generation: Predicted solar output (MW)
            electricity_demand: Predicted demand (MW)
            battery_level: Current battery charge (MW). If None, uses instance level.
        
        Returns:
            Dict containing:
            - action: Recommended action string
            - explanation: Reasoning for the recommendation
            - energy_balance: Surplus/deficit amount
            - confidence: How strongly we recommend this action (0-1)
            - battery_level: Updated battery level (MW)
            - grid_energy_used: Energy drawn from grid (MW)
            - co2_emitted: CO2 emissions (kg)
            - renewable_contribution: Percentage of demand met by renewables
        """
        if battery_level is None:
            battery_level = self.current_battery_level
        
        energy_balance = solar_generation - electricity_demand
        grid_energy_used = 0.0
        co2_emitted = 0.0
        renewable_contribution = 0.0
        
        if energy_balance > 0:
            # Surplus: Charge battery
            new_battery_level = min(battery_level + energy_balance, self.battery_capacity)
            excess = energy_balance - (new_battery_level - battery_level)
            action = "🔋 Store Excess Energy"
            explanation = f"Storing {energy_balance:.1f} MW excess solar in battery. Battery at {new_battery_level:.1f}/{self.battery_capacity:.1f} MW."
            confidence = 0.9
            renewable_contribution = 1.0  # All demand met by solar
            
        elif energy_balance < 0:
            # Deficit: Check battery
            deficit = -energy_balance
            if battery_level > 0:
                # Use battery
                battery_used = min(deficit, battery_level)
                new_battery_level = battery_level - battery_used
                remaining_deficit = deficit - battery_used
                if remaining_deficit > 0:
                    grid_energy_used = remaining_deficit
                    co2_emitted = grid_energy_used * self.EMISSION_FACTOR
                    action = "🔋 + 🔌 Use Battery + Grid"
                    explanation = f"Using {battery_used:.1f} MW from battery, {remaining_deficit:.1f} MW from grid. Battery at {new_battery_level:.1f}/{self.battery_capacity:.1f} MW."
                    renewable_contribution = (electricity_demand - grid_energy_used) / electricity_demand
                else:
                    action = "🔋 Use Battery Backup"
                    explanation = f"Using {battery_used:.1f} MW from battery. Battery at {new_battery_level:.1f}/{self.battery_capacity:.1f} MW."
                    renewable_contribution = 1.0
                confidence = 0.8
            else:
                # No battery: Use grid
                grid_energy_used = deficit
                co2_emitted = grid_energy_used * self.EMISSION_FACTOR
                new_battery_level = battery_level
                action = "🔌 Draw from Grid"
                explanation = f"Drawing {grid_energy_used:.1f} MW from grid. Battery empty."
                confidence = 0.7
                renewable_contribution = 0.0
        else:
            # Balanced
            new_battery_level = battery_level
            action = "⚖️ Balanced Supply"
            explanation = "Solar generation matches demand perfectly."
            confidence = 1.0
            renewable_contribution = 1.0
        
        # Update instance battery level
        self.current_battery_level = new_battery_level
        
        # Determine color based on renewable contribution
        if renewable_contribution == 1.0:
            color = "green"
        elif renewable_contribution > 0:
            color = "orange"
        else:
            color = "red"
        
        return {
            "action": action,
            "explanation": explanation,
            "energy_balance": energy_balance,
            "confidence": confidence,
            "battery_level": new_battery_level,
            "grid_energy_used": grid_energy_used,
            "co2_emitted": co2_emitted,
            "renewable_contribution": renewable_contribution,
            "color": color
        }
    
    def simulate_24_hour_forecast(
        self,
        demand_predictions: List[float],
        solar_predictions: List[float],
        initial_battery_level: float = None
    ) -> Dict:
        """
        Simulate 24-hour energy optimization.
        
        Args:
            demand_predictions: List of 24 demand predictions (MW)
            solar_predictions: List of 24 solar predictions (MW)
            initial_battery_level: Starting battery level (MW)
        
        Returns:
            Dict with simulation results
        """
        if initial_battery_level is None:
            initial_battery_level = self.current_battery_level
        
        battery_levels = [initial_battery_level]
        actions = []
        grid_usage = []
        co2_emissions = []
        renewable_contributions = []
        
        current_battery = initial_battery_level
        
        for demand, solar in zip(demand_predictions, solar_predictions):
            result = self.get_recommendation(solar, demand, current_battery)
            current_battery = result["battery_level"]
            battery_levels.append(current_battery)
            actions.append(result["action"])
            grid_usage.append(result["grid_energy_used"])
            co2_emissions.append(result["co2_emitted"])
            renewable_contributions.append(result["renewable_contribution"])
        
        # Remove the last battery level (it's the final state)
        battery_levels = battery_levels[:-1]
        
        total_grid_energy = sum(grid_usage)
        total_co2 = sum(co2_emissions)
        avg_renewable = sum(renewable_contributions) / len(renewable_contributions) if renewable_contributions else 0
        
        return {
            "battery_levels": battery_levels,
            "actions": actions,
            "grid_usage": grid_usage,
            "co2_emissions": co2_emissions,
            "renewable_contributions": renewable_contributions,
            "total_grid_energy": total_grid_energy,
            "total_co2": total_co2,
            "avg_renewable_contribution": avg_renewable
        }
    
    def get_grid_status(self, solar_generation: float, electricity_demand: float) -> str:
        """
        Get grid status based on supply vs demand.
        
        Args:
            solar_generation: Current solar output (MW)
            electricity_demand: Current demand (MW)
        
        Returns:
            Status string: "Balanced", "Surplus", or "Deficit"
        """
        balance = solar_generation - electricity_demand
        if abs(balance) < 10:  # Small threshold for "balanced"
            return "Balanced"
        elif balance > 0:
            return "Surplus"
        else:
            return "Deficit"


def create_visualization_data(
    solar_generation: float,
    electricity_demand: float
) -> Dict:
    """
    Prepare data for energy comparison visualization.
    
    Args:
        solar_generation: Predicted solar output
        electricity_demand: Predicted demand
    
    Returns:
        Dict with labels and values for charting
    """
    return {
        "labels": ["Solar Generation", "Electricity Demand"],
        "values": [solar_generation, electricity_demand],
        "colors": ["#FFD700", "#FF6B6B"],  # Gold and red
        "difference": solar_generation - electricity_demand
    }


# Example usage
if __name__ == "__main__":
    optimizer = EnergyOptimizer()
    
    # Test scenarios
    scenarios = [
        (150, 100),  # Excess solar
        (80, 150),   # Insufficient solar, battery available
        (70, 200),   # Severe deficit, low battery
    ]
    
    for solar, demand in scenarios:
        rec = optimizer.get_recommendation(solar, demand)
        print(f"\nSolar: {solar} MW, Demand: {demand} MW")
        print(f"→ {rec['action']}")
        print(f"  {rec['explanation']}")
