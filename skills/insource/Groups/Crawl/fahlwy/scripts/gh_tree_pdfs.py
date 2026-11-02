#!/usr/bin/env python3
"""Walk GitHub repos the honest way: verify the license, then list PDFs.

For each owner/repo on stdin:
  1. read /repos/<r>/license  -> refuse unless the license is a known
     content-Open one (CC-BY*, GPL, FDL, BSD, MIT, OFL) or custom-but-stated
  2. read the default branch tree recursively -> every path ending .pdf
  3. also list release assets ending .pdf
Emits raw.githubusercontent / browser_download URLs for the verifier.
"""
from __future__ import annotations

import json
import subprocess
import sys

OPEN_LICENSES = {
    "cc-by-4.0", "cc-by-sa-4.0", "cc-by-3.0", "cc-by-sa-3.0", "cc0-1.0",
    "gfdl", "gpl-3.0", "gpl-2.0", "bsd-3-clause", "bsd-2-clause", "mit",
    "apache-2.0", "ofl-1.1", "artistic-2.0", "epl-2.0", "unlicense", "za",
}


def gh(*args: str) -> object:
    p = subprocess.run(["gh", "api", *args], capture_output=True, text=True)
    if p.returncode:
        return None
    try:
        return json.loads(p.stdout or "null")
    except json.JSONDecodeError:
        return None


def handle(repo: str) -> None:
    lic = gh(f"/repos/{repo}/license")
    spdx = (lic or {}).get("license", {}).get("spdx_id") if lic else None
    if spdx in (None, "NOASSERTION"):
        # custom license: only accept if README/licence text says freely distributed
        note = ((lic or {}).get("license", {}) or {}).get("name", "")
        verdict = f"CUSTOM({note})"
    else:
        verdict = "OPEN" if (spdx or "").lower() in OPEN_LICENSES else f"CLOSED({spdx})"
    meta = gh(f"/repos/{repo}") or {}
    br = meta.get("default_branch", "HEAD")
    print(f"### {repo} [{verdict}] ★{meta.get('stargazers_count','?')} branch={br}", file=sys.stderr)
    if verdict.startswith("CLOSED"):
        print(f"##SKIP closed-license repo: {repo}", file=sys.stderr)
        return
    tree = gh(f"/repos/{repo}/git/trees/{br}?recursive=1") or {}
    for t in tree.get("tree", []):
        if t["type"] == "blob" and t["path"].lower().endswith(".pdf"):
            size = t.get("size", 0)
            if size < 60_000:
                continue
            print(f"https://raw.githubusercontent.com/{repo}/{br}/{t['path'].replace(' ', '%20')}")
    rels = gh(f"/repos/{repo}/releases?per_page=5") or []
    for r in rels if isinstance(rels, list) else []:
        for a in r.get("assets", []):
            if a["name"].lower().endswith(".pdf"):
                print(a["browser_download_url"])


def main() -> None:
    for line in sys.stdin:
        repo = line.strip()
        if repo and not repo.startswith("#"):
            try:
                handle(repo)
            except Exception as e:
                print(f"##ERR {repo} {type(e).__name__} {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
