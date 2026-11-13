"""Discover a site's routes, then screenshot every route as a scrolling series.

A native port of the `capturer` pipeline. Route discovery runs in this order:

  1. Sitemap  — robots.txt `Sitemap:` directives first, then /sitemap.xml,
                sitemap indexes (recursively), gzip sitemaps, locale-prefixed
                sitemaps, and `<xhtml:link rel="alternate" hreflang>` entries.
  2. robots.txt — folded into step 1: a `Sitemap:` line is the authoritative
                sitemap location.
  3. Crawler  — Playwright follows same-origin `<a href>` links, bounded by
                --max-depth and --max-pages.

Every discovered route is captured as an overlapping scroll series (like
`screenshots --scroll`) in its own folder, and one JSON report records the
method, the route patterns, every page's status and every saved image.

Usage:
  python siteshots.py https://example.com
  python siteshots.py https://example.com --routes "about, contact, blog"
  python siteshots.py https://example.com --force-crawl --max-depth 2
  python siteshots.py https://example.com/eg?lang=ar --max-pages 40 --json

Requires: pip install playwright && playwright install chromium
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import html
import json
import os
import re
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, parse_qsl, urljoin, urlparse
from urllib.request import Request, urlopen

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli import (add_browser_args, add_device_args, add_json_args, add_output_args,  # noqa: E402
                  add_session_args, add_theme_args, add_view_args, begin, check_file, emit,
                  list_devices, resolve_device, resolve_viewport, seed_theme, apply_theme)
from _common import default_user_agent  # noqa: E402
from screenshots import Opts, folder_name, uniform_positions  # noqa: E402

# Limits (named so they are visible and tunable in one place).
DEFAULT_MAX_PAGES = 50
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_SHOTS = 500
MAX_SITEMAPS = 50
MAX_SITEMAP_BYTES = 8_000_000
SETTLE_TIMEOUT_MS = 3_000
LOCALE_KEYS = ("lang", "locale", "language", "hl")
LOCALE_SEGMENT = re.compile(r"^[a-z]{2}(?:[-_][a-z]{2})?$", re.I)

# Links that are almost never a page worth screenshotting.
NON_PAGE_EXT = (
    ".pdf", ".zip", ".rar", ".7z", ".tar", ".gz", ".dmg", ".exe", ".msi",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".avif", ".svg", ".ico", ".bmp",
    ".css", ".js", ".mjs", ".json", ".xml", ".txt", ".csv", ".map",
    ".mp4", ".m4v", ".mov", ".webm", ".mp3", ".wav", ".ogg",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
)

# Route families that are real pages even though they look slug-like.
STATIC_NAMES = {
    "about", "about-us", "contact", "contact-us", "help", "faq", "faqs", "support",
    "privacy", "privacy-policy", "terms", "terms-of-service", "terms-and-conditions",
    "disclaimer", "legal", "accessibility", "cookies", "security",
    "sitemap", "search", "404", "500", "error",
    "login", "signin", "sign-in", "logout", "sign-out", "signup", "sign-up", "register",
    "dashboard", "settings", "profile", "account", "cart", "checkout",
    "home", "index", "feed", "explore",
    "blog", "blogs", "news", "articles", "posts", "press", "media",
    "funds", "fund", "products", "services", "categories", "category",
    "features", "pricing", "enterprise", "api", "docs", "documentation",
    "events", "partners", "team", "investors", "careers", "jobs",
    "community", "recommendations", "feedback",
    "fund-prices", "compare", "fund-compare", "page", "pages",
    "eg", "sa", "ae", "en", "ar", "us", "uk", "gb", "ca", "au", "tr", "fr", "de",
}

# Errors raised when a page navigates while Playwright is reading it.
NAVIGATION_RE = re.compile(
    r"execution context was destroyed|most likely because of a navigation|"
    r"frame was detached|target closed|target page, context or browser has been closed|"
    r"cannot find context|navigation interrupted",
    re.I,
)


# ---------- URL helpers ----------
def normalize_url(url: str) -> str:
    """Add https:// (http:// for localhost) to a bare host."""
    if "://" in url:
        return url
    host = url.split("/")[0].split(":")[0]
    return f"{'http' if host in ('localhost', '127.0.0.1', '0.0.0.0') else 'https'}://{url}"


