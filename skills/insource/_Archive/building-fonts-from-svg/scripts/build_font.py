#!/usr/bin/env python3
"""Compile a folder of SVG glyph drawings into a TrueType font.

    python build_font.py SVG_DIR --family "My Font" [--out MyFont.ttf] [--web]

Each SVG becomes one glyph. The character comes from the file name:
    uni0041.svg / u0041.svg / U+0041.svg  -> codepoint U+0041 (preferred)
    A.svg, 7.svg                          -> that single character
    uni0628_init.svg / _medi / _fina      -> contextual form of U+0628.
      The unsuffixed file (or _isol) is the isolated form and owns the cmap
      entry; GSUB feature rules (init/medi/fina) are generated automatically
      so HarfBuzz-based renderers join Arabic letters. See
      references/arabic-shaping.md.
Grid: 1 SVG unit = `--scale` font units; SVG y=`--baseline` is the baseline
(default: bottom edge of each file's viewBox). Strokes are unioned per glyph,
so overlapping shapes are safe. Requires: fonttools, skia-pathops
(optional: brotli for .woff2).
"""
import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pathops
from fontTools.agl import UV2AGL
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Transform
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path
from fontTools.svgLib.path.shapes import PathBuilder
from fontTools.ttLib import TTFont

SKIP_TAGS = {"defs", "clipPath", "mask", "symbol", "metadata", "title", "desc"}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def apply_transform(base, attr):
    """Append an SVG transform="..." list to `base` (a fontTools Transform)."""
    t = base
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", attr or ""):
        v = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "translate":
            t = t.translate(v[0], v[1] if len(v) > 1 else 0)
        elif name == "scale":
            t = t.scale(v[0], v[1] if len(v) > 1 else v[0])
        elif name == "rotate":
            cx, cy = (v[1], v[2]) if len(v) == 3 else (0, 0)
            t = t.translate(cx, cy).rotate(math.radians(v[0])).translate(-cx, -cy)
        elif name == "skewX":
            t = t.skew(math.radians(v[0]), 0)
        elif name == "skewY":
            t = t.skew(0, math.radians(v[0]))
        elif name == "matrix":
            t = t.transform(Transform(*v))
        else:
            raise ValueError(f"unsupported transform '{name}'")
    return t


def walk(el, transform=None):
    """Yield (element, cumulative transform) so group transforms are inherited."""
    if local(el.tag) in SKIP_TAGS:
        return
    transform = apply_transform(transform or Transform(), el.get("transform"))
    yield el, transform
    for child in el:
        yield from walk(child, transform)


def style_of(el):
    return el.get("style", "").replace(" ", "")


def codepoint_from_stem(stem):
    m = re.fullmatch(r"(?:uni|u\+?)([0-9A-Fa-f]{4,6})", stem, re.IGNORECASE)
    if m:
        return int(m.group(1), 16)
    if len(stem) == 1:
        return ord(stem)
    return None


FORMS = ("isol", "init", "medi", "fina")


def parse_stem(stem):
    """'uni0628_init' -> (0x628, 'init'); 'uni0041' -> (0x41, None)."""
    m = re.fullmatch(r"(.*?)[-_](isol|init|medi|fina)", stem, re.IGNORECASE)
    if not m:
        return codepoint_from_stem(stem), None
    return codepoint_from_stem(m.group(1)), m.group(2).lower()


def read_grid(root):
    """Return (min_x, min_y, width, height) of the SVG's coordinate box."""
    vb = root.get("viewBox")
    if vb:
        min_x, min_y, w, h = (float(v) for v in re.split(r"[\s,]+", vb.strip()))
        return min_x, min_y, w, h
    num = lambda s: float(re.sub(r"[^0-9.\-]", "", s or "") or 0)
    w, h = num(root.get("width")), num(root.get("height"))
    if not (w and h):
        raise ValueError("SVG needs a viewBox (or width and height)")
    return 0.0, 0.0, w, h


