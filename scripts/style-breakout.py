"""Style generated contribution SVGs as a modern, animated arcade card."""
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import date, timedelta

NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", NS)

def node(tag, **attrs):
    return ET.Element("{" + NS + "}" + tag,
                      {key.replace("_", "-"): str(value) for key, value in attrs.items()})

def add(parent, tag, **attrs):
    element = node(tag, **attrs)
    parent.append(element)
    return element

def label(parent, text, x, y, size, fill, **attrs):
    element = add(parent, "text", x=x, y=y, fill=fill, font_size=size,
                  font_family="Segoe UI, Inter, Arial, sans-serif", **attrs)
    element.text = text
    return element

def style(path):
    root = ET.parse(path).getroot()
    width, height = map(float, root.get("viewBox").split()[2:])
    dark = "dark" in path.name
    bg, panel, text, muted, border = "#0a0e12", "#0d1217", "#e6edf3", "#697681", "#202830"
    def map_y(y):
        return y if y <= 112 else 112 + (y - 112) * .4
    total_width, total_height = width + 64, map_y(height) + 116
    root.set("viewBox", f"0 0 {total_width:g} {total_height:g}")
    root.set("width", f"{total_width:g}")
    root.set("height", f"{total_height:g}")
    root.set("role", "img")
    old_children = list(root)
    for child in old_children:
        root.remove(child)
    add(root, "title").text = "Contribution Breakout — Lordiod"
    defs = add(root, "defs")
    surface = add(defs, "linearGradient", id="arcadeSurface", x1="0", y1="0", x2="1", y2="1")
    add(surface, "stop", offset="0%", stop_color=panel)
    add(surface, "stop", offset="100%", stop_color=bg)
    colors = [("#173b2b", "#122e26"), ("#1b5838", "#1b5838"),
              ("#248347", "#248347"), ("#31b951", "#31b951"),
              ("#53e66b", "#53e66b")]
    for index, (top, bottom) in enumerate(colors):
        gradient = add(defs, "linearGradient", id=f"brick{index}", x1="0", y1="0", x2="0", y2="1")
        add(gradient, "stop", offset="0%", stop_color=top)
        add(gradient, "stop", offset="100%", stop_color=bottom)
    gradient = add(defs, "linearGradient", id="paddleGradient")
    add(gradient, "stop", offset="0%", stop_color="#4cd969")
    add(gradient, "stop", offset="100%", stop_color="#4cd969")
    glow = add(defs, "filter", id="arcadeGlow", x="-100%", y="-100%", width="300%", height="300%")
    add(glow, "feGaussianBlur", stdDeviation="3", result="blur")
    merge = add(glow, "feMerge")
    add(merge, "feMergeNode", **{"in": "blur"})
    add(merge, "feMergeNode", **{"in": "SourceGraphic"})
    add(root, "rect", x=".5", y=".5", width=total_width - 1, height=total_height - 1,
        rx="20", fill="url(#arcadeSurface)", stroke="#131a20")
    add(root, "rect", x=14, y=14, width=total_width - 28, height=total_height - 28,
        rx="8", fill="none", stroke=border)
    add(root, "path", d=f"M14 68 H{total_width - 14:g}", stroke=border)
    icon = ["00100000100", "00010001000", "00111111100", "01101110110",
            "11111111111", "10111111101", "10100000101", "00011011000"]
    for row, cells in enumerate(icon):
        for col, cell in enumerate(cells):
            if cell == "1":
                add(root, "rect", x=32 + col * 2.4, y=36 + row * 2.4,
                    width="2.4", height="2.4", fill="#39d65d")
    heading = label(root, "Contribution ", 78, 52, 23, text, font_weight="700")
    add(heading, "tspan", fill="#36df62").text = "Breakout"
    today = date.today()
    start = today - timedelta(days=364)
    start -= timedelta(days=(start.weekday() + 1) % 7)
    for index in range(13):
        month = (today.month - 1 + index) % 12 + 1
        label(root, date(2000, month, 1).strftime("%b"),
              32 + index * (width - 28) / 12, 91, 10, muted)
    arena = add(root, "g", transform="translate(32 100)")
    for x in range(53):
        for y in range(12):
            add(arena, "rect", x=x * 16 + 1, y=y * 16 + 1,
                width="13", height="13", rx="2", fill="#141b21", opacity=".8")
    for child in old_children:
        arena.append(child)
    # Original colors encode contribution intensity; keep that mapping.
    color_levels = {
        "#ebedf0": 0, "#9be9a8": 1, "#40c463": 2, "#30a14e": 3, "#216e39": 4,
        "#161b22": 0, "#01311f": 1, "#034525": 2, "#0f6d31": 3, "#00c647": 4,
    }
    animations = list(arena.iter("{" + NS + "}animate"))
    duration = float(animations[0].get("dur").removesuffix("s")) / 3
    for animation in animations:
        animation.set("dur", f"{duration:.3f}s")
        if animation.get("attributeName") == "fill":
            values = animation.get("values").split(";")
            animation.set("values", ";".join(
                f"url(#brick{color_levels[value]})" if value in color_levels else value
                for value in values))
    blocks = [element for element in arena if element.get("id", "").startswith("block-")]
    for block in blocks:
        block.set("rx", "2")
        block.set("ry", "2")
        block.set("width", "13")
        block.set("height", "13")
        level = color_levels.get(block.get("fill"), 0)
        block.set("fill", f"url(#brick{level})")
        block.set("stroke", colors[level][0])
        block.set("stroke-width", "0")
        opacity = next((a for a in block if a.get("attributeName") == "opacity"), None)
        if opacity is None:
            continue
        vals = opacity.get("values").split(";")
        times = list(map(float, opacity.get("keyTimes").split(";")))
        hit = next((times[i] for i in range(1, len(vals)) if vals[i - 1] == "1" and vals[i] == "0"), None)
        if hit is None or hit >= .98:
            continue
        # Small sparks appear only when the corresponding contribution brick breaks.
        x, y = float(block.get("x")) + 5.5, float(block.get("y")) + 5.5
        end = min(hit + .006, .999999)
        keys = f"0;{max(0.000001, hit - .000001):.8f};{hit:.8f};{end:.8f};1"
        for dx, dy in [(-12, -10), (13, -7), (3, 15)]:
            spark = add(arena, "rect", x=x, y=y, width="3", height="3", rx=".5",
                        fill=colors[level][0], opacity="0")
            for attr, values in [
                ("x", f"{x};{x};{x};{x + dx};{x + dx}"),
                ("y", f"{y};{y};{y};{y + dy};{y + dy}"),
                ("opacity", "0;0;.9;0;0"),
            ]:
                add(spark, "animate", attributeName=attr, values=values, keyTimes=keys,
                    dur=f"{duration:.3f}s", repeatCount="indefinite", calcMode="linear")
    for element in arena:
        if element.get("id") == "paddle":
            element.set("fill", "url(#paddleGradient)")
            element.set("rx", "5")
            element.set("filter", "url(#arcadeGlow)")
        elif element.get("id") == "ball":
            element.set("fill", "#e5ffe9")
            element.set("filter", "url(#arcadeGlow)")
        elif element.get("class") == "trail":
            element.set("fill", "#36d960")
            element.set("opacity", ".28")
        elif element.get("id") == "victory":
            element.text = "LEVEL CLEARED"
            element.set("fill", text)
            element.set("font-family", "Segoe UI, Arial, sans-serif")
            element.set("font-weight", "700")
            for animation in element:
                animation.set("repeatCount", "indefinite")
    ball = next(e for e in arena if e.get("id") == "ball")
    trails = [e for e in arena if e.get("class") == "trail"]
    for offset, trail in enumerate(trails, 1):
        trail.set("opacity", str(.45 - offset * .055))
        for attribute in ("cx", "cy"):
            source = next(a for a in ball if a.get("attributeName") == attribute)
            target = next(a for a in trail if a.get("attributeName") == attribute)
            values = source.get("values").split(";")
            target.set("values", ";".join(values[max(0, i - offset)] for i in range(len(values))))
    for element in list(arena):
        if element.tag == "{" + NS + "}style":
            arena.remove(element)
        if element.get("id") == "paddle":
            element.set("y", str(map_y(float(element.get("y")))))
            element.set("rx", "3")
        if element.get("id") == "ball" or element.get("class") == "trail":
            element.set("cy", str(map_y(float(element.get("cy")))))
        if element.get("id") == "victory":
            element.set("y", str(map_y(height) / 2))
    for animation in arena.iter("{" + NS + "}animate"):
        if animation.get("attributeName") == "cy":
            animation.set("values", ";".join(str(round(map_y(float(v)), 2))
                                            for v in animation.get("values").split(";")))
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    assert path.stat().st_size < 2_500_000
    print(f"Styled {path}: {path.stat().st_size:,} bytes")

if __name__ == "__main__":
    for path in Path("dist").glob("*.svg"):
        style(path)
