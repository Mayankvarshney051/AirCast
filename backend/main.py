from fastapi import FastAPI
from pydantic import BaseModel, Field
from functools import lru_cache

from backend.ml.predict import predict_pm25
from backend.ml.explain import calculate_feature_importance

from backend.services.risk import get_risk_details
from backend.services.advisory import generate_advisory
from backend.services.grap import generate_grap_response

from backend.database import save_prediction, get_prediction_history

from fastapi.middleware.cors import CORSMiddleware


# --------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="AirCast API",
    description="AI-Based Air Quality Forecasting & Advisory System",
    version="1.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# INPUT MODEL
# --------------------------------------------------

class AirQualityInput(BaseModel):

    city: str

    pm10: float = Field(ge=0)
    no: float = Field(ge=0)
    no2: float = Field(ge=0)
    nox: float = Field(ge=0)
    nh3: float = Field(ge=0)
    co: float = Field(ge=0)
    so2: float = Field(ge=0)
    o3: float = Field(ge=0)

    hour: int = Field(ge=0, le=23)
    month: int = Field(ge=1, le=12)
    day_of_week: int = Field(ge=0, le=6)

    pm25_lag_24: float = Field(ge=0)
    pm25_lag_48: float = Field(ge=0)

    aqi: float | None = Field(default=None, ge=0)


# --------------------------------------------------
# XAI CACHE
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_xai_result():

    return calculate_feature_importance()


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.get("/")
def home():

    return {
        "message": "AirCast Backend is Running",
        "status": "success"
    }


# --------------------------------------------------
# PREDICTION API
# --------------------------------------------------

@app.post("/predict")
def predict_air_quality(data: AirQualityInput):

    # ----------------------------------------------
    # 1. PM2.5 PREDICTION
    # ----------------------------------------------

    predicted_pm25 = predict_pm25(

        pm10=data.pm10,

        no=data.no,

        no2=data.no2,

        nox=data.nox,

        nh3=data.nh3,

        co=data.co,

        so2=data.so2,

        o3=data.o3,

        hour=data.hour,

        month=data.month,

        day_of_week=data.day_of_week,

        pm25_lag_24=data.pm25_lag_24,

        pm25_lag_48=data.pm25_lag_48
    )

    predicted_pm25 = float(predicted_pm25)


    # ----------------------------------------------
    # 2. RISK CLASSIFICATION
    # ----------------------------------------------

    risk = get_risk_details(
        predicted_pm25
    )


    # ----------------------------------------------
    # 3. HEALTH ADVISORY
    # ----------------------------------------------

    advisory = generate_advisory(
        pm25=predicted_pm25,
        city=data.city
    )


    # ----------------------------------------------
    # 4. AQI / GRAP
    # ----------------------------------------------

    aqi = data.aqi

    if aqi is not None:

        grap = generate_grap_response(
            data.city,
            aqi
        )

        if grap["ncr_applicable"] is True:

            # Delhi-NCR
            grap_stage = grap["grap_stage"]

        elif grap["ncr_applicable"] is False:

            # Non-NCR
            grap_stage = f"Action: {grap['action_level']}"

        else:

            grap_stage = "AQI Required"

    else:

        grap = {
            "city": data.city,
            "ncr_applicable": None,
            "grap_stage": "AQI Required",
            "action_level": "AQI Required",
            "message": "AQI is required for air-quality action assessment",
            "recommendations": []
        }

        grap_stage = "AQI Required"


    # ----------------------------------------------
    # 5. DATABASE LOGGING
    # ----------------------------------------------

   # ----------------------------------------------
# 5. DATABASE LOGGING
# ----------------------------------------------

    try:
        db_record = save_prediction(
            city=data.city,
            predicted_pm25=predicted_pm25,
            risk_category=risk["category"],
            risk_level=risk["risk_level"],
            aqi=aqi,
            grap_stage=grap_stage
        )

        db_response = {
            "status": "saved",
            "prediction_id": db_record["prediction_id"],
            "prediction_time": db_record["prediction_time"].isoformat()
        }

    except Exception as e:
        print(f"Warning: Database logging failed: {e}")
        db_response = {
            "status": "offline",
            "prediction_id": "OFFLINE",
            "prediction_time": "Not Logged"
        }


    # ----------------------------------------------
    # 6. API RESPONSE
    # ----------------------------------------------

    return {

        "city": data.city,

        "prediction": {

            "predicted_pm25_24h":
                round(
                    predicted_pm25,
                    2
                ),

            "unit":
                "µg/m³"
        },

        "risk": risk,

        "advisory": advisory,

        "grap": grap,

        "database": db_response
    }


# --------------------------------------------------
# XAI / EXPLAINABILITY API
# --------------------------------------------------

@app.get("/explain")
def explain_model():

    explanation = get_xai_result()

    return {

        "status": "success",

        "explainability":
            explanation
    }


# --------------------------------------------------
# PREDICTION HISTORY API
# --------------------------------------------------

@app.get("/history")
def prediction_history(limit: int = 20):

    try:

        history = get_prediction_history(
            limit
        )

        return {

            "status": "success",

            "count": len(history),

            "history": history
        }

    except Exception as e:

        return {

            "status": "error",

            "message": str(e),

            "history": []
        }