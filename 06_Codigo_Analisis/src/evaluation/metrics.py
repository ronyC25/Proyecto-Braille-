import numpy as np
from sklearn.metrics import cohen_kappa_score, f1_score, roc_auc_score


def box_iou(box_a, box_b):
    ax1, ay1, ax2, ay2 = box_a
    bx1, by1, bx2, by2 = box_b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    inter_w = max(0.0, inter_x2 - inter_x1)
    inter_h = max(0.0, inter_y2 - inter_y1)
    inter = inter_w * inter_h
    area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
    area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0.0


def match_boxes(detections, ground_truths, iou_threshold=0.5):
    """Greedy matching by confidence. Returns tp, fp, fn and matched pairs."""
    detections = sorted(detections, key=lambda item: item.get("score", 1.0), reverse=True)
    used = set()
    tp = 0
    matches = []
    for detection in detections:
        best_index = None
        best_iou = 0.0
        for index, truth in enumerate(ground_truths):
            if index in used:
                continue
            if detection["class_id"] != truth["class_id"]:
                continue
            iou = box_iou(detection["box"], truth["box"])
            if iou > best_iou:
                best_iou = iou
                best_index = index
        if best_index is not None and best_iou >= iou_threshold:
            used.add(best_index)
            tp += 1
            matches.append((detection, ground_truths[best_index], best_iou))
    fp = len(detections) - tp
    fn = len(ground_truths) - tp
    return tp, fp, fn, matches


def precision_recall_f1(tp, fp, fn):
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def f1_macro(y_true, y_pred, labels=None):
    return f1_score(y_true, y_pred, labels=labels, average="macro", zero_division=0)


def cohen_kappa(y_true, y_pred):
    return cohen_kappa_score(y_true, y_pred)


def auc_roc_macro(y_true, y_score):
    return roc_auc_score(y_true, y_score, multi_class="ovr", average="macro")


def levenshtein(reference, hypothesis):
    reference = list(reference)
    hypothesis = list(hypothesis)
    rows = len(reference) + 1
    cols = len(hypothesis) + 1
    table = np.zeros((rows, cols), dtype=int)
    table[:, 0] = range(rows)
    table[0, :] = range(cols)
    for row in range(1, rows):
        for col in range(1, cols):
            cost = 0 if reference[row - 1] == hypothesis[col - 1] else 1
            table[row, col] = min(
                table[row - 1, col] + 1,
                table[row, col - 1] + 1,
                table[row - 1, col - 1] + cost,
            )
    return int(table[-1, -1])


def cer(reference, hypothesis):
    if not reference:
        return 0.0 if not hypothesis else 1.0
    return levenshtein(reference, hypothesis) / len(reference)


def wer(reference, hypothesis):
    reference_words = reference.split()
    hypothesis_words = hypothesis.split()
    if not reference_words:
        return 0.0 if not hypothesis_words else 1.0
    return levenshtein(reference_words, hypothesis_words) / len(reference_words)


def bootstrap_ci(values, statistic=np.mean, n_resamples=5000, confidence_level=0.95, seed=42):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(n_resamples):
        sample = rng.choice(values, size=len(values), replace=True)
        estimates.append(statistic(sample))
    alpha = (1 - confidence_level) / 2
    return float(np.quantile(estimates, alpha)), float(np.quantile(estimates, 1 - alpha))
