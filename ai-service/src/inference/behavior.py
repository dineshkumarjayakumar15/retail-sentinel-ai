import os
import sys
import pickle
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import TrackedEntity, EventPayload
from utils.logger import ai_logger

class BehaviorEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BehaviorEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self.model_path = ai_settings.BEHAVIOR_MODEL_PATH
        self.model_loaded = False
        self.weights = None
        self.bias = 0.0
        self.zone_entry_timestamps: Dict[str, float] = {}

        if self.model_path and os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    model_data = pickle.load(f)
                    self.weights = model_data.get("weights")
                    self.bias = model_data.get("bias", 0.0)
                    self.model_loaded = True
                    ai_logger.info(f"Loaded Behavior Classification Model from '{self.model_path}' successfully!")
            except Exception as e:
                ai_logger.warning(f"Failed to load behavior classifier weights from '{self.model_path}': {e}")
        else:
            ai_logger.info(f"Behavior model weights not found at '{self.model_path}'. Using rule-based behavioral window evaluator.")

    def analyze_customer_behavior(
        self,
        customer: TrackedEntity,
        current_time_sec: float
    ) -> Optional[Dict[str, Any]]:
        """
        Analyzes customer spatial and temporal behavior across a 5-second window.
        Returns behavioral event payload with normalized suspicion_score (0.0 - 1.0)
        when suspicion exceeds SUSPICION_THRESHOLD (0.75).
        """
        tracking_id = customer.tracking_id
        zone = customer.zone or "shopping_area"

        # Track zone duration
        key = f"{tracking_id}_{zone}"
        if key not in self.zone_entry_timestamps:
            self.zone_entry_timestamps[key] = current_time_sec

        zone_duration = current_time_sec - self.zone_entry_timestamps[key]
        window_duration = ai_settings.BEHAVIOR_WINDOW_SECONDS

        # Feature vector based on spatial duration, zone weight, stay time, and bbox size
        bbox = customer.bbox or [0, 0, 100, 100]
        bbox_area = max(1.0, (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]))
        
        # Calculate suspicion score
        if self.model_loaded and self.weights is not None:
            feat = np.zeros((32, 1))
            feat[0] = min(1.0, zone_duration / 10.0)
            feat[1] = 1.0 if zone == "shelf_zone" else 0.3
            feat[2] = min(1.0, customer.stay_duration / 60.0)
            feat[3] = min(1.0, bbox_area / 200000.0)

            logit = float(np.dot(self.weights.T, feat)[0, 0] + self.bias)
            suspicion_score = 1.0 / (1.0 + np.exp(-np.clip(logit, -15, 15)))
            suspicion_score = round(float(suspicion_score), 2)
        else:
            base_score = 0.40 if zone == "shelf_zone" else 0.15
            duration_factor = min(0.45, (zone_duration / 8.0) * 0.45)
            suspicion_score = round(min(0.98, base_score + duration_factor), 2)

        # Trigger SUSPICIOUS_BEHAVIOR event if suspicion_score >= SUSPICION_THRESHOLD
        if suspicion_score >= ai_settings.SUSPICION_THRESHOLD and zone_duration >= window_duration:
            window_start = max(0.0, round(current_time_sec - window_duration, 1))
            window_end = round(current_time_sec, 1)

            return {
                "event_type": "SUSPICIOUS_BEHAVIOR",
                "confidence": suspicion_score,
                "metadata": {
                    "suspicion_score": suspicion_score,
                    "window_start": window_start,
                    "window_end": window_end,
                    "interaction_duration": round(zone_duration, 1),
                    "zone": zone,
                    "model_name": "behavior_classifier"
                }
            }

        return None

    def analyze_frame_tracks(
        self,
        tracks: List[Tuple[str, List[float], float]],
        video_id: int,
        timestamp_seconds: float,
        associations: Dict[str, Tuple[str, float]] = None
    ) -> List[EventPayload]:
        """Convenience method evaluating active tracks in a frame and returning EventPayload list."""
        events: List[EventPayload] = []
        from events.event_generator import EventGenerator
        gen = EventGenerator()

        for item in tracks:
            tracking_id = item[0]
            bbox = item[1]
            cust = TrackedEntity(
                tracking_id=tracking_id,
                bbox=bbox,
                first_seen_time=datetime.utcnow(),
                last_seen_time=datetime.utcnow(),
                zone="shopping_area",
                status="ACTIVE"
            )
            res = self.analyze_customer_behavior(cust, timestamp_seconds)
            if res:
                evt = gen.create_behavior_event(video_id, tracking_id, res, timestamp_seconds, cust.zone)
                if evt:
                    events.append(evt)
        return events
