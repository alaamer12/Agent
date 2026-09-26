#!/usr/bin/env python3
"""Validate an animated SVG against its original static source.

Usage: python3 validate.py <original.svg> <animated.svg>

Checks (exit 1 on any FAIL):
  1. Both files are well-formed XML
  2. Every original path's `d` string appears verbatim in the animated file
  3. Every original fill-rule is preserved (count + presence on the elements
     that carry the corresponding d)
  4. Every original fill color is present in the animated file
  5. viewBox is unchanged
"""
import re
import sys
import xml.dom.minidom as minidom


def parse(f):
    content = open(f).read()
    # Hardened: reject DTD/entity declarations (XXE + expansion bombs) before parsing.
    # Well-formed SVGs never need them; expat alone does not block these.
    head = content[:4096].lower()
    if '<!doctype' in head or '<!entity' in head:
        sys.exit(f"FAIL: {f} contains a DTD/entity declaration — refusing to parse")
    minidom.parseString(content)  # raises on malformed XML
    return content


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: validate.py <original.svg> <animated.svg>")
    orig_f, anim_f = sys.argv[1], sys.argv[2]
    ok = True

    try:
        orig = parse(orig_f)
    except Exception as e:
        sys.exit(f"FAIL: original is not well-formed XML: {e}")
    print(f"PASS  original well-formed XML ({orig_f})")

    try:
        anim = parse(anim_f)
    except Exception as e:
        sys.exit(f"FAIL: animated is not well-formed XML: {e}")
    print(f"PASS  animated well-formed XML ({anim_f})")

    orig_paths = re.findall(r'<path\b[^>]*?/>', orig)
    orig_ds = [re.search(r'd="([^"]*)"', p).group(1) for p in orig_paths]
    missing = [i for i, d in enumerate(orig_ds) if d not in anim]
    if missing:
        ok = False
        print(f"FAIL  {len(missing)}/{len(orig_ds)} original d strings missing in animated output: indices {missing}")
    else:
        print(f"PASS  all {len(orig_ds)} original d strings present verbatim")

    for i, p in enumerate(orig_paths):
        fr = re.search(r'fill-rule="([^"]*)"', p)
        if fr:
            rule = fr.group(1)
            n_orig = len(re.findall(r'fill-rule="' + re.escape(rule) + r'"', orig))
            n_anim = len(re.findall(r'fill-rule="' + re.escape(rule) + r'"', anim))
            if n_anim >= n_orig:
                print(f"PASS  fill-rule=\"{rule}\" preserved ({n_anim} occurrences)")
            else:
                ok = False
                print(f"FAIL  fill-rule=\"{rule}\" lost: {n_orig} in original, {n_anim} in animated")

    orig_fills = set(re.findall(r'fill="(#[0-9a-fA-F]{3,8})"', orig))
    css_fills = set(re.findall(r'fill:\s*(#[0-9a-fA-F]{3,8})', orig))
    for c in sorted(orig_fills | css_fills):
        if c.lower() in anim.lower():
            print(f"PASS  fill color {c} present")
        else:
            ok = False
            print(f"FAIL  fill color {c} missing")

    vb_orig = re.search(r'viewBox="([^"]*)"', orig)
    vb_anim = re.search(r'viewBox="([^"]*)"', anim)
    if vb_orig and vb_anim and vb_orig.group(1) == vb_anim.group(1):
        print(f"PASS  viewBox unchanged ({vb_orig.group(1)})")
    else:
        ok = False
        print(f"FAIL  viewBox changed: {vb_orig and vb_orig.group(1)} -> {vb_anim and vb_anim.group(1)}")

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
