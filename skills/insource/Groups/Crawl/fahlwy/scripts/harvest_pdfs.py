#!/usr/bin/env python3
"""Harvest direct .pdf links out of official book landing pages.

Given pages (one per line, optional "label<TAB>url"), fetch the HTML and
extract every href that ends in .pdf (absolutised against the page URL).
Prints "host<TAB>url" so the result can be piped into pdf_probe.py.
"""
from __future__ import annotations

import concurrent.futures as cf
import html
import re
import sys
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")
LINK_RE = re.compile(r"""(?:href|src)=["']([^"'>]+?)["']""", re.I)


def harvest(page: str) -> list[str]:
    try:
        req = urllib.request.Request(page, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40) as r:
            raw = r.read(2_000_000)
            base = r.geturl()
    except Exception as e:
        return [f"##ERR {type(e).__name__} {e} :: {page}"]
    text = html.unescape(raw.decode("utf-8", "replace"))
    found, seen = [], set()
    for m in LINK_RE.finditer(text):
        href = m.group(1).strip()
        if href.startswith(("data:", "javascript:")):
            continue
        absu = urllib.parse.urljoin(base, href)
        if absu.lower().split("?")[0].endswith(".pdf") and absu not in seen:
            seen.add(absu)
            found.append(absu)
    if not found:
        # also catch bare URLs typed into the HTML
        for u in re.findall(r"https?://\S+?\.pdf", text, re.I):
            u = u.rstrip('"\')., >')
            if u not in seen:
                seen.add(u)
                found.append(u)
    return found or [f"##NONE no pdf href :: {page}"]


def main() -> None:
    pages = [l.strip() for l in sys.stdin if l.strip() and not l.startswith("#")]
    if len(sys.argv) > 1:
        pages = sys.argv[1:]
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        for urls in ex.map(harvest, pages):
            for u in urls:
                print(u)


if __name__ == "__main__":
    main()
