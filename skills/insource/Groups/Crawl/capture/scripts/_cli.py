"""Shared CLI plumbing: canonical output flags, --json/--quiet, browser flags.

Every `capture` command follows the same contract:

  -o, --output FILE    one artifact (file). Format follows the extension (.md/.json/.png/.html).
  --output-dir DIR     a root folder. `--out` is kept as an alias.
  --json               machine-readable summary on stdout; progress moves to stderr.
  --quiet              no progress output.

Browser commands (`designs`, `screenshots`, `siteshots`, `website`, `dom`, `images`) share one flag group:

  --view, --width, --height, --scale, --device, --list-devices
  --timeout, --headed, --user-agent, --wait-ms, --wait-until
  --theme, --theme-key, --storage-state

Commands that only ever write a folder (`designs`, `website`, `images`) accept
`-o/--output` as another name for that folder, so `-o` works everywhere.
"""
from __future__ import annotations

import contextlib
import difflib
import json
import os
import sys

VIEW_PRESETS = {
    "desktop": (1280, 800),
    "wide": (1920, 1080),
    "tablet": (768, 1024),
    "mobile": (375, 812),
}


def add_output_args(p, *, single=True, default_dir=None, dir_help=None):
    """Register the canonical output flags.

    single=True  -> -o/--output FILE for one artifact; --output-dir/--out DIR for batches.
    single=False -> -o/--output/--output-dir/--out all name the destination folder.
    """
    if single:
        p.add_argument("-o", "--output", metavar="FILE",
                       help="Single artifact to write (PNG/HTML/MD/JSON); format follows the extension where supported")
        p.add_argument("--output-dir", "--out", dest="output_dir", metavar="DIR",
                       default=default_dir,
                       help=dir_help or "Root folder for multi-item runs")
    else:
        p.add_argument("-o", "--output", "--output-dir", "--out", dest="output_dir", metavar="DIR",
                       default=default_dir,
                       help=dir_help or "Destination folder")


def add_json_args(p):
    p.add_argument("--json", action="store_true", help="Print a machine-readable JSON summary on stdout")
    p.add_argument("--quiet", action="store_true", help="Suppress progress output")


def add_browser_args(p, *, timeout=30000, timeout_help=None, scale=False, user_agent=None, with_timeout=True):
    """Common Playwright knobs, with the same names on every browser-based command."""
    if with_timeout:
        p.add_argument("--timeout", type=int, default=timeout,
                       help=timeout_help or f"Navigation timeout in ms (default {timeout})")
    p.add_argument("--headed", action="store_true", help="Show the browser window (debugging)")
    p.add_argument("--user-agent", default=user_agent, help="Override the browser user agent")
    if scale:
        p.add_argument("--scale", type=float, default=1.0,
                       help="Device pixel ratio, e.g. 2 for retina (default 1)")


def add_view_args(p, *, default=None, width=None, height=None):
    """--view preset plus --width/--height overrides (same names everywhere)."""
    p.add_argument("--view", choices=list(VIEW_PRESETS), default=default,
                   help="Viewport preset: " + ", ".join(f"{k} {w}x{h}" for k, (w, h) in VIEW_PRESETS.items()))
    p.add_argument("--width", type=int, default=width, help="Override preset width")
    p.add_argument("--height", type=int, default=height, help="Override preset height")


def resolve_viewport(args, fallback=(1280, 800)) -> tuple[int, int]:
    """(width, height) from --width/--height, else --view, else the command's fallback."""
    vw, vh = VIEW_PRESETS.get(getattr(args, "view", None), fallback)
    width, height = getattr(args, "width", None), getattr(args, "height", None)
    return (vw if width is None else width, vh if height is None else height)


def add_device_args(p):
    p.add_argument("--device", metavar="NAME",
                   help="Emulate a real device with Playwright's maintained profile (viewport, user agent, "
                        "pixel ratio, touch), e.g. \"iPhone 13\"; see --list-devices")
    p.add_argument("--list-devices", action="store_true",
                   help="Print the device names Playwright knows and exit")


def resolve_device(p, name: str) -> dict:
    """Playwright device descriptor for --device, or exit with close matches."""
    dev = p.devices.get(name)
    if dev is None:
        close = difflib.get_close_matches(name, list(p.devices), n=4)
        sys.exit(f"Unknown device {name!r}."
                 + (f" Did you mean: {', '.join(close)}?" if close else "")
                 + " Use --list-devices.")
    return {k: v for k, v in dev.items() if k != "default_browser_type"}


def list_devices(args, command: str) -> bool:
    """Handle --list-devices: print known profiles and return True when the run is done."""
    if not getattr(args, "list_devices", False):
        return False
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        devices = sorted(p.devices)
    with begin(args) as real:
        print("\n".join(devices))
    emit(args, {"command": command, "devices": devices}, real)
    return True


def add_theme_args(p, *, default=None):
    p.add_argument("--theme", choices=["light", "dark"], default=default,
                   help="Emulate color scheme and toggle .dark / data-theme (default: untouched)")
    p.add_argument("--theme-key", default=None, help="localStorage key the page reads its theme from")


def add_session_args(p):
    p.add_argument("--storage-state", metavar="FILE",
                   help="Playwright storage-state JSON (cookies/login) to reuse")


def check_file(path, flag: str) -> None:
    if path and not os.path.isfile(path):
        sys.exit(f"{flag} file not found: {path}")


def seed_theme(page, theme, theme_key=None) -> None:
    """Seed localStorage before first paint (must be called before navigation)."""
    if theme and theme_key:
        page.add_init_script("try{localStorage.setItem(%r,%r)}catch(e){}" % (theme_key, theme))


def apply_theme(page, theme) -> None:
    """Toggle .dark / data-theme to match the emulated color scheme (call after navigation).

    Best effort: a page that navigated away mid-call must not abort the run.
    """
    if theme:
        try:
            page.evaluate("t=>{const r=document.documentElement;"
                          "r.classList.toggle('dark',t==='dark');r.setAttribute('data-theme',t)}", theme)
        except Exception:
            pass


@contextlib.contextmanager
def begin(args=None):
    """Move progress output off stdout while work runs; yield the real stdout.

    --json keeps progress visible on stderr; --quiet drops it; plain runs keep stdout.
    """
    quiet = bool(getattr(args, "quiet", False))
    as_json = bool(getattr(args, "json", False))
    real = sys.stdout
    sink = sys.stderr if as_json and not quiet else (open(os.devnull, "w", encoding="utf-8") if quiet else None)
    try:
        if sink is not None:
            sys.stdout = sink
        yield real
    finally:
        sys.stdout = real
        if sink is not None and sink is not sys.stderr:
            sink.close()


def emit(args, payload, real_stdout=None):
    """Print the JSON summary on the real stdout when --json is set."""
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2, ensure_ascii=False), file=real_stdout or sys.stdout)
