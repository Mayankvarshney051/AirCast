import joblib
import pandas as pd


MODEL_PATH = "models/trained_model.pkl"


def load_model():

    package = joblib.load(MODEL_PATH)

    model = package["model"]
    features = package["features"]

    return model, features


def predict_pm25(
    pm10,
    no,
    no2,
    nox,
    nh3,
    co,
    so2,
    o3,
    hour,
    month,
    day_of_week,
    pm25_lag_24,
    pm25_lag_48
):

    model, features = load_model()

    input_data = pd.DataFrame([{
        "PM10": pm10,
        "NO": no,
        "NO2": no2,
        "NOx": nox,
        "NH3": nh3,
        "CO": co,
        "SO2": so2,
        "O3": o3,
        "Hour": hour,
        "Month": month,
        "DayOfWeek": day_of_week,
        "PM2.5_lag_24": pm25_lag_24,
        "PM2.5_lag_48": pm25_lag_48
    }])

    # Keep exact training feature order
    input_data = input_data[features]

    prediction = model.predict(input_data)[0]

    # PM2.5 cannot be negative
    prediction = max(0, prediction)

    return float(prediction)


if __name__ == "__main__":

    print("=" * 60)
    print("AIRCAST 24-HOUR PM2.5 PREDICTION")
    print("=" * 60)

    # Example input
    # Ahmedabad-type example observation

    prediction = predict_pm25(
        pm10=80,
        no=20,
        no2=35,
        nox=45,
        nh3=20,
        co=1.0,
        so2=15,
        o3=40,
        hour=15,
        month=12,
        day_of_week=3,
        pm25_lag_24=60,
        pm25_lag_48=55
    )

    print("\nInput successfully processed")

    print(
        f"\nPredicted PM2.5 after 24 hours: "
        f"{prediction:.2f} µg/m³"
    )

    print("\nPrediction service: PASS")
    print("=" * 60)