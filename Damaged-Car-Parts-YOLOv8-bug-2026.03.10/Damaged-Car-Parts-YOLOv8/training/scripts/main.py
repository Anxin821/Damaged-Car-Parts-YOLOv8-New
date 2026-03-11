from pathlib import Path
from ultralytics import YOLO

# Load a model
model = YOLO("yolov8n.yaml")  # build a new model from scratch

# Use the model
_config_path = (Path(__file__).resolve().parent / "config.yaml").as_posix()
results = model.train(data=_config_path, epochs=5000)  # train the model
