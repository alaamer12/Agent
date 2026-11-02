"""Optimize images and produce width variants, reporting before/after sizes for every file.

Jobs:
  optimize   re-encode one image or a directory to WebP/JPEG (or keep the format), optionally
             downscaling past --max-width.
  variants   emit several widths (e.g. 320,640,1280) of each source: <name>-320.webp, ...
  thumbs     emit a small preview per source: <name>-thumb.webp (default 240px wide)

Every run ends with a per-file report - source size, output size(s), the saving, and totals - so the
result is a number the agent can quote, not a claim of "optimized".

This script is for images. Audio, video, fonts and documents are governed by the same rules
(naming, placement, one source of truth) with medium-specific guidance in references/05-optimization.md;
this script does not pretend to re-encode them.

Usage:
    python scripts/optimize.py --in assets/raw --out assets/build --format webp --quality 80 --max-width 1600
    python scripts/optimize.py --in hero.jpg --variants 320,640,1280 --out assets/build
    python scripts/optimize.py --in gallery/ --thumbs --out assets/thumbs

Requires: pillow.
"""

import argparse
import os
import sys

from PIL import Image

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
TARGETS = {"keep": None, "webp": "WEBP", "jpeg": "JPEG", "png": "PNG"}


def parse_sizes(value):
    try:
        return sorted({int(part) for part in value.split(",") if part.strip()})
    except ValueError:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers")


def load_image(path):
    with Image.open(path) as image:
        return image.convert("RGBA") if image.mode in ("RGBA", "LA", "P") else image.convert("RGB")


def save(image, path, fmt, quality):
    if fmt == "JPEG" and image.mode == "RGBA":
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[-1])
        image = background
    options = {"quality": quality} if fmt in ("WEBP", "JPEG") else {}
    image.save(path, format=fmt, **options)


def scaled(image, width=None, max_width=None):
    target = width or (min(image.size[0], max_width) if max_width else image.size[0])
    if target >= image.size[0]:
        return image
    height = max(1, round(image.size[1] * target / image.size[0]))
    return image.resize((target, height), Image.LANCZOS)


def process(path, args, report):
    image = load_image(path)
    stem = os.path.splitext(os.path.basename(path))[0]
    base_format = TARGETS[args.format] or ("PNG" if image.mode == "RGBA" else "JPEG")
    extension = {"WEBP": "webp", "JPEG": "jpg", "PNG": "png"}[base_format]
    before = os.path.getsize(path)
    outputs = []

    def emit(img, name):
        out = os.path.join(args.out, name)
        save(img, out, base_format, args.quality)
        outputs.append(out)

    if args.variants:
        for width in args.variants:
            emit(scaled(image, width=width), "%s-%d.%s" % (stem, width, extension))
    elif args.thumbs:
        emit(scaled(image, width=args.thumb_width), "%s-thumb.%s" % (stem, extension))
    else:
        out = os.path.join(args.out, "%s.%s" % (stem, extension))
        save(scaled(image, max_width=args.max_width), out, base_format, args.quality)
        outputs.append(out)

    report.append((path, before, [(p, os.path.getsize(p)) for p in outputs]))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True, help="image or directory")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--format", choices=sorted(TARGETS), default="webp", help="target format (default webp)")
    parser.add_argument("--quality", type=int, default=80, help="JPEG/WebP quality (default 80)")
    parser.add_argument("--max-width", type=int, default=None, help="downscale if wider than this")
    parser.add_argument("--variants", type=parse_sizes, default=None, help="widths, e.g. 320,640,1280")
    parser.add_argument("--thumbs", action="store_true", help="emit one small preview per source")
    parser.add_argument("--thumb-width", type=int, default=240, help="thumbnail width (default 240)")
    args = parser.parse_args(argv)

    os.makedirs(args.out, exist_ok=True)
    report = []

    if os.path.isdir(args.src):
        for name in sorted(os.listdir(args.src)):
            path = os.path.join(args.src, name)
            if os.path.isfile(path) and os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS:
                process(path, args, report)
    else:
        process(args.src, args, report)

    if not report:
        print("nothing to do: no image files found in %s" % args.src)
        return 1

    before_total = after_total = 0
    print("%-42s %10s %10s %8s" % ("source", "before", "after", "saved"))
    print("-" * 74)
    for source, before, outputs in report:
        after = sum(size for _, size in outputs)
        before_total += before
        after_total += after
        saved = 100.0 * (before - after) / before if before else 0.0
        print("%-42s %10d %10d %7.1f%%" % (os.path.basename(source), before, after, saved))
        for path, size in outputs:
            print("    -> %-42s %10d" % (os.path.relpath(path, args.out), size))
    print("-" * 74)
    saved = 100.0 * (before_total - after_total) / before_total if before_total else 0.0
    print("%-42s %10d %10d %7.1f%%" % ("TOTAL (%d file(s))" % len(report), before_total, after_total, saved))
    print("out : %s" % os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
