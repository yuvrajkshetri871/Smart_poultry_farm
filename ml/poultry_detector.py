from ultralytics import YOLO
from pathlib import Path

# Find model.pt relative to this file
MODEL_PATH = Path(__file__).parent / "models" / "model.pt"

# Load YOLO model
model = YOLO(str(MODEL_PATH))

print("================================")
print("POULTRY MODEL CLASSES")
print("================================")
print(model.names)
print("================================")


def detect_poultry_signs(image_path):
    """
    Detect poultry disease signs from a chicken image.
    """

    results = model(image_path)

    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]

            detections.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": round(confidence * 100, 2)
            })

    # Keep only the highest-confidence detection for each disease sign
    best_detections = {}

    for detection in detections:
        class_name = detection["class_name"]

        if (
            class_name not in best_detections
            or detection["confidence"] > best_detections[class_name]["confidence"]
        ):
            best_detections[class_name] = detection

    detections = list(best_detections.values())

    # Highest confidence first
    detections.sort(
        key=lambda x: x["confidence"],
        reverse=True
    )

    return detections