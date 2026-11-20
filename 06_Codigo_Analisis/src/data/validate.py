import json
from collections import Counter, defaultdict
from pathlib import Path

from PIL import Image

from src.utils.io import read_csv, write_json


def validate(metadata_csv, catalog_csv, folds_csv=None, report_json=None, expected_images=480):
    rows = read_csv(metadata_csv)
    catalog = read_csv(catalog_csv)
    errors = []

    if len(rows) != expected_images:
        errors.append(f"Se esperaban {expected_images} imágenes, hay {len(rows)}")

    page_ids = {row["page_id"] for row in rows}
    if len(page_ids) != 40:
        errors.append(f"Se esperaban 40 páginas, hay {len(page_ids)}")

    conditions_per_page = defaultdict(set)
    classes = set()
    invalid_labels = 0
    invalid_images = 0
    for row in rows:
        conditions_per_page[row["page_id"]].add(row["condition_id"])
        label_path = Path(row["label_path"])
        if not label_path.exists():
            errors.append(f"Falta etiqueta: {label_path}")
            continue
        with open(label_path, "r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.split()
                if len(parts) != 5:
                    invalid_labels += 1
                    continue
                class_id = int(parts[0])
                values = [float(value) for value in parts[1:]]
                classes.add(class_id)
                if class_id < 0 or class_id > 62:
                    invalid_labels += 1
                if any(value < 0 or value > 1 for value in values):
                    invalid_labels += 1
        image_path = Path(row["image_path"])
        if not image_path.exists():
            errors.append(f"Falta imagen: {image_path}")
            continue
        try:
            with Image.open(image_path) as image:
                if image.size != (1024, 1024):
                    invalid_images += 1
        except Exception:
            invalid_images += 1

    bad_conditions = {
        page_id: len(conditions)
        for page_id, conditions in conditions_per_page.items()
        if len(conditions) != 12
    }
    if bad_conditions:
        errors.append(f"Páginas sin 12 condiciones: {bad_conditions}")

    if len(classes) != 63:
        errors.append(f"Se esperaban 63 clases, hay {len(classes)}")

    if invalid_labels:
        errors.append(f"Etiquetas inválidas: {invalid_labels}")
    if invalid_images:
        errors.append(f"Imágenes con tamaño distinto de 1024x1024: {invalid_images}")

    fold_summary = {}
    if folds_csv and Path(folds_csv).exists():
        fold_rows = read_csv(folds_csv)
        by_fold = defaultdict(lambda: defaultdict(set))
        for row in fold_rows:
            by_fold[row["experiment_fold"]][row["split"]].add(row["page_id"])
        for fold, splits in sorted(by_fold.items()):
            counts = {split: len(pages) for split, pages in splits.items()}
            fold_summary[fold] = counts
            if counts.get("train") != 24 or counts.get("val") != 4:
                errors.append(f"Fold {fold} con conteos inesperados: {counts}")
            if counts.get("test") != 7:
                errors.append(f"Fold {fold} sin 7 páginas de test: {counts}")
            if counts.get("external") != 5:
                errors.append(f"Fold {fold} sin 5 páginas externas: {counts}")
            all_pages = set().union(*splits.values())
            if len(all_pages) != sum(len(pages) for pages in splits.values()):
                errors.append(f"Fold {fold} con páginas repetidas entre splits")

    summary = {
        "images": len(rows),
        "pages": len(page_ids),
        "classes": sorted(classes),
        "n_classes": len(classes),
        "conditions_per_page": {page: len(conds) for page, conds in conditions_per_page.items()},
        "invalid_labels": invalid_labels,
        "invalid_images": invalid_images,
        "folds": fold_summary,
        "errors": errors,
        "ok": not errors,
    }
    if report_json:
        write_json(report_json, summary)
    return summary
