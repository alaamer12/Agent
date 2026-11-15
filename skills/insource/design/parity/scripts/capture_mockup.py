#!/usr/bin/env python3
"""
capture_mockup.py — deterministic headless screenshots of a served design page.

A mockup capture is only useful for parity when it is *reproducible*: the same
URL, viewport, device-pixel-ratio, colour scheme and preloaded state must produce
the same pixels every run. This script pins all five.

The design page can be plain HTML/CSS, a Figma/Stitch export, or any local page
that a browser can render. It must be served over HTTP, never ``file://`` —
query-param state forcing, relative assets and ``fetch``-based fixtures are
unreliable or broken over ``file://``.

State seeding (all optional, all generic):

  --set-storage theme=dark        localStorage before any page script runs
  --set-storage source=alpha      (repeatable; one KEY=VALUE per flag)
  --init-js "document.body.classList.add('ready')"
  --toggle-dark-class             toggles <html class="dark"> after load
  --theme dark                    sets prefers-color-scheme

Usage:
    python capture_mockup.py --url http://localhost:8000/home.html \
        --output captures/home_light.png
    python capture_mockup.py --url http://localhost:8000/home.html \
        --output captures/home_dark.png --theme dark --dpr 1 --reduced-motion
    python capture_mockup.py --url "http://localhost:8000/home.html?state=open" \
        --output captures/home_open.png --width 1440 --height 900 --wait-ms 800

Requirements: playwright (``pip install playwright && playwright install chromium``)
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from playwright.sync_api import sync_playwright


def _storage_script(storage: dict[str, str]) -> str:
    """Build a localStorage seeding script safe against disabled storage."""
    pairs = ",".join(
        f"{json.dumps(k)}:{json.dumps(str(v))}" for k, v in storage.items()
    )
    return (
        "try { const s = {%s}; for (const k in s) "
        "localStorage.setItem(k, s[k]); } catch (e) {}" % pairs
    )


def capture(url: str, output: str, width: int, height: int, full_page: bool,
            wait_ms: int, theme: str = "light",
            device_scale_factor: float = 1.0, reduced_motion: bool = False,
            init_scripts: list[str] | None = None,
            storage: dict[str, str] | None = None,
            toggle_dark_class: bool = False, dark_class: str = "dark",
            color_scheme: str | None = None) -> None:
    """Capture one deterministic frame of ``url``.

    ``device_scale_factor`` must match the app capture's effective DPR. A
    mismatch resizes every downstream crop and inflates the noise floor before
    any real content is compared.
    ``reduced_motion`` emulates ``prefers-reduced-motion: reduce``, which
    well-built mockups honour by disabling decorative animation — the only
    frame-varying pixels on an otherwise static page.
    """
    out_dir = os.path.dirname(os.path.abspath(output))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    scheme = color_scheme or ("dark" if theme == "dark" else "light")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": width, "height": height},
            device_scale_factor=device_scale_factor,
            color_scheme=scheme,
        )
        if reduced_motion:
            page.emulate_media(reduced_motion="reduce")

        if storage:
            page.add_init_script(_storage_script(storage))
        for script in init_scripts or []:
            page.add_init_script(script)

        page.goto(url, wait_until="networkidle")
        if toggle_dark_class:
            page.evaluate(
                "([cls, on]) => document.documentElement.classList.toggle(cls, on)",
                [dark_class, theme == "dark"],
            )
        if wait_ms:
            page.wait_for_timeout(wait_ms)
        page.screenshot(path=output, full_page=full_page)
        browser.close()

    print(f"Saved: {output}")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="capture_mockup.py",
        description="Screenshot a served design page with Playwright/Chromium.")
    parser.add_argument("--url", required=True,
                        help="served page URL, e.g. http://localhost:8000/home.html")
    parser.add_argument("--output", required=True, help="output PNG path")
    parser.add_argument("--width", type=int, default=1280, help="viewport width")
    parser.add_argument("--height", type=int, default=800, help="viewport height")
    parser.add_argument("--full-page", action="store_true",
                        help="capture the whole scrollable page, not just the viewport")
    parser.add_argument("--wait-ms", type=int, default=300,
                        help="extra settle time after load (default 300ms)")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                        help="colour-scheme state to emulate (default light)")
    parser.add_argument("--color-scheme", default=None,
                        help="explicit CSS colour-scheme override")
    parser.add_argument("--dpr", type=float, default=1.0,
                        help="device scale factor; must match the app capture (default 1.0)")
    parser.add_argument("--reduced-motion", action="store_true",
                        help="emulate prefers-reduced-motion: reduce")
    parser.add_argument("--set-storage", action="append", default=[], metavar="KEY=VALUE",
                        help="seed localStorage before page scripts (repeatable)")
    parser.add_argument("--init-js", action="append", default=[], metavar="JS",
                        help="run JavaScript before page scripts (repeatable)")
    parser.add_argument("--toggle-dark-class", action="store_true",
                        help="toggle a dark class on <html> after load")
    parser.add_argument("--dark-class", default="dark",
                        help="class name used by --toggle-dark-class (default: dark)")
    return parser


def parse_storage(values: list[str]) -> dict[str, str]:
    storage: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"--set-storage expects KEY=VALUE, got: {item}")
        key, value = item.split("=", 1)
        storage[key] = value
    return storage


def main() -> int:
    args = build_arg_parser().parse_args()
    try:
        capture(
            args.url, args.output, args.width, args.height, args.full_page,
            args.wait_ms, theme=args.theme,
            device_scale_factor=args.dpr, reduced_motion=args.reduced_motion,
            init_scripts=args.init_js, storage=parse_storage(args.set_storage),
            toggle_dark_class=args.toggle_dark_class, dark_class=args.dark_class,
            color_scheme=args.color_scheme,
        )
    except Exception as exc:  # pragma: no cover - CLI guard
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
