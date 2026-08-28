import os
import sys
import uuid
import traceback
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.config import settings, PROJECT_ROOT
from app.database.models import Video
from app.utils.enums import VideoStatus

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

class VideoService:

    @staticmethod
    async def upload_video(db: Session, file: UploadFile, background_tasks: Optional[BackgroundTasks] = None) -> Video:
        filename = file.filename or "video.mp4"
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported video format '{ext}'. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        
        # Save file to canonical absolute path inside PROJECT_ROOT / uploads
        upload_dir = Path(settings.UPLOAD_DIR).resolve()
        upload_dir.mkdir(parents=True, exist_ok=True)
        abs_file_path = upload_dir / unique_filename

        # Write uploaded bytes to disk
        async with aiofiles.open(abs_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        # Verify physical file existence immediately after write
        if not abs_file_path.exists() or abs_file_path.stat().st_size == 0:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Video upload failed: File could not be written to disk at {abs_file_path}"
            )

        # Store stable relative path for DB portability
        rel_file_path = f"uploads/{unique_filename}"

        initial_status = VideoStatus.PROCESSING.value if background_tasks else VideoStatus.UPLOADED.value
        initial_message = "Initiating OpenCV + YOLO + ByteTrack intelligence pipeline..." if background_tasks else "Uploaded & Ready for Processing"

        db_video = Video(
            filename=unique_filename,
            original_filename=filename,
            file_path=rel_file_path,
            upload_time=datetime.utcnow(),
            processing_status=initial_status,
            progress_percent=0.0,
            status_message=initial_message,
            current_frame=0,
            duration_seconds=60.0,
            total_frames=1800
        )
        db.add(db_video)
        db.commit()
        db.refresh(db_video)

        # Trigger AI Video Processing Pipeline automatically in background
        if background_tasks:
            background_tasks.add_task(VideoService.run_ai_pipeline_background, db_video.id)

        return db_video

    @staticmethod
    def get_videos(db: Session) -> List[Video]:
        return db.query(Video).order_by(Video.created_at.desc()).all()

    @staticmethod
    def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
        return db.query(Video).filter(Video.id == video_id).first()

    @staticmethod
    def update_processing_progress(
        db: Session,
        video_id: int,
        status_val: str,
        progress: float,
        current_frame: int,
        total_frames: int,
        message: str,
        processed_path: Optional[str] = None
    ):
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.processing_status = status_val
            video.progress_percent = round(progress, 1)
            video.current_frame = current_frame
            if total_frames:
                video.total_frames = total_frames
            video.status_message = message
            if processed_path:
                video.processed_video_path = processed_path
            db.commit()

    @staticmethod
    def run_ai_pipeline_background(video_id: int):
        """
        Executes the AI Video Processor pipeline in the background.
        Injects sys.path dynamically and resolves video paths via PROJECT_ROOT.
        """
        print(f"[1] Video processing requested for video_id={video_id}")
        print(f"[2] Background task started for video_id={video_id}")
        
        backend_dir = (PROJECT_ROOT / "backend").resolve()
        ai_src = (PROJECT_ROOT / "ai-service" / "src").resolve()
        
        for p in [str(ai_src), str(backend_dir), str(PROJECT_ROOT)]:
            if p not in sys.path:
                sys.path.insert(0, p)

        try:
            from app.database.connection import SessionLocal
            from inference.video_processor import VideoProcessor

            db = SessionLocal()
            try:
                processor = VideoProcessor(db=db, video_id=video_id)
                processor.process_video()
            finally:
                db.close()
        except Exception as e:
            tb_str = traceback.format_exc()
            print(f"[VideoService ERROR] Background AI pipeline exception for video_id={video_id}:\n{tb_str}")
            from app.database.connection import SessionLocal
            db = SessionLocal()
            try:
                VideoService.update_processing_progress(
                    db=db,
                    video_id=video_id,
                    status_val=VideoStatus.FAILED.value,
                    progress=0.0,
                    current_frame=0,
                    total_frames=0,
                    message=f"Processing failed: {str(e)}"
                )
            finally:
                db.close()

    @staticmethod
    def start_processing(db: Session, video_id: int, background_tasks: BackgroundTasks) -> dict:
        video = VideoService.get_video_by_id(db, video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        video.processing_status = VideoStatus.PROCESSING.value
        video.progress_percent = 0.0
        video.status_message = "Initiating OpenCV + YOLO + ByteTrack intelligence pipeline..."
        db.commit()

        # Dispatch background processing task
        background_tasks.add_task(VideoService.run_ai_pipeline_background, video_id)

        return {
            "video_id": video.id,
            "status": VideoStatus.PROCESSING.value,
            "message": "Video processing started in background"
        }
