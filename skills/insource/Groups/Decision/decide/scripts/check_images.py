#!/usr/bin/env python3
"""Check that every image a decide page references exists and loads.

Usage: python check_images.py page.html [--hosted] [--browser] [--timeout 12]

Finds image references in <img src>, srcset, CSS url(...), and string literals inside the
page's script (full http(s) URLs ending in an image extension, and data:image URIs).
Keep full URLs as plain string literals in data arrays so they can be found.

Each reference is reported as OK, WARN (could not verify here) or PROBLEM (verified bad):
  - data URIs: must decode and be a real image
  - local paths: must exist next to the page and decode
  - http(s) URLs: must answer 200, return image bytes (not an HTML error page), decode,
    and not be a tiny tracking pixel. A request blocked by this environment's network policy is a
    WARN, not a PROBLEM: open the page in a browser to confirm.
Page-level checks: <img> needs alt text, a fallback for failed loads, and reserved space.

--hosted   for hosted viewers that block remote and local images: every reference must
           be a data: URI. Anything else is a PROBLEM.
--browser  also load the page in headless Chromium (Playwright) and report images that
           did not decode.
Exit code 1 if any PROBLEM is found.
"""
import re, sys, os, io, base64, urllib.request, urllib.error, urllib.parse
from concurrent.futures import ThreadPoolExecutor

try:
    from PIL import Image
except Exception:
    Image = None

# Tunable limits. Adjust them for the environment or the page.
MIN_PX = 64      # smaller images are flagged as icons or tracking pixels
MAX_KB = 2500    # larger files are flagged for compression

EXT = r"(?:png|jpe?g|gif|webp|avif|svg|bmp|ico)"

def line_of(text, idx):
    return text.count("\n", 0, idx) + 1

def collect(html):
    refs, seen, page = [], set(), []
    def add(url, idx):
        url = url.strip()
        if url and url not in seen:
            seen.add(url); refs.append((url, line_of(html, idx)))
    for m in re.finditer(r"<img\b([^>]*)>", html, re.I | re.S):
        a = m.group(1)
        src = re.search(r"\bsrc\s*=\s*(?:\"([^\"]*)\"|'([^']*)')", a)
        if src: add(src.group(1) or src.group(2) or "", m.start())
        if not re.search(r"\balt\s*=", a):
            page.append(("PROBLEM", f"line {line_of(html, m.start())}: <img> without alt text"))
    for m in re.finditer(r"\bsrcset\s*=\s*\"([^\"]*)\"", html, re.I):
        for part in m.group(1).split(","):
            if part.strip(): add(part.strip().split()[0], m.start())
    for m in re.finditer(r"url\(\s*[\"']?([^)\"']+)[\"']?\s*\)", html, re.I):
        u = m.group(1)
        if u.startswith("data:image") or re.search(r"\." + EXT + r"(\?|$)", u, re.I): add(u, m.start())
    for m in re.finditer(r"[\"'`](https?://[^\"'`\s<>]+?\." + EXT + r"(?:\?[^\"'`\s<>]*)?)[\"'`]", html, re.I):
        add(m.group(1), m.start())
    for m in re.finditer(r"[\"'`](data:image/[a-z+.\-]+;base64,[A-Za-z0-9+/=]+)[\"'`]", html, re.I):
        add(m.group(1), m.start())
    return refs, page

def verify_bytes(raw, label):
    head = raw[:16]
    txt = raw[:300].lstrip().lower()
    if txt.startswith((b"<!doctype html", b"<html")):
        return "PROBLEM", f"{label}: returned an HTML page, not an image"
    is_svg = b"<svg" in raw[:2000].lower()
    magic = head.startswith((b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"BM")) or (head[:4] == b"RIFF" and raw[8:12] == b"WEBP") or raw[4:12] in (b"ftypavif", b"ftypavis") or head[:4] == b"\x00\x00\x01\x00"
    if not (magic or is_svg):
        return "PROBLEM", f"{label}: content is not a recognizable image"
    kb = len(raw) / 1024
    if is_svg: return "OK", f"{label}: SVG, {kb:.0f} KB"
    if Image is None: return "WARN", f"{label}: {kb:.0f} KB, decoding not verified (Pillow not installed)"
    try:
        im = Image.open(io.BytesIO(raw)); im.verify(); im = Image.open(io.BytesIO(raw)); w, h = im.size
    except Exception as e:
        return "PROBLEM", f"{label}: image data is corrupt ({str(e)[:60]})"
    if w < MIN_PX or h < MIN_PX: return "WARN", f"{label}: only {w}x{h}px (icon or tracking pixel?)"
    if kb > MAX_KB: return "WARN", f"{label}: {w}x{h}px but {kb/1024:.1f} MB, compress it"
    return "OK", f"{label}: {w}x{h}px, {kb:.0f} KB"

