import os
import sys
import cv2
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.schemas import TrackedEntity

class VideoUtils:

    @staticmethod
    def draw_annotations(
        frame: np.ndarray,
        tracked_persons: List[TrackedEntity],
        tracked_baskets: List[TrackedEntity] = None,
        associations: Dict[str, Tuple[str, float]] = None,
        fps: float = 0.0,
        frame_idx: int = 0
    ) -> np.ndarray:
        """
        Draws clean, professional overlay bounding boxes, customer tracking IDs,
        basket tracking IDs, customer-basket association indicators, and telemetry stats onto the video frame.
        """
        annotated = frame.copy()
        h, w, _ = frame.shape
        tracked_baskets = tracked_baskets or []
        associations = associations or {}

        # 1. Draw Person Bounding Boxes & Badges
        person_centers: Dict[str, Tuple[int, int]] = {}
        for p in tracked_persons:
            if not p.bbox or len(p.bbox) < 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in p.bbox[:4]]
            person_centers[p.tracking_id] = ((x1 + x2) // 2, (y1 + y2) // 2)

            if p.risk_level == "CRITICAL":
                color = (200, 50, 160)
            elif p.risk_level == "HIGH":
                color = (50, 50, 240)
            elif p.risk_level == "MEDIUM":
                color = (30, 160, 240)
            else:
                color = (50, 200, 100)

            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            label = f"{p.tracking_id} | {p.zone} | Risk:{p.risk_score:.0f}"
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)

            cv2.rectangle(annotated, (x1, max(0, y1 - 22)), (x1 + text_w + 10, max(22, y1)), color, -1)
            cv2.putText(
                annotated,
                label,
                (x1 + 5, max(15, y1 - 6)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )

        # 2. Draw Basket Bounding Boxes & Badges
        basket_centers: Dict[str, Tuple[int, int]] = {}
        for b in tracked_baskets:
            if not b.bbox or len(b.bbox) < 4:
                continue

            x1, y1, x2, y2 = [int(v) for v in b.bbox[:4]]
            basket_centers[b.tracking_id] = ((x1 + x2) // 2, (y1 + y2) // 2)
            b_color = (245, 158, 11)

            cv2.rectangle(annotated, (x1, y1), (x2, y2), b_color, 2)

            b_assoc = associations.get(b.tracking_id)
            if b_assoc:
                b_label = f"{b.tracking_id} -> {b_assoc[0]}"
            else:
                b_label = f"{b.tracking_id}"

            (text_w, text_h), _ = cv2.getTextSize(b_label, cv2.FONT_HERSHEY_SIMPLEX, 0.42, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - 20)), (x1 + text_w + 8, max(20, y1)), b_color, -1)
            cv2.putText(annotated, b_label, (x1 + 4, max(14, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (255, 255, 255), 1, cv2.LINE_AA)

            if b_assoc and b_assoc[0] in person_centers:
                c_pt = person_centers[b_assoc[0]]
                b_pt = basket_centers[b.tracking_id]
                cv2.line(annotated, b_pt, c_pt, (6, 182, 212), 2, cv2.LINE_AA)

        # 3. Draw Telemetry Banner Top Left
        banner_text = f"RETAIL SENTINEL AI | Frame: {frame_idx} | Customers: {len(tracked_persons)} | Baskets: {len(tracked_baskets)}"
        cv2.rectangle(annotated, (10, 10), (480, 40), (15, 23, 42), -1)
        cv2.putText(annotated, banner_text, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (6, 182, 212), 1, cv2.LINE_AA)

        return annotated

    @staticmethod
    def draw_tracks_and_zones(
        frame: np.ndarray,
        customer_tracks: List[Any] = None,
        basket_tracks: List[Any] = None,
        associations: Dict[str, Tuple[str, float]] = None,
        zone_manager: Any = None
    ) -> np.ndarray:
        """Alias method drawing tracks and store zone overlays."""
        annotated = frame.copy()
        customer_tracks = customer_tracks or []
        basket_tracks = basket_tracks or []
        associations = associations or {}

        person_entities = []
        for item in customer_tracks:
            if isinstance(item, tuple) and len(item) >= 2:
                tracking_id, bbox = item[0], item[1]
                person_entities.append(TrackedEntity(
                    tracking_id=tracking_id,
                    bbox=bbox,
                    first_seen_time=datetime.utcnow(),
                    last_seen_time=datetime.utcnow(),
                    zone="shopping_area",
                    status="ACTIVE"
                ))

        basket_entities = []
        for item in basket_tracks:
            if isinstance(item, tuple) and len(item) >= 2:
                tracking_id, bbox = item[0], item[1]
                basket_entities.append(TrackedEntity(
                    tracking_id=tracking_id,
                    bbox=bbox,
                    first_seen_time=datetime.utcnow(),
                    last_seen_time=datetime.utcnow(),
                    status="ACTIVE"
                ))

        return VideoUtils.draw_annotations(annotated, person_entities, basket_entities, associations)
