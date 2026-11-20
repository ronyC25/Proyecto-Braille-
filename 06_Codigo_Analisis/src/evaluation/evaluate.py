import argparse
import json
from pathlib import Path

from src.config import resolve_from_project


def evaluate(weights, data, imgsz=640, split="val", output=None):
    from ultralytics import YOLO

    model = YOLO(weights)
    results = model.val(data=str(resolve_from_project(data)), imgsz=imgsz, split=split)
    metrics = {}
    for key in ("map", "map50", "map75", "mp", "mr"):
        value = getattr(results.box, key, None)
        if value is not None:
            metrics[key] = float(value)
    if output:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, "w", encoding="utf-8") as handle:
            json.dump(metrics, handle, ensure_ascii=False, indent=2)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evalúa un modelo YOLO")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--split", default="val", choices=["train", "val", "test"])
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    evaluate(args.weights, args.data, args.imgsz, args.split, args.output)


if __name__ == "__main__":
    main()
