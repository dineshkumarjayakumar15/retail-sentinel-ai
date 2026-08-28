import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.schemas.event import EventIngestRequest, EventIngestResponse
from app.database.models import Video, Customer, Basket, Event, Alert, Incident
from app.utils.enums import EventType, CustomerStatus, BasketStatus, EntityType
from app.utils.helpers import calculate_stay_duration, compute_risk_level
from app.services.risk_engine import RiskEngine
from app.websocket.manager import manager

class EventService:

    @staticmethod
    async def process_event(db: Session, request: EventIngestRequest) -> EventIngestResponse:
        """
        Validates event, updates customer/basket state, evaluates risk score using RiskEngine,
        and broadcasts updates over WebSockets.
        """
        video = db.query(Video).filter(Video.id == request.video_id).first()
        if not video:
            video = Video(
                id=request.video_id,
                filename="feed_camera_01.mp4",
                original_filename="feed_camera_01.mp4",
                file_path="uploads/feed_camera_01.mp4",
                processing_status="PROCESSING",
                duration_seconds=120.0,
                total_frames=3600
            )
            db.add(video)
            db.flush()

        customer: Optional[Customer] = None
        basket: Optional[Basket] = None

        # Customer State Logic
        if request.entity_type == EntityType.CUSTOMER or request.tracking_id.startswith("customer"):
            customer = db.query(Customer).filter(
                Customer.video_id == request.video_id,
                Customer.tracking_id == request.tracking_id
            ).first()

            if not customer:
                customer = Customer(
                    tracking_id=request.tracking_id,
                    video_id=request.video_id,
                    status=CustomerStatus.ACTIVE.value,
                    entry_time=datetime.utcnow(),
                    last_seen_time=datetime.utcnow(),
                    current_zone=request.zone or "entrance",
                    current_risk_score=0.0,
                    risk_level="LOW"
                )
                db.add(customer)
                db.flush()
            else:
                customer.last_seen_time = datetime.utcnow()
                if request.zone:
                    customer.current_zone = request.zone
                
                if request.event_type == EventType.CUSTOMER_ENTERED.value:
                    customer.status = CustomerStatus.ACTIVE.value
                    customer.entry_time = datetime.utcnow()
                elif request.event_type == EventType.CUSTOMER_EXITED.value:
                    customer.status = CustomerStatus.EXITED.value
                    customer.exit_time = datetime.utcnow()
                    customer.total_stay_seconds = calculate_stay_duration(customer.entry_time, customer.exit_time)

        # Basket State Logic
        if request.entity_type == EntityType.BASKET or request.event_type in [EventType.BASKET_DETECTED.value, EventType.BASKET_ACTIVE.value]:
            basket_tracking_id = request.tracking_id if request.tracking_id.startswith("basket") else request.metadata.get("basket_tracking_id", f"basket_{request.tracking_id}")
            basket = db.query(Basket).filter(
                Basket.video_id == request.video_id,
                Basket.tracking_id == basket_tracking_id
            ).first()
            if not basket:
                basket = Basket(
                    tracking_id=basket_tracking_id,
                    video_id=request.video_id,
                    status=BasketStatus.ACTIVE.value,
                    associated_customer_id=customer.id if customer else None,
                    first_seen_time=datetime.utcnow(),
                    last_seen_time=datetime.utcnow()
                )
                db.add(basket)
                db.flush()
            else:
                basket.last_seen_time = datetime.utcnow()
                if customer and not basket.associated_customer_id:
                    basket.associated_customer_id = customer.id

            # Handle explicit customer-basket association from metadata
            assoc_cust_tracking_id = request.metadata.get("associated_customer_tracking_id")
            if assoc_cust_tracking_id:
                assoc_cust = db.query(Customer).filter(
                    Customer.video_id == request.video_id,
                    Customer.tracking_id == assoc_cust_tracking_id
                ).first()
                if assoc_cust:
                    basket.associated_customer_id = assoc_cust.id

        # Save Event Record
        db_event = Event(
            video_id=request.video_id,
            customer_id=customer.id if customer else None,
            basket_id=basket.id if basket else None,
            event_type=request.event_type.value,
            timestamp_seconds=request.timestamp_seconds,
            event_time=datetime.utcnow(),
            zone=request.zone,
            confidence=request.confidence,
            metadata_json=json.dumps(request.metadata or {})
        )
        db.add(db_event)
        db.flush()

        # Risk Engine Evaluation
        alert_created: Optional[Alert] = None
        incident_created: Optional[Incident] = None

        if customer:
            score, level, alert_created, incident_created = RiskEngine.process_event_risk(
                db=db,
                customer=customer,
                event=db_event
            )
        else:
            db.commit()

        # Real-time WebSocket Broadcast
        broadcast_payload = {
            "type": "NEW_EVENT",
            "event": {
                "id": db_event.id,
                "video_id": db_event.video_id,
                "customer_id": db_event.customer_id,
                "tracking_id": request.tracking_id,
                "event_type": db_event.event_type,
                "timestamp_seconds": db_event.timestamp_seconds,
                "zone": db_event.zone,
                "confidence": db_event.confidence,
                "event_time": db_event.event_time.isoformat()
            },
            "customer": {
                "id": customer.id if customer else None,
                "tracking_id": customer.tracking_id if customer else None,
                "current_risk_score": customer.current_risk_score if customer else 0.0,
                "risk_level": customer.risk_level if customer else "LOW",
                "status": customer.status if customer else "ACTIVE",
                "zone": customer.current_zone if customer else None
            } if customer else None,
            "basket": {
                "id": basket.id if basket else None,
                "tracking_id": basket.tracking_id if basket else None,
                "status": basket.status if basket else "ACTIVE",
                "associated_customer_id": basket.associated_customer_id if basket else None
            } if basket else None,
            "alert": {
                "id": alert_created.id,
                "severity": alert_created.severity,
                "title": alert_created.title,
                "description": alert_created.description,
                "risk_score": alert_created.risk_score,
                "status": alert_created.status,
                "created_at": alert_created.created_at.isoformat()
            } if alert_created else None
        }

        await manager.broadcast(broadcast_payload)

        return EventIngestResponse(
            status="success",
            event_id=db_event.id,
            tracking_id=request.tracking_id,
            event_type=request.event_type.value,
            current_risk_score=customer.current_risk_score if customer else 0.0,
            risk_level=customer.risk_level if customer else "LOW",
            alert_created=alert_created is not None,
            alert_id=alert_created.id if alert_created else None
        )

    @staticmethod
    def get_events(db: Session, video_id: Optional[int] = None, limit: int = 50) -> List[Event]:
        query = db.query(Event)
        if video_id:
            query = query.filter(Event.video_id == video_id)
        return query.order_by(Event.id.desc()).limit(limit).all()