def check(ref, base, hosted, timeout):
    url, line = ref
    short = url if len(url) < 70 else url[:67] + "..."
    if url.startswith("data:"):
        try: raw = base64.b64decode(url.split(",", 1)[1])
        except Exception: return "PROBLEM", f"line {line}: data URI cannot be decoded"
        s, msg = verify_bytes(raw, "data URI"); return s, f"line {line}: {msg}"
    p = urllib.parse.urlparse(url)
    if hosted:
        return "PROBLEM", f"line {line}: {short} is not a data: URI. Hosted pages block remote and local images, so embed it"
    if p.scheme in ("http", "https"):
        prefix = f"line {line}: {short}"
        if p.scheme == "http": prefix += " (http: blocked as mixed content on https pages)"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (decide image check)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                raw = r.read(8_000_001); ctype = r.headers.get("Content-Type", "")
        except urllib.error.HTTPError as e:
            if e.headers.get("x-deny-reason"): return "WARN", f"{prefix}: blocked by this environment's network policy ({e.headers.get('x-deny-reason')}); could not verify, check in a browser"
            return "PROBLEM", f"{prefix}: HTTP {e.code}"
        except Exception as e:
            return "WARN", f"{prefix}: could not connect ({str(e)[:70]}); bad host or network limit, check in a browser"
        s, msg = verify_bytes(raw, "image")
        if s == "OK" and not ctype.lower().startswith("image/"): s, msg = "WARN", msg + f"; Content-Type is '{ctype}'"
        if p.scheme == "http" and s == "OK": s = "WARN"
        return s, f"{prefix}: {msg}"
    path = os.path.join(base, urllib.parse.unquote(url))
    if not os.path.isfile(path): return "PROBLEM", f"line {line}: {short} not found next to the page"
    s, msg = verify_bytes(open(path, "rb").read(), "file"); return s, f"line {line}: {short}: {msg}"

def browser_check(path):
    from playwright.sync_api import sync_playwright
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page()
        pg.goto("file://" + os.path.abspath(path), wait_until="load")
        pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')")
        pg.wait_for_timeout(2500)
        for r in pg.evaluate("[...document.images].map(i=>({s:(i.currentSrc||i.src).slice(0,80),a:i.alt,ok:i.complete&&i.naturalWidth>0}))"):
            out.append(("OK" if r["ok"] else "PROBLEM", f"browser: {r['s']} ({r['a'] or 'no alt'}) " + ("loaded" if r["ok"] else "did not load")))
        b.close()
    return out

def main():
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    path = sys.argv[1]; hosted = "--hosted" in sys.argv
    timeout = float(sys.argv[sys.argv.index("--timeout") + 1]) if "--timeout" in sys.argv else 12
    html = open(path, encoding="utf-8").read(); base = os.path.dirname(os.path.abspath(path))
    refs, results = collect(html)
    with ThreadPoolExecutor(8) as ex:
        results += list(ex.map(lambda r: check(r, base, hosted, timeout), refs))
    n_img = len(re.findall(r"<img\b", html, re.I)) + len(refs)
    if refs or "<img" in html.lower():
        if not re.search(r"onerror\s*=|addEventListener\(\s*[\"']error[\"']", html):
            results.append(("WARN", "no fallback for failed image loads (add an error handler that shows a placeholder with the alt text)"))
        if "aspect-ratio" not in html and not re.search(r"<img[^>]+\bwidth\s*=", html, re.I):
            results.append(("WARN", "images have no reserved size (add aspect-ratio or width/height to avoid layout jumps)"))
    if "--browser" in sys.argv:
        try: results += browser_check(path)
        except Exception as e: results.append(("WARN", f"browser check skipped: {e}"))
    if not refs and "<img" not in html.lower(): print("note: no images referenced"); sys.exit(0)
    for lvl in ("PROBLEM", "WARN", "OK"):
        for s, m in results:
            if s == lvl: print(f"{s:7} {m}")
    bad = sum(1 for s, _ in results if s == "PROBLEM"); warn = sum(1 for s, _ in results if s == "WARN")
    print(f"\n{len(refs)} reference(s): {bad} problem(s), {warn} warning(s). Warnings mean the check could not confirm; open the page in a browser.")
    sys.exit(1 if bad else 0)

if __name__ == "__main__":
    main()