def svg_to_skpath(svg_file, scale, baseline):
    """Parse one SVG into a single unioned, winding-correct pathops Path.

    Returns (path_or_None, grid_height). Each filled element is resolved on its
    own (so fill-rule="evenodd" holes work) and then unioned with the rest.
    """
    root = ET.parse(svg_file).getroot()
    min_x, min_y, _, height = read_grid(root)
    base = (min_y + height) if baseline is None else baseline
    to_font = Transform(scale, 0, 0, -scale, -min_x * scale, base * scale)

    pieces = []
    for el, el_transform in walk(root):
        style = style_of(el)
        if el.get("fill") == "none" or "fill:none" in style:
            continue  # unfilled shapes are strokes; strokes are not supported
        # fontTools' shape parser rejects transform attributes; we handle them ourselves
        plain = ET.Element(el.tag, {k: v for k, v in el.attrib.items() if k != "transform"})
        builder = PathBuilder()
        builder.add_path_from_element(plain)
        evenodd = el.get("fill-rule") == "evenodd" or "fill-rule:evenodd" in style
        for d in builder.paths:
            sk = pathops.Path()
            pen = TransformPen(TransformPen(sk.getPen(), to_font), el_transform)
            parse_path(d, pen)
            sk.fillType = (pathops.FillType.EVEN_ODD if evenodd
                           else pathops.FillType.WINDING)
            sk.simplify(fix_winding=True, keep_starting_points=False, clockwise=True)
            if list(sk.segments):
                pieces.append(sk)
    if not pieces:
        return None, height
    result = pieces[0]
    for other in pieces[1:]:
        result = pathops.op(result, other, pathops.PathOp.UNION,
                            fix_winding=True, keep_starting_points=False,
                            clockwise=True)
    return result, height


