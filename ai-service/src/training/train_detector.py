"""
Retail Sentinel AI - Detector Training Module
Trains custom YOLO object detection models and saves trained weights to data/models/.
"""

import os
import argparse
from ai_service.src.config import ai_settings
from ai_service.src.utils.logger import ai_logger

def train_detector(dataset_yaml: str, epochs: int = 10, imgsz: int = 640):
    ai_logger.info(f"Initiating YOLO Detector Training using '{dataset_yaml}' for {epochs} epochs...")
    try:
        from ultralytics import YOLO
        model = YOLO(ai_settings.YOLO_MODEL)
        results = model.train(
            data=dataset_yaml,
            epochs=epochs,
            imgsz=imgsz,
            project=ai_settings.MODEL_PATH,
            name="custom_yolo_sentinel",
            exist_ok=True
        )
        ai_logger.info(f"Detector training complete! Weights saved to {ai_settings.MODEL_PATH}/custom_yolo_sentinel/weights/best.pt")
        return results
    except Exception as e:
        ai_logger.error(f"Detector training failed: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", type=str, required=True, help="Path to dataset.yaml")
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    train_detector(args.yaml, args.epochs)
