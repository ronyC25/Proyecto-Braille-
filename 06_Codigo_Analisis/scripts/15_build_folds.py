import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.build_folds import build_folds
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Genera los folds 24/4/7 + externos")
    parser.add_argument("--paths", default=None)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    build_folds(
        paths["splits_dir"] / "page_catalog.csv",
        paths["derived_dir"] / "metadata.csv",
        paths["splits_dir"],
        paths["yolo_dir"],
    )


if __name__ == "__main__":
    main()
