from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.analytics import AnalyticsOverviewResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/overview", response_model=AnalyticsOverviewResponse)
def get_analytics_overview(days: int = Query(30, ge=1, le=365), db: Session = Depends(get_db)):
    """Returns overview statistics and daily trends computed from real SQLite data."""
    return AnalyticsService.get_overview_analytics(db, days=days)
