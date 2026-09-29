from ultralytics import YOLO

model = YOLO("ml/models/model.pt")

print("Poultry disease model loaded successfully!")
print("Model classes:")

for class_id, class_name in model.names.items():
    print(class_id, ":", class_name)