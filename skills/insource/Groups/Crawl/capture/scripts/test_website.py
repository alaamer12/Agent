"""Browser test for `website`: content-type link probing, long paths, extensionless pages. Needs Playwright.

  python test_website.py        # exit 0 = all passed (skips if Playwright/Chromium is unavailable)
"""
from __future__ import annotations

import http.server
import importlib
import os
import shutil
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
LONG = "a" * 300


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, status, ctype, body, head=False):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if not head:
            self.wfile.write(body)

    def _route(self, head):
        if self.path == "/":
            links = f'<a href="/page2">p2</a><a href="/download">dl</a><a href="/doc.pdf">pdf</a><a href="/{LONG}.html">long</a>'
            return self._send(200, "text/html; charset=utf-8", f"<!doctype html><title>home</title><h1>home</h1>{links}".encode(), head)
        if self.path == "/page2" or self.path == f"/{LONG}.html":
            return self._send(200, "text/html; charset=utf-8", b"<!doctype html><title>p</title><h1>inner page</h1>", head)
        if self.path == "/download":                      # extensionless download: only the Content-Type reveals it
            return self._send(200, "application/zip", b"PK\x03\x04" + b"0" * 64, head)
        if self.path == "/doc.pdf":
            return self._send(200, "application/pdf", b"%PDF-1.4 fake", head)
        return self._send(404, "text/plain", b"nope", head)

    def do_GET(self):
        self._route(False)

    def do_HEAD(self):
        self._route(True)


def main() -> int:
    try:
        importlib.import_module("playwright")
    except ImportError:
        print("SKIP: Playwright not installed")
        return 0
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = tempfile.mkdtemp(prefix="website-test-")
    site = os.path.join(tmp, "site")
    try:
        r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "website", f"http://127.0.0.1:{srv.server_address[1]}/",
                            "--depth", "1", "--output-dir", site, "--no-verify", "--wait-ms", "100", "--scroll-steps", "0"],
                           capture_output=True, text=True, timeout=120)
    except Exception as e:
        print("SKIP: browser not usable here:", e)
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
        return 0
    if r.returncode != 0 and "Executable doesn't exist" in (r.stderr + r.stdout):
        print("SKIP: Chromium not installed")
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
        return 0
    files = [os.path.relpath(os.path.join(d, f), site) for d, _, fs in os.walk(site) for f in fs]
    out = r.stdout + r.stderr
    check("crawl succeeded", r.returncode == 0)
    check("extensionless HTML page saved as <route>/index.html", os.path.join("page2", "index.html") in files)
    check("extensionless download skipped by Content-Type (not by extension)", "download" not in " ".join(files) and f"skipping non-page link http://127.0.0.1:{srv.server_address[1]}/download" in out)
    check("PDF skipped by Content-Type", "doc.pdf" not in " ".join(files) and "/doc.pdf" in out and "skipping non-page link" in out)
    longs = [f for f in files if f.endswith(".html") and "aaaa" in f]
    check("over-long path segment is shortened to a safe filename", bool(longs) and all(len(os.path.basename(f)) <= 100 for f in longs))
    check("no save errors reported", "save error" not in out)
    srv.shutdown()
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all website tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
