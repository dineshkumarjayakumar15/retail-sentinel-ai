import os
import sys
from typing import List
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import Detection
from utils.logger import ai_logger

class BasketDetector:
    _instance = None
    model = None
    is_supported: bool = False

    def __new__(cls, model_path: str = None):
        if cls._instance is None:
            cls._instance = super(BasketDetector, cls).__new__(cls)
            cls._instance._init_model(model_path)
        return cls._instance

    def _init_model(self, model_path: str = None):
        target_path = model_path or ai_settings.BASKET_MODEL_PATH
        
        if not target_path or not os.path.exists(target_path):
            ai_logger.info(f"Basket detection model not configured or missing at '{target_path}'. Operating in UNSUPPORTED mode (honest 0 count).")
            self.model = None
            self.is_supported = False
            return

        try:
            ai_logger.info(f"Loading Custom Basket Detection Model from '{target_path}'...")
            from ultralytics import YOLO
            self.model = YOLO(target_path)
            self.is_supported = True
            ai_logger.info("Custom Basket Detection Model loaded successfully!")
        except Exception as e:
            ai_logger.warning(f"Failed to load custom basket model ({e}). Operating in UNSUPPORTED mode.")
            self.model = None
            self.is_supported = False

    def detect(self, frame: np.ndarray, conf_threshold: float = 0.35) -> List[Detection]:
        """
        Runs basket detection on a single frame.
        Returns empty list [] if basket detector is unconfigured or unsupported.
        """
        if not self.is_supported or self.model is None:
            return []

        detections: List[Detection] = []
        try:
            results = self.model(frame, verbose=False, conf=conf_threshold)
            if results and len(results) > 0:
                boxes = results[0].boxes
                for box in boxes:
                    conf = float(box.conf[0].item())
                    xyxy = box.xyxy[0].tolist()
                    detections.append(Detection(
                        bbox=xyxy,
                        confidence=conf,
                        class_id=1,
                        class_name="basket"
                    ))
        except Exception as e:
            ai_logger.error(f"Error during Basket Detector frame inference: {e}")

        return detections

    def detect_baskets(self, frame: np.ndarray, conf_threshold: float = 0.35) -> List[Detection]:
        """Alias for detect() method."""
        return self.detect(frame, conf_threshold=conf_threshold)
