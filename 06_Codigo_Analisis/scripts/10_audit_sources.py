import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.audit import audit
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Audita Angelina y DSBI")
    parser.add_argument("--paths", default=None, help="Ruta a configs/paths.yaml")
    args = parser.parse_args()

    paths = load_paths(args.paths)
    report = paths["reports_dir"] / "auditoria_fuentes.json"
    result = audit(paths["angelina_root"], paths["dsbi_root"], report)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\nReporte: {report}")


if __name__ == "__main__":
    main()
