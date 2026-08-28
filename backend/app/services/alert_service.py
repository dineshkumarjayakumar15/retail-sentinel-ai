from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Alert, Customer, Video
from app.utils.enums import AlertStatus, AlertSeverity

class AlertService:

    @staticmethod
    def get_alerts(db: Session, status: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        query = db.query(Alert, Customer.tracking_id, Video.original_filename).outerjoin(
            Customer, Alert.customer_id == Customer.id
        ).outerjoin(
            Video, Alert.video_id == Video.id
        )

        if status:
            query = query.filter(Alert.status == status)
        if severity:
            query = query.filter(Alert.severity == severity)

        results = query.order_by(Alert.created_at.desc()).limit(limit).all()
        formatted_alerts = []
        for alert, tracking_id, filename in results:
            alert_dict = {
                "id": alert.id,
                "video_id": alert.video_id,
                "customer_id": alert.customer_id,
                "severity": alert.severity,
                "title": alert.title,
                "description": alert.description,
                "risk_score": alert.risk_score,
                "status": alert.status,
                "event_id": alert.event_id,
                "customer_tracking_id": tracking_id or "System",
                "video_filename": filename or "feed.mp4",
                "created_at": alert.created_at,
                "updated_at": getattr(alert, "updated_at", alert.created_at)
            }
            formatted_alerts.append(alert_dict)
        return formatted_alerts

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[Dict[str, Any]]:
        result = db.query(Alert, Customer.tracking_id, Video.original_filename).outerjoin(
            Customer, Alert.customer_id == Customer.id
        ).outerjoin(
            Video, Alert.video_id == Video.id
        ).filter(Alert.id == alert_id).first()

        if not result:
            return None

        alert, tracking_id, filename = result
        return {
            "id": alert.id,
            "video_id": alert.video_id,
            "customer_id": alert.customer_id,
            "severity": alert.severity,
            "title": alert.title,
            "description": alert.description,
            "risk_score": alert.risk_score,
            "status": alert.status,
            "event_id": alert.event_id,
            "customer_tracking_id": tracking_id or "System",
            "video_filename": filename or "feed.mp4",
            "created_at": alert.created_at,
            "updated_at": getattr(alert, "updated_at", alert.created_at)
        }

    @staticmethod
    def update_alert_status(db: Session, alert_id: int, status: AlertStatus) -> Optional[Dict[str, Any]]:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if not alert:
            return None
        alert.status = status.value
        db.commit()
        db.refresh(alert)
        return AlertService.get_alert_by_id(db, alert_id)
