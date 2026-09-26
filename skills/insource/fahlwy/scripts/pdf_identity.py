#!/usr/bin/env python3
"""Prove what a PDF really is, with no external tools.

- walks every FlateDecode stream (object streams too) to find the page-tree
  /Type /Pages ... /Count N, and /Info /Title (plain, hex, or UTF-16BE)
- extracts text from the first content stream's Tj/TJ operators as a fingerprint
"""
from __future__ import annotations

import pathlib
import re
import sys
import zlib

STREAM = re.compile(rb"stream\r?\n(.*?)endstream", re.S)
PAGES = re.compile(rb"/Type\s*/Pages(?!(\s*/[A-Za-z]))")
COUNT = re.compile(rb"/Count\s+(\d{1,5})")
TITLE = re.compile(rb"/Title\s*(\(((?:[^()\\]|\\.)*)\)|<([0-9A-Fa-f]{4,256})>)")


def unescape(b: bytes) -> bytes:
    return b.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")


def decode_title(m: re.Match) -> str:
    if m.group(2) is not None:
        raw = unescape(m.group(2))
    else:
        raw = bytes.fromhex(m.group(3).decode("ascii"))
    if raw[:2] in (b"\xfe\xff",):
        return raw[2:].decode("utf-16-be", "replace")
    if len(raw) >= 2 and raw[0] == 0 and raw[2:3] == b"\x00"[:0] + raw[2:3]:
        pass
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", "replace")


def text_from(content: bytes) -> str:
    chunks = re.findall(rb"\((?:[^()\\]|\\.)*\)", content)
    out = "".join(unescape(c[1:-1]).decode("latin-1", "replace") for c in chunks)
    out = re.sub(r"\s+", " ", out)
    return out[:240]


def inspect(path: pathlib.Path) -> str:
    data = path.read_bytes()
    counts, titles, samples = [], [], []
    for m in STREAM.finditer(data):
        raw = m.group(1)
        try:
            dec = zlib.decompress(raw)
        except zlib.error:
            try:
                dec = zlib.decompressobj().decompress(raw)
            except zlib.error:
                continue
        for p in PAGES.finditer(dec):
            tail = dec[p.start():p.end() + 200]
            for c in COUNT.finditer(tail):
                counts.append(int(c.group(1)))
        for t in TITLE.finditer(dec):
            titles.append(decode_title(t))
        if b"Tj" in dec or b"TJ" in dec:
            s = text_from(dec)
            if len(s.split()) > 12:
                samples.append(s)
    for t in TITLE.finditer(data):
        titles.append(decode_title(t))
    # also scan uncompressed page tree
    for p in PAGES.finditer(data):
        for c in COUNT.finditer(data[p.start():p.end() + 200]):
            counts.append(int(c.group(1)))
    pages = max(counts) if counts else 0
    title = max(titles, key=len) if titles else ""
    title = "".join(ch for ch in title if 32 <= ord(ch) < 127).strip()
    samples.sort(key=lambda s: -len(s.split()))
    fingerprint = samples[0][:120] if samples else "(no text extracted)"
    return (f"{path.name:52} {len(data)/1e6:6.1f}MB pages={pages or '?':>4} "
            f"title={title[:38]!r:42}\n{'':12}fingerprint: {fingerprint!r}")


def main() -> int:
    root = pathlib.Path(sys.argv[1])
    files = sorted(root.glob("*.pdf"))
    for f in files:
        print(inspect(f))
    print(f"\n{len(files)} files inspected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
