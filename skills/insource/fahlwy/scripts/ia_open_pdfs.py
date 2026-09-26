#!/usr/bin/env python3
"""Internet Archive route, done safely: only emit PDFs from items that are
(a) not access-restricted (no lending library / no DRMS) and
(b) carry an explicit open license in their metadata.

Anything else -- including in-copyright scans and user uploads of commercial
books -- is skipped and reported, because those are not ours to download.

Usage: ia_open_pdfs.py "search query" [max_items]
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

UA = "fahlwy-research/1.0 (source-hunting script)"
OPEN_HINTS = ("creativecommons.org", "publicdomain", "gfdl", "opendatacommons",
              "mit-license", "apache.org/licenses", "opensource.org")


def get(url: str) -> object:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=45) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def search(query: str, rows: int) -> list[str]:
    q = urllib.parse.quote(query)
    u = (f"https://archive.org/advancedsearch.php?q={q}"
         f"&fl%5B%5D=identifier&fl%5B%5D=title&page=1&rows={rows}&output=json")
    j = get(u)
    return [d["identifier"] for d in j["response"]["docs"]]


def evaluate(ident: str) -> tuple[str | None, str]:
    try:
        j = get(f"https://archive.org/metadata/{urllib.parse.quote(ident)}")
    except Exception as e:
        return None, f"metadata-error {type(e).__name__}"
    md = j.get("metadata", {}) or {}
    if str(md.get("access-restricted-item", "")).lower() == "true":
        return None, "SKIP access-restricted (lending library / DRMS)"
    blob = json.dumps(md).lower()
    lic = next((h for h in OPEN_HINTS if h in blob), None)
    if not lic:
        return None, "SKIP no open-license field in metadata"
    if str(md.get("protecteddat", "")).lower() not in ("", "none"):
        return None, f"SKIP protecteddat={md.get('protecteddat')}"
    pdfs = [f["name"] for f in j.get("files", []) or []
            if f["name"].lower().endswith(".pdf")
            and int(f.get("size", 0) or 0) > 80_000
            and f.get("source") not in ("djvu_pt",)]
    if not pdfs:
        return None, f"SKIP no large pdf (license={lic})"
    title = md.get("title", ident)
    if isinstance(title, list):
        title = title[0]
    pick = sorted(pdfs, key=len)[0]
    u = f"https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(pick)}"
    return u, f"OK [{lic}] {str(title)[:58]} :: {pick}"


def main() -> None:
    query = sys.argv[1] if len(sys.argv) > 1 else "mediatype:texts AND subject:programming"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    ids = search(query, n)
    print(f"# {len(ids)} candidates for: {query}", file=sys.stderr)
    for i in ids:
        url, note = evaluate(i)
        print(f"# {i}: {note}", file=sys.stderr)
        if url:
            print(url)


if __name__ == "__main__":
    main()
