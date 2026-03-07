"""
Model training script for Grid Energy Optimizer.

This script loads preprocessed energy data, trains two regression models
for forecasting electricity demand and solar generation, evaluates them,
and persists the models to disk for later use.
"""

import os
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def load_processed_data(path: str) -> pd.DataFrame:
    """Read the processed dataset from CSV."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Processed data not found at {path}")
    return pd.read_csv(path)


def evaluate_model(model, X_test, y_test):
    """Compute and return MAE, RMSE, and R2 metrics for the provided model."""
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    r2 = r2_score(y_test, preds)
    return mae, rmse, r2


def main():
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_energy_data.csv")
    print(f"Loading processed data from {data_path}")
    df = load_processed_data(data_path)

    # select feature columns
    features = ["temperature", "cloud_cover", "humidity", "hour"]
    X = df[features]
    y_demand = df["electricity_demand"]
    y_solar = df["solar_generation"]

    # split for demand model
    X_train_d, X_test_d, y_train_d, y_test_d = train_test_split(
        X, y_demand, test_size=0.2, random_state=42
    )

    # split for solar model
    X_train_s, X_test_s, y_train_s, y_test_s = train_test_split(
        X, y_solar, test_size=0.2, random_state=42
    )

    # train linear regression for demand
    print("Training Linear Regression model for electricity demand...")
    demand_model = LinearRegression()
    demand_model.fit(X_train_d, y_train_d)

    # evaluate demand model
    mae_d, rmse_d, r2_d = evaluate_model(demand_model, X_test_d, y_test_d)
    print("Demand model evaluation:")
    print(f"  MAE: {mae_d:.4f}")
    print(f"  RMSE: {rmse_d:.4f}")
    print(f"  R2: {r2_d:.4f}")

    # train random forest for solar
    print("Training Random Forest model for solar generation...")
    solar_model = RandomForestRegressor(n_estimators=100, random_state=42)
    solar_model.fit(X_train_s, y_train_s)

    # evaluate solar model
    mae_s, rmse_s, r2_s = evaluate_model(solar_model, X_test_s, y_test_s)
    print("Solar model evaluation:")
    print(f"  MAE: {mae_s:.4f}")
    print(f"  RMSE: {rmse_s:.4f}")
    print(f"  R2: {r2_s:.4f}")

    # save models
    model_dir = os.path.join(os.path.dirname(__file__), "..", "models")
    os.makedirs(model_dir, exist_ok=True)

    demand_path = os.path.join(model_dir, "demand_model.pkl")
    print(f"Saving demand model to {demand_path}")
    with open(demand_path, "wb") as f:
        pickle.dump(demand_model, f)

    solar_path = os.path.join(model_dir, "solar_model.pkl")
    print(f"Saving solar model to {solar_path}")
    with open(solar_path, "wb") as f:
        pickle.dump(solar_model, f)

    print("Training complete, models persisted.")


if __name__ == "__main__":
    main()
