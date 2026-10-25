import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "aircast_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def save_prediction(
    city,
    predicted_pm25,
    risk_category,
    risk_level,
    aqi,
    grap_stage
):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            INSERT INTO predictions (
                city,
                predicted_pm25,
                risk_category,
                risk_level,
                aqi,
                grap_stage
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING prediction_id, prediction_time
        """

        cursor.execute(
            query,
            (
                city,
                predicted_pm25,
                risk_category,
                risk_level,
                aqi,
                grap_stage,
            ),
        )

        result = cursor.fetchone()
        conn.commit()

        return {
            "prediction_id": result[0],
            "prediction_time": result[1],
        }

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()


def get_prediction_history(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        query = """
            SELECT
                prediction_id,
                city,
                predicted_pm25,
                risk_category,
                risk_level,
                aqi,
                grap_stage,
                prediction_time
            FROM predictions
            ORDER BY prediction_time DESC
            LIMIT %s
        """

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()

        history = []

        for row in rows:
            history.append({
                "prediction_id": row[0],
                "city": row[1],
                "predicted_pm25": row[2],
                "risk_category": row[3],
                "risk_level": row[4],
                "aqi": row[5],
                "grap_stage": row[6],
                "prediction_time": row[7],
            })

        return history

    finally:
        cursor.close()
        conn.close()