from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class Detection:
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float
    class_id: int
    class_name: str

@dataclass
class TrackedEntity:
    tracking_id: str
    bbox: List[float]
    first_seen_time: datetime
    last_seen_time: datetime
    zone: str = "entrance"
    risk_score: float = 0.0
    risk_level: str = "LOW"
    status: str = "ACTIVE"
    stay_duration: float = 0.0

@dataclass
class EventPayload:
    video_id: int
    tracking_id: str
    entity_type: str
    event_type: str
    timestamp_seconds: float
    zone: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)
