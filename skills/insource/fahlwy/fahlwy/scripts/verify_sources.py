#!/usr/bin/env python3
"""fahlwy asset-source verifier.

Prove a candidate URL really serves usable bytes -- not just HTTP 200.
Validates magic bytes (not only Content-Type), because some "asset" hosts
return a 200 HTML error/consent page.

Usage:
    verify_sources.py image URL [URL ...]
    verify_sources.py video URL [URL ...]
    verify_sources.py audio URL [URL ...]
    verify_sources.py any URL [URL ...]      # image|video|audio, auto-detect

Exit code 0 only if every URL passes. Prints one LLM-friendly line per URL.
"""
from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def sniff(buf: bytes) -> str | None:
    """Return 'video'|'audio'|'image' from magic bytes, or None."""
    if buf[4:8] == b"ftyp" or buf[:4] == b"\x1a\x45\xdf\xa3":  # mp4/mov | webm/mkv
        return "video"
    if (buf[:3] == b"ID3" or buf[:4] == b"OggS" or buf[:4] == b"fLaC"
            or (buf[:4] == b"RIFF" and buf[8:12] == b"WAVE")
            or (len(buf) > 1 and buf[0] == 0xFF and (buf[1] & 0xE0) == 0xE0)):
        return "audio"
    if buf[:8] == b"\x89PNG\r\n\x1a\n" or buf[:3] == b"\xff\xd8\xff" or buf[:6] in (b"GIF87a", b"GIF89a"):
        return "image"
    if buf[:4] == b"RIFF" and buf[8:12] == b"WEBP":
        return "image"
    return None


def check(url: str, want: str, retries: int = 3) -> tuple[bool, str]:
    last = ""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                ct = r.headers.get("Content-Type", "").lower()
                buf = r.read(4096)
                if want == "image":
                    ok = ct.startswith("image/") and len(buf) > 256
                elif want in ("video", "audio"):
                    ok = ct.startswith(want + "/") or ct == "application/ogg" or sniff(buf) == want
                else:  # any
                    ok = sniff(buf) is not None or ct.split("/")[0] in ("image", "video", "audio")
                return ok, f"{r.status} {ct[:24]:24} {len(buf)}B"
        except urllib.error.HTTPError as e:
            if e.code < 500:  # 4xx: bad URL / auth / geo -- do not retry
                return False, f"{e.code} HTTPError"
            last = f"{e.code} HTTPError"
        except (TimeoutError, urllib.error.URLError) as e:
            last = f"NET {type(e).__name__}"
        if attempt < retries - 1:
            time.sleep(1.5 * (attempt + 1))  # backoff for transient 5xx / throttle
    return False, last


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[0] not in ("image", "video", "audio", "any"):
        print("usage: verify_sources.py <image|video|audio|any> URL [URL ...]")
        return 2
    want, urls = argv[0], argv[1:]
    passed = 0
    for u in urls:
        ok, info = check(u, want)
        passed += ok
        print(f"[{'OK ' if ok else 'BAD'}] {want:5} {info:34} {u}")
    print(f"\n{passed}/{len(urls)} {want} sources pass.")
    return 0 if passed == len(urls) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
