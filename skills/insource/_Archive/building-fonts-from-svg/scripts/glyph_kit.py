"""Path primitives for generating glyph SVGs from code.

Every function returns an SVG path 'd' string, on a shared grid so letters
drawn with different primitives still line up in the font.
Default grid: y=0 is cap-height, y=700 is the baseline, x starts at 0.

    from glyph_kit import bar, ribbon, burst, poly, write_glyph
    write_glyph("svgs", "T", [bar(0, 0, 560, 0), bar(280, 0, 280, 700)])

Set jag=0 for clean geometric strokes; raise it for a fractured/shard look.
"""
import math
import os
import random

CAP_HEIGHT = 700
DEFAULT_WIDTH = 620


def _d(points):
    head, *rest = points
    return (f"M {head[0]:.1f} {head[1]:.1f} "
            + " ".join(f"L {x:.1f} {y:.1f}" for x, y in rest) + " Z")


def poly(points):
    """Closed polygon through the given (x, y) points."""
    return _d(points)


def ribbon(points, width=90, jag=0, seed=0):
    """Stroke of nominal `width` along a polyline spine.

    Each side of the spine is pushed in/out by a random amount up to `jag`
    (reproducible via `seed`). Follows corners, so use it for bends and bowls.
    """
    rnd = random.Random(seed)
    left, right = [], []
    n = len(points)
    for i, (x, y) in enumerate(points):
        a = points[max(i - 1, 0)]
        b = points[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1.0
        px, py = -dy / length, dx / length          # unit normal to the spine
        wl = width / 2 + (rnd.uniform(-jag, jag) if jag else 0)
        wr = width / 2 + (rnd.uniform(-jag, jag) if jag else 0)
        left.append((x + px * wl, y + py * wl))
        right.append((x - px * wr, y - py * wr))
    return _d(left + right[::-1])


def bar(x0, y0, x1, y1, width=90, jag=0, seed=0):
    """Straight stroke between two points."""
    return ribbon([(x0, y0), (x1, y1)], width, jag, seed)


def burst(cx, cy, r, points=3, seed=0, rot=0):
    """Spiky star-like accent centred on (cx, cy) with outer radius r."""
    rnd = random.Random(seed)
    pts = []
    for i in range(points * 2):
        rad = r if i % 2 == 0 else r * rnd.uniform(0.35, 0.55)
        rad *= rnd.uniform(0.85, 1.1)
        a = math.radians(i * 180 / points - 90 + rot)
        pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
    return _d(pts)


def svg_wrap(paths, width=DEFAULT_WIDTH, height=CAP_HEIGHT, evenodd=False):
    """Wrap path strings in an SVG document.

    Overlapping strokes are fine: the font builder unions them. Pass
    evenodd=True only when one path deliberately contains holes as extra
    sub-contours (a hand-drawn 'B' or 'O').
    """
    rule = ' fill-rule="evenodd"' if evenodd else ""
    body = "\n  ".join(f'<path d="{d}"{rule}/>' for d in paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {width} {height}">\n  {body}\n</svg>\n')


def filename_for(char):
    """Case-safe file stem: 'A' -> 'uni0041'. Avoids a.svg / A.svg collisions
    on case-insensitive filesystems (Windows, macOS)."""
    return f"uni{ord(char):04X}"


def write_glyph(out_dir, char, paths, **wrap_kwargs):
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, filename_for(char) + ".svg")
    with open(path, "w") as f:
        f.write(svg_wrap(paths, **wrap_kwargs))
    return path
