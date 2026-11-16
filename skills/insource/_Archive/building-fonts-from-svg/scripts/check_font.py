#!/usr/bin/env python3
"""Sanity-check a generated font and optionally render a specimen image.

    python check_font.py Font.ttf [--text "BOOM SHARDS"] [--png specimen.png] [--size 160]

Checks: required tables, .notdef, every mapped character has outlines and
actually draws ink, contour direction (TrueType wants outer contours
clockwise), and vertical bounds versus ascender/descender.
Exit code 1 if a hard problem is found. ALWAYS look at the PNG too: a font
can pass every check and still look wrong.
"""
import argparse
import sys

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REQUIRED = ["head", "hhea", "maxp", "OS/2", "hmtx", "cmap", "glyf", "name", "post"]


def ranges(codepoints):
    out, start, prev = [], None, None
    for cp in sorted(codepoints) + [None]:
        if start is None:
            start = prev = cp
        elif cp is not None and cp == prev + 1:
            prev = cp
        else:
            out.append(_label(start) if start == prev else f"{_label(start)}-{_label(prev)}")
            start = prev = cp
    return ", ".join(out)


def _label(cp):
    """ASCII-safe character label so the summary prints on any console."""
    ch = chr(cp)
    return ch if 0x20 < cp < 0x7F else f"U+{cp:04X}"


def net_area(glyf, name):
    """Sum of signed contour areas. Negative = clockwise (correct for TrueType)."""
    g = glyf[name]
    if g.numberOfContours <= 0:
        return 0.0
    coords, ends, _ = g.getCoordinates(glyf)
    total, start = 0.0, 0
    for end in ends:
        pts = coords[start:end + 1]
        total += sum(x0 * y1 - x1 * y0
                     for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1])) / 2
        start = end + 1
    return total


def plain_specimen(path, text, size, out_png):
    font = ImageFont.truetype(path, size)
    ascent, descent = font.getmetrics()
    lines = text.split("\n")
    pad, line_h = size // 4, int((ascent + descent) * 1.15)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    width = max(probe.textlength(line, font=font) for line in lines)
    img = Image.new("RGB", (int(width) + 2 * pad, line_h * len(lines) + 2 * pad), "white")
    draw = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        draw.text((pad, pad + ascent + i * line_h), line, font=font, fill="black", anchor="ls")
    img.save(out_png)


def shaped_specimen(path, text, size, out_png):
    """Render through HarfBuzz so GSUB/GPOS actually apply (Arabic joins, RTL).

    Shapes the text to glyph ids + positions, then draws each glyph by
    remapping it to a temporary PUA codepoint in a copy of the font.
    """
    import tempfile

    import uharfbuzz as hb

    blob = hb.Blob.from_file_path(path)
    face = hb.Face(blob)
    font = hb.Font(face)
    font.scale = (size, size)  # uharfbuzz returns positions already in pixels
    px = lambda v: v

    tt = TTFont(path)
    order = tt.getGlyphOrder()
    mapping = {0xE000 + i: name for i, name in enumerate(order)}
    for sub in tt["cmap"].tables:
        sub.cmap.update(mapping)
    tmp = tempfile.NamedTemporaryFile(suffix=".ttf", delete=False)
    tt.save(tmp.name)
    tmp.close()
    pil = ImageFont.truetype(tmp.name, size)

    upm = tt["head"].unitsPerEm
    lines = text.split("\n")
    ascent, descent = tt["hhea"].ascent * size / upm, -tt["hhea"].descent * size / upm

    shaped = []
    for line in lines:
        buf = hb.Buffer()
        buf.add_str(line)
        buf.guess_segment_properties()
        hb.shape(font, buf)
        shaped.append((buf, sum(px(p.x_advance) for p in buf.glyph_positions)))

    pad, line_h = size // 4, int((ascent + descent) * 1.4)
    width = int(max(w for _, w in shaped)) + 2 * pad
    img = Image.new("RGB", (width, line_h * len(lines) + 2 * pad + int(descent)), "white")
    draw = ImageDraw.Draw(img)
    y0 = pad + int(ascent)
    for i, (buf, _w) in enumerate(shaped):
        # HarfBuzz already returns glyphs in visual (left-to-right) order, even
        # for RTL, so always advance the pen to the right. Reversing it here
        # mirrors the word.
        x = pad
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            draw.text((x + px(pos.x_offset), y0 + i * line_h - px(pos.y_offset)),
                      chr(0xE000 + info.codepoint), font=pil, fill="black", anchor="ls")
            x += px(pos.x_advance)
    img.save(out_png)


def specimen(path, text, size, out_png):
    try:
        import uharfbuzz  # noqa: F401
    except ImportError:
        print("note: pip install uharfbuzz to render Arabic (shaped) specimens; "
              "falling back to unshaped PIL output")
        plain_specimen(path, text, size, out_png)
    else:
        shaped_specimen(path, text, size, out_png)
    print(f"specimen: {out_png}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("font")
    ap.add_argument("--text", help="text for the specimen (use \\n for new lines)")
    ap.add_argument("--png", help="write a specimen PNG here")
    ap.add_argument("--size", type=int, default=140)
    args = ap.parse_args()

    font = TTFont(args.font)
    problems, warnings = [], []

    for table in REQUIRED:
        if table not in font:
            problems.append(f"missing table {table}")
    if problems:
        sys.exit("\n".join(problems))

    cmap, glyf = font.getBestCmap(), font["glyf"]
    if font.getGlyphOrder()[0] != ".notdef":
        problems.append(".notdef is not the first glyph")

    upm = font["head"].unitsPerEm
    asc, desc = font["hhea"].ascent, font["hhea"].descent
    pil = ImageFont.truetype(args.font, 100)

    for cp, name in sorted(cmap.items()):
        ch = chr(cp)
        advance = font["hmtx"][name][0]
        if advance <= 0:
            problems.append(f"{ch!r} ({name}): zero advance width")
        if ch.isspace():
            continue
        g = glyf[name]
        if g.numberOfContours == 0:
            problems.append(f"{ch!r} ({name}): no outline")
            continue
        if pil.getmask(ch).getbbox() is None:
            problems.append(f"{ch!r} ({name}): renders blank")
        if net_area(glyf, name) > 0:
            warnings.append(f"{ch!r}: contours run counter-clockwise (outer should be clockwise)")
        if g.yMax <= 0:
            problems.append(f"{ch!r} ({name}): sits entirely below the baseline "
                            f"(y {g.yMin}..{g.yMax}); fix --baseline / viewBox in the build")
        if g.yMax > asc:
            warnings.append(f"{ch!r}: top {g.yMax} above ascender {asc}")
        if g.yMin < desc:
            warnings.append(f"{ch!r}: bottom {g.yMin} below descender {desc}")

    print(f"{args.font}: {len(font.getGlyphOrder())} glyphs, upm {upm}, ascender {asc}, descender {desc}")
    print(f"characters: {ranges(cmap)}")
    for w in warnings:
        print("warning:", w)
    for p in problems:
        print("PROBLEM:", p)

    if args.png:
        text = (args.text or "").replace("\\n", "\n")
        if not text:
            chars = [chr(c) for c in sorted(cmap) if not chr(c).isspace()]
            text = "\n".join("".join(chars[i:i + 14]) for i in range(0, len(chars), 14))
        specimen(args.font, text, args.size, args.png)

    print("OK" if not problems else f"{len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
