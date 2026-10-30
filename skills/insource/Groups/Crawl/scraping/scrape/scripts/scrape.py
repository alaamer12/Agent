#!/usr/bin/env python3
"""Fetch full framework documentation as clean Markdown (requests + bs4 only).

Modes (exactly one):
  ionic                 All Ionic docs: guide nav pages + every API component page
  auto START_URL        Best-effort discovery of the doc subtree (sitemaps, nav crawl)
  --url URL (repeat)    Scrape exactly these URLs

Flags:
  --output DIR       Write one Markdown file per page (omit -> full content to stdout)
  --verify           Only check resolved URLs return HTTP 200, or for JS-rendered
                     sources that the content element exists; print "OK" when all pass
  --workers N        Concurrent fetches (default 16)
  --min-chars N      Thin-content threshold; a passing page must exceed it (default 120)

Exit: 0 success / OK; 1 any failure (listed on stderr).
"""

import argparse
import re
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
}
TIMEOUT = 30
RETRIES = 3
MAX_CRAWL_PAGES = 300
ASSET_RE = re.compile(r"\.(xml|json|zip|pdf|png|jpe?g|gif|svg|ico|webp|css|js)$", re.I)
CONTENT_SELECTORS = ["div.theme-doc-markdown", "article", "main", "#main-content", "div.body[role=main]"]
SKIP_TAGS = {"script", "style", "noscript", "svg", "iframe", "form", "button", "canvas"}
SKIP_CLASS = {
    "theme-doc-breadcrumbs",
    "theme-doc-version-badge",
    "theme-doc-toc-mobile",
    "theme-doc-toc-desktop",
    "pagination-nav",
}
HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}

IONIC_BASE = "https://ionicframework.com/docs"

