import random
from pathlib import Path

from src.data.sources import angelina, dsbi
from src.utils.io import ensure_dir, write_csv, write_json


def _class_set(page):
    return {box.class_id + 1 for box in page.boxes}


def _greedy(pages, count, covered, rng):
    selected = []
    remaining = list(pages)
    while len(selected) < count and remaining:
        best = max(remaining, key=lambda page: len(_class_set(page) - covered))
        new_classes = _class_set(best) - covered
        if not new_classes:
            break
        selected.append(best)
        remaining.remove(best)
        covered |= new_classes
    if len(selected) < count:
        rng.shuffle(remaining)
        selected.extend(remaining[: count - len(selected)])
    return selected, covered


def _repair_coverage(selected, pools, missing, rng):
    """Try to swap pages so that every missing class is represented."""
    selected_ids = {page.page_id for page in selected}
    for class_label in sorted(missing):
        candidates = []
        for subset, pages in pools.items():
            for page in pages:
                if page.page_id in selected_ids:
                    continue
                if class_label in _class_set(page):
                    candidates.append((subset, page))
        if not candidates:
            continue
        subset, candidate = candidates[0]
        # Replace a selected page from the same subset with no unique class.
        subset_selected = [page for page in selected if page.subset == subset]
        replacement = None
        for page in subset_selected:
            others = [p for p in selected if p.page_id != page.page_id]
            covered = set().union(*[_class_set(p) for p in others]) if others else set()
            if not (_class_set(page) - covered):
                replacement = page
                break
        if replacement is None and subset_selected:
            replacement = rng.choice(subset_selected)
        if replacement is not None:
            selected.remove(replacement)
            selected.append(candidate)
            selected_ids.remove(replacement.page_id)
            selected_ids.add(candidate.page_id)
    return selected


def build_catalog(
    angelina_root,
    dsbi_root,
    output_csv,
    pages_dir,
    summary_json,
    seed=42,
    n_books=20,
    n_uploaded=5,
    n_dsbi=10,
    n_handwritten=5,
):
    rng = random.Random(seed)

    books = list(angelina.iter_pages(angelina_root, subsets=("books",)))
    uploaded = list(angelina.iter_pages(angelina_root, subsets=("uploaded",)))
    handwritten = list(angelina.iter_pages(angelina_root, subsets=("handwritten",)))
    dsbi_pages = list(dsbi.iter_pages(dsbi_root))

    if len(books) < n_books:
        raise ValueError(f"Angelina books insuficientes: {len(books)} < {n_books}")
    if len(uploaded) < n_uploaded:
        raise ValueError(f"Angelina uploaded insuficientes: {len(uploaded)} < {n_uploaded}")
    if len(handwritten) < n_handwritten:
        raise ValueError(
            f"Angelina handwritten insuficientes: {len(handwritten)} < {n_handwritten}"
        )
    if len(dsbi_pages) < n_dsbi:
        raise ValueError(f"DSBI recto insuficientes: {len(dsbi_pages)} < {n_dsbi}")

    covered = set()
    dsbi_with_41 = [page for page in dsbi_pages if 41 in _class_set(page)]
    if not dsbi_with_41:
        raise ValueError("Ninguna página DSBI contiene la clase 41")
    dsbi_with_41.sort(key=lambda page: (-len(_class_set(page)), page.page_id))
    selected_dsbi = [dsbi_with_41[0]]
    covered |= _class_set(dsbi_with_41[0])
    dsbi_pool = [page for page in dsbi_pages if page.page_id != dsbi_with_41[0].page_id]
    selected_dsbi, covered = _greedy(dsbi_pool, n_dsbi - 1, covered, rng)
    selected_dsbi = [dsbi_with_41[0]] + selected_dsbi

    selected_books, covered = _greedy(books, n_books, covered, rng)
    selected_uploaded = rng.sample(uploaded, n_uploaded)
    selected_handwritten = rng.sample(handwritten, n_handwritten)

    selected = selected_books + selected_uploaded + selected_dsbi + selected_handwritten
    all_classes = set(range(1, 64))
    missing = all_classes - covered
    if missing:
        pools = {
            "books": books,
            "uploaded": uploaded,
            "dsbi": dsbi_pages,
            "handwritten": handwritten,
        }
        selected = _repair_coverage(selected, pools, missing, rng)
        covered = set().union(*[_class_set(page) for page in selected])

    missing = sorted(all_classes - covered)
    if missing:
        raise ValueError(f"No se cubren las clases: {missing}")

    controlled = [
        page
        for page in selected
        if page.subset in {"books", "uploaded", "recto"}
    ]
    spontaneous = [page for page in selected if page.subset == "handwritten"]
    rng.shuffle(controlled)
    if len(controlled) != 35:
        raise ValueError(f"Se esperaban 35 páginas controladas, hay {len(controlled)}")
    if len(spontaneous) != 5:
        raise ValueError(f"Se esperaban 5 páginas manuscritas, hay {len(spontaneous)}")

    for index, page in enumerate(controlled):
        page.fold = index // 7
    for page in spontaneous:
        page.fold = -1

    ensure_dir(pages_dir)
    rows = []
    for page in selected:
        page_json = Path(pages_dir) / f"{page.page_id}.json"
        write_json(page_json, page.to_dict())
        classes = sorted(_class_set(page))
        rows.append(
            {
                "page_id": page.page_id,
                "source": page.source,
                "subset": page.subset,
                "image_path": page.image_path,
                "width": page.width,
                "height": page.height,
                "n_boxes": len(page.boxes),
                "classes": ",".join(str(value) for value in classes),
                "group": "spontaneous" if page.fold == -1 else "controlled",
                "fold": page.fold,
            }
        )

    write_csv(output_csv, rows)
    summary = {
        "seed": seed,
        "n_pages": len(selected),
        "n_controlled": len(controlled),
        "n_spontaneous": len(spontaneous),
        "counts_by_subset": {
            "books": sum(1 for page in selected if page.subset == "books"),
            "uploaded": sum(1 for page in selected if page.subset == "uploaded"),
            "dsbi_recto": sum(1 for page in selected if page.subset == "recto"),
            "handwritten": sum(1 for page in selected if page.subset == "handwritten"),
        },
        "coverage": len(covered),
        "missing_classes": missing,
        "folds": {
            str(fold): sum(1 for page in controlled if page.fold == fold)
            for fold in range(5)
        },
    }
    write_json(summary_json, summary)
    return summary
