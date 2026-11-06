#!/usr/bin/env python3
"""Compare a render against the reference: panels + numeric score + worst regions.

  python scripts/compare.py ref.png render.png --ref-box 95,15,195,100 \
         [--render-box x0,y0,x1,y1] [--ignore x0,y0,x1,y1 ...] [--grid 4] --out compare.png

Panels: reference | render | 50% blend | difference. Boxes are in each image's own pixels.
--ignore marks regions of the REFERENCE (original pixel coords) that are out of scope
(surrounding interface elements, text, badges). They are blanked and excluded from the score.
Output: MAE (0 = identical, lower is better) and the grid cells with the largest error,
so each iteration can target the worst region instead of guessing.
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw


def box(s):
    return tuple(int(float(v)) for v in s.split(","))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ref")
    ap.add_argument("render")
    ap.add_argument("--ref-box")
    ap.add_argument("--render-box")
    ap.add_argument("--ignore", action="append", default=[])
    ap.add_argument("--height", type=int, default=600, help="panel height in px")
    ap.add_argument("--grid", type=int, default=4, help="N x N grid for worst-region report")
    ap.add_argument("--out", default="compare.png")
    a = ap.parse_args()

    ref = Image.open(a.ref).convert("RGB")
    ren = Image.open(a.render).convert("RGB")
    rb = box(a.ref_box) if a.ref_box else (0, 0, ref.width, ref.height)
    nb = box(a.render_box) if a.render_box else (0, 0, ren.width, ren.height)
    ref_c, ren_c = ref.crop(rb), ren.crop(nb)

    h = a.height
    w = max(1, round(ref_c.width * h / ref_c.height))
    ref_p = ref_c.resize((w, h), Image.LANCZOS)
    ren_p = ren_c.resize((w, h), Image.LANCZOS)

    keep = np.ones((h, w), bool)
    sx, sy = w / (rb[2] - rb[0]), h / (rb[3] - rb[1])
    for s in a.ignore:
        x0, y0, x1, y1 = box(s)
        keep[max(0, int((y0 - rb[1]) * sy)):max(0, int((y1 - rb[1]) * sy)),
             max(0, int((x0 - rb[0]) * sx)):max(0, int((x1 - rb[0]) * sx))] = False

    A = np.asarray(ref_p, np.float32)
    B = np.asarray(ren_p, np.float32)
    err = np.abs(A - B).mean(axis=2)                       # per-pixel error 0..255
    mae = err[keep].mean() if keep.any() else 0.0

    blend = Image.blend(ref_p, ren_p, 0.5)
    diff = Image.fromarray(np.clip(err * 3, 0, 255).astype(np.uint8)).convert("RGB")
    panels = [ref_p, ren_p, blend, diff]
    grey = Image.new("RGB", (w, h), (200, 200, 200))
    for i, p in enumerate(panels):
        panels[i] = Image.composite(p, grey, Image.fromarray((keep * 255).astype(np.uint8)))

    gap = 10
    sheet = Image.new("RGB", (w * 4 + gap * 3, h + 22), "white")
    d = ImageDraw.Draw(sheet)
    for i, (p, label) in enumerate(zip(panels, ["reference", "render", "blend", "difference x3"])):
        sheet.paste(p, (i * (w + gap), 22))
        d.text((i * (w + gap) + 4, 4), label, fill=(0, 0, 0))
    sheet.save(a.out)

    n = a.grid
    cells = []
    for r in range(n):
        for c in range(n):
            ys, ye, xs, xe = r * h // n, (r + 1) * h // n, c * w // n, (c + 1) * w // n
            m = keep[ys:ye, xs:xe]
            if m.any():
                cells.append((err[ys:ye, xs:xe][m].mean(), r, c))
    cells.sort(reverse=True)
    print(f"MAE = {mae:.2f}  (0 = identical; judge progress by the trend between rounds, not the absolute value)")
    print("worst regions (row, col of the %dx%d grid; row 0 = top):" % (n, n))
    for e, r, c in cells[:4]:
        print(f"  row {r} col {c}: {e:.1f}")
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
