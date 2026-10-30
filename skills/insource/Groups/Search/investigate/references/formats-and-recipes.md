# Investigation & Search: Cross-Format Recipes & CLI Playbook

This reference provides illustrative recipes and dynamic patterns for investigating raw bytes, structured datasets, binary blobs, relational stores, and deeply nested hierarchies.

> **Instruction for Autonomous Agents**:
> These examples demonstrate format-specific parsing concepts. **Do not hardcode or copy these templates verbatim.** Always inspect the user's specific task, environment, available packages, and schema requirements, then dynamically construct or select the appropriate tooling, libraries, and script structure.

---

## 1. High-Performance Text & Code Traversal

When scanning thousands of code or log files:

### Grep / Ripgrep Optimization
```bash
# Case-insensitive recursive search, pruning noise
rg -i "pattern" --hidden -g '!.git' -g '!node_modules' -g '!obj' -g '!bin'

# Filter by extension and sort chronologically
rg -t py -t json "search_query" --sort path
```

### PowerShell High-Throughput Stream Search
```powershell
# Stream search without loading entire files into memory
Get-ChildItem -Path . -Recurse -File -Exclude *.dll,*.exe,*.iso |
    Select-String -Pattern "search_term" |
    Select-Object -First 25 Path, LineNumber, Line
```

---

## 2. Parquet & Columnar Data Inspection

Parquet files store data in columnar chunks with Thrift metadata footers.

### Python In-Memory Parquet Column / Schema Scan
```python
import pyarrow.parquet as pq

# Read metadata without reading row groups (instantaneous)
meta = pq.read_metadata("data.parquet")
print("Num rows:", meta.num_rows)
print("Num columns:", meta.num_columns)
print("Schema:", meta.schema)

# Read specific column without scanning whole table
table = pq.read_table("data.parquet", columns=["target_column"])
df = table.to_pandas()
matches = df[df["target_column"].str.contains("query", case=False, na=False)]
print(matches.head(10))
```

### DuckDB Fast Query (Zero-Setup SQL)
```bash
# Query parquet directly from CLI
duckdb -c "SELECT * FROM 'data.parquet' WHERE column_name LIKE '%term%' LIMIT 20;"
```

---

## 3. SQLite & Embedded Databases

### Dump Schema and Scan Tables
```bash
# List all tables and column schemas
sqlite3 database.db ".schema"

# Search across all tables dynamically
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
c = conn.cursor()
tables = [r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table'\")]
for t in tables:
    cols = [col[1] for col in c.execute(f\"PRAGMA table_info('{t}')\")]
    for row in c.execute(f\"SELECT * FROM '{t}' LIMIT 500\"):
        row_str = ' '.join(str(x) for x in row)
        if 'SEARCH_TERM' in row_str:
            print(f'Match in {t}: {row_str[:120]}')
"
```

---

## 4. Compressed Archives (ZIP, JAR, TAR, GZ)

### Stream Search Inside Archives (Without Disk Extraction)
```python
import zipfile, io

with zipfile.ZipFile("bundle.jar", "r") as z:
    for name in z.namelist():
        if name.endswith(('.json', '.xml', '.properties', '.txt', '.md')):
            with z.open(name) as f:
                for line in io.TextIOWrapper(f, encoding='utf-8', errors='ignore'):
                    if "target_string" in line:
                        print(f"{name}: {line.strip()}")
```

---

## 5. Documents & Ebooks (PDF, DOCX, EPUB)

When searching documents and ebooks, autonomous agents should dynamically detect and employ specialized libraries, with built-in zero-dependency fallbacks:

### PDF (pypdf, pdfplumber, PyMuPDF / fitz)
```python
# With pypdf (fastest pure Python)
import pypdf

reader = pypdf.PdfReader("document.pdf")
for page_num, page in enumerate(reader.pages):
    text = page.extract_text() or ""
    if "SEARCH_TERM" in text:
        print(f"Match on page {page_num + 1}")

# With PyMuPDF (fastest C-backed extraction)
import fitz

doc = fitz.open("document.pdf")
for page_num, page in enumerate(doc):
    if "SEARCH_TERM" in page.get_text():
        print(f"Match on page {page_num + 1}")
```

### Word Documents (.docx via python-docx or zero-dependency XML)
```python
# With python-docx
import docx

doc = docx.Document("document.docx")
for p in doc.paragraphs:
    if "SEARCH_TERM" in p.text:
        print("Paragraph match:", p.text[:120])

# Zero-dependency fallback (DOCX is a zip with word/document.xml)
import zipfile, xml.etree.ElementTree as ET

with zipfile.ZipFile("document.docx", "r") as z:
    xml_data = z.read("word/document.xml")
    root = ET.fromstring(xml_data)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    for p in root.iterfind(".//w:p", ns):
        text = "".join(t.text for t in p.iterfind(".//w:t", ns) if t.text)
        if "SEARCH_TERM" in text:
            print("XML Match:", text[:120])
```

### EPUB Ebooks (ebooklib or zero-dependency HTML parser)
```python
# With ebooklib
import ebooklib
from ebooklib import epub

book = epub.read_epub("book.epub")
for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
    content = item.get_content().decode("utf-8", errors="replace")
    if "SEARCH_TERM" in content:
        print(f"Match in chapter: {item.get_name()}")

# Zero-dependency fallback (EPUB is a zip holding XHTML chapters)
import zipfile, re

with zipfile.ZipFile("book.epub", "r") as z:
    for name in z.namelist():
        if name.lower().endswith((".html", ".xhtml", ".htm")):
            with z.open(name) as f:
                content = f.read().decode("utf-8", errors="replace")
                plain = re.sub(r"<[^>]+>", " ", content)
                if "SEARCH_TERM" in plain:
                    print(f"Match in {name}")
```

---

## 6. Raw Bytes, Hex, and Native Binaries

### Carve Printable Strings (ASCII + UTF-16LE)
```bash
# Extract ASCII and UTF-16 strings
strings -a -n 6 binary.dat | grep -i "pattern"
```

### Python Hex Chunk Scanner (Handles Gigabyte Blobs)
```python
import re

pattern = re.compile(rb"[\x20-\x7e]{5,}")
with open("blob.bin", "rb") as f:
    offset = 0
    while chunk := f.read(1024 * 1024):
        for m in pattern.finditer(chunk):
            s = m.group()
            if b"TargetTerm" in s:
                print(f"Match at 0x{offset + m.start():08X}: {s.decode('latin-1')}")
        offset += len(chunk)
```

---

## 6. High-Precision Tabular Output Pattern

Autonomous agents must format results cleanly so humans and parsers can immediately interpret match density:

```python
def print_ascii_table(headers, rows, max_widths=None):
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))
    if max_widths:
        col_widths = [min(w, mw) if mw else w for w, mw in zip(col_widths, max_widths)]
    
    border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    print(border)
    print("| " + " | ".join(str(h)[:w].ljust(w) for h, w in zip(headers, col_widths)) + " |")
    print(border)
    for row in rows:
        print("| " + " | ".join(str(c)[:w].ljust(w) for c, w in zip(row, col_widths)) + " |")
    print(border)
```
