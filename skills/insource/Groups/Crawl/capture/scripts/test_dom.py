"""Browser test for `dom`: multilingual "show more", structural lazy-image promotion, safety. Needs Playwright.

  python test_dom.py        # exit 0 = all passed (skips if Playwright/Chromium is unavailable)
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))

PAGE = """<!doctype html><html lang="ar" dir="rtl"><body>
<ul id="list"></ul>
<button id="b1" onclick="add('item-ar')">عرض المزيد (12)</button>
<button id="b2" onclick="add('item-es')">Ver más</button>
<button id="b3" onclick="add('item-custom')">klik lagi</button>
<button id="b4" onclick="add('DESTRUCTIVE-CLICKED')">Delete all</button>
<img id="im1" data-hero-image="./pic.png" src="data:image/gif;base64,R0lGODlhAQABAAAAACw=">
<img id="im2" data-thumb-source="./thumb.png 1x, ./thumb2.png 2x">
<img id="im3" data-id="12345" alt="not a lazy attr">
<img id="im4" data-x7="./pic4.png">
<img id="im5" data-aa="./a.png" data-bb="./b.png">
<script>function add(t){const li=document.createElement('li');li.textContent=t;document.getElementById('list').appendChild(li);}</script>
</body></html>"""


def run(args, page):
    out = os.path.join(os.path.dirname(page), "out.html")
    r = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "dom", page, "-o", out, "--wait-ms", "200",
                        "--scroll-pause-ms", "150", "--max-rounds", "3", *args], capture_output=True, text=True)
    return r, (open(out, encoding="utf-8").read() if os.path.exists(out) else "")


def main() -> int:
    try:
        import importlib
        importlib.import_module("playwright")
    except ImportError:
        print("SKIP: Playwright not installed")
        return 0
    failures = []

    def check(name, cond):
        print(("ok   " if cond else "FAIL ") + name)
        if not cond:
            failures.append(name)

    tmp = tempfile.mkdtemp(prefix="dom-test-")
    page = os.path.join(tmp, "p.html")
    open(page, "w", encoding="utf-8").write(PAGE)

    r, h = run(["--more-phrase", "klik lagi"], page)
    if r.returncode != 0:
        print("SKIP: browser not usable here:", (r.stderr or r.stdout).strip()[-160:])
        shutil.rmtree(tmp, ignore_errors=True)
        return 0
    li = lambda t, html: f"<li>{t}</li>" in html     # the RENDERED element, not the onclick source text
    check("Arabic 'show more' (with a count suffix) is clicked", li("item-ar", h))
    check("Spanish 'show more' is clicked", li("item-es", h))
    check("custom --more-phrase is clicked", li("item-custom", h))
    check("a destructive button is never clicked", not li("DESTRUCTIVE-CLICKED", h))
    check("lazy image under an unlisted attribute name is promoted", 'src="file://' in h.split('id="im1"')[1].split(">")[0] and "pic.png" in h.split('id="im1"')[1].split(">")[0])
    check("srcset-shaped lazy value goes to srcset", "srcset=" in h.split('id="im2"')[1].split(">")[0] and "thumb2.png" in h.split('id="im2"')[1].split(">")[0])
    check("non-URL data attribute is left alone", " src=" not in h.split('id="im3"')[1].split(">")[0])

    check("single URL-valued data attribute is promoted without any name hint", "pic4.png" in h.split('id="im4"')[1].split(">")[0] and " src=" in h.split('id="im4"')[1].split(">")[0])
    check("several ambiguous candidates (no name hint) are left alone", " src=" not in h.split('id="im5"')[1].split(">")[0])

    def cli(*extra):
        r_ = subprocess.run([sys.executable, os.path.join(HERE, "capture.py"), "dom", page, *extra], capture_output=True, text=True)
        return r_.returncode, (r_.stderr + r_.stdout)
    code, text = cli("--storage-state", os.path.join(tmp, "missing.json"))
    check("missing --storage-state fails fast with a clear message", code != 0 and "not found" in text)
    code, text = cli("--stable-rounds", "0")
    check("invalid numeric options are rejected", code != 0 and "--stable-rounds" in text)

    r, h = run(["--more-lang", "ar"], page)
    check("--more-lang ar: Arabic clicked, Spanish not", li("item-ar", h) and not li("item-es", h))
    r, h = run(["--no-expand"], page)
    check("--no-expand clicks nothing", not li("item-ar", h) and not li("item-es", h))
    r, h = run(["--no-expand", "--lazy-attr", "data-id"], page)
    check("--lazy-attr names an attribute explicitly", " src=" in h.split('id="im3"')[1].split(">")[0])

    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{'FAILED: ' + ', '.join(failures) if failures else 'all dom tests passed'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
