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
    p.add_argument("--theme-key", help="localStorage key the pages read their theme from")
    p.add_argument("--out", default=".capture", help="Output root (default .capture)")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=800)
    p.add_argument("--full-page", action="store_true")
    p.add_argument("--wait-ms", type=int, default=500)


def run(args):
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
    if args.list:
        print(f"Folder: {folder}")
        print("\n".join(f"  {pg}.html" for pg in pages))
        return

    srv = None
    base = args.base_url
    if not base:
        srv, base = serve(folder)
    print(f"Folder: {folder}\nServing: {base}\nPages: {pages}")
    try:
        jobs = [{"url": f"{base.rstrip('/')}/{pg}.html",
                 "output": os.path.join(args.out, pg, f"design_{th}.png"),
                 "theme": th}
                for pg in pages for th in args.themes]
        capture_batch(jobs, args.width, args.height, args.full_page, args.wait_ms, args.theme_key)
    finally:
        if srv:
            srv.shutdown()


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
