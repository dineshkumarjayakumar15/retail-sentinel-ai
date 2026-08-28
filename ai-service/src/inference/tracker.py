import os
import sys
import math
import numpy as np
from typing import List, Dict, Any, Tuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from models.schemas import Detection

class MultiObjectTracker:
    def __init__(self, max_disappeared: int = 15):
        self.next_customer_id = 1
        self.tracked_objects: Dict[str, Dict[str, Any]] = {}
        self.disappeared: Dict[str, int] = {}
        self.max_disappeared = max_disappeared

        # Attempt to load Supervision ByteTrack if available
        self.bytetrack_tracker = None
        try:
            import supervision as sv
            self.bytetrack_tracker = sv.ByteTrack()
        except Exception:
            self.bytetrack_tracker = None

    def update_person_tracks(self, detections: List[Detection], frame: np.ndarray = None) -> List[Tuple[str, List[float], float]]:
        """
        Updates multi-object tracks for persons.
        Returns list of (tracking_id, bbox, confidence).
        """
        results = []

        if self.bytetrack_tracker is not None and len(detections) > 0:
            try:
                import supervision as sv
                boxes = np.array([d.bbox for d in detections])
                confs = np.array([d.confidence for d in detections])
                cls_ids = np.array([d.class_id for d in detections])

                sv_detections = sv.Detections(
                    xyxy=boxes,
                    confidence=confs,
                    class_id=cls_ids
                )
                tracked = self.bytetrack_tracker.update_with_detections(sv_detections)

                for t in tracked:
                    raw_id = int(t[4])
                    bbox = t[0].tolist()
                    conf = float(t[2]) if len(t) > 2 else 0.9
                    tracking_id = f"customer_{raw_id:03d}"
                    results.append((tracking_id, bbox, conf))
                return results
            except Exception:
                pass

        # Distance-IoU Fallback Tracker
        results = self._distance_iou_track(detections, prefix="customer")
        return results

    def update_customer_tracks(self, detections: List[Detection], frame: np.ndarray = None) -> List[Tuple[str, List[float], float]]:
        """Alias for update_person_tracks."""
        return self.update_person_tracks(detections, frame)

    def update_basket_tracks(self, detections: List[Detection], frame: np.ndarray = None) -> List[Tuple[str, List[float], float]]:
        """Updates multi-object tracks for baskets. Returns [] if none detected."""
        if not detections:
            return []
        return self._distance_iou_track(detections, prefix="basket")

    def _distance_iou_track(self, detections: List[Detection], prefix: str = "customer") -> List[Tuple[str, List[float], float]]:
        if not detections:
            for track_id in list(self.disappeared.keys()):
                self.disappeared[track_id] += 1
                if self.disappeared[track_id] > self.max_disappeared:
                    del self.tracked_objects[track_id]
                    del self.disappeared[track_id]
            return []

        input_centers = []
        for d in detections:
            cx = (d.bbox[0] + d.bbox[2]) / 2.0
            cy = (d.bbox[1] + d.bbox[3]) / 2.0
            input_centers.append((cx, cy))

        if not self.tracked_objects:
            for i, d in enumerate(detections):
                app_id = f"{prefix}_{self.next_customer_id:03d}"
                self.next_customer_id += 1
                self.tracked_objects[app_id] = {"bbox": d.bbox, "center": input_centers[i], "conf": d.confidence}
                self.disappeared[app_id] = 0

        else:
            object_ids = list(self.tracked_objects.keys())
            object_centers = [self.tracked_objects[oid]["center"] for oid in object_ids]

            D = []
            for oc in object_centers:
                row = []
                for ic in input_centers:
                    dist = math.hypot(oc[0] - ic[0], oc[1] - ic[1])
                    row.append(dist)
                D.append(row)

            matched_input_indices = set()
            matched_object_ids = set()

            for obj_idx, row in enumerate(D):
                min_dist = min(row)
                min_inp_idx = row.index(min_dist)

                if min_dist < 150.0 and min_inp_idx not in matched_input_indices:
                    obj_id = object_ids[obj_idx]
                    self.tracked_objects[obj_id] = {
                        "bbox": detections[min_inp_idx].bbox,
                        "center": input_centers[min_inp_idx],
                        "conf": detections[min_inp_idx].confidence
                    }
                    self.disappeared[obj_id] = 0
                    matched_input_indices.add(min_inp_idx)
                    matched_object_ids.add(obj_id)

            for i, d in enumerate(detections):
                if i not in matched_input_indices:
                    app_id = f"{prefix}_{self.next_customer_id:03d}"
                    self.next_customer_id += 1
                    self.tracked_objects[app_id] = {"bbox": d.bbox, "center": input_centers[i], "conf": d.confidence}
                    self.disappeared[app_id] = 0

            for obj_id in object_ids:
                if obj_id not in matched_object_ids:
                    self.disappeared[obj_id] += 1
                    if self.disappeared[obj_id] > self.max_disappeared:
                        del self.tracked_objects[obj_id]
                        del self.disappeared[obj_id]

        output = []
        for obj_id, data in self.tracked_objects.items():
            if obj_id.startswith(prefix):
                output.append((obj_id, data["bbox"], data["conf"]))
        return output
