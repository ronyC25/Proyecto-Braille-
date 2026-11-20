import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.validate import validate
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Valida el corpus derivado 480")
    parser.add_argument("--paths", default=None)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    derived_dir = paths["derived_dir"]
    summary = validate(
        derived_dir / "metadata.csv",
        paths["splits_dir"] / "page_catalog.csv",
        paths["splits_dir"] / "derived_folds.csv",
        paths["reports_dir"] / "validacion_derived_480.json",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["ok"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
