from backend.services.risk import get_risk_details


def generate_advisory(pm25, city):
    """
    Generate health advisory based on predicted PM2.5.
    """

    pm25 = float(pm25)

    risk_details = get_risk_details(pm25)

    category = risk_details["category"]
    risk_level = risk_details["risk_level"]

    if category == "Good":

        recommendations = [
            "Outdoor activities are generally safe",
            "Normal exercise and daily activities can continue",
            "Continue monitoring air quality"
        ]

    elif category == "Satisfactory":

        recommendations = [
            "Normal outdoor activities are generally okay",
            "Sensitive individuals should monitor symptoms",
            "Consider reducing prolonged outdoor exposure if discomfort occurs",
            "Continue monitoring air quality"
        ]

    elif category == "Moderate":

        recommendations = [
            "Sensitive individuals should reduce prolonged outdoor exposure",
            "Consider taking breaks during outdoor activities",
            "People with respiratory sensitivity should monitor symptoms",
            "Keep monitoring air quality"
        ]

    elif category == "Poor":

        recommendations = [
            "Reduce prolonged outdoor activities",
            "Sensitive individuals should avoid strenuous outdoor exercise",
            "Consider wearing a suitable pollution mask outdoors",
            "Keep indoor areas well ventilated when outdoor pollution is lower",
            "Monitor air quality frequently"
        ]

    elif category == "Very Poor":

        recommendations = [
            "Avoid prolonged outdoor exposure",
            "Avoid strenuous outdoor exercise",
            "Sensitive individuals should remain indoors when possible",
            "Use a suitable pollution mask if outdoor travel is necessary",
            "Keep doors and windows closed during peak pollution periods",
            "Monitor air quality frequently"
        ]

    else:

        recommendations = [
            "Avoid unnecessary outdoor exposure",
            "Avoid outdoor exercise",
            "Sensitive individuals should remain indoors",
            "Use a suitable pollution mask if outdoor travel is unavoidable",
            "Keep indoor air clean where possible",
            "Follow local government pollution advisories",
            "Monitor air quality continuously"
        ]

    return {
        "city": city,
        "predicted_pm25": round(pm25, 2),
        "category": category,
        "risk_level": risk_level,
        "summary": risk_details["message"],
        "recommendations": recommendations
    }


if __name__ == "__main__":

    print("=" * 60)
    print("AIRCAST ADVISORY ENGINE")
    print("=" * 60)

    predicted_pm25 = 51.28
    city = "Ahmedabad"

    advisory = generate_advisory(
        pm25=predicted_pm25,
        city=city
    )

    print(f"\nCity: {advisory['city']}")
    print(
        f"Predicted PM2.5: "
        f"{advisory['predicted_pm25']} µg/m³"
    )

    print(f"Category: {advisory['category']}")
    print(f"Risk Level: {advisory['risk_level']}")

    print("\nSummary:")
    print(advisory["summary"])

    print("\nRecommendations:")

    for number, recommendation in enumerate(
        advisory["recommendations"],
        start=1
    ):
        print(f"{number}. {recommendation}")

    print("\nAdvisory engine: PASS")
    print("=" * 60)