def origin_of(url: str) -> str:
    u = urlparse(url)
    return f"{u.scheme}://{u.netloc}"


def safe_host(url: str) -> str:
    return re.sub(r"[^\w.-]", "_", urlparse(url).netloc or "site")


def normalize_key(url: str) -> str:
    """Deduplication key: no fragment, no trailing slash."""
    u = urlparse(url)
    return f"{u.scheme}://{u.netloc}{u.path.rstrip('/') or '/'}" + (f"?{u.query}" if u.query else "")


def locale_preference(entry: str) -> tuple[tuple[str, str] | None, str | None]:
    """(query parameter, path prefix) describing the entry URL's locale, if any."""
    u = urlparse(entry)
    query = dict(parse_qsl(u.query, keep_blank_values=True))
    param = next(((key, query[key]) for key in LOCALE_KEYS if query.get(key)), None)
    segments = [s for s in u.path.split("/") if s]
    prefix = "/" + segments[0] if segments and LOCALE_SEGMENT.fullmatch(segments[0]) else None
    return param, prefix


def apply_locale_filter(urls: list[str], entry: str) -> list[str]:
    """Keep the routes that belong to the entry URL's locale, falling back to all.

    A site that publishes both `?lang=ar` and `?lang=en` (or `/ar/` and `/en/`)
    otherwise doubles every route and captures the wrong language.
    """
    if not urls:
        return urls
    param, prefix = locale_preference(entry)
    kept = urls
    if param:
        key, value = param
        same = [u for u in kept if (dict(parse_qsl(urlparse(u).query)).get(key) == value)]
        if same:
            kept = same
    if prefix:
        def belongs(url: str) -> bool:
            path = urlparse(url).path
            if path == prefix or path.startswith(prefix + "/"):
                return True
            # Keep paths that are not themselves language-prefixed: they are shared
            # pages, not another locale. Only drop a different `/xx/` tree.
            first = path.strip("/").split("/")[0] if path.strip("/") else ""
            return not LOCALE_SEGMENT.fullmatch(first)
        same = [u for u in kept if belongs(u)]
        if same:
            kept = same
    return kept


def is_page_url(url: str, origin: str) -> bool:
    u = urlparse(url)
    if u.scheme not in ("http", "https"):
        return False
    if f"{u.scheme}://{u.netloc}" != origin:
        return False
    return not u.path.lower().endswith(NON_PAGE_EXT)


def same_origin(url: str, origin: str) -> bool:
    try:
        return origin_of(url) == origin
    except ValueError:
        return False


# ---------- HTTP sitemap reader ----------
def fetch_text(url: str, timeout_ms: int) -> str:
    """GET a small text document; transparently gunzip .gz or encoded bodies."""
    req = Request(url, headers={
        "User-Agent": default_user_agent(),
        "Accept": "application/xml,text/xml,text/html;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "identity",
    })
    with urlopen(req, timeout=max(1.0, timeout_ms / 1000)) as resp:
        raw = resp.read(MAX_SITEMAP_BYTES + 1)
        encoding = (resp.headers.get("Content-Encoding") or "").lower()
    if len(raw) > MAX_SITEMAP_BYTES:
        raise ValueError(f"sitemap larger than {MAX_SITEMAP_BYTES} bytes")
    if raw[:2] == b"\x1f\x8b" or "gzip" in encoding or url.lower().endswith(".gz"):
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "replace")


def _attr(tag: str, name: str) -> str | None:
    match = re.search(rf'\b{name}\s*=\s*["\']([^"\']*)["\']', tag, re.I)
    return html.unescape(match.group(1)) if match else None


