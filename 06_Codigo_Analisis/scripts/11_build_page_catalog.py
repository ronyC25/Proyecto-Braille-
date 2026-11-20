import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.page_catalog import build_catalog
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Selecciona las 40 páginas del corpus")
    parser.add_argument("--paths", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--books", type=int, default=20)
    parser.add_argument("--uploaded", type=int, default=5)
    parser.add_argument("--dsbi", type=int, default=10)
    parser.add_argument("--handwritten", type=int, default=5)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    catalog_csv = paths["splits_dir"] / "page_catalog.csv"
    pages_dir = paths["interim_dir"] / "pages"
    summary_json = paths["reports_dir"] / "page_catalog_summary.json"
    summary = build_catalog(
        paths["angelina_root"],
        paths["dsbi_root"],
        catalog_csv,
        pages_dir,
        summary_json,
        seed=args.seed,
        n_books=args.books,
        n_uploaded=args.uploaded,
        n_dsbi=args.dsbi,
        n_handwritten=args.handwritten,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nCatálogo: {catalog_csv}")
    print(f"Resumen: {summary_json}")


if __name__ == "__main__":
    main()
