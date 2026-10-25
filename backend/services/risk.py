def classify_pm25(pm25):
    """
    Classify predicted PM2.5 level.
    """

    pm25 = float(pm25)

    if pm25 <= 30:
        return "Good"

    elif pm25 <= 60:
        return "Satisfactory"

    elif pm25 <= 90:
        return "Moderate"

    elif pm25 <= 120:
        return "Poor"

    elif pm25 <= 250:
        return "Very Poor"

    else:
        return "Severe"


def get_risk_level(category):
    """
    Convert PM2.5 category into project risk level.
    """

    if category in ["Good", "Satisfactory"]:
        return "Low"

    elif category == "Moderate":
        return "Medium"

    elif category == "Poor":
        return "High"

    elif category == "Very Poor":
        return "Very High"

    else:
        return "Severe"


def get_risk_details(pm25):
    """
    Return complete risk information.
    """

    pm25 = float(pm25)

    category = classify_pm25(pm25)
    risk_level = get_risk_level(category)

    messages = {
        "Good": "Air quality is good",
        "Satisfactory": "Air quality is satisfactory",
        "Moderate": "Air quality may affect sensitive individuals",
        "Poor": "Air quality may cause health effects",
        "Very Poor": "Air quality is unhealthy",
        "Severe": "Air quality is severely polluted"
    }

    return {
        "pm25": round(pm25, 2),
        "category": category,
        "risk_level": risk_level,
        "message": messages[category]
    }
