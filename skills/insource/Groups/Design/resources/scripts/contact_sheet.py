"""Review conformed slot files: compose them on a checkerboard and measure their edges.

`conform.py` proves the geometry. This script answers the two questions geometry cannot:

- **Do the edges look clean?** Transparency is invisible against white. Compositing every slot on
  a checkerboard shows halos, opaque corners and clipped subjects that a size check passes.
- **Did the background actually go away?** For an alpha asset the border should be transparent. A
  high share of opaque border pixels means keying was skipped or the subject genuinely fills the
  frame - the report says which, and the picture shows it.

It never edits the files it reads: this is a review step, not a processing step.

Usage:
    python scripts/contact_sheet.py assets/avatars --out review/avatars.png
    python scripts/contact_sheet.py assets/avatars --out review/avatars.png --skip-density
    python scripts/contact_sheet.py --files a.webp b.webp --out review/pair.png --columns 2
    python scripts/contact_sheet.py assets/avatars --json

Requires: pillow. Exit codes: 0 ok, 2 unreadable input or bad arguments.
"""

import argparse
import json
import sys
from pathlib import Path

EXTENSIONS = (".png", ".webp", ".jpg", ".jpeg", ".avif", ".gif", ".bmp", ".tif", ".tiff")
ALPHA = 8


class ReviewError(Exception):
    """An input that cannot be read, or arguments that cannot be composed."""


def _require_pillow():
    try:
        from PIL import Image  # noqa: F401
    except Exception:  # pragma: no cover - environment dependent
        raise SystemExit("contact_sheet: pillow is required (pip install pillow).")


def collect(folder=None, files=None, skip_density=False):
    """Paths to review, in the order they will be laid out."""
    paths = []
    if folder:
        root = Path(folder)
        if not root.is_dir():
            raise ReviewError(f"{folder} is not a folder")
        paths.extend(sorted(path for path in root.iterdir()
                            if path.is_file() and path.suffix.lower() in EXTENSIONS))
    for item in files or []:
        path = Path(item)
        if not path.is_file():
            raise ReviewError(f"{item} does not exist")
        paths.append(path)
    if skip_density:
        paths = [path for path in paths if "@" not in path.stem]
    if not paths:
        raise ReviewError("no image files matched - check the folder, --files or --skip-density")
    return paths


def analyse(path):
    """Facts about one delivered file, including what its border says about the background."""
    from PIL import Image

    with Image.open(path) as handle:
        handle.load()
        image = handle.copy()
    record = {
        "file": str(path),
        "name": path.stem,
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "bytes": path.stat().st_size,
        "alpha": False,
        "transparent_share": None,
        "corner_alpha": None,
        "border_opaque": None,
        "note": "",
    }
    if image.mode not in ("RGBA", "LA"):
        record["note"] = "no alpha channel - border colour was not measured"
        return record

    alpha = image.getchannel("A")
    low = alpha.getextrema()[0]
    record["alpha"] = low < 250

    width, height = image.size
    histogram = alpha.histogram()
    transparent = sum(histogram[: ALPHA + 1])
    record["transparent_share"] = round(transparent / (width * height), 4)
    record["corner_alpha"] = alpha.getpixel((0, 0))
    border = [alpha.getpixel((x, 0)) for x in range(width)]
    border += [alpha.getpixel((x, height - 1)) for x in range(width)]
    border += [alpha.getpixel((0, y)) for y in range(1, height - 1)]
    border += [alpha.getpixel((width - 1, y)) for y in range(1, height - 1)]
    opaque = sum(1 for value in border if value > ALPHA)
    record["border_opaque"] = round(opaque / len(border), 4)
    if not record["alpha"]:
        record["note"] = "alpha channel is fully opaque - nothing was keyed"
    elif record["border_opaque"] > 0.5:
        record["note"] = "border is mostly opaque - background not keyed, or a full-bleed subject"
    elif record["corner_alpha"] > ALPHA:
        record["note"] = "a corner is opaque - check for a leftover background patch"
    return record


