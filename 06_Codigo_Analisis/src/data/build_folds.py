from collections import defaultdict
from pathlib import Path

import yaml

from src.data.class_mapping import CLASS_NAMES
from src.utils.io import ensure_dir, read_csv, write_csv


def build_folds(catalog_csv, metadata_csv, splits_dir, yolo_dir):
    catalog = read_csv(catalog_csv)
    metadata = read_csv(metadata_csv)
    splits_dir = Path(splits_dir)
    yolo_dir = Path(yolo_dir)
    ensure_dir(splits_dir)

    page_to_images = defaultdict(list)
    for row in metadata:
        page_to_images[row["page_id"]].append(row["image_path"])

    controlled = [row for row in catalog if row["group"] == "controlled"]
    external = [row for row in catalog if row["group"] == "spontaneous"]

    folds = {index: [row for row in controlled if int(row["fold"]) == index] for index in range(5)}
    for index, pages in folds.items():
        if len(pages) != 7:
            raise ValueError(f"El fold {index} tiene {len(pages)} páginas, se esperaban 7")

    fold_rows = []
    for experiment in range(5):
        test_pages = folds[experiment]
        val_pool = folds[(experiment + 1) % 5]
        val_pages = val_pool[:4]
        test_ids = {page["page_id"] for page in test_pages}
        val_ids = {page["page_id"] for page in val_pages}
        train_pages = [
            page
            for page in controlled
            if page["page_id"] not in test_ids and page["page_id"] not in val_ids
        ]
        if len(train_pages) != 24:
            raise ValueError(
                f"El fold {experiment} tiene {len(train_pages)} páginas de train, "
                "se esperaban 24"
            )

        split_pages = {
            "train": train_pages,
            "val": val_pages,
            "test": test_pages,
            "external": external,
        }
        fold_dir = ensure_dir(splits_dir / f"fold_{experiment}")
        for split, pages in split_pages.items():
            lines = []
            for page in pages:
                lines.extend(page_to_images[page["page_id"]])
            with open(fold_dir / f"{split}.txt", "w", encoding="utf-8") as handle:
                for line in lines:
                    handle.write(line + "\n")
            for page in pages:
                fold_rows.append(
                    {
                        "page_id": page["page_id"],
                        "experiment_fold": experiment,
                        "split": split,
                    }
                )

        data_yaml = {
            "path": str(yolo_dir.resolve()),
            "train": str((fold_dir / "train.txt").resolve()),
            "val": str((fold_dir / "val.txt").resolve()),
            "test": str((fold_dir / "test.txt").resolve()),
            "names": {index: name for index, name in enumerate(CLASS_NAMES)},
        }
        yaml_dir = ensure_dir(yolo_dir / "folds" / f"fold_{experiment}")
        with open(yaml_dir / "data.yaml", "w", encoding="utf-8") as handle:
            yaml.safe_dump(data_yaml, handle, allow_unicode=True, sort_keys=False)

    write_csv(
        splits_dir / "derived_folds.csv",
        fold_rows,
        fieldnames=["page_id", "experiment_fold", "split"],
    )
    print(f"Folds generados en: {splits_dir}")
    return fold_rows
