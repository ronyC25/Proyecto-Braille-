import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.photometric import CONDITIONS, condition_id
from src.utils.io import read_csv
from src.utils.paths import load_paths


def main():
    parser = argparse.ArgumentParser(description="Genera una rejilla visual de 12 condiciones")
    parser.add_argument("--paths", default=None)
    parser.add_argument("--page-id", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    paths = load_paths(args.paths)
    metadata = read_csv(paths["derived_dir"] / "metadata.csv")
    page_id = args.page_id or metadata[0]["page_id"]
    rows = {row["condition_id"]: row for row in metadata if row["page_id"] == page_id}
    if len(rows) != 12:
        raise ValueError(f"La página {page_id} no tiene 12 condiciones")

    thumb_w, thumb_h = 256, 256
    label_h = 28
    cols, rows_count = 4, 3
    canvas = Image.new(
        "RGB", (cols * thumb_w, rows_count * (thumb_h + label_h)), (255, 255, 255)
    )
    draw = ImageDraw.Draw(canvas)
    for index, (lighting, orientation, support) in enumerate(CONDITIONS):
        condition = condition_id(lighting, orientation, support)
        image = Image.open(rows[condition]["image_path"]).convert("RGB")
        image.thumbnail((thumb_w, thumb_h))
        x = (index % cols) * thumb_w
        y = (index // cols) * (thumb_h + label_h)
        canvas.paste(image, (x, y))
        draw.text((x + 4, y + thumb_h + 4), condition, fill=(0, 0, 0))

    output = Path(args.output) if args.output else paths["reports_dir"] / "figuras" / "condiciones_12.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    print(f"Rejilla guardada: {output}")


if __name__ == "__main__":
    main()