def compose(records, out, tile=160, columns=5, gap=16, labels=True):
    """Write a checkerboard sheet: every slot at `tile` px, labelled by stem."""
    from PIL import Image, ImageDraw, ImageFont

    columns = max(1, min(columns, len(records)))
    rows = (len(records) + columns - 1) // columns
    font = ImageFont.load_default()
    label_height = 14 if labels else 0
    cell_height = tile + label_height + gap
    width = columns * (tile + gap) + gap
    height = rows * cell_height + gap
    canvas = Image.new("RGB", (width, height), (24, 24, 28))
    draw = ImageDraw.Draw(canvas)

    for index, record in enumerate(records):
        row, col = divmod(index, columns)
        x = gap + col * (tile + gap)
        y = gap + row * cell_height
        for cy in range(0, tile, 8):
            for cx in range(0, tile, 8):
                shade = (68, 68, 78) if ((cx // 8) + (cy // 8)) % 2 else (44, 44, 52)
                draw.rectangle((x + cx, y + cy, x + cx + 7, y + cy + 7), fill=shade)
        with Image.open(record["file"]) as handle:
            image = handle.convert("RGBA")
        image.thumbnail((tile, tile), Image.LANCZOS)
        canvas.paste(image, (x + (tile - image.width) // 2,
                             y + (tile - image.height) // 2), image)
        if labels:
            label = record["name"]
            while draw.textlength(label + "...", font=font) > tile and len(label) > 4:
                label = label[:-2]
            draw.text((x, y + tile + 2), label, fill=(210, 210, 220), font=font)

    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    return out


def build_report(records, sheet):
    flagged = [record for record in records
               if record["note"] and not record["note"].startswith("no alpha channel")]
    return {
        "sheet": str(sheet),
        "count": len(records),
        "tiles": [{"name": record["name"], "size": [record["width"], record["height"]],
                   "mode": record["mode"], "bytes": record["bytes"],
                   "alpha": record["alpha"],
                   "transparent_share": record["transparent_share"],
                   "corner_alpha": record["corner_alpha"],
                   "border_opaque": record["border_opaque"],
                   "note": record["note"]} for record in records],
        "flagged": [record["name"] for record in flagged],
        "ok": not flagged,
    }


def render(report):
    print(f"sheet     {report['sheet']}")
    print(f"tiles     {report['count']}")
    for tile in report["tiles"]:
        alpha = "-" if tile["transparent_share"] is None else f"{tile['transparent_share']:.1%}"
        border = "-" if tile["border_opaque"] is None else f"{tile['border_opaque']:.0%}"
        print(f"  {tile['name']:<24} {tile['size'][0]}x{tile['size'][1]} "
              f"{tile['mode']:<5} transparent {alpha:<6} border {border:<5} "
              f"{tile['note']}")
    if report["flagged"]:
        print(f"flagged   {', '.join(report['flagged'])}")
    else:
        print("flagged   none")


def build_parser():
    parser = argparse.ArgumentParser(
        description="Composite conformed slot files on a checkerboard and report their edges.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("folder", nargs="?", help="folder of delivered slot files")
    parser.add_argument("--files", nargs="+", help="explicit files instead of a folder")
    parser.add_argument("--out", help="contact sheet path (default: ./contact-sheet.png)")
    parser.add_argument("--tile", type=int, default=160, help="tile size in px (default: 160)")
    parser.add_argument("--columns", type=int, default=5, help="tiles per row (default: 5)")
    parser.add_argument("--gap", type=int, default=16, help="padding between tiles (default: 16)")
    parser.add_argument("--skip-density", action="store_true",
                        help="ignore @2x/@3x files, review the 1x ladder step only")
    parser.add_argument("--no-labels", dest="labels", action="store_false",
                        help="draw no filenames under the tiles")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.folder and not args.files:
        parser.error("pass a folder or --files")
    _require_pillow()
    try:
        paths = collect(args.folder, args.files, args.skip_density)
        records = [analyse(path) for path in paths]
        out = Path(args.out) if args.out else Path.cwd() / "contact-sheet.png"
        sheet = compose(records, out, args.tile, args.columns, args.gap, args.labels)
    except (ReviewError, OSError) as error:
        print(f"contact_sheet: {error}", file=sys.stderr)
        return 2
    report = build_report(records, sheet)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        render(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