def parse_sitemap(xml: str) -> tuple[bool, list[str], list[str]]:
    """(is_index, locs, hrefs) for one sitemap document.

    `<xhtml:link rel="alternate" hreflang="...">` entries are the locale
    alternates Google recommends; they are page URLs just like `<loc>`.
    """
    lowered = xml.lower()
    if "<urlset" not in lowered and "<sitemapindex" not in lowered:
        return False, [], []
    is_index = "<sitemapindex" in lowered
    locs = [html.unescape(m.group(1).strip())
            for m in re.finditer(r"<loc>\s*(.*?)\s*</loc>", xml, re.I | re.S)]
    alternates = []
    for match in re.finditer(r"<xhtml:link\b[^>]*>", xml, re.I):
        tag = match.group(0)
        if (_attr(tag, "rel") or "").lower() == "alternate" and _attr(tag, "href"):
            alternates.append(_attr(tag, "href"))
    return is_index, locs, alternates


def expand_sitemap(url: str, *, origin: str, timeout_ms: int,
                   seen: set[str], depth: int = 0) -> list[str]:
    """Fetch one sitemap (or index) and return its same-origin page URLs.

    Indexes are expanded recursively. Sitemap XML URLs are never returned as
    pages: the previous implementation screenshotted them as routes.
    """
    if depth > 3 or len(seen) >= MAX_SITEMAPS:
        return []
    absolute = urljoin(origin + "/", url)
    if absolute in seen:
        return []
    seen.add(absolute)
    try:
        xml = fetch_text(absolute, timeout_ms)
    except Exception:
        return []
    is_index, locs, alternates = parse_sitemap(xml)
    if is_index:
        pages: list[str] = []
        for child in locs:
            pages.extend(expand_sitemap(child, origin=origin, timeout_ms=timeout_ms,
                                        seen=seen, depth=depth + 1))
        return pages
    pages = []
    for raw in locs + alternates:
        candidate = urljoin(absolute, raw)
        # A `<loc>` may still point at another XML file, a PDF, or a mailto: link;
        # those are not pages worth screenshotting.
        if is_page_url(candidate, origin):
            pages.append(candidate)
    return pages


def standard_sitemap_candidates(entry: str) -> list[str]:
    """Common sitemap locations, with the entry's locale prefix tried first."""
    origin = origin_of(entry)
    _, prefix = locale_preference(entry)
    paths: list[str] = []
    if prefix:
        paths += [f"{prefix}/sitemap.xml", f"{prefix}/sitemap_index.xml"]
    paths += [
        "/sitemap.xml",
        "/sitemap.xml.gz",
        "/sitemap_index.xml",
        "/sitemap-index.xml",
        "/wp-sitemap.xml",
        "/sitemap/sitemap.xml",
        "/sitemaps/sitemap.xml",
    ]
    return list(dict.fromkeys(origin + path for path in paths))


def discover_sitemap(entry: str, timeout_ms: int) -> tuple[list[str], str] | None:
    """Return (page URLs, method) from robots-declared or standard sitemaps."""
    origin = origin_of(entry)
    declared: list[str] = []
    try:
        robots = fetch_text(origin + "/robots.txt", timeout_ms)
        for line in robots.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("sitemap:"):
                value = stripped.split(":", 1)[1].strip()
                if value:
                    declared.append(value)
    except Exception:
        pass

    if declared:
        seen: set[str] = set()
        pages: list[str] = []
        for sitemap in declared:
            pages.extend(expand_sitemap(sitemap, origin=origin, timeout_ms=timeout_ms, seen=seen))
        if pages:
            return list(dict.fromkeys(pages)), "sitemap (robots.txt)"

    seen = set()
    pages = []
    for candidate in standard_sitemap_candidates(entry):
        pages.extend(expand_sitemap(candidate, origin=origin, timeout_ms=timeout_ms, seen=seen))
        if pages:
            break
    if pages:
        return list(dict.fromkeys(pages)), "sitemap"
    return None


# ---------- navigation-race-safe helpers ----------
def wait_after_navigation(page) -> None:
    try:
        page.wait_for_load_state("load", timeout=SETTLE_TIMEOUT_MS)
    except Exception:
        pass
    try:
        page.wait_for_timeout(250)
    except Exception:
        pass


