import os
import sys
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import ai_settings
from models.schemas import TrackedEntity

class CustomerBasketAssociationEngine:
    def __init__(self):
        # Maps basket_id -> candidate_customer_id
        self.candidate_associations: Dict[str, str] = {}
        # Maps basket_id -> consecutive frame count
        self.candidate_frame_counts: Dict[str, int] = {}
        # Confirmed associations: basket_id -> (customer_id, confidence)
        self.confirmed_associations: Dict[str, Tuple[str, float]] = {}

    def update_associations(
        self,
        baskets: List[TrackedEntity],
        customers: List[TrackedEntity]
    ) -> Dict[str, Tuple[str, float]]:
        """
        Evaluates spatial proximity and temporal stability across multiple frames.
        Returns confirmed associations dict: { basket_id: (customer_id, confidence) }
        """
        if not baskets or not customers:
            return self.confirmed_associations

        max_dist = ai_settings.BASKET_ASSOCIATION_DISTANCE
        stable_threshold = ai_settings.BASKET_ASSOCIATION_STABLE_FRAMES

        for basket in baskets:
            b_center = ((basket.bbox[0] + basket.bbox[2]) / 2.0, (basket.bbox[1] + basket.bbox[3]) / 2.0)
            
            # Find nearest customer
            nearest_customer_id = None
            min_dist = float("inf")

            for cust in customers:
                c_center = ((cust.bbox[0] + cust.bbox[2]) / 2.0, (cust.bbox[1] + cust.bbox[3]) / 2.0)
                dist = math.hypot(b_center[0] - c_center[0], b_center[1] - c_center[1])
                if dist < min_dist and dist <= max_dist:
                    min_dist = dist
                    nearest_customer_id = cust.tracking_id

            if nearest_customer_id is not None:
                current_candidate = self.candidate_associations.get(basket.tracking_id)
                if current_candidate == nearest_customer_id:
                    self.candidate_frame_counts[basket.tracking_id] = self.candidate_frame_counts.get(basket.tracking_id, 0) + 1
                else:
                    self.candidate_associations[basket.tracking_id] = nearest_customer_id
                    self.candidate_frame_counts[basket.tracking_id] = 1

                # Calculate spatial confidence (inverse distance normalized)
                conf = max(0.5, round(1.0 - (min_dist / max_dist), 2))

                # Confirm association once temporal stability threshold is reached
                if self.candidate_frame_counts[basket.tracking_id] >= stable_threshold:
                    self.confirmed_associations[basket.tracking_id] = (nearest_customer_id, conf)
            else:
                # Reset candidate if out of proximity range
                if basket.tracking_id in self.candidate_frame_counts:
                    self.candidate_frame_counts[basket.tracking_id] = max(0, self.candidate_frame_counts[basket.tracking_id] - 1)
                    if self.candidate_frame_counts[basket.tracking_id] == 0:
                        self.candidate_associations.pop(basket.tracking_id, None)

        return self.confirmed_associations

    def update(self, customer_tracks=None, basket_tracks=None) -> Dict[str, Tuple[str, float]]:
        """Alias method accepting customer_tracks and basket_tracks."""
        baskets = basket_tracks if isinstance(basket_tracks, list) else []
        customers = customer_tracks if isinstance(customer_tracks, list) else []
        return self.update_associations(baskets, customers)
