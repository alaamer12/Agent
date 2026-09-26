#!/usr/bin/env python3
"""Self-test for motion.py: build frames with known motion, then classify them.

Deterministic and offline — needs only ffmpeg. Run this after touching any
threshold in motion.py:

  python3 scripts/selftest.py            # 8 cases, exits 0 when all pass
"""
from __future__ import annotations

import json
import math
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
MOTION = SCRIPTS / "motion.py"
WORK = Path(tempfile.gettempdir()) / "watch-selftest"

W, H = 320, 240


def canvas():
    """A static checkerboard, so the scene has texture to track."""
    buf = bytearray()
    for y in range(H):
        for x in range(W):
            v = 100 + 30 * (((x // 24) + (y // 24)) % 2)
            buf += bytes((v, v, v))
    return buf


def paint(buf, pts, col=(245, 245, 245)):
    for x, y in pts:
        xi, yi = int(round(x)), int(round(y))
        if 0 <= xi < W and 0 <= yi < H:
            i = (yi * W + xi) * 3
            buf[i:i + 3] = bytes(col)


def square(buf, ox, oy, s=44):
    paint(buf, [(x, y) for y in range(oy, oy + s) for x in range(ox, ox + s)])


def bar(buf, cx, cy, length, thickness, angle_deg):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(cx + u * ca - v * sa, cy + u * sa + v * ca)
           for u in range(-length // 2, length // 2) for v in range(-thickness // 2, thickness // 2)]
    paint(buf, pts)


def noise(seed):
    buf = bytearray()
    state = seed
    for _ in range(W * H):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        v = (state >> 16) & 0xFF
        buf += bytes((v, v, v))
    return buf


def write(name, buf):
    path = WORK / name
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{W}x{H}", "-i", "-", str(path)],
        input=bytes(buf), check=True,
    )
    return path


def build() -> dict:
    WORK.mkdir(parents=True, exist_ok=True)
    f = {}
    for name, (ox, oy) in {
        "right_a": (60, 100), "right_b": (200, 100),
        "up_a": (140, 160), "up_b": (140, 40),
        "bl_a": (220, 60), "bl_b": (60, 180),
        "tr_a": (60, 180), "tr_b": (220, 60),
        "same_a": (100, 100), "same_b": (100, 100),
    }.items():
        b = canvas()
        square(b, ox, oy)
        f[name] = write(f"{name}.png", b)

    b = canvas(); bar(b, 160, 120, 120, 26, 90); f["rot_a"] = write("rot_a.png", b)
    b = canvas(); bar(b, 160, 120, 120, 26, 0); f["rot_b"] = write("rot_b.png", b)

    b = canvas(); square(b, 60, 100); f["cut_a"] = write("cut_a.png", b)
    f["cut_b"] = write("cut_b.png", noise(7))

    # A dark scene with a small bright subject: low global contrast, but the
    # subject is unmistakably there and unmistakably moving.
    b = bytearray(W * H * 3); square(b, 60, 100, s=24); f["dark_a"] = write("dark_a.png", b)
    b = bytearray(W * H * 3); square(b, 200, 100, s=24); f["dark_b"] = write("dark_b.png", b)

    flat = bytearray(W * H * 3)
    f["flat_a"] = write("flat_a.png", flat)
    f["flat_b"] = write("flat_b.png", bytearray(v + 4 for v in flat))
    return f


CASES = [
    ("right", "right", "object travels right"),
    ("up", "top", "object travels up"),
    ("bl", "bottom-left", "object travels down and left"),
    ("tr", "top-right", "object travels up and right"),
    ("same", "in-place", "identical frames"),
    ("rot", "in-place", "bar rotates 90 degrees about its own centre"),
    ("cut", "cannot-determine", "shot A then unrelated noise shot B"),
    ("dark", "right", "small bright subject on a black field (low global contrast)"),
    ("flat", "cannot-determine", "near-uniform frames, nothing to track"),
]


def main() -> int:
    if not MOTION.is_file():
        print(f"cannot find {MOTION}", file=sys.stderr)
        return 2
    frames = build()
    failures = 0
    for prefix, expected, label in CASES:
        res = subprocess.run(
            [sys.executable, str(MOTION), str(frames[f"{prefix}_a"]), str(frames[f"{prefix}_b"]),
             "--json"],
            capture_output=True, text=True,
        )
        if res.returncode:
            print(f"FAIL {label}: motion.py exited {res.returncode}: {res.stderr.strip()[:160]}")
            failures += 1
            continue
        got = res.stdout.strip()
        verdict = json.loads(got)
        ok = verdict["direction"] == expected
        failures += 0 if ok else 1
        print(f"{'ok  ' if ok else 'FAIL'} {label:<46} expected={expected:<17} "
              f"got={verdict['direction']:<17} conf={verdict['confidence']}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