def safe_evaluate(page, script: str, arg=None, *, attempts: int = 3):
    """Evaluate JS, retrying when a client-side navigation destroys the context."""
    for attempt in range(attempts):
        try:
            return page.evaluate(script, arg) if arg is not None else page.evaluate(script)
        except Exception as exc:
            if attempt == attempts - 1 or not NAVIGATION_RE.search(str(exc)):
                raise
            wait_after_navigation(page)


def safe_screenshot(page, path: str, *, attempts: int = 3, **kwargs) -> None:
    for attempt in range(attempts):
        try:
            page.screenshot(path=path, **kwargs)
            return
        except Exception as exc:
            if attempt == attempts - 1 or not NAVIGATION_RE.search(str(exc)):
                raise
            wait_after_navigation(page)


def stable_url(page, wait_ms: int, wait_for: str | None = None) -> str:
    """Wait until the URL and readyState stop changing, then the settle delay.

    A client-side redirect after DOMContentLoaded used to race the first
    `page.evaluate` and abort the whole capture. Waiting for two identical
    readings plus `load` closes that window.
    """
    if wait_for:
        try:
            page.wait_for_selector(wait_for, timeout=8_000)
        except Exception:
            pass
    try:
        page.wait_for_load_state("load", timeout=SETTLE_TIMEOUT_MS)
    except Exception:
        pass
    previous = None
    for _ in range(20):
        current = page.url
        try:
            ready = page.evaluate("document.readyState")
        except Exception:
            ready = None
        if current == previous and ready in ("interactive", "complete"):
            break
        previous = current
        try:
            page.wait_for_timeout(150)
        except Exception:
            break
    if wait_ms:
        page.wait_for_timeout(wait_ms)
    return page.url


# ---------- Playwright crawler ----------
def crawl_routes(entry: str, args, o: Opts, playwright) -> list[str]:
    """Breadth-first same-origin crawl; links are read only after the page settles."""
    origin = origin_of(entry)
    found: list[str] = []
    seen = {normalize_key(entry)}
    queue: list[tuple[str, int]] = [(entry, 0)]

    browser = playwright.chromium.launch(headless=not args.headed)
    try:
        context = browser.new_context(**_context_options(o))
        try:
            while queue and len(found) < args.max_pages:
                url, depth = queue.pop(0)
                page = context.new_page()
                try:
                    seed_theme(page, o.theme, o.theme_key)
                    try:
                        page.goto(url, wait_until=args.wait_until, timeout=args.timeout)
                    except Exception as exc:
                        if "ERR_ABORTED" not in str(exc) and not NAVIGATION_RE.search(str(exc)):
                            raise
                    final = stable_url(page, args.wait_ms, args.wait_for)
                    apply_theme(page, o.theme)
                    if normalize_key(final) not in {normalize_key(f) for f in found}:
                        found.append(final)
                    if depth >= args.max_depth or len(found) >= args.max_pages:
                        continue
                    try:
                        links = page.eval_on_selector_all("a[href]", "els=>els.map(e=>e.href)")
                    except Exception:
                        links = []
                    for link in links:
                        link = link.split("#")[0]
                        key = normalize_key(link)
                        if not is_page_url(link, origin) or key in seen:
                            continue
                        seen.add(key)
                        queue.append((link, depth + 1))
                finally:
                    page.close()
        finally:
            context.close()
    finally:
        browser.close()
    return found


# ---------- slug collapsing ----------
def locale_first(variants: list[str], entry: str | None) -> list[str]:
    """Order variants so the entry URL's locale variant comes first, then queryless ones."""
    param, _ = locale_preference(entry) if entry else (None, None)
    def rank(url: str) -> tuple[int, int, int]:
        matches = 0
        if param:
            key, value = param
            matches = 0 if dict(parse_qsl(urlparse(url).query)).get(key) == value else 1
        return (matches, 1 if "?" in url else 0, len(url))
    return sorted(variants, key=rank)


