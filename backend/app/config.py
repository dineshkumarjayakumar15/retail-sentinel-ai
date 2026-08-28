import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Programmatically resolve PROJECT_ROOT (hackathonob) using pathlib.Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PROJECT_ROOT / "backend"
DEFAULT_DB_PATH = str(BASE_DIR / "retail_sentinel.db").replace("\\", "/")

class Settings(BaseSettings):
    PORT: int = 8002
    HOST: str = "127.0.0.1"
    DEBUG: bool = True
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH}"
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:8002,http://localhost:8002"
    
    # Canonical absolute paths derived from PROJECT_ROOT
    UPLOAD_DIR: str = str((PROJECT_ROOT / "uploads").resolve())
    PROCESSED_VIDEO_DIR: str = str((PROJECT_ROOT / "data" / "processed").resolve())
    MODEL_PATH: str = str((PROJECT_ROOT / "data" / "models").resolve())

    # Dataset & AI Configuration
    DATASET_PATH: str = ""
    BASKET_MODEL_PATH: str = ""
    BEHAVIOR_MODEL_PATH: str = str(PROJECT_ROOT / "data" / "models" / "behavior_classifier.pt")
    BACKEND_URL: str = "http://127.0.0.1:8002"
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

    # Risk Engine Rules & Scoring Deltas
    SCORE_CUSTOMER_ENTERED: float = 0.0
    SCORE_SHELF_INTERACTION: float = 5.0
    SCORE_PRODUCT_PICKED: float = 10.0
    SCORE_PRODUCT_IN_BASKET: float = -10.0
    SCORE_PRODUCT_RETURNED: float = -5.0
    SCORE_PRODUCT_UNRESOLVED: float = 25.0
    SCORE_SUSPICIOUS_BEHAVIOR: float = 30.0
    SCORE_POSSIBLE_CONCEALMENT: float = 45.0
    SCORE_HIGH_RISK_DETECTED: float = 50.0
    SCORE_LONG_DWELL_TIME: float = 10.0
    SCORE_UNUSUAL_ZONE_TRANSITION: float = 15.0

    # Risk Threshold Boundaries
    RISK_THRESHOLD_LOW: float = 0.0
    RISK_THRESHOLD_MEDIUM: float = 30.0
    RISK_THRESHOLD_HIGH: float = 60.0
    RISK_THRESHOLD_CRITICAL: float = 80.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()

# Ensure canonical directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_VIDEO_DIR, exist_ok=True)
os.makedirs(settings.MODEL_PATH, exist_ok=True)
os.makedirs(str(PROJECT_ROOT / "data" / "raw"), exist_ok=True)
