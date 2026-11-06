#!/usr/bin/env python3
"""revoke_image.py - pixel-level redaction mechanics for the revoke skill.

Deterministic plumbing only: WHICH regions and WHICH treatment is the agent's
judgment (see ../references/08-image-redaction.md); this script applies a
region spec, flattens into the raster, strips metadata and embedded
thumbnails, handles every frame of animated/multi-frame files, and refuses to
touch the original. Needs Pillow; if missing, create a project-local venv:
    python -m venv .venv && .venv/Scripts/pip install pillow   (Windows)
    python3 -m venv .venv && .venv/bin/pip install pillow      (unix)
Exit codes: 0 ok, 1 findings/warnings in check, 2 usage or environment error.
On Windows use `python`, not `python3`. Output is ASCII.
"""
import json
import sys

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
except ImportError:
    sys.stderr.write(
        "error: Pillow is required for pixel work and is not importable.\n"
        "install it in a PROJECT-LOCAL virtualenv (never the global interpreter):\n"
        "  python -m venv .venv && .venv/Scripts/pip install pillow    (Windows)\n"
        "  python3 -m venv .venv && .venv/bin/pip install pillow       (unix)\n"
        "or use another tool that meets the same obligations (opaque paint,\n"
        "flatten, strip metadata, every frame) - see the reference.\n")
    sys.exit(2)

META_KEYS = ("exif", "xmp_metadata", "icc_profile", "info")


def open_frames(path):
    """All frames of an animated/multi-frame image, as RGBA, frame-count honest."""
    im = Image.open(path)
    frames = []
    n = getattr(im, "n_frames", 1)
    for i in range(n):
        im.seek(i)
        frames.append(im.convert("RGBA"))
    return frames, n


