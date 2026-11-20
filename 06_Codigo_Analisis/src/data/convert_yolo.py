import os
import shutil
from pathlib import Path

import yaml

from src.data.class_mapping import CLASS_NAMES
from src.utils.io import ensure_dir, read_csv


def _link_or_copy(source, destination):
    source = Path(source)
    destination = Path(destination)
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def convert(metadata_csv, yolo_dir):
    rows = read_csv(metadata_csv)
    yolo_dir = Path(yolo_dir)
    images_dir = ensure_dir(yolo_dir / "images" / "all")
    labels_dir = ensure_dir(yolo_dir / "labels" / "all")

    for row in rows:
        image_path = Path(row["image_path"])
        label_path = Path(row["label_path"])
        _link_or_copy(image_path, images_dir / image_path.name)
        _link_or_copy(label_path, labels_dir / label_path.name)

    data_yaml = {
        "path": str(yolo_dir.resolve()),
        "train": "images/all",
        "val": "images/all",
        "names": {index: name for index, name in enumerate(CLASS_NAMES)},
    }
    with open(yolo_dir / "data.yaml", "w", encoding="utf-8") as handle:
        yaml.safe_dump(data_yaml, handle, allow_unicode=True, sort_keys=False)

    print(f"YOLO generado en: {yolo_dir}")
    print(f"  imágenes: {len(rows)}")
    return data_yaml
