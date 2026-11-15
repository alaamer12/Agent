"""Probe a generated sheet before conforming it: what is on it, how the layout sits, what fits.

`conform.py` needs a plan and a delivery spec. This script measures the image so those numbers come
from the pixels instead of a guess:

- where the content is (bounds and margins) - cutting the canvas instead of the content is what
  clips the last column of an unevenly margined sheet;
- how the sheet is laid out: row by row, because a staggered or mixed sheet has no single grid and
  a global projection would report it as one column;
- which interior cut lines an even split would land on, so a plan is fixed before it writes files;
- how large the subjects are, which sets the real master ceiling;
- which delivery sizes at which DPRs that ceiling supports, and which it does not.

The report ends with the master spec to paste into the BOM (`1536x1024 sheet rows 8,8,8,10`).

Usage:
    python scripts/sheet_probe.py raw/avatars.png
    python scripts/sheet_probe.py raw/badges.png --json
    python scripts/sheet_probe.py raw/avatars.png --grid 5x2 --delivery "128x128 1:1 webp @1x,2x"

Requires: pillow. Exit codes: 0 ok, 2 unreadable image or bad arguments.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from sheet_geometry import (  # noqa: E402
    bands,
    cell_subjects,
    content_box,
    content_mask,
    feasibility,
    has_alpha,
    row_layout,
    split_boxes,
)


class ProbeError(Exception):
    """An image that cannot be read, or arguments that cannot be measured."""


def _require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except Exception:  # pragma: no cover - environment dependent
        raise SystemExit(
            "sheet_probe: pillow is required (pip install pillow)."
        )


def _subjects(layout):
    """Subject sizes straight from the band layout, so a staggered sheet is measured honestly."""
    sizes = []
    for row in layout["rows"]:
        for index, width in enumerate(row["sizes"]):
            height = row["height"]
            sizes.append((width, height))
    return sizes


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
    mask = content_mask(image, threshold)
    x_bands = bands(mask, "x")
    y_bands = bands(mask, "y")
    layout = row_layout(image, box, threshold)

    # A mixed or staggered sheet has one column count per row. Reporting `1 x rows` for it would
    # describe a grid nobody can cut, so the grid is only inferred when the rows agree.
    simple = layout["kind"] in ("regular", "empty") and layout["counts"]
    columns = columns if columns is not None else (layout["counts"][0] if simple else None)
    rows = rows if rows is not None else (len(layout["counts"]) if simple else None)
    cells = cell_subjects(image, box, columns, rows, threshold) if columns and rows else []
    subjects = _subjects(layout)
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
        "layout": {
            "kind": layout["kind"],
            "counts": layout["counts"],
            "subjects": layout["subjects"],
            "master": layout["master"],
            "clipped_cuts": layout["clipped_cuts"],
            "rows": layout["rows"],
        },
        "grid": (
            {"columns": columns, "rows": rows,
             "cell": [round((box[2] - box[0]) / columns),
                      round((box[3] - box[1]) / rows)]}
            if columns and rows else None
        ),
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
    layout = report["layout"]
    grid = report["grid"]
    if layout["kind"] == "mixed":
        notes.append(
            f"rows hold different column counts ({', '.join(str(c) for c in layout['counts'])}) "
            f"- no single grid describes this sheet; plan `{layout['master']}`"
        )
    elif layout["kind"] == "staggered":
        notes.append(
            "rows do not line up - an even column split will clip; plan "
            f"`{layout['master']}` and cut on the measured gutters (`--bands`)"
        )
    if not report["columns"]["regular"] or not report["rows"]["regular"]:
        notes.append("gutters are uneven - cut on the measured bands, not an even grid")
    if layout["clipped_cuts"]:
        where = ", ".join(f"{cut['axis']}={cut['at']}" for cut in layout["clipped_cuts"][:4])
        notes.append(
            f"{len(layout['clipped_cuts'])} interior cut line(s) of an even split land on content "
            f"({where}) - cut on the measured gutters instead"
        )
    if report["empty_cells"]:
        notes.append(f"{len(report['empty_cells'])} cell(s) look empty: "
                     f"{report['empty_cells']}")
    if grid and report["columns"]["count"] not in (0, grid["columns"]):
        notes.append(f"the image shows {report['columns']['count']} column band(s), the grid "
                     f"says {grid['columns']} - some subjects may be touching")
    if grid and report["rows"]["count"] not in (0, grid["rows"]):
        notes.append(f"the image shows {report['rows']['count']} row band(s), the grid "
                     f"says {grid['rows']}")
    if report["margins"]["left"] != report["margins"]["right"]:
        notes.append(f"left/right margins differ ({report['margins']['left']} vs "
                     f"{report['margins']['right']}): cutting the canvas would shift the grid")
    if not notes:
        notes.append("grid and content look regular - a content-box cut will separate the "
                     "subjects")
    return notes


def render(report):
    layout = report["layout"]
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
    print(f"layout    {layout['kind']} - {layout['subjects']} subject(s), rows "
          f"{','.join(str(count) for count in layout['counts']) or 'none'}")
    if report["grid"]:
        grid = report["grid"]
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
    if layout["master"]:
        print(f"master    {layout['master']}")
    if layout["clipped_cuts"]:
        print(f"clips     {len(layout['clipped_cuts'])} interior cut line(s) of an even split "
              "land on content")
    for note in report["verdict"]:
        print(f"note      {note}")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Measure a generated sheet: content bounds, layout, per-row columns, cut "
                    "lines, cell sizes, deliverable resolutions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("sheet", help="the generated sheet to measure")
    parser.add_argument("--grid", help="expected grid COLSxROWS (default: inferred when the rows "
                                       "agree, otherwise the measured row layout)")
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
