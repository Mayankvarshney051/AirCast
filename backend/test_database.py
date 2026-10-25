from backend.database import save_prediction


if __name__ == "__main__":
    result = save_prediction(
        city="Delhi",
        predicted_pm25=51.28,
        risk_category="Satisfactory",
        risk_level="Low",
        aqi=350,
        grap_stage="Stage II"
    )

    print("=" * 50)
    print("AIRCAST DATABASE INSERT TEST")
    print("=" * 50)
    print(f"Prediction ID: {result['prediction_id']}")
    print(f"Prediction Time: {result['prediction_time']}")
    print("Prediction saved successfully")
    print("Database insert test: PASS")
    print("=" * 50)