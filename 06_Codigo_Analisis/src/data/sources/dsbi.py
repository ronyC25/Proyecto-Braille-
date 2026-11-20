from dataclasses import dataclass
from pathlib import Path
from typing import List

from PIL import Image

from src.data.class_mapping import dots_to_int
from src.data.sources.angelina import Box, Page
from src.utils.io import sanitize_id


def _parse_annotation(txt_path):
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if len(lines) < 3:
        return None
    try:
        angle = float(lines[0])
        verts = [float(value) for value in lines[1].split()]
        horizs = [float(value) for value in lines[2].split()]
    except ValueError:
        return None

    cells = []
    for line in lines[3:]:
        parts = line.split()
        if len(parts) < 8:
            return None
        try:
            row = int(parts[0]) - 1
            col = int(parts[1]) - 1
            dots = [int(value) for value in parts[2:8]]
        except ValueError:
            return None
        int_label = dots_to_int(dots)
        if int_label == 0:
            continue
        if col * 2 + 1 >= len(verts) or row * 3 + 2 >= len(horizs):
            continue
        x1 = verts[col * 2]
        x2 = verts[col * 2 + 1]
        y1 = horizs[row * 3]
        y2 = horizs[row * 3 + 2]
        cells.append((x1, y1, x2, y2, int_label - 1))
    return {"angle": angle, "verts": verts, "horizs": horizs, "cells": cells}


def load_page(image_path):
    image_path = Path(image_path)
    txt_path = image_path.with_suffix(".txt")
    annotation = _parse_annotation(txt_path) if txt_path.exists() else None
    if annotation is None:
        raise ValueError(f"Anotación DSBI inválida o vacía: {txt_path}")
    with Image.open(image_path) as image:
        width, height = image.size
    boxes = [
        Box(x1=x1, y1=y1, x2=x2, y2=y2, class_id=class_id)
        for x1, y1, x2, y2, class_id in annotation["cells"]
    ]
    page_id = f"dsbi_recto_{sanitize_id(image_path.stem)}"
    return Page(
        page_id=page_id,
        source="dsbi",
        subset="recto",
        image_path=str(image_path),
        width=width,
        height=height,
        boxes=boxes,
    )


def iter_pages(dsbi_root, include_empty=False):
    dsbi_root = Path(dsbi_root)
    for image_path in sorted(dsbi_root.rglob("*+recto.jpg")):
        if "figures" in image_path.parts:
            continue
        try:
            page = load_page(image_path)
        except ValueError:
            continue
        if not page.boxes and not include_empty:
            continue
        yield page


def audit(dsbi_root):
    result = {
        "source": "dsbi",
        "root": str(dsbi_root),
        "images": 0,
        "annotated": 0,
        "empty": 0,
        "invalid": 0,
        "boxes": 0,
        "classes": set(),
    }
    for image_path in sorted(Path(dsbi_root).rglob("*+recto.jpg")):
        if "figures" in image_path.parts:
            continue
        result["images"] += 1
        try:
            page = load_page(image_path)
        except ValueError:
            result["invalid"] += 1
            continue
        if not page.boxes:
            result["empty"] += 1
        else:
            result["annotated"] += 1
        result["boxes"] += len(page.boxes)
        for box in page.boxes:
            result["classes"].add(box.class_id + 1)
    result["classes"] = sorted(result["classes"])
    return result
