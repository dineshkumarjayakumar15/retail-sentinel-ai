import sys
import os
import cv2
from pathlib import Path

# Programmatically resolve PROJECT_ROOT relative to this file
PROJECT_ROOT = Path(__file__).resolve().parent

stored_db_path = "uploads/retail_main_entrance_01.mp4"

# Path resolution logic
if Path(stored_db_path).is_absolute():
    resolved_path = Path(stored_db_path)
else:
    resolved_path = (PROJECT_ROOT / stored_db_path).resolve()

print(f"Project Root: {PROJECT_ROOT}")
print(f"Original Database Path: {stored_db_path}")
print(f"Resolved Path: {resolved_path}")

file_exists = resolved_path.exists() and resolved_path.is_file()
print(f"File Exists: {'PASS' if file_exists else 'FAIL'}")

if file_exists:
    cap = cv2.VideoCapture(str(resolved_path))
    can_open = cap.isOpened()
    if can_open:
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"OpenCV Can Open Video: PASS ({width}x{height} @ {fps:.1f} FPS, total_frames={total_frames})")
        ret, frame = cap.read()
        print(f"Read Frame 1: {'PASS' if ret else 'FAIL'}")
    else:
        print("OpenCV Can Open Video: FAIL")
    cap.release()
else:
    print("OpenCV Can Open Video: FAIL")