def collapse_by_slug(routes: list[str], entry: str | None = None) -> tuple[list[str], list[dict]]:
    """Collapse slug families into one capture target each, plus the patterns for the report.

    `/funds/a`, `/funds/b`, `/funds/c` become one `[slug]` pattern and one example page
    instead of three nearly identical captures. Genuinely static names stay separate.
    Returns (capture_targets, patterns); targets are always real URLs.
    """
    path_map: dict[str, dict] = {}
    for raw in routes:
        u = urlparse(raw)
        origin = f"{u.scheme}://{u.netloc}"
        path = u.path.rstrip("/") or "/"
        key = origin + path
        item = path_map.setdefault(key, {"origin": origin, "path": path, "variants": []})
        item["variants"].append(raw)

    for item in path_map.values():
        # A locale expressed as a query (?lang=ar) must survive: dropping it would capture
        # the default language instead of the one the user asked for.
        item["canonical"] = locale_first(item["variants"], entry)[0]
        item["clean"] = item["canonical"].split("?")[0].rstrip("/") or item["origin"] + "/"
        segments = [] if item["path"] == "/" else [s for s in item["path"].split("/") if s]
        item["last"] = segments[-1] if segments else ""
        parent = "/".join(segments[:-1]) if len(segments) > 1 else ""
        item["parent"] = item["origin"] + ("/" + parent if parent else "")

    groups: dict[str, list[dict]] = {}
    for item in path_map.values():
        groups.setdefault(item["parent"], []).append(item)

    targets: list[str] = []
    patterns: list[dict] = []
    for parent in sorted(groups, key=lambda p: (p.count("/"), p)):
        children = groups[parent]
        known = [c for c in children if c["last"].lower() in STATIC_NAMES]
        rest = [c for c in children if c["last"].lower() not in STATIC_NAMES]
        if len(rest) <= 1:
            known, rest = children, []

        for item in sorted(known, key=lambda c: c["canonical"]):
            targets.append(item["canonical"])
            patterns.append({"type": "static", "pattern": item["clean"],
                             "example": item["canonical"], "variants": item["variants"]})

        if len(rest) >= 2:
            parent_path = urlparse(rest[0]["parent"]).path.rstrip("/")
            pattern_url = rest[0]["origin"] + (parent_path + "/[slug]" if parent_path else "/[slug]")
            ordered = locale_first([c["canonical"] for c in rest], entry)
            targets.append(ordered[0])
            patterns.append({
                "type": "dynamic",
                "pattern": pattern_url,
                "example": ordered[0],
                "slugs": sorted(c["last"] for c in rest),
                "variants": sorted(v for c in rest for v in c["variants"])[:100],
            })
    return targets, patterns


# ---------- manual routes ----------
def parse_manual_routes(raw: str, entry: str) -> list[str]:
    origin = origin_of(entry)
    routes = []
    for token in re.split(r"[\s,\n\r]+", raw):
        token = token.replace("[", "").replace("]", "").strip()
        if not token:
            continue
        if re.match(r"^https?://", token, re.I):
            routes.append(token)
        elif token.startswith("/"):
            routes.append(origin + token)
        else:
            routes.append(origin + "/" + token)
    return list(dict.fromkeys(routes))


# ---------- page options ----------
def _context_options(o: Opts) -> dict:
    if o.device_cfg:
        options = dict(o.device_cfg)
    else:
        options = {"viewport": {"width": o.css_width, "height": o.css_height},
                   "device_scale_factor": o.scale * o.zoom / 100}
    if o.theme:
        options["color_scheme"] = o.theme
    if o.user_agent:
        options["user_agent"] = o.user_agent
    if o.storage_state:
        options["storage_state"] = o.storage_state
    return options


# ---------- capture ----------
def route_dir_name(url: str) -> str:
    """Folder name for a route; query strings get a short deterministic hash."""
    name = folder_name(url)
    if urlparse(url).query:
        name += "_" + hashlib.md5(url.encode()).hexdigest()[:6]
    return name


