"""Batch-capture every HTML design/mockup in a designs folder.

Auto-detects the folder (designs/, design/, mockups/, .config/design/ ...), serves it on a
local port, and screenshots each .html at a fixed viewport, per theme.

Usage:
  python designs.py                              # auto-detect folder, light theme
  python designs.py --dir design/mvp --themes light dark
  python designs.py --pages projects settings    # names relative to folder, no .html needed
  python designs.py --base-url http://localhost:5173   # use an already-running server instead

Output: <out>/<page>/design_<theme>.png   (default out: .capture/)
"""
from __future__ import annotations

import argparse
import functools
import http.server
import os
import sys
import threading
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import (add_browser_args, add_device_args, add_json_args, add_output_args,  # noqa: E402
                  add_session_args, add_view_args, begin, check_file, emit, list_devices,
                  resolve_viewport)
from screenshots import capture_batch  # noqa: E402

NAMES = ["designs", "design", "mockups", "mockup", "wireframes"]
SKIP = {"node_modules", ".git", ".venv", "venv", "dist", "build", "__pycache__"}


def find_design_dir(root: Path, names=NAMES):
    for n in names:                       # direct children, e.g. ./designs
        if (root / n).is_dir():
            return root / n
    hidden = [d for d in root.glob(".*/") if d.is_dir() and d.name != ".git"]
    for h in hidden:                      # e.g. .config/design
        for n in names:
            if (h / n).is_dir():
                return h / n
    for depth in range(1, 4):             # shallow search anywhere else
        for d in root.glob("/".join(["*"] * depth)):
            if d.is_dir() and d.name.lower() in names and not (set(d.parts) & SKIP):
                return d
    return None


def find_pages(folder: Path):
    pages = []
    for f in sorted(folder.rglob("*.html")):
        if set(f.relative_to(folder).parts) & SKIP or f.name.startswith("_"):
            continue
        pages.append(f.relative_to(folder).with_suffix("").as_posix())
    return pages


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(folder: Path):
    handler = functools.partial(_Quiet, directory=str(folder))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def add_args(p):
    p.add_argument("--dir", help="Designs folder (default: auto-detect)")
    p.add_argument("--folder-names", nargs="+", metavar="NAME", help="Folder names to look for when auto-detecting (default: designs design mockups mockup wireframes)")
    p.add_argument("--base-url", help="Use an existing server serving the folder; skips the built-in one")
    p.add_argument("--pages", nargs="*", help="Page names relative to folder (default: all .html)")
    p.add_argument("--list", action="store_true", help="Only list detected folder and pages; capture nothing")
    p.add_argument("--themes", nargs="*", default=["light"], choices=["light", "dark"])
    p.add_argument("--theme", action="append", choices=["light", "dark"], default=[],
                   help="One theme (repeatable); same as --themes, for symmetry with `screenshots`")
    p.add_argument("--theme-key", help="localStorage key the pages read their theme from")
    add_output_args(p, single=False, default_dir=".capture", dir_help="Output root (default .capture)")
    add_view_args(p)
    p.add_argument("--full-page", action="store_true")
    p.add_argument("--wait-ms", type=int, default=500)
    p.add_argument("--wait-until", choices=["networkidle", "load", "domcontentloaded"], default="networkidle",
                   help="Navigation readiness (default networkidle)")
    add_device_args(p)
    add_session_args(p)
    add_browser_args(p, scale=True)
    add_json_args(p)


def run(args):
    if list_devices(args, "designs"):
        return
    check_file(args.storage_state, "--storage-state")
    folder = Path(args.dir).resolve() if args.dir else find_design_dir(Path.cwd(), [n.lower() for n in args.folder_names] if args.folder_names else NAMES)
    if not folder or not folder.is_dir():
        sys.exit("No designs folder found. Pass --dir <folder> (expected HTML files).")
    available = find_pages(folder)
    pages = [p[:-5] if p.endswith(".html") else p for p in args.pages] if args.pages else available
    unknown = [p for p in pages if p not in available]
    if unknown:
        sys.exit(f"Unknown page(s): {unknown}. Available: {available}")
    if not pages:
        sys.exit(f"No .html files in {folder}")
    if not 0 < args.scale <= 8:
        sys.exit("--scale must be between 0 and 8")
    vw, vh = resolve_viewport(args)
    if not (0 < vw <= 16384 and 0 < vh <= 16384):
        sys.exit("--width and --height must be between 1 and 16384")
    if args.list:
        payload = {"command": "designs", "folder": str(folder), "pages": pages}
        with begin(args) as real:
            print(f"Folder: {folder}")
            print("\n".join(f"  {pg}.html" for pg in pages))
        emit(args, payload, real)
        return

    themes = args.theme or args.themes
    width, height = vw, vh
    payload = {"command": "designs", "folder": str(folder), "pages": pages, "themes": themes,
               "output_dir": args.output_dir, "files": []}
    with begin(args) as real:
        srv = None
        base = args.base_url
        if not base:
            srv, base = serve(folder)
        print(f"Folder: {folder}\nServing: {base}\nPages: {pages}\nThemes: {themes}")
        try:
            jobs = [{"url": f"{base.rstrip('/')}/{pg}.html",
                     "output": os.path.join(args.output_dir, pg, f"design_{th}.png"),
                     "theme": th}
                    for pg in pages for th in themes]
            payload["files"] = capture_batch(
                jobs, width, height, args.full_page, args.wait_ms, args.theme_key,
                scale=args.scale, timeout=args.timeout, headed=args.headed, user_agent=args.user_agent,
                device=args.device, wait_until=args.wait_until, storage_state=args.storage_state)
        finally:
            if srv:
                srv.shutdown()
    emit(args, payload, real)


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    try:
        run(ap.parse_args())
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
