import os
import sys
import cv2
import time
import traceback
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session

# Add ai-service/src and backend to sys.path for clean imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

from config import ai_settings, PROJECT_ROOT
from utils.logger import ai_logger
from utils.video_utils import VideoUtils
from inference.detector import YOLODetector
from inference.basket_detector import BasketDetector
from inference.tracker import MultiObjectTracker
from zones.zone_manager import ZoneManager
from tracking.customer_manager import CustomerManager
from tracking.basket_manager import BasketManager
from tracking.association import CustomerBasketAssociationEngine
from events.event_generator import EventGenerator
from events.event_client import AIEventClient

def resolve_video_path(path_str: str) -> Path:
    """
    Resolves stored relative or absolute video paths against PROJECT_ROOT
    with fallback candidates for full backward compatibility.
    """
    p = Path(path_str)
    if p.is_absolute() and p.exists():
        return p.resolve()

    candidates = [
        (PROJECT_ROOT / p),
        (PROJECT_ROOT / "uploads" / p.name),
        (PROJECT_ROOT / "backend" / p),
        (PROJECT_ROOT / "backend" / "uploads" / p.name),
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()

    return (PROJECT_ROOT / p).resolve()

class VideoProcessor:
    def __init__(self, db: Session, video_id: int):
        self.db = db
        self.video_id = video_id
        
        # Load Video Record from database
        from app.database.models import Video
        self.video_record = db.query(Video).filter(Video.id == video_id).first()
        if not self.video_record:
            raise ValueError(f"Video ID {video_id} not found in database.")

        # [3] Video file path check & Path resolution
        self.raw_video_path = self.video_record.file_path
        self.resolved_video_path = resolve_video_path(self.raw_video_path)
        self.video_path = str(self.resolved_video_path)

        ai_logger.info(f"[3] Video file path resolution | Video ID={video_id} | Stored: '{self.raw_video_path}' | Resolved Absolute Path: '{self.video_path}'")
        
        if not self.resolved_video_path.exists():
            error_msg = (
                f"VIDEO FILE NOT FOUND (Video ID={self.video_id}). "
                f"Stored path: '{self.raw_video_path}', "
                f"Resolved absolute path: '{self.video_path}'"
            )
            ai_logger.error(f"[3] {error_msg}")
            from app.services.video_service import VideoService
            VideoService.update_processing_progress(
                db=self.db,
                video_id=self.video_id,
                status_val="FAILED",
                progress=0.0,
                current_frame=0,
                total_frames=0,
                message=error_msg
            )
            raise FileNotFoundError(error_msg)

        # [6] YOLO model loading
        ai_logger.info(f"[6] YOLO model loading: '{ai_settings.YOLO_MODEL}'")
        try:
            self.detector = YOLODetector(ai_settings.YOLO_MODEL)
            ai_logger.info(f"[7] YOLO model ready")
        except Exception as e:
            ai_logger.error(f"[6] YOLO model loading FAILED: {e}")
            from app.services.video_service import VideoService
            VideoService.update_processing_progress(
                db=self.db,
                video_id=self.video_id,
                status_val="FAILED",
                progress=0.0,
                current_frame=0,
                total_frames=0,
                message=f"YOLO model loading failed: {str(e)}"
            )
            raise e

        # [8] ByteTrack initializing
        ai_logger.info("[8] ByteTrack initializing")
        self.tracker = MultiObjectTracker()
        
        self.basket_detector = BasketDetector(ai_settings.BASKET_MODEL_PATH)
        self.zone_manager = ZoneManager()
        self.customer_manager = CustomerManager(self.zone_manager)
        self.basket_manager = BasketManager()
        self.association_engine = CustomerBasketAssociationEngine()
        self.event_generator = EventGenerator()
        self.event_client = AIEventClient(ai_settings.BACKEND_URL)

        # [9] Behaviour model check
        ai_logger.info("[9] Behaviour model check")
        try:
            from inference.behavior import BehaviorEngine
            self.behavior_engine = BehaviorEngine()
            ai_logger.info("[9] Behavior model initialized")
        except Exception as e:
            ai_logger.warning(f"[9] Behavior model unavailable ({e}). Continuing core detection pipeline.")
            self.behavior_engine = None

    def process_video(self):
        ai_logger.info(f"Starting Video Processing Pipeline for Video ID={self.video_id} ('{self.video_record.original_filename}')...")

        # [4] OpenCV opening video using resolved absolute path
        ai_logger.info(f"[4] OpenCV opening video absolute path: '{self.video_path}'")
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            error_msg = f"OpenCV failed to open video file (Video ID={self.video_id}) at absolute path: '{self.video_path}'"
            ai_logger.error(f"[4] {error_msg}")
            from app.services.video_service import VideoService
            VideoService.update_processing_progress(
                db=self.db,
                video_id=self.video_id,
                status_val="FAILED",
                progress=0.0,
                current_frame=0,
                total_frames=0,
                message=error_msg
            )
            raise IOError(error_msg)

        # [5] Video metadata loaded
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 1
        fps = float(cap.get(cv2.CAP_PROP_FPS)) or 25.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720
        duration_sec = total_frames / fps

        ai_logger.info(f"[5] Video metadata loaded: {width}x{height} @ {fps:.1f} FPS | Total Frames: {total_frames} | Duration: {duration_sec:.1f}s")

        self.video_record.total_frames = total_frames
        self.video_record.duration_seconds = round(duration_sec, 1)
        self.db.commit()

        # Output Annotated Video Writer Setup
        output_filename = f"processed_video_{self.video_id}_{self.resolved_video_path.name}"
        processed_dir = Path(ai_settings.PROCESSED_VIDEO_DIR).resolve()
        processed_dir.mkdir(parents=True, exist_ok=True)
        processed_file_path = str(processed_dir / output_filename)
        rel_processed_path = f"data/processed/{output_filename}"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out_writer = cv2.VideoWriter(processed_file_path, fourcc, fps, (width, height))

        # [12] Immediately send initial progress update (Frame 0)
        from app.services.video_service import VideoService
        VideoService.update_processing_progress(
            db=self.db,
            video_id=self.video_id,
            status_val="PROCESSING",
            progress=0.1,
            current_frame=0,
            total_frames=total_frames,
            message=f"Processing started: {total_frames} total frames",
            processed_path=rel_processed_path
        )

        frame_idx = 0
        last_progress_update_time = time.time()
        last_progress_pct = 0.0

        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                frame_idx += 1
                timestamp_sec = frame_idx / fps

                # 1. Person Detection
                person_detections = self.detector.detect_persons(frame)

                # 2. Basket Detection
                basket_detections = self.basket_detector.detect_baskets(frame)

                # 3. Customer Tracking
                customer_tracks = self.tracker.update_customer_tracks(person_detections, frame)

                # 4. Basket Tracking
                basket_tracks = self.tracker.update_basket_tracks(basket_detections, frame)

                # 5. Spatial Customer-Basket Association
                associations = self.association_engine.update(customer_tracks, basket_tracks)

                # 6. Customer Lifecycle & Zone Events
                customer_events = self.customer_manager.update(
                    tracks=customer_tracks,
                    video_id=self.video_id,
                    timestamp_seconds=timestamp_sec,
                    frame_width=width,
                    frame_height=height,
                    associations=associations
                )

                # 7. Basket Lifecycle Events
                basket_events = self.basket_manager.update(
                    tracks=basket_tracks,
                    video_id=self.video_id,
                    timestamp_seconds=timestamp_sec,
                    associations=associations
                )

                all_frame_events = customer_events + basket_events

                # 8. Behavior Analysis if model present
                if self.behavior_engine:
                    behavior_events = self.behavior_engine.analyze_frame_tracks(
                        tracks=customer_tracks,
                        video_id=self.video_id,
                        timestamp_seconds=timestamp_sec,
                        associations=associations
                    )
                    all_frame_events.extend(behavior_events)

                # Send generated events to backend
                for evt in all_frame_events:
                    self.event_client.send_event(evt)

                # Annotate frame
                annotated_frame = VideoUtils.draw_tracks_and_zones(
                    frame=frame,
                    customer_tracks=customer_tracks,
                    basket_tracks=basket_tracks,
                    associations=associations,
                    zone_manager=self.zone_manager
                )
                out_writer.write(annotated_frame)

                # Dispatch progress updates
                now_time = time.time()
                progress_pct = (frame_idx / total_frames) * 100.0
                if frame_idx == 1 or (progress_pct - last_progress_pct >= 1.0) or (now_time - last_progress_update_time >= 1.0):
                    VideoService.update_processing_progress(
                        db=self.db,
                        video_id=self.video_id,
                        status_val="PROCESSING",
                        progress=progress_pct,
                        current_frame=frame_idx,
                        total_frames=total_frames,
                        message=f"Frame {frame_idx}/{total_frames} ({progress_pct:.1f}%) processed",
                        processed_path=rel_processed_path
                    )
                    last_progress_pct = progress_pct
                    last_progress_update_time = now_time

            # Final completion state
            VideoService.update_processing_progress(
                db=self.db,
                video_id=self.video_id,
                status_val="COMPLETED",
                progress=100.0,
                current_frame=total_frames,
                total_frames=total_frames,
                message="AI Video Processing Completed Successfully",
                processed_path=rel_processed_path
            )
            ai_logger.info(f"Video Processing Pipeline Completed for Video ID={self.video_id}! Output: '{processed_file_path}'")

        except Exception as e:
            tb_str = traceback.format_exc()
            ai_logger.error(f"Error processing Video ID={self.video_id}:\n{tb_str}")
            VideoService.update_processing_progress(
                db=self.db,
                video_id=self.video_id,
                status_val="FAILED",
                progress=0.0,
                current_frame=frame_idx,
                total_frames=total_frames,
                message=f"Processing failed at frame {frame_idx}: {str(e)}",
                processed_path=rel_processed_path
            )
            raise e
        finally:
            cap.release()
            out_writer.release()
