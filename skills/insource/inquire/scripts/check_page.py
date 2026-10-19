#!/usr/bin/env python3
"""Headless-browser smoke test for a built Inquire page (needs: pip install playwright && playwright install chromium).

usage: check_page.py page.html [--shots DIR]
Checks, at phone and desktop widths: no JS errors, no sideways page scroll, every option can be
clicked without errors, visible question numbers are unique, textareas grow and stop at their
limit, Shift+Enter makes a new line, an empty Skip is refused, and every code block has a Copy button.
Exit code 1 if any check fails.
"""
import argparse, pathlib, sys
from playwright.sync_api import sync_playwright

fails = []
def check(ok, msg):
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok: fails.append(msg)

def run(p, url, w, shots):
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": w, "height": 900})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
    pg.goto(url); pg.wait_for_timeout(400)
    tag = f"[{w}px] "
    check(pg.evaluate("document.documentElement.scrollWidth <= window.innerWidth + 1"), tag + "no sideways page scroll")
    # click through every option of every currently visible question, repeatedly (reveals branches)
    for _ in range(4):
        for lab in pg.query_selector_all(".q:not([hidden]) label.opt:not([hidden])"):
            inp = lab.query_selector("input")
            if inp and inp.get_attribute("value") != "c" and lab.is_visible():
                try: lab.click(position={"x": 12, "y": 12}, timeout=1500)
                except Exception: pass
    pg.wait_for_timeout(300)
    nums = pg.eval_on_selector_all(".q:not([hidden]) .n", "e=>e.map(x=>x.textContent)")
    check(len(nums) == len(set(nums)) and all(nums), tag + f"visible question numbers are unique {nums}")
    # textarea growth and limit
    ta = pg.query_selector(".q:not([hidden]) textarea")
    if ta:
        ta.scroll_into_view_if_needed(); h0 = ta.bounding_box()["height"]
        ta.click(); pg.keyboard.type("line")
        for _ in range(30):
            pg.keyboard.press("Shift+Enter"); pg.keyboard.type("more text")
        h1 = ta.bounding_box()["height"]; mh = pg.evaluate("e=>parseFloat(getComputedStyle(e).maxHeight)", ta)
        check(h1 > h0, tag + f"answer textarea grows ({h0:.0f}px to {h1:.0f}px)")
        check(h1 <= mh + 2, tag + f"answer textarea stops at its limit ({mh:.0f}px)")
    skm = pg.query_selector("#skm"); skm.click(); pg.keyboard.press("Enter"); pg.wait_for_timeout(150)
    check("bad" in (skm.get_attribute("class") or ""), tag + "empty Skip is refused")
    pg.keyboard.type("first"); pg.keyboard.press("Shift+Enter"); pg.keyboard.type("second")
    check("\n" in skm.input_value(), tag + "Shift+Enter inserts a new line in the skip box")
    nb = pg.eval_on_selector_all("[data-code-missing-copy]", "e=>e.length")
    codes = pg.eval_on_selector_all(".cb", "e=>e.map(x=>!!x.querySelector('.cpy'))")
    check(all(codes), tag + f"all {len(codes)} code blocks have a Copy button")
    check(not errs, tag + "no JS errors" + (": " + "; ".join(errs[:3]) if errs else ""))
    if shots:
        pathlib.Path(shots).mkdir(parents=True, exist_ok=True)
        pg.screenshot(path=f"{shots}/page-{w}.png", full_page=True)
    b.close()

ap = argparse.ArgumentParser(); ap.add_argument("page"); ap.add_argument("--shots")
a = ap.parse_args()
url = pathlib.Path(a.page).resolve().as_uri()
with sync_playwright() as p:
    for w in (375, 1280): run(p, url, w, a.shots)
sys.exit(1 if fails else 0)
