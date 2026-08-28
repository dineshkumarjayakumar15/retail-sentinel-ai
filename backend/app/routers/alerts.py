from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.alert import AlertResponse, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])

@router.get("", response_model=List[AlertResponse])
def get_alerts(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Returns list of security alerts."""
    return AlertService.get_alerts(db, status=status, severity=severity, limit=limit)

@router.get("/{id}", response_model=AlertResponse)
def get_alert_by_id(id: int, db: Session = Depends(get_db)):
    """Returns detailed alert information by ID."""
    alert = AlertService.get_alert_by_id(db, id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.patch("/{id}", response_model=AlertResponse)
def update_alert(id: int, payload: AlertUpdate, db: Session = Depends(get_db)):
    """Updates alert status (ACTIVE, ACKNOWLEDGED, RESOLVED)."""
    if not payload.status:
        raise HTTPException(status_code=400, detail="Status must be provided")
    updated = AlertService.update_alert_status(db, id, payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Alert not found")
    return updated
