"""Tests for `siteshots`: route discovery (sitemap recursion, gzip, entities, locale), slug
collapsing, and navigation-race-safe capture.

  python test_siteshots.py       # exit 0 = all passed (browser checks skip if Playwright/Chromium is absent)

The fixture publishes a sitemap index whose child sitemaps are *not* pages, a gzipped sitemap,
locale variants (`?lang=ar` / `?lang=en`) that must not both be captured, a `&amp;` querystring,
and a route that redirects client-side shortly after load.
"""
from __future__ import annotations

import gzip
import http.server
import importlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from urllib.parse import urlparse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>{title}</title></head>
<body style="margin:0;font:16px sans-serif">
<h1>{title}</h1>{extra}
<div style="height:700px;background:linear-gradient(#fafafa,#222)"></div>
</body></html>"""

INDEX = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<sitemap><loc>/sitemap-pages.xml</loc></sitemap>
<sitemap><loc>/sitemap-extra.xml.gz</loc></sitemap>
</sitemapindex>"""

PAGES = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
<url><loc>/eg?lang=ar</loc></url>
<url><loc>/eg/funds/alpha?lang=ar&amp;page=1</loc></url>
<url><loc>/eg/funds/beta?lang=ar</loc></url>
<url><loc>/eg/funds/gamma?lang=ar</loc></url>
<url><loc>/eg/about?lang=ar</loc><xhtml:link rel="alternate" hreflang="en" href="/eg/about?lang=en"/></url>
<url><loc>/eg/contact?lang=ar</loc></url>
<url><loc>/eg?lang=en</loc></url>
<url><loc>/eg/funds/alpha?lang=en</loc></url>
<url><loc>/sa/funds?lang=ar</loc></url>
<url><loc>/redirect?lang=ar</loc></url>
<url><loc>/sitemap-pages.xml</loc></url>
<url><loc>mailto:hi@example.com</loc></url>
</urlset>"""

EXTRA = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>/eg/gzip?lang=ar</loc></url>
</urlset>"""

ROBOTS = """User-agent: *
Allow: /
Sitemap: /sitemap-index.xml
"""


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

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/robots.txt":
            return self._send(200, "text/plain; charset=utf-8", ROBOTS.encode(), False)
        if route == "/sitemap-index.xml":
            return self._send(200, "application/xml; charset=utf-8", INDEX.encode(), False)
        if route == "/sitemap-pages.xml":
            return self._send(200, "application/xml; charset=utf-8", PAGES.encode(), False)
        if route == "/sitemap-extra.xml.gz":
            return self._send(200, "application/xml", gzip.compress(EXTRA.encode()), False)
        if route == "/":
            links = '<a href="/eg/about?lang=ar">a</a>'
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.format(title="home", extra=links).encode(), False)
        if route == "/eg":
            links = ('<a href="/eg/about?lang=ar">about</a>'
                     '<a href="/eg/funds/alpha?lang=ar">fund</a>'
                     '<a href="https://example.com/out">external</a>')
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.format(title="eg", extra=links).encode(), False)
        if route == "/redirect":
            script = "<script>setTimeout(function(){location.href='/final'},250)</script>"
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.format(title="redirect", extra=script).encode(), False)
        if route == "/final":
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.format(title="final", extra="").encode(), False)
        if route in ("/eg/about", "/eg/contact", "/eg/gzip", "/eg/funds/alpha",
                     "/eg/funds/beta", "/eg/funds/gamma", "/eg/funds", "/sa/funds"):
            return self._send(200, "text/html; charset=utf-8",
                              PAGE.format(title=route, extra="").encode(), False)
        return self._send(404, "text/plain", b"nope", False)

    def do_HEAD(self):
        route = urlparse(self.path).path
        self._send(200, "text/html; charset=utf-8", PAGE.format(title="head", extra="").encode(), True)


def run_cli(*argv: str, timeout: int = 240):
    return subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "siteshots", *argv],
                          capture_output=True, text=True, timeout=timeout)


