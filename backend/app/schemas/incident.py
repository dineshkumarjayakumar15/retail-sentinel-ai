from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.utils.enums import IncidentStatus

class IncidentBase(BaseModel):
    alert_id: Optional[int] = None
    video_id: int
    customer_id: Optional[int] = None
    incident_type: str
    summary: str
    risk_score: float
    incident_status: IncidentStatus = IncidentStatus.OPEN

class IncidentCreate(IncidentBase):
    start_time: Optional[datetime] = None

class IncidentResponse(IncidentBase):
    id: int
    customer_tracking_id: Optional[str] = None
    video_filename: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
