import json
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, model_validator
from app.utils.enums import EventType, EntityType

class EventIngestRequest(BaseModel):
    video_id: int
    tracking_id: str
    entity_type: EntityType = EntityType.CUSTOMER
    event_type: EventType
    timestamp_seconds: float = 0.0
    zone: Optional[str] = "entrance"
    confidence: float = 1.0
    metadata: Optional[Dict[str, Any]] = {}

class EventResponse(BaseModel):
    id: int
    video_id: int
    customer_id: Optional[int] = None
    basket_id: Optional[int] = None
    event_type: str
    timestamp_seconds: float
    event_time: datetime
    zone: Optional[str] = None
    confidence: float
    metadata: Optional[Dict[str, Any]] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def parse_metadata_json(cls, data: Any) -> Any:
        # Dynamically convert metadata_json to metadata dict
        if hasattr(data, 'metadata_json'):
            raw = getattr(data, 'metadata_json', None)
            parsed = {}
            if raw:
                try:
                    parsed = json.loads(raw)
                except Exception:
                    parsed = {}
            # Return dict structure for Pydantic from_attributes
            return {
                "id": getattr(data, 'id', 0),
                "video_id": getattr(data, 'video_id', 0),
                "customer_id": getattr(data, 'customer_id', None),
                "basket_id": getattr(data, 'basket_id', None),
                "event_type": str(getattr(data, 'event_type', '')),
                "timestamp_seconds": float(getattr(data, 'timestamp_seconds', 0.0)),
                "event_time": getattr(data, 'event_time', datetime.utcnow()),
                "zone": getattr(data, 'zone', None),
                "confidence": float(getattr(data, 'confidence', 1.0)),
                "metadata": parsed,
                "created_at": getattr(data, 'created_at', datetime.utcnow()),
            }
        return data

class EventIngestResponse(BaseModel):
    status: str = "success"
    event_id: int
    tracking_id: str
    event_type: str
    current_risk_score: float
    risk_level: str
    alert_created: bool = False
    alert_id: Optional[int] = None
