from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Retail Sentinel AI Backend",
        "phase": 1,
        "timestamp": datetime.utcnow().isoformat(),
        "ai_pipeline_ready": True
    }
