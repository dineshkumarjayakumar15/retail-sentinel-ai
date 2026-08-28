<<<<<<< HEAD
# Retail Sentinel AI — Production Intelligence System

**Retail Sentinel AI** is an enterprise-grade AI-powered retail monitoring, video surveillance, customer tracking, and decision-support platform.

The system processes surveillance video feeds using **OpenCV + YOLO + ByteTrack**, tracks customer entry/exit states, calculates explainable risk scores, streams events to a FastAPI backend, updates SQLite, and renders real-time telemetry on a modern light-themed React glassmorphism dashboard shell.

---

## 🏗️ Architecture & Pipeline Flow

```
VIDEO FEED (Upload / Dataset)
        │
        ▼
   OpenCV Frame Processing
        │
        ▼
YOLO Person/Object Detection (Single-Instance Loader)
        │
        ▼
ByteTrack Multi-Object Tracking (customer_001, customer_002)
        │
        ▼
Spatial Zone Manager (entrance, shopping_area, shelf_zone, exit)
        │
        ▼
Customer State Manager (Entry, Active Throttling, 5s Exit Disappearance)
        │
        ▼
Behavior Analysis Engine (Interaction duration & Anomaly signals)
        │
        ▼
Centralized Event Generator (Deduplication & Cooldowns)
        │
        ▼
AI Event Client (POST /api/events)
        │
        ▼
FastAPI Backend (Event Validation & State Updates)
        │
        ▼
SQLite Database (Single Source of Truth)
        │
        ▼
Explainable Risk Engine (0-100 Clamping & Alert/Incident Triggering)
        │
        ▼
WebSocket Stream (/ws/dashboard) & Real-time React Dashboard UI
```

---

## 🌟 Key Features (Phase 1 & Phase 2 Integrated)

* **Dataset Inspection Tool**: Command `python ai-service/src/dataset/inspect_dataset.py` inspects any local dataset directory (`DATASET_PATH` in `.env`), checks video/image counts, YOLO annotations vs classification folders, and auto-recommends Strategy A, B, or C.
* **OpenCV + YOLO + ByteTrack Video Intelligence**: Loads Ultralytics YOLO model once and tracks persons with stable tracking IDs (`customer_001`, `customer_002`).
* **Customer State Machine**:
  * `CUSTOMER_ENTERED`: Generated on initial detection. Sets status `ACTIVE`.
  * `CUSTOMER_ACTIVE`: Throttled every 2s to prevent event spam. Updates last seen time and zone.
  * `CUSTOMER_EXITED`: Triggered when customer is undetected for > 5s (`TRACK_DISAPPEARANCE_SECONDS`). Calculates `total_stay_seconds = exit_time - entry_time` and sets status `EXITED`.
* **Spatial Zone Management**: Configurable `zones.json` mapping frame bounding boxes to `entrance`, `shopping_area`, `shelf_zone`, and `exit`.
* **Explainable Rule-Based Risk Engine**: Neutral decision-support language ("Suspicious activity pattern", "Staff review recommended") with clamped risk scores (0–100) and automatic Alert/Incident creation when risk score ≥ 60 (`HIGH`) or ≥ 80 (`CRITICAL`).
* **Asynchronous Progress Telemetry**: Video processing runs asynchronously in FastAPI background tasks. Live progress bar % is exposed at `GET /api/videos/{id}/status`.
* **Annotated Video Export**: Saves processed videos with bounding boxes, tracking IDs, zones, and risk level badges to `data/processed/`.
* **Glassmorphism React Dashboard**:
  * Dashboard (`/`): Summary cards, Video status widget, Recent alerts, Watchlist, Live event ticker.
  * Alerts List (`/alerts`): Filterable alerts.
  * Alert Details (`/alerts/:id`): Severity badge, risk gauge, status updater, timeline events, incident summary.
  * Customer Details (`/customers/:id`): Dedicated subject profile, entry/exit timestamps, stay duration, zone, timeline events, alerts, incidents.
  * Analytics (`/analytics`): Recharts multi-period incident trends and risk distribution charts.
  * Videos (`/videos`): Drag-and-drop upload widget, directory table, real-time progress bar, AI process trigger.
  * Settings (`/settings`): Configurable risk thresholds and event scoring deltas.

