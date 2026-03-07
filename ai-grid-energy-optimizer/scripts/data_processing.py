"""
Data processing script for Grid Energy Optimizer hackathon project.

This script loads raw CSV energy data, cleans it, engineers features,
prepares ML-ready datasets, splits into train/test sets, and saves the
processed data for later use.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split


def load_data(csv_path: str) -> pd.DataFrame:
    """Load dataset from a CSV file."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and preprocess the raw dataframe.

    Steps:
    - Drop rows with missing values
    - Convert `datetime` column to pandas datetime dtype
    - Create `hour`, `day`, and `month` features
    """
    # drop any rows that contain NaNs
    df = df.dropna()

    # ensure datetime column exists and convert
    df["datetime"] = pd.to_datetime(df["datetime"])

    # feature engineering from datetime
    df["hour"] = df["datetime"].dt.hour
    df["day"] = df["datetime"].dt.day
    df["month"] = df["datetime"].dt.month

    return df


def prepare_ml_data(df: pd.DataFrame) -> tuple:
    """Prepare features (X) and targets (y) for ML models.

    Returns:
        X: DataFrame containing features temperature, cloud_cover,
           humidity, and hour.
        y_demand: Series with electricity demand values.
        y_solar: Series with solar generation values.
    """
    required_cols = ["temperature", "cloud_cover", "humidity", "hour", 
                     "electricity_demand", "solar_generation"]
    feature_cols = ["temperature", "cloud_cover", "humidity", "hour"]
    
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        available = list(df.columns)
        raise ValueError(
            f"❌ CSV missing required columns: {missing}\n"
            f"   Available columns: {available}\n"
            f"   Required columns: {required_cols}"
        )
    
    X = df[feature_cols].copy()

    y_demand = df["electricity_demand"].copy()
    y_solar = df["solar_generation"].copy()

    return X, y_demand, y_solar


def split_data(X: pd.DataFrame, y, test_size: float = 0.2, random_state: int = 42):
    """Split features and target into training and testing subsets."""
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def main():
    # path to raw CSV (user should replace with their actual file location)
    raw_csv = os.path.join(os.path.dirname(__file__), "..", "data", "energy_data.csv")

    print("Loading data...")
    df = load_data(raw_csv)

    print("Cleaning data...")
    df = clean_data(df)

    print("Preparing machine learning data...")
    X, y_demand, y_solar = prepare_ml_data(df)

    # split both targets separately so we can train two models later
    X_train_d, X_test_d, y_train_d, y_test_d = split_data(X, y_demand)
    X_train_s, X_test_s, y_train_s, y_test_s = split_data(X, y_solar)

    # combine into one DataFrame for storage (keeping train/test flags)
    processed = df.copy()
    processed["X_temperature"] = X["temperature"]
    processed["X_cloud_cover"] = X["cloud_cover"]
    processed["X_humidity"] = X["humidity"]
    processed["X_hour"] = X["hour"]

    # mark which rows would be in train/test
    processed["is_test"] = False
    processed.loc[X_test_d.index, "is_test"] = True

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed_energy_data.csv")
    print(f"Saving processed data to {out_path}...")
    processed.to_csv(out_path, index=False)
    print(f"✅ Data processing complete! Processed data saved to {out_path}")


if __name__ == "__main__":
    main()

    print("Data processing complete.")


if __name__ == "__main__":
    main()
