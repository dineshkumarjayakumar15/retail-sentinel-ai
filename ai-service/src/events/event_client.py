import os
import sys
import requests
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import EventPayload
from utils.logger import ai_logger

class AIEventClient:
    def __init__(self, backend_url: str = None):
        env_url = os.getenv("BACKEND_URL")
        base = backend_url or env_url or ai_settings.BACKEND_URL
        self.backend_url = base.rstrip('/')

    def send_event(self, event: EventPayload) -> bool:
        """Sends structured event payload to backend FastAPI API endpoint (POST /api/events)."""
        url = f"{self.backend_url}/api/events"
        payload = {
            "video_id": event.video_id,
            "tracking_id": event.tracking_id,
            "entity_type": event.entity_type,
            "event_type": event.event_type,
            "timestamp_seconds": event.timestamp_seconds,
            "zone": event.zone,
            "confidence": event.confidence,
            "metadata": event.metadata
        }

        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code in [200, 201]:
                data = res.json()
                ai_logger.info(f"[AI Event Client] Event {event.event_type} for {event.tracking_id} sent successfully to {url}. Risk Score: {data.get('current_risk_score')}")
                return True
            else:
                ai_logger.warning(f"[AI Event Client] Failed to send event to {url} ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            ai_logger.error(f"[AI Event Client] Exception sending event to {url}: {e}")
            return False
