"""Convert image formats, or repair a file whose extension lies about its content.

Two jobs:

  convert   re-encode an image into another format (png, jpeg, webp, bmp, gif, tiff, ico).
            Transparency is preserved where the target supports it; converting to JPEG flattens
            transparency onto white, because JPEG has none.
  fix       detect the real format from the file's bytes and rename the file to match its actual
            extension - no re-encoding, no pixel changes. A PNG named ".jpg" stops being a lie.

Raster targets only. SVG is reported, never converted: rasterizing or vectorizing SVG needs a
dedicated toolchain (e.g. cairosvg/resvg for raster, potrace-style tracing for the reverse) - this
script does neither silently.

Usage:
    python scripts/convert.py --in photo.jpg --to webp --out photo.webp --quality 82
    python scripts/convert.py --in banner.png --to ico
    python scripts/convert.py --fix --in assets/ --recursive

Requires: pillow.
"""

import argparse
import os
import sys

from PIL import Image

RASTER_FORMATS = {
    "png": "PNG",
    "jpeg": "JPEG",
    "jpg": "JPEG",
    "webp": "WEBP",
    "bmp": "BMP",
    "gif": "GIF",
    "tiff": "TIFF",
    "ico": "ICO",
}
# PIL's canonical name -> the extension we use on disk
EXTENSION_OF = {"PNG": "png", "JPEG": "jpg", "WEBP": "webp", "BMP": "bmp", "GIF": "gif",
                "TIFF": "tiff", "ICO": "ico", "MPO": "jpg", "PPM": "ppm"}


def detect_format(path):
    with Image.open(path) as image:
        return image.format


def convert(src, dst_format, dst_path, quality):
    target = RASTER_FORMATS[dst_format.lower()]
    with Image.open(src) as image:
        if target == "ICO":
            # ICO wants square, bounded sizes; let Pillow derive them from the largest edge.
            side = min(256, max(image.size))
            image = image.convert("RGBA").resize((side, side), Image.LANCZOS)
            image.save(dst_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (side, side)])
            return
        has_alpha = image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info)
        image = image.convert("RGBA" if has_alpha else "RGB")
        options = {}
        if target == "JPEG":
            # JPEG has no alpha: flatten onto white rather than letting Pillow error out.
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == "RGBA" else None)
            image = background
        if target in ("JPEG", "WEBP"):
            options["quality"] = int(quality)
        image.save(dst_path, format=target, **options)


def fix_extension(path):
    actual = detect_format(path)
    if actual is None:
        return False, "unrecognized"
    extension = EXTENSION_OF.get(actual)
    if extension is None:
        return False, "format %s has no mapping" % actual
    current = os.path.splitext(path)[1].lower().lstrip(".")
    normalized = "jpg" if current == "jpeg" else current
    if normalized == extension:
        return False, "ok (%s)" % actual
    target = os.path.splitext(path)[0] + "." + extension
    if os.path.exists(target):
        return False, "refused: %s already exists" % target
    os.rename(path, target)
    return True, "%s -> %s (%s)" % (os.path.basename(path), os.path.basename(target), actual)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--in", dest="src", required=True, help="input file or directory")
    parser.add_argument("--to", choices=sorted(RASTER_FORMATS), default=None, help="target format (convert mode)")
    parser.add_argument("--out", dest="dst", default=None,
                        help="output path; default: same name with the new extension")
    parser.add_argument("--quality", type=int, default=85, help="JPEG/WebP quality (default 85)")
    parser.add_argument("--fix", action="store_true", help="rename files to match their real format")
    parser.add_argument("--recursive", action="store_true", help="with --fix, walk subdirectories")
    args = parser.parse_args(argv)

    if args.fix:
        if not os.path.isdir(args.src):
            changed, note = fix_extension(args.src)
            print("%s: %s" % (args.src, note))
            return 0 if changed or note.startswith("ok") else 1
        walked = []
        for root, dirs, files in os.walk(args.src):
            if not args.recursive:
                dirs[:] = []
            for name in sorted(files):
                if os.path.splitext(name)[1].lower() in (".png", ".jpg", ".jpeg", ".webp", ".bmp",
                                                          ".gif", ".tif", ".tiff", ".ico"):
                    walked.append((os.path.join(root, name), fix_extension(os.path.join(root, name))))
        renames = 0
        for path, (changed, note) in walked:
            print("%s: %s" % (path, note))
            renames += 1 if changed else 0
        print("renamed: %d of %d files" % (renames, len(walked)))
        return 0

    if args.to is None:
        parser.error("either --to <format> or --fix is required")
    if not os.path.isfile(args.src):
        parser.error("convert needs a single input file, not a directory")

    dst = args.dst or os.path.splitext(args.src)[0] + "." + ("jpg" if args.to in ("jpeg", "jpg") else args.to)
    before = os.path.getsize(args.src)
    convert(args.src, args.to, dst, args.quality)
    after = os.path.getsize(dst)
    saved = 100.0 * (before - after) / before if before else 0.0
    print("in  : %s (%d bytes)" % (args.src, before))
    print("out : %s (%s, quality %s, %d bytes, %+.1f%%)" % (dst, args.to, args.quality, after, -saved))
    return 0


if __name__ == "__main__":
    sys.exit(main())
