from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Incident, Customer, Video

class IncidentService:

    @staticmethod
    def get_incidents(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        results = db.query(Incident, Customer.tracking_id, Video.original_filename).outerjoin(
            Customer, Incident.customer_id == Customer.id
        ).outerjoin(
            Video, Incident.video_id == Video.id
        ).order_by(Incident.created_at.desc()).limit(limit).all()

        formatted = []
        for inc, tracking_id, filename in results:
            formatted.append({
                "id": inc.id,
                "alert_id": inc.alert_id,
                "video_id": inc.video_id,
                "customer_id": inc.customer_id,
                "incident_type": inc.incident_type,
                "summary": inc.summary,
                "risk_score": inc.risk_score,
                "incident_status": inc.incident_status,
                "customer_tracking_id": tracking_id or "System",
                "video_filename": filename or "feed.mp4",
                "start_time": inc.start_time,
                "end_time": inc.end_time,
                "created_at": inc.created_at
            })
        return formatted

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: int) -> Optional[Dict[str, Any]]:
        result = db.query(Incident, Customer.tracking_id, Video.original_filename).outerjoin(
            Customer, Incident.customer_id == Customer.id
        ).outerjoin(
            Video, Incident.video_id == Video.id
        ).filter(Incident.id == incident_id).first()

        if not result:
            return None

        inc, tracking_id, filename = result
        return {
            "id": inc.id,
            "alert_id": inc.alert_id,
            "video_id": inc.video_id,
            "customer_id": inc.customer_id,
            "incident_type": inc.incident_type,
            "summary": inc.summary,
            "risk_score": inc.risk_score,
            "incident_status": inc.incident_status,
            "customer_tracking_id": tracking_id or "System",
            "video_filename": filename or "feed.mp4",
            "start_time": inc.start_time,
            "end_time": inc.end_time,
            "created_at": inc.created_at
        }
