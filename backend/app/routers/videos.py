from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.video import VideoResponse, VideoStatusResponse
from app.services.video_service import VideoService

router = APIRouter(prefix="/api/videos", tags=["Videos"])

@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Validates supported video formats, saves video into uploads/, creates Video record, and triggers background AI pipeline."""
    return await VideoService.upload_video(db, file, background_tasks)

@router.get("", response_model=List[VideoResponse])
def get_videos(db: Session = Depends(get_db)):
    """Returns list of all uploaded videos."""
    return VideoService.get_videos(db)

@router.get("/{id}", response_model=VideoResponse)
def get_video_by_id(id: int, db: Session = Depends(get_db)):
    """Returns details for a specific video."""
    video = VideoService.get_video_by_id(db, id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@router.get("/{id}/status", response_model=VideoStatusResponse)
def get_video_status(id: int, db: Session = Depends(get_db)):
    """Returns real-time processing status & progress % for a video."""
    video = VideoService.get_video_by_id(db, id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    error_msg = video.status_message if video.processing_status == "FAILED" else None

    return VideoStatusResponse(
        video_id=video.id,
        filename=video.original_filename,
        status=video.processing_status,
        progress=video.progress_percent or 0.0,
        current_frame=video.current_frame or 0,
        total_frames=video.total_frames,
        duration_seconds=video.duration_seconds,
        message=video.status_message or "Processing",
        error=error_msg,
        processed_video_path=video.processed_video_path
    )

@router.post("/{id}/process")
def process_video(id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Triggers asynchronous OpenCV + YOLO + ByteTrack video processing pipeline."""
    return VideoService.start_processing(db, id, background_tasks)
