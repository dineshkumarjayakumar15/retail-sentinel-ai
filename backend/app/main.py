import os
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.database.connection import init_db
from app.websocket.manager import manager
from app.routers import (
    health, videos, dashboard, customers,
    events, alerts, incidents, analytics, settings as settings_router
)

app = FastAPI(
    title="Retail Sentinel AI API",
    description="Production-quality retail surveillance, customer risk calculation & decision-support backend service.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration — Allow all origins for Vercel & local frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Uploads directory for raw video feed preview
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Mount Static Processed & Data directory for AI annotated video playback
if os.path.exists(settings.PROCESSED_VIDEO_DIR):
    app.mount("/data/processed", StaticFiles(directory=settings.PROCESSED_VIDEO_DIR), name="processed_videos")

data_dir = str(settings.PROJECT_ROOT / "data")
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")

# Include Routers
app.include_router(health.router)
app.include_router(videos.router)
app.include_router(dashboard.router)
app.include_router(customers.router)
app.include_router(events.router)
app.include_router(alerts.router)
app.include_router(incidents.router)
app.include_router(analytics.router)
app.include_router(settings_router.router)

@app.on_event("startup")
def on_startup():
    """Initializes database tables on FastAPI server startup."""
    init_db()

@app.websocket("/ws/dashboard")
async def websocket_dashboard(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates (events, risk score updates, alert notifications).
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open & handle client messages/heartbeats if sent
            data = await websocket.receive_text()
            # Echo back pong or acknowledge message
            await websocket.send_text(f'{{"type": "ACK", "client_message": {data}}}')
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        manager.disconnect(websocket)
