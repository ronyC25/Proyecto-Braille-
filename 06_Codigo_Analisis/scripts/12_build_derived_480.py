import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.derive_corpus import derive
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Genera el corpus derivado 40 x 12")
    parser.add_argument("--paths", default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit-pages", type=int, default=None, help="Solo para pruebas")
    parser.add_argument("--limit-conditions", type=int, default=None, help="Solo para pruebas")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    paths = load_paths(args.paths)
    catalog_csv = paths["splits_dir"] / "page_catalog.csv"
    pages_dir = paths["interim_dir"] / "pages"
    derived_dir = paths["derived_dir"]
    metadata_csv = derived_dir / "metadata.csv"
    rows = derive(
        catalog_csv,
        pages_dir,
        derived_dir,
        metadata_csv,
        seed=args.seed,
        limit_pages=args.limit_pages,
        limit_conditions=args.limit_conditions,
        overwrite=args.overwrite,
    )
    print(f"Imágenes generadas: {len(rows)}")
    print(f"Metadata: {metadata_csv}")


if __name__ == "__main__":
    main()
