"""Logic tests for winshot using a fake Win32 layer (runs on any OS; needs Pillow).

  python test_winshot.py        # exit 0 = all passed

Covers targeting (root-process preference, filters, hidden windows, sorting), RTL flip correction,
and the no-match diagnostics. It does NOT exercise real Win32 calls; on Windows, `check_env.py --smoke`
additionally captures a live window.
"""
from __future__ import annotations

import io
import os
import shutil
import sys
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import winshot  # noqa: E402

try:
    from PIL import Image
except ImportError:
    print("SKIP: Pillow not installed")
    sys.exit(0)

RTL = 0x400000
# hwnd -> window; pids: 100 = App.exe root, 101 = App.exe helper (child of 100), 200 = Other.exe, 300 = Tray.exe
WINDOWS = {
    1: dict(pid=100, title="App - Main", rect=(0, 0, 1000, 800), visible=True, ex=0),
    2: dict(pid=101, title="App - Helper", rect=(0, 0, 1200, 900), visible=True, ex=0),   # bigger, but a helper
    3: dict(pid=200, title="Other window", rect=(0, 0, 300, 200), visible=True, ex=RTL),
    4: dict(pid=300, title="", rect=(0, 0, 10, 10), visible=False, ex=0),                 # hidden/untitled
}
PROCS = [dict(pid=100, name="App.exe", ppid=1), dict(pid=101, name="App.exe", ppid=100),
         dict(pid=200, name="Other.exe", ppid=1), dict(pid=300, name="Tray.exe", ppid=1)]
# 2x1 image in BGRX: left pixel red, right pixel blue
BITS = bytes([0, 0, 255, 0, 255, 0, 0, 0])


class _Bitmap:
    def CreateCompatibleBitmap(self, dc, w, h): self.w, self.h = w, h
    def GetInfo(self): return {"bmWidth": 2, "bmHeight": 1}
    def GetBitmapBits(self, _): return BITS
    def GetHandle(self): return 1


class _Dc:
    def CreateCompatibleDC(self): return self
    def SelectObject(self, b): pass
    def GetSafeHdc(self): return 1
    def DeleteDC(self): pass


class _NoSuch(Exception): pass
class _Denied(Exception): pass


def fake_win():
    gui = SimpleNamespace(
        IsWindowVisible=lambda h: WINDOWS[h]["visible"], GetWindowText=lambda h: WINDOWS[h]["title"],
        GetWindowRect=lambda h: WINDOWS[h]["rect"], GetWindowDC=lambda h: 1, ReleaseDC=lambda h, d: None,
        DeleteObject=lambda h: None, GetWindowLong=lambda h, i: WINDOWS[h]["ex"],
        IsIconic=lambda h: WINDOWS[h].get("minimized", False),
        GetClientRect=lambda h: (0, 0, WINDOWS[h]["rect"][2] - WINDOWS[h]["rect"][0] - _inset(h)[0] - _inset(h)[2],
                                 WINDOWS[h]["rect"][3] - WINDOWS[h]["rect"][1] - _inset(h)[1] - _inset(h)[3]),
        ClientToScreen=lambda h, pt: (WINDOWS[h]["rect"][0] + _inset(h)[0] + pt[0], WINDOWS[h]["rect"][1] + _inset(h)[1] + pt[1]),
        EnumWindows=lambda cb, x: [cb(h, x) for h in WINDOWS])
    ps = SimpleNamespace(
        process_iter=lambda attrs: [SimpleNamespace(info=dict(p)) for p in PROCS],
        Process=lambda pid: SimpleNamespace(name=lambda: next(p["name"] for p in PROCS if p["pid"] == pid)),
        pid_exists=lambda pid: any(p["pid"] == pid for p in PROCS), NoSuchProcess=_NoSuch, AccessDenied=_Denied)
    return SimpleNamespace(
        gui=gui, psutil=ps, con=SimpleNamespace(GWL_EXSTYLE=-20, WS_EX_LAYOUTRTL=RTL),
        process=SimpleNamespace(GetWindowThreadProcessId=lambda h: (0, WINDOWS[h]["pid"])),
        ui=SimpleNamespace(CreateDCFromHandle=lambda d: _Dc(), CreateBitmap=_Bitmap),
        user32=SimpleNamespace(PrintWindow=lambda h, d, f: 1), Image=Image, ImageGrab=None, dwmapi=None, api=None)


