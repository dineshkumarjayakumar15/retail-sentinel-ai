"""
Retail Sentinel AI - Dataset Inspection Tool
Inspects local dataset structure, annotations, video/image file counts, and classes,
and recommends Strategy A (Object Detection), Strategy B (Behavior Classification),
or Strategy C (Temporal Anomaly Detection).
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List

# Add ai-service/src directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import ai_settings
from utils.logger import ai_logger

VIDEO_EXTS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
ANNOTATION_EXTS = {'.txt', '.xml', '.json', '.csv', '.yaml'}

def inspect_dataset(dataset_path: str = None) -> Dict[str, Any]:
    if not dataset_path:
        dataset_path = ai_settings.DATASET_PATH

    if not dataset_path or not os.path.exists(dataset_path):
        ai_logger.warning(f"Dataset path '{dataset_path}' does not exist or is not configured.")
        report = {
            "status": "UNCONFIGURED",
            "dataset_root_path": dataset_path,
            "message": f"Dataset path '{dataset_path}' not found. User can enter DATASET_PATH in .env file.",
            "recommended_strategy": "Strategy A — Object Detection (Using Pretrained YOLO Weights)"
        }
        print_report(report)
        return report

    ai_logger.info(f"Starting inspection of dataset at: {dataset_path}")

    folder_count = 0
    video_count = 0
    image_count = 0
    annotation_count = 0
    extensions_found = set()
    categories_found = set()

    has_yolo_bboxes = False
    has_classification_folders = False
    has_temporal_labels = False

    for root, dirs, files in os.walk(dataset_path):
        folder_count += len(dirs)
        dir_name = os.path.basename(root).lower()

        if dir_name in ['normal', 'shoplifting', 'suspicious', 'theft', 'robbery', 'fight', 'anomaly']:
            has_classification_folders = True
            categories_found.add(dir_name)

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            extensions_found.add(ext)

            if ext in VIDEO_EXTS:
                video_count += 1
            elif ext in IMAGE_EXTS:
                image_count += 1
            elif ext in ANNOTATION_EXTS:
                annotation_count += 1
                if ext == '.txt' and file != 'classes.txt':
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            if lines and len(lines[0].split()) == 5:
                                has_yolo_bboxes = True
                    except Exception:
                        pass

    if has_yolo_bboxes:
        selected_strategy = "Strategy A — Object Detection (YOLO Bounding Box Annotations Found)"
        strategy_code = "STRATEGY_A"
    elif has_classification_folders or (video_count > 0 and annotation_count == 0):
        selected_strategy = "Strategy B — Behavior Classification (Category / Clip Folders Found)"
        strategy_code = "STRATEGY_B"
    elif has_temporal_labels:
        selected_strategy = "Strategy C — Temporal Anomaly Detection"
        strategy_code = "STRATEGY_C"
    else:
        selected_strategy = "Strategy A — Object Detection (Using Pretrained YOLO Weights)"
        strategy_code = "STRATEGY_A_PRETRAINED"

    report = {
        "status": "SUCCESS",
        "dataset_root_path": dataset_path,
        "folder_count": folder_count,
        "video_count": video_count,
        "image_count": image_count,
        "annotation_count": annotation_count,
        "extensions_found": sorted(list(extensions_found)),
        "categories_found": sorted(list(categories_found)),
        "has_yolo_bboxes": has_yolo_bboxes,
        "has_classification_folders": has_classification_folders,
        "has_temporal_labels": has_temporal_labels,
        "recommended_strategy": selected_strategy,
        "strategy_code": strategy_code
    }

    report_file = os.path.join("data", "dataset_inspection_report.json")
    try:
        os.makedirs("data", exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        ai_logger.info(f"Inspection report saved to {report_file}")
    except Exception as e:
        ai_logger.warning(f"Could not save inspection report file: {e}")

    print_report(report)
    return report

def print_report(report: Dict[str, Any]):
    print("\n" + "="*75)
    print("           RETAIL SENTINEL AI — DATASET INSPECTION REPORT           ")
    print("="*75)
    print(f"Dataset Root Path:        {report.get('dataset_root_path', 'Not Configured')}")
    print(f"Status:                   {report.get('status')}")
    print(f"Folders Discovered:       {report.get('folder_count', 0)}")
    print(f"Videos Found:             {report.get('video_count', 0)}")
    print(f"Images Found:             {report.get('image_count', 0)}")
    print(f"Annotation Files:         {report.get('annotation_count', 0)}")
    print(f"File Extensions:          {', '.join(report.get('extensions_found', []))}")
    print(f"Discovered Categories:    {', '.join(report.get('categories_found', [])) if report.get('categories_found') else 'Pretrained Customer/Person'}")
    print("-" * 75)
    print(f"RECOMMENDED STRATEGY:     {report.get('recommended_strategy')}")
    print("="*75 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect local surveillance dataset")
    parser.add_argument("--dataset-path", type=str, default="", help="Path to dataset directory")
    args = parser.parse_args()

    inspect_dataset(args.dataset_path)
