"""
Retail Sentinel AI - Seed Generator Script
Populates SQLite database with 8 customers, realistic event timelines, baskets,
LOW, MEDIUM, HIGH, and CRITICAL alerts, and incidents.
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add parent directory to sys.path so app module can be resolved when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.database.connection import SessionLocal, init_db, engine
from app.database.models import Base, Video, Customer, Basket, Event, Alert, Incident
from app.utils.enums import (
    VideoStatus, CustomerStatus, BasketStatus, EventType,
    RiskLevel, AlertSeverity, AlertStatus, IncidentStatus
)

def seed_database():
    print("Initializing database tables...")
    Base.metadata.drop_all(bind=engine)
    init_db()

    db = SessionLocal()
    try:
        print("Seeding sample videos...")
        v1 = Video(
            id=1,
            filename="retail_main_entrance_01.mp4",
            original_filename="Main Entrance & Aisle 3 Feed.mp4",
            file_path="uploads/retail_main_entrance_01.mp4",
            upload_time=datetime.utcnow() - timedelta(hours=3),
            processing_status=VideoStatus.COMPLETED.value,
            duration_seconds=180.0,
            total_frames=5400
        )
        v2 = Video(
            id=2,
            filename="electronics_section_cam02.mp4",
            original_filename="High Value Electronics Cam 02.mp4",
            file_path="uploads/electronics_section_cam02.mp4",
            upload_time=datetime.utcnow() - timedelta(hours=1),
            processing_status=VideoStatus.PROCESSING.value,
            duration_seconds=240.0,
            total_frames=7200
        )
        db.add_all([v1, v2])
        db.flush()

        print("Seeding sample customers...")
        now = datetime.utcnow()

        customers_data = [
            # Low Risk Customer 1
            {
                "tracking_id": "customer_001",
                "video_id": 1,
                "status": CustomerStatus.ACTIVE.value,
                "entry_time": now - timedelta(minutes=14),
                "last_seen_time": now - timedelta(minutes=1),
                "exit_time": None,
                "total_stay_seconds": 840.0,
                "current_zone": "produce_section",
                "current_risk_score": 10.0,
                "risk_level": RiskLevel.LOW.value
            },
            # Low Risk Customer 2 (Exited)
            {
                "tracking_id": "customer_002",
                "video_id": 1,
                "status": CustomerStatus.EXITED.value,
                "entry_time": now - timedelta(minutes=45),
                "last_seen_time": now - timedelta(minutes=20),
                "exit_time": now - timedelta(minutes=20),
                "total_stay_seconds": 1500.0,
                "current_zone": "checkout_lane_2",
                "current_risk_score": 0.0,
                "risk_level": RiskLevel.LOW.value
            },
            # Medium Risk Customer 3
            {
                "tracking_id": "customer_003",
                "video_id": 1,
                "status": CustomerStatus.ACTIVE.value,
                "entry_time": now - timedelta(minutes=10),
                "last_seen_time": now - timedelta(seconds=45),
                "exit_time": None,
                "total_stay_seconds": 600.0,
                "current_zone": "aisle_4_cosmetics",
                "current_risk_score": 45.0,
                "risk_level": RiskLevel.MEDIUM.value
            },
            # High Risk Customer 4
            {
                "tracking_id": "customer_004",
                "video_id": 1,
                "status": CustomerStatus.ACTIVE.value,
                "entry_time": now - timedelta(minutes=8),
                "last_seen_time": now - timedelta(seconds=12),
                "exit_time": None,
                "total_stay_seconds": 480.0,
                "current_zone": "aisle_3_electronics",
                "current_risk_score": 75.0,
                "risk_level": RiskLevel.HIGH.value
            },
            # Critical Risk Customer 5
            {
                "tracking_id": "customer_005",
                "video_id": 2,
                "status": CustomerStatus.ACTIVE.value,
                "entry_time": now - timedelta(minutes=6),
                "last_seen_time": now - timedelta(seconds=5),
                "exit_time": None,
                "total_stay_seconds": 360.0,
                "current_zone": "designer_apparel",
                "current_risk_score": 90.0,
                "risk_level": RiskLevel.CRITICAL.value
            },
            # Active Normal Customer 6
            {
                "tracking_id": "customer_006",
                "video_id": 2,
                "status": CustomerStatus.ACTIVE.value,
                "entry_time": now - timedelta(minutes=5),
                "last_seen_time": now - timedelta(minutes=2),
                "exit_time": None,
                "total_stay_seconds": 300.0,
                "current_zone": "bakery",
                "current_risk_score": 5.0,
                "risk_level": RiskLevel.LOW.value
            },
            # Exited Customer 7
            {
                "tracking_id": "customer_007",
                "video_id": 1,
                "status": CustomerStatus.EXITED.value,
                "entry_time": now - timedelta(hours=2),
                "last_seen_time": now - timedelta(hours=1, minutes=30),
                "exit_time": now - timedelta(hours=1, minutes=30),
                "total_stay_seconds": 1800.0,
                "current_zone": "exit_gate",
                "current_risk_score": 35.0,
                "risk_level": RiskLevel.MEDIUM.value
            },
            # Exited Customer 8
            {
                "tracking_id": "customer_008",
                "video_id": 1,
                "status": CustomerStatus.EXITED.value,
                "entry_time": now - timedelta(hours=3),
                "last_seen_time": now - timedelta(hours=2, minutes=20),
                "exit_time": now - timedelta(hours=2, minutes=20),
                "total_stay_seconds": 2400.0,
                "current_zone": "exit_gate",
                "current_risk_score": 80.0,
                "risk_level": RiskLevel.CRITICAL.value
            }
        ]

        db_customers = []
        for cd in customers_data:
            c = Customer(**cd)
            db.add(c)
            db_customers.append(c)
        db.flush()

        print("Seeding sample baskets...")
        b1 = Basket(
            tracking_id="basket_001",
            video_id=1,
            status=BasketStatus.ACTIVE.value,
            associated_customer_id=db_customers[0].id,
            first_seen_time=now - timedelta(minutes=13),
            last_seen_time=now - timedelta(minutes=1)
        )
        b2 = Basket(
            tracking_id="basket_004",
            video_id=1,
            status=BasketStatus.ACTIVE.value,
            associated_customer_id=db_customers[3].id,
            first_seen_time=now - timedelta(minutes=7),
            last_seen_time=now - timedelta(seconds=12)
        )
        db.add_all([b1, b2])
        db.flush()

        print("Seeding customer event timelines...")
        events_data = [
            # Customer 001 timeline
            {
                "video_id": 1,
                "customer_id": db_customers[0].id,
                "basket_id": b1.id,
                "event_type": EventType.CUSTOMER_ENTERED.value,
                "timestamp_seconds": 4.2,
                "event_time": now - timedelta(minutes=14),
                "zone": "entrance",
                "confidence": 0.98,
                "metadata_json": json.dumps({"apparel": "green sweater"})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[0].id,
                "basket_id": b1.id,
                "event_type": EventType.SHELF_INTERACTION.value,
                "timestamp_seconds": 45.0,
                "event_time": now - timedelta(minutes=12),
                "zone": "produce_section",
                "confidence": 0.94,
                "metadata_json": json.dumps({"item": "organic apples"})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[0].id,
                "basket_id": b1.id,
                "event_type": EventType.PRODUCT_IN_BASKET.value,
                "timestamp_seconds": 52.1,
                "event_time": now - timedelta(minutes=11, seconds=50),
                "zone": "produce_section",
                "confidence": 0.95,
                "metadata_json": json.dumps({"basket_slot": 1})
            },

            # Customer 004 timeline (High Risk)
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "basket_id": b2.id,
                "event_type": EventType.CUSTOMER_ENTERED.value,
                "timestamp_seconds": 12.0,
                "event_time": now - timedelta(minutes=8),
                "zone": "entrance",
                "confidence": 0.97,
                "metadata_json": json.dumps({"apparel": "dark hoodie"})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "basket_id": b2.id,
                "event_type": EventType.SHELF_INTERACTION.value,
                "timestamp_seconds": 110.5,
                "event_time": now - timedelta(minutes=6),
                "zone": "aisle_3_electronics",
                "confidence": 0.91,
                "metadata_json": json.dumps({"shelf_id": "shelf_smartphones"})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "basket_id": b2.id,
                "event_type": EventType.PRODUCT_PICKED.value,
                "timestamp_seconds": 125.4,
                "event_time": now - timedelta(minutes=5, seconds=40),
                "zone": "aisle_3_electronics",
                "confidence": 0.89,
                "metadata_json": json.dumps({"product": "wireless earbuds", "sku": "ELE-9982"})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "basket_id": b2.id,
                "event_type": EventType.PRODUCT_UNRESOLVED.value,
                "timestamp_seconds": 180.0,
                "event_time": now - timedelta(minutes=4),
                "zone": "aisle_3_electronics",
                "confidence": 0.88,
                "metadata_json": json.dumps({"duration_unplaced_sec": 45})
            },
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "basket_id": b2.id,
                "event_type": EventType.SUSPICIOUS_BEHAVIOR.value,
                "timestamp_seconds": 210.2,
                "event_time": now - timedelta(minutes=2),
                "zone": "aisle_3_electronics",
                "confidence": 0.92,
                "metadata_json": json.dumps({"gesture": "rapid concealment motion near coat"})
            },

            # Customer 005 timeline (Critical Risk)
            {
                "video_id": 2,
                "customer_id": db_customers[4].id,
                "basket_id": None,
                "event_type": EventType.CUSTOMER_ENTERED.value,
                "timestamp_seconds": 8.0,
                "event_time": now - timedelta(minutes=6),
                "zone": "entrance",
                "confidence": 0.99,
                "metadata_json": json.dumps({"apparel": "leather jacket"})
            },
            {
                "video_id": 2,
                "customer_id": db_customers[4].id,
                "basket_id": None,
                "event_type": EventType.POSSIBLE_CONCEALMENT.value,
                "timestamp_seconds": 85.6,
                "event_time": now - timedelta(minutes=3),
                "zone": "designer_apparel",
                "confidence": 0.94,
                "metadata_json": json.dumps({"anomaly": "item placed inside jacket pocket", "shelf": "luxury_handbags"})
            }
        ]

        db_events = []
        for ed in events_data:
            e = Event(**ed)
            db.add(e)
            db_events.append(e)
        db.flush()

        print("Seeding alerts...")
        alerts_data = [
            {
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "severity": AlertSeverity.HIGH.value,
                "title": "Suspicious Activity Pattern - customer_004",
                "description": "Irregular motion & product unresolved duration in aisle_3_electronics. Review recommended.",
                "risk_score": 75.0,
                "status": AlertStatus.ACTIVE.value,
                "event_id": db_events[4].id,
                "created_at": now - timedelta(minutes=2)
            },
            {
                "video_id": 2,
                "customer_id": db_customers[4].id,
                "severity": AlertSeverity.CRITICAL.value,
                "title": "High-Priority Review Required - customer_005",
                "description": "Potential product concealment indicator detected in designer_apparel section. High-priority visual verification requested.",
                "risk_score": 90.0,
                "status": AlertStatus.ACTIVE.value,
                "event_id": db_events[6].id,
                "created_at": now - timedelta(minutes=3)
            },
            {
                "video_id": 1,
                "customer_id": db_customers[2].id,
                "severity": AlertSeverity.MEDIUM.value,
                "title": "Unresolved Item Picked - customer_003",
                "description": "Item picked in aisle_4_cosmetics without basket placement. Monitoring active.",
                "risk_score": 45.0,
                "status": AlertStatus.ACKNOWLEDGED.value,
                "event_id": None,
                "created_at": now - timedelta(minutes=8)
            },
            {
                "video_id": 1,
                "customer_id": db_customers[6].id,
                "severity": AlertSeverity.LOW.value,
                "title": "Routine Shelf Interaction Notice - customer_007",
                "description": "Subject stayed near high-value shelf for extended duration before exit.",
                "risk_score": 35.0,
                "status": AlertStatus.RESOLVED.value,
                "event_id": None,
                "created_at": now - timedelta(hours=1, minutes=40)
            }
        ]

        db_alerts = []
        for ad in alerts_data:
            a = Alert(**ad)
            db.add(a)
            db_alerts.append(a)
        db.flush()

        print("Seeding incidents...")
        incidents_data = [
            {
                "alert_id": db_alerts[0].id,
                "video_id": 1,
                "customer_id": db_customers[3].id,
                "incident_type": "RETAIL_MONITORING_HIGH",
                "summary": "Automated risk threshold (HIGH) triggered for customer_004 in aisle_3_electronics. Unresolved item pick & rapid concealment movement observed.",
                "risk_score": 75.0,
                "incident_status": IncidentStatus.OPEN.value,
                "start_time": now - timedelta(minutes=4)
            },
            {
                "alert_id": db_alerts[1].id,
                "video_id": 2,
                "customer_id": db_customers[4].id,
                "incident_type": "RETAIL_MONITORING_CRITICAL",
                "summary": "Automated risk threshold (CRITICAL) triggered for customer_005 in designer_apparel. Direct concealment anomaly detected.",
                "risk_score": 90.0,
                "incident_status": IncidentStatus.UNDER_REVIEW.value,
                "start_time": now - timedelta(minutes=3)
            },
            {
                "alert_id": db_alerts[3].id,
                "video_id": 1,
                "customer_id": db_customers[7].id,
                "incident_type": "RETAIL_MONITORING_CLOSED",
                "summary": "Historical suspicious behavior verified and resolved at checkout counter by store staff.",
                "risk_score": 80.0,
                "incident_status": IncidentStatus.CLOSED.value,
                "start_time": now - timedelta(hours=2, minutes=30),
                "end_time": now - timedelta(hours=2, minutes=15)
            }
        ]

        for inc in incidents_data:
            db.add(Incident(**inc))

        db.commit()
        print("Database seed completed successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