# Sidebar label -> path (verified against the live Ionic sitemap).
IONIC_NAV = {
    "Developing": [
        ("Starting", "developing/starting"),
        ("Previewing", "developing/previewing"),
        ("Scaffolding", "developing/scaffolding"),
        ("Developing for iOS", "developing/ios"),
        ("Developing for Android", "developing/android"),
        ("Development Tips", "developing/tips"),
        ("Hardware Back Button", "developing/hardware-back-button"),
        ("Keyboard", "developing/keyboard"),
        ("Config", "developing/config"),
        ("Managing Focus", "developing/managing-focus"),
    ],
    "Layout": [
        ("Structure", "layout/structure"),
        ("Responsive Grid", "layout/grid"),
        ("Global Stylesheets", "layout/global-stylesheets"),
        ("CSS Utilities", "layout/css-utilities"),
        ("Dynamic Font Scaling", "layout/dynamic-font-scaling"),
    ],
    "Theming": [
        ("Basics", "theming/basics"),
        ("Platform Styles", "theming/platform-styles"),
        ("CSS Variables", "theming/css-variables"),
        ("CSS Shadow Parts", "theming/css-shadow-parts"),
        ("Colors", "theming/colors"),
        ("Themes", "theming/themes"),
        ("Dark Mode", "theming/dark-mode"),
        ("High Contrast Mode", "theming/high-contrast-mode"),
        ("Advanced", "theming/advanced"),
        ("Color Generator", "theming/color-generator"),
    ],
    "Angular": [
        ("Overview", "angular/overview"),
        ("Quickstart", "angular/quickstart"),
        ("Build Your First App", "angular/your-first-app"),
        ("Add to Existing", "angular/add-to-existing"),
        ("Build Options", "angular/build-options"),
        ("Lifecycle", "angular/lifecycle"),
        ("Navigation/Routing", "angular/navigation"),
        ("Overlays", "angular/overlays"),
        ("Injection Tokens", "angular/injection-tokens"),
        ("Virtual Scroll", "angular/virtual-scroll"),
        ("Migrating from ion-slides to Swiper.js", "angular/slides"),
        ("Platform", "angular/platform"),
        ("Testing", "angular/testing"),
        ("Storage", "angular/storage"),
        ("Performance", "angular/performance"),
        ("Zoneless", "angular/zoneless"),
        ("Progressive Web Apps", "angular/pwa"),
    ],
    "JavaScript": [
        ("Overview", "javascript/overview"),
        ("Quickstart", "javascript/quickstart"),
    ],
    "React": [
        ("Overview", "react/overview"),
        ("Quickstart", "react/quickstart"),
        ("Build Your First App", "react/your-first-app"),
        ("Add to Existing", "react/add-to-existing"),
        ("Lifecycle", "react/lifecycle"),
        ("Navigation/Routing", "react/navigation"),
        ("Virtual Scroll", "react/virtual-scroll"),
        ("Migrating From IonSlides to Swiper.js", "react/slides"),
        ("Utility Functions", "react/utility-functions"),
        ("Platform", "react/platform"),
        ("Progressive Web Apps", "react/pwa"),
        ("Overlays", "react/overlays"),
        ("Storage", "react/storage"),
        ("Testing", "react/testing/introduction"),
        ("Performance", "react/performance"),
    ],
    "Vue": [
        ("Overview", "vue/overview"),
        ("Quickstart", "vue/quickstart"),
        ("Build Your First App", "vue/your-first-app"),
        ("Add to Existing", "vue/add-to-existing"),
        ("Build Options", "vue/build-options"),
        ("Lifecycle", "vue/lifecycle"),
        ("Navigation/Routing", "vue/navigation"),
        ("Virtual Scroll", "vue/virtual-scroll"),
        ("Migrating From ion-slides to Swiper.js", "vue/slides"),
        ("Utility Functions", "vue/utility-functions"),
        ("Platform", "vue/platform"),
        ("Testing", "vue/testing"),
        ("Progressive Web Apps", "vue/pwa"),
        ("Storage", "vue/storage"),
        ("Troubleshooting", "vue/troubleshooting"),
        ("Performance", "vue/performance"),
    ],
    "Utilities": [
        ("Animations", "utilities/animations"),
        ("Gestures", "utilities/gestures"),
    ],
    "Deployment": [
        ("iOS App Store", "deployment/app-store"),
        ("Android Play Store", "deployment/play-store"),
        ("Progressive Web App (PWA)", "deployment/progressive-web-app"),
    ],
    "Techniques": [
        ("Security", "techniques/security"),
    ],
    "Troubleshooting": [
        ("Build Errors", "troubleshooting/build"),
        ("Runtime Issues", "troubleshooting/runtime"),
        ("Debugging", "troubleshooting/debugging"),
        ("Native Errors", "troubleshooting/native"),
        ("CORS Errors", "troubleshooting/cors"),
    ],
    "Core Concepts": [
        ("Fundamentals", "core-concepts/fundamentals"),
        ("Cross Platform", "core-concepts/cross-platform"),
        ("Web View", "core-concepts/webview"),
        ("What are PWAs?", "core-concepts/what-are-progressive-web-apps"),
    ],
}


def new_session():
    session = requests.Session()
    session.headers.update(UA)
    return session


def get(session, url):
    """GET with retries. Returns (response, None) or (None, error-string)."""
    last = None
    for attempt in range(RETRIES):
        wait = 1 + attempt
        try:
            resp = session.get(url, timeout=TIMEOUT, allow_redirects=True)
            if resp.status_code == 200:
                return resp, None
            last = f"HTTP {resp.status_code}"
            if resp.status_code < 500 and resp.status_code != 429:
                return None, last  # 4xx will not heal on retry
            if resp.status_code == 429:
                wait = 3 * (attempt + 1)
        except requests.RequestException as exc:
            last = f"{type(exc).__name__}"
        time.sleep(wait)
    return None, last


def parse_sitemap(text):
    soup = BeautifulSoup(text, "html.parser")
    locs = [t.get_text(strip=True) for t in soup.find_all("loc")]
    return locs, bool(soup.find("sitemapindex"))


