from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator
from app.utils.enums import AlertSeverity, AlertStatus

class AlertBase(BaseModel):
    video_id: int
    customer_id: Optional[int] = None
    severity: AlertSeverity
    title: str
    description: str
    risk_score: float
    status: AlertStatus = AlertStatus.ACTIVE

class AlertCreate(AlertBase):
    event_id: Optional[int] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None

class AlertResponse(AlertBase):
    id: int
    event_id: Optional[int] = None
    customer_tracking_id: Optional[str] = None
    video_filename: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode='before')
    @classmethod
    def populate_computed_fields(cls, data: Any) -> Any:
        if hasattr(data, 'created_at'):
            created = getattr(data, 'created_at', datetime.utcnow())
            cust = getattr(data, 'customer', None)
            vid = getattr(data, 'video', None)
            return {
                "id": getattr(data, 'id', 0),
                "video_id": getattr(data, 'video_id', 0),
                "customer_id": getattr(data, 'customer_id', None),
                "severity": getattr(data, 'severity', AlertSeverity.LOW.value),
                "title": str(getattr(data, 'title', '')),
                "description": str(getattr(data, 'description', '')),
                "risk_score": float(getattr(data, 'risk_score', 0.0)),
                "status": getattr(data, 'status', AlertStatus.ACTIVE.value),
                "event_id": getattr(data, 'event_id', None),
                "customer_tracking_id": cust.tracking_id if cust else None,
                "video_filename": vid.original_filename if vid else "Surveillance Feed",
                "created_at": created,
                "updated_at": created,
            }
        return data
