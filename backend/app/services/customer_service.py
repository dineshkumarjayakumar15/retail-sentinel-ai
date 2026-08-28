import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.database.models import Customer, Event
from app.utils.helpers import calculate_stay_duration

class CustomerService:

    @staticmethod
    def get_customers(db: Session, status: Optional[str] = None, high_risk_only: bool = False, limit: int = 100) -> List[Customer]:
        query = db.query(Customer)
        if status:
            query = query.filter(Customer.status == status)
        if high_risk_only:
            query = query.filter(Customer.current_risk_score >= 60.0)
        
        customers = query.order_by(Customer.created_at.desc()).limit(limit).all()
        for c in customers:
            c.total_stay_seconds = calculate_stay_duration(c.entry_time, c.exit_time)
        return customers

    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int) -> Optional[Customer]:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if customer:
            customer.total_stay_seconds = calculate_stay_duration(customer.entry_time, customer.exit_time)
        return customer

    @staticmethod
    def get_customer_timeline(db: Session, customer_id: int) -> Dict[str, Any]:
        customer = CustomerService.get_customer_by_id(db, customer_id)
        if not customer:
            return None
        
        events = db.query(Event).filter(Event.customer_id == customer_id).order_by(Event.timestamp_seconds.asc()).all()
        formatted_events = []
        for e in events:
            meta = {}
            if e.metadata_json:
                try:
                    meta = json.loads(e.metadata_json)
                except Exception:
                    meta = {}
            formatted_events.append({
                "id": e.id,
                "event_type": e.event_type,
                "timestamp_seconds": e.timestamp_seconds,
                "event_time": e.event_time,
                "zone": e.zone,
                "confidence": e.confidence,
                "metadata": meta
            })

        return {
            "customer": customer,
            "events": formatted_events
        }
