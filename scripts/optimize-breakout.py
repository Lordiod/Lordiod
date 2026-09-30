"""Compress SVG keyframes without smoothing away ball or paddle turns."""
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

def motion_indices(values, tolerance=.04):
    """Keep a piecewise linear path within .04 pixels of every original frame."""
    keep = {0, len(values) - 1}
    pending = [(0, len(values) - 1)]
    while pending:
        first, last = pending.pop()
        if last - first < 2:
            continue
        slope = (values[last] - values[first]) / (last - first)
        worst, error = first, tolerance
        for i in range(first + 1, last):
            distance = abs(values[i] - (values[first] + slope * (i - first)))
            if distance > error:
                worst, error = i, distance
        if worst != first:
            keep.add(worst)
            pending.extend(((first, worst), (worst, last)))
    return sorted(keep)

for path in Path("dist").glob("*.svg"):
    original_size = path.stat().st_size
    root = ET.parse(path).getroot()
    for animation in root.iter("{" + NS + "}animate"):
        values = animation.get("values", "").split(";")
        count = len(values)
        if count < 2:
            continue
        if animation.get("attributeName") in {"fill", "opacity"}:
            indices = [0] + [i for i in range(1, count) if values[i] != values[i - 1]]
            if indices[-1] != count - 1:
                indices.append(count - 1)
            animation.set("calcMode", "discrete")
            selected = [values[i] for i in indices]
        else:
            coordinates = list(map(float, values))
            indices = motion_indices(coordinates)
            selected = [str(round(coordinates[i], 3)) for i in indices]
            animation.set("calcMode", "linear")
        animation.set("values", ";".join(selected))
        animation.set("keyTimes", ";".join(
            "0" if i == 0 else "1" if i == count - 1 else f"{i / (count - 1):.8f}"
            for i in indices
        ))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print(f"{path}: {original_size:,} -> {path.stat().st_size:,} bytes")
    assert path.stat().st_size < 2_000_000, "Animation is too large for the README"
