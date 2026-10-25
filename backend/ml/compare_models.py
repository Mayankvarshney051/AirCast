import os
import joblib

from sklearn.ensemble import (
    RandomForestRegressor,
    HistGradientBoostingRegressor
)
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


def evaluate_model(model, X_train, y_train, X_test, y_test):

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    r2 = r2_score(y_test, predictions)

    return model, mae, rmse, r2


def main():

    print("=" * 60)
    print("AirCast - Model Comparison")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Prepare data using existing preprocessing pipeline
    # --------------------------------------------------

    print("\nLoading dataset...")

    df = load_data()

    df = handle_pm25_missing(df)

    df = create_time_features(df)

    df = create_lag_and_target_features(df)

    df = impute_selected_features(df)

    model_df = create_model_dataset(df)

    train_df, test_df, split_date = time_based_split(model_df)

    model_features = (
        SELECTED_FEATURES
        + TIME_FEATURES
        + LAG_FEATURES
    )

    X_train = train_df[model_features]
    y_train = train_df[TARGET]

    X_test = test_df[model_features]
    y_test = test_df[TARGET]

    print("\nModel features:")
    print(model_features)

    print("\nTarget:")
    print(TARGET)

    print("\nTraining rows:", len(train_df))
    print("Testing rows:", len(test_df))
    print("Split date:", split_date)

    print("\nTraining models...\n")

    # --------------------------------------------------
    # 2. Random Forest - Baseline
    # --------------------------------------------------

    random_forest = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    rf_model, rf_mae, rf_rmse, rf_r2 = evaluate_model(
        random_forest,
        X_train,
        y_train,
        X_test,
        y_test
    )

    print("Random Forest")
    print(f"MAE  : {rf_mae:.4f}")
    print(f"RMSE : {rf_rmse:.4f}")
    print(f"R²   : {rf_r2:.4f}")

    # --------------------------------------------------
    # 3. HistGradientBoosting
    # --------------------------------------------------

    hgb_model = HistGradientBoostingRegressor(
        learning_rate=0.08,
        max_iter=300,
        max_leaf_nodes=31,
        min_samples_leaf=30,
        l2_regularization=1.0,
        early_stopping=True,
        validation_fraction=0.1,
        random_state=42
    )

    hgb_model, hgb_mae, hgb_rmse, hgb_r2 = evaluate_model(
        hgb_model,
        X_train,
        y_train,
        X_test,
        y_test
    )

    print("\nHistGradientBoosting")
    print(f"MAE  : {hgb_mae:.4f}")
    print(f"RMSE : {hgb_rmse:.4f}")
    print(f"R²   : {hgb_r2:.4f}")

    # --------------------------------------------------
    # 4. Select final model
    # --------------------------------------------------

    if (
        hgb_mae < rf_mae
        and hgb_rmse < rf_rmse
        and hgb_r2 > rf_r2
    ):
        best_model = hgb_model
        best_model_name = "HistGradientBoosting"

    else:
        best_model = rf_model
        best_model_name = "RandomForest"

    print("\n" + "=" * 60)
    print("FINAL MODEL SELECTION")
    print("=" * 60)

    print("Selected Model:", best_model_name)

    # --------------------------------------------------
    # 5. Save final deployed model
    # --------------------------------------------------

    os.makedirs("models", exist_ok=True)

    model_package = {
        "model": best_model,
        "model_name": best_model_name,
        "features": model_features,
        "target": TARGET,
        "split_date": split_date
    }

    joblib.dump(model_package, MODEL_PATH)

    print("\nFinal model saved to:", MODEL_PATH)
    print("Model package saved successfully.")

    print("\n" + "=" * 60)
    print("Comparison completed")
    print("=" * 60)


if __name__ == "__main__":
    main()