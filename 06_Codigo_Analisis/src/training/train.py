import argparse
from pathlib import Path

import yaml

from src.config import resolve_from_project


def train(config_path):
    with open(config_path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    from ultralytics import YOLO

    model = YOLO(config["model"])
    data = resolve_from_project(config["data"])
    project = resolve_from_project(config.get("project", "outputs/runs"))
    model.train(
        data=str(data),
        epochs=int(config.get("epochs", 100)),
        imgsz=int(config.get("imgsz", 640)),
        batch=int(config.get("batch", 16)),
        seed=int(config.get("seed", 42)),
        project=str(project),
        name=config.get("name", "run"),
        exist_ok=True,
    )
    print(f"Entrenamiento finalizado: {project / config.get('name', 'run')}")


def main():
    parser = argparse.ArgumentParser(description="Entrena un modelo YOLO")
    parser.add_argument("--config", required=True, help="Ruta a configs/*.yaml")
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()
