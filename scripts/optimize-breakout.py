"""Reduce redundant SVG keyframes while preserving the Breakout simulation."""
from pathlib import Path
import xml.etree.ElementTree as ET

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

for path in Path("dist").glob("*.svg"):
    original_size = path.stat().st_size
    root = ET.parse(path).getroot()
    for animation in root.iter(f"{NS and '{' + NS + '}'}animate"):
        values = animation.get("values", "").split(";")
        count = len(values)
        if count < 2:
            continue
        attribute = animation.get("attributeName")
        if attribute in {"fill", "opacity"}:
            indices = [0] + [i for i in range(1, count) if values[i] != values[i - 1]]
            if indices[-1] != count - 1:
                indices.append(count - 1)
            animation.set("calcMode", "discrete")
            selected = [values[i] for i in indices]
        else:
            # Keep ten motion samples per second, with linear interpolation.
            indices = list(range(0, count, 6))
            if indices[-1] != count - 1:
                indices.append(count - 1)
            selected = [str(round(float(values[i]), 2)) for i in indices]
            animation.set("calcMode", "linear")
        animation.set("values", ";".join(selected))
        animation.set("keyTimes", ";".join(
            "0" if i == 0 else "1" if i == count - 1 else f"{i / (count - 1):.8f}"
            for i in indices
        ))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    print(f"{path}: {original_size:,} -> {path.stat().st_size:,} bytes")
    assert path.stat().st_size < 2_000_000, "Animation is too large for the README"
