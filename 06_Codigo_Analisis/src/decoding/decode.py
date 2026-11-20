from src.decoding.braille_map import decode_cells
from src.evaluation.reading_order import group_lines


def decode_detections(detections, y_tolerance=0.02):
    """Decode detections (class_id 0..62) into lines of Spanish Grade 1 text."""
    lines = group_lines(detections, y_tolerance=y_tolerance)
    decoded = []
    for line in lines:
        int_labels = [item["class_id"] + 1 for item in line["items"]]
        decoded.append(decode_cells(int_labels))
    return "\n".join(decoded)
