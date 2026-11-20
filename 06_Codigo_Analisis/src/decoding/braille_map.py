"""Canonical mapping between Braille dot patterns and YOLO class ids.

The project uses 63 classes: every non-empty combination of the six Braille
dots. The canonical integer label is the bitmask sum:

    int_label = sum(2 ** (dot - 1) for every raised dot)

so int_label is in [1, 63]. YOLO classes are zero-indexed: class_id = int_label - 1.
"""

INT_TO_DOTS = {}
DOTS_TO_INT = {}


def dots_to_int(dots):
    """Convert a sequence of six 0/1 values to the canonical integer label."""
    if len(dots) != 6:
        raise ValueError("Se esperaban 6 puntos Braille")
    value = 0
    for index, dot in enumerate(dots):
        if int(dot) == 1:
            value += 2 ** index
    return value


def int_to_dots(int_label):
    """Return the six 0/1 values for a canonical integer label."""
    int_label = int(int_label)
    if not 0 <= int_label <= 63:
        raise ValueError(f"Etiqueta Braille fuera de rango: {int_label}")
    return tuple(1 if int_label & (2 ** index) else 0 for index in range(6))


def int_to_label123(int_label):
    """Return the dot numbers, e.g. 25 -> '14'."""
    return "".join(str(index + 1) for index, dot in enumerate(int_to_dots(int_label)) if dot)


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


for _int_label in range(1, 64):
    _dots = int_to_dots(_int_label)
    INT_TO_DOTS[_int_label] = _dots
    DOTS_TO_INT[_dots] = _int_label

CLASS_NAMES = [f"dots_{int_to_label123(int_label)}" for int_label in range(1, 64)]

# Spanish Grade 1: letters and a few signs. Accented vowels and Spanish-specific
# signs are intentionally left as TODO until they are validated against a
# Spanish Braille table.
SPANISH_GRADE1 = {
    "1": "a",
    "12": "b",
    "14": "c",
    "145": "d",
    "15": "e",
    "124": "f",
    "1245": "g",
    "125": "h",
    "24": "i",
    "245": "j",
    "13": "k",
    "123": "l",
    "134": "m",
    "1345": "n",
    "12456": "ñ",
    "135": "o",
    "1234": "p",
    "12345": "q",
    "1235": "r",
    "234": "s",
    "2345": "t",
    "136": "u",
    "1236": "v",
    "2456": "w",
    "1346": "x",
    "13456": "y",
    "1356": "z",
    "2": ",",
    "23": ";",
    "25": ":",
    "256": ".",
    "26": "?",
    "235": "!",
    "36": "-",
}

# TODO: add á, é, í, ó, ú, ü, ¿, ¡, «, », numbers with the number sign,
# capital sign and Spanish-specific punctuation once validated.


def decode_int(int_label):
    """Decode one cell to a Spanish character, or '?' if still unmapped."""
    key = int_to_label123(int_label)
    return SPANISH_GRADE1.get(key, "?")


def decode_cells(int_labels):
    return "".join(decode_int(int_label) for int_label in int_labels)
