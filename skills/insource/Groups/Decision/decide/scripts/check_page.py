#!/usr/bin/env python3
"""Check a decide HTML page.

Usage: python check_page.py page.html [--pdf out.pdf]

Checks:
  1. Inline <script> contains no literal "<!--" or nested "<script" (unclosed-tag bug).
  2. Inline JavaScript parses (needs node; skipped if missing).
  3. Basic requirements: viewport meta, theme query param, print stylesheet, Export button,
     and a dedicated freshness section (data-section="freshness") holding the comparison date.
  4. With --pdf: renders the print view with headless Chromium (Playwright), reports page
     count and flags nearly empty pages (blank-gap bug). Needs playwright + pdftotext.

Prints one line per finding. Exit code 1 if any PROBLEM is found.
"""
import re, subprocess, sys, tempfile, os, shutil

BLANK_PAGE_CHARS = 350  # PDF pages with less text than this are flagged as nearly empty

def main():
    if len(sys.argv) < 2:
        print("usage: check_page.py page.html [--pdf out.pdf]"); sys.exit(2)
    path = sys.argv[1]
    pdf = sys.argv[sys.argv.index("--pdf") + 1] if "--pdf" in sys.argv else None
    html = open(path, encoding="utf-8").read()
    problems, notes = [], []

    scripts = [m for m in re.finditer(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script\s*>", html, re.S | re.I)]
    if not scripts:
        problems.append("no inline <script> found")
    for i, m in enumerate(scripts):
        body = m.group(1)
        if "<!--" in body:
            problems.append(f"script {i+1}: literal '<!--' inside script. Write '<\\!--' in JS strings.")
        if "<!--" in body and re.search(r"<script\b", body, re.I):
            problems.append(f"script {i+1}: '<!--' plus '<script' inside script puts the parser in double-escaped state. Escape both.")
    rest = re.sub(r"<script\b(?![^>]*\bsrc=)[^>]*>.*?</script\s*>", "", html, flags=re.S | re.I)
    if re.search(r"<script\b(?![^>]*\bsrc=)", rest, re.I) or re.search(r"</script", rest, re.I):
        problems.append("stray or unclosed <script> tag outside the inline script (a '</script>' inside a JS string must be written '<\\/script>').")

    if shutil.which("node") and scripts:
        for i, m in enumerate(scripts):
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(m.group(1)); tmp = f.name
            r = subprocess.run(["node", "--check", tmp], capture_output=True, text=True)
            os.unlink(tmp)
            if r.returncode:
                problems.append(f"script {i+1}: JS syntax error: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else 'unknown'}")
    else:
        notes.append("node not found: JS syntax not checked")

    if "viewport-fit=cover" not in html and 'name="viewport"' not in html:
        problems.append("missing viewport meta tag")
    if "URLSearchParams" not in html or "theme" not in html:
        problems.append("no ?theme=light|dark handling found")
    if 'data-section="freshness"' not in html:
        problems.append("no freshness section: add an element with data-section=\"freshness\" showing the compared-on date, data period and re-check date")
    if "@media print" not in html:
        problems.append("no print stylesheet (@media print)")
    if "window.print" not in html:
        problems.append("no Export PDF button wired to window.print()")
    if re.search(r"<img\b|data:image/|https?://[^\"'\s]+\.(?:png|jpe?g|gif|webp|avif|svg)", html, re.I):
        notes.append("images found: run scripts/check_images.py (add --hosted if the page will be published)")
    if re.search(r"<(?:audio|video)\b|\.(?:mp3|wav|ogg|opus|flac|m4a|mp4|webm|mov|pdf|glb|gltf|woff2?)\b", html, re.I):
        notes.append("media found: run scripts/check_media.py (or write a checker for this medium, see references/media.md)")
    if "localStorage" in html:
        notes.append("localStorage used: wrap in try/catch and do not depend on it")

    if pdf:
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b = p.chromium.launch(); pg = b.new_page()
                pg.goto("file://" + os.path.abspath(path), wait_until="domcontentloaded")
                pg.wait_for_timeout(600)
                pg.emulate_media(media="print")
                pg.evaluate("window.dispatchEvent(new Event('beforeprint'))")
                pg.pdf(path=pdf, prefer_css_page_size=True, print_background=True)
                b.close()
            info = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
            n = int(re.search(r"Pages:\s+(\d+)", info).group(1))
            notes.append(f"PDF rendered: {n} pages -> {pdf}")
            for pno in range(1, n + 1):
                t = subprocess.run(["pdftotext", "-f", str(pno), "-l", str(pno), pdf, "-"], capture_output=True, text=True).stdout
                chars = len(t.strip())
                if chars < BLANK_PAGE_CHARS and pno != n:
                    problems.append(f"PDF page {pno} is nearly empty ({chars} chars): check for unbreakable containers or grids")
                else:
                    notes.append(f"page {pno}: {chars} chars")
        except Exception as e:
            notes.append(f"PDF test skipped: {e}")

    for p_ in problems: print("PROBLEM:", p_)
    for n_ in notes: print("note:", n_)
    if not problems: print("OK: no problems found")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
