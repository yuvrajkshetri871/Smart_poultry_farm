from sklearn.ensemble import RandomForestClassifier
import random


def generate_training_data():
    """
    Generate sample poultry farm data for ML training.
    """

    X = []
    y = []

    for _ in range(1000):

        birds = random.randint(500, 5000)
        eggs = random.randint(200, birds)
        feed = random.uniform(50, 600)
        water = random.uniform(100, 1000)
        temperature = random.uniform(15, 40)
        humidity = random.uniform(30, 90)
        mortality = random.randint(0, 100)
        performance = random.uniform(40, 100)

        # Create training label using farm conditions
        risk_score = 0

        if temperature < 18 or temperature > 32:
            risk_score += 2

        if humidity < 40 or humidity > 80:
            risk_score += 2

        mortality_rate = (mortality / birds) * 100

        if mortality_rate > 2:
            risk_score += 3
        elif mortality_rate > 1:
            risk_score += 1

        if performance < 60:
            risk_score += 3
        elif performance < 75:
            risk_score += 1

        if risk_score >= 6:
            risk = "HIGH RISK"
        elif risk_score >= 3:
            risk = "WARNING"
        else:
            risk = "NORMAL"

        X.append([
            birds,
            eggs,
            feed,
            water,
            temperature,
            humidity,
            mortality,
            performance
        ])

        y.append(risk)

    return X, y


# Generate training data
X_train, y_train = generate_training_data()

# Create ML model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# Train model
model.fit(X_train, y_train)


def predict_risk(data):
    """
    Predict poultry farm risk using Machine Learning.
    """

    features = [[
        data["birds"],
        data["eggs"],
        data["feed"],
        data["water"],
        data["temperature"],
        data["humidity"],
        data["mortality"],
        data["performance"]
    ]]

    prediction = model.predict(features)[0]

    return prediction