#!/usr/bin/env python3
"""pdf_extract.py - READ side of the pdf skill: get text out of a PDF, then split it into modules.

Why modules: a 145-page PDF is ~130k characters, which is far too much to read at once and far too little
to be useful as one opaque blob. Splitting the extracted text into numbered line-boxed module files with a
manifest lets you (or an agent) read the pages you need, search the rest, and cite page numbers accurately.

Usage:
  python scripts/pdf_extract.py IN.pdf --report
  python scripts/pdf_extract.py IN.pdf --out text.txt [--pages 1-10,14] [--layout] [--clean] [--markers]
  python scripts/pdf_extract.py IN.pdf --modules OUTDIR [--module-lines 200] [--manifest] [--clean --markers]
  python scripts/pdf_extract.py IN.pdf --modules OUTDIR --module-pages 5            # page-aligned modules
  python scripts/pdf_extract.py IN.pdf --out text.txt --engine pypdf               # force an engine

Flags:
  --engine auto|poppler|pypdf   extraction backend (default auto: poppler if installed, else pypdf)
  --pages 1-5,8,20-24          page selection, 1-based (default: all pages)
  --layout / --no-layout       keep the visual column layout (poppler only; default --layout)
  --markers                    insert '===== [page N] =====' lines so text can be traced back to pages
  --clean                      collapse repeated header/footer lines, 3+ blank lines, hyphen-split words
  --out FILE                   write one text file
  --modules DIR                write module files (module-0001.txt ...) instead of one blob
  --module-lines N             lines per module, default 200 (ignored with --module-pages)
  --module-pages N             pages per module - keeps citations honest, at the cost of uneven sizes
  --manifest                   write DIR/manifest.md + DIR/manifest.json (module -> pages, lines, chars)
  --report                     print per-page text stats, garble warnings, repeated-line candidates
  --preview N                  print N lines of the result to stdout (default 0: nothing)
  --max-line N                 hard wrap for output lines (default 0: leave as extracted)

stdout is ASCII and truncated so it never floods a context window. Exit 0 ok, 1 warnings worth reading,
2 usage/read/dependency error.
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

MARKER = "===== [page {n}] ====="
REPL = "\ufffd"


# ------------------------------------------------------------------ extraction

def have_poppler() -> bool:
    return bool(shutil.which("pdftotext"))


def parse_pages(spec: str, total: int) -> list[int]:
    """'1-5,8,20-24' -> [1,2,3,4,5,8,...] 1-based, validated."""
    out: list[int] = []
    if not spec:
        return list(range(1, total + 1))
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            lo, hi = int(a or 1), int(b or total)
        else:
            lo = hi = int(part)
        if lo < 1 or hi < lo or hi > total:
            raise ValueError("page range %r is outside 1..%d" % (part, total))
        out.extend(range(lo, hi + 1))
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            uniq.append(p)
    return sorted(uniq)


def extract_poppler(pdf: str, pages: list[int], layout: bool) -> list[str]:
    """One poppler call, split on its page breaks (form feeds)."""
    tmp = tempfile.NamedTemporaryFile("r", suffix=".txt", delete=False, encoding="utf-8", errors="replace")
    tmp.close()
    try:
        cmd = ["pdftotext"] + (["-layout"] if layout else ["-raw"])
        lo, hi = pages[0], pages[-1]
        contiguous = pages == list(range(lo, hi + 1))
        if contiguous:
            cmd += ["-f", str(lo), "-l", str(hi)]
        cmd += [pdf, tmp.name]
        subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
        text = io.open(tmp.name, encoding="utf-8", errors="replace").read()
        parts = text.split("\x0c")
        if parts and not parts[-1].strip():
            parts.pop()
        if contiguous:
            # poppler emitted only the requested range: parts[i] is pages[i]
            picked = parts[:len(pages)]
            return picked + [""] * (len(pages) - len(picked))
        # whole document extracted: index by absolute page number
        return [parts[p - 1] if p - 1 < len(parts) else "" for p in pages]
    finally:
        os.unlink(tmp.name)


def extract_pypdf(pdf: str, pages: list[int]) -> list[str]:
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.exit("2: pypdf is not installed and poppler was not found - install one: pip install pypdf")
    reader = PdfReader(pdf)
    out = []
    for n in pages:
        try:
            out.append(reader.pages[n - 1].extract_text() or "")
        except Exception as exc:                                # noqa: BLE001 - per-page resilience
            out.append("%s page %d unreadable: %s" % (MARKER.format(n=n), n, exc))
    return out


# ------------------------------------------------------------------ cleaning

def clean_pages(pages: list[str], strip_chrome: bool = True) -> list[str]:
    """Collapse blank runs, drop repeated header/footer lines, rejoin words split across a line break."""
    counts: dict[str, int] = {}
    if strip_chrome:
        for text in pages:
            for line in text.splitlines():
                s = line.strip()
                if 0 < len(s) <= 60:
                    counts[s] = counts.get(s, 0) + 1
    repeated = {k for k, v in counts.items() if v >= max(4, len(pages) // 3)}
    cleaned = []
    for text in pages:
        lines = []
        for raw in text.split("\n"):
            s = raw.rstrip()
            if s.strip() in repeated:
                continue
            lines.append(s)
        joined = "\n".join(lines)
        joined = re.sub(r"-\n(?=[a-z])", "", joined)              # hyphenation across a line break
        joined = re.sub(r"[ \t]{2,}", " ", joined)
        joined = re.sub(r"\n{3,}", "\n\n", joined)
        cleaned.append(joined.strip("\n"))
    return cleaned


def build_text(pages: list[str], numbers: list[int], markers: bool, max_line: int) -> str:
    chunks = []
    for n, text in zip(numbers, pages):
        if markers:
            chunks.append(MARKER.format(n=n))
        if max_line:
            text = "\n".join(shutil.wrap(t, max_line) if len(t) > max_line else t
                             for t in text.split("\n"))
        chunks.append(text)
    return "\n".join(chunks).strip("\n") + "\n"


# ------------------------------------------------------------------ modules

def split_modules(text: str, numbers: list[int], pages: list[str], mode: str, size: int,
                  markers: bool) -> list[dict]:
    """Group pages into module files: by line budget or by page count. Returns the manifest rows."""
    modules: list[dict] = []
    if mode == "pages":
        for start in range(0, len(numbers), size):
            idx = list(range(start, min(start + size, len(numbers))))
            body = build_text([pages[i] for i in idx], [numbers[i] for i in idx], markers, 0)
            modules.append({"pages": [numbers[idx[0]], numbers[idx[-1]]],
                            "lines": body.count("\n"), "chars": len(body), "body": body})
        return modules

    buf, buf_pages, first, last = [], [], None, None
    for n, body in zip(numbers, pages):
        block = ([MARKER.format(n=n)] + body.split("\n")) if markers else body.split("\n")
        for line in block:
            if len(buf) >= size:
                modules.append({"pages": [first, last], "lines": len(buf),
                                "chars": sum(len(x) + 1 for x in buf),
                                "body": "\n".join(buf) + "\n"})
                buf, first, last = [], None, None
            if not buf:
                first = n
            last = n
            buf.append(line)
    if buf:
        modules.append({"pages": [first, last], "lines": len(buf),
                        "chars": sum(len(x) + 1 for x in buf), "body": "\n".join(buf) + "\n"})
    return modules


def write_modules(modules: list[dict], outdir: str, stem: str, manifest: bool) -> list[dict]:
    os.makedirs(outdir, exist_ok=True)
    rows = []
    for i, m in enumerate(modules, 1):
        name = "%s.module-%04d.txt" % (stem, i)
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(m["body"])
        head = next((l.strip() for l in m["body"].splitlines() if l.strip() and not l.startswith("=====")), "")
        rows.append({"module": name, "start_page": m["pages"][0], "end_page": m["pages"][1],
                     "lines": m["lines"], "chars": m["chars"], "first_line": head[:80]})
    if manifest:
        with io.open(os.path.join(outdir, "manifest.json"), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(rows, fh, indent=2)
        with io.open(os.path.join(outdir, "manifest.md"), "w", encoding="utf-8", newline="\n") as fh:
            fh.write("| module | pages | lines | chars | first line |\n|---|---|---|---|---|\n")
            for r in rows:
                fh.write("| %s | %s-%s | %d | %d | %s |\n" % (r["module"], r["start_page"], r["end_page"],
                                                              r["lines"], r["chars"], r["first_line"]))
    return rows


# ------------------------------------------------------------------ report

def report(pdf: str, numbers: list[int], pages: list[str], engine: str) -> list[str]:
    lines = ["engine %s | pages selected %d | chars %d" % (engine, len(numbers), sum(len(p) for p in pages))]
    empty = [n for n, p in zip(numbers, pages) if len(p.strip()) < 2]
    if empty:
        shown = ",".join(str(x) for x in empty[:12])
        lines.append("EMPTY/TEXTLESS pages: %s%s - these need OCR (see reading.md), not more extraction"
                     % (shown, "..." if len(empty) > 12 else ""))
    thin = [n for n, p in zip(numbers, pages) if 2 <= len(p.strip()) < 60]
    if thin:
        lines.append("very short pages (%d): %s" % (len(thin), ",".join(str(x) for x in thin[:12])))
    repl = sum(p.count(REPL) for p in pages)
    if repl:
        lines.append("%d replacement characters - font/encoding damage; the text is partially unusable "
                     "where they cluster; consider the other engine or OCR" % repl)
    counts: dict[str, int] = {}
    for p in pages:
        for l in p.splitlines():
            s = l.strip()
            if 0 < len(s) <= 60:
                counts[s] = counts.get(s, 0) + 1
    chrome = sorted(((v, k) for k, v in counts.items() if v >= max(4, len(pages) // 3)), reverse=True)[:6]
    if chrome:
        lines.append("repeated lines (page furniture - use --clean): " +
                     "; ".join("%dx %r" % (v, k[:40]) for v, k in chrome))
    biggest = max(range(len(pages)), key=lambda i: len(pages[i]))
    lines.append("densest page: %d (%d chars)" % (numbers[biggest], len(pages[biggest])))
    return lines


# ------------------------------------------------------------------ main

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(prog="pdf_extract.py", add_help=True)
    ap.add_argument("pdf")
    ap.add_argument("--engine", default="auto", choices=["auto", "poppler", "pypdf"])
    ap.add_argument("--pages", default="")
    ap.add_argument("--layout", dest="layout", action="store_true", default=True)
    ap.add_argument("--no-layout", dest="layout", action="store_false")
    ap.add_argument("--markers", action="store_true")
    ap.add_argument("--clean", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--modules")
    ap.add_argument("--module-lines", type=int, default=200)
    ap.add_argument("--module-pages", type=int, default=0)
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--preview", type=int, default=0)
    ap.add_argument("--max-line", type=int, default=0)
    a = ap.parse_args(argv)

    if not os.path.exists(a.pdf):
        print("error: no such file: %s" % a.pdf)
        return 2
    if not (a.out or a.modules or a.report):
        print("error: nothing to do - pass --out, --modules, or --report")
        return 2

    engine = a.engine if a.engine != "auto" else ("poppler" if have_poppler() else "pypdf")
    total = 0
    try:
        if engine == "poppler":
            if not have_poppler():
                print("error: pdftotext not found on PATH; use --engine pypdf")
                return 2
            from_pypdf = None
            try:
                from pypdf import PdfReader
                total = len(PdfReader(a.pdf).pages)
            except Exception:
                total = 10 ** 6                       # trust poppler when pypdf cannot count
        else:
            from pypdf import PdfReader
            total = len(PdfReader(a.pdf).pages)
        numbers = parse_pages(a.pages, total)
    except ValueError as exc:
        print("error: %s" % exc)
        return 2
    except Exception as exc:                            # noqa: BLE001
        print("error: cannot open %s (%s) - if encrypted, decrypt first: qpdf --password=... --decrypt"
              % (a.pdf, exc))
        return 2

    try:
        pages = extract_poppler(a.pdf, numbers, a.layout) if engine == "poppler" else extract_pypdf(a.pdf, numbers)
    except subprocess.CalledProcessError as exc:
        print("error: pdftotext failed: %s" % (exc.stderr or "")[:300])
        return 2
    if a.clean:
        pages = clean_pages(pages)

    warn = 0
    if a.report:
        for line in report(a.pdf, numbers, pages, engine):
            print(line)
            if line.startswith(("EMPTY", "very short", "replacement")):
                warn = 1
    text = build_text(pages, numbers, a.markers, a.max_line)

    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        io.open(a.out, "w", encoding="utf-8", newline="\n").write(text)
        print("wrote %s (%d lines, %d chars)" % (a.out, text.count("\n"), len(text)))

    if a.modules:
        mode, size = ("pages", a.module_pages) if a.module_pages else ("lines", a.module_lines)
        mods = split_modules(text, numbers, pages, mode, size, a.markers)
        stem = os.path.splitext(os.path.basename(a.pdf))[0]
        rows = write_modules(mods, a.modules, stem, a.manifest)
        print("wrote %d module(s) to %s (%s per module)"
              % (len(rows), a.modules, ("%d pages" % size) if mode == "pages" else ("%d lines" % size)))
        for r in rows[:5]:
            print("  %s  pages %s-%s  %d lines  %s" % (r["module"], r["start_page"], r["end_page"],
                                                       r["lines"], r["first_line"][:50]))
        if len(rows) > 5:
            print("  ... %d more (see manifest.md)" % (len(rows) - 5))
        if a.manifest:
            print("  manifest: %s" % os.path.join(a.modules, "manifest.md"))

    if a.preview:
        body = [l for l in text.splitlines()][: a.preview]
        print("--- preview (first %d lines) ---" % len(body))
        for l in body:
            print(l[:200])
    return warn


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