def capture_route(browser, url: str, o: Opts, out_root: Path, args) -> dict:
    """Capture one route as a scroll series; restart once if it navigates away."""
    result = {"url": url, "dir": route_dir_name(url), "status": None,
              "httpCode": None, "shots": 0, "error": None}
    page_dir = out_root / result["dir"]

    for attempt in range(2):
        page = None
        try:
            page = browser.new_page(**_context_options(o))
            seed_theme(page, o.theme, o.theme_key)
            response = None
            try:
                response = page.goto(url, wait_until=args.wait_until, timeout=args.timeout)
            except Exception as exc:
                if "ERR_ABORTED" not in str(exc) and not NAVIGATION_RE.search(str(exc)):
                    raise
            result["httpCode"] = response.status if response else None
            if result["httpCode"] == 404:
                result["status"] = "404"
                return result
            if result["httpCode"] and result["httpCode"] >= 500:
                result["status"] = str(result["httpCode"])
                return result

            final = stable_url(page, o.wait_ms, args.wait_for)
            result["finalUrl"] = final
            apply_theme(page, o.theme)

            total = int(safe_evaluate(
                page, "Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)") or 0)
            positions = uniform_positions(total, o.css_height, args.overlap)
            if len(positions) > args.max_shots:
                raise ValueError(f"this route would produce {len(positions)} screenshots "
                                 f"(cap {args.max_shots}); raise --max-shots or increase --overlap")

            if page_dir.exists():
                shutil.rmtree(page_dir)
            page_dir.mkdir(parents=True, exist_ok=True)
            for index, y in enumerate(positions, 1):
                safe_evaluate(page, f"window.scrollTo(0,{int(y)})")
                page.wait_for_timeout(min(o.wait_ms, 300))
                safe_screenshot(page, str(page_dir / f"{index}.png"))
            result["shots"] = len(positions)
            result["status"] = "ok"
            return result

        except Exception as exc:
            if attempt == 0 and NAVIGATION_RE.search(str(exc)):
                shutil.rmtree(page_dir, ignore_errors=True)
                continue
            result["status"] = "error"
            result["error"] = str(exc)
            shutil.rmtree(page_dir, ignore_errors=True)
            return result
        finally:
            if page:
                page.close()
    return result


# ---------- report ----------
def build_report(meta: dict, patterns: list[dict], results: list[dict]) -> dict:
    succeeded = [r for r in results if r["status"] == "ok"]
    failed_404 = [r for r in results if r["status"] == "404"]
    failed_5xx = [r for r in results if r["status"] not in ("ok", "404", "error") and r["status"]]
    errored = [r for r in results if r["status"] == "error"]
    total_shots = sum(r["shots"] for r in succeeded)
    average = round(total_shots / len(succeeded), 2) if succeeded else 0.0
    return {
        "command": "siteshots",
        "meta": meta,
        "routes": {"method": meta.get("method"), "discovered": len(results), "patterns": patterns},
        "summary": {
            "total": len(results),
            "succeeded": len(succeeded),
            "failed404": len(failed_404),
            "failed5xx": len(failed_5xx),
            "errored": len(errored),
            "totalShots": total_shots,
            "avgShotsPerPage": average,
        },
        "pages": {
            "succeeded": [{"url": r["url"], "finalUrl": r.get("finalUrl"), "dir": r["dir"],
                           "shots": r["shots"]} for r in succeeded],
            "404": [{"url": r["url"], "dir": r["dir"]} for r in failed_404],
            "5xx": [{"url": r["url"], "code": r["status"], "dir": r["dir"]} for r in failed_5xx],
            "errored": [{"url": r["url"], "error": r["error"], "dir": r["dir"]} for r in errored],
        },
    }


