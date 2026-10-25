import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from backend.preprocessing.preprocess import (
    load_data,
    handle_pm25_missing,
    create_time_features,
    create_lag_and_target_features,
    impute_selected_features,
    create_model_dataset,
    time_based_split,
    SELECTED_FEATURES,
    TIME_FEATURES,
    LAG_FEATURES,
    TARGET
)


MODEL_PATH = "models/trained_model.pkl"


def prepare_data():

    print("Loading and preprocessing data...")

    df = load_data()

    df = handle_pm25_missing(df)

    df = create_time_features(df)

    df = create_lag_and_target_features(df)

    df = impute_selected_features(df)

    model_df = create_model_dataset(df)

    train_df, test_df, split_date = time_based_split(
        model_df
    )

    return train_df, test_df, split_date


def train_model(X_train, y_train):

    print("\nTraining Random Forest model...")

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    return model


def evaluate_model(model, X_test, y_test):

    print("\nGenerating predictions...")

    predictions = model.predict(X_test)

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\n" + "=" * 60)
    print("MODEL PERFORMANCE")
    print("=" * 60)

    print(f"MAE  : {mae:.4f}")
    print(f"RMSE : {rmse:.4f}")
    print(f"R²   : {r2:.4f}")

    print("=" * 60)

    return predictions, mae, rmse, r2


def show_feature_importance(model, feature_names):

    importance = pd.DataFrame({
        "Feature": feature_names,
        "Importance": model.feature_importances_
    })

    importance = importance.sort_values(
        "Importance",
        ascending=False
    )

    print("\n" + "=" * 60)
    print("FEATURE IMPORTANCE")
    print("=" * 60)

    print(
        importance.to_string(index=False)
    )

    print("=" * 60)

    return importance


def show_prediction_samples(
    test_df,
    predictions
):

    comparison = pd.DataFrame({
        "Datetime": test_df["Datetime"].values,
        "City": test_df["City"].values,
        "Actual_PM2.5": test_df[TARGET].values,
        "Predicted_PM2.5": predictions
    })

    comparison["Error"] = (
        comparison["Actual_PM2.5"]
        - comparison["Predicted_PM2.5"]
    )

    print("\n" + "=" * 60)
    print("SAMPLE PREDICTIONS")
    print("=" * 60)

    print(
        comparison.head(20).to_string(
            index=False
        )
    )

    print("=" * 60)

    return comparison


def save_model(
    model,
    feature_names,
    split_date
):

    os.makedirs(
        "models",
        exist_ok=True
    )

    model_package = {
        "model": model,
        "features": feature_names,
        "target": TARGET,
        "split_date": split_date
    }

    joblib.dump(
        model_package,
        MODEL_PATH
    )

    print(
        f"\nModel saved successfully:"
        f" {MODEL_PATH}"
    )


if __name__ == "__main__":

    # -------------------------------------------------
    # 1. Prepare data
    # -------------------------------------------------

    train_df, test_df, split_date = prepare_data()

    # -------------------------------------------------
    # 2. Define features
    # -------------------------------------------------

    feature_names = (
        SELECTED_FEATURES
        + TIME_FEATURES
        + LAG_FEATURES
    )

    X_train = train_df[feature_names]
    y_train = train_df[TARGET]

    X_test = test_df[feature_names]
    y_test = test_df[TARGET]

    print("\n" + "=" * 60)
    print("TRAINING DATA")
    print("=" * 60)

    print("X_train:", X_train.shape)
    print("y_train:", y_train.shape)

    print("\nTESTING DATA")
    print("=" * 60)

    print("X_test:", X_test.shape)
    print("y_test:", y_test.shape)

    # -------------------------------------------------
    # 3. Train model
    # -------------------------------------------------

    model = train_model(
        X_train,
        y_train
    )

    # -------------------------------------------------
    # 4. Evaluate
    # -------------------------------------------------

    predictions, mae, rmse, r2 = evaluate_model(
        model,
        X_test,
        y_test
    )

    # -------------------------------------------------
    # 5. Feature importance
    # -------------------------------------------------

    importance = show_feature_importance(
        model,
        feature_names
    )

    # -------------------------------------------------
    # 6. Sample predictions
    # -------------------------------------------------

    comparison = show_prediction_samples(
        test_df,
        predictions
    )

    # -------------------------------------------------
    # 7. Save model
    # -------------------------------------------------

    save_model(
        model,
        feature_names,
        split_date
    )

    # -------------------------------------------------
    # 8. Final validation
    # -------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL MODEL TRAINING CHECK")
    print("=" * 60)

    print(
        "Training rows:",
        len(X_train)
    )

    print(
        "Testing rows:",
        len(X_test)
    )

    print(
        "Predictions generated:",
        len(predictions)
    )

    print(
        "Model file exists:",
        os.path.exists(MODEL_PATH)
    )

    print(
        "MAE:",
        round(mae, 4)
    )

    print(
        "RMSE:",
        round(rmse, 4)
    )

    print(
        "R²:",
        round(r2, 4)
    )

    if (
        len(predictions) == len(y_test)
        and os.path.exists(MODEL_PATH)
    ):
        print("\nMODEL TRAINING: PASS")
    else:
        print("\nMODEL TRAINING: CHECK REQUIRED")

    print("=" * 60)