import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import TrackedEntity, EventPayload
from zones.zone_manager import ZoneManager

class CustomerManager:
    def __init__(self, zone_manager: ZoneManager):
        self.zone_manager = zone_manager
        self.active_customers: Dict[str, TrackedEntity] = {}
        self.exited_customers: Dict[str, TrackedEntity] = {}
        self.last_active_event_time: Dict[str, float] = {}

    def update_customers(
        self,
        current_tracks: List[Tuple[str, List[float], float]],
        current_time_sec: float,
        frame_width: int,
        frame_height: int
    ) -> Tuple[List[TrackedEntity], List[TrackedEntity], List[TrackedEntity]]:
        """
        Updates active customer states.
        Returns: (newly_entered_customers, active_customer_list, newly_exited_customers)
        """
        now = datetime.utcnow()
        newly_entered: List[TrackedEntity] = []
        newly_exited: List[TrackedEntity] = []
        current_tracking_ids = set()

        for tracking_id, bbox, conf in current_tracks:
            current_tracking_ids.add(tracking_id)
            zone = self.zone_manager.get_zone_for_bbox(bbox, frame_width, frame_height)

            if tracking_id not in self.active_customers:
                # New Customer Entered
                customer = TrackedEntity(
                    tracking_id=tracking_id,
                    bbox=bbox,
                    first_seen_time=now,
                    last_seen_time=now,
                    zone=zone,
                    status="ACTIVE"
                )
                self.active_customers[tracking_id] = customer
                self.last_active_event_time[tracking_id] = current_time_sec
                newly_entered.append(customer)
            else:
                # Update existing customer
                cust = self.active_customers[tracking_id]
                cust.bbox = bbox
                cust.last_seen_time = now
                cust.zone = zone
                cust.stay_duration = (now - cust.first_seen_time).total_seconds()

        # Handle Disappearance Exit Logic (disappeared >= TRACK_DISAPPEARANCE_SECONDS)
        disappeared_ids = []
        for tracking_id, cust in list(self.active_customers.items()):
            if tracking_id not in current_tracking_ids:
                time_since_last_seen = (now - cust.last_seen_time).total_seconds()
                if time_since_last_seen >= ai_settings.TRACK_DISAPPEARANCE_SECONDS:
                    cust.status = "EXITED"
                    cust.stay_duration = max(0.0, round((cust.last_seen_time - cust.first_seen_time).total_seconds(), 1))
                    disappeared_ids.append(tracking_id)
                    newly_exited.append(cust)
                    self.exited_customers[tracking_id] = cust

        for tracking_id in disappeared_ids:
            del self.active_customers[tracking_id]
            if tracking_id in self.last_active_event_time:
                del self.last_active_event_time[tracking_id]

        active_list = list(self.active_customers.values())
        return newly_entered, active_list, newly_exited

    def should_send_active_event(self, tracking_id: str, current_time_sec: float) -> bool:
        """Throttles active customer events to prevent database event spam."""
        last_time = self.last_active_event_time.get(tracking_id, 0.0)
        if current_time_sec - last_time >= ai_settings.ACTIVE_EVENT_INTERVAL_SECONDS:
            self.last_active_event_time[tracking_id] = current_time_sec
            return True
        return False

    def update(
        self,
        tracks: List[Tuple[str, List[float], float]],
        video_id: int,
        timestamp_seconds: float,
        frame_width: int,
        frame_height: int,
        associations: Dict[str, Tuple[str, float]] = None
    ) -> List[EventPayload]:
        """Convenience update method generating EventPayloads for video processor pipeline."""
        newly_entered, active_list, newly_exited = self.update_customers(tracks, timestamp_seconds, frame_width, frame_height)
        events: List[EventPayload] = []

        from events.event_generator import EventGenerator
        gen = EventGenerator()

        for cust in newly_entered:
            evt = gen.create_customer_entered_event(video_id, cust, timestamp_seconds)
            if evt:
                events.append(evt)

        for cust in active_list:
            if self.should_send_active_event(cust.tracking_id, timestamp_seconds):
                evt = gen.create_customer_active_event(video_id, cust, timestamp_seconds)
                if evt:
                    events.append(evt)

            zone_evts = self.zone_manager.evaluate_customer_zone(cust, video_id, timestamp_seconds, associations)
            events.extend(zone_evts)

        for cust in newly_exited:
            evt = gen.create_customer_exited_event(video_id, cust, timestamp_seconds)
            if evt:
                events.append(evt)

        return events
