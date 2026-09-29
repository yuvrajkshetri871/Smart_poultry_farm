def egg_production_rate(birds, eggs):
    """Calculate percentage of birds producing eggs."""
    if birds <= 0:
        return 0

    return round((eggs / birds) * 100, 2)


def mortality_rate(birds, mortality):
    """Calculate mortality percentage."""
    if birds <= 0:
        return 0

    return round((mortality / birds) * 100, 2)


def feed_efficiency(eggs, feed):
    """Calculate eggs produced per kg of feed."""
    if feed <= 0:
        return 0

    return round(eggs / feed, 2)


def environmental_risk(temperature, humidity):
    """
    Estimate environmental risk.

    This is a rule-based algorithm, not ML.
    """
    risk = 0

    # Temperature risk
    if temperature < 18 or temperature > 32:
        risk += 2
    elif temperature < 20 or temperature > 30:
        risk += 1

    # Humidity risk
    if humidity < 40 or humidity > 80:
        risk += 2
    elif humidity < 50 or humidity > 70:
        risk += 1

    if risk >= 4:
        return "HIGH"
    elif risk >= 2:
        return "WARNING"
    else:
        return "NORMAL"


def overall_risk(
    birds,
    mortality,
    temperature,
    humidity,
    performance
):
    """
    Calculate overall farm risk using multiple conditions.
    """

    score = 0

    # Mortality condition
    mortality_percentage = mortality_rate(birds, mortality)

    if mortality_percentage > 2:
        score += 3
    elif mortality_percentage > 1:
        score += 1

    # Temperature condition
    if temperature < 18 or temperature > 32:
        score += 3
    elif temperature < 20 or temperature > 30:
        score += 1

    # Humidity condition
    if humidity < 40 or humidity > 80:
        score += 3
    elif humidity < 50 or humidity > 70:
        score += 1

    # Performance condition
    if performance < 60:
        score += 3
    elif performance < 75:
        score += 1

    # Final classification
    if score >= 6:
        return "HIGH RISK"
    elif score >= 3:
        return "WARNING"
    else:
        return "NORMAL"


def analyze_farm(data):
    """
    Main farm analysis function.

    Returns all calculated indicators.
    """

    birds = data["birds"]
    eggs = data["eggs"]
    feed = data["feed"]
    temperature = data["temperature"]
    humidity = data["humidity"]
    mortality = data["mortality"]
    performance = data["performance"]

    return {
        "egg_rate": egg_production_rate(birds, eggs),

        "mortality_rate": mortality_rate(
            birds,
            mortality
        ),

        "feed_efficiency": feed_efficiency(
            eggs,
            feed
        ),

        "environmental_risk": environmental_risk(
            temperature,
            humidity
        ),

        "overall_risk": overall_risk(
            birds,
            mortality,
            temperature,
            humidity,
            performance
        )
    }