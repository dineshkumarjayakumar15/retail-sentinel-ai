from datetime import datetime, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import Incident, Alert, Customer, Event
from app.utils.enums import AlertSeverity, RiskLevel

class AnalyticsService:

    @staticmethod
    def get_overview_analytics(db: Session, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        total_incidents = db.query(Incident).filter(Incident.created_at >= start_date).count()
        high_risk_incidents = db.query(Incident).filter(
            Incident.created_at >= start_date,
            Incident.risk_score >= 60.0
        ).count()
        active_customers_cnt = db.query(Customer).filter(Customer.status == "ACTIVE").count()

        # Dynamic daily stats for the requested days range (up to 30 days, aggregated per day)
        num_days = min(days, 30)
        daily_stats: List[Dict[str, Any]] = []
        for i in range(num_days - 1, -1, -1):
            day = datetime.utcnow() - timedelta(days=i)
            day_str = day.strftime("%b %d")
            start_of_day = datetime(day.year, day.month, day.day, 0, 0, 0)
            end_of_day = datetime(day.year, day.month, day.day, 23, 59, 59)

            suspicious = db.query(Incident).filter(
                Incident.created_at >= start_of_day,
                Incident.created_at <= end_of_day,
                Incident.risk_score < 60.0
            ).count()

            high_risk = db.query(Incident).filter(
                Incident.created_at >= start_of_day,
                Incident.created_at <= end_of_day,
                Incident.risk_score >= 60.0
            ).count()

            daily_stats.append({
                "date": day_str,
                "suspicious_incidents": suspicious,
                "high_risk_incidents": high_risk
            })

        # Risk distribution from real Alerts in SQLite
        low_count = db.query(Alert).filter(Alert.created_at >= start_date, Alert.severity == AlertSeverity.LOW.value).count()
        med_count = db.query(Alert).filter(Alert.created_at >= start_date, Alert.severity == AlertSeverity.MEDIUM.value).count()
        high_count = db.query(Alert).filter(Alert.created_at >= start_date, Alert.severity == AlertSeverity.HIGH.value).count()
        crit_count = db.query(Alert).filter(Alert.created_at >= start_date, Alert.severity == AlertSeverity.CRITICAL.value).count()

        risk_distribution = [
            {"name": "Low Risk", "value": low_count, "color": "#10B981"},
            {"name": "Medium Risk", "value": med_count, "color": "#F59E0B"},
            {"name": "High Risk", "value": high_count, "color": "#EF4444"},
            {"name": "Critical Risk", "value": crit_count, "color": "#7C3AED"}
        ]

        # Customer Risk Level Distribution from real Customers in SQLite
        low_cust = db.query(Customer).filter(Customer.risk_level == RiskLevel.LOW.value).count()
        med_cust = db.query(Customer).filter(Customer.risk_level == RiskLevel.MEDIUM.value).count()
        high_cust = db.query(Customer).filter(Customer.risk_level == RiskLevel.HIGH.value).count()
        crit_cust = db.query(Customer).filter(Customer.risk_level == RiskLevel.CRITICAL.value).count()

        customer_risk_distribution = [
            {"name": "Low Risk", "value": low_cust, "color": "#10B981"},
            {"name": "Medium Risk", "value": med_cust, "color": "#F59E0B"},
            {"name": "High Risk", "value": high_cust, "color": "#EF4444"},
            {"name": "Critical Risk", "value": crit_cust, "color": "#7C3AED"}
        ]

        return {
            "total_incidents_30d": total_incidents,
            "high_risk_incidents_30d": high_risk_incidents,
            "active_customers": active_customers_cnt,
            "daily_stats": daily_stats,
            "risk_distribution": risk_distribution,
            "customer_risk_distribution": customer_risk_distribution
        }
