import numpy as np
from PIL import Image

from src.data.photometric import CONDITIONS, apply_condition, condition_id, letterbox


def _synthetic_image():
    image = Image.new("RGB", (300, 200), (255, 255, 255))
    for x in range(60, 140):
        for y in range(50, 150):
            image.putpixel((x, y), (0, 0, 0))
    return image, [(60, 50, 140, 150, 0)]


def test_letterbox():
    image, boxes = _synthetic_image()
    canvas, transformed = letterbox(image, boxes, size=1024)
    assert canvas.shape == (1024, 1024, 3)
    assert len(transformed) == 1
    x1, y1, x2, y2, class_id = transformed[0]
    assert 0 <= x1 < x2 <= 1024
    assert 0 <= y1 < y2 <= 1024
    assert class_id == 0


def test_all_conditions():
    image, boxes = _synthetic_image()
    for lighting, orientation, support in CONDITIONS:
        output, transformed, params = apply_condition(
            image,
            boxes,
            lighting=lighting,
            orientation=orientation,
            support=support,
            seed=42,
        )
        assert output.shape == (1024, 1024, 3)
        assert output.dtype == np.uint8
        assert len(transformed) == 1
        x1, y1, x2, y2, class_id = transformed[0]
        assert 0 <= x1 < x2 <= 1024
        assert 0 <= y1 < y2 <= 1024
        assert class_id == 0
        assert params["lighting"] == lighting
        assert params["orientation"] == orientation
        assert params["support"] == support


def test_condition_ids_are_unique():
    ids = {condition_id(*condition) for condition in CONDITIONS}
    assert len(ids) == 12
