from typing import Tuple, Dict, Any, Optional, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.config import settings
from app.utils.enums import EventType, RiskLevel, AlertSeverity, AlertStatus, IncidentStatus
from app.utils.helpers import clamp_risk_score, compute_risk_level
from app.database.models import Customer, Event, Alert, Incident

class RiskEngine:
    """
    Explainable, multi-signal rule-based decision-support risk calculation engine for Retail Sentinel AI.
    Calculates customer risk score deltas, tracks contributing signals, clamps values between 0.0 and 100.0,
    and automatically triggers explainable Alerts & Incidents upon crossing HIGH or CRITICAL thresholds.
    """

    @staticmethod
    def get_event_weight(event_type: str) -> float:
        """Returns the configurable score delta for a given event type."""
        weights: Dict[str, float] = {
            EventType.CUSTOMER_ENTERED.value: settings.SCORE_CUSTOMER_ENTERED,
            EventType.CUSTOMER_ACTIVE.value: 0.0,
            EventType.CUSTOMER_EXITED.value: 0.0,
            EventType.ZONE_ENTERED.value: 0.0,
            EventType.ZONE_EXITED.value: 0.0,
            EventType.BASKET_DETECTED.value: 0.0,
            EventType.BASKET_ACTIVE.value: 0.0,
            EventType.SHELF_INTERACTION.value: settings.SCORE_SHELF_INTERACTION,
            EventType.LONG_DWELL_TIME.value: settings.SCORE_LONG_DWELL_TIME,
            EventType.UNUSUAL_ZONE_TRANSITION.value: settings.SCORE_UNUSUAL_ZONE_TRANSITION,
            EventType.PRODUCT_PICKED.value: settings.SCORE_PRODUCT_PICKED,
            EventType.PRODUCT_IN_BASKET.value: settings.SCORE_PRODUCT_IN_BASKET,
            EventType.PRODUCT_RETURNED.value: settings.SCORE_PRODUCT_RETURNED,
            EventType.PRODUCT_UNRESOLVED.value: settings.SCORE_PRODUCT_UNRESOLVED,
            EventType.SUSPICIOUS_BEHAVIOR.value: settings.SCORE_SUSPICIOUS_BEHAVIOR,
            EventType.POSSIBLE_CONCEALMENT.value: settings.SCORE_POSSIBLE_CONCEALMENT,
            EventType.HIGH_RISK_DETECTED.value: settings.SCORE_HIGH_RISK_DETECTED,
        }
        return weights.get(event_type, 0.0)

    @classmethod
    def process_event_risk(
        cls,
        db: Session,
        customer: Customer,
        event: Event
    ) -> Tuple[float, RiskLevel, Optional[Alert], Optional[Incident]]:
        """
        Evaluates an event for a customer, updates risk score, and generates alerts/incidents if threshold crossed.
        """
        delta = cls.get_event_weight(event.event_type)
        new_score = clamp_risk_score(customer.current_risk_score + delta)
        old_level = compute_risk_level(customer.current_risk_score)
        new_level = compute_risk_level(new_score)

        # Update customer state
        customer.current_risk_score = new_score
        customer.risk_level = new_level.value
        customer.updated_at = datetime.utcnow()

        alert_created: Optional[Alert] = None
        incident_created: Optional[Incident] = None

        # Check if HIGH or CRITICAL threshold reached or a high-severity event occurred
        high_risk_event_types = [
            EventType.PRODUCT_UNRESOLVED.value,
            EventType.SUSPICIOUS_BEHAVIOR.value,
            EventType.POSSIBLE_CONCEALMENT.value,
            EventType.HIGH_RISK_DETECTED.value,
            EventType.UNUSUAL_ZONE_TRANSITION.value
        ]

        should_trigger_alert = (
            new_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] or 
            event.event_type in high_risk_event_types
        )

        if should_trigger_alert:
            severity = (
                AlertSeverity.CRITICAL if new_level == RiskLevel.CRITICAL or event.event_type == EventType.POSSIBLE_CONCEALMENT.value
                else AlertSeverity.HIGH if new_level == RiskLevel.HIGH or event.event_type in [EventType.SUSPICIOUS_BEHAVIOR.value, EventType.UNUSUAL_ZONE_TRANSITION.value]
                else AlertSeverity.MEDIUM
            )

            # Fetch contributing signals history for subject
            contributing_signals = cls.get_contributing_signals(db, customer.id)
            title, description = cls.generate_neutral_title_desc(event.event_type, customer.tracking_id, event.zone, new_score, contributing_signals)

            alert_created = Alert(
                video_id=customer.video_id,
                customer_id=customer.id,
                severity=severity.value,
                title=title,
                description=description,
                risk_score=new_score,
                status=AlertStatus.ACTIVE.value,
                event_id=event.id
            )
            db.add(alert_created)
            db.flush()

            # Create an incident for high-risk / critical cases
            if severity in [AlertSeverity.HIGH, AlertSeverity.CRITICAL]:
                incident_created = Incident(
                    alert_id=alert_created.id,
                    video_id=customer.video_id,
                    customer_id=customer.id,
                    incident_type=f"RETAIL_MONITORING_{severity.value}",
                    summary=f"Automated risk threshold ({new_level.value}) triggered for subject {customer.tracking_id} in {event.zone or 'retail zone'}. {description}",
                    risk_score=new_score,
                    incident_status=IncidentStatus.OPEN.value,
                    start_time=event.event_time
                )
                db.add(incident_created)
                db.flush()

        db.commit()
        db.refresh(customer)

        return new_score, new_level, alert_created, incident_created

    @staticmethod
    def get_contributing_signals(db: Session, customer_id: int) -> List[str]:
        """Collects human-readable list of contributing risk signals for a subject."""
        events = db.query(Event).filter(Event.customer_id == customer_id).order_by(Event.event_time.asc()).all()
        signals = []
        for evt in events:
            w = RiskEngine.get_event_weight(evt.event_type)
            if w != 0:
                sign_str = f"+{int(w)}" if w > 0 else f"{int(w)}"
                label = evt.event_type.replace('_', ' ').title()
                zone_info = f" ({evt.zone})" if evt.zone else ""
                signals.append(f"{sign_str} {label}{zone_info}")
        return signals

    @staticmethod
    def generate_neutral_title_desc(
        event_type: str,
        tracking_id: str,
        zone: Optional[str],
        risk_score: float,
        signals: List[str] = None
    ) -> Tuple[str, str]:
        """Generates decision-support neutral wording for alerts with contributing signals explanation."""
        location_str = f"in {zone}" if zone else "in retail store"
        signals_summary = f" Contributing Signals: {', '.join(signals)}." if signals else ""

        descriptions = {
            EventType.PRODUCT_UNRESOLVED.value: (
                f"Unresolved Item Picked - {tracking_id}",
                f"Subject {tracking_id} picked product {location_str} without basket placement.{signals_summary} Staff review recommended. (Risk Score: {risk_score})"
            ),
            EventType.SUSPICIOUS_BEHAVIOR.value: (
                f"Suspicious Activity Pattern - {tracking_id}",
                f"The behaviour analysis model detected activity requiring staff review.{signals_summary} This alert is AI-generated and does not confirm theft. (Risk Score: {risk_score})"
            ),
            EventType.UNUSUAL_ZONE_TRANSITION.value: (
                f"Unusual Zone Transition - {tracking_id}",
                f"Subject {tracking_id} exhibited unusual zone transition {location_str}.{signals_summary} Staff review recommended. (Risk Score: {risk_score})"
            ),
            EventType.POSSIBLE_CONCEALMENT.value: (
                f"High-Priority Review Required - {tracking_id}",
                f"Potential product concealment indicator detected for subject {tracking_id} {location_str}.{signals_summary} High-priority visual verification requested. (Risk Score: {risk_score})"
            ),
            EventType.HIGH_RISK_DETECTED.value: (
                f"High Risk Threshold Exceeded - {tracking_id}",
                f"Subject {tracking_id} accumulated elevated risk score {risk_score} {location_str}.{signals_summary} Security decision support alert."
            )
        }

        default_title = f"Risk Threshold Notice - {tracking_id}"
        default_desc = f"Subject {tracking_id} reached elevated risk level {risk_score} {location_str}.{signals_summary} AI decision support alert."

        return descriptions.get(event_type, (default_title, default_desc))