---

## ⚙️ Environment Configuration

Create or edit `.env` in the root directory:

```env
PORT=8000
HOST=0.0.0.0
DEBUG=True
DATABASE_URL=sqlite:///./retail_sentinel.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173
UPLOAD_DIR=uploads
PROCESSED_VIDEO_DIR=data/processed
MODEL_PATH=data/models

# Local Dataset Configuration (User Configurable)
DATASET_PATH=C:/path/to/your/surveillance-dataset

# AI Service Configuration
BACKEND_URL=http://localhost:8000
YOLO_MODEL=yolov8n.pt
FRAME_SKIP=1
PROCESSING_FPS_LIMIT=15
YOLO_CONFIDENCE=0.35
TRACK_DISAPPEARANCE_SECONDS=5.0
ACTIVE_EVENT_INTERVAL_SECONDS=2.0
SUSPICIOUS_EVENT_COOLDOWN_SECONDS=10.0
```

---

## 🚀 How to Run

### 1. Inspect Local Dataset
```bash
python ai-service/src/dataset/inspect_dataset.py --dataset-path C:/path/to/your/dataset
```

### 2. Start Backend Service & Seed Database
```bash
# Navigate to backend directory
cd backend

# Install Python requirements
pip install -r requirements.txt

# Populate SQLite database with seed data
python -m app.database.seed

# Launch FastAPI server
uvicorn app.main:app --port 8000 --host 0.0.0.0 --reload
```
* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
* Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Start Frontend Dashboard Application
```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite dev server
npm run dev
```
* Dashboard Application: [http://localhost:5173](http://localhost:5173)

### 4. Process Video via CLI (Optional)
```bash
python ai-service/src/main.py process --video-id 1
```

---

## 📋 Test Verification Summary

| Feature | Status | Details |
| :--- | :---: | :--- |
| Dataset Inspection Script | **PASS** | Script inspects dataset, counts videos/images/annotations, saves report |
| Video Upload API & Storage | **PASS** | Uploads `.mp4`/`.avi`/`.mov`/`.mkv`, saves to `uploads/`, creates Video DB record |
| Single-Instance YOLO Detector | **PASS** | `yolov8n.pt` loaded once, filters person class 0 detections |
| ByteTrack Customer Tracker | **PASS** | Assigns stable tracking IDs (`customer_001`, `customer_002`) |
| Customer Entry & Active State | **PASS** | Generates `CUSTOMER_ENTERED`, throttles `CUSTOMER_ACTIVE` every 2s |
| Disappearance Exit Logic | **PASS** | `CUSTOMER_EXITED` triggered after 5s disappearance, calculates stay duration |
| Spatial Zone Manager | **PASS** | Classifies `entrance`, `shopping_area`, `shelf_zone`, `exit` via `zones.json` |
| Risk Engine Calculation | **PASS** | Clamps 0–100, updates customer score, auto-triggers Alerts/Incidents ≥ 60 |
| AI Event Client | **PASS** | Streams events to `POST /api/events`; does NOT directly edit SQLite |
| Asynchronous Video Processing | **PASS** | `POST /api/videos/{id}/process` runs in background, updates progress % |
| Annotated Video Export | **PASS** | Saves output video with overlays to `data/processed/` |
| Real-time Dashboard Updates | **PASS** | WebSocket `/ws/dashboard` pushes updates to React UI without refresh |
| Customer Details View | **PASS** | Route `/customers/:id` displays subject timeline, stay duration, alerts |
| Frontend Production Build | **PASS** | `npm run build` completed with 0 errors |
=======
# retail-sentinel-ai
AI-powered real-time retail monitoring and suspicious behavior detection system
>>>>>>> e8dc869baa1856050060be7035dd764fc63cf828
