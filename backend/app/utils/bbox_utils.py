def convert_xyxy_to_dict(box):
    x1, y1, x2, y2 = box

    return {
        "x1": int(x1),
        "y1": int(y1),
        "x2": int(x2),
        "y2": int(y2)
    }


def calculate_box_area(box):
    x1 = box["x1"]
    y1 = box["y1"]
    x2 = box["x2"]
    y2 = box["y2"]

    width = max(0, x2 - x1)
    height = max(0, y2 - y1)

    return width * height