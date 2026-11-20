from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

from PIL import Image

from src.utils.io import sanitize_id


@dataclass
class Box:
    x1: float
    y1: float
    x2: float
    y2: float
    class_id: int


@dataclass
class Page:
    page_id: str
    source: str
    subset: str
    image_path: str
    width: int
    height: int
    boxes: List[Box]

    def to_dict(self):
        data = asdict(self)
        data["boxes"] = [asdict(box) for box in self.boxes]
        return data


def _parse_csv(csv_path, width, height):
    boxes = []
    with open(csv_path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            parts = line.split(";")
            if len(parts) != 5:
                continue
            left, top, right, bottom, label = parts
            label = int(label)
            if not 1 <= label <= 63:
                continue
            boxes.append(
                Box(
                    x1=float(left) * width,
                    y1=float(top) * height,
                    x2=float(right) * width,
                    y2=float(bottom) * height,
                    class_id=label - 1,
                )
            )
    return boxes


def load_page(image_path, subset="books"):
    image_path = Path(image_path)
    csv_path = image_path.with_suffix(".csv")
    if not csv_path.exists():
        raise FileNotFoundError(f"No existe la anotación CSV: {csv_path}")
    with Image.open(image_path) as image:
        width, height = image.size
    boxes = _parse_csv(csv_path, width, height)
    page_id = f"angelina_{sanitize_id(subset)}_{sanitize_id(image_path.stem)}"
    return Page(
        page_id=page_id,
        source="angelina",
        subset=subset,
        image_path=str(image_path),
        width=width,
        height=height,
        boxes=boxes,
    )


def iter_pages(angelina_root, subsets=("books", "uploaded", "handwritten"), include_empty=False):
    angelina_root = Path(angelina_root)
    for subset in subsets:
        subset_dir = angelina_root / subset
        if not subset_dir.exists():
            continue
        for image_path in sorted(subset_dir.rglob("*.jpg")):
            if "pics" in image_path.parts:
                continue
            try:
                page = load_page(image_path, subset=subset)
            except (FileNotFoundError, ValueError):
                continue
            if not page.boxes and not include_empty:
                continue
            yield page


def audit(angelina_root):
    result = {
        "source": "angelina",
        "root": str(angelina_root),
        "subsets": {},
        "images": 0,
        "boxes": 0,
        "classes": set(),
        "empty": 0,
    }
    for subset in ("books", "handwritten", "not_braille", "uploaded"):
        subset_dir = Path(angelina_root) / subset
        if not subset_dir.exists():
            continue
        images = sorted(subset_dir.rglob("*.jpg"))
        subset_info = {"images": len(images), "boxes": 0, "empty": 0}
        for image_path in images:
            if "pics" in image_path.parts:
                continue
            try:
                page = load_page(image_path, subset=subset)
            except (FileNotFoundError, ValueError):
                continue
            if not page.boxes:
                subset_info["empty"] += 1
            subset_info["boxes"] += len(page.boxes)
            for box in page.boxes:
                result["classes"].add(box.class_id + 1)
        result["subsets"][subset] = subset_info
        result["images"] += subset_info["images"]
        result["boxes"] += subset_info["boxes"]
        result["empty"] += subset_info["empty"]
    result["classes"] = sorted(result["classes"])
    return result
