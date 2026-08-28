import os
import sys
from typing import List
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import Detection
from utils.logger import ai_logger

class YOLODetector:
    _instance = None
    model = None

    def __new__(cls, model_name: str = None):
        if cls._instance is None:
            cls._instance = super(YOLODetector, cls).__new__(cls)
            cls._instance._init_model(model_name)
        return cls._instance

    def _init_model(self, model_name: str = None):
        target_model = model_name or ai_settings.YOLO_MODEL
        ai_logger.info(f"Loading YOLO Model '{target_model}' (Single-Instance Model Loader)...")
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(target_model)
            ai_logger.info(f"YOLO Model '{target_model}' loaded successfully!")
        except Exception as e:
            ai_logger.warning(f"Ultralytics YOLO load exception ({e}). Operating in fallback detection mode.")
            self.model = None

    def detect(self, frame: np.ndarray, conf_threshold: float = None) -> List[Detection]:
        """
        Runs object detection on a single video frame.
        Filters detections strictly for Person (COCO class 0).
        """
        if conf_threshold is None:
            conf_threshold = ai_settings.YOLO_CONFIDENCE

        detections: List[Detection] = []

        if self.model is not None:
            try:
                results = self.model(frame, verbose=False, conf=conf_threshold)
                if results and len(results) > 0:
                    boxes = results[0].boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].item())
                        conf = float(box.conf[0].item())
                        xyxy = box.xyxy[0].tolist()

                        # Class 0 in COCO is person
                        if cls_id == 0:
                            detections.append(Detection(
                                bbox=xyxy,
                                confidence=conf,
                                class_id=cls_id,
                                class_name="person"
                            ))
            except Exception as e:
                ai_logger.error(f"Error during YOLO frame inference: {e}")

        return detections

    def detect_persons(self, frame: np.ndarray, conf_threshold: float = None) -> List[Detection]:
        """Alias for detect() method."""
        return self.detect(frame, conf_threshold=conf_threshold)
