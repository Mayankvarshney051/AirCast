NCR_CITIES = {
    "Delhi",
    "Gurugram",
    "Noida",
    "Ghaziabad",
    "Faridabad",
    "Greater Noida",
    "Sonipat",
    "Bahadurgarh",
    "Panipat",
    "Rohtak",
    "Rewari",
    "Bhiwani",
    "Jhajjar",
    "Palwal",
    "Alwar",
    "Bharatpur"
}


def is_ncr_city(city):
    """
    Check whether the city is part of Delhi-NCR
    for this application layer.
    """

    return city.strip().lower() in {
        name.lower()
        for name in NCR_CITIES
    }


# ============================================================
# DELHI-NCR GRAP LOGIC
# ============================================================

def get_grap_stage(aqi):
    """
    Determine GRAP stage from Delhi/NCR AQI.

    Stage I   : 201-300
    Stage II  : 301-400
    Stage III : 401-450
    Stage IV  : >450
    """

    aqi = float(aqi)

    if aqi <= 200:

        return {
            "stage": "No GRAP Stage",
            "category": "Below GRAP threshold"
        }

    elif aqi <= 300:

        return {
            "stage": "Stage I",
            "category": "Poor"
        }

    elif aqi <= 400:

        return {
            "stage": "Stage II",
            "category": "Very Poor"
        }

    elif aqi <= 450:

        return {
            "stage": "Stage III",
            "category": "Severe"
        }

    else:

        return {
            "stage": "Stage IV",
            "category": "Severe+"
        }


def get_grap_advisory(aqi):
    """
    Generate citizen-focused GRAP advisory
    for Delhi-NCR cities.
    """

    aqi = float(aqi)

    result = get_grap_stage(aqi)

    stage = result["stage"]

    advisories = {

        "No GRAP Stage": [
            "No GRAP stage is triggered by the AQI threshold",
            "Continue monitoring air quality"
        ],

        "Stage I": [
            "Reduce unnecessary pollution-generating activities",
            "Avoid open waste burning",
            "Prefer public transport or cleaner modes of travel",
            "Follow local pollution-control instructions"
        ],

        "Stage II": [
            "Reduce prolonged outdoor exposure",
            "Prefer public transport and shared mobility",
            "Avoid unnecessary use of private vehicles",
            "Avoid outdoor activities during peak pollution periods",
            "Follow local GRAP-related instructions"
        ],

        "Stage III": [
            "Avoid prolonged outdoor exposure",
            "Avoid strenuous outdoor exercise",
            "Sensitive individuals should remain indoors when possible",
            "Follow restrictions and instructions issued by authorities",
            "Prefer cleaner transport options"
        ],

        "Stage IV": [
            "Avoid unnecessary outdoor exposure",
            "Avoid outdoor physical activity",
            "Follow all applicable government restrictions",
            "Use public or cleaner transport where available",
            "Follow official emergency pollution advisories",
            "Monitor updates from CAQM and local authorities"
        ]
    }

    return {
        "aqi": round(aqi, 2),
        "grap_stage": stage,
        "aqi_category": result["category"],
        "recommendations": advisories[stage]
    }


# ============================================================
# NON-NCR AIR ACTION LEVEL
# ============================================================

def get_air_action_level(aqi):
    """
    Determine AirCast Air Action Level for non-NCR cities
    using AQI-based air quality categories.
    """

    aqi = float(aqi)

    if aqi <= 50:

        return {
            "level": "Good",
            "category": "Good"
        }

    elif aqi <= 100:

        return {
            "level": "Satisfactory",
            "category": "Satisfactory"
        }

    elif aqi <= 200:

        return {
            "level": "Moderate",
            "category": "Moderate"
        }

    elif aqi <= 300:

        return {
            "level": "Poor",
            "category": "Poor"
        }

    elif aqi <= 400:

        return {
            "level": "Very Poor",
            "category": "Very Poor"
        }

    else:

        return {
            "level": "Severe",
            "category": "Severe"
        }


def get_air_action_advisory(aqi):
    """
    Generate general air-quality advisory
    for non-NCR cities.
    """

    aqi = float(aqi)

    result = get_air_action_level(aqi)

    level = result["level"]

    advisories = {

        "Good": [
            "Normal outdoor activities are generally safe",
            "Continue routine air-quality monitoring"
        ],

        "Satisfactory": [
            "Normal outdoor activities are generally okay",
            "Sensitive individuals should monitor symptoms",
            "Continue monitoring air quality"
        ],

        "Moderate": [
            "Reduce prolonged outdoor exposure if discomfort occurs",
            "Sensitive individuals should limit strenuous outdoor activity",
            "Prefer cleaner transport options",
            "Continue monitoring air quality"
        ],

        "Poor": [
            "Reduce prolonged outdoor exposure",
            "Avoid strenuous outdoor activity",
            "Sensitive individuals should remain indoors when possible",
            "Prefer public transport and cleaner mobility"
        ],

        "Very Poor": [
            "Avoid prolonged outdoor exposure",
            "Avoid strenuous outdoor exercise",
            "Sensitive individuals should remain indoors when possible",
            "Reduce unnecessary vehicle use",
            "Follow local air-quality advisories"
        ],

        "Severe": [
            "Avoid unnecessary outdoor exposure",
            "Avoid outdoor physical activity",
            "Sensitive individuals should remain indoors",
            "Reduce unnecessary travel and vehicle use",
            "Follow official local pollution advisories"
        ]
    }

    return {
        "aqi": round(aqi, 2),
        "action_level": level,
        "aqi_category": result["category"],
        "recommendations": advisories[level]
    }


