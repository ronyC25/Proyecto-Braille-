from src.evaluation.metrics import box_iou, cer, levenshtein, wer
from src.statistics.surveys import nasa_tlx, sus_score


def test_box_iou():
    assert box_iou((0, 0, 10, 10), (0, 0, 10, 10)) == 1.0
    assert box_iou((0, 0, 10, 10), (20, 20, 30, 30)) == 0.0
    assert 0 < box_iou((0, 0, 10, 10), (5, 5, 15, 15)) < 1


def test_cer_wer():
    assert cer("abc", "abc") == 0.0
    assert cer("abc", "abd") == 1 / 3
    assert wer("hola mundo", "hola mundo") == 0.0
    assert wer("hola mundo", "hola") == 0.5
    assert levenshtein("kitten", "sitting") == 3


def test_surveys():
    assert sus_score([5, 1, 5, 1, 5, 1, 5, 1, 5, 1]) == 100.0
    assert sus_score([1, 5, 1, 5, 1, 5, 1, 5, 1, 5]) == 0.0
    assert nasa_tlx([50, 50, 50, 50, 50, 50]) == 50.0
