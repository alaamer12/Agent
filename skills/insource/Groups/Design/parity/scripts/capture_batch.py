#!/usr/bin/env python3
"""
capture_batch.py — capture an entire mockup matrix in one deterministic pass.

Parity scope is a matrix: pages × themes × variants (data sources, locales,
layout modes…). Capturing that by hand is where runs silently diverge — one
screen captured at a different DPR, one theme forgotten, one page pointed at the
wrong served folder.

This script owns the matrix and nothing else. It does not compare; it produces
the reference side that ``parity_run.py`` / ``run_suite.py`` score against.

URL templating
--------------
``--url-template`` supports these placeholders:

  {base}            value of --base-url
  {page}            page id
  {theme}           light | dark (whatever you pass via --themes)
  {variant}         variant id (raw, always substituted)
  {variant_query}   ``&variant=<id>`` for non-default variants, empty otherwise
  {page_query}      ``?theme=<theme>`` shortcut for the common case

The default template is ``{base}/{page}.html?theme={theme}{variant_query}``.

Output layout
-------------
Default folder: ``{page}`` when there is exactly one variant, otherwise
``{page}_{variant}``. Inside it the default filename is ``design_{theme}.png``.
Override with ``--folder-template`` / ``--filename-template``.

Usage:
    python capture_batch.py --base-url http://localhost:8000 \
        --design-root design --pages home settings profile
    python capture_batch.py --base-url http://localhost:8000 \
        --pages home --themes light dark --variants alpha beta \
        --out-root captures --width 1440 --height 900
    python capture_batch.py --base-url http://localhost:8000 \
        --pages home --themes dark --set-storage theme=dark --reduced-motion

Requirements: playwright (via capture_mockup).
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from capture_mockup import capture, parse_storage  # noqa: E402

DEFAULT_URL_TEMPLATE = "{base}/{page}.html?theme={theme}{variant_query}"


def build_url(template: str, base: str, page: str, theme: str, variant: str) -> str:
    variant_query = "" if variant in {"", "default"} else f"&variant={variant}"
    return (template
            .replace("{base}", base.rstrip("/"))
            .replace("{page}", page)
            .replace("{theme}", theme)
            .replace("{variant}", variant)
            .replace("{variant_query}", variant_query)
            .replace("{page_query}", f"?theme={theme}"))


def build_path(template: str, page: str, theme: str, variant: str) -> str:
    return (template
            .replace("{page}", page)
            .replace("{theme}", theme)
            .replace("{variant}", variant))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Capture a page x theme x variant mockup matrix.")
    parser.add_argument("--base-url", default="http://localhost:8000",
                        help="root URL the mockup folder is served at")
    parser.add_argument("--url-template", default=DEFAULT_URL_TEMPLATE,
                        help=f"URL template (default: {DEFAULT_URL_TEMPLATE})")
    parser.add_argument("--pages", nargs="+", required=True,
                        help="page ids, e.g. home settings profile")
    parser.add_argument("--themes", nargs="+", default=["light", "dark"])
    parser.add_argument("--variants", nargs="+", default=["default"],
                        help="data-source / locale / layout variants")
    parser.add_argument("--design-root", default=None,
                        help="optional folder being served; validates that each "
                             "{page}.html exists before capturing")
    parser.add_argument("--out-root", default="parity_captures",
                        help="output root (default: ./parity_captures)")
    parser.add_argument("--folder-template", default=None,
                        help="output folder template; default is {page} for one "
                             "variant, {page}_{variant} otherwise")
    parser.add_argument("--filename-template", default="design_{theme}.png",
                        help="output filename template (default: design_{theme}.png)")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=800)
    parser.add_argument("--dpr", type=float, default=1.0)
    parser.add_argument("--wait-ms", type=int, default=500)
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--reduced-motion", action="store_true")
    parser.add_argument("--set-storage", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--init-js", action="append", default=[], metavar="JS")
    parser.add_argument("--toggle-dark-class", action="store_true")
    parser.add_argument("--dark-class", default="dark")
    parser.add_argument("--json-out", default=None,
                        help="write the capture manifest (path -> metadata) here")
    args = parser.parse_args()

    if args.design_root:
        missing = [
            p for p in args.pages
            if not os.path.exists(os.path.join(args.design_root, p + ".html"))
        ]
        if missing:
            print(f"ERROR: --design-root {args.design_root} has no: {', '.join(missing)}")
            return 1

    folder_template = args.folder_template
    if folder_template is None:
        folder_template = "{page}" if len(args.variants) == 1 else "{page}_{variant}"

    storage = parse_storage(args.set_storage)
    manifest = []

    for page in args.pages:
        for theme in args.themes:
            for variant in args.variants:
                url = build_url(args.url_template, args.base_url, page, theme, variant)
                folder = build_path(folder_template, page, theme, variant)
                filename = build_path(args.filename_template, page, theme, variant)
                output = os.path.join(args.out_root, folder, filename)

                capture(
                    url=url, output=output,
                    width=args.width, height=args.height,
                    full_page=args.full_page, wait_ms=args.wait_ms,
                    theme=theme, device_scale_factor=args.dpr,
                    reduced_motion=args.reduced_motion,
                    init_scripts=args.init_js, storage=storage,
                    toggle_dark_class=args.toggle_dark_class,
                    dark_class=args.dark_class,
                )
                manifest.append({
                    "page": page, "theme": theme, "variant": variant,
                    "url": url, "output": output,
                    "viewport": [args.width, args.height], "dpr": args.dpr,
                })

    if args.json_out:
        out_dir = os.path.dirname(os.path.abspath(args.json_out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(manifest, fh, indent=2, ensure_ascii=False)
        print(f"Manifest: {args.json_out} ({len(manifest)} captures)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
