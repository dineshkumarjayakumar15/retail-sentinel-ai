import sys
import os

# Configure project paths
project_root = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(project_root, "backend")
ai_src_dir = os.path.join(project_root, "ai-service", "src")

for path in [project_root, backend_dir, ai_src_dir]:
    if path not in sys.path:
        sys.path.insert(0, path)

results = {}

# 1. OpenCV
try:
    import cv2
    results["OpenCV"] = "PASS"
except Exception as e:
    results["OpenCV"] = f"FAIL ({e})"

# 2. YOLO
try:
    from inference.detector import YOLODetector
    results["YOLO"] = "PASS"
except Exception as e:
    results["YOLO"] = f"FAIL ({e})"

# 3. ByteTrack
try:
    from inference.tracker import MultiObjectTracker
    results["ByteTrack"] = "PASS"
except Exception as e:
    results["ByteTrack"] = f"FAIL ({e})"

# 4. Inference Pipeline
try:
    from inference.video_processor import VideoProcessor
    results["Inference Pipeline"] = "PASS"
except Exception as e:
    results["Inference Pipeline"] = f"FAIL ({e})"

# 5. Risk Engine
try:
    from app.services.risk_engine import RiskEngine
    results["Risk Engine"] = "PASS"
except Exception as e:
    results["Risk Engine"] = f"FAIL ({e})"

# 6. Database
try:
    from app.database.connection import engine, SessionLocal
    from app.database.models import Video, Customer, Alert, Event
    db = SessionLocal()
    video_cnt = db.query(Video).count()
    db.close()
    results["Database"] = f"PASS (DB Connected, videos={video_cnt})"
except Exception as e:
    results["Database"] = f"FAIL ({e})"

print("\n================ IMPORT VERIFICATION RESULTS ================")
for comp, status in results.items():
    print(f"{comp}: {status}")
print("=============================================================\n")

if any("FAIL" in v for v in results.values()):
    sys.exit(1)
else:
    sys.exit(0)
