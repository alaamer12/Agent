"""winshot: headless Windows window capture with smart process/window targeting.

Used by `capture page`. Windows only (Win32 APIs); importing this module is safe on any OS,
the Windows-specific dependencies load on first use and fail with a clear message.

Requirements (Windows):  pip install pywin32 psutil pillow

Public API
    find_target_windows(name=None, pid=None, title=None, include_hidden=False) -> list[dict]
    capture_window(hwnd, flip_override=None) -> PIL.Image            (PrintWindow: works while occluded)
    capture_window_with_frame(hwnd) -> PIL.Image                     (real screen pixels incl. title bar)
    enum_visible_windows(include_hidden=False), get_process_name(pid), get_root_pids_for_name(name)
    print_candidates(candidates), report_no_match(name, pid, title), setup_logging(debug)

Targeting notes
    Electron apps, browsers and IDEs run many helper processes under the same executable name,
    and only one owns the real main window. When targeting by name, processes whose parent has
    the same name are treated as helpers; among the remaining root processes the largest visible
    top-level window wins. Candidates are always sorted largest-first.
"""
from __future__ import annotations

import ctypes
import logging
import sys
import time
from types import SimpleNamespace

log = logging.getLogger("winshot")
_WIN = None   # lazily populated Win32 handle bundle (tests inject a fake)


def setup_logging(debug: bool = False) -> None:
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    log.handlers.clear()
    log.addHandler(handler)
    log.setLevel(logging.DEBUG if debug else logging.WARNING)
    log.propagate = False


def _w():
    """Load Windows-only dependencies on first use (and make the process DPI aware)."""
    global _WIN
    if _WIN is not None:
        return _WIN
    if sys.platform != "win32":
        raise RuntimeError("Window capture needs Windows (Win32 APIs); `page` is not available on this OS.")
    try:
        import psutil
        import win32api
        import win32con
        import win32gui
        import win32process
        import win32ui
        from PIL import Image, ImageGrab
    except ImportError as e:
        raise RuntimeError(f"Missing dependency '{e.name}'. Install: pip install pywin32 psutil pillow") from e
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)      # per-monitor DPI aware: true pixel sizes
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass
    _WIN = SimpleNamespace(api=win32api, con=win32con, gui=win32gui, process=win32process, ui=win32ui,
                           psutil=psutil, Image=Image, ImageGrab=ImageGrab,
                           user32=ctypes.windll.user32, dwmapi=ctypes.windll.dwmapi)
    return _WIN


# ---------- capture ----------

def is_rtl_mirrored_window(hwnd) -> bool:
    """True if the window has WS_EX_LAYOUTRTL (Arabic/Hebrew UI). GDI mirrors those windows at the
    device-context level; the compositor shows them correctly but PrintWindow returns the physically
    mirrored bitmap, so captures come out flipped left-right unless corrected."""
    W = _w()
    try:
        ex = W.gui.GetWindowLong(hwnd, W.con.GWL_EXSTYLE)
        mirrored = bool(ex & W.con.WS_EX_LAYOUTRTL)
        log.debug("is_rtl_mirrored_window: hwnd=%s ex_style=0x%X mirrored=%s", hwnd, ex, mirrored)
        return mirrored
    except Exception as e:
        log.debug("is_rtl_mirrored_window: cannot read style for hwnd=%s: %s", hwnd, e)
        return False


def _require_restored(W, hwnd) -> None:
    if W.gui.IsIconic(hwnd):
        raise RuntimeError("The window is minimized, so there is nothing to render. Restore it first, then capture again.")


