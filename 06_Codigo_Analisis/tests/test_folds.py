from pathlib import Path

import pytest

from src.utils.io import read_csv


FOLDS = Path("data/splits/derived_folds.csv")


@pytest.mark.skipif(not FOLDS.exists(), reason="Aún no se generaron los folds")
def test_fold_counts():
    rows = read_csv(FOLDS)
    by_fold = {}
    for row in rows:
        by_fold.setdefault(row["experiment_fold"], {}).setdefault(row["split"], set()).add(
            row["page_id"]
        )
    assert len(by_fold) == 5
    for fold, splits in by_fold.items():
        assert len(splits["train"]) == 24
        assert len(splits["val"]) == 4
        assert len(splits["test"]) == 7
        assert len(splits["external"]) == 5
        all_pages = set().union(*splits.values())
        assert len(all_pages) == sum(len(pages) for pages in splits.values())
