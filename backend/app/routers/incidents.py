from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.incident import IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.get("", response_model=List[IncidentResponse])
def get_incidents(limit: int = 50, db: Session = Depends(get_db)):
    """Returns list of recorded high-risk retail incidents."""
    return IncidentService.get_incidents(db, limit=limit)

@router.get("/{id}", response_model=IncidentResponse)
def get_incident_by_id(id: int, db: Session = Depends(get_db)):
    """Returns details for a specific incident."""
    incident = IncidentService.get_incident_by_id(db, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident
