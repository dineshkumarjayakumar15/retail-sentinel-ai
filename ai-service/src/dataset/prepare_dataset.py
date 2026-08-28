"""
Retail Sentinel AI - Dataset Preparation Utility
Formats dataset directories and creates dataset.yaml for YOLO training.
"""

import os
import yaml
from ai_service.src.config import ai_settings
from ai_service.src.utils.logger import ai_logger

def prepare_yolo_yaml(dataset_dir: str, classes: list = None) -> str:
    if not classes:
        classes = ["person", "basket", "product"]

    yaml_data = {
        "path": os.path.abspath(dataset_dir),
        "train": "images/train",
        "val": "images/val",
        "names": {i: name for i, name in enumerate(classes)}
    }

    yaml_path = os.path.join(dataset_dir, "dataset.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_data, f)

    ai_logger.info(f"Generated YOLO dataset.yaml at {yaml_path}")
    return yaml_path
