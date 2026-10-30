---
name: pdf
description: "Use this skill whenever the user wants to do anything with PDF files, in either of its two modes. READ mode: extract text from a PDF into .txt with scripts/pdf_extract.py - page ranges, layout vs raw engines, page markers, cleaning, a quality report (textless pages, font damage), and export as numbered module files (e.g. --module-lines 200) with a manifest, so long documents can be read selectively instead of dumped into context; also tables, images, OCR for scans, metadata, encrypted files. WRITE mode: create new PDFs, merge, split, rotate, watermark, fill and validate PDF forms, encrypt/decrypt, fix glyphs. If the user mentions a .pdf file - to read it, to search it, or to produce one - use this skill."
license: Proprietary. LICENSE.txt has complete terms
---

# PDF Processing Guide

## Overview

Two modes, and the second sentence of the request decides which one:

| Mode | For | Start with |
|---|---|---|
| **READ** | get content *out*: text, tables, page counts, metadata, searching a long document, OCR of scans | `scripts/pdf_extract.py`, then [`reading.md`](reading.md) |
| **WRITE** | put content *in*, or make a new PDF: create, merge, split, rotate, watermark, encrypt, fill forms | the library sections below, plus [`forms.md`](forms.md) for forms and [`reference.md`](reference.md) for advanced/troubleshooting |

## READ mode - extract to text, then module it

A PDF is not a text file, and reading one page-by-page through a viewer wastes context. Extract once, then
read the pieces you need.

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

Everything below creates or transforms PDFs.

## Quick Start (write)

```python
from pypdf import PdfReader, PdfWriter

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text (for programmatic use; prefer pdf_extract.py for reading a document)
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Basic Operations

#### Merge PDFs
```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### Split PDF
```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### Extract Metadata
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### Rotate Pages
```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # Rotate 90 degrees clockwise
writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables
```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### Advanced Table Extraction
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - Create PDFs

#### Basic PDF Creation
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# Add text
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# Add a line
c.line(100, height - 140, 400, height - 140)

# Save
c.save()
```

#### Create PDF with Multiple Pages
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Add content
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# Page 2
story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# Build PDF
doc.build(story)
```

#### Subscripts and Superscripts

**IMPORTANT**: Never use Unicode subscript/superscript characters (₀₁₂₃₄₅₆₇₈₉, ⁰¹²³⁴⁵⁶⁷⁸⁹) in ReportLab PDFs. The built-in fonts do not include these glyphs, causing them to render as solid black boxes.

Instead, use ReportLab's XML markup tags in Paragraph objects:
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# Subscripts: use <sub> tag
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# Superscripts: use <super> tag
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

For canvas-drawn text (not Paragraph objects), manually adjust font the size and position rather than using Unicode subscripts/superscripts.

## Command-Line Tools

### pdftotext (poppler-utils)
```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

### qpdf
```bash
# Merge PDFs
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# Split pages
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# Rotate pages
qpdf input.pdf output.pdf --rotate=+90:1  # Rotate page 1 by 90 degrees

# Remove password
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftk (if available)
```bash
# Merge
pdftk file1.pdf file2.pdf cat output merged.pdf

# Split
pdftk input.pdf burst

# Rotate
pdftk input.pdf rotate 1east output rotated.pdf
```

## Common Tasks

### Extract Text from Scanned PDFs
```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Add Watermark
```python
from pypdf import PdfReader, PdfWriter

# Create watermark (or load existing)
watermark = PdfReader("watermark.pdf").pages[0]

# Apply to all pages
reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Extract Images
```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

### Password Protection
```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Add password
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

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
| Fill PDF forms | pdf-lib or pypdf (see FORMS.md) | See FORMS.md |

## Next Steps

- **READ mode depth** - engine differences, tables, scanned/OCR, encrypted files, huge-document strategy, module conventions: [`reading.md`](reading.md)
- For advanced pypdfium2 usage, see REFERENCE.md
- For JavaScript libraries (pdf-lib), see REFERENCE.md
- If you need to fill out a PDF form, follow the instructions in FORMS.md
- For troubleshooting guides, see REFERENCE.md