def capture_window(hwnd, flip_override=None):
    """Capture a window by handle with PrintWindow (works when occluded or in the background).

    flip_override: None = auto-detect RTL mirroring and correct it; True = always flip; False = never.
    """
    W = _w()
    _require_restored(W, hwnd)
    log.debug("capture_window: hwnd=%s title=%r", hwnd, W.gui.GetWindowText(hwnd))
    left, top, right, bottom = W.gui.GetWindowRect(hwnd)
    width, height = max(right - left, 1), max(bottom - top, 1)

    hwnd_dc = W.gui.GetWindowDC(hwnd)
    if not hwnd_dc:
        raise RuntimeError(f"GetWindowDC failed for hwnd {hwnd} (window may have closed)")
    mfc_dc = W.ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = W.ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)
    try:
        # PW_RENDERFULLCONTENT (2) renders modern apps (UWP, browsers, GPU surfaces) correctly
        result = W.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)
        if result == 0:
            result = W.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 0)
        if result == 0:
            log.debug("capture_window: PrintWindow failed (GetLastError=%s); image may be blank", ctypes.GetLastError())
        info = bitmap.GetInfo()
        image = W.Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]),
                                   bitmap.GetBitmapBits(True), "raw", "BGRX", 0, 1)
    finally:
        W.gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        W.gui.ReleaseDC(hwnd, hwnd_dc)

    flip = flip_override if flip_override is not None else is_rtl_mirrored_window(hwnd)
    if flip:
        log.debug("capture_window: flipping horizontally to correct RTL mirroring")
        image = image.transpose(getattr(W.Image, "Transpose", W.Image).FLIP_LEFT_RIGHT)
    return image


def client_insets(hwnd) -> tuple[int, int, int, int]:
    """(left, top, right, bottom) pixels between the window rectangle and its client area: the exact size of the
    title bar and borders from Win32 geometry (DPI-aware), so a PrintWindow capture can be cropped to the client
    area without guessing from pixel colours."""
    W = _w()
    l, t, r, b = W.gui.GetWindowRect(hwnd)
    _cl, _ct, cr, cb = W.gui.GetClientRect(hwnd)
    ox, oy = W.gui.ClientToScreen(hwnd, (0, 0))
    return (max(0, ox - l), max(0, oy - t), max(0, r - (ox + cr)), max(0, b - (oy + cb)))


def capture_window_with_frame(hwnd):
    """Capture a window INCLUDING its OS-drawn frame (title bar, caption buttons) from real screen pixels.

    PrintWindow never renders the non-client chrome that DWM composites; this reads the composited
    screen instead, so the window is brought to the foreground first and must not be covered.
    """
    import ctypes.wintypes as wt
    W = _w()
    _require_restored(W, hwnd)
    rect = wt.RECT()
    hr = W.dwmapi.DwmGetWindowAttribute(wt.HWND(hwnd), wt.DWORD(9), ctypes.byref(rect), ctypes.sizeof(rect))  # DWMWA_EXTENDED_FRAME_BOUNDS
    if hr == 0:
        box = (rect.left, rect.top, rect.right, rect.bottom)
    else:
        box = W.gui.GetWindowRect(hwnd)
        log.debug("capture_window_with_frame: DWM bounds failed (hresult=%s); using GetWindowRect", hr)
    try:
        W.gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception as e:
        log.debug("capture_window_with_frame: SetForegroundWindow failed: %s", e)
    return W.ImageGrab.grab(bbox=box, all_screens=True)


# ---------- targeting ----------

def get_process_name(pid):
    try:
        return _w().psutil.Process(pid).name()
    except RuntimeError:
        raise
    except Exception as e:
        log.debug("get_process_name(%s) failed: %s", pid, e)
        return None


def get_root_pids_for_name(name: str) -> list[int]:
    """PIDs of processes called `name` (case-insensitive) whose parent does NOT share the name,
    i.e. the app's root process rather than its helpers. Falls back to all matches if none qualify."""
    ps = _w().psutil
    lowered = name.lower()
    matches = []
    for p in ps.process_iter(["pid", "name", "ppid"]):
        try:
            if p.info["name"] and p.info["name"].lower() == lowered:
                matches.append(p.info)
        except (ps.NoSuchProcess, ps.AccessDenied):
            continue
    pids = {m["pid"] for m in matches}
    roots = [m["pid"] for m in matches if m["ppid"] not in pids]
    log.debug("get_root_pids_for_name(%r): %d match(es), roots=%s", name, len(matches), roots)
    return roots or [m["pid"] for m in matches]


