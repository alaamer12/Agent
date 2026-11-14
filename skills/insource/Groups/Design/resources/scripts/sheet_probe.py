"""Probe a generated sheet before conforming it: what is on it, how the grid sits, what fits.

`conform.py` needs a grid and a delivery spec. This script measures the sheet so those numbers
come from the image instead of a guess:

- where the content is (bounds and margins) - cutting the canvas instead of the content is what
  clips the last column of an unevenly margined sheet;
- how many subject bands the image actually has, per axis, and how wide the gaps are;
- where the gutters are, so a cut line can be placed inside one;
- how large the subjects are after trimming, which sets the real master ceiling;
- which delivery sizes at which DPRs that ceiling supports, and which it does not.

Usage:
    python scripts/sheet_probe.py raw/avatars.png
    python scripts/sheet_probe.py raw/avatars.png --json
    python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"

Requires: pillow. Exit codes: 0 ok, 2 unreadable image or bad arguments.
"""

import argparse
import json
import statistics
import sys
from dataclasses import dataclass, field
from pathlib import Path

COMFORTABLE = (64, 96, 128, 192, 256, 384, 512)
LEVELS = (1, 2, 3, 4)


class ProbeError(Exception):
    """An image that cannot be read, or arguments that cannot be measured."""


@dataclass
class Bands:
    count: int = 0
    starts: list = field(default_factory=list)
    ends: list = field(default_factory=list)
    sizes: list = field(default_factory=list)
    gaps: list = field(default_factory=list)

    @property
    def regular(self):
        if len(self.gaps) < 2:
            return True
        median = statistics.median(self.gaps)
        return all(abs(gap - median) <= max(4, median * 0.25) for gap in self.gaps)

    def as_dict(self):
        return {
            "count": self.count,
            "starts": self.starts,
            "ends": self.ends,
            "sizes": self.sizes,
            "gaps": self.gaps,
            "regular": self.regular,
        }


def _require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except Exception:  # pragma: no cover - environment dependent
        raise SystemExit(
            "sheet_probe: pillow is required (pip install pillow)."
        )


def has_alpha(image):
    return image.mode in ("RGBA", "LA") and image.getchannel("A").getextrema()[0] < 250


def content_mask(image, threshold=8):
    """An L mask: 255 where a subject is, 0 where the background is."""
    from PIL import Image, ImageChops

    if has_alpha(image):
        alpha = image.getchannel("A")
        return alpha.point(lambda value: 255 if value > threshold else 0)
    rgb = image.convert("RGB")
    background = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
    return ImageChops.difference(rgb, background).convert("L").point(
        lambda value: 255 if value > threshold else 0
    )


def content_box(image, threshold=8):
    mask = content_mask(image, threshold)
    return mask.getbbox() or (0, 0, image.width, image.height)


def bands(mask, axis, limit=400):
    """Contiguous runs of content along `axis`, measured on a downscaled projection."""
    from PIL import Image

    width, height = mask.size
    scale = min(1.0, limit / max(width, height))
    small = mask.resize((max(1, round(width * scale)), max(1, round(height * scale))),
                        Image.BOX) if scale < 1 else mask
    pixels = small.load()
    small_w, small_h = small.size
    if axis == "x":
        hits = [any(pixels[x, y] > 8 for y in range(small_h)) for x in range(small_w)]
    else:
        hits = [any(pixels[x, y] > 8 for x in range(small_w)) for y in range(small_h)]
    found = Bands()
    start = None
    for index, hit in enumerate(hits):
        if hit and start is None:
            start = index
        elif not hit and start is not None:
            found.starts.append(round(start / scale))
            found.ends.append(round(index / scale))
            found.sizes.append(round((index - start) / scale))
            start = None
    if start is not None:
        found.starts.append(round(start / scale))
        found.ends.append(round(len(hits) / scale))
        found.sizes.append(round((len(hits) - start) / scale))
    found.count = len(found.starts)
    for index in range(len(found.ends) - 1):
        found.gaps.append(found.starts[index + 1] - found.ends[index])
    return found


def split_boxes(box, columns, rows):
    """Evenly divide a box, distributing the remainder - the same rule conform uses."""
    left, top, right, bottom = box
    xs = [left + round(index * (right - left) / columns) for index in range(columns + 1)]
    ys = [top + round(index * (bottom - top) / rows) for index in range(rows + 1)]
    return [(xs[col], ys[row], xs[col + 1], ys[row + 1])
            for row in range(rows) for col in range(columns)]


def cell_subjects(image, box, columns, rows, threshold=8):
    """Subject bbox (relative to each cell) and whether the cell is empty."""
    mask = content_mask(image, threshold)
    cells = []
    for index, cell in enumerate(split_boxes(box, columns, rows)):
        piece = mask.crop(cell)
        found = piece.getbbox()
        cells.append({
            "index": index,
            "box": list(cell),
            "subject": list(found) if found else None,
            "size": [found[2] - found[0], found[3] - found[1]] if found else [0, 0],
            "empty": found is None,
        })
    return cells


def feasibility(ceiling, delivery=None):
    """Which (size, dpr) pairs a square master of `ceiling` can serve."""
    fits = {}
    for size in COMFORTABLE:
        levels = [level for level in LEVELS if size * level <= ceiling]
        if levels:
            fits[size] = levels
    out = {"max_square_master": ceiling, "fits": fits, "rejected": {}}
    for size in COMFORTABLE:
        if size in fits:
            continue
        out["rejected"][size] = f"needs {size}x{size} at 1x, ceiling is {ceiling}"
    if delivery:
        out["delivery"] = delivery
    return out


