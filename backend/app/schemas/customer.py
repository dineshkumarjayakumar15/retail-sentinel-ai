from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict, model_validator
from app.utils.enums import CustomerStatus, RiskLevel

class CustomerBase(BaseModel):
    tracking_id: str
    video_id: int
    status: CustomerStatus = CustomerStatus.ACTIVE
    current_zone: Optional[str] = None
    current_risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW

class CustomerCreate(CustomerBase):
    entry_time: Optional[datetime] = None

class CustomerResponse(CustomerBase):
    id: int
    entry_time: datetime
    last_seen_time: datetime
    exit_time: Optional[datetime] = None
    total_stay_seconds: Optional[float] = 0.0
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def populate_computed_fields(cls, data: Any) -> Any:
        if hasattr(data, 'created_at'):
            created = getattr(data, 'created_at', datetime.utcnow())
            entry = getattr(data, 'entry_time', created)
            last = getattr(data, 'last_seen_time', created)
            exit_t = getattr(data, 'exit_time', None)
            return {
                "id": getattr(data, 'id', 0),
                "tracking_id": str(getattr(data, 'tracking_id', '')),
                "video_id": getattr(data, 'video_id', 0),
                "status": getattr(data, 'status', CustomerStatus.ACTIVE.value),
                "current_zone": getattr(data, 'current_zone', 'entrance'),
                "current_risk_score": float(getattr(data, 'current_risk_score', 0.0)),
                "risk_level": getattr(data, 'risk_level', RiskLevel.LOW.value),
                "entry_time": entry,
                "last_seen_time": last,
                "exit_time": exit_t,
                "total_stay_seconds": getattr(data, 'total_stay_seconds', 0.0),
                "created_at": created,
                "updated_at": created,
            }
        return data

class CustomerTimelineEvent(BaseModel):
    id: int
    event_type: str
    timestamp_seconds: float
    event_time: datetime
    zone: Optional[str] = None
    confidence: float
    metadata: Optional[dict] = {}

    model_config = ConfigDict(from_attributes=True)

class CustomerTimelineResponse(BaseModel):
    customer: CustomerResponse
    events: List[CustomerTimelineEvent]
