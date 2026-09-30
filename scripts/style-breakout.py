"""Style generated contribution SVGs as a modern, animated arcade card."""
from pathlib import Path
import xml.etree.ElementTree as ET

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
    bg, panel, text, muted, border = (
        ("#080d1a", "#101a2f", "#edf4ff", "#8da2c3", "#243751") if dark else
        ("#f4f7ff", "#e6eefb", "#15213b", "#586d8e", "#cad8ef"))
    total_width, total_height = width + 56, height + 134
    root.set("viewBox", f"0 0 {total_width:g} {total_height:g}")
    root.set("width", f"{total_width:g}")
    root.set("height", f"{total_height:g}")
    root.set("role", "img")
    title = node("title")
    title.text = "Youssef's contribution arcade — animated Breakout"
    root.insert(0, title)
    old_children = [child for child in root if child is not title]
    for child in old_children:
        root.remove(child)
    defs = add(root, "defs")
    gradient = add(defs, "linearGradient", id="arcadeSurface", x1="0", y1="0", x2="1", y2="1")
    add(gradient, "stop", offset="0%", stop_color=panel)
    add(gradient, "stop", offset="100%", stop_color=bg)
    colors = [("#647da1", "#3a506d"), ("#34d399", "#059669"),
              ("#38bdf8", "#2563eb"), ("#818cf8", "#6366f1"),
              ("#e879f9", "#a855f7")]
    if not dark:
        colors[0] = ("#dbe6f5", "#bccde4")
    for index, (top, bottom) in enumerate(colors):
        gradient = add(defs, "linearGradient", id=f"brick{index}", x1="0", y1="0", x2="0", y2="1")
        add(gradient, "stop", offset="0%", stop_color=top)
        add(gradient, "stop", offset="100%", stop_color=bottom)
    gradient = add(defs, "linearGradient", id="paddleGradient")
    for offset, color in [("0%", "#22d3ee"), ("50%", "#818cf8"), ("100%", "#e879f9")]:
        add(gradient, "stop", offset=offset, stop_color=color)
    glow = add(defs, "filter", id="arcadeGlow", x="-100%", y="-100%", width="300%", height="300%")
    add(glow, "feGaussianBlur", stdDeviation="3", result="blur")
    merge = add(glow, "feMerge")
    add(merge, "feMergeNode", **{"in": "blur"})
    add(merge, "feMergeNode", **{"in": "SourceGraphic"})
    pattern = add(defs, "pattern", id="arenaGrid", width="32", height="32", patternUnits="userSpaceOnUse")
    add(pattern, "path", d="M 32 0 L 0 0 0 32", fill="none", stroke=border, stroke_width=".5", opacity=".45")
    add(root, "rect", x=".5", y=".5", width=total_width - 1, height=total_height - 1,
        rx="22", fill="url(#arcadeSurface)", stroke=border)
    label(root, "CONTRIBUTION ARCADE", 28, 34, 11, muted, letter_spacing="2.5", font_weight="600")
    label(root, "Break. Build. Repeat.", 28, 61, 22, text, font_weight="700")
    live = add(root, "circle", cx=total_width - 114, cy=36, r="3", fill="#34d399")
    add(live, "animate", attributeName="opacity", values="1;.3;1", dur="2s", repeatCount="indefinite")
    label(root, "LORDIOD", total_width - 101, 40, 11, muted, letter_spacing="1.3")
    add(root, "rect", x=20, y=79, width=width + 16, height=height + 14,
        rx="14", fill=bg, stroke=border)
    add(root, "rect", x=20, y=79, width=width + 16, height=height + 14,
        rx="14", fill="url(#arenaGrid)")
    arena = add(root, "g", transform="translate(28 86)")
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
        block.set("rx", "3")
        block.set("ry", "3")
        level = color_levels.get(block.get("fill"), 0)
        block.set("fill", f"url(#brick{level})")
        block.set("stroke", colors[level][0])
        block.set("stroke-width", ".35")
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
            spark = add(arena, "circle", cx=x, cy=y, r="1.5",
                        fill=colors[level][0], opacity="0")
            for attr, values in [
                ("cx", f"{x};{x};{x};{x + dx};{x + dx}"),
                ("cy", f"{y};{y};{y};{y + dy};{y + dy}"),
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
            element.set("fill", "#e0faff" if dark else "#0891b2")
            element.set("filter", "url(#arcadeGlow)")
        elif element.get("class") == "trail":
            element.set("fill", "#38bdf8")
            element.set("opacity", ".28")
        elif element.get("id") == "victory":
            element.text = "LEVEL CLEARED"
            element.set("fill", text)
            element.set("font-family", "Segoe UI, Arial, sans-serif")
            element.set("font-weight", "700")
            for animation in element:
                animation.set("repeatCount", "indefinite")
    label(root, "A YEAR OF BUILDING", 28, total_height - 18, 10, muted,
          letter_spacing="1.6")
    for index, (top, _) in enumerate(colors[1:]):
        add(root, "rect", x=total_width - 95 + index * 16, y=total_height - 29,
            width="10", height="10", rx="3", fill=top)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)
    assert path.stat().st_size < 2_500_000
    print(f"Styled {path}: {path.stat().st_size:,} bytes")

if __name__ == "__main__":
    for path in Path("dist").glob("*.svg"):
        style(path)
