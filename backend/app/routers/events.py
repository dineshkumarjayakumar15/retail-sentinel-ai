from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.event import EventIngestRequest, EventIngestResponse, EventResponse
from app.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["Events"])

@router.post("", response_model=EventIngestResponse, status_code=status.HTTP_201_CREATED)
async def ingest_event(request: EventIngestRequest, db: Session = Depends(get_db)):
    """
    CRITICAL EVENT CONTRACT ENDPOINT.
    Ingests video intelligence events from Phase 2 YOLO+ByteTrack pipeline.
    Calculates customer state and risk engine deltas, triggers alerts/incidents if threshold crossed.
    """
    return await EventService.process_event(db, request)

@router.get("", response_model=List[EventResponse])
def get_events(limit: int = 50, db: Session = Depends(get_db)):
    """Returns recent events list."""
    return EventService.get_events(db, limit=limit)

@router.get("/video/{video_id}", response_model=List[EventResponse])
def get_events_by_video(video_id: int, limit: int = 100, db: Session = Depends(get_db)):
    """Returns events for a specific video feed."""
    return EventService.get_events(db, video_id=video_id, limit=limit)
