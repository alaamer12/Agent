"""Worked example: a geometric (Kufic-style) Arabic alphabet drawn in code.

    python make_letters.py
    python ../../scripts/build_font.py svgs --family ArabicSans --out ArabicSans.ttf \\
        --baseline 700 --side-bearing 0 --tracking 0
    python ../../scripts/check_font.py ArabicSans.ttf --text "سلام عليكم\\nالحمد لله" --png specimen.png

Arabic letters change shape by position. Each letter here is ONE skeleton plus a
dot pattern; the four forms (isolated / initial / medial / final) are derived by
attaching or detaching a horizontal "spine" connector at each side. The spine sits
at the same height (SPINE) in every glyph, so when HarfBuzz substitutes the right
form and places glyphs edge-to-edge, the strokes join into one continuous line.

Grid: viewBox 0 0 W 1000, baseline y=700 (so 300 units of descender room below).
Letters that only join from the right (alif, dal, ra, ...) get isolated+final only;
HarfBuzz never asks them for initial/medial.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from glyph_kit import bar, ribbon, svg_wrap  # noqa: E402

# --- shared levels (SVG y grows down; baseline is 700) ---------------------
TOP, MID, SPINE, BASE, BOWL, DEEP = 150, 430, 650, 700, 800, 900
SW, EXT, JAG = 90, 150, 0
_seed = [0]


def _n():
    _seed[0] += 1
    return _seed[0]


def R(points, w=SW):
    return ribbon(points, w, JAG, _n())


def B(x0, y0, x1, y1, w=SW):
    return bar(x0, y0, x1, y1, w, JAG, _n())


def ring(cx, cy, r, w=SW, seg=8):
    """Closed circular loop (thick annulus) -> gives letters like م ه a counter."""
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a))
           for a in [i * 2 * math.pi / seg for i in range(seg)]]
    return R(pts + pts[:2], w)


def dot(cx, cy, r=58):
    """Filled round dot (12-gon) for the Arabic diacritic points."""
    pts = [(cx + r * math.cos(i * math.pi / 6), cy + r * math.sin(i * math.pi / 6))
           for i in range(12)]
    return ribbon(pts, 2 * r, 0, _n())


def hamza(cx, cy, s=42):
    """Small hamza curl placed above/below a base letter (أ إ آ ؤ ئ)."""
    return R([(cx - s, cy + s), (cx - s, cy - s // 2), (cx + s // 2, cy - s // 2),
              (cx + s // 2, cy - s * 3 // 2), (cx - s // 2, cy - s * 3 // 2)], w=46)


def _marbuta(x):  # ة : closed round head, joins from the right only
    return [ring(x + 115, 600, 92)]


# --- letter skeletons ------------------------------------------------------
# Each entry: codepoint -> (bw, body(x0)->paths, rm, lm, jr, jl, dots)
#   bw = body width; rm/lm = (dx,dy) where the right/left connector meets the body
#   jr/jl = joins right (from previous) / joins left (to next)
#   dots = [(dx,dy,r)] relative to body origin
def _boat(x):
    return [R([(x, SPINE), (x + 70, SPINE), (x + 110, BOWL), (x + 270, BOWL),
               (x + 310, SPINE), (x + 380, SPINE)])]


def _hook(x):  # ج ح خ : stem + bowl
    return [R([(x + 340, SPINE), (x + 230, SPINE), (x + 230, BOWL), (x + 150, DEEP),
               (x + 70, DEEP), (x + 20, BOWL), (x + 20, SPINE), (x, SPINE)]),
            B(x + 230, SPINE, x + 230, MID)]


def _seen(x):  # س ش : three short teeth + deep tail
    return [R([(x + 460, SPINE), (x + 380, SPINE), (x + 355, 545), (x + 330, SPINE),
               (x + 305, 545), (x + 280, SPINE), (x + 255, 545), (x + 230, SPINE),
               (x + 150, SPINE), (x + 100, BOWL), (x + 60, DEEP), (x + 20, BOWL),
               (x, SPINE)])]


def _ayn(x):  # ع غ : tooth + round bowl
    return [R([(x + 320, SPINE), (x + 210, SPINE), (x + 210, MID), (x + 130, MID),
               (x + 130, SPINE), (x + 130, BOWL), (x + 70, DEEP), (x + 10, BOWL),
               (x, SPINE)])]


def _faa(x):  # ف ق : bowl + rising stem
    return [R([(x + 340, SPINE), (x + 230, SPINE), (x + 230, BOWL), (x + 150, DEEP),
               (x + 70, DEEP), (x + 30, BOWL), (x + 30, SPINE), (x, SPINE)]),
            B(x + 230, SPINE, x + 230, MID)]


def _kaf(x):
    return [R([(x, SPINE), (x + 150, SPINE), (x + 230, MID), (x + 300, SPINE),
               (x + 360, SPINE)]), B(x + 300, TOP, x + 300, SPINE)]


def _lam(x):
    return [R([(x + 200, SPINE), (x + 110, SPINE), (x + 110, MID), (x + 50, TOP)]),
            B(x, SPINE, x + 110, SPINE)]


def _mim(x):  # م ه : round head + short tail
    return [ring(x + 120, 560, 95), B(x + 120, 650, x + 120, DEEP)]


def _noon(x):  # ن ي ى : bowl with descender
    return [R([(x + 340, SPINE), (x + 250, SPINE), (x + 200, BOWL), (x + 120, DEEP),
               (x + 60, DEEP), (x + 20, BOWL), (x, SPINE)])]


def _dal(x):
    return [R([(x + 240, SPINE), (x + 120, SPINE), (x + 80, BOWL), (x + 40, DEEP),
               (x, DEEP)])]


def _ra(x):
    return [R([(x + 240, SPINE), (x + 130, SPINE), (x + 70, BOWL), (x + 20, DEEP),
               (x, DEEP)])]


def _alif(x):
    return [B(x + 90, TOP, x + 90, BASE)]


def _waw(x):
    return [ring(x + 110, 560, 90),
            R([(x + 200, SPINE), (x + 250, SPINE), (x + 285, BOWL), (x + 260, DEEP)])]


def _sad(x):  # ص ض : loop head + long bowl
    return [R([(x + 300, SPINE), (x + 300, MID), (x + 210, MID), (x + 210, SPINE),
               (x + 210, BOWL), (x + 130, DEEP), (x + 40, DEEP), (x, BOWL), (x, SPINE)]),
            B(x + 300, SPINE, x + 380, SPINE)]


def _tah(x):  # ط ظ : loop + tall vertical
    return [R([(x + 320, SPINE), (x + 230, SPINE), (x + 230, BOWL), (x + 150, DEEP),
               (x + 70, DEEP), (x + 30, BOWL), (x + 30, SPINE), (x, SPINE)]),
            ring(x + 175, 540, 80), B(x + 175, 460, x + 175, TOP)]


LETTERS = {
    0x0627: (180, _alif, (90, BASE), None, True, False, []),                                               # ا
    0x0623: (180, _alif, (90, BASE), None, True, False, [('h', 90, 70, 0)]),                               # أ
    0x0625: (180, _alif, (90, BASE), None, True, False, [('h', 90, 860, 0)]),                              # إ
    0x0622: (180, _alif, (90, BASE), None, True, False, [('h', 90, 150, 0), ('m', 90, 60, 0)]),           # آ
    0x0624: (300, _waw, (285, SPINE), None, True, False, [('h', 110, 360, 0)]),                            # ؤ
    0x0629: (230, _marbuta, (207, SPINE), None, True, False, [('d', 82, 430, 48), ('d', 148, 430, 48)]),   # ة
    0x0628: (380, _boat, (380, SPINE), (0, SPINE), True, True, [(190, 910, 55)]),                          # ب
    0x062A: (380, _boat, (380, SPINE), (0, SPINE), True, True, [(150, 430, 55), (230, 430, 55)]),          # ت
    0x062B: (380, _boat, (380, SPINE), (0, SPINE), True, True, [(140, 450, 52), (240, 450, 52), (190, 330, 52)]),  # ث
    0x062C: (340, _hook, (340, SPINE), (0, SPINE), True, True, [(180, 300, 55)]),                          # ج
    0x062D: (340, _hook, (340, SPINE), (0, SPINE), True, True, []),                                        # ح
    0x062E: (340, _hook, (340, SPINE), (0, SPINE), True, True, [(180, 300, 55)]),                          # خ
    0x062F: (240, _dal, (240, SPINE), None, True, False, []),                                              # د
    0x0630: (240, _dal, (240, SPINE), None, True, False, [(150, 430, 55)]),                                # ذ
    0x0631: (240, _ra, (240, SPINE), None, True, False, []),                                               # ر
    0x0632: (240, _ra, (240, SPINE), None, True, False, [(150, 430, 55)]),                                 # ز
    0x0633: (460, _seen, (460, SPINE), (0, SPINE), True, True, []),                                        # س
    0x0634: (460, _seen, (460, SPINE), (0, SPINE), True, True, [('d', 210, 420, 50), ('d', 300, 420, 50), ('d', 255, 320, 50)]),  # ش
    0x0635: (380, _sad, (380, SPINE), (0, SPINE), True, True, []),                                         # ص
    0x0636: (380, _sad, (380, SPINE), (0, SPINE), True, True, [(250, 300, 55)]),                           # ض
    0x0637: (320, _tah, (320, SPINE), (0, SPINE), True, True, []),                                         # ط
    0x0638: (320, _tah, (320, SPINE), (0, SPINE), True, True, [(175, 300, 55)]),                           # ظ
    0x0639: (320, _ayn, (320, SPINE), (0, SPINE), True, True, []),                                         # ع
    0x063A: (320, _ayn, (320, SPINE), (0, SPINE), True, True, [(200, 300, 55)]),                           # غ
    0x0641: (340, _faa, (340, SPINE), (0, SPINE), True, True, [(180, 300, 55)]),                           # ف
    0x0642: (340, _faa, (340, SPINE), (0, SPINE), True, True, [('d', 150, 300, 50), ('d', 230, 300, 50)]),  # ق
    0x0643: (360, _kaf, (360, SPINE), (0, SPINE), True, True, []),                                         # ك
    0x0644: (200, _lam, (200, SPINE), (0, SPINE), True, True, []),                                         # ل
    0x0645: (240, _mim, (215, SPINE), (25, SPINE), True, True, []),                                        # م
    0x0646: (340, _noon, (340, SPINE), (0, SPINE), True, True, [(170, 430, 55)]),                          # ن
    0x0647: (240, _mim, (215, SPINE), (25, SPINE), True, True, []),                                        # ه
    0x0648: (300, _waw, (285, SPINE), None, True, False, []),                                              # و
    0x0649: (340, _noon, (340, SPINE), None, True, False, []),                                             # ى
    0x064A: (340, _noon, (340, SPINE), (0, SPINE), True, True, [('d', 140, 1000, 45), ('d', 240, 1000, 45)]),  # ي
    0x0626: (340, _noon, (340, SPINE), (0, SPINE), True, True, [('h', 170, 380, 0), ('d', 140, 1000, 45), ('d', 240, 1000, 45)]),  # ئ
}


def connector(meet, edge_x):
    """Horizontal spine stub from the glyph edge (at SPINE) to the body meet point."""
    mx, my = meet
    if my == SPINE:
        return B(edge_x, SPINE, mx, SPINE)
    return R([(edge_x, SPINE), (mx, SPINE), (mx, my)])


def build_forms(cp, bw, body, rm, lm, jr, jl, dots):
    """Return {form: (width, paths)} for the forms this letter actually has."""
    def ink(x0):
        paths = list(body(x0))
        for m in dots:
            if len(m) == 3:
                paths.append(dot(x0 + m[0], m[1], m[2]))
            elif m[0] == "d":
                paths.append(dot(x0 + m[1], m[2], m[3]))
            elif m[0] == "h":
                paths.append(hamza(x0 + m[1], m[2]))
            elif m[0] == "m":  # madda: a small horizontal tilde-bar
                paths.append(B(x0 + m[1] - 45, m[2], x0 + m[1] + 45, m[2], w=44))
        return paths

    forms = {"isol": (bw, ink(0))}
    if jr:
        forms["fina"] = (bw + EXT, ink(0) + [connector(rm, bw + EXT)])
    if jl:
        forms["init"] = (bw + EXT, ink(EXT) + [connector(lm, 0)])
        forms["medi"] = (bw + 2 * EXT, ink(EXT) + [connector(lm, 0), connector(rm, bw + 2 * EXT)])
    return forms


if __name__ == "__main__":
    out = Path(__file__).parent / "svgs"
    out.mkdir(exist_ok=True)
    count = 0
    for cp, spec in LETTERS.items():
        for form, (width, paths) in build_forms(cp, *spec).items():
            suffix = "" if form == "isol" else f"_{form}"
            name = f"uni{cp:04X}{suffix}.svg"
            (out / name).write_text(svg_wrap(paths, width=width, height=1000), newline="\n")
            count += 1
    print(f"wrote {count} glyph SVGs ({len(LETTERS)} letters) to {out}")