def resolve_ionic(session):
    urls = [IONIC_BASE, f"{IONIC_BASE}/api"]
    urls += [f"{IONIC_BASE}/{p}" for pages in IONIC_NAV.values() for _, p in pages]
    resp, err = get(session, f"{IONIC_BASE}/sitemap.xml")
    if resp is None:
        sys.exit(f"ionic: cannot fetch sitemap: {err}")
    locs, _ = parse_sitemap(resp.text)
    urls += sorted(u for u in locs if u.startswith(f"{IONIC_BASE}/api/"))
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def discover_urls(session, start):
    """Best effort: sitemap.xml along the path (deepest first), then one nav crawl."""
    split = urlsplit(start)
    parts = [p for p in split.path.split("/") if p]
    prefix = start.rstrip("/") + "/"
    for i in range(len(parts), -1, -1):
        sitemap = urlunsplit((split.scheme, split.netloc, "/" + "/".join(parts[:i] + ["sitemap.xml"]), "", ""))
        resp, _ = get(session, sitemap)
        if resp is None or "<loc" not in resp.text[:5000]:
            continue
        locs, is_index = parse_sitemap(resp.text)
        if is_index:
            child_sitemaps = locs[:20]
            locs = []
            for child in child_sitemaps:
                child_resp, _ = get(session, child)
                if child_resp is not None:
                    locs.extend(parse_sitemap(child_resp.text)[0])
        urls = sorted({u for u in locs if (u.startswith(prefix) or u.rstrip("/") == start.rstrip("/")) and not re.search(r"/v\d+(/|$)", u)})
        if urls:
            return urls
    # fallback: bounded BFS over same-subtree links (mdbook/rustdoc sites have no sitemap)
    resp, err = get(session, start)
    if resp is None:
        sys.exit(f"auto: cannot fetch start URL: {err}")
    root = resp.url if resp.url.endswith("/") else resp.url + "/" if "." not in urlsplit(resp.url).path.rsplit("/", 1)[-1] else resp.url
    sp = urlsplit(root)
    subtree = urlunsplit((sp.scheme, sp.netloc, sp.path, "", ""))

    def norm(u):
        return u[: -len("index.html")] if u.endswith("index.html") else u

    def page_links(u):
        r, _ = get(session, u)
        if r is None:
            return set()
        page = BeautifulSoup(r.text, "html.parser")
        return {
            norm(t)
            for t in (urljoin(u, a["href"]).split("#")[0].split("?")[0] for a in page.find_all("a", href=True))
            if t.startswith(subtree) and not ASSET_RE.search(t) and norm(t) != subtree
        }

    seen = {subtree}
    frontier = page_links(subtree)
    while frontier and len(seen) < MAX_CRAWL_PAGES:
        batch = sorted(frontier)[:80]
        seen |= set(batch)
        links = set()
        with ThreadPoolExecutor(max_workers=16) as pool:
            for got in pool.map(page_links, batch):
                links |= got
        frontier = links - seen
    return sorted(seen)[:MAX_CRAWL_PAGES]


# ---------- HTML -> Markdown ----------

def skippable(tag):
    classes = " ".join(tag.get("class", []))
    return any(c in classes for c in SKIP_CLASS)


def collapse(text):
    return " ".join(text.split())


def inline(node, base):
    buf = []
    for child in node.children:
        if getattr(child, "name", None) is None:
            buf.append(str(child))
            continue
        tag = child.name
        if tag in SKIP_TAGS or skippable(child):
            continue
        if tag == "code":
            buf.append("`" + child.get_text().replace("\n", " ").strip() + "`")
        elif tag in ("strong", "b"):
            text = inline(child, base).strip()
            buf.append(f"**{text}**" if text else "")
        elif tag in ("em", "i"):
            text = inline(child, base).strip()
            buf.append(f"*{text}*" if text else "")
        elif tag == "a":
            text = inline(child, base).strip()
            href = child.get("href", "")
            if text and href and not href.startswith("#"):
                buf.append(f"[{text}]({urljoin(base, href)})")
            else:
                buf.append(text)
        elif tag == "br":
            buf.append("\n")
        elif tag == "img":
            src = child.get("src", "")
            if src:
                buf.append(f"![{child.get('alt') or 'image'}]({urljoin(base, src)})")
        else:
            buf.append(inline(child, base))
    return "".join(buf)


def render_list(node, base, depth):
    out = []
    ordered = node.name == "ol"
    idx = int(node.get("start", "1") or 1)
    for li in node.find_all("li", recursive=False):
        nested = li.find_all(["ul", "ol"], recursive=False)
        for n in nested:
            n.extract()
        text = collapse(inline(li, base))
        marker = f"{idx}. " if ordered else "- "
        idx += 1
        if text:
            out.append("  " * depth + marker + text)
        for n in nested:
            out.append(render_list(n, base, depth + 1))
    return "\n" + "\n".join(out) + "\n"