# ---------- CLI ----------
def add_args(p):
    p.add_argument("url", nargs="?", help="Site entry URL (https:// added if missing)")
    p.add_argument("--url", dest="url_opt", help="Site entry URL, same as the positional")
    add_output_args(p, single=False, default_dir=None,
                    dir_help="Destination folder (default .capture/siteshots/<host>)")
    p.add_argument("--routes", metavar="LIST",
                   help="Manual routes — skip discovery. Accepts 'about, contact', '/eg/about', or full URLs")
    p.add_argument("--force-crawl", action="store_true",
                   help="Skip sitemap and robots.txt; go straight to the Playwright crawler")
    p.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH,
                   help=f"Crawler link depth when discovery falls back to Playwright (default {DEFAULT_MAX_DEPTH})")
    p.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES,
                   help=f"Cap on routes captured (default {DEFAULT_MAX_PAGES})")
    p.add_argument("--all-routes", "--no-collapse", dest="all_routes", action="store_true",
                   help="Capture every discovered URL; do not collapse slug families into one example")
    p.add_argument("--no-hash-slug", dest="all_routes", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--max-shots", type=int, default=DEFAULT_MAX_SHOTS,
                   help=f"Cap on screenshots for one route (default {DEFAULT_MAX_SHOTS})")
    p.add_argument("--overlap", type=int, default=100, metavar="PX",
                   help="Overlap between scroll steps in pixels (default 100)")
    p.add_argument("--wait-ms", type=int, default=500,
                   help="Settle time after load and between scroll steps (default 500)")
    p.add_argument("--wait-for", metavar="SELECTOR",
                   help="Wait for this CSS selector before the first screenshot")
    p.add_argument("--wait-until", choices=["networkidle", "load", "domcontentloaded"], default="domcontentloaded",
                   help="Navigation readiness (default domcontentloaded)")
    p.add_argument("--report", metavar="FILE",
                   help="JSON report path (default <output-dir>/report.json)")
    p.add_argument("--delay-ms", type=int, default=0,
                   help="Pause between routes, for small or shared servers (default 0)")
    add_view_args(p, default="mobile")
    p.add_argument("--scale", type=float, default=1.0, help="Device pixel ratio, e.g. 2 for retina (default 1)")
    add_device_args(p)
    add_session_args(p)
    add_theme_args(p)
    add_browser_args(p)
    add_json_args(p)


def _validate(args) -> None:
    if args.max_depth < 0:
        sys.exit("--max-depth cannot be negative")
    if args.max_pages < 1:
        sys.exit("--max-pages must be at least 1")
    if args.max_shots < 1:
        sys.exit("--max-shots must be at least 1")
    if args.overlap < 0:
        sys.exit("--overlap cannot be negative")
    if args.wait_ms < 0 or args.delay_ms < 0:
        sys.exit("--wait-ms and --delay-ms cannot be negative")
    if not 0 < args.scale <= 8:
        sys.exit("--scale must be between 0 and 8")
    check_file(args.storage_state, "--storage-state")


