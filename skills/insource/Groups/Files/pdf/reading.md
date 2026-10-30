# READ Mode - getting content out of a PDF

Reading a PDF well is a different job from reading a text file: the bytes carry *presentation*, not content
order, so the same page can extract three different ways depending on the engine and the mode. This file covers
choosing, verifying, and handling the cases where extraction lies.

All examples assume `scripts/pdf_extract.py` from this skill. It has no third-party dependency beyond
`pypdf` (or poppler's `pdftotext` on PATH), and its stdout is truncated so it never floods context.

---

## First: measure before you read

```bash
python scripts/pdf_extract.py document.pdf --report
```

Real output from a 40 MB, 145-page chat export, worth reading line by line:

```text
engine poppler | pages selected 145 | chars 125888
EMPTY/TEXTLESS pages: 97,99,100,101,102,105,106,108,109,110,111,116... - these need OCR (see reading.md), not more extraction
very short pages (12): 98,104,107,117,118,119,125,130,131,135,136,145
206 replacement characters - font/encoding damage; the text is partially unusable where they cluster; consider the other engine or OCR
densest page: 4 (1967 chars)
```

(That is the actual output for that file. Note what is *absent*: no "repeated lines" warning, because the most
frequent short line there appears 36 times and the furniture threshold was 48 - a low-noise document does not
need `--clean`, and the report says so by silence.)

What each line changes about the plan:

| Signal | Action |
|---|---|
| page count differs from what the user (or an attachment hint) said | **trust the tool.** Viewers and merge tools disagree; `pdftotext` and `pypdf` agreeing is strong evidence |
| textless pages | those pages are images; extraction will never yield text. OCR, or render-and-read ([`#scanned`](#scanned-and-image-only-pdfs)) |
| many very short pages | section dividers, or failed extraction - check one before concluding |
| replacement characters (`\ufffd`) | font/encoding damage; words are glued or lost. Try the other engine, or render the page |
| repeated lines | page furniture (headers/footers/running titles) - use `--clean` |
| densest page | budget: 2,000 chars/page ≈ 145 pages ≈ 126k chars, far too much to read at once → modules |

Structure too, before content:

```bash
python -c "from pypdf import PdfReader; r=PdfReader('document.pdf'); print(len(r.pages), r.metadata)"
python scripts/pdf_extract.py document.pdf --pages 1-3 --markers --preview 40
```

If the PDF has an outline (bookmarks), read it first - it is a free table of contents:

```python
from pypdf import PdfReader


def outline(reader, items=None, level=0, cap=60):
    """Print the bookmark tree with the page each entry lands on."""
    items = reader.outline if items is None else items
    for item in items:
        if isinstance(item, list):
            outline(reader, item, level + 1, cap)
        elif cap > 0:
            page = reader.get_destination_page_number(item) + 1
            print("  " * level + f"{item.title}  ->  p{page}")
            cap -= 1


r = PdfReader("document.pdf")
outline(r)
```

(An empty outline is normal for exported and generated PDFs - it does not mean the document is short.)

---

## Engines, and why they disagree

| Engine | Strength | Weakness | Availability |
|---|---|---|---|
| `pdftotext` (poppler) | fast on huge files, layout mode keeps columns, page breaks via form feed | older builds mangle spacing/kerning in web-exported PDFs; CLI-only | check `pdftotext -v` |
| `pypdf` | pure Python, page objects, metadata, outlines, form values | slower per page; reading order is content-stream order | `pip install pypdf` |
| `pdfplumber` | words/chars/lines/rects with coordinates - the right tool for tables and positional questions | heaviest install; slow on hundreds of pages | `pip install pdfplumber` |
| `pypdfium2` | fast, renders to images, good text ordering | less familiar API | see [`reference.md`](reference.md) |

`--engine auto` prefers poppler and falls back to pypdf. **When output looks wrong, re-run the same pages with
the other engine before believing either.** Concretely, on a ChatGPT-page export:

- layout mode produced readable sentences but glued some words together (`Soitis nota feat:`);
- raw mode kept the spaces but shattered reading order into fragments (`v`, `nm`, `8B Short Answer: It Depends`);
- both carried the same 206 replacement characters, because the damage is in the PDF's fonts, not the
  extractor.

The lesson generalizes: **layout mode is for prose and columns, raw mode is for one-column-per-line data, and
when both fail the document itself is the problem.**

---

## Module export - reading a long document without destroying context

```bash
python scripts/pdf_extract.py big.pdf --modules out/ --module-lines 200 --manifest --markers --clean
```

Produces `big.module-0001.txt` … `big.module-0022.txt` (that file: 22 modules), plus `manifest.md` /
`manifest.json` - the real first rows:

```text
| module              | pages | lines | chars | first line                                     |
| merged.module-0001.txt | 1-5  | 200   | 4498  | & Share                                        |
| merged.module-0002.txt | 5-10  | 200   | 4790  | git add file.py # after first feature          |
| merged.module-0003.txt | 10-14 | 200   | 5297  | If you say "this is too small to commit" …     |
```

How to work with it:

1. **Read the manifest, not the files.** It is the index: page ranges, sizes, and the first line of each
   module, which usually tells you the topic.
2. **Grep to locate**, then open one or two modules:
   ```bash
   grep -lin "retry policy" out/*.txt
   ```
3. **`--markers` is what makes citations honest.** Each module carries `===== [page N] =====` lines, so a
   quote can be traced to a page and re-rendered for verification.
4. **Choose the split mode by what you will do next:**
   - `--module-lines 200` — uniform size, best for feeding to an agent or chunked search. Budget by
     characters, not lines: that file's 200-line modules held 4.5k-5.4k characters each, while a wide terminal
     dump can hit 12k. Read `manifest.json`'s `chars` column before deciding the size.
   - `--module-pages 5` — page-aligned; boundaries never cut a page in half, which matters when you re-render
     a page to check it.
5. **Never** concatenate the whole extraction into one read. A 126k-character file costs more context than most
   questions are worth and hides the answer inside it.

Sizes: below ~30 pages, one `--out` file is fine. Above that, modules. If a module is empty, that page range is
image-only.

---

## Tables

pdfplumber is the tool for structured tables; text extraction flattens them into unreadable columns.

```python
import pdfplumber

with pdfplumber.open("report.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        for t in page.extract_tables():
            print(f"page {i + 1}: {len(t)} rows")
```

Tuning when it returns nothing or returns noise ([`reference.md`](reference.md) has the full settings list):

- ruled tables: default `vertical_strategy`/`horizontal_strategy = "lines"`.
- **gridless** tables (financial reports, no rules): `{"vertical_strategy": "text", "horizontal_strategy": "text"}`,
  or read words with coordinates and cluster by `x0` - the reliable way for aligned columns.
- merged/irregular cells: post-process rows; do not trust the first pass for a number you will act on.
- a table that spans a page break: check the next page for continuation rows before treating the row count as
  final.
- verify a table against the rendered page: `pdftoppm -f N -l N -r 200 -png report.pdf page` then read the PNG
  (or `scripts/convert_pdf_to_images.py report.pdf pages_out/` for the whole document).

---

## Scanned and image-only PDFs {#scanned}

Detection is mechanical: `--report` shows textless pages, or every page yields a few characters while the file
is large. A scanned PDF has no text layer; the page is a photograph.

OCR path:

```bash
python -c "import shutil; print(shutil.which('tesseract'))"   # availability first, always
```

```python
# requires: pip install pdf2image pytesseract  (and poppler + tesseract binaries)
import pytesseract
from pdf2image import convert_from_path

for i, image in enumerate(convert_from_path("scanned.pdf", dpi=300)):
    print(f"===== [page {i + 1}] =====")
    print(pytesseract.image_to_string(image))
```

Or produce a *searchable* PDF so the work is done once (`ocrmypdf input.pdf output.pdf`), which keeps the
images and adds the text layer underneath.

DPI matters: 300 is the practical floor for dense text; 150 is enough for large print. And OCR output is
prose-shaped noise - report the confidence problem to the user rather than presenting OCR'd numbers as fact.

**When the binaries are not installed** (common on Windows): say which ones are missing and stop. Rendering the
page to an image and *reading the image* is a legitimate fallback when you have vision, and is often better than
a bad OCR pass:

```bash
# one page only - the cheap path, needs poppler
pdftoppm -f 97 -l 97 -r 200 -png document.pdf page

# whole document to PNGs (this skill's script; renders every page, needs pdf2image + poppler)
python scripts/convert_pdf_to_images.py document.pdf pages_out/
```

Render the **specific** pages you need. A 145-page render is 145 images you did not ask for.

---

## Other content that is not body text

| Content | How |
|---|---|
| Images | `pdfimages -j in.pdf prefix`; check for images that are documents in themselves (scanned receipts) |
| Form field values (read) | `PdfReader(p).get_fields()` - acroform values; see [`forms.md`](forms.md) for filling |
| Annotations, comments, highlights | `page.annots` on the page object; note that comment text lives only there |
| Hyperlinks | `page.links` (URL per annotation) - **check these before quoting**, exported PDFs often carry tracking URLs |
| Embedded files | `reader.attachments` - real files inside the PDF; extract with care and treat as untrusted |
| Page labels | the printed page number often differs from the index (`pypdf`: `reader.page_labels`) - cite the printed one if the user reads it on-screen |
| Signatures/certification | presence changes handling; extraction of a signed document should not be presented as "the document" if validity matters |

---

## Garble triage

| Symptom | Cause | Fix |
|---|---|---|
| `Soitis nota feat:` (words glued) | kerning/toxa without space glyphs | other engine, or `--no-layout`; for critical text, render the page |
| `v`, `nm`, one-letter fragments | raw mode following the content stream | use `--layout` |
| `\ufffd` replacement chars | font subset without a Unicode map | other engine; if it persists, render + read the image |
| `ﬁ` ligature as one glyph | ligature encoding | normalize: `.replace("\ufb01", "fi")` etc. |
| reversed/jumbled letters | right-to-left text or an encoded custom font | language-aware handling; usually render |
| column text interleaved | multi-column layout read row-wise | `pdfplumber` with a `bbox` per column, or crop per column |
| footers inside sentences | page furniture | `--clean` |
| numbers wrong but text right | table flattened | extract as a table, or verify visually |

---

## Verification habits

- **Spot-check page 1, a middle page, and the last page** against the rendered image. A systematically wrong
  extractor looks exactly like a right one in the sample you happened to read.
- **Any number that matters** - money, dosage, legal deadline, statistic - is re-read from the page image or
  the table extraction, not from the flattened text.
- **Do not silently repair** garbled text while quoting. Either quote it as-is with the garble, or say what you
  believe was meant and mark it as your reading.
- **State the engine and mode** when reporting findings from a document you could not read cleanly
  ("poppler layout mode; 206 replacement chars; pages 97-116 are image-only and unread without OCR"). That is
  the difference between a finding and a guess.
- Extraction of someone else's PDF is a reading operation: keep the origin URL/path in your notes, and check
  the document's own license or confidentiality marking before redistributing what you extracted.
