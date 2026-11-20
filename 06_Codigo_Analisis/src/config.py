from pathlib import Path

import yaml

from src.utils.paths import CONFIG_DIR


def load_yaml(path):
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_dataset_config(name):
    return load_yaml(CONFIG_DIR / "datasets" / f"{name}.yaml")


def load_train_config(name):
    return load_yaml(CONFIG_DIR / f"{name}.yaml")


def resolve_from_project(value):
    path = Path(value)
    return path if path.is_absolute() else (CONFIG_DIR.parent / path).resolve()