def run(args):
    if list_devices(args, "siteshots"):
        return
    url = args.url_opt or args.url
    if not url:
        sys.exit("Give the site URL (or --serve-only is not supported here).")
    _validate(args)

    start = normalize_url(url)
    if urlparse(start).scheme not in ("http", "https"):
        sys.exit(f"Not an http(s) URL: {start}")
    host = safe_host(start)
    output_dir = Path(args.output_dir) if args.output_dir else Path(".capture/siteshots") / host
    report_path = Path(args.report) if args.report else output_dir / "report.json"

    vw, vh = resolve_viewport(args, (375, 812))
    o = Opts(width=vw, height=vh, scale=args.scale, wait_ms=args.wait_ms,
             wait_until=args.wait_until, theme=args.theme, theme_key=args.theme_key,
             timeout=args.timeout, user_agent=args.user_agent, storage_state=args.storage_state)

    payload = {"command": "siteshots", "source": start, "output_dir": str(output_dir),
               "report": str(report_path)}
    failures: list[dict] = []

    with begin(args) as real:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            if args.device:
                device = resolve_device(playwright, args.device)
                o.width = device["viewport"]["width"]
                o.height = device["viewport"]["height"]
                o.device_cfg = device
            if not 0 <= args.overlap < o.css_height:
                sys.exit(f"--overlap ({args.overlap}px) must be smaller than the viewport height "
                         f"({o.css_height}px)")

            print(f"[+] Target: {start}")
            print(f"[+] Viewport: {o.css_width}x{o.css_height} @ {o.scale}x"
                  + (f"  device: {args.device}" if args.device else f"  view: {args.view}"))

            # ── Route discovery ──────────────────────────────────────────────
            def collapse(urls: list[str]) -> tuple[list[str], list[dict]]:
                if args.all_routes:
                    return urls, [{"type": "static", "pattern": u, "example": u, "variants": [u]}
                                  for u in urls]
                return collapse_by_slug(urls, start)

            patterns: list[dict]
            if args.routes:
                routes = parse_manual_routes(args.routes, start)
                method = "manual"
                patterns = [{"type": "static", "pattern": r, "example": r, "variants": [r]}
                            for r in routes]
                print(f"[+] Routes: manual ({len(routes)})")
            elif not args.force_crawl and (found := discover_sitemap(start, args.timeout)):
                discovered, method = found
                discovered = apply_locale_filter(discovered, start)
                routes, patterns = collapse(discovered)
                print(f"[+] Routes: {method} ({len(discovered)} URLs -> {len(routes)} captures)")
            else:
                discovered = apply_locale_filter(crawl_routes(start, args, o, playwright), start)
                method = "playwright"
                routes, patterns = collapse(discovered)
                print(f"[+] Routes: Playwright crawler ({len(discovered)} URLs -> {len(routes)} captures)")

            if len(routes) > args.max_pages:
                print(f"[!] {len(routes)} routes discovered; capturing the first {args.max_pages} "
                      f"(--max-pages)")
                routes = routes[:args.max_pages]
                patterns = patterns[:args.max_pages]
            if not routes:
                print("[!] No routes found. Nothing to capture.")
                payload.update({"method": method, "routes": 0, "summary": {"total": 0}})
                emit(args, payload, real)
                return

            # ── Capture ──────────────────────────────────────────────────────
            output_dir.mkdir(parents=True, exist_ok=True)
            browser = playwright.chromium.launch(headless=not args.headed)
            results: list[dict] = []
            try:
                for index, route in enumerate(routes, 1):
                    print(f"[{index}/{len(routes)}] {route}")
                    result = capture_route(browser, route, o, output_dir, args)
                    results.append(result)
                    if result["status"] == "ok":
                        print(f"      -> {result['dir']} ({result['shots']} shots)")
                    elif result["status"] == "error":
                        print(f"      -> ERROR: {result['error']}", file=sys.stderr)
                        failures.append({"url": route, "error": result["error"]})
                    else:
                        print(f"      -> {result['status']}")
                    if args.delay_ms and index < len(routes):
                        time.sleep(args.delay_ms / 1000)
            finally:
                browser.close()

        meta = {
            "targetUrl": start,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "method": method,
            "view": args.view,
            "device": args.device,
            "viewport": f"{o.css_width}x{o.css_height}",
            "scale": o.scale,
            "overlap": args.overlap,
            "outputDir": str(output_dir),
            "collapsed": not args.all_routes,
        }
        report = build_report(meta, patterns, results)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

        summary = report["summary"]
        print()
        print(f"[+] Captured {summary['succeeded']}/{summary['total']} route(s), "
              f"{summary['totalShots']} image(s)")
        if summary["failed404"]:
            print(f"[!] 404 routes: {summary['failed404']}")
        if summary["failed5xx"]:
            print(f"[!] 5xx routes: {summary['failed5xx']}")
        if summary["errored"]:
            print(f"[!] Errored routes: {summary['errored']}")
        print(f"[+] Report: {report_path}")

        payload.update({"method": method, "routes": summary["total"], "summary": summary,
                        "pages": report["pages"]})
        emit(args, payload, real)

    if failures:
        sys.exit(f"{len(failures)} route(s) failed: " + ", ".join(f["url"] for f in failures))


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
