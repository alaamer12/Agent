"""Screenshot URLs or local HTML files with Playwright/Chromium.

Modes (at most one; default is a single viewport-sized image):
  --full-page        one image of the whole page            (alias: --big-shot)
  --scroll           scroll top to bottom, one image per step (see --overlap)
  --slices N         split the whole page into N equal slices (alias: --symmetrical)
  --selector CSS     one image of the first matching element

Usage:
  python screenshots.py https://example.com --full-page
  python screenshots.py a.com b.com --view mobile --scroll
  python screenshots.py design/home.html -o .capture/home.png --theme dark
  python screenshots.py --url http://localhost:3000 --slices 4 --output-dir shots

Targets may be http(s) URLs, file:// URLs, local paths, or bare domains (https:// is added;
localhost gets http://). Requires: pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import (add_browser_args, add_device_args, add_json_args, add_output_args,  # noqa: E402
                  add_session_args, add_view_args, begin, check_file, emit,
                  list_devices, resolve_device, resolve_viewport)
from _common import ensure_parent, resolve_output  # noqa: E402

# Limits and safety parameters (named so they are visible and tunable in one place).
MIN_ZOOM_PCT, MAX_ZOOM_PCT = 10, 500       # below ~10% the emulated CSS viewport becomes absurdly large
MAX_DIMENSION_PX = 16384                   # Chromium's practical texture limit
MAX_SCALE = 8                              # device pixel ratio
MIN_SLICE_PX = 50                         # --slices must not make slices thinner than this
DEFAULT_MAX_SHOTS = 500                    # cap on images from --scroll / --slices (override with --max-shots)
MAX_NAME_CHARS = 100                       # folder names are shortened (with a hash) beyond this
WINDOWS_RESERVED = {"con", "prn", "aux", "nul", *(f"com{i}" for i in range(1, 10)), *(f"lpt{i}" for i in range(1, 10))}
LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


# ---------- helpers ----------
def normalize_url(url: str) -> str:
    if "://" in url:
        return url
    p = Path(url).expanduser()
    if p.exists():
        return p.resolve().as_uri()
    if url.lower().endswith((".html", ".htm")):
        raise FileNotFoundError(f"No such file: {url}")
    host = url.split("/")[0].split(":")[0]
    return f"{'http' if host in LOCAL_HOSTS else 'https'}://{url}"


def folder_name(url: str) -> str:
    """Filesystem-safe folder name for a URL: example.com/a/b -> example.com_a_b."""
    u = urlparse(url)
    if u.scheme == "file":
        raw = Path(unquote(u.path)).stem or "page"
    else:
        path = u.path.strip("/").replace("/", "_")
        raw = f"{u.netloc.replace(':', '_')}_{path}" if path else u.netloc
    cleaned = "".join(c if c.isalnum() or c in "_-." else "_" for c in raw).strip("_") or "page"
    if cleaned.split(".")[0].lower() in WINDOWS_RESERVED:          # CON, NUL, COM1... cannot be Windows folder names
        cleaned = "_" + cleaned
    if len(cleaned) > MAX_NAME_CHARS:                              # stay far below filesystem name limits
        cleaned = cleaned[:MAX_NAME_CHARS - 9] + "_" + hashlib.md5(cleaned.encode()).hexdigest()[:8]
    return cleaned


def parse_zoom(value: str) -> int:
    v = value.strip().rstrip("%")
    try:
        f = float(v)
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid zoom: {value}")
    pct = int(round(f * 100)) if (0 < f <= 5.0 and "." in v) else int(round(f))
    if not MIN_ZOOM_PCT <= pct <= MAX_ZOOM_PCT:
        raise argparse.ArgumentTypeError(f"Zoom must be between {MIN_ZOOM_PCT}% and {MAX_ZOOM_PCT}%")
    return pct


def uniform_positions(total: int, viewport_h: int, overlap: int) -> list[int]:
    """Scroll offsets covering `total` px with `overlap` px shared between steps."""
    if total <= viewport_h:
        return [0]
    step = max(viewport_h - overlap, 1)
    out, y = [], 0
    while True:
        pos = min(y, total - viewport_h)
        if pos not in out:
            out.append(pos)
        if y + viewport_h >= total:
            return out
        y += step


def equal_segments(total: int, n: int) -> list[tuple[int, int]]:
    """n (y, height) segments that tile `total` px exactly (remainder spread over the first ones)."""
    if n <= 0:
        raise ValueError("slice count must be a positive integer")
    base, rem = divmod(total, n)
    segs, y = [], 0
    for i in range(n):
        h = base + (1 if i < rem else 0)
        segs.append((y, h))
        y += h
    return segs


@dataclass
class Opts:
    width: int = 1280
    height: int = 800
    scale: float = 1.0
    zoom: int = 100
    wait_ms: int = 300
    wait_until: str = "networkidle"
    theme: str | None = None
    theme_key: str | None = None
    device_cfg: dict | None = None      # Playwright device descriptor (--device)
    lazy: bool = False
    user_agent: str | None = None
    timeout: int | None = None
    storage_state: str | None = None

    # Zoom is emulated like real browser zoom: a larger/smaller CSS viewport rendered at a
    # compensating pixel ratio. Output pixel size stays width*scale x height*scale.
    @property
    def css_width(self) -> int:
        return max(1, round(self.width * 100 / self.zoom))

    @property
    def css_height(self) -> int:
        return max(1, round(self.height * 100 / self.zoom))


# ---------- page handling ----------
def scroll_height(page) -> int:
    return page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")


def settle(page, wait_ms: int) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=3000)
    except Exception:
        pass
    if wait_ms:
        page.wait_for_timeout(wait_ms)


def preload_lazy(page, step: int) -> None:
    """Scroll through the page once so lazy-loaded images/sections render, then return to top."""
    y = 0
    for _ in range(200):
        if y >= scroll_height(page):
            break
        page.evaluate(f"window.scrollTo(0,{y})")
        page.wait_for_timeout(150)
        y += step
    page.evaluate("window.scrollTo(0,0)")


def open_page(browser, url: str, o: Opts):
    if o.device_cfg:
        args = dict(o.device_cfg)       # Playwright's maintained descriptor: viewport, UA, pixel ratio, touch, mobile
    else:
        args = {"viewport": {"width": o.css_width, "height": o.css_height},
                "device_scale_factor": o.scale * o.zoom / 100}
    if o.theme:
        args["color_scheme"] = o.theme
    if o.user_agent:
        args["user_agent"] = o.user_agent
    if o.storage_state:
        args["storage_state"] = o.storage_state
    page = browser.new_page(**args)
    if o.theme and o.theme_key:
        # Seed before first paint so pages that read storage in <head> are deterministic.
        page.add_init_script("try{localStorage.setItem(%r,%r)}catch(e){}" % (o.theme_key, o.theme))
    goto = {"wait_until": o.wait_until}
    if o.timeout:
        goto["timeout"] = o.timeout
    page.goto(normalize_url(url), **goto)
    if o.theme:
        page.evaluate("t=>{const r=document.documentElement;"
                      "r.classList.toggle('dark',t==='dark');r.setAttribute('data-theme',t)}", o.theme)
    if o.lazy:
        preload_lazy(page, o.css_height)
    settle(page, o.wait_ms)
    return page


# ---------- capture primitives ----------
def shoot_single(page, output: str, o: Opts, full_page=False, selector=None) -> str:
    ensure_parent(output)
    if selector:
        loc = page.locator(selector)
        if loc.count() == 0:
            raise ValueError(f"--selector {selector!r} matched no element on the page")
        loc.first.screenshot(path=output)
    else:
        page.screenshot(path=output, full_page=full_page)
    return output


def shoot_series(page, out_dir: Path, o: Opts, mode: str, slices=None, overlap=100, suffix="",
                 max_shots: int = DEFAULT_MAX_SHOTS) -> list[str]:
    total = scroll_height(page)
    if mode == "scroll":
        positions = uniform_positions(total, o.css_height, overlap)
        if len(positions) > max_shots:
            raise ValueError(f"--scroll would produce {len(positions)} screenshots (cap {max_shots}); "
                             "use --slices, reduce --overlap, or raise --max-shots")
        segments = None
    else:
        if slices > max_shots:
            raise ValueError(f"--slices {slices} exceeds the cap of {max_shots} images; raise --max-shots if you really need it")
        if slices > total:
            raise ValueError(f"the page is only {total}px tall, so --slices {slices} would create empty slices (use at most {total})")
        if total / slices < MIN_SLICE_PX:
            raise ValueError(f"--slices {slices} on a {total}px page would make slices thinner than {MIN_SLICE_PX}px "
                             f"(use at most {max(1, total // MIN_SLICE_PX)})")
        segments = equal_segments(total, slices)
    out_dir.mkdir(parents=True, exist_ok=True)
    saved = []
    if mode == "scroll":
        for i, y in enumerate(positions, 1):
            page.evaluate(f"window.scrollTo(0,{y})")
            settle(page, min(o.wait_ms, 300))
            path = str(out_dir / f"{i}{suffix}.png")
            page.screenshot(path=path)
            saved.append(path)
    else:  # slices: document-coordinate clips, so tall segments are never cut off
        for i, (y, h) in enumerate(segments, 1):
            path = str(out_dir / f"{i}{suffix}.png")
            page.screenshot(path=path, full_page=True,
                            clip={"x": 0, "y": y, "width": o.css_width, "height": max(h, 1)})
            saved.append(path)
    return saved


def capture_batch(jobs, width=1280, height=800, full_page=False, wait_ms=300,
                  theme_key=None, selector=None, scale=1.0, timeout=30000,
                  headed=False, user_agent=None, device=None,
                  wait_until="networkidle", storage_state=None, **extra):
    """jobs: iterable of {url, output, theme}. One browser, one PNG per job (used by `designs`)."""
    from playwright.sync_api import sync_playwright

    saved = []
    with sync_playwright() as p:
        device_cfg = resolve_device(p, device) if device else None
        if device_cfg:
            width, height = device_cfg["viewport"]["width"], device_cfg["viewport"]["height"]
        browser = p.chromium.launch(headless=not headed)
        try:
            for job in jobs:
                o = Opts(width=width, height=height, scale=scale, wait_ms=wait_ms, theme=job.get("theme"),
                         theme_key=theme_key, timeout=timeout, user_agent=user_agent,
                         device_cfg=device_cfg, wait_until=wait_until, storage_state=storage_state, **extra)
                page = open_page(browser, job["url"], o)
                try:
                    shoot_single(page, job["output"], o, full_page, selector)
                finally:
                    page.close()
                print(f"Saved: {job['output']}")
                saved.append(job["output"])
        finally:
            browser.close()
    return saved


# ---------- CLI ----------
def add_args(p):
    p.add_argument("urls_pos", nargs="*", metavar="URL", help="Targets (URL, file path, or bare domain)")
    p.add_argument("--url", "--urls", dest="url", nargs="+", default=[], metavar="URL",
                   help="Targets, same as positionals")
    add_output_args(
        p,
        dir_help="Root for per-target folders <dir>/<name>/<i>.png (default .capture/screenshots)",
        default_dir=".capture/screenshots",
    )
    add_view_args(p, default="desktop")
    p.add_argument("--scale", type=float, default=1.0, help="Device pixel ratio, e.g. 2 for retina (default 1)")
    add_device_args(p)
    add_session_args(p)
    p.add_argument("--max-shots", type=int, default=DEFAULT_MAX_SHOTS, metavar="N", help=f"Cap on images from --scroll/--slices (default {DEFAULT_MAX_SHOTS})")
    p.add_argument("--zoom", type=parse_zoom, default=100,
                   help="Browser-style zoom: 90, 90%%, or 0.9. Below 100 fits more page into the same image size")
    m = p.add_mutually_exclusive_group()
    m.add_argument("--full-page", "--big-shot", dest="full_page", action="store_true",
                   help="One image of the entire page")
    m.add_argument("--scroll", action="store_true", help="Scroll top to bottom, one image per viewport step")
    m.add_argument("--slices", "--symmetrical", dest="slices", type=int, metavar="N",
                   help="Split the entire page into N equal slices")
    m.add_argument("--selector", help="Capture only the first element matching this CSS selector")
    p.add_argument("--overlap", type=int, default=100, metavar="PX", help="Overlap between --scroll steps (100)")
    p.add_argument("--wait-ms", type=int, default=300, help="Settle time after load/scroll (300)")
    p.add_argument("--wait-until", choices=["networkidle", "load", "domcontentloaded"], default="networkidle",
                   help="Navigation readiness; use load for pages with long-lived connections")
    p.add_argument("--lazy", action="store_true", help="Pre-scroll once to trigger lazy-loaded content")
    p.add_argument("--theme", choices=["light", "dark"], default=None,
                   help="Emulate color scheme and toggle .dark / data-theme (default: untouched)")
    p.add_argument("--theme-key", default=None, help="localStorage key the page reads its theme from")
    add_browser_args(p)
    add_json_args(p)


def run(args):
    if list_devices(args, "screenshots"):
        return

    urls = list(dict.fromkeys(args.urls_pos + args.url))
    if not urls:
        sys.exit("Give at least one target (positional or --url).")
    # Validate every option before any browser starts (fast, offline, and no runaway jobs).
    check_file(args.storage_state, "--storage-state")
    if args.slices is not None and args.slices <= 0:
        sys.exit("--slices must be a positive integer")
    for name, val in (("--width", args.width), ("--height", args.height)):
        if val is not None and not 0 < val <= MAX_DIMENSION_PX:
            sys.exit(f"{name} must be between 1 and {MAX_DIMENSION_PX}, got {val}")
    if not 0 < args.scale <= MAX_SCALE:
        sys.exit(f"--scale must be between 0 and {MAX_SCALE}, got {args.scale}")
    if args.wait_ms < 0 or args.overlap < 0 or args.max_shots < 1:
        sys.exit("--wait-ms and --overlap cannot be negative, and --max-shots must be at least 1")
    if args.device and args.zoom != 100:
        sys.exit("--zoom cannot be combined with --device (a device profile fixes the viewport)")
    from playwright.sync_api import sync_playwright

    mode = ("scroll" if args.scroll else "slices" if args.slices else
            "selector" if args.selector else "full" if args.full_page else "viewport")
    series = mode in ("scroll", "slices")
    if args.output and (series or len(urls) > 1):
        sys.exit("--output is for one target in a single-image mode. "
                 "Use --output-dir for several targets, --scroll or --slices.")

    vw, vh = resolve_viewport(args)
    o = Opts(width=vw, height=vh, scale=args.scale, zoom=args.zoom,
             wait_ms=args.wait_ms, wait_until=args.wait_until, theme=args.theme,
             theme_key=args.theme_key, lazy=args.lazy, timeout=args.timeout,
             user_agent=args.user_agent, storage_state=args.storage_state)
    suffix = f"_{args.theme}" if args.theme else ""
    failures = []
    saved = []
    payload = {"command": "screenshots", "mode": mode, "files": saved, "failed": failures}

    with begin(args) as real:
        with sync_playwright() as p:
            if args.device:
                dev = resolve_device(p, args.device)
                o.width, o.height, o.device_cfg = dev["viewport"]["width"], dev["viewport"]["height"], dev
            if mode == "scroll" and not 0 <= args.overlap < o.css_height:
                sys.exit(f"--overlap ({args.overlap}px) must be smaller than the viewport height ({o.css_height}px), "
                         "otherwise every step would barely move")
            browser = p.chromium.launch(headless=not args.headed)
            try:
                for url in urls:
                    try:
                        page = open_page(browser, url, o)
                        try:
                            name = folder_name(normalize_url(url))
                            if series:
                                paths = shoot_series(page, Path(args.output_dir) / name, o, mode,
                                                     args.slices, args.overlap, suffix, args.max_shots)
                            else:
                                out = resolve_output(args.output) if args.output else \
                                    str(Path(args.output_dir) / name / f"1{suffix}.png")
                                paths = [shoot_single(page, out, o, mode == "full", args.selector)]
                        finally:
                            page.close()
                        for path in paths:
                            print(f"Saved: {path}")
                            saved.append(path)
                    except Exception as e:
                        failures.append({"url": url, "error": str(e)})
                        print(f"FAILED {url}: {e}", file=sys.stderr)
            finally:
                browser.close()
    emit(args, payload, real)
    if failures:
        sys.exit(f"{len(failures)} of {len(urls)} target(s) failed: "
                 + ", ".join(f["url"] for f in failures))


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_args(ap)
    try:
        run(ap.parse_args())
    except SystemExit:
        raise
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