def make_notdef(width=500):
    """Hollow rectangle: the box people see when a character has no glyph."""
    pen = TTGlyphPen(None)
    pen.moveTo((50, 0)); pen.lineTo((50, 700)); pen.lineTo((450, 700)); pen.lineTo((450, 0))
    pen.closePath()
    pen.moveTo((100, 50)); pen.lineTo((400, 50)); pen.lineTo((400, 650)); pen.lineTo((100, 650))
    pen.closePath()
    return pen.glyph()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("svg_dir")
    ap.add_argument("--family", required=True)
    ap.add_argument("--style", default="Regular")
    ap.add_argument("--out", help="output .ttf (default: <Family>.ttf)")
    ap.add_argument("--upm", type=int, default=1000, help="units per em")
    ap.add_argument("--scale", type=float, default=1.0, help="font units per SVG unit")
    ap.add_argument("--baseline", type=float, help="SVG y of the baseline (default: viewBox bottom)")
    ap.add_argument("--ascender", type=int, default=800)
    ap.add_argument("--descender", type=int, default=-200)
    ap.add_argument("--cap-height", type=int, default=700, help="metadata only")
    ap.add_argument("--x-height", type=int, default=500, help="metadata only")
    ap.add_argument("--side-bearing", type=int, default=50)
    ap.add_argument("--tracking", type=int, default=0, help="extra advance per glyph")
    ap.add_argument("--space-width", type=int, default=300)
    ap.add_argument("--web", action="store_true", help="also write .woff (+ .woff2 if brotli installed)")
    args = ap.parse_args()

    svg_files = sorted(Path(args.svg_dir).glob("*.svg"))
    if not svg_files:
        sys.exit(f"No .svg files in {args.svg_dir}")

    order, cmap, glyphs, advances = [".notdef"], {}, {".notdef": make_notdef()}, {".notdef": 500}
    heights = set()

    groups = {}
    for f in svg_files:
        cp, form = parse_stem(f.stem)
        if cp is None:
            print(f"skip {f.name}: cannot derive a character from the file name")
            continue
        form = form or "isol"
        if form in groups.setdefault(cp, {}):
            sys.exit(f"duplicate {form} form for U+{cp:04X}: {f.name}")
        groups[cp][form] = f

    sub_rules = {feat: [] for feat in ("init", "medi", "fina")}
    for cp, forms in sorted(groups.items()):
        if "isol" not in forms:
            sys.exit(f"U+{cp:04X}: has contextual forms but no isolated glyph "
                     f"(add uni{cp:04X}.svg or uni{cp:04X}_isol.svg)")
        base = UV2AGL.get(cp, f"uni{cp:04X}")
        for form in FORMS:
            if form not in forms:
                continue
            name = base if form == "isol" else f"{base}_{form}"
            try:
                sk, grid_h = svg_to_skpath(forms[form], args.scale, args.baseline)
            except Exception as e:
                sys.exit(f"{forms[form].name}: {type(e).__name__}: {e}")
            heights.add(grid_h)
            tt = TTGlyphPen(None)
            if sk is None:
                advances[name] = args.space_width
            else:
                xmin, _, xmax, _ = sk.bounds
                dx = args.side_bearing - xmin
                sk.draw(TransformPen(Cu2QuPen(tt, max_err=1.0), Transform(1, 0, 0, 1, dx, 0)))
                advances[name] = round(xmax - xmin + 2 * args.side_bearing + args.tracking)
            glyphs[name] = tt.glyph()
            order.append(name)
            if form == "isol":
                if cp in cmap:
                    sys.exit(f"duplicate codepoint U+{cp:04X}")
                cmap[cp] = base
            else:
                sub_rules[form].append(f"  sub {base} by {name};")

    if len(heights) > 1:
        print(f"warning: SVGs use different viewBox heights {sorted(heights)}; "
              "glyphs will not share a baseline unless you pass --baseline")
    if 0x20 not in cmap:
        glyphs["space"] = TTGlyphPen(None).glyph()
        advances["space"], cmap[0x20] = args.space_width, "space"
        order.append("space")
    if len(order) == 1:
        sys.exit("No usable glyphs found")

    fb = FontBuilder(args.upm, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    glyf = fb.font["glyf"]
    fb.setupHorizontalMetrics({n: (advances[n], getattr(glyf[n], "xMin", 0)) for n in order})

    y_max = max((getattr(glyf[n], "yMax", 0) for n in order), default=0)
    y_min = min((getattr(glyf[n], "yMin", 0) for n in order), default=0)
    if y_max > args.ascender:
        print(f"warning: tallest glyph reaches y={y_max}, above --ascender {args.ascender}")
    if y_min < args.descender:
        print(f"warning: lowest glyph reaches y={y_min}, below --descender {args.descender}")

    fb.setupHorizontalHeader(ascent=args.ascender, descent=args.descender)
    ps = f"{args.family.replace(' ', '')}-{args.style.replace(' ', '')}"
    fb.setupNameTable({
        "familyName": args.family, "styleName": args.style,
        "uniqueFontIdentifier": f"{ps};1.0", "fullName": f"{args.family} {args.style}",
        "version": "Version 1.0", "psName": ps,
    })
    fb.setupOS2(sTypoAscender=args.ascender, sTypoDescender=args.descender, sTypoLineGap=0,
                usWinAscent=max(args.ascender, y_max), usWinDescent=max(-args.descender, -y_min),
                sCapHeight=args.cap_height, sxHeight=args.x_height)
    fb.setupPost()

    fea = [line for feat, rules in sub_rules.items() if rules
           for line in (f"feature {feat} {{", *rules, f"}} {feat};", "")]
    if fea:
        from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
        addOpenTypeFeaturesFromString(fb.font,
                                      "\n".join(["languagesystem arab dflt;", *fea]))

    out = Path(args.out or f"{args.family.replace(' ', '')}.ttf")
    fb.save(out)
    print(f"wrote {out} ({len(order)} glyphs, {len(cmap)} characters)")

    if args.web:
        for flavor in ("woff", "woff2"):
            font = TTFont(out)
            font.flavor = flavor
            try:
                font.save(out.with_suffix("." + flavor))
                print(f"wrote {out.with_suffix('.' + flavor)}")
            except ImportError:
                print("skipped .woff2: pip install brotli")


if __name__ == "__main__":
    main()
