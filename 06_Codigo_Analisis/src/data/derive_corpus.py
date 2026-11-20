import shutil
from pathlib import Path

from PIL import Image

from src.data.photometric import CONDITIONS, apply_condition, condition_id
from src.utils.io import ensure_dir, read_csv, read_json, write_csv


def derive(
    catalog_csv,
    pages_dir,
    output_dir,
    metadata_csv,
    size=1024,
    seed=42,
    limit_pages=None,
    limit_conditions=None,
    overwrite=False,
):
    rows = read_csv(catalog_csv)
    if limit_pages:
        rows = rows[: int(limit_pages)]
    conditions = CONDITIONS[: int(limit_conditions)] if limit_conditions else CONDITIONS

    output_dir = Path(output_dir)
    images_dir = output_dir / "images"
    labels_dir = output_dir / "labels"
    labels_px_dir = output_dir / "labels_px"
    if overwrite:
        for directory in (images_dir, labels_dir, labels_px_dir):
            if directory.exists():
                shutil.rmtree(directory)
    ensure_dir(images_dir)
    ensure_dir(labels_dir)
    ensure_dir(labels_px_dir)

    metadata = []
    for page_index, row in enumerate(rows):
        page_id = row["page_id"]
        page_data = read_json(Path(pages_dir) / f"{page_id}.json")
        image = Image.open(page_data["image_path"]).convert("RGB")
        boxes = [
            (box["x1"], box["y1"], box["x2"], box["y2"], box["class_id"])
            for box in page_data["boxes"]
        ]
        for condition_index, (lighting, orientation, support) in enumerate(conditions):
            condition = condition_id(lighting, orientation, support)
            seed_value = seed + page_index * 100 + condition_index
            transformed, transformed_boxes, params = apply_condition(
                image,
                boxes,
                lighting=lighting,
                orientation=orientation,
                support=support,
                size=size,
                seed=seed_value,
            )
            stem = f"{page_id}__{condition}"
            image_path = images_dir / f"{stem}.jpg"
            label_path = labels_dir / f"{stem}.txt"
            label_px_path = labels_px_dir / f"{stem}.txt"
            Image.fromarray(transformed).save(image_path, quality=95)

            with open(label_path, "w", encoding="utf-8") as handle:
                for x1, y1, x2, y2, class_id in transformed_boxes:
                    x_center = (x1 + x2) / 2.0 / size
                    y_center = (y1 + y2) / 2.0 / size
                    width = (x2 - x1) / size
                    height = (y2 - y1) / size
                    handle.write(
                        f"{class_id} {x_center:.6f} {y_center:.6f} "
                        f"{width:.6f} {height:.6f}\n"
                    )

            with open(label_px_path, "w", encoding="utf-8") as handle:
                for x1, y1, x2, y2, class_id in transformed_boxes:
                    handle.write(
                        f"{class_id} {x1:.2f} {y1:.2f} {x2:.2f} {y2:.2f}\n"
                    )

            metadata.append(
                {
                    "image_path": str(image_path),
                    "label_path": str(label_path),
                    "label_px_path": str(label_px_path),
                    "page_id": page_id,
                    "source": row["source"],
                    "subset": row["subset"],
                    "source_page": row["image_path"],
                    "condition_id": condition,
                    "lighting": lighting,
                    "orientation": orientation,
                    "support": support,
                    "fold": row["fold"],
                    "group": row["group"],
                    "n_boxes": len(transformed_boxes),
                    "seed": seed_value,
                }
            )
        if (page_index + 1) % 5 == 0:
            print(f"  páginas procesadas: {page_index + 1}/{len(rows)}")

    write_csv(metadata_csv, metadata)
    return metadata