def enum_visible_windows(include_hidden: bool = False) -> list[dict]:
    """Top-level windows as dicts {hwnd, pid, title, rect, area, visible}. By default only visible,
    titled windows; include_hidden=True also returns invisible/untitled ones (tray apps, cloaked)."""
    W = _w()
    out: list[dict] = []

    def cb(hwnd, _):
        visible = W.gui.IsWindowVisible(hwnd)
        title = W.gui.GetWindowText(hwnd)
        if not include_hidden and not (visible and title):
            return True
        try:
            _, pid = W.process.GetWindowThreadProcessId(hwnd)
            l, t, r, b = W.gui.GetWindowRect(hwnd)
            out.append({"hwnd": hwnd, "pid": pid, "title": title or "(no title)", "rect": (l, t, r, b),
                        "area": max(0, r - l) * max(0, b - t), "visible": bool(visible),
                        "minimized": bool(W.gui.IsIconic(hwnd))})
        except Exception as e:
            log.debug("enum_visible_windows: skipping hwnd=%s: %s", hwnd, e)
        return True

    W.gui.EnumWindows(cb, None)
    return out


def find_target_windows(name=None, pid=None, title=None, include_hidden=False) -> list[dict]:
    """Windows matching a process name, pid and/or title substring (all given filters must match).
    When several windows of the named process remain, those on its root process are preferred
    (not its helpers). Largest window first."""
    cands = enum_visible_windows(include_hidden)
    if pid is not None:
        cands = [w for w in cands if w["pid"] == pid]
    if title:       # explicit filters first; the root-process preference below is only a tiebreak
        cands = [w for w in cands if title.lower() in w["title"].lower()]
    if name is not None:
        roots = set(get_root_pids_for_name(name))
        lowered = name.lower()
        matched = [w for w in cands if (get_process_name(w["pid"]) or "").lower() == lowered]
        preferred = [w for w in matched if w["pid"] in roots]
        cands = preferred or matched
    cands.sort(key=lambda w: w["area"], reverse=True)
    log.debug("find_target_windows: %d candidate(s)", len(cands))
    return cands


def print_candidates(cands: list[dict]) -> None:
    if not cands:
        print("No matching windows found.")
        return
    print(f"{'PID':>7}  {'Process':<28} {'Size':<11} {'Visible':<8} Title")
    print("-" * 90)
    for w in cands:
        l, t, r, b = w["rect"]
        print(f"{w['pid']:>7}  {(get_process_name(w['pid']) or '?'):<28.28} {f'{r - l}x{b - t}':<11} "
              f"{'yes' if w.get('visible', True) else 'no':<8} {w['title']}{' [minimized]' if w.get('minimized') else ''}")


def report_no_match(name=None, pid=None, title=None) -> None:
    """Explain WHY nothing matched (no such process vs. process without a visible titled window)."""
    err = lambda m: print(m, file=sys.stderr)
    ps = _w().psutil
    err("No matching window found.")
    if pid is not None:
        if ps.pid_exists(pid):
            err(f"  PID {pid} exists (process: {get_process_name(pid) or '?'}) but has no visible titled top-level window.")
            hidden = find_target_windows(pid=pid, include_hidden=True)
            err(f"  It owns {len(hidden)} hidden/untitled top-level window(s); re-run with --include-hidden --list."
                if hidden else "  It owns no top-level window (background/tray process, or the window is a child window).")
        else:
            err(f"  PID {pid} is not running.")
    if name:
        pids = get_root_pids_for_name(name)
        if pids:
            err(f"  '{name}' is running (pid(s): {', '.join(map(str, pids))}) but none has a visible titled top-level window.")
            hidden = find_target_windows(name=name, include_hidden=True)
            if hidden:
                err(f"  {len(hidden)} hidden/untitled window(s) exist for it; re-run with --include-hidden --list.")
        else:
            err(f"  No running process named '{name}'.")
    if title and pid is None and not name:
        err(f"  No visible window title contains '{title}'. Try --include-hidden --list.")
