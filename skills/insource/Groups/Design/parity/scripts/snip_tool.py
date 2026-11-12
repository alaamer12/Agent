#!/usr/bin/env python3
"""
snip_tool.py — Windows window-capture library and CLI for parity workflows.

Why this exists
---------------
A parity harness must capture the *real* application window deterministically,
even when it is partially occluded or not the foreground window. The screen-
compositor route (``ImageGrab``) only works when the window is visible on top;
``PrintWindow`` asks the application to render itself into a caller-supplied
bitmap, which works for occluded windows and modern (UWP/WinUI/Electron)
compositors.

Two Windows facts this module handles that a naive ``ImageGrab`` does not:

1. **RTL-mirrored windows.** An app with ``WS_EX_LAYOUTRTL`` set (common in
   Arabic/Hebrew UIs) is mirrored at the GDI device-context level. The screen
   shows it correctly, but ``PrintWindow`` returns the raw mirrored bitmap.
   ``capture_window`` detects the style and flips the result back.
2. **DPI virtualisation.** Without per-monitor DPI awareness, Windows lies about
   window rectangles and captures come back blurry or cropped. Awareness is
   enabled at import time.

This module is intentionally a library first: ``capture_app.py``,
``parity_run.py``, ``parity_cut.py`` and ``run_suite.py`` import it. The CLI is
a thin diagnostic shell around the same functions (list candidates, capture
one window, capture the full virtual screen).

Requirements (Windows only):
    pip install pywin32 pillow psutil

CLI examples:
    python snip_tool.py --name app.exe --list
    python snip_tool.py --name app.exe --output shots/app.png
    python snip_tool.py --pid 12345 --output shots/app.png --debug
    python snip_tool.py --title "My App" --include-frame --output shots/framed.png
    python snip_tool.py --fullscreen --output shots/all-monitors.png

Exit codes: 0 = captured/listed, 1 = no match or capture failure.
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes
import logging
import os
import sys
import time
import traceback

from PIL import Image, ImageGrab

try:
    import win32api
    import win32con
    import win32gui
    import win32process
    import win32ui
except ImportError:  # pragma: no cover - dependency guard
    raise SystemExit(
        "snip_tool needs pywin32. Install it with:\n"
        "    pip install pywin32"
    )

try:
    import psutil
except ImportError:  # pragma: no cover - dependency guard
    raise SystemExit(
        "snip_tool needs psutil for process targeting. Install it with:\n"
        "    pip install psutil"
    )


# Make the process DPI aware so coordinates/captures are neither scaled nor blurry.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:  # pragma: no cover - older Windows
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


log = logging.getLogger("snip_tool")


# --------------------------------------------------------------------------- #
# Logging / small utilities
# --------------------------------------------------------------------------- #

def setup_logging(debug: bool = False) -> None:
    """Configure the module logger. ``--debug`` prints window/process filtering."""
    level = logging.DEBUG if debug else logging.WARNING
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    log.handlers.clear()
    log.addHandler(handler)
    log.setLevel(level)
    log.propagate = False


def get_virtual_screen_bounds() -> tuple[int, int, int, int]:
    """``(left, top, right, bottom)`` covering every monitor."""
    left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
    top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)
    width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
    height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
    return left, top, left + width, top + height


def sanitize_filename(name: str) -> str:
    """Replace characters Windows forbids in filenames."""
    import re

    return re.sub(r'[<>:"/\\|?*]', "_", name).strip() or "window"


# --------------------------------------------------------------------------- #
# Capture
# --------------------------------------------------------------------------- #

def is_rtl_mirrored_window(hwnd: int) -> bool:
    """True when the window has ``WS_EX_LAYOUTRTL`` (GDI mirrors its content)."""
    try:
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        mirrored = bool(ex_style & win32con.WS_EX_LAYOUTRTL)
        log.debug("is_rtl_mirrored_window: hwnd=%s ex_style=0x%X mirrored=%s",
                  hwnd, ex_style, mirrored)
        return mirrored
    except Exception as exc:  # pragma: no cover - defensive
        log.debug("is_rtl_mirrored_window: failed for hwnd=%s: %s", hwnd, exc)
        return False


def capture_window(hwnd: int, flip_override: bool | None = None) -> Image.Image:
    """Capture one window with ``PrintWindow`` (works while occluded).

    ``flip_override=None`` auto-detects ``WS_EX_LAYOUTRTL`` and corrects the
    mirrored bitmap; ``True``/``False`` forces the behaviour.
    """
    log.debug("capture_window: hwnd=%s title=%r", hwnd, win32gui.GetWindowText(hwnd))

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = max(right - left, 1), max(bottom - top, 1)
    log.debug("capture_window: rect=(%s,%s,%s,%s) size=%sx%s",
              left, top, right, bottom, width, height)

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    if not hwnd_dc:
        raise RuntimeError(f"GetWindowDC failed for hwnd {hwnd} (window may have closed)")
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    # PW_RENDERFULLCONTENT (2) renders modern compositors correctly; 0 is the
    # legacy fallback for windows that reject the newer flag.
    result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
    log.debug("capture_window: PrintWindow(flags=2) result=%s", result)
    if result == 0:
        result = ctypes.windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)
        log.debug("capture_window: PrintWindow(flags=0) result=%s", result)
    if result == 0:
        log.debug("capture_window: both PrintWindow attempts returned 0; image may be blank")

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)
    image = Image.frombuffer(
        "RGB",
        (bmpinfo["bmWidth"], bmpinfo["bmHeight"]),
        bmpstr, "raw", "BGRX", 0, 1,
    )

    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    should_flip = flip_override if flip_override is not None else is_rtl_mirrored_window(hwnd)
    if should_flip:
        log.debug("capture_window: flipping image horizontally to correct RTL mirroring")
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    log.debug("capture_window: produced image size=%s", image.size)
    return image


def capture_window_with_frame(hwnd: int) -> Image.Image:
    """Capture the *composited* on-screen window, native frame included.

    ``capture_window`` never contains the non-client chrome (title bar, caption
    buttons, DWM border). Use this when the question is "what does the real
    frame look like", accepting that the window must not be occluded.
    """
    log.debug("capture_window_with_frame: hwnd=%s", hwnd)

    # DWMWA_EXTENDED_FRAME_BOUNDS (9) is the true visible outer bounds; the
    # plain GetWindowRect includes invisible resize-border padding.
    rect = ctypes.wintypes.RECT()
    hresult = ctypes.windll.dwmapi.DwmGetWindowAttribute(
        ctypes.wintypes.HWND(hwnd),
        ctypes.wintypes.DWORD(9),
        ctypes.byref(rect),
        ctypes.sizeof(rect),
    )
    if hresult == 0:
        left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
    else:  # pragma: no cover - older Windows / DWM disabled
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        log.debug("capture_window_with_frame: DWM call failed (hresult=%s)", hresult)

    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception as exc:  # pragma: no cover - focus stealing protection
        log.debug("capture_window_with_frame: SetForegroundWindow failed: %s", exc)

    image = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)
    log.debug("capture_window_with_frame: produced image size=%s", image.size)
    return image


def capture_screen(box: tuple[int, int, int, int] | None = None) -> Image.Image:
    """Grab a screen rectangle (``None`` = every monitor)."""
    return ImageGrab.grab(bbox=box or get_virtual_screen_bounds(), all_screens=True)


# --------------------------------------------------------------------------- #
# Process / window targeting
# --------------------------------------------------------------------------- #

def get_process_name(pid: int) -> str | None:
    try:
        return psutil.Process(pid).name()
    except Exception as exc:  # pragma: no cover - process may exit mid-scan
        log.debug("get_process_name(%s) failed: %s", pid, exc)
        return None


def get_root_pids_for_name(name: str) -> list[int]:
    """Return the 'root' pids among processes named ``name`` (case-insensitive).

    Apps that spawn same-named helpers (Electron, browsers, IDEs) would
    otherwise match a renderer/GPU child process instead of the real window
    owner. A root pid is one whose parent is *not* also named ``name``. Falls
    back to every match when no clear root exists.
    """
    name_lower = name.lower()
    matches = []
    for proc in psutil.process_iter(["pid", "name", "ppid"]):
        try:
            pname = proc.info["name"]
            if pname and pname.lower() == name_lower:
                matches.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    match_pids = {m["pid"] for m in matches}
    roots = [m["pid"] for m in matches if m["ppid"] not in match_pids]
    result = roots if roots else [m["pid"] for m in matches]
    log.debug("get_root_pids_for_name(%r): %d match(es), roots=%s",
              name, len(matches), result)
    return result


def enum_visible_windows(include_hidden: bool = False) -> list[dict]:
    """Describe top-level windows.

    Default keeps visible windows with a non-empty title. ``include_hidden``
    also includes invisible/untitled top-level windows, which is how you
    diagnose tray-only, cloaked or minimised apps.
    """
    windows: list[dict] = []
    seen = {"total": 0, "kept": 0}

    def callback(hwnd, _):
        seen["total"] += 1
        visible = win32gui.IsWindowVisible(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if not include_hidden and not (visible and title):
            return True
        try:
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            area = max(0, r - l) * max(0, b - t)
            windows.append({
                "hwnd": hwnd,
                "pid": pid,
                "title": title or "(no title)",
                "rect": (l, t, r, b),
                "area": area,
                "visible": visible,
            })
            seen["kept"] += 1
        except Exception as exc:  # pragma: no cover - window vanished mid-enum
            log.debug("enum_visible_windows: skipping hwnd=%s: %s", hwnd, exc)
        return True

    win32gui.EnumWindows(callback, None)
    log.debug("enum_visible_windows(include_hidden=%s): scanned %d, kept %d",
              include_hidden, seen["total"], seen["kept"])
    return windows


def find_target_windows(
    name: str | None = None,
    pid: int | None = None,
    title: str | None = None,
    include_hidden: bool = False,
) -> list[dict]:
    """Find candidate windows by process name, pid and/or title substring.

    Results are sorted by window area so the main window is first. When
    filtering by name, root pids are preferred over helper processes.
    """
    candidates = enum_visible_windows(include_hidden=include_hidden)

    if pid is not None:
        candidates = [w for w in candidates if w["pid"] == pid]

    if name is not None:
        root_pids = set(get_root_pids_for_name(name))
        name_lower = name.lower()
        matched = [
            w for w in candidates
            if (get_process_name(w["pid"]) or "").lower() == name_lower
        ]
        preferred = [w for w in matched if w["pid"] in root_pids]
        candidates = preferred if preferred else matched

    if title:
        title_lower = title.lower()
        candidates = [w for w in candidates if title_lower in w["title"].lower()]

    candidates.sort(key=lambda w: w["area"], reverse=True)
    return candidates


def print_candidates(candidates: list[dict]) -> None:
    if not candidates:
        print("No matching windows found.")
        return
    print(f"{'PID':>7}  {'Process':<28} {'Size':<11} {'Visible':<8} Title")
    print("-" * 90)
    for w in candidates:
        proc = get_process_name(w["pid"]) or "?"
        l, t, r, b = w["rect"]
        size = f"{r - l}x{b - t}"
        visible = "yes" if w.get("visible", True) else "no"
        print(f"{w['pid']:>7}  {proc:<28.28} {size:<11} {visible:<8} {w['title']}")


def default_output_for_pid(pid: int, out_dir: str | None = None) -> str:
    """``<dir>/<processName>_<pid>.png`` (``.exe`` dropped)."""
    proc_name = get_process_name(pid) or "process"
    base = os.path.splitext(proc_name)[0]
    directory = out_dir or os.getcwd()
    return os.path.join(directory, f"{sanitize_filename(base)}_{pid}.png")


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snip_tool.py",
        description="Capture a window by process name, PID or title substring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  snip_tool.py --name notepad.exe\n"
            "  snip_tool.py --pid 12345\n"
            "  snip_tool.py --title \"Visual Studio Code\"\n"
            "  snip_tool.py --name chrome.exe --list\n"
            "  snip_tool.py --name chrome.exe --output shot.png\n"
            "  snip_tool.py --fullscreen --output screen.png\n"
        ),
    )
    target = parser.add_argument_group("target selection")
    target.add_argument("-n", "--name", help="process/executable name, e.g. notepad.exe")
    target.add_argument("-p", "--pid", type=int, help="exact process ID")
    target.add_argument("-t", "--title", help="substring matched against the window title")

    actions = parser.add_argument_group("actions")
    actions.add_argument("-l", "--list", action="store_true",
                         help="list matching windows instead of capturing")
    actions.add_argument("--include-hidden", action="store_true",
                         help="also consider hidden/untitled top-level windows")
    actions.add_argument("--fullscreen", action="store_true",
                         help="capture the whole virtual screen (ignores target filters)")
    actions.add_argument("--include-frame", action="store_true",
                         help="capture the on-screen window including native title bar "
                              "and DWM border instead of the client bitmap")

    out = parser.add_argument_group("output")
    out.add_argument("-o", "--output",
                     help="output PNG path (default: ./<processName>_<pid>.png)")
    out.add_argument("--wait", type=float, default=0.0,
                     help="seconds to sleep before capturing")

    mirror = parser.add_argument_group(
        "RTL / mirrored window correction",
        "RTL-layout windows can capture mirrored via PrintWindow; auto-detection "
        "corrects this by default.",
    )
    flip = mirror.add_mutually_exclusive_group()
    flip.add_argument("--flip-horizontal", action="store_true",
                      help="force a horizontal flip correction")
    flip.add_argument("--no-flip-fix", action="store_true",
                      help="disable the flip correction")

    parser.add_argument("--debug", action="store_true", help="verbose diagnostics")
    return parser


def _report_no_match(args: argparse.Namespace) -> None:
    print("No matching window found.", file=sys.stderr)
    if args.pid is not None:
        if psutil.pid_exists(args.pid):
            print(f"  PID {args.pid} exists but owns no visible titled top-level window now.",
                  file=sys.stderr)
            hidden = find_target_windows(pid=args.pid, include_hidden=True)
            if hidden:
                print(f"  It owns {len(hidden)} hidden/untitled window(s); "
                      f"re-run with --include-hidden --list.", file=sys.stderr)
        else:
            print(f"  PID {args.pid} is not running.", file=sys.stderr)
    if args.name:
        pids = get_root_pids_for_name(args.name)
        if pids:
            print(f"  Process '{args.name}' is running (pid(s): "
                  f"{', '.join(map(str, pids))}) but has no visible titled window.",
                  file=sys.stderr)
        else:
            print(f"  No running process named '{args.name}'.", file=sys.stderr)
    if args.title and not args.pid and not args.name:
        print(f"  No visible title contains '{args.title}'. "
              f"Try --include-hidden --list.", file=sys.stderr)


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.wait > 0:
        time.sleep(args.wait)

    if args.fullscreen:
        image = capture_screen()
        out = args.output or os.path.join(
            os.getcwd(), time.strftime("screen_%Y-%m-%d_%H-%M-%S.png"))
    else:
        if not (args.name or args.pid or args.title):
            build_arg_parser().print_help()
            return 0

        candidates = find_target_windows(
            name=args.name, pid=args.pid, title=args.title,
            include_hidden=args.include_hidden,
        )
        if args.list:
            print_candidates(candidates)
            return 0 if candidates else 1
        if not candidates:
            _report_no_match(args)
            return 1

        chosen = candidates[0]
        if len(candidates) > 1:
            print(f"Multiple matches; using the largest (PID {chosen['pid']}, "
                  f"{chosen['title']!r}). Use --list to see all {len(candidates)}.",
                  file=sys.stderr)

        flip = True if args.flip_horizontal else (False if args.no_flip_fix else None)
        image = (capture_window_with_frame(chosen["hwnd"]) if args.include_frame
                 else capture_window(chosen["hwnd"], flip_override=flip))
        out = args.output or default_output_for_pid(chosen["pid"])

    out_dir = os.path.dirname(os.path.abspath(out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    image.save(out)
    print(f"Saved: {out} ({image.width}x{image.height})")
    return 0


if __name__ == "__main__":
    setup_logging(debug="--debug" in sys.argv)
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:  # pragma: no cover - top-level guard
        print("ERROR: unexpected exception.", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        print("Re-run with --debug for details.", file=sys.stderr)
        sys.exit(1)
