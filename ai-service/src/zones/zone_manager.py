import json
import os
import sys
from typing import List, Dict, Any, Tuple, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import EventPayload

class ZoneManager:
    def __init__(self, zones_file: str = None):
        if not zones_file:
            zones_file = os.path.join(os.path.dirname(__file__), "zones.json")
        
        self.zones: Dict[str, Dict[str, Any]] = {}
        if os.path.exists(zones_file):
            try:
                with open(zones_file, 'r') as f:
                    self.zones = json.load(f)
            except Exception:
                self.zones = self.default_zones()
        else:
            self.zones = self.default_zones()

        # Customer tracking states: tracking_id -> current_zone
        self.customer_zones: Dict[str, str] = {}
        # Customer zone entry time: tracking_id -> timestamp_sec
        self.zone_entry_times: Dict[str, float] = {}
        # Customer zone history: tracking_id -> List[zone_name]
        self.customer_zone_history: Dict[str, List[str]] = {}
        
        # Flags to prevent event duplicate spam per visit: (tracking_id, zone_name, event_type) -> bool
        self.emitted_visit_events: set = set()

    @staticmethod
    def default_zones() -> Dict[str, Dict[str, Any]]:
        return {
            "entrance": {
                "id": "entrance_zone", "name": "Main Entrance", "type": "ENTRANCE",
                "bounds": { "x1": 0.0, "y1": 0.0, "x2": 0.25, "y2": 1.0 }
            },
            "shopping_area": {
                "id": "shopping_area_zone", "name": "General Shopping Area", "type": "SHELF",
                "bounds": { "x1": 0.25, "y1": 0.0, "x2": 0.65, "y2": 1.0 }
            },
            "shelf_zone": {
                "id": "electronics_shelf_zone", "name": "High Value Shelf", "type": "SHELF",
                "bounds": { "x1": 0.65, "y1": 0.0, "x2": 0.85, "y2": 1.0 }
            },
            "exit": {
                "id": "exit_gate_zone", "name": "Store Exit", "type": "EXIT",
                "bounds": { "x1": 0.85, "y1": 0.0, "x2": 1.0, "y2": 1.0 }
            }
        }

    def get_zone_for_bbox(self, bbox: List[float], frame_width: int, frame_height: int) -> str:
        """Returns zone_name for a given bounding box."""
        zone_name, _ = self.get_zone_info_for_bbox(bbox, frame_width, frame_height)
        return zone_name

    def get_zone_info_for_bbox(self, bbox: List[float], frame_width: int, frame_height: int) -> Tuple[str, str]:
        """
        Returns (zone_name, zone_type) based on bottom-center point of bounding box.
        """
        if not bbox or len(bbox) < 4 or frame_width <= 0 or frame_height <= 0:
            return "shopping_area", "SHELF"

        # Bottom-center location
        bc_x = (bbox[0] + bbox[2]) / 2.0
        bc_y = bbox[3]

        rel_x = bc_x / frame_width
        rel_y = bc_y / frame_height

        for zone_name, info in self.zones.items():
            b = info.get("bounds", {})
            if b and (b.get("x1", 0) <= rel_x <= b.get("x2", 1)) and (b.get("y1", 0) <= rel_y <= b.get("y2", 1)):
                return zone_name, info.get("type", "SHELF")

        return "shopping_area", "SHELF"

    def process_customer_position(
        self,
        tracking_id: str,
        bbox: List[float],
        timestamp_sec: float,
        frame_width: int,
        frame_height: int
    ) -> List[Dict[str, Any]]:
        """
        Evaluates customer position, zone transitions, dwell time, shelf interactions,
        long dwell thresholds, and unusual zone transitions.
        Returns list of generated event payloads.
        """
        events_to_emit = []
        new_zone, zone_type = self.get_zone_info_for_bbox(bbox, frame_width, frame_height)
        prev_zone = self.customer_zones.get(tracking_id)

        if prev_zone is None:
            # First appearance in a zone -> ZONE_ENTERED
            self.customer_zones[tracking_id] = new_zone
            self.zone_entry_times[tracking_id] = timestamp_sec
            self.customer_zone_history[tracking_id] = [new_zone]

            events_to_emit.append({
                "event_type": "ZONE_ENTERED",
                "zone": new_zone,
                "confidence": 1.0,
                "metadata": {"zone_type": zone_type, "entry_time_sec": timestamp_sec}
            })
        elif prev_zone != new_zone:
            # Zone Transition occurred!
            entry_t = self.zone_entry_times.get(tracking_id, timestamp_sec)
            stay_duration = max(0.0, round(timestamp_sec - entry_t, 1))

            # 1. ZONE_EXITED for previous zone
            events_to_emit.append({
                "event_type": "ZONE_EXITED",
                "zone": prev_zone,
                "confidence": 1.0,
                "metadata": {"previous_zone": prev_zone, "zone_stay_duration": stay_duration}
            })

            # Check Unusual Transition (e.g. RESTRICTED -> EXIT)
            if self._is_unusual_transition(prev_zone, new_zone):
                events_to_emit.append({
                    "event_type": "UNUSUAL_ZONE_TRANSITION",
                    "zone": new_zone,
                    "confidence": 0.90,
                    "metadata": {
                        "from_zone": prev_zone,
                        "to_zone": new_zone,
                        "transition_rule": "Direct transition from RESTRICTED area to EXIT"
                    }
                })

            # Reset state for new zone
            self.customer_zones[tracking_id] = new_zone
            self.zone_entry_times[tracking_id] = timestamp_sec
            if tracking_id in self.customer_zone_history:
                self.customer_zone_history[tracking_id].append(new_zone)

            # 2. ZONE_ENTERED for new zone
            events_to_emit.append({
                "event_type": "ZONE_ENTERED",
                "zone": new_zone,
                "confidence": 1.0,
                "metadata": {"zone_type": zone_type, "entry_time_sec": timestamp_sec}
            })
        else:
            # Customer remains inside same zone -> check dwell time triggers
            entry_t = self.zone_entry_times.get(tracking_id, timestamp_sec)
            dwell_time = timestamp_sec - entry_t

            # Check SHELF_INTERACTION (dwell_time >= 3s)
            if zone_type == "SHELF" and dwell_time >= ai_settings.SHELF_INTERACTION_MIN_SECONDS:
                event_key = (tracking_id, new_zone, "SHELF_INTERACTION")
                if event_key not in self.emitted_visit_events:
                    self.emitted_visit_events.add(event_key)
                    events_to_emit.append({
                        "event_type": "SHELF_INTERACTION",
                        "zone": new_zone,
                        "confidence": 0.92,
                        "metadata": {
                            "dwell_time": round(dwell_time, 1),
                            "zone_type": "SHELF"
                        }
                    })

            # Check LONG_DWELL_TIME (dwell_time >= 60s)
            if dwell_time >= ai_settings.LONG_DWELL_THRESHOLD_SECONDS:
                event_key = (tracking_id, new_zone, "LONG_DWELL_TIME")
                if event_key not in self.emitted_visit_events:
                    self.emitted_visit_events.add(event_key)
                    events_to_emit.append({
                        "event_type": "LONG_DWELL_TIME",
                        "zone": new_zone,
                        "confidence": 0.95,
                        "metadata": {
                            "dwell_time": round(dwell_time, 1),
                            "threshold": ai_settings.LONG_DWELL_THRESHOLD_SECONDS
                        }
                    })

        return events_to_emit

    def evaluate_customer_zone(
        self,
        customer: Any,
        video_id: int,
        timestamp_seconds: float,
        associations: Dict[str, Tuple[str, float]] = None
    ) -> List[EventPayload]:
        """Convenience method evaluating customer zone transitions and returning EventPayload list."""
        events: List[EventPayload] = []
        from events.event_generator import EventGenerator
        gen = EventGenerator()

        bbox = getattr(customer, 'bbox', [0, 0, 100, 100])
        tracking_id = getattr(customer, 'tracking_id', 'customer_001')

        fw, fh = 1280, 720
        raw_evts = self.process_customer_position(tracking_id, bbox, timestamp_seconds, fw, fh)

        for item in raw_evts:
            evt_type = item.get("event_type", "ZONE_ENTERED")
            zone = item.get("zone", "shopping_area")
            conf = item.get("confidence", 1.0)
            meta = item.get("metadata", {})

            if associations and tracking_id in associations.values():
                for b_id, (c_id, b_conf) in associations.items():
                    if c_id == tracking_id:
                        meta["associated_basket_id"] = b_id

            evt = gen.create_zone_event(video_id, tracking_id, evt_type, zone, timestamp_seconds, conf, meta)
            if evt:
                events.append(evt)

        return events

    def _is_unusual_transition(self, from_zone: str, to_zone: str) -> bool:
        from_type = self.zones.get(from_zone, {}).get("type", "")
        to_type = self.zones.get(to_zone, {}).get("type", "")

        if from_type == "RESTRICTED" and to_type == "EXIT":
            return True
        if from_type == "ENTRANCE" and to_type == "EXIT":
            return True
        return False
