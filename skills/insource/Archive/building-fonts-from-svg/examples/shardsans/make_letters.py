"""Worked example: a 26-letter 'shard' display alphabet drawn entirely in code.

    python make_letters.py          # writes ./svgs/uniXXXX.svg for A-Z
    python ../../scripts/build_font.py svgs --family ShardSans --out ShardSans.ttf

Copy this file to start a new style: keep the grid (cap-height y=0, baseline
y=700), change the stroke recipes. Set JAG = 0 for a clean geometric look.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from glyph_kit import bar, burst, ribbon, write_glyph  # noqa: E402

W, JAG = 90, 22          # stroke width, edge roughness
_seed = [0]


def _next():
    _seed[0] += 1
    return _seed[0]


def R(points, w=W):
    return ribbon(points, w, JAG, _next())


def B(x0, y0, x1, y1, w=W):
    return bar(x0, y0, x1, y1, w, JAG, _next())


def ring(points, w=W):
    """Closed loop: repeat the first two points so the ends overlap."""
    return R(points + points[:2], w)


_O = [(300, 0), (500, 90), (580, 350), (500, 610), (300, 700), (100, 610), (20, 350), (100, 90)]
_P = [(60, 0), (330, 0), (420, 90), (420, 260), (330, 350), (60, 350)]
_C = [(560, 90), (380, 0), (150, 40), (30, 220), (30, 480), (150, 660), (380, 700), (560, 610)]

LETTERS = {
    "A": lambda: [R([(300, 0), (60, 700)]), R([(300, 0), (540, 700)]),
                  B(170, 460, 430, 460, W - 10), burst(300, 20, 55, 3, _next())],
    "B": lambda: [B(60, 0, 60, 700), R([(60, 0), (330, 0), (400, 90), (330, 340), (60, 340)], W - 15),
                  R([(60, 340), (350, 340), (430, 520), (350, 700), (60, 700)], W - 15)],
    "C": lambda: [R(_C)],
    "D": lambda: [B(60, 0, 60, 700),
                  R([(60, 0), (300, 0), (480, 150), (520, 350), (480, 550), (300, 700), (60, 700)], W - 15)],
    "E": lambda: [B(60, 0, 60, 700), B(60, 0, 480, 0, W - 10), B(60, 340, 400, 340, W - 20),
                  B(60, 700, 480, 700, W - 10)],
    "F": lambda: [B(60, 0, 60, 700), B(60, 0, 480, 0, W - 10), B(60, 340, 400, 340, W - 20)],
    "G": lambda: [R(_C + [(560, 380)]), B(380, 380, 560, 380, W - 15)],
    "H": lambda: [B(60, 0, 60, 700), B(480, 0, 480, 700), B(90, 350, 450, 350, W - 15)],
    "I": lambda: [B(270, 0, 270, 700)],
    "J": lambda: [R([(420, 0), (420, 480), (330, 660), (150, 700), (30, 570), (60, 430)], W - 10)],
    "K": lambda: [B(60, 0, 60, 700), R([(500, 0), (100, 360)], W - 10), R([(140, 360), (520, 700)], W - 10)],
    "L": lambda: [B(60, 0, 60, 700), B(60, 700, 460, 700, W - 10)],
    "M": lambda: [B(40, 700, 40, 0, W - 10), R([(40, 0), (300, 420)], W - 15),
                  R([(300, 420), (560, 0)], W - 15), B(560, 0, 560, 700, W - 10)],
    "N": lambda: [B(60, 700, 60, 0, W - 10), R([(60, 0), (480, 700)], W - 15), B(480, 700, 480, 0, W - 10)],
    "O": lambda: [ring(_O)],
    "P": lambda: [B(60, 0, 60, 700), R(_P, W - 15)],
    "Q": lambda: [ring(_O), B(360, 480, 560, 700, W - 20)],
    "R": lambda: [B(60, 0, 60, 700), R(_P, W - 15), R([(280, 350), (500, 700)], W - 15)],
    "S": lambda: [R([(540, 130), (380, 10), (170, 10), (40, 140), (60, 300), (220, 350), (420, 400),
                     (560, 520), (520, 640), (330, 700), (120, 660), (30, 540)], W - 15)],
    "T": lambda: [B(30, 0, 570, 0, W - 10), B(300, 0, 300, 700)],
    "U": lambda: [R([(60, 0), (60, 480), (170, 660), (350, 700), (500, 600), (540, 420), (540, 0)], W - 10)],
    "V": lambda: [R([(30, 0), (300, 700)], W - 10), R([(300, 700), (570, 0)], W - 10)],
    "W": lambda: [R([(10, 0), (170, 700)], W - 20), R([(170, 700), (310, 260)], W - 25),
                  R([(310, 260), (450, 700)], W - 25), R([(450, 700), (610, 0)], W - 20)],
    "X": lambda: [R([(40, 0), (520, 700)], W - 10), R([(520, 0), (40, 700)], W - 10)],
    "Y": lambda: [R([(30, 0), (300, 380)], W - 15), R([(570, 0), (300, 380)], W - 15),
                  B(300, 380, 300, 700, W - 10)],
    "Z": lambda: [B(40, 0, 560, 0, W - 10), R([(560, 0), (40, 700)], W - 10), B(40, 700, 560, 700, W - 10)],
}

if __name__ == "__main__":
    out = Path(__file__).parent / "svgs"
    for char, recipe in LETTERS.items():
        write_glyph(out, char, recipe())
    print(f"wrote {len(LETTERS)} glyph SVGs to {out}")
