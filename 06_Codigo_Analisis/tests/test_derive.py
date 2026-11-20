from pathlib import Path

import pytest

from src.utils.io import read_csv


METADATA = Path("data/processed/derived_480/metadata.csv")


@pytest.mark.skipif(not METADATA.exists(), reason="Aún no se generó el corpus")
def test_derived_counts():
    rows = read_csv(METADATA)
    assert len(rows) == 480
    pages = {row["page_id"] for row in rows}
    assert len(pages) == 40
    conditions = {}
    for row in rows:
        conditions.setdefault(row["page_id"], set()).add(row["condition_id"])
    assert all(len(values) == 12 for values in conditions.values())
