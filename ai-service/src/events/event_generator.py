import os
import sys
from typing import Dict, List, Optional, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.schemas import EventPayload, TrackedEntity
from config import ai_settings

class EventGenerator:
    def __init__(self):
        self.emitted_events: set = set()
        self.event_cooldowns: Dict[str, float] = {}

    def create_customer_entered_event(self, video_id: int, customer: TrackedEntity, timestamp_sec: float) -> Optional[EventPayload]:
        event_key = f"{video_id}_{customer.tracking_id}_ENTERED"
        if event_key in self.emitted_events:
            return None

        self.emitted_events.add(event_key)
        return EventPayload(
            video_id=video_id,
            tracking_id=customer.tracking_id,
            entity_type="CUSTOMER",
            event_type="CUSTOMER_ENTERED",
            timestamp_seconds=round(timestamp_sec, 1),
            zone=customer.zone,
            confidence=0.96,
            metadata={"entry_time": customer.first_seen_time.isoformat()}
        )

    def create_customer_active_event(self, video_id: int, customer: TrackedEntity, timestamp_sec: float) -> Optional[EventPayload]:
        cooldown_key = f"{video_id}_{customer.tracking_id}_ACTIVE"
        last_time = self.event_cooldowns.get(cooldown_key, 0.0)

        if timestamp_sec - last_time < ai_settings.ACTIVE_EVENT_INTERVAL_SECONDS:
            return None

        self.event_cooldowns[cooldown_key] = timestamp_sec
        return EventPayload(
            video_id=video_id,
            tracking_id=customer.tracking_id,
            entity_type="CUSTOMER",
            event_type="CUSTOMER_ACTIVE",
            timestamp_seconds=round(timestamp_sec, 1),
            zone=customer.zone,
            confidence=0.98,
            metadata={"current_zone": customer.zone}
        )

    def create_customer_exited_event(self, video_id: int, customer: TrackedEntity, timestamp_sec: float) -> Optional[EventPayload]:
        event_key = f"{video_id}_{customer.tracking_id}_EXITED"
        if event_key in self.emitted_events:
            return None

        self.emitted_events.add(event_key)
        return EventPayload(
            video_id=video_id,
            tracking_id=customer.tracking_id,
            entity_type="CUSTOMER",
            event_type="CUSTOMER_EXITED",
            timestamp_seconds=round(timestamp_sec, 1),
            zone=customer.zone,
            confidence=0.95,
            metadata={"stay_duration_sec": customer.stay_duration}
        )

    def create_basket_detected_event(self, video_id: int, basket: TrackedEntity, timestamp_sec: float) -> Optional[EventPayload]:
        event_key = f"{video_id}_{basket.tracking_id}_DETECTED"
        if event_key in self.emitted_events:
            return None

        self.emitted_events.add(event_key)
        return EventPayload(
            video_id=video_id,
            tracking_id=basket.tracking_id,
            entity_type="BASKET",
            event_type="BASKET_DETECTED",
            timestamp_seconds=round(timestamp_sec, 1),
            zone=basket.zone or "shopping_area",
            confidence=0.92,
            metadata={}
        )

    def create_basket_active_event(self, video_id: int, basket: TrackedEntity, timestamp_sec: float) -> Optional[EventPayload]:
        cooldown_key = f"{video_id}_{basket.tracking_id}_ACTIVE"
        last_time = self.event_cooldowns.get(cooldown_key, 0.0)

        if timestamp_sec - last_time < ai_settings.BASKET_ACTIVE_INTERVAL_SECONDS:
            return None

        self.event_cooldowns[cooldown_key] = timestamp_sec
        return EventPayload(
            video_id=video_id,
            tracking_id=basket.tracking_id,
            entity_type="BASKET",
            event_type="BASKET_ACTIVE",
            timestamp_seconds=round(timestamp_sec, 1),
            zone=basket.zone or "shopping_area",
            confidence=0.95,
            metadata={}
        )

    def create_zone_event(
        self,
        video_id: int,
        tracking_id: str,
        event_type: str,
        zone: str,
        timestamp_sec: float,
        confidence: float = 1.0,
        metadata: Dict[str, Any] = None
    ) -> Optional[EventPayload]:
        cooldown_key = f"{video_id}_{tracking_id}_{event_type}_{zone}"
        last_time = self.event_cooldowns.get(cooldown_key, 0.0)

        # Allow zone events once every 3 seconds per zone
        if timestamp_sec - last_time < 3.0 and event_type not in ["ZONE_ENTERED", "ZONE_EXITED"]:
            return None

        self.event_cooldowns[cooldown_key] = timestamp_sec
        return EventPayload(
            video_id=video_id,
            tracking_id=tracking_id,
            entity_type="CUSTOMER",
            event_type=event_type,
            timestamp_seconds=round(timestamp_sec, 1),
            zone=zone,
            confidence=confidence,
            metadata=metadata or {}
        )

    def create_behavior_event(self, video_id: int, tracking_id: str, behavior_info: Dict[str, Any], timestamp_sec: float, zone: str) -> Optional[EventPayload]:
        event_type = behavior_info.get("event_type", "SUSPICIOUS_BEHAVIOR")
        cooldown_key = f"{video_id}_{tracking_id}_{event_type}"
        last_time = self.event_cooldowns.get(cooldown_key, 0.0)

        if timestamp_sec - last_time < ai_settings.SUSPICIOUS_EVENT_COOLDOWN_SECONDS:
            return None

        self.event_cooldowns[cooldown_key] = timestamp_sec
        return EventPayload(
            video_id=video_id,
            tracking_id=tracking_id,
            entity_type="CUSTOMER",
            event_type=event_type,
            timestamp_seconds=round(timestamp_sec, 1),
            zone=zone,
            confidence=behavior_info.get("confidence", 0.90),
            metadata=behavior_info.get("metadata", {})
        )
