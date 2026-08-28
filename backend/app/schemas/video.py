from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class VideoBase(BaseModel):
    filename: str
    original_filename: str
    file_path: str
    processing_status: str
    processed_video_path: Optional[str] = None
    progress_percent: float = 0.0
    status_message: str = "Uploaded"
    current_frame: int = 0
    total_frames: Optional[int] = None
    duration_seconds: Optional[float] = None

class VideoCreate(BaseModel):
    filename: str
    original_filename: str
    file_path: str

class VideoResponse(VideoBase):
    id: int
    upload_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VideoStatusResponse(BaseModel):
    video_id: int
    filename: str
    status: str
    progress: float
    current_frame: int
    total_frames: Optional[int] = None
    duration_seconds: Optional[float] = None
    message: str
    error: Optional[str] = None
    processed_video_path: Optional[str] = None
