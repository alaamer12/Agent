#!/usr/bin/env python3
"""
run_android_suite.py — Android/emulator screenshot parity suite over ADB.

The Android counterpart of ``run_suite.py``. It drives each screen through the
platform's own screenshot mechanism (``adb exec-out screencap -p``), crops the
OS status/navigation bars, and scores the result against a design baseline.

It is deliberately ADB-only: no Appium, no test framework, no device code. If a
device can be reached with ``adb``, this works.

Screen definition
-----------------
A JSON screens file is the deterministic form:

    {
      "screens": [
        {
          "name": "home",
          "page": "home",
          "theme": "light",
          "extra": {"design-data": "1"},
          "crop": {"top": 64, "bottom": 2270}
        },
        {
          "name": "home_dark",
          "page": "home",
          "theme": "dark",
          "extra": {"design-data": "1"},
          "crop": {"top": 64, "bottom": 2270}
        }
      ]
    }

Without a file, ``--screens home,home_dark`` derives:
  page   = name with a trailing ``_dark`` removed
  theme  = dark when the suffix is present, else light
  crop   = --crop-top / --crop-bottom (default 0 / full height)

The launch intent is:
  am start -S -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
           -n <component> -e default-page <page> -e theme <theme> [--extra K V]...

Design baselines are resolved as ``<design-dir>/<name>/design.png`` by default
(``--design-pattern`` accepts ``{name} {page} {theme}``).

Usage:
    python run_android_suite.py --package com.example.app \
        --screens-file screens.json --design-dir baselines
    python run_android_suite.py --package com.example.app \
        --screens home,home_dark --crop-top 64 --crop-bottom 2270
Documentation example:

    python run_android_suite.py --package com.example.app \
        --screens-file screens.json --serial <device-serial> --threshold 0.9

The serial is whatever `adb devices` prints (an emulator console, a USB device
serial, or omitted entirely when exactly one device is attached).

Exit codes: 0 = every screen scored at/above threshold; 1 = missing baseline,
capture failure, or below-threshold score.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from similarity import run_comparison  # noqa: E402


# --------------------------------------------------------------------------- #
# ADB helpers
# --------------------------------------------------------------------------- #

def adb_base(serial: str | None) -> list[str]:
    return ["adb"] + (["-s", serial] if serial else [])


def adb(args: list[str], serial: str | None, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(adb_base(serial) + args, check=True, **kwargs)


def resolve_component(package: str, component: str | None, serial: str | None) -> str:
    if component:
        return component if "/" in component else f"{package}/{component}"
    try:
        out = adb(["shell", "cmd", "package", "resolve-activity", "--brief",
                   package], serial, capture_output=True, text=True).stdout.strip()
        for line in reversed(out.splitlines()):
            if "/" in line:
                return line.strip()
    except subprocess.CalledProcessError:
        pass
    raise SystemExit(
        f"Could not resolve a launcher activity for {package}. "
        f"Pass --component explicitly (e.g. {package}/.MainActivity)."
    )


# --------------------------------------------------------------------------- #
# Screen model
# --------------------------------------------------------------------------- #

def load_screens(args: argparse.Namespace) -> list[dict]:
    if args.screens_file:
        with open(args.screens_file, encoding="utf-8") as fh:
            data = json.load(fh)
        screens = data.get("screens") if isinstance(data, dict) else data
        return [
            {
                "name": s["name"],
                "page": s.get("page", s["name"].replace("_dark", "")),
                "theme": s.get("theme", "dark" if s["name"].endswith("_dark") else "light"),
                "extra": s.get("extra", {}),
                "crop": s.get("crop", {"top": args.crop_top, "bottom": args.crop_bottom}),
            }
            for s in screens
        ]

    names = [n.strip() for n in (args.screens or "home").split(",") if n.strip()]
    return [
        {
            "name": name,
            "page": name.replace("_dark", ""),
            "theme": "dark" if name.endswith("_dark") else "light",
            "extra": {},
            "crop": {"top": args.crop_top, "bottom": args.crop_bottom},
        }
        for name in names
    ]


def crop_frame(img: Image.Image, crop: dict) -> Image.Image:
    w, h = img.size
    top = max(0, int(crop.get("top", 0)))
    left = max(0, int(crop.get("left", 0)))
    right = int(crop.get("right", w))
    bottom = int(crop.get("bottom", h))
    if bottom <= 0 or bottom > h:
        bottom = h
    if right <= 0 or right > w:
        right = w
    return img.crop((left, top, right, bottom))


# --------------------------------------------------------------------------- #
# Capture + score
# --------------------------------------------------------------------------- #

def capture_screen(screen: dict, args: argparse.Namespace,
                   component: str) -> tuple[Image.Image, str]:
    out_dir = os.path.join(args.out_root, screen["name"])
    os.makedirs(out_dir, exist_ok=True)
    raw_path = os.path.join(out_dir, "current_raw.png")
    cropped_path = os.path.join(out_dir, "current.png")

    print(f"\n--- {screen['name']} ---")
    if not args.no_force_stop:
        adb(["shell", "am", "force-stop", args.package], args.serial)
        time.sleep(1)

    cmd = [
        "shell", "am", "start", "-S",
        "-a", "android.intent.action.MAIN",
        "-c", "android.intent.category.LAUNCHER",
        "-n", component,
        "-e", "default-page", screen["page"],
        "-e", "theme", screen["theme"],
    ]
    for key, value in list((args.extra or {}).items()) + list(screen["extra"].items()):
        cmd += ["-e", key, str(value)]
    adb(cmd, args.serial)

    time.sleep(args.wait)
    with open(raw_path, "wb") as fh:
        adb(["exec-out", "screencap", "-p"], args.serial, stdout=fh)

    with Image.open(raw_path) as img:
        content = crop_frame(img.convert("RGB"), screen["crop"])
        content.save(cropped_path)
    print(f"captured {raw_path} -> {cropped_path} ({content.width}x{content.height})")
    return content, cropped_path


def score_screen(name: str, current_path: str, design_path: str,
                 args: argparse.Namespace) -> dict:
    heatmap = os.path.join(args.out_root, name, "heatmap.png")
    report = run_comparison(
        design_path, current_path,
        resize_mode="pad",
        methods=None,
        region_report=False,
        regional_score=4,
        palette=8,
        heatmap_out=heatmap,
    )
    data = report.to_dict()
    return {
        "name": name,
        "overall": data.get("overall_similarity"),
        "ssim": (data.get("scores") or {}).get("ssim"),
        "palette": (data.get("palette") or {}).get("palette_similarity"),
        "regional": (data.get("regional_score") or {}).get("worst", [])[:4],
        "heatmap": heatmap,
        "meets_threshold": (data.get("overall_similarity") or 0) >= args.threshold,
    }


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def md_report(rows: list[dict], threshold: float) -> str:
    lines = [
        "# Android parity suite",
        "",
        f"Generated: {dt.datetime.now().isoformat(timespec='seconds')}  ",
        f"Threshold: {threshold:.0%}",
        "",
        "| screen | status | overall | ssim | palette | worst cells |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        if row.get("unverified"):
            lines.append(f"| {row['name']} | UNVERIFIED (no baseline) | — | — | — | — |")
            continue
        if row.get("error"):
            lines.append(f"| {row['name']} | ERROR: {row['error']} | — | — | — | — |")
            continue
        worst = ", ".join(
            f"r{c['row']}c{c['col']}={c['similarity']:.2f}" for c in row.get("regional", [])
        ) or "—"
        lines.append(
            f"| {row['name']} | {'OK' if row['meets_threshold'] else 'LOW'} | "
            f"{row['overall']:.2%} | {row['ssim']:.2%} | "
            f"{(row['palette'] or 0):.2%} | {worst} |"
        )
    bad = [r["name"] for r in rows
           if r.get("unverified") or r.get("error") or not r.get("meets_threshold")]
    lines += ["", f"FAILED: {len(bad)} screen(s): {', '.join(bad)}"
              if bad else "", "PASSED: every screen scored." if not bad else ""]
    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Android screenshot parity suite over ADB.")
    parser.add_argument("--package", required=True, help="application package name")
    parser.add_argument("--component", default=None,
                        help="launcher component; resolved from the package when omitted")
    parser.add_argument("--serial", default=None, help="adb device serial")
    parser.add_argument("--screens-file", default=None, help="JSON screen definitions")
    parser.add_argument("--screens", default=None,
                        help="comma-separated simple screen names (no JSON)")
    parser.add_argument("--design-dir", default="baselines",
                        help="design baseline root (default ./baselines)")
    parser.add_argument("--design-pattern", default="{name}/design.png",
                        help="baseline path template under --design-dir")
    parser.add_argument("--out-root", default="parity_mobile",
                        help="artifacts root (default ./parity_mobile)")
    parser.add_argument("--crop-top", type=int, default=0,
                        help="status-bar pixels to remove (simple mode)")
    parser.add_argument("--crop-bottom", type=int, default=0,
                        help="absolute y where content ends; 0 = image bottom")
    parser.add_argument("--extra", action="append", default=[], metavar="KEY=VALUE",
                        help="extra intent extras applied to every screen")
    parser.add_argument("--wait", type=float, default=14.0,
                        help="settle seconds after launch (default 14)")
    parser.add_argument("--threshold", type=float, default=0.90)
    parser.add_argument("--no-force-stop", action="store_true")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    try:
        subprocess.run(adb_base(args.serial) + ["version"],
                       capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        print("ERROR: adb is not available on PATH.", file=sys.stderr)
        return 2

    extra = {}
    for item in args.extra:
        if "=" not in item:
            parser.error(f"--extra expects KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        extra[key] = value
    args.extra = extra

    component = resolve_component(args.package, args.component, args.serial)
    screens = load_screens(args)
    os.makedirs(args.out_root, exist_ok=True)

    rows = []
    for screen in screens:
        design = os.path.join(args.design_dir,
                              args.design_pattern
                              .replace("{name}", screen["name"])
                              .replace("{page}", screen["page"])
                              .replace("{theme}", screen["theme"]))
        if not os.path.exists(design):
            print(f"NO BASELINE for {screen['name']}: {design} — NOT verified")
            rows.append({"name": screen["name"], "unverified": True})
            continue
        try:
            _, current = capture_screen(screen, args, component)
            row = score_screen(screen["name"], current, design, args)
        except Exception as exc:
            rows.append({"name": screen["name"], "error": f"{type(exc).__name__}: {exc}"})
            print(f"ERROR {screen['name']}: {type(exc).__name__}: {exc}")
            continue
        rows.append(row)
        print(f"  overall {row['overall']:.2%} ssim {row['ssim']:.2%} "
              f"palette {(row['palette'] or 0):.2%}")

    report = md_report(rows, args.threshold)
    print(report)
    with open(os.path.join(args.out_root, "report.md"), "w", encoding="utf-8") as fh:
        fh.write(report)
    json_path = args.json_out or os.path.join(args.out_root, "results.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump({"generated": dt.datetime.now().isoformat(timespec="seconds"),
                   "package": args.package, "screens": rows},
                  fh, indent=2, ensure_ascii=False, default=str)

    bad = [r for r in rows
           if r.get("unverified") or r.get("error") or not r.get("meets_threshold")]
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