def edge_median_color(img, box, pad=6):
    """Dominant ring color just outside the region: blocks read intentional."""
    x0, y0, x1, y1 = box
    w, h = img.size
    ring = Image.new("RGBA", img.size, (0, 0, 0, 0))
    m = Image.new("1", img.size, 0)
    d = ImageDraw.Draw(m)
    d.rectangle([max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)], fill=1)
    d.rectangle(box, fill=0)
    masked = Image.composite(img, Image.new("RGBA", img.size, (0, 0, 0, 0)), m)
    pxl = masked.load()
    w2, h2 = masked.size
    px = [pxl[x, y] for y in range(0, h2, 4) for x in range(0, w2, 4) if pxl[x, y][3] > 0]
    if not px:
        return (0, 0, 0, 255)
    counts = {}
    for p in px:
        key = (p[0] // 8 * 8, p[1] // 8 * 8, p[2] // 8 * 8)
        counts[key] = counts.get(key, 0) + 1
    best = max(counts.items(), key=lambda kv: kv[1])[0]
    return best + (255,)


def apply_region(frame, region):
    x, y, w, h = region["region"]
    pad = int(region.get("pad", 4))
    box = (max(0, x - pad), max(0, y - pad), x + w + pad, y + h + pad)
    mode = region["mode"]
    if mode == "block":
        color = region.get("color", "auto")
        if color in ("auto", "bg"):
            color = edge_median_color(frame, box)
        elif isinstance(color, str) and color.startswith("#"):
            color = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5)) + (255,)
        ImageDraw.Draw(frame).rectangle(box, fill=tuple(color))
    elif mode == "mosaic":
        grid = max(8, int(region.get("grid", 24)))
        crop = frame.crop(box)
        fw, fh = max(1, box[2] - box[0]), max(1, box[3] - box[1])
        small = crop.resize((max(1, fw // grid), max(1, fh // grid)))
        frame.paste(small.resize((fw, fh), Image.NEAREST), (box[0], box[1]))
    elif mode == "blur":
        crop = frame.crop(box)
        r = int(region.get("radius", 12))
        frame.paste(crop.filter(ImageFilter.GaussianBlur(r)), (box[0], box[1]))
        print("  warning: blur is de-identification, not revocation - deconvolution")
        print("           and embedding matchers undo it; record it as such, or use block")
    else:
        raise ValueError("unknown mode %r (block|mosaic|blur)" % mode)
    return frame


def redact(in_path, out_path, spec_path):
    if in_path == out_path:
        sys.stderr.write("error: refusing to write over the original; the source stays intact\n")
        return 2
    with open(spec_path, encoding="utf-8") as fh:
        spec = json.load(fh)
    regions = spec["regions"] if isinstance(spec, dict) else spec
    frames, n = open_frames(in_path)
    if n > 1:
        print("  %d frames: applying spec to EVERY frame" % n)
    out_frames = []
    for f in frames:
        for r in regions:
            f = apply_region(f, dict(r))
        out_frames.append(ImageOps.exif_transpose(f))
    save(out_frames, in_path, out_path)
    print("redacted %s -> %s (%d frame(s), %d region(s), metadata not carried over)"
          % (in_path, out_path, len(out_frames), len(regions)))
    return 0


def save(frames, in_path, out_path):
    fmt = (out_path.rsplit(".", 1)[-1] or "png").upper()
    if fmt in ("JPG", "JPEG"):
        frames[0].convert("RGB").save(out_path, "JPEG", quality=92)  # no exif= -> stripped
    elif len(frames) > 1:
        frames[0].save(out_path, save_all=True, append_images=frames[1:], loop=0)
    elif fmt == "PNG":
        frames[0].save(out_path, "PNG")  # fresh PNG: no info dict copied
    else:
        frames[0].save(out_path)
    return out_path


def has_embedded_thumbnail(im):
    """EXIF thumbnail IFD (0x0100) with image data pointer (0x0201) - the classic
    'redacted view, original bytes inside' bypass. JPEG-family only."""
    try:
        ifd = im.getexif().get_ifd(0x8769)
    except Exception:
        return False
    return bool(ifd) and 0x0201 in ifd


def info(path):
    frames, n = open_frames(path)
    im = Image.open(path)
    print("%s: %dx%d, format=%s mode=%s frames=%d" % (path, *im.size, im.format, im.mode, n))
    leaked = []
    exif = im.getexif()
    if exif:
        tags = {hex(k): str(v)[:60] for k, v in exif.items()}
        leaked.append("exif tags: %d" % len(tags))
    for key in ("xmp_metadata", "icc_profile"):
        if im.info.get(key):
            leaked.append(key)
    text = {k: v for k, v in im.info.items() if isinstance(v, str) and k not in ("transparency",)}
    if text:
        leaked.append("text chunks: %s" % (sorted(text)[:8],))
    if has_embedded_thumbnail(im):
        leaked.append("embedded EXIF thumbnail present (often holds the ORIGINAL pixels)")
    print("  metadata surface: %s" % ("; ".join(leaked) if leaked else "clean"))
    print("  reminder: this lists what identifies; treating pixels is the redact command")
    return 0, bool(leaked)


def check(path):
    _, warn = info(path)
    frames, n = open_frames(path)
    im = Image.open(path)
    if has_embedded_thumbnail(im):
        print("  finding: embedded thumbnail survived - the redaction is bypassable")
        warn = True
    print("check %s: %s" % (path, "FINDINGS (see above)" if warn else "clean"))
    return 1 if warn else 0


def selftest():
    import tempfile
    import os
    import io
    bad = 0
    d = tempfile.mkdtemp(prefix="revoke-image-selftest-")
    try:
        src = os.path.join(d, "orig.png")
        a = Image.new("RGB", (200, 120), (240, 240, 245))
        dr = ImageDraw.Draw(a)
        dr.ellipse([10, 10, 50, 50], fill=(30, 90, 200))          # avatar
        dr.text((60, 20), "Amr Muhamed", fill=(10, 10, 10))       # name label
        a.save(src, "PNG", Software="OriginalOwnerTool")
        has_meta = Image.open(src).info.get("Software") == "OriginalOwnerTool"
        spec = os.path.join(d, "spec.json")
        with open(spec, "w") as fh:
            json.dump([{"region": [8, 8, 44, 44], "mode": "block", "pad": 2},
                       {"region": [58, 14, 110, 20], "mode": "mosaic", "grid": 12}], fh)
        out = os.path.join(d, "revoked.png")
        rc = redact(src, out, spec)
        checks = [("redact exit", rc == 0)]
        r = Image.open(out)
        if has_meta:
            checks.append(("original untouched",
                           Image.open(src).info.get("Software") == "OriginalOwnerTool"))
            checks.append(("metadata not carried", r.info.get("Software") is None))
        else:
            print("selftest metadata pair            SKIP (this Pillow build drops PNG"
                  " text chunks on save - the check would be vacuous)")
        av = {r.getpixel((x, y)) for x in range(12, 48) for y in range(12, 48)}
        checks.append(("avatar region uniform", len(av) == 1))
        nm = r.crop((70, 18, 160, 32))
        checks.append(("name region mosaic-ed", len(nm.getcolors(4096) or []) <=
                       (nm.size[0] // 12 + 2) * (nm.size[1] // 12 + 2)))
        so, se = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
        try:
            rc2 = redact(src, src, spec)
        finally:
            sys.stdout, sys.stderr = so, se
        checks.append(("refuses to overwrite original", rc2 == 2))
        with open(spec, "w") as fh:
            json.dump([{"region": [58, 14, 110, 20], "mode": "blur", "radius": 6}], fh)
        so = sys.stdout
        sys.stdout = io.StringIO()
        try:
            redact(src, os.path.join(d, "b.png"), spec)
            printed = sys.stdout.getvalue()
        finally:
            sys.stdout = so
        checks.append(("blur prints de-identification warning", "not revocation" in printed))
        for name, ok in checks:
            print("%-38s %s" % ("selftest " + name, "PASS" if ok else "FAIL"))
            bad += 0 if ok else 1
    finally:
        import shutil
        shutil.rmtree(d, ignore_errors=True)
    print("self-test: %d problems" % bad)
    return 0 if bad == 0 else 1


def usage():
    print(__doc__.strip().splitlines()[0])
    print("commands:")
    print("  info IN                       what the file carries (frames, metadata surface)")
    print("  redact IN --out OUT --spec S  apply region spec (block|mosaic|blur), strip metadata")
    print("  check OUT                     metadata/thumbnail findings on a produced file (exit 1 if any)")
    print("  (no args)                     run self-test")
    print("spec JSON: [{\"region\":[x,y,w,h],\"mode\":\"block\",\"color\":\"auto|#RRGGBB\",\"pad\":4}]")
    print("           modes: block (opaque, default), mosaic (grid>=8), blur (NOT a redaction)")


def main(argv):
    if not argv:
        return selftest()
    cmd, args = argv[0], argv[1:]
    opts = {}
    rest = []
    i = 0
    while i < len(args):
        if args[i].startswith("--") and i + 1 < len(args):
            opts[args[i][2:]] = args[i + 1]
            i += 2
        else:
            rest.append(args[i])
            i += 1
    try:
        if cmd == "info" and rest:
            _, warn = info(rest[0])
            return 1 if warn else 0
        if cmd == "redact" and rest and "out" in opts and "spec" in opts:
            return redact(rest[0], opts["out"], opts["spec"])
        if cmd == "check" and rest:
            return check(rest[0])
    except FileNotFoundError as exc:
        print("error: %s" % exc)
        return 2
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        print("error: bad spec or file: %s" % exc)
        return 2
    usage()
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
