def group_lines(detections, y_tolerance=0.02):
    """Group detections into lines using normalized y centers."""
    if not detections:
        return []
    ordered = sorted(detections, key=lambda item: item["y_center"])
    lines = []
    for detection in ordered:
        placed = False
        for line in lines:
            if abs(detection["y_center"] - line["y_center"]) <= y_tolerance:
                line["items"].append(detection)
                line["y_center"] = sum(item["y_center"] for item in line["items"]) / len(
                    line["items"]
                )
                placed = True
                break
        if not placed:
            lines.append({"y_center": detection["y_center"], "items": [detection]})
    lines.sort(key=lambda line: line["y_center"])
    for line in lines:
        line["items"].sort(key=lambda item: item["x_center"])
    return lines


def reading_order(detections, y_tolerance=0.02):
    lines = group_lines(detections, y_tolerance=y_tolerance)
    return [item for line in lines for item in line["items"]]
