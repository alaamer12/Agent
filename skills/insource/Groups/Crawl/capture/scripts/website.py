"""Download a whole website for offline use, driven by a real browser (Playwright/Chromium).

A real browser executes the site's JavaScript, so assets that plain HTTP crawlers miss
(lazy-loaded chunks, fetched JSON, fonts, wasm, models) are captured as they are requested.
After the download, a verification pass re-opens the local copy and reports anything that 404s
or still needs the internet.

Usage:
  python website.py https://example.com                       # entry page + every asset it loads
  python website.py https://example.com --depth 2 --max-pages 40   # also follow same-site links
  python website.py https://example.com --external fonts.googleapis.com fonts.gstatic.com
  python website.py https://example.com --serve --open        # then serve the copy locally
  python website.py --serve-only .capture/website/example.com # serve an existing copy

Only mirror sites you own or are permitted to copy, and don't republish them.
Requires: pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import hashlib
import functools
import http.server
import json
import os
import re
import sys
import threading
import time
from pathlib import Path
from urllib import robotparser
from urllib.parse import unquote, urldefrag, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import (add_browser_args, add_device_args, add_json_args, add_output_args,  # noqa: E402
                  add_session_args, add_theme_args, add_view_args, begin, check_file, emit,
                  list_devices, resolve_device, resolve_viewport, seed_theme, apply_theme)
from _data import host_listed, load_lines  # noqa: E402

VIEW = (1920, 1080)
RAW_EXT = (".woff2", ".woff", ".ttf", ".otf", ".wasm")
TEXT_EXT = (".html", ".htm", ".js", ".mjs", ".css", ".json", ".svg", ".xml", ".txt", ".webmanifest", ".map")
MAX_SEGMENT_CHARS = 100        # URL path segments longer than this are shortened (with a hash) to fit filesystem limits
HEAD_TIMEOUT_MS = 10000        # timeout of the content-type probe made before visiting a crawled link



# ---------- small helpers ----------
def normalize(url: str) -> str:
    if "://" in url:
        return url
    host = url.split("/")[0].split(":")[0]
    return f"{'http' if host in ('localhost', '127.0.0.1', '0.0.0.0') else 'https'}://{url}"


def safe_netloc(netloc: str) -> str:
    return re.sub(r"[^\w.-]", "_", netloc)


def is_text(content_type: str, path: str) -> bool:
    ct = content_type.lower()
    return any(t in ct for t in ("text", "javascript", "json", "xml", "svg")) or path.lower().endswith(TEXT_EXT)


def blocklist(args) -> list[str]:
    """Hosts never saved as external assets: data/trackers.txt (unless disabled) plus --block hosts."""
    base = [] if args.no_default_blocklist else list(load_lines("trackers.txt"))
    return base + [h.lower() for h in (args.block or [])]


def external_allowed(u, allow: list[str] | None, block: list[str]) -> bool:
    """allow=None: externals off. []: all except blocked hosts. [..]: only the listed hosts (never blocked ones)."""
    if allow is None or host_listed(u.hostname or "", block):
        return False
    if not allow:
        return True
    return any(a in (u.hostname, u.netloc) or (u.hostname or "").endswith("." + a) for a in allow)


def _safe_segment(seg: str) -> str:
    """Shorten an over-long path segment (keeping a short extension) so it fits filesystem name limits."""
    if len(seg) <= MAX_SEGMENT_CHARS:
        return seg
    _stem, dot, ext = seg.rpartition(".")
    ext = ext if dot and len(ext) <= 10 else ""
    digest = hashlib.md5(seg.encode()).hexdigest()[:8]
    return seg[:MAX_SEGMENT_CHARS - 10 - len(ext)] + "_" + digest + ("." + ext if ext else "")


def is_html_url(ctx, url: str) -> bool:
    """HEAD probe: skip links that are clearly not pages (PDF, archive, image, media) by their Content-Type.
    Unknown (HEAD unsupported, error, no header) means allow, so a failing probe never hides a page."""
    try:
        r = ctx.request.head(url, timeout=HEAD_TIMEOUT_MS)
    except Exception:
        return True
    ct = (r.headers.get("content-type") or "").lower()
    if r.status in (405, 501) or not ct:
        return True
    return "html" in ct or "xml" in ct


def local_path(root: Path, url: str, content_type: str, same_origin: bool) -> Path:
    u = urlparse(url)
    path = unquote(u.path)
    segs = [_safe_segment(re.sub(r'[<>:"|?*\\]', "_", s)) for s in path.split("/") if s not in ("", ".", "..")]
    if not segs or path.endswith("/"):
        segs.append("index.html")
    elif "html" in content_type.lower() and "." not in segs[-1]:
        segs.append("index.html")      # /about  ->  about/index.html (avoids file/dir clashes)
    base = root if same_origin else root / "_external" / safe_netloc(u.netloc)
    return base.joinpath(*segs)


# ---------- local server (verification and --serve) ----------
class _Handler(http.server.SimpleHTTPRequestHandler):
    spa = False

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        super().end_headers()

    def translate_path(self, path):
        p = super().translate_path(path)
        if self.spa and not os.path.exists(p) and not os.path.splitext(p)[1]:
            return os.path.join(self.directory, "index.html")   # client-side routes
        return p

    def log_message(self, *a):
        pass


def make_server(root: Path, port: int = 0, spa: bool = False):
    cls = type("H", (_Handler,), {"spa": spa})
    handler = functools.partial(cls, directory=str(root))
    try:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    except OSError:
        srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


# ---------- download ----------
def gradual_scroll(page, steps: int) -> None:
    """Scroll down in steps so lazy-loaded chunks, images, models and data requests fire."""
    if steps <= 0:
        return
    for i in range(1, steps + 1):
        h = page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)")
        page.evaluate(f"window.scrollTo(0,{int(h * i / steps)})")
        page.wait_for_timeout(400)
    page.wait_for_timeout(1000)
    page.evaluate("window.scrollTo(0,0)")
    page.wait_for_timeout(300)


def _context_args(args, p=None) -> dict:
    """Browser-context options shared by the download and verify passes."""
    if args.device:
        kw = dict(resolve_device(p, args.device))
    else:
        width, height = resolve_viewport(args, VIEW)
        kw = {"viewport": {"width": width, "height": height},
              "device_scale_factor": args.scale}
    if args.user_agent:
        kw["user_agent"] = args.user_agent
    if args.theme:
        kw["color_scheme"] = args.theme
    if args.storage_state:
        kw["storage_state"] = args.storage_state
    return kw


def download(args, start: str, root: Path) -> dict:
    from playwright.sync_api import sync_playwright

    u0 = urlparse(start)
    origin, netloc = f"{u0.scheme}://{u0.netloc}", u0.netloc
    block = blocklist(args)
    saved: dict[str, tuple[Path, str, bool]] = {}     # url -> (file, content_type, same_origin)
    errors: list[str] = []
    pages: list[str] = []

    robots = robotparser.RobotFileParser()
    if not args.ignore_robots:
        try:
            robots.set_url(origin + "/robots.txt")
            robots.read()
        except Exception:
            robots = None
    else:
        robots = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        ctx = browser.new_context(**_context_args(args, p))

        def on_response(resp):
            try:
                if resp.request.method != "GET" or resp.status != 200:
                    return
                url = urldefrag(resp.url)[0]
                u = urlparse(url)
                if u.scheme not in ("http", "https") or url in saved:
                    return
                same = u.netloc == netloc
                if not same and not external_allowed(u, args.external, block):
                    return
                ct = resp.headers.get("content-type", "")
                body = None
                if u.path.lower().endswith(RAW_EXT):      # raw bytes, untouched by the browser
                    try:
                        body = ctx.request.get(url).body()
                    except Exception:
                        body = None
                if body is None:
                    body = resp.body()
                dest = local_path(root, url, ct, same)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)
                saved[url] = (dest, ct, same)
            except Exception as e:
                errors.append(f"{resp.url}: {e}")

        ctx.on("response", on_response)

        queue, seen = [(start, 0)], {urldefrag(start)[0]}
        while queue and len(pages) < args.max_pages:
            url, depth = queue.pop(0)
            if depth > 0 and robots and not robots.can_fetch("*", url):
                print(f"[-] robots.txt disallows {url}")
                continue
            if depth > 0 and not args.no_head_check and not is_html_url(ctx, url):
                print(f"[-] skipping non-page link {url}")
                continue
            print(f"[+] ({len(pages) + 1}) {url}")
            page = ctx.new_page()
            try:
                seed_theme(page, args.theme, args.theme_key)
                try:
                    page.goto(url, wait_until=args.wait_until, timeout=args.timeout)
                except Exception as e:
                    print(f"[-] navigation notice: {e}")
                apply_theme(page, args.theme)
                page.wait_for_timeout(args.wait_ms)
                gradual_scroll(page, args.scroll_steps)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass
                pages.append(url)
                if depth < args.depth:
                    links = page.eval_on_selector_all("a[href]", "els=>els.map(e=>e.href)")
                    for link in links:
                        link = urldefrag(link)[0]
                        lu = urlparse(link)
                        if lu.scheme in ("http", "https") and lu.netloc == netloc and link not in seen:
                            seen.add(link)
                            queue.append((link, depth + 1))
            finally:
                page.close()
            if args.delay_ms and queue:
                time.sleep(args.delay_ms / 1000)

        # Static references the page never requested while running (icons, manifests)
        try:
            page = ctx.new_page()
            seed_theme(page, args.theme, args.theme_key)
            page.goto(start, wait_until=args.wait_until, timeout=args.timeout)
            apply_theme(page, args.theme)
            extra = page.eval_on_selector_all("link[href], img[src]", "els=>els.map(e=>e.href||e.src).filter(Boolean)")
            page.close()
            for url in extra:
                url = urldefrag(url)[0]
                u = urlparse(url)
                if url not in saved and u.scheme in ("http", "https") and u.netloc == netloc:
                    try:
                        r = ctx.request.get(url)
                        if r.status == 200:
                            ct = r.headers.get("content-type", "")
                            dest = local_path(root, url, ct, True)
                            dest.parent.mkdir(parents=True, exist_ok=True)
                            dest.write_bytes(r.body())
                            saved[url] = (dest, ct, True)
                    except Exception:
                        pass
        except Exception:
            pass
        browser.close()

    ext_hosts = sorted({urlparse(u).netloc for u, (_, _, same) in saved.items() if not same})
    rewrite(saved, origin, ext_hosts)
    return {"origin": origin, "pages": pages, "files": len(saved), "external_hosts": ext_hosts, "errors": errors}


def rewrite(saved, origin: str, ext_hosts: list[str]) -> None:
    """Make absolute references point at the local copy; strip SRI hashes that rewriting would break."""
    o = re.escape(origin)
    bare_host = re.escape(urlparse(origin).netloc)
    for dest, ct, _ in saved.values():
        if not is_text(ct, str(dest)):
            continue
        try:
            t = dest.read_text(encoding="utf-8")
        except Exception:
            continue
        t = t.replace(origin + "/", "/").replace(origin.replace("/", "\\/") + "\\/", "\\/")
        t = re.sub(o + r"(?![\w.:-])", "/", t)
        t = re.sub(r"(?<![:\w])//" + bare_host + "/", "/", t)
        for h in ext_hosts:
            local = f"/_external/{safe_netloc(h)}/"
            for scheme in ("https:", "http:"):
                t = t.replace(f"{scheme}//{h}/", local)
            t = re.sub(r"(?<![:\w])//" + re.escape(h) + "/", local, t)
        if "html" in ct.lower() or str(dest).lower().endswith((".html", ".htm")):
            t = re.sub(r'\sintegrity="[^"]*"', "", t)
        dest.write_text(t, encoding="utf-8")


# ---------- verification ----------
def verify(root: Path, start: str, args) -> dict:
    from playwright.sync_api import sync_playwright

    srv, base = make_server(root, spa=args.spa)
    local_host = urlparse(base).netloc
    missing, external = [], set()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed)
            ctx = browser.new_context(**_context_args(args, p))
            page = ctx.new_page()
            seed_theme(page, args.theme, args.theme_key)

            def on_resp(r):
                if urlparse(r.url).netloc == local_host and r.status >= 400:
                    missing.append(f"{r.status} {urlparse(r.url).path}")

            def on_req(r):
                u = urlparse(r.url)
                if u.scheme in ("http", "https") and u.netloc != local_host:
                    external.add(u.netloc)

            page.on("response", on_resp)
            page.on("request", on_req)
            page.on("requestfailed", lambda r: urlparse(r.url).netloc == local_host and missing.append(f"failed {urlparse(r.url).path}"))
            u0 = urlparse(start)
            try:
                page.goto(base + (u0.path or "/") + (f"?{u0.query}" if u0.query else ""),
                          wait_until=args.wait_until, timeout=args.timeout)
            except Exception as e:
                missing.append(f"navigation: {e}")
            apply_theme(page, args.theme)
            page.wait_for_timeout(args.wait_ms)
            gradual_scroll(page, args.scroll_steps)
            browser.close()
    finally:
        srv.shutdown()
    return {"missing": sorted(set(missing)), "external": sorted(external)}


# ---------- CLI ----------
def add_args(p):
    p.add_argument("url", nargs="?", help="Site entry URL (https:// added if missing)")
    p.add_argument("--url", dest="url_opt", help="Site entry URL, same as the positional")
    add_output_args(p, single=False, default_dir=None,
                    dir_help="Destination folder (default .capture/website/<host>)")
    p.add_argument("--depth", type=int, default=0, help="Follow same-site links this many levels (default 0 = entry page only)")
    p.add_argument("--max-pages", type=int, default=50, help="Page cap when crawling (default 50)")
    p.add_argument("--delay-ms", type=int, default=0, help="Pause between crawled pages")
    p.add_argument("--ignore-robots", action="store_true", help="Do not honour robots.txt when following links")
    p.add_argument("--no-head-check", action="store_true", help="Do not probe crawled links with HEAD; every same-site link is navigated")
    p.add_argument("--external", nargs="*", default=None, metavar="HOST",
                   help="Also save assets from other hosts (fonts, CDNs) under _external/. "
                        "No hosts = all except the tracker blocklist (data/trackers.txt; see --block)")
    p.add_argument("--block", action="append", metavar="HOST", help="Never save assets from this host (repeatable; subdomains included)")
    p.add_argument("--no-default-blocklist", action="store_true", help="Ignore data/trackers.txt; only --block hosts are blocked")
    add_view_args(p, default="wide")
    p.add_argument("--wait-ms", type=int, default=2000, help="Wait after load before scrolling (2000)")
    p.add_argument("--wait-until", choices=["networkidle", "load", "domcontentloaded"], default="domcontentloaded",
                   help="Navigation readiness for each page (default domcontentloaded)")
    p.add_argument("--scroll-steps", type=int, default=10, help="Gradual scroll steps to trigger lazy loading; 0 = off")
    p.add_argument("--timeout", type=int, default=30000, help="Navigation timeout in ms")
    add_device_args(p)
    add_session_args(p)
    add_theme_args(p)
    add_browser_args(p, with_timeout=False, scale=True)
    add_json_args(p)
    p.add_argument("--no-verify", action="store_true", help="Skip the post-download check of the local copy")
    p.add_argument("--serve", action="store_true", help="Serve the copy locally after download (blocks until Ctrl+C)")
    p.add_argument("--serve-only", metavar="DIR", help="Serve an existing copy and do nothing else")
    p.add_argument("--port", type=int, default=8000, help="Port for --serve/--serve-only (falls back to a free port)")
    p.add_argument("--open", action="store_true", help="Open the served site in your browser")
    p.add_argument("--spa", action="store_true",
                   help="Serve index.html for unknown extensionless routes (single-page apps)")


def serve_forever(root: Path, args):
    srv, base = make_server(root, args.port, args.spa)
    print(f"\n[+] Serving {root} at {base}  (Ctrl+C to stop)")
    if args.open:
        import webbrowser
        webbrowser.open(base)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] Server stopped.")
        srv.shutdown()


def run(args):
    if list_devices(args, "website"):
        return
    check_file(args.storage_state, "--storage-state")
    if args.serve_only:
        root = Path(args.serve_only)
        if not root.is_dir():
            sys.exit(f"No such folder: {root}")
        return serve_forever(root, args)
    url = args.url_opt or args.url
    if not url:
        sys.exit("Give the site URL (or --serve-only DIR).")
    if args.depth < 0 or args.max_pages < 1 or args.delay_ms < 0 or args.scroll_steps < 0 or args.wait_ms < 0:
        sys.exit("--depth, --delay-ms, --scroll-steps and --wait-ms cannot be negative, and --max-pages must be at least 1")
    if not 0 < args.scale <= 8:
        sys.exit("--scale must be between 0 and 8")
    vw, vh = resolve_viewport(args, VIEW)
    if not (0 < vw <= 16384 and 0 < vh <= 16384):
        sys.exit("--width and --height must be between 1 and 16384")

    start = normalize(url)
    root = Path(args.output_dir) if args.output_dir else Path(".capture/website") / safe_netloc(urlparse(start).netloc)
    root.mkdir(parents=True, exist_ok=True)
    payload = {"command": "website", "source": start, "output_dir": str(root)}

    with begin(args) as real:
        print(f"[+] Mirroring {start} -> {root}")

        res = download(args, start, root)
        if res["files"] == 0:
            sys.exit("Nothing was downloaded. Check the URL, your connection, or raise --timeout.")
        print(f"[+] Saved {res['files']} file(s) from {len(res['pages'])} page(s) to {root}")
        if res["external_hosts"]:
            print(f"[+] External hosts saved under _external/: {', '.join(res['external_hosts'])}")
        for e in res["errors"][:10]:
            print(f"[-] save error: {e}", file=sys.stderr)

        ver = None
        if not args.no_verify:
            ver = verify(root, start, args)
            if ver["missing"]:
                print(f"[!] VERIFY: {len(ver['missing'])} request(s) failed against the local copy:")
                for m in ver["missing"][:20]:
                    print(f"      {m}")
            else:
                print("[+] VERIFY: local copy loaded with no failed requests")
            if ver["external"]:
                print("[!] VERIFY: still contacts external hosts (needs internet; rerun with --external to save them): "
                      + ", ".join(ver["external"]))

        (root / ".capture-manifest.json").write_text(json.dumps({
            "source": start, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "pages": res["pages"],
            "files": res["files"], "external_hosts": res["external_hosts"], "verify": ver}, indent=2), encoding="utf-8")
        payload.update({"pages": res["pages"], "files": res["files"],
                        "external_hosts": res["external_hosts"],
                        "manifest": str(root / ".capture-manifest.json"),
                        "verify": ver})
        print(f"[+] Done. View it: python capture.py website --serve-only {root}")
    emit(args, payload, real)
    if args.serve:
        serve_forever(root, args)


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
