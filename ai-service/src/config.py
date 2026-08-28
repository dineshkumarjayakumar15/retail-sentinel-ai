import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Programmatically resolve PROJECT_ROOT (hackathonob) using pathlib.Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class AIServiceSettings(BaseSettings):
    BACKEND_URL: str = "http://127.0.0.1:8002"
    DATASET_PATH: str = ""
    BASKET_MODEL_PATH: str = ""
    BEHAVIOR_MODEL_PATH: str = str(PROJECT_ROOT / "data" / "models" / "behavior_classifier.pt")
    MODEL_PATH: str = str((PROJECT_ROOT / "data" / "models").resolve())
    PROCESSED_VIDEO_DIR: str = str((PROJECT_ROOT / "data" / "processed").resolve())
    UPLOAD_DIR: str = str((PROJECT_ROOT / "uploads").resolve())
    
    YOLO_MODEL: str = "yolov8n.pt"
    FRAME_SKIP: int = 1
    PROCESSING_FPS_LIMIT: int = 15
    YOLO_CONFIDENCE: float = 0.35
    TRACK_DISAPPEARANCE_SECONDS: float = 5.0
    ACTIVE_EVENT_INTERVAL_SECONDS: float = 2.0
    BASKET_ACTIVE_INTERVAL_SECONDS: float = 2.0
    SUSPICIOUS_EVENT_COOLDOWN_SECONDS: float = 10.0

    BEHAVIOR_WINDOW_SECONDS: float = 5.0
    BEHAVIOR_WINDOW_STRIDE_SECONDS: float = 2.0
    SUSPICION_THRESHOLD: float = 0.75
    SHELF_INTERACTION_MIN_SECONDS: float = 3.0
    LONG_DWELL_THRESHOLD_SECONDS: float = 60.0

    BASKET_ASSOCIATION_DISTANCE: float = 250.0
    BASKET_ASSOCIATION_STABLE_FRAMES: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

ai_settings = AIServiceSettings()

os.makedirs(ai_settings.MODEL_PATH, exist_ok=True)
os.makedirs(ai_settings.PROCESSED_VIDEO_DIR, exist_ok=True)
os.makedirs(ai_settings.UPLOAD_DIR, exist_ok=True)
