import pytest

from src.data.class_mapping import (
    class_id_to_int,
    dots_to_int,
    int_to_class_id,
    int_to_dots,
    int_to_label123,
)


def test_dots_to_int():
    assert dots_to_int([1, 0, 0, 0, 0, 0]) == 1
    assert dots_to_int([0, 1, 0, 0, 0, 0]) == 2
    assert dots_to_int([1, 1, 0, 0, 0, 0]) == 3
    assert dots_to_int([1, 1, 1, 1, 1, 1]) == 63


def test_roundtrip():
    for value in range(1, 64):
        assert dots_to_int(int_to_dots(value)) == value


def test_class_ids():
    assert int_to_class_id(1) == 0
    assert int_to_class_id(63) == 62
    assert class_id_to_int(0) == 1
    assert class_id_to_int(62) == 63


def test_label123():
    assert int_to_label123(1) == "1"
    assert int_to_label123(25) == "145"
    assert int_to_label123(63) == "123456"


def test_invalid_values():
    with pytest.raises(ValueError):
        int_to_dots(64)
    with pytest.raises(ValueError):
        int_to_class_id(0)
    with pytest.raises(ValueError):
        dots_to_int([1, 0, 0])
