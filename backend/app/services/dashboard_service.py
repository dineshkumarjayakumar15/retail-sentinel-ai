from sqlalchemy.orm import Session
from app.database.models import Customer, Basket, Alert, Incident, Event, Video
from app.utils.enums import CustomerStatus, BasketStatus, AlertStatus
from app.services.alert_service import AlertService
from app.services.customer_service import CustomerService
from app.services.event_service import EventService

class DashboardService:

    @staticmethod
    def get_summary(db: Session) -> dict:
        active_customers = db.query(Customer).filter(Customer.status == CustomerStatus.ACTIVE.value).count()
        active_baskets = db.query(Basket).filter(Basket.status == BasketStatus.ACTIVE.value).count()
        active_alerts = db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE.value).count()
        high_risk_customers = db.query(Customer).filter(
            Customer.status == CustomerStatus.ACTIVE.value,
            Customer.current_risk_score >= 60.0
        ).count()
        total_incidents = db.query(Incident).count()

        recent_alerts = AlertService.get_alerts(db, limit=10)
        recent_events_db = EventService.get_events(db, limit=15)
        high_risk_customer_list = CustomerService.get_customers(db, high_risk_only=True, limit=10)

        formatted_events = []
        for e in recent_events_db:
            formatted_events.append({
                "id": e.id,
                "video_id": e.video_id,
                "customer_id": e.customer_id,
                "basket_id": e.basket_id,
                "event_type": e.event_type,
                "timestamp_seconds": e.timestamp_seconds,
                "event_time": e.event_time,
                "zone": e.zone,
                "confidence": e.confidence,
                "created_at": e.created_at,
                "metadata": {}
            })

        return {
            "active_customers": active_customers,
            "active_baskets": active_baskets,
            "active_alerts": active_alerts,
            "high_risk_customers": high_risk_customers,
            "total_incidents": total_incidents,
            "recent_alerts": recent_alerts,
            "recent_events": formatted_events,
            "high_risk_customer_list": high_risk_customer_list
        }