def probe(path, columns=None, rows=None, delivery=None, threshold=8):
    _require_pillow()
    from PIL import Image

    source = Path(path)
    if not source.exists():
        raise ProbeError(f"{path} does not exist")
    try:
        with Image.open(source) as handle:
            handle.load()
            image = handle.copy()
    except Exception as error:
        raise ProbeError(f"{path} is not a readable image: {error}")

    box = content_box(image, threshold)
    x_bands = bands(content_mask(image, threshold), "x")
    y_bands = bands(content_mask(image, threshold), "y")
    columns = columns or x_bands.count or 1
    rows = rows or y_bands.count or 1
    cells = cell_subjects(image, box, columns, rows, threshold)
    subjects = [cell["size"] for cell in cells if not cell["empty"]]
    ceiling = min((min(size) for size in subjects), default=0)

    report = {
        "sheet": str(source),
        "size": [image.width, image.height],
        "mode": image.mode,
        "has_alpha": has_alpha(image),
        "background": list(image.convert("RGB").getpixel((0, 0))),
        "content_box": list(box),
        "margins": {
            "left": box[0],
            "top": box[1],
            "right": image.width - box[2],
            "bottom": image.height - box[3],
        },
        "columns": x_bands.as_dict(),
        "rows": y_bands.as_dict(),
        "grid": {"columns": columns, "rows": rows,
                 "cell": [round((box[2] - box[0]) / columns),
                          round((box[3] - box[1]) / rows)]},
        "cells": cells,
        "empty_cells": [cell["index"] for cell in cells if cell["empty"]],
        "subject": {
            "count": len(subjects),
            "min": [min(size[index] for size in subjects) for index in (0, 1)] if subjects else [0, 0],
            "max": [max(size[index] for size in subjects) for index in (0, 1)] if subjects else [0, 0],
        },
        "master_ceiling": ceiling,
        "delivery_ceiling": feasibility(ceiling, delivery),
    }
    report["verdict"] = _verdict(report)
    return report


def _verdict(report):
    notes = []
    columns, rows = report["grid"]["columns"], report["grid"]["rows"]
    if not report["columns"]["regular"] or not report["rows"]["regular"]:
        notes.append("gutters are uneven - cut on the measured bands, not an even grid")
    if report["empty_cells"]:
        notes.append(f"{len(report['empty_cells'])} cell(s) look empty: "
                     f"{report['empty_cells']}")
    if report["columns"]["count"] not in (0, columns):
        notes.append(f"the image shows {report['columns']['count']} column band(s), the grid "
                     f"says {columns} - some subjects may be touching")
    if report["rows"]["count"] not in (0, rows):
        notes.append(f"the image shows {report['rows']['count']} row band(s), the grid "
                     f"says {rows}")
    if report["margins"]["left"] != report["margins"]["right"]:
        notes.append(f"left/right margins differ ({report['margins']['left']} vs "
                     f"{report['margins']['right']}): cutting the canvas would shift the grid")
    if not notes:
        notes.append("grid and content look regular - a content-box cut will separate the "
                     "subjects")
    return notes


def render(report):
    grid = report["grid"]
    delivery = report["delivery_ceiling"]
    print(f"sheet     {report['sheet']}")
    print(f"size      {report['size'][0]}x{report['size'][1]} {report['mode']} "
          f"alpha={'yes' if report['has_alpha'] else 'no'} "
          f"background={tuple(report['background'])}")
    print(f"content   {report['content_box']}  margins "
          + " ".join(f"{key}={value}" for key, value in report["margins"].items()))
    print(f"columns   {report['columns']['count']} band(s) gaps {report['columns']['gaps']}"
          f"{'' if report['columns']['regular'] else '  (uneven)'}")
    print(f"rows      {report['rows']['count']} band(s) gaps {report['rows']['gaps']}"
          f"{'' if report['rows']['regular'] else '  (uneven)'}")
    print(f"grid      {grid['columns']}x{grid['rows']} cells about "
          f"{grid['cell'][0]}x{grid['cell'][1]}")
    print(f"subjects  {report['subject']['count']} found, min "
          f"{report['subject']['min'][0]}x{report['subject']['min'][1]}, max "
          f"{report['subject']['max'][0]}x{report['subject']['max'][1]}")
    if report["empty_cells"]:
        print(f"empty     cells {report['empty_cells']}")
    print(f"ceiling   {delivery['max_square_master']}px square master")
    ladder = "  ".join(
        f"{size}@" + ",".join(f"{level}x" for level in levels)
        for size, levels in delivery["fits"].items()
    )
    print(f"delivers  {ladder or 'nothing - the sheet is too small'}")
    for note in report["verdict"]:
        print(f"note      {note}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Measure a generated sheet: content bounds, bands, cell sizes, "
                    "deliverable resolutions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sheet", help="the generated sheet to measure")
    parser.add_argument("--grid", help="expected grid COLSxROWS (default: the measured bands)")
    parser.add_argument("--delivery", help="delivery spec to test, e.g. '128x128 1:1 webp @1x,2x'")
    parser.add_argument("--threshold", type=int, default=8,
                        help="pixel difference treated as subject (default: 8)")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    columns = rows = None
    if args.grid:
        try:
            columns, rows = (int(part) for part in args.grid.lower().split("x"))
        except ValueError:
            parser.error("--grid must be COLSxROWS, e.g. 5x2")
    try:
        report = probe(args.sheet, columns, rows, args.delivery, args.threshold)
    except ProbeError as error:
        print(f"sheet_probe: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        render(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
