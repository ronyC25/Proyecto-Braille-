import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.convert_yolo import convert
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Convierte el corpus derivado a YOLO")
    parser.add_argument("--paths", default=None)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    convert(paths["derived_dir"] / "metadata.csv", paths["yolo_dir"])


if __name__ == "__main__":
    main()
