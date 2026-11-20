"""Canonical Braille dot-pattern mapping used by the data pipeline.

The project uses 63 classes: every non-empty combination of six Braille dots.
The canonical integer label is the bitmask sum:

    int_label = sum(2 ** (dot - 1) for every raised dot)

so int_label is in [1, 63]. YOLO classes are zero-indexed: class_id = int_label - 1.
"""


def dots_to_int(dots):
    if len(dots) != 6:
        raise ValueError("Se esperaban 6 puntos Braille")
    value = 0
    for index, dot in enumerate(dots):
        if int(dot) == 1:
            value += 2 ** index
    return value


def int_to_dots(int_label):
    int_label = int(int_label)
    if not 0 <= int_label <= 63:
        raise ValueError(f"Etiqueta Braille fuera de rango: {int_label}")
    return tuple(1 if int_label & (2 ** index) else 0 for index in range(6))


def int_to_label123(int_label):
    return "".join(
        str(index + 1)
        for index, dot in enumerate(int_to_dots(int_label))
        if dot
    )


def int_to_unicode(int_label):
    return chr(0x2800 + int(int_label))


def int_to_class_id(int_label):
    int_label = int(int_label)
    if not 1 <= int_label <= 63:
        raise ValueError(f"La clase debe estar en [1, 63], recibido {int_label}")
    return int_label - 1


def class_id_to_int(class_id):
    class_id = int(class_id)
    if not 0 <= class_id <= 62:
        raise ValueError(f"El class_id debe estar en [0, 62], recibido {class_id}")
    return class_id + 1


CLASS_NAMES = [f"dots_{int_to_label123(int_label)}" for int_label in range(1, 64)]
