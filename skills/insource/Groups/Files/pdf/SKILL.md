---
name: pdf
version: 1.1.1
author: Amr
specialized: pdf
description: "Use this skill whenever the user wants to do anything with PDF files, in either of its two modes. READ mode: extract text from a PDF into .txt with scripts/pdf_extract.py - page ranges, layout vs raw engines, page markers, cleaning, a quality report (textless pages, font damage), and export as numbered module files (e.g. --module-lines 200) with a manifest, so long documents can be read selectively instead of dumped into context; also tables, images, OCR for scans, metadata, encrypted files. WRITE mode: create new PDFs, merge, split, rotate, watermark, fill and validate PDF forms, encrypt/decrypt, fix glyphs. If the user mentions a .pdf file - to read it, to search it, or to produce one - use this skill."
license: Proprietary. LICENSE.txt has complete terms
argument-hint: "[read|write] <file or task> [options]"
---

# PDF Processing Guide

## Overview

Two modes, and the second sentence of the request decides which one:

| Mode | For | Start with |
|---|---|---|
| **READ** | get content *out*: text, tables, page counts, metadata, searching a long document, OCR of scans | `scripts/pdf_extract.py`, then [`reading.md`](reading.md) |
| **WRITE** | put content *in*, or make a new PDF: create, merge, split, rotate, watermark, encrypt, fill forms | [`write.md`](write.md) for the code cookbook, [`forms.md`](forms.md) for forms, [`reference.md`](reference.md) for advanced/troubleshooting |

## READ mode - extract to text, then module it

A PDF is not a text file, and reading one page-by-page through a viewer
wastes context. Extract once, then read the pieces you need.

```bash
# 1. Know what you are dealing with before reading anything
python scripts/pdf_extract.py document.pdf --report

# 2. Extract the whole thing to one text file
python scripts/pdf_extract.py document.pdf --out document.txt --markers --clean

# 3. Or export as modules - the usual move for a long document
python scripts/pdf_extract.py document.pdf --modules out/ --module-lines 200 --manifest --markers --clean

# 4. Targeted reads: only the pages in question
python scripts/pdf_extract.py document.pdf --pages 1-5,12 --out excerpt.txt
```

| Flag | Effect |
|---|---|
| `--engine auto\|poppler\|pypdf` | `auto` prefers `pdftotext` (poppler) and falls back to pypdf; they differ in line order, spacing and glyph fidelity - see [`reading.md`](reading.md) |
| `--layout` / `--no-layout` | poppler layout mode keeps columns; `--no-layout` (raw) follows the content stream |
| `--markers` | inserts `===== [page N] =====` so any quote can be cited back to a page - on by default in practice |
| `--clean` | drops repeated header/footer lines, collapses blank runs, rejoins hyphen-split words |
| `--modules DIR` + `--module-lines 200` | writes `STEM.module-0001.txt`, `…0002.txt`, each ~200 lines |
| `--module-pages 5` | page-aligned modules instead of line-count ones - uneven sizes, exact citations |
| `--manifest` | `manifest.md` + `manifest.json`: module → page range, lines, chars, first line |
| `--report` | page count, chars, textless pages (→ OCR), replacement-character count, repeated chrome lines, densest page |
| `--preview N` | print N lines of output so the first look costs almost no context |

Reading workflow, in order:

1. `--report` first. It tells you whether the document has a text layer at all; a page count of textless
   pages means OCR is the real job ([`reading.md`](reading.md#scanned-and-image-only-pdfs)).
2. Export modules with `--markers --clean --manifest`. Read the **manifest**, not the files.
3. Open only the module(s) the question points at; grep across the module directory when the location is
   unknown (`grep -lin "topic" out/*.txt`).
4. Quote with page numbers taken from the markers. If a module looks garbled, re-extract those pages with the
   other `--engine` before concluding the document is unreadable.
5. Never `cat` a whole extraction of a long PDF into context. 145 pages is roughly 125k characters.

Exit codes: `0` clean, `1` the report found quality problems worth reading, `2` usage or file or dependency
error. stdout is ASCII and truncated by design.

## WRITE mode

Everything that creates or transforms PDFs lives in [`write.md`](write.md)
— don't guess APIs from memory, open it and copy the worked pattern:

| Task | Recipe in write.md | Tool |
|---|---|---|
| Merge / split / rotate / metadata / encrypt | Quick recipes | pypdf |
| Create new PDFs (single page, multi-page report) | reportlab section | reportlab |
| Subscripts and superscripts (glyph-safety rule) | reportlab section | reportlab |
| Text and table extraction with layout | pdfplumber section | pdfplumber + pandas |
| OCR of scanned PDFs | Common tasks | pytesseract + pdf2image |
| Watermark, image extraction, CLI one-offs | Common tasks / tools | pypdf, pdfimages, qpdf, pdftk |

Two standing rules:

- **Forms** (fillable or annotation-filled) are their own workflow with
  validation scripts: follow [`forms.md`](forms.md).
- **Never ship `--allow-upscale`-style fudges quietly** — when the
  document resists (encrypted, textless, garbled), the fix paths are in
  [`reference.md`](reference.md); check it before improvising.

## Quick Reference

| Task | Best Tool | Command/Code |
|------|-----------|--------------|
| Read a document's text | this skill's script | `python scripts/pdf_extract.py IN.pdf --modules out/ --module-lines 200 --manifest` |
| Check whether pages have a text layer | same, report | `python scripts/pdf_extract.py IN.pdf --report` |
| Extract text (programmatic) | pypdf / pdfplumber | `page.extract_text()`, `page.extract_text(tables=True)` |
| Extract tables | pdfplumber | `page.extract_tables()` (see reading.md for gridless tables) |
| Extract images | pdfimages | `pdfimages -j input.pdf prefix` |
| Merge PDFs | pypdf | `writer.add_page(page)` |
| Split PDFs | pypdf | One page per file |
| Create PDFs | reportlab | Canvas or Platypus |
| Command line merge | qpdf | `qpdf --empty --pages ...` |
| OCR scanned PDFs | pytesseract | Convert to image first; see reading.md |
| Fill PDF forms | pdf-lib or pypdf | See [forms.md](forms.md) |

## Next Steps

- **READ mode depth** - engine differences, tables, scanned/OCR, encrypted files, huge-document strategy, module conventions: [`reading.md`](reading.md)
- **WRITE cookbook** - every create/transform recipe above in full code: [`write.md`](write.md)
- **Forms** - field inspection, filling, validation scripts, annotation fallback: [`forms.md`](forms.md)
- **Advanced & troubleshooting** - pypdfium2, pdf-lib (JavaScript), glyph fixes, OCR tuning: [`reference.md`](reference.md)
