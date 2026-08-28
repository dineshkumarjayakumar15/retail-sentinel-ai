import argparse
import sys
import os

src_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(src_dir, "..", ".."))
backend_dir = os.path.join(project_root, "backend")

if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from dataset.inspect_dataset import inspect_dataset
from config import ai_settings
from utils.logger import ai_logger

def main():
    parser = argparse.ArgumentParser(description="Retail Sentinel AI Service CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect local surveillance dataset")
    inspect_parser.add_argument("--dataset-path", type=str, default="", help="Path to local dataset")

    process_parser = subparsers.add_parser("process", help="Process video with OpenCV + YOLO + ByteTrack")
    process_parser.add_argument("--video-id", type=int, required=True, help="Video ID in SQLite DB")

    args = parser.parse_args()

    if args.command == "inspect":
        inspect_dataset(args.dataset_path)
    elif args.command == "process":
        from app.database.connection import SessionLocal
        from inference.video_processor import VideoProcessor
        
        db = SessionLocal()
        try:
            processor = VideoProcessor(db=db, video_id=args.video_id)
            processor.process_video()
        finally:
            db.close()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