# ============================================================
# COMPLETE AIRCAST RESPONSE
# ============================================================

def generate_grap_response(city, aqi):
    """
    Complete air-quality policy response for AirCast.

    Delhi-NCR:
        Uses GRAP stages.

    Non-NCR:
        Uses AirCast Air Action Level based on AQI.
    """

    aqi = float(aqi)

    # --------------------------------------------------------
    # NON-NCR CITY
    # --------------------------------------------------------

    if not is_ncr_city(city):

        advisory = get_air_action_advisory(aqi)

        return {
            "city": city,
            "ncr_applicable": False,

            "grap_stage": "Not Applicable",

            "action_level": advisory["action_level"],

            "aqi": advisory["aqi"],

            "aqi_category": advisory["aqi_category"],

            "message": (
                "GRAP is specific to Delhi-NCR. "
                "AirCast provides a general air-quality "
                "action level for this city."
            ),

            "recommendations": advisory["recommendations"]
        }

    # --------------------------------------------------------
    # DELHI-NCR CITY
    # --------------------------------------------------------

    advisory = get_grap_advisory(aqi)

    return {
        "city": city,
        "ncr_applicable": True,

        "grap_stage": advisory["grap_stage"],

        "action_level": None,

        "aqi": advisory["aqi"],

        "aqi_category": advisory["aqi_category"],

        "message": (
            "Delhi-NCR GRAP assessment based on the provided AQI."
        ),

        "recommendations": advisory["recommendations"]
    }


# ============================================================
# TESTING
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AIRCAST AIR QUALITY ACTION ENGINE")
    print("=" * 60)

    # --------------------------------------------------------
    # TEST 1: Delhi - NCR GRAP
    # --------------------------------------------------------

    print("\nTEST 1: Delhi")

    city = "Delhi"
    aqi = 350

    result = generate_grap_response(
        city=city,
        aqi=aqi
    )

    print("\nCity:", result["city"])
    print("NCR applicable:", result["ncr_applicable"])
    print("AQI:", result["aqi"])
    print("AQI category:", result["aqi_category"])
    print("GRAP stage:", result["grap_stage"])
    print("Air Action Level:", result["action_level"])

    print("\nRecommendations:")

    for number, recommendation in enumerate(
        result["recommendations"],
        start=1
    ):
        print(f"{number}. {recommendation}")

    print("\n" + "-" * 60)

    # --------------------------------------------------------
    # TEST 2: Hyderabad - Non-NCR
    # --------------------------------------------------------

    print("\nTEST 2: Hyderabad")

    city = "Hyderabad"
    aqi = 350

    result = generate_grap_response(
        city=city,
        aqi=aqi
    )

    print("\nCity:", result["city"])
    print("NCR applicable:", result["ncr_applicable"])
    print("AQI:", result["aqi"])
    print("AQI category:", result["aqi_category"])
    print("GRAP stage:", result["grap_stage"])
    print("Air Action Level:", result["action_level"])

    print("\nRecommendations:")

    for number, recommendation in enumerate(
        result["recommendations"],
        start=1
    ):
        print(f"{number}. {recommendation}")

    print("\n" + "-" * 60)

    # --------------------------------------------------------
    # TEST 3: Mumbai - Non-NCR
    # --------------------------------------------------------

    print("\nTEST 3: Mumbai")

    city = "Mumbai"
    aqi = 150

    result = generate_grap_response(
        city=city,
        aqi=aqi
    )

    print("\nCity:", result["city"])
    print("NCR applicable:", result["ncr_applicable"])
    print("AQI:", result["aqi"])
    print("AQI category:", result["aqi_category"])
    print("GRAP stage:", result["grap_stage"])
    print("Air Action Level:", result["action_level"])

    print("\nRecommendations:")

    for number, recommendation in enumerate(
        result["recommendations"],
        start=1
    ):
        print(f"{number}. {recommendation}")

    print("\n" + "-" * 60)

    print("\nAIRCAST ACTION ENGINE: PASS")

    print("=" * 60)