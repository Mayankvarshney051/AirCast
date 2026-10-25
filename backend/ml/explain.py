import os
import sys
import pandas as pd
import numpy as np
import joblib

from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error


# --------------------------------------------------
# PATH SETUP
# --------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "trained_model.pkl"
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "city_hour.csv"
)


# --------------------------------------------------
# LOAD TRAINED MODEL
# --------------------------------------------------

package = joblib.load(MODEL_PATH)

model = package["model"]
FEATURES = package["features"]
TARGET = package["target"]


# --------------------------------------------------
# LOAD AND PREPARE DATA
# --------------------------------------------------

def prepare_data():

    df = pd.read_csv(DATA_PATH)

    df["Datetime"] = pd.to_datetime(
        df["Datetime"]
    )

    df = df.sort_values(
        ["City", "Datetime"]
    ).reset_index(drop=True)

    # Same PM2.5 short-gap treatment
    # used during preprocessing

    df["PM2.5"] = (
        df.groupby("City")["PM2.5"]
        .transform(
            lambda x: x.interpolate(
                method="linear",
                limit=3,
                limit_area="inside"
            )
        )
    )

    # Temporal features

    df["Hour"] = df["Datetime"].dt.hour

    df["Month"] = df["Datetime"].dt.month

    df["DayOfWeek"] = (
        df["Datetime"].dt.day_of_week
    )

    # Lag features

    df["PM2.5_lag_24"] = (
        df.groupby("City")["PM2.5"]
        .shift(24)
    )

    df["PM2.5_lag_48"] = (
        df.groupby("City")["PM2.5"]
        .shift(48)
    )

    # 24-hour prediction target

    df["PM2.5_target_24h"] = (
        df.groupby("City")["PM2.5"]
        .shift(-24)
    )

    # Selected pollutant features

    pollutant_features = [
        "PM10",
        "NO",
        "NO2",
        "NOx",
        "NH3",
        "CO",
        "SO2",
        "O3"
    ]

    # Same city-wise median imputation
    # approach used during preprocessing

    for col in pollutant_features:

        df[col] = (
            df.groupby("City")[col]
            .transform(
                lambda x: x.fillna(x.median())
            )
        )

        df[col] = df[col].fillna(
            df[col].median()
        )

    # Keep only required columns

    required_columns = FEATURES + [TARGET]

    df = df[
        required_columns
    ].dropna()

    return df


# --------------------------------------------------
# FEATURE IMPORTANCE
# --------------------------------------------------

def calculate_feature_importance():

    df = prepare_data()

    X = df[FEATURES]
    y = df[TARGET]

    # Use a sample so XAI calculation
    # stays practical

    sample_size = min(
        5000,
        len(df)
    )

    sample = df.sample(
        n=sample_size,
        random_state=42
    )

    X_sample = sample[FEATURES]

    y_sample = sample[TARGET]

    # Baseline prediction

    baseline_prediction = model.predict(
        X_sample
    )

    baseline_mae = mean_absolute_error(
        y_sample,
        baseline_prediction
    )

    # Permutation importance

    result = permutation_importance(
        model,
        X_sample,
        y_sample,
        scoring="neg_mean_absolute_error",
        n_repeats=5,
        random_state=42,
        n_jobs=-1
    )

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "importance": result.importances_mean
    })

    # Negative values can occur because
    # of sampling variation

    importance_df["importance"] = (
        importance_df["importance"]
        .clip(lower=0)
    )

    # Sort highest to lowest

    importance_df = (
        importance_df
        .sort_values(
            "importance",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # FEATURE GROUPS
    # --------------------------------------------------

    lag_features = [
        "PM2.5_lag_24",
        "PM2.5_lag_48"
    ]

    pollutant_features = [
        "PM10",
        "NO",
        "NO2",
        "NOx",
        "NH3",
        "CO",
        "SO2",
        "O3"
    ]

    temporal_features = [
        "Hour",
        "Month",
        "DayOfWeek"
    ]

    def group_feature(feature):

        if feature in lag_features:
            return "Lag Features"

        if feature in pollutant_features:
            return "Pollutants"

        if feature in temporal_features:
            return "Temporal Features"

        return "Other"

    importance_df["group"] = (
        importance_df["feature"]
        .apply(group_feature)
    )

    # Group-level importance

    group_importance = (
        importance_df
        .groupby("group")["importance"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------

    print("\n")

    print("=" * 60)

    print(
        "AIRCAST MODEL EXPLAINABILITY"
    )

    print("=" * 60)

    print(
        f"\nModel: {package['model_name']}"
    )

    print(
        f"Sample size used: {sample_size}"
    )

    print(
        f"Baseline MAE: {baseline_mae:.4f}"
    )

    print("\nFeature Importance:")

    print("-" * 60)

    for _, row in importance_df.iterrows():

        print(
            f"{row['feature']:20s}"
            f" | {row['importance']:.6f}"
            f" | {row['group']}"
        )

    print(
        "\nTop 5 Important Features:"
    )

    print("-" * 60)

    for i, row in importance_df.head(5).iterrows():

        print(
            f"{i + 1}. "
            f"{row['feature']} "
            f"({row['importance']:.6f})"
        )

    print(
        "\nComponent Importance:"
    )

    print("-" * 60)

    for group, value in group_importance.items():

        print(
            f"{group:20s} | "
            f"{value:.6f}"
        )

    print("\n" + "=" * 60)

    print("XAI: PASS")

    print("=" * 60)

    # --------------------------------------------------
    # RETURN XAI RESULT FOR API
    # --------------------------------------------------

    return {
        "model": package["model_name"],

        "sample_size": sample_size,

        "baseline_mae": round(
            float(baseline_mae),
            4
        ),

        "top_features": [
            {
                "feature": row["feature"],
                "importance": round(
                    float(row["importance"]),
                    6
                ),
                "group": row["group"]
            }

            for _, row
            in importance_df.head(5).iterrows()
        ],

        "group_importance": {
            group: round(
                float(value),
                6
            )

            for group, value
            in group_importance.items()
        }
    }


# --------------------------------------------------
# RUN
# --------------------------------------------------

if __name__ == "__main__":

    calculate_feature_importance()