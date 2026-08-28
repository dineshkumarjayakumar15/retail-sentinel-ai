"""
Retail Sentinel AI - AI Service Integration Interface Placeholder (Phase 2 & 3 Prep)

This placeholder module outlines how the YOLO + OpenCV + ByteTrack video intelligence pipeline
will interface with the backend in Phase 2.

In Phase 2:
1. OpenCV reads video frames from `uploads/<filename>`.
2. YOLOv8 detects bounding boxes for Persons, Baskets, Products, Shelves.
3. ByteTrack maintains consistent `tracking_id` for entities across frames.
4. Spatial & temporal analysis triggers events (e.g. CUSTOMER_ENTERED, SHELF_INTERACTION,
   PRODUCT_UNRESOLVED, POSSIBLE_CONCEALMENT).
5. Events are POSTed in real-time to `/api/events` backend endpoint.
"""

import os
import time
import requests
import json

BACKEND_EVENT_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8002") + "/api/events"

def simulate_ai_pipeline_stream(video_id: int, tracking_id: str = "customer_001"):
    """
    Simulates real-time event streaming from AI processing pipeline to backend API.
    """
    print(f"[AI Service Placeholder] Starting simulated processing for video_id={video_id}...")
    
    events_sequence = [
        {
            "video_id": video_id,
            "tracking_id": tracking_id,
            "entity_type": "CUSTOMER",
            "event_type": "CUSTOMER_ENTERED",
            "timestamp_seconds": 2.5,
            "zone": "entrance",
            "confidence": 0.96,
            "metadata": {"bbox": [100, 120, 250, 480], "apparel": "blue jacket"}
        },
        {
            "video_id": video_id,
            "tracking_id": tracking_id,
            "entity_type": "CUSTOMER",
            "event_type": "SHELF_INTERACTION",
            "timestamp_seconds": 8.0,
            "zone": "aisle_3_electronics",
            "confidence": 0.91,
            "metadata": {"shelf_id": "shelf_electronics_4"}
        },
        {
            "video_id": video_id,
            "tracking_id": tracking_id,
            "entity_type": "CUSTOMER",
            "event_type": "PRODUCT_PICKED",
            "timestamp_seconds": 12.2,
            "zone": "aisle_3_electronics",
            "confidence": 0.89,
            "metadata": {"product_class": "high_value_item"}
        },
        {
            "video_id": video_id,
            "tracking_id": tracking_id,
            "entity_type": "CUSTOMER",
            "event_type": "POSSIBLE_CONCEALMENT",
            "timestamp_seconds": 18.7,
            "zone": "aisle_3_electronics",
            "confidence": 0.85,
            "metadata": {"anomaly": "hand movement into inner coat pocket", "duration_sec": 3.2}
        }
    ]

    for evt in events_sequence:
        try:
            res = requests.post(BACKEND_EVENT_URL, json=evt)
            print(f"[AI Service Placeholder] Sent event {evt['event_type']} -> Status {res.status_code}: {res.json()}")
        except Exception as e:
            print(f"[AI Service Placeholder] Error sending event: {e}")
        time.sleep(1.0)

if __name__ == "__main__":
    simulate_ai_pipeline_stream(video_id=1)