def render_table(node, base):
    def cell_text(cell):
        return collapse(inline(cell, base)).replace("|", "\\|") or " "

    def row(cls):
        return "| " + " | ".join(cell_text(c) for c in cls.find_all(["th", "td"], recursive=False)) + " |"

    lines = []
    rows = node.find_all("tr")
    if not rows:
        return ""
    head = node.find("thead")
    if head is not None:
        for tr in head.find_all("tr"):
            lines.append(row(tr))
        lines.append("|" + "---|" * len(rows[0].find_all(["th", "td"], recursive=False)))
        rest = [tr for tr in rows if tr.find_parent("thead") is None]
    else:
        lines.append(row(rows[0]))
        lines.append("|" + "---|" * len(rows[0].find_all(["th", "td"], recursive=False)))
        rest = rows[1:]
    for tr in rest:
        lines.append(row(tr))
    return "\n" + "\n".join(lines) + "\n"


def block(node, base):
    name = getattr(node, "name", None)
    if name is None:
        text = str(node).strip()
        return f"\n{text}\n" if text else ""
    if name in SKIP_TAGS or skippable(node):
        return ""
    if name in HEADINGS:
        text = collapse(inline(node, base))
        return f"\n{'#' * HEADINGS[name]} {text}\n" if text else ""
    if name == "pre":
        code = node.get_text().rstrip()
        code_cls = " ".join(" ".join(c.get("class", [])) for c in node.find_all("code", recursive=False))
        classes = " ".join(node.get("class", [])) + " " + code_cls
        m = re.search(r"language-([\w+#-]+)", classes)
        lang = m.group(1) if m else ""
        return f"\n```{lang}\n{code}\n```\n"
    if name == "table":
        return render_table(node, base)
    if name in ("ul", "ol"):
        return render_list(node, base, 0)
    if name == "blockquote":
        inner = "".join(block(c, base) for c in node.children).strip()
        return "\n" + "\n".join("> " + line for line in inner.splitlines()) + "\n" if inner else ""
    if name == "div":
        classes = " ".join(node.get("class", []))
        if "theme-admonition" in classes or "admonition" in classes.split():
            m = (
                re.search(r"theme-admonition-(\w+)", classes)
                or re.search(r"alert--(\w+)", classes)
                or re.search(r"\b(attention|caution|danger|error|hint|important|note|tip|warning|seealso)\b", classes)
            )
            kind = (m.group(1) if m else "note").upper()
            title = node.find("p", class_="admonition-title")
            content = node.find("div", class_=re.compile(r"^admonitionContent"))
            kids = content.children if content else (c for c in node.children if c is not title)
            inner = "".join(block(c, base) for c in kids).strip()
            quoted = "\n".join(("> " + line).rstrip() for line in inner.splitlines())
            return f"\n> **[{kind}]**\n{quoted}\n" if inner else ""
    if name == "hr":
        return "\n---\n"
    if name in ("p", "caption", "figcaption"):
        text = collapse(inline(node, base))
        return f"\n{text}\n" if text else ""
    return "".join(block(c, base) for c in node.children)


def content_element(soup):
    for selector in CONTENT_SELECTORS:
        el = soup.select_one(selector)
        if el is not None and collapse(el.get_text()):
            return el
    return None


def page_to_md(session, url):
    """Returns (markdown | None, error | None)."""
    resp, err = get(session, url)
    if resp is None:
        return None, err
    soup = BeautifulSoup(resp.text, "html.parser")
    el = content_element(soup)
    if el is None:
        return None, "JS-RENDERED (content element missing from server HTML)"
    md = re.sub(r"\n{3,}", "\n\n", block(el, url)).strip()
    if len(md) < 20:
        return None, f"EMPTY CONTENT ({len(md)} chars)"
    return md + "\n", None


# ---------- output helpers ----------

def file_name_for(url, flatten):
    path = urlsplit(url).path
    if flatten:
        path = re.sub(r"^/docs/", "", path)
    parts = [re.sub(r"[^A-Za-z0-9._-]+", "-", p).strip("-") for p in path.split("/") if p]
    if parts and parts[-1].lower().endswith(".html"):
        parts[-1] = parts[-1][: -len(".html")]
    if parts and parts[-1].lower().endswith(".htm"):
        parts[-1] = parts[-1][: -len(".htm")]
    if not parts:
        parts = ["_index"]
    name = ("-".join(parts) if flatten else "/".join(parts)) + ".md"
    return name


# ---------- modes ----------

