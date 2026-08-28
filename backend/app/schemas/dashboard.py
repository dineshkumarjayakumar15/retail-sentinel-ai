from typing import List, Optional
from pydantic import BaseModel
from app.schemas.customer import CustomerResponse
from app.schemas.alert import AlertResponse
from app.schemas.event import EventResponse

class DashboardSummaryResponse(BaseModel):
    active_customers: int
    active_baskets: int
    active_alerts: int
    high_risk_customers: int
    total_incidents: int
    recent_alerts: List[AlertResponse] = []
    recent_events: List[EventResponse] = []
    high_risk_customer_list: List[CustomerResponse] = []
