from pathlib import Path
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_paths(config_path=None):
    """Load dataset/output paths from configs/paths.yaml (fallback: paths.example.yaml)."""
    config_path = Path(config_path) if config_path else CONFIG_DIR / "paths.yaml"
    if not config_path.exists():
        config_path = CONFIG_DIR / "paths.example.yaml"

    with open(config_path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    def resolve(key, default):
        value = raw.get(key, default)
        path = Path(value)
        return path if path.is_absolute() else (PROJECT_ROOT / path).resolve()

    return {
        "project_root": PROJECT_ROOT,
        "dataset_root": resolve("dataset_root", "../../Semana 7/dataset"),
        "angelina_root": resolve(
            "angelina_root",
            "../../Semana 7/dataset/data 1/AngelinaDataset",
        ),
        "dsbi_root": resolve(
            "dsbi_root",
            "../../Semana 7/dataset/data 2/DSBI",
        ),
        "derived_dir": resolve("derived_dir", "data/processed/derived_480"),
        "yolo_dir": resolve("yolo_dir", "data/processed/yolo_derived"),
        "splits_dir": resolve("splits_dir", "data/splits"),
        "interim_dir": resolve("interim_dir", "data/interim"),
        "outputs_dir": resolve("outputs_dir", "outputs"),
        "reports_dir": resolve("reports_dir", "reports"),
    }
