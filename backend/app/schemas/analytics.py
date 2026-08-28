from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class DailyIncidentStat(BaseModel):
    date: str
    suspicious_incidents: int
    high_risk_incidents: int

class RiskDistributionStat(BaseModel):
    name: str
    value: int
    color: str

class AnalyticsOverviewResponse(BaseModel):
    total_incidents_30d: int
    high_risk_incidents_30d: int
    active_customers: int
    daily_stats: List[DailyIncidentStat]
    risk_distribution: List[RiskDistributionStat]
    customer_risk_distribution: List[RiskDistributionStat]