def main() -> int:
    try:
        importlib.import_module("playwright")
    except ImportError:
        print("SKIP: Playwright not installed")
        return 0

    import siteshots as s

    failures: list[str] = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}"
    entry = f"{base}/eg?lang=ar"
    tmp = tempfile.mkdtemp(prefix="siteshots-test-")
    try:
        # ── discovery, without a browser ──────────────────────────────────────
        found = s.discover_sitemap(entry, 8000)
        check("robots-declared sitemap index is read", bool(found))
        if found:
            routes, method = found
            check("method names robots.txt", method == "sitemap (robots.txt)")
            check("index child sitemap is expanded, not captured as a page",
                  f"{base}/sitemap-pages.xml" not in routes and not any(u.endswith(".xml") for u in routes))
            check("gzipped child sitemap is expanded", f"{base}/eg/gzip?lang=ar" in routes)
            check("&amp; is decoded in sitemap URLs", f"{base}/eg/funds/alpha?lang=ar&page=1" in routes)
            check("xhtml:link alternate is read as a page URL", f"{base}/eg/about?lang=en" in routes)
            check("mailto: loc is dropped", not any(u.startswith("mailto:") for u in routes))

            kept = s.apply_locale_filter(routes, entry)
            check("locale filter keeps the entry's language", all("lang=ar" in u for u in kept))
            check("locale filter drops the other language", not any("lang=en" in u for u in kept))
            check("locale filter keeps the entry's path prefix",
                  f"{base}/eg/about?lang=ar" in kept and f"{base}/eg?lang=ar" in kept)
            check("locale filter drops a sibling locale tree", not any("/sa/" in u for u in kept))
            check("locale filter keeps shared non-locale paths", any(u.endswith("/redirect?lang=ar") for u in kept))

        collapsed, patterns = s.collapse_by_slug([
            f"{base}/products/alpha", f"{base}/products/beta", f"{base}/products/gamma",
            f"{base}/about",
        ], entry)
        check("slug family collapses to one real capture target",
              len(collapsed) == 2 and all(c.startswith(base) for c in collapsed))
        check("collapsed pattern keeps a real example",
              any(p["type"] == "dynamic" and p["example"] in collapsed
                  and "/products/" in p["example"] for p in patterns))
        check("static names stay separate", f"{base}/about" in collapsed)

        locale_target, _ = s.collapse_by_slug([f"{base}/eg?lang=ar", f"{base}/eg?lang=en"], entry)
        check("collapsing keeps the entry's locale variant", locale_target == [f"{base}/eg?lang=ar"])

        manual = s.parse_manual_routes("[about, /eg/contact, https://x.test/y]", entry)
        check("manual routes accept bare, rooted and absolute forms",
              manual == [f"{base}/about", f"{base}/eg/contact", "https://x.test/y"])

        # ── capture from the sitemap ──────────────────────────────────────────
        out1 = os.path.join(tmp, "sitemap")
        r1 = run_cli(entry, "--output-dir", out1, "--json", "--width", "300", "--height", "200",
                     "--overlap", "20", "--wait-ms", "120", "--max-pages", "9", "--timeout", "15000")
        blended = r1.stdout + r1.stderr
        if r1.returncode != 0 and ("Executable doesn't exist" in blended or "playwright install" in blended):
            print("SKIP: Chromium not installed")
            return 0
        check("sitemap capture exits 0", r1.returncode == 0)
        payload = json.loads(r1.stdout) if r1.returncode == 0 else {}
        report_file = os.path.join(out1, "report.json")
        check("report.json is written", os.path.isfile(report_file))
        report = json.loads(open(report_file, encoding="utf-8").read()) if os.path.isfile(report_file) else {}
        meta = report.get("meta", {})
        check("report records the sitemap method", str(meta.get("method", "")).startswith("sitemap"))
        check("--json emits the same summary", payload.get("summary") == report.get("summary"))
        captured = [p["url"] for p in report.get("pages", {}).get("succeeded", [])]
        variants = [v for p in report.get("routes", {}).get("patterns", []) for v in p.get("variants", [])]
        check("entry route captured with its locale", entry in captured)
        check("no other language captured", not any("lang=en" in u for u in captured))
        check("no sitemap XML captured", not any(u.endswith(".xml") for u in captured))
        check("client-side redirect route is captured, not errored",
              any("/redirect" in u for u in captured)
              and report.get("summary", {}).get("errored") == 0)
        check("gzipped sitemap route captured", any("/eg/gzip" in u for u in captured))
        check("slug family captured once, as its pattern example",
              sum(1 for u in captured if "/eg/funds/" in u) == 1)
        check("entity-decoded querystring survives discovery",
              any(v.endswith("/alpha?lang=ar&page=1") for v in variants))
        dirs = [os.path.join(out1, p["dir"]) for p in report.get("pages", {}).get("succeeded", [])]
        check("every captured route has at least one image",
              bool(dirs) and all(os.path.isdir(d) and any(f.endswith(".png") for f in os.listdir(d)) for d in dirs))

        # ── capture from the crawler ──────────────────────────────────────────
        out2 = os.path.join(tmp, "crawl")
        r2 = run_cli(entry, "--force-crawl", "--max-depth", "1", "--max-pages", "5",
                     "--output-dir", out2, "--json", "--width", "300", "--height", "200",
                     "--overlap", "20", "--wait-ms", "80", "--timeout", "15000")
        check("crawler capture exits 0", r2.returncode == 0)
        crawl_payload = json.loads(r2.stdout) if r2.returncode == 0 else {}
        crawled = [p["url"] for p in crawl_payload.get("pages", {}).get("succeeded", [])]
        check("--force-crawl uses the Playwright crawler", crawl_payload.get("method") == "playwright")
        check("crawler found same-origin routes", bool(crawled) and all(u.startswith(base) for u in crawled))
        check("crawler ignored the external link", not any("example.com" in u for u in crawled))

        # ── capture from manual routes ────────────────────────────────────────
        out3 = os.path.join(tmp, "manual")
        r3 = run_cli(entry, "--routes", "/eg/about?lang=ar, /eg/contact?lang=ar",
                     "--output-dir", out3, "--json", "--width", "300", "--height", "200",
                     "--overlap", "20", "--wait-ms", "80", "--timeout", "15000")
        check("manual-route capture exits 0", r3.returncode == 0)
        manual_payload = json.loads(r3.stdout) if r3.returncode == 0 else {}
        check("--routes skips discovery", manual_payload.get("method") == "manual"
              and manual_payload.get("summary", {}).get("total") == 2)
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all siteshots tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
