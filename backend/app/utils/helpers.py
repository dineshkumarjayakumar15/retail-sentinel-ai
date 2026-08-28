from datetime import datetime
from typing import Optional
from app.utils.enums import RiskLevel

def clamp_risk_score(score: float) -> float:
    """Clamps risk score between 0.0 and 100.0."""
    return max(0.0, min(100.0, round(score, 1)))

def compute_risk_level(score: float) -> RiskLevel:
    """Computes risk level category based on numerical risk score."""
    score = clamp_risk_score(score)
    if score >= 80.0:
        return RiskLevel.CRITICAL
    elif score >= 60.0:
        return RiskLevel.HIGH
    elif score >= 30.0:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW

def calculate_stay_duration(entry_time: datetime, exit_time: Optional[datetime] = None) -> float:
    """Calculates total stay duration in seconds."""
    end = exit_time or datetime.utcnow()
    if not entry_time:
        return 0.0
    delta = (end - entry_time).total_seconds()
    return max(0.0, round(delta, 1))
