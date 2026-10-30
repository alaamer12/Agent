"""Check that the capture commands can run here, and print the exact fix for anything missing.

Usage:
  python check_env.py            # report only
  python check_env.py --smoke    # also render examples/sample-designs end to end
"""
from __future__ import annotations

import argparse
import importlib
import os
import platform
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "..", "examples", "sample-designs")
INSTALL_IMAGES = ("pip install curl_cffi pillow "
                  "&& python -m playwright install chromium")


def line(ok, label, fix=""):
    print(f"[{'ok' if ok else '!!'}] {label}" + (f"\n     fix: {fix}" if not ok and fix else ""))
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    ok = True

    try:
        importlib.import_module("playwright")
        have_pw = line(True, "playwright (designs, screenshots, website, dom, images)")
    except ImportError:
        have_pw = line(False, "playwright (designs, screenshots, website, dom, images)", "pip install playwright")
    ok &= have_pw

    if have_pw:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                p.chromium.launch().close()
            line(True, "chromium browser")
        except Exception:
            ok &= line(False, "chromium browser", "playwright install chromium")

    import shutil
    have_curl = any(shutil.which(n) for n in (("curl.exe", "curl") if os.name == "nt" else ("curl", "curl.exe")))
    ok &= line(have_curl, "curl (design)", "install curl (Windows 10+ ships curl.exe)")

    print("\n`images` - needs curl_cffi (WAF/TLS impersonation) and Pillow (sizes, dedup)")
    for mod, pkg in (("curl_cffi", "curl_cffi"), ("PIL", "pillow")):
        try:
            importlib.import_module(mod)
            line(True, pkg)
        except ImportError:
            ok &= line(False, pkg, f"pip install {pkg}   # then: {INSTALL_IMAGES}")

    on_win = platform.system() == "Windows"
    print(f"\n`page` (optional, Windows only) - detected {platform.system()}")
    win_ok = False
    if on_win:
        win_ok = True
        for mod, pkg in (("win32gui", "pywin32"), ("psutil", "psutil")):
            try:
                importlib.import_module(mod)
                line(True, pkg)
            except ImportError:
                win_ok = line(False, pkg, f"pip install {pkg}")
        if not win_ok:
            print("     (pillow is shared with `images`; the check above covers it)")
    else:
        print("[--] skipped: window capture needs Windows (the targeting logic is still tested by --smoke)")

    if args.smoke and have_pw:
        out = tempfile.mkdtemp(prefix="capture-smoke-")
        cmd = [sys.executable, os.path.join(HERE, "capture.py"), "designs", "--dir", SAMPLE,
               "--themes", "light", "dark", "--theme-key", "sample-theme", "--out", out]
        r = subprocess.run(cmd, capture_output=True, text=True)
        n = sum(f.endswith(".png") for _, _, fs in os.walk(out) for f in fs)
        ok &= line(r.returncode == 0 and n == 4, f"smoke: designs ({n}/4 PNGs in {out})", r.stderr.strip())
        tall = os.path.join(HERE, "..", "examples", "tall-page.html")
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "screenshots", tall,
                            "--slices", "3", "--output-dir", os.path.join(out, "slices")],
                           capture_output=True, text=True)
        n = len(os.listdir(os.path.join(out, "slices", "tall-page"))) if r.returncode == 0 else 0
        ok &= line(n == 3, f"smoke: screenshots --slices 3 ({n}/3 PNGs)", r.stderr.strip())
        sys.path.insert(0, HERE)
        from designs import serve
        srv, base = serve(__import__("pathlib").Path(SAMPLE))
        site = os.path.join(out, "site")
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "website", base + "/index.html",
                            "--depth", "1", "--output-dir", site, "--wait-ms", "300", "--scroll-steps", "2"],
                           capture_output=True, text=True)
        srv.shutdown()
        good = (r.returncode == 0 and os.path.exists(os.path.join(site, "index.html"))
                and os.path.exists(os.path.join(site, "settings.html")) and "no failed requests" in r.stdout)
        ok &= line(good, "smoke: website --depth 1 (2 pages, verified)", (r.stderr or r.stdout).strip()[-300:])
        srv, base = serve(__import__("pathlib").Path(SAMPLE))
        dom_out = os.path.join(out, "dom.html")
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "dom", base + "/index.html",
                            "-o", dom_out, "--wait-ms", "300", "--max-rounds", "3", "--scroll-pause-ms", "200"],
                           capture_output=True, text=True)
        srv.shutdown()
        good = r.returncode == 0 and os.path.exists(dom_out) and "<h2>Projects</h2>" in open(dom_out, encoding="utf-8").read()
        ok &= line(good, "smoke: dom (rendered HTML saved)", (r.stderr or r.stdout).strip()[-300:])
        if have_curl:
            srv, base = serve(__import__("pathlib").Path(SAMPLE))
            dz = os.path.join(out, "design")
            r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "design", "both", base + "/index.html", "--out", dz],
                               capture_output=True, text=True)
            srv.shutdown()
            files = ("html.dump", "css.dump", "design-system.md", "design-patterns.md")
            good = r.returncode == 0 and all(os.path.exists(os.path.join(dz, f)) for f in files)
            ok &= line(good, "smoke: design both (curl dumps + tokens + patterns)", (r.stderr or r.stdout).strip()[-300:])
    if args.smoke:
        r = subprocess.run([sys.executable, os.path.join(HERE, "test_design.py")], capture_output=True, text=True)
        ok &= line(r.returncode == 0, "smoke: design logic (parser, charset, naming, local files)", (r.stdout + r.stderr).strip()[-400:])
        for script, label in (("test_robust.py", "smoke: robustness (fuzzing, pathological inputs, validation, limits)"),
                              ("test_tech.py", "smoke: technology evidence + structural heuristics + data files"),
                              ("test_dom.py", "smoke: dom (multilingual show-more, lazy media, safety)"),
                              ("test_website.py", "smoke: website (content-type link probing, long paths)")):
            r = subprocess.run([sys.executable, os.path.join(HERE, script)], capture_output=True, text=True)
            ok &= line(r.returncode == 0, label, (r.stdout + r.stderr).strip()[-400:])
        r = subprocess.run([sys.executable, os.path.join(HERE, "test_winshot.py")], capture_output=True, text=True)
        passed = r.returncode == 0
        ok &= line(passed, "smoke: page/winshot logic (fake Win32 layer)", (r.stdout + r.stderr).strip()[-400:])
        if on_win and win_ok:
            try:
                import winshot
                wins = winshot.find_target_windows()
                img = winshot.capture_window(wins[0]["hwnd"]) if wins else None
                ok &= line(img is not None and img.size[0] > 0 and img.size[1] > 0, "smoke: page (live window capture)",
                           "no visible windows found to capture" if not wins else "")
            except Exception as e:
                ok &= line(False, "smoke: page (live window capture)", str(e))
    if args.smoke and have_pw:
        if ok:
            shutil.rmtree(out, ignore_errors=True)
        else:
            print(f"     (test output kept for inspection: {out})")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    from _common import utf8_console
    utf8_console()
    main()
