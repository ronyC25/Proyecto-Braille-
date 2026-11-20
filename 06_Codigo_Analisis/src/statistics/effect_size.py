import numpy as np


def cohens_d(group_a, group_b):
    group_a = np.asarray(group_a, dtype=float)
    group_b = np.asarray(group_b, dtype=float)
    n_a, n_b = len(group_a), len(group_b)
    if n_a < 2 or n_b < 2:
        return float("nan")
    pooled = np.sqrt(
        ((n_a - 1) * np.var(group_a, ddof=1) + (n_b - 1) * np.var(group_b, ddof=1))
        / (n_a + n_b - 2)
    )
    if pooled == 0:
        return 0.0
    return float((np.mean(group_a) - np.mean(group_b)) / pooled)


def rank_biserial(x, y):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    differences = x - y
    differences = differences[differences != 0]
    if len(differences) == 0:
        return 0.0
    ranks = np.argsort(np.argsort(np.abs(differences))) + 1
    positive = ranks[differences > 0].sum()
    negative = ranks[differences < 0].sum()
    total = positive + negative
    return float((positive - negative) / total) if total else 0.0