def run_verify(urls, workers, min_chars, probe):
    session = new_session()

    def check(url):
        try:
            resp, err = get(session, url)
            if resp is None:
                return url, err
            if probe:
                el = content_element(BeautifulSoup(resp.text, "html.parser"))
                if el is None:
                    return url, "THIN (server HTML lacks rendered content)"
                n = len(el.get_text(strip=True))
                if n < min_chars:
                    return url, f"THIN ({n} chars)"
            return url, None
        except Exception as exc:  # noqa: BLE001
            return url, f"{type(exc).__name__}"

    with ThreadPoolExecutor(max_workers=workers) as pool:
        failures = [r for r in pool.map(check, urls) if r[1]]
    if failures:
        for url, reason in failures:
            print(f"FAIL {reason}: {url}", file=sys.stderr)
        print(f"{len(failures)}/{len(urls)} failed", file=sys.stderr)
        return 1
    print("OK")
    return 0


def safe_scrape(session, url):
    try:
        return page_to_md(session, url)
    except Exception as exc:  # noqa: BLE001 - one bad page must not kill the run
        return None, f"{type(exc).__name__}: {exc}"


def run_scrape(urls, output, workers, base_path, flatten):
    session = new_session()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(lambda u: safe_scrape(session, u), urls))
    failures = [(u, e) for u, (_, e) in zip(urls, results) if e]
    if failures:
        for url, reason in failures:
            print(f"FAIL {reason}: {url}", file=sys.stderr)
    if output:
        out_dir = Path(output)
        used = {}
        written = 0
        for url, (md, err) in zip(urls, results):
            if err:
                continue
            name = file_name_for(url, flatten)
            if name in used:
                stem, _, tail = name.rpartition(".md")
                name = f"{stem}-{len(used)}{'.md' if not tail else ''}"
            used[name] = True
            dest = out_dir / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"<!-- {url} -->\n{md}", encoding="utf-8")
            written += 1
        print(f"wrote {written}/{len(urls)} pages to {out_dir}")
    else:
        for url, (md, err) in zip(urls, results):
            if err:
                continue
            print(f"\n{'=' * 8}\n# {url}\n{'=' * 8}\n")
            sys.stdout.write(md)
        print(f"\n{len(urls) - len(failures)}/{len(urls)} pages printed ({len(failures)} failed)", file=sys.stderr)
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(prog="scrape.py", description=__doc__.splitlines()[0], formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("command", nargs="?", choices=["ionic"], help="framework command (currently: ionic)")
    ap.add_argument("target", nargs="?", help="start URL (auto mode only)")
    ap.add_argument("--auto", metavar="START_URL", help="auto-discover doc URLs for a site subtree (best effort)")
    ap.add_argument("--url", action="append", default=[], help="explicit URL to scrape (repeatable)")
    ap.add_argument("--output", help="directory for Markdown files (omit for console)")
    ap.add_argument("--verify", action="store_true", help="check all resolved URLs pass; print OK")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--min-chars", type=int, default=120, help="verify-mode thin threshold")
    ns = ap.parse_args()

    given = [bool(ns.command), bool(ns.target), bool(ns.auto), bool(ns.url)]
    if sum(given[:1] + given[2:]) > 1 or (ns.target and not ns.auto):
        ap.error("choose exactly one: `ionic`, `--auto START_URL`, or `--url URL ...`")
    if not any(given):
        ap.error("no mode given (see --help)")

    session = new_session()
    flatten = False
    base_path = ""
    if ns.command == "ionic":
        urls = resolve_ionic(session)
        base_path = "/docs"
        flatten = True
    elif ns.auto:
        urls = discover_urls(session, ns.auto)
        if not urls:
            sys.exit(f"auto: discovered 0 URLs under {ns.auto}")
        print(f"auto: discovered {len(urls)} URLs", file=sys.stderr)
        base_path = urlsplit(ns.auto).path
    else:
        urls = []
        for u in ns.url:
            urls.extend(x.strip() for x in u.split(",") if x.strip())

    if ns.verify:
        probe = bool(ns.command)  # content-element probe only for known SSR frameworks
        sys.exit(run_verify(urls, ns.workers, ns.min_chars, probe))
    sys.exit(run_scrape(urls, ns.output, ns.workers, base_path, flatten))


if __name__ == "__main__":
    main()