def _inset(h):
    return WINDOWS[h].get("inset", (0, 0, 0, 0))


def titles(c): return [w["title"] for w in c]


def run() -> int:
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    # import safety / clear error when Win32 is unavailable
    winshot._WIN = None
    if sys.platform != "win32":
        try:
            winshot.find_target_windows(name="x")
            check("clear RuntimeError off Windows", False)
        except RuntimeError as e:
            check("clear RuntimeError off Windows", "Windows" in str(e))

    winshot._WIN = fake_win()

    check("default listing: visible+titled, largest first", titles(winshot.find_target_windows()) == ["App - Helper", "App - Main", "Other window"])
    check("name prefers root process over bigger helper window", titles(winshot.find_target_windows(name="app.exe"))[0] == "App - Main")
    check("name match is case-insensitive and exact", titles(winshot.find_target_windows(name="OTHER.EXE")) == ["Other window"])
    check("pid filter", titles(winshot.find_target_windows(pid=101)) == ["App - Helper"])
    check("title substring filter (case-insensitive)", titles(winshot.find_target_windows(title="HELPER")) == ["App - Helper"])
    check("name + title combine", titles(winshot.find_target_windows(name="App.exe", title="main")) == ["App - Main"])
    check("name + title that only fits a helper window still finds it", titles(winshot.find_target_windows(name="App.exe", title="helper")) == ["App - Helper"])
    check("hidden windows excluded by default", winshot.find_target_windows(name="Tray.exe") == [])
    check("include_hidden returns them", titles(winshot.find_target_windows(name="Tray.exe", include_hidden=True)) == ["(no title)"])
    check("root pids exclude same-name children", winshot.get_root_pids_for_name("App.exe") == [100])

    # name whose root has no visible window falls back to matching helper windows
    saved = WINDOWS[1]["visible"]
    WINDOWS[1]["visible"] = False
    check("falls back to helper window when root is hidden", titles(winshot.find_target_windows(name="App.exe")) == ["App - Helper"])
    WINDOWS[1]["visible"] = saved

    # capture + RTL flip
    img = winshot.capture_window(1)
    check("normal window: not flipped", img.size == (2, 1) and img.getpixel((0, 0)) == (255, 0, 0))
    img = winshot.capture_window(3)
    check("RTL window: auto-flipped", img.getpixel((0, 0)) == (0, 0, 255))
    check("flip_override=False disables fix", winshot.capture_window(3, flip_override=False).getpixel((0, 0)) == (255, 0, 0))
    check("flip_override=True forces flip", winshot.capture_window(1, flip_override=True).getpixel((0, 0)) == (0, 0, 255))

    # exact client-area geometry
    WINDOWS[2]["inset"] = (8, 31, 8, 8)
    check("client_insets returns exact title-bar/border sizes", winshot.client_insets(2) == (8, 31, 8, 8))
    del WINDOWS[2]["inset"]
    check("client_insets is zero for a borderless window", winshot.client_insets(2) == (0, 0, 0, 0))

    # minimized windows
    WINDOWS[3]["minimized"] = True
    try:
        winshot.capture_window(3)
        check("minimized window raises a clear error", False)
    except RuntimeError as e:
        check("minimized window raises a clear error", "minimized" in str(e))
    check("minimized flag appears in listings", [w["minimized"] for w in winshot.find_target_windows(title="Other")] == [True])
    WINDOWS[3]["minimized"] = False

    # diagnostics
    def diag(**kw):
        buf = io.StringIO()
        with redirect_stderr(buf):
            winshot.report_no_match(**kw)
        return buf.getvalue()
    check("diagnose: no such process", "No running process named 'Nope.exe'" in diag(name="Nope.exe"))
    check("diagnose: pid not running", "not running" in diag(pid=999))
    check("diagnose: running but hidden", "hidden/untitled" in diag(name="Tray.exe"))
    check("diagnose: title miss", "No visible window title contains" in diag(title="zzz"))

    buf = io.StringIO()
    with redirect_stdout(buf):
        winshot.print_candidates(winshot.find_target_windows())
        winshot.print_candidates([])
    check("print_candidates renders table + empty message", "Process" in buf.getvalue() and "No matching windows" in buf.getvalue())

    # ---- `page` command end to end (fake Win32 + real Pillow) ----
    import argparse
    import tempfile
    import page

    def page_args(*argv):
        ap = argparse.ArgumentParser()
        page.add_args(ap)
        return ap.parse_args(list(argv))

    def page_run(*argv):
        buf, code = io.StringIO(), 0
        with redirect_stdout(buf), redirect_stderr(buf):
            try:
                page.run(page_args(*argv))
            except SystemExit as e:
                code = e.code if isinstance(e.code, int) else 1
                if isinstance(e.code, str):
                    buf.write(e.code)
        return code, buf.getvalue()

    tmp = tempfile.mkdtemp(prefix="winshot-test-")
    out = os.path.join(tmp, "app_v{n}.png")
    code, text = page_run("--name", "App.exe", "--output", out, "--no-crop")
    check("page: captures root window and saves PNG", code == 0 and os.path.exists(os.path.join(tmp, "app_v1.png")) and "Saved:" in text)
    code, text = page_run("--name", "App.exe", "--output", out, "--no-crop", "--target-size", "6x4", "--pad-color", "#102030")
    img = Image.open(os.path.join(tmp, "app_v2.png"))
    check("page: {n} numbering + target-size canvas + pad color", code == 0 and img.size == (6, 4) and img.getpixel((5, 3)) == (16, 32, 48))
    code, text = page_run("--list")
    check("page: --list with no filter lists visible windows", code == 0 and "App - Main" in text)
    code, text = page_run("--name", "App.exe")
    check("page: capture without --output is an error", code != 0 and "--output" in text)
    code, text = page_run("--output", out)
    check("page: capture without a target is an error", code != 0 and "--pid, --name or --title" in text)
    code, text = page_run("--name", "Nope.exe", "--output", out)
    check("page: no match exits 1 with a diagnosis", code == 1 and "No running process named" in text)
    code, text = page_run("--name", "App.exe", "--title", "Helper", "--output", os.path.join(tmp, "x.png"), "--no-crop")
    check("page: explicit --title beats the root-process preference", code == 0 and "Saved:" in text)
    code, text = page_run("--title", "App", "--output", os.path.join(tmp, "y.png"), "--no-crop")
    check("page: several matches note which window was used", code == 0 and "2 windows matched" in text and "App - Helper" in text)

    WINDOWS[1]["inset"] = (1, 0, 0, 0)
    code, text = page_run("--name", "App.exe", "--output", os.path.join(tmp, "c.png"), "--crop-client", "--no-flip-fix")
    cimg = Image.open(os.path.join(tmp, "c.png")) if os.path.exists(os.path.join(tmp, "c.png")) else None
    check("page: --crop-client crops exactly by the window geometry", code == 0 and cimg is not None and cimg.size == (1, 1) and cimg.getpixel((0, 0)) == (0, 0, 255))
    del WINDOWS[1]["inset"]
    code, text = page_run("--name", "App.exe", "--output", out, "--crop-client", "--no-crop")
    check("page: --crop-client rejects conflicting crop options", code != 0 and "--crop-client cannot be combined" in text)
    WINDOWS[3]["minimized"] = True
    code, text = page_run("--title", "Other", "--output", os.path.join(tmp, "m.png"), "--no-crop")
    check("page: minimized window stops with advice", code != 0 and "minimized" in text)
    WINDOWS[3]["minimized"] = False
    code, text = page_run("--name", "App.exe", "--output", out, "--target-size", "12ab")
    check("page: invalid --target-size is rejected before capturing", code != 0 and "--target-size must look like" in text)
    code, text = page_run("--name", "App.exe", "--output", out, "--pad-color", "red")
    check("page: invalid --pad-color is rejected", code != 0 and "--pad-color must be" in text)

    shutil.rmtree(tmp, ignore_errors=True)
    winshot._WIN = None
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all winshot logic tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run())
