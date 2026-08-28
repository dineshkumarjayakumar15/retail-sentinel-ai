import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import TrackedEntity, Detection, EventPayload

class BasketManager:
    def __init__(self):
        self.next_basket_id = 1
        self.active_baskets: Dict[str, TrackedEntity] = {}
        self.exited_baskets: Dict[str, TrackedEntity] = {}
        self.last_active_event_time: Dict[str, float] = {}

    def update_baskets(
        self,
        basket_detections: List[Detection],
        current_time_sec: float
    ) -> Tuple[List[TrackedEntity], List[TrackedEntity], List[TrackedEntity]]:
        """
        Updates active basket states.
        Returns: (newly_detected_baskets, active_basket_list, newly_exited_baskets)
        """
        now = datetime.utcnow()
        newly_detected: List[TrackedEntity] = []
        newly_exited: List[TrackedEntity] = []
        current_tracking_ids = set()

        if basket_detections:
            for det in basket_detections:
                matched_id = None
                b_center = ((det.bbox[0] + det.bbox[2])/2.0, (det.bbox[1] + det.bbox[3])/2.0)

                for b_id, b_entity in self.active_baskets.items():
                    prev_center = ((b_entity.bbox[0] + b_entity.bbox[2])/2.0, (b_entity.bbox[1] + b_entity.bbox[3])/2.0)
                    dist = ((b_center[0] - prev_center[0])**2 + (b_center[1] - prev_center[1])**2)**0.5
                    if dist < 120.0:
                        matched_id = b_id
                        break

                if matched_id is None:
                    basket_id = f"basket_{self.next_basket_id:03d}"
                    self.next_basket_id += 1
                    basket = TrackedEntity(
                        tracking_id=basket_id,
                        bbox=det.bbox,
                        first_seen_time=now,
                        last_seen_time=now,
                        status="ACTIVE"
                    )
                    self.active_baskets[basket_id] = basket
                    self.last_active_event_time[basket_id] = current_time_sec
                    newly_detected.append(basket)
                    current_tracking_ids.add(basket_id)
                else:
                    b_entity = self.active_baskets[matched_id]
                    b_entity.bbox = det.bbox
                    b_entity.last_seen_time = now
                    current_tracking_ids.add(matched_id)

        # Handle Disappearance Exit Logic (disappeared >= TRACK_DISAPPEARANCE_SECONDS)
        disappeared_ids = []
        for b_id, b_entity in list(self.active_baskets.items()):
            if b_id not in current_tracking_ids:
                time_since_last_seen = (now - b_entity.last_seen_time).total_seconds()
                if time_since_last_seen >= ai_settings.TRACK_DISAPPEARANCE_SECONDS:
                    b_entity.status = "INACTIVE"
                    disappeared_ids.append(b_id)
                    newly_exited.append(b_entity)
                    self.exited_baskets[b_id] = b_entity

        for b_id in disappeared_ids:
            del self.active_baskets[b_id]
            if b_id in self.last_active_event_time:
                del self.last_active_event_time[b_id]

        return newly_detected, list(self.active_baskets.values()), newly_exited

    def should_send_active_event(self, tracking_id: str, current_time_sec: float) -> bool:
        """Throttles active basket events to prevent database event spam."""
        last_time = self.last_active_event_time.get(tracking_id, 0.0)
        if current_time_sec - last_time >= ai_settings.BASKET_ACTIVE_INTERVAL_SECONDS:
            self.last_active_event_time[tracking_id] = current_time_sec
            return True
        return False

    def update(
        self,
        tracks: List[Tuple[str, List[float], float]] = None,
        video_id: int = 1,
        timestamp_seconds: float = 0.0,
        associations: Dict[str, Tuple[str, float]] = None
    ) -> List[EventPayload]:
        """Convenience update method returning EventPayload list."""
        return []
