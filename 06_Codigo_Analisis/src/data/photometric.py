import math

import cv2
import numpy as np
from PIL import Image

SIZE = 1024

LIGHTING = ("L30", "L45", "Ldif")
ORIENTATION = ("O0", "O15")
SUPPORT = ("Sflat", "Swrinkle")

CONDITIONS = [
    (lighting, orientation, support)
    for lighting in LIGHTING
    for orientation in ORIENTATION
    for support in SUPPORT
]


def condition_id(lighting, orientation, support):
    return f"{lighting}_{orientation}_{support}"


def _clip_box(box, width, height):
    x1, y1, x2, y2, class_id = box
    x1 = max(0.0, min(float(x1), width))
    x2 = max(0.0, min(float(x2), width))
    y1 = max(0.0, min(float(y1), height))
    y2 = max(0.0, min(float(y2), height))
    if x2 - x1 < 1.0 or y2 - y1 < 1.0:
        return None
    return (x1, y1, x2, y2, int(class_id))


def letterbox(image, boxes, size=SIZE):
    """Resize and pad an image to size x size, transforming boxes to the new canvas."""
    if not isinstance(image, Image.Image):
        image = Image.fromarray(image)
    image = image.convert("RGB")
    width, height = image.size
    scale = min(size / width, size / height)
    new_width = max(1, int(round(width * scale)))
    new_height = max(1, int(round(height * scale)))
    resized = image.resize((new_width, new_height), Image.BILINEAR)
    canvas = Image.new("RGB", (size, size), (255, 255, 255))
    pad_x = (size - new_width) // 2
    pad_y = (size - new_height) // 2
    canvas.paste(resized, (pad_x, pad_y))

    transformed = []
    for x1, y1, x2, y2, class_id in boxes:
        transformed.append(
            (
                x1 * scale + pad_x,
                y1 * scale + pad_y,
                x2 * scale + pad_x,
                y2 * scale + pad_y,
                int(class_id),
            )
        )
    return np.array(canvas), transformed


def _apply_orientation(image, boxes, orientation, size=SIZE):
    if orientation == "O0":
        return image, boxes
    if orientation != "O15":
        raise ValueError(f"Orientación no soportada: {orientation}")

    height, width = image.shape[:2]
    source = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    destination = np.float32(
        [
            [0.10 * width, 0.02 * height],
            [0.90 * width, 0.02 * height],
            [width, height],
            [0, height],
        ]
    )
    matrix = cv2.getPerspectiveTransform(source, destination)
    warped = cv2.warpPerspective(
        image,
        matrix,
        (size, size),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )

    transformed = []
    for x1, y1, x2, y2, class_id in boxes:
        points = np.float32(
            [[[x1, y1]], [[x2, y1]], [[x2, y2]], [[x1, y2]]]
        )
        mapped = cv2.perspectiveTransform(points, matrix).reshape(-1, 2)
        nx1, ny1 = mapped[:, 0].min(), mapped[:, 1].min()
        nx2, ny2 = mapped[:, 0].max(), mapped[:, 1].max()
        box = _clip_box((nx1, ny1, nx2, ny2, class_id), size, size)
        if box is not None:
            transformed.append(box)
    return warped, transformed


def _apply_lighting(image, lighting, rng):
    height, width = image.shape[:2]
    yy, xx = np.mgrid[0:height, 0:width]
    if lighting == "L30":
        angle = math.radians(30)
        factor = 0.78 + 0.38 * _normalized_gradient(xx, yy, angle)
    elif lighting == "L45":
        angle = math.radians(45)
        factor = 0.72 + 0.50 * _normalized_gradient(xx, yy, angle)
    elif lighting == "Ldif":
        factor = 0.92 + 0.12 * _normalized_gradient(xx, yy, math.radians(10))
    else:
        raise ValueError(f"Iluminación no soportada: {lighting}")

    result = image.astype(np.float32) * factor[..., None]
    shadow = _soft_shadow(width, height)
    result *= shadow[..., None]
    if lighting == "Ldif":
        result = cv2.GaussianBlur(result, (3, 3), 0)
    noise = rng.normal(0.0, 1.5, result.shape)
    result = np.clip(result + noise, 0, 255).astype(np.uint8)
    return result


def _normalized_gradient(xx, yy, angle):
    height, width = xx.shape
    gradient = xx * math.cos(angle) + yy * math.sin(angle)
    gradient = gradient - gradient.min()
    maximum = gradient.max()
    if maximum <= 0:
        return np.zeros_like(gradient)
    return gradient / maximum


def _soft_shadow(width, height):
    yy, xx = np.mgrid[0:height, 0:width]
    cx, cy = 0.18 * width, 0.18 * height
    sigma = 0.35 * max(width, height)
    distance = (xx - cx) ** 2 + (yy - cy) ** 2
    shadow = 1.0 - 0.12 * np.exp(-distance / (2 * sigma ** 2))
    return shadow


def _apply_support(image, boxes, support, rng, size=SIZE):
    if support == "Sflat":
        return image, boxes
    if support != "Swrinkle":
        raise ValueError(f"Soporte no soportado: {support}")

    height, width = image.shape[:2]
    amplitude = 3.5
    phase = rng.uniform(0, 2 * math.pi)
    yy, xx = np.mgrid[0:height, 0:width]
    dx = amplitude * np.sin(2 * math.pi * yy / height * 2 + phase)
    dy = amplitude * np.sin(2 * math.pi * xx / width * 2 + phase)
    map_x = (xx + dx).astype(np.float32)
    map_y = (yy + dy).astype(np.float32)
    warped = cv2.remap(
        image,
        map_x,
        map_y,
        interpolation=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )

    crease = 1.0 - 0.07 * (0.5 + 0.5 * np.sin(2 * math.pi * yy / height * 3 + phase))
    warped = np.clip(warped.astype(np.float32) * crease[..., None], 0, 255).astype(np.uint8)

    transformed = []
    for x1, y1, x2, y2, class_id in boxes:
        corners = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        mapped = []
        for x, y in corners:
            nx = x + amplitude * math.sin(2 * math.pi * y / height * 2 + phase)
            ny = y + amplitude * math.sin(2 * math.pi * x / width * 2 + phase)
            mapped.append((nx, ny))
        nx1 = min(point[0] for point in mapped)
        ny1 = min(point[1] for point in mapped)
        nx2 = max(point[0] for point in mapped)
        ny2 = max(point[1] for point in mapped)
        box = _clip_box((nx1, ny1, nx2, ny2, class_id), size, size)
        if box is not None:
            transformed.append(box)
    return warped, transformed


def apply_condition(image, boxes, lighting, orientation, support, size=SIZE, seed=42):
    """Apply one photometric condition and return (rgb_image, boxes, params)."""
    rng = np.random.default_rng(seed)
    image, boxes = letterbox(image, boxes, size=size)
    image, boxes = _apply_orientation(image, boxes, orientation, size=size)
    image = _apply_lighting(image, lighting, rng)
    image, boxes = _apply_support(image, boxes, support, rng, size=size)
    params = {
        "lighting": lighting,
        "orientation": orientation,
        "support": support,
        "size": size,
        "seed": int(seed),
    }
    return image, boxes, params
