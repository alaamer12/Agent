#!/usr/bin/env python3
"""
Universal Fast & Robust Investigation Search Utility
====================================================
Cross-platform, zero-dependency search engine designed for autonomous agents
and engineers investigating massive directory trees, heterogeneous file formats
(text, source code, binary/raw bytes, JSON/JSONL, Parquet metadata, ZIP/JAR/TAR
archives, SQLite schemas/tables), applying smart contextual filters, regex/literal
matching, and outputting structured tabular reports.

Usage:
  python search.py --path <dir_or_file> --term <str_or_regex> [options]
"""

import os
import sys
import re
import io
import json
import zipfile
import tarfile
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows terminal without crashes
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if sys.stderr.encoding != "utf-8":
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Common binary / metadata signatures
MAGIC_PARQUET = b"PAR1"
MAGIC_SQLITE = b"SQLite format 3\x00"
MAGIC_ZIP = b"PK\x03\x04"
MAGIC_GZIP = b"\x1f\x8b"
MAGIC_TAR_USTAR = b"ustar"
MAGIC_ELF = b"\x7fELF"
MAGIC_PE = b"MZ"
MAGIC_CLASS = b"\xca\xfe\xba\xbe"
MAGIC_PDF = b"%PDF"

# Memory protection constants
READ_CHUNK_SIZE = 128 * 1024       # 128 KB buffer chunks
MAX_LINE_SCAN_LEN = 16 * 1024      # 16 KB max characters evaluated per line to avoid regex blowout


def clean_line_snippet(text, max_len=120):
    """Normalize internal newlines, control characters, and collapse spaces."""
    cleaned = re.sub(r"[\r\n\t\x00-\x1f]+", " ", str(text)).strip()
    if len(cleaned) > max_len:
        return cleaned[: max_len - 3] + "..."
    return cleaned


def iter_file_lines_chunked(file_path, chunk_size=READ_CHUNK_SIZE, max_line_len=MAX_LINE_SCAN_LEN):
    """
    Zero-memory-peak line generator for large text or JSONL files.
    Streams binary chunks and yields lines capped at max_line_len without
    accumulating entire files or massive strings into memory.
    """
    try:
        with open(file_path, "rb") as f:
            carry = b""
            line_no = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    if carry:
                        line_no += 1
                        line = carry.decode("utf-8", errors="replace")
                        yield line_no, line[:max_line_len]
                    break

                data = carry + chunk
                lines = data.split(b"\n")
                carry = lines.pop()

                for raw_line in lines:
                    line_no += 1
                    if raw_line.endswith(b"\r"):
                        raw_line = raw_line[:-1]
                    if len(raw_line) > max_line_len:
                        line = raw_line[:max_line_len].decode("utf-8", errors="replace")
                    else:
                        line = raw_line.decode("utf-8", errors="replace")
                    yield line_no, line
    except Exception:
        return


def format_table(headers, rows, max_col_widths=None):
    """
    Render clean, robust ASCII tables with dynamic column widths,
    clean truncation, and proper alignment.
    """
    if not rows:
        return "No matching records found."

    num_cols = len(headers)
    col_widths = [len(h) for h in headers]

    for row in rows:
        for idx in range(num_cols):
            cell_str = str(row[idx]) if idx < len(row) else ""
            col_widths[idx] = max(col_widths[idx], len(cell_str))

    if max_col_widths:
        for idx, mw in enumerate(max_col_widths):
            if mw is not None and col_widths[idx] > mw:
                col_widths[idx] = mw

    def truncate_cell(val, w):
        s = clean_line_snippet(str(val), max_len=w)
        return s

    sep_border = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "| " + " | ".join(truncate_cell(headers[i], col_widths[i]).ljust(col_widths[i]) for i in range(num_cols)) + " |"

    lines = [sep_border, header_row, sep_border]
    for row in rows:
        cells = []
        for i in range(num_cols):
            val = row[i] if i < len(row) else ""
            w = col_widths[i]
            truncated = truncate_cell(val, w)
            if isinstance(val, int) or (isinstance(val, str) and val.isdigit()):
                cells.append(truncated.rjust(w))
            else:
                cells.append(truncated.ljust(w))
        lines.append("| " + " | ".join(cells) + " |")
    lines.append(sep_border)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Format Search Handlers
# ---------------------------------------------------------------------------

def search_text_stream(stream, pattern, max_matches=50, max_snippets=3):
    """Search line-by-line in a decoded text stream."""
    count = 0
    snippets = []
    line_no = 0
    for line in stream:
        line_no += 1
        if pattern.search(line):
            count += 1
            if len(snippets) < max_snippets:
                snippets.append(f"L{line_no}: {clean_line_snippet(line)}")
            if count >= max_matches:
                break
    return count, snippets


def search_plain_file(file_path, pattern, max_matches=50, max_snippets=3):
    """
    Search regular text and JSONL files using chunked streaming line iteration.
    Prevents memory peaks on large files by reading binary blocks of 128KB and
    capping line buffer lengths.
    """
    count = 0
    snippets = []
    for line_no, line in iter_file_lines_chunked(file_path):
        if pattern.search(line):
            count += 1
            if len(snippets) < max_snippets:
                snippets.append(f"L{line_no}: {clean_line_snippet(line)}")
            if count >= max_matches:
                break
    return count, snippets


def search_binary_file(file_path, pattern, byte_pattern=None, max_matches=50, max_snippets=3, chunk_size=256 * 1024):
    """
    Robust binary search scanning printable chunks + decoded strings.
    Handles raw bytes, executables, compiled bytecode, and unknown blobs.
    """
    count = 0
    snippets = []
    try:
        with open(file_path, "rb") as f:
            offset = 0
            carryover = b""
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                data = carryover + chunk
                # Extract printable ASCII/UTF-8 strings of min length 4
                ascii_strings = re.findall(rb"[\x20-\x7e]{4,}", data)
                for s in ascii_strings:
                    try:
                        text = s.decode("utf-8", errors="ignore")
                        if pattern.search(text):
                            count += 1
                            if len(snippets) < max_snippets:
                                snippets.append(f"0x{offset:X}: {clean_line_snippet(text)}")
                            if count >= max_matches:
                                return count, snippets
                    except Exception:
                        pass

                # If byte pattern provided or regex applies on latin-1
                if byte_pattern:
                    for m in byte_pattern.finditer(data):
                        count += 1
                        if len(snippets) < max_snippets:
                            snippets.append(f"byte 0x{offset + m.start():X}")
                        if count >= max_matches:
                            return count, snippets

                carryover = data[-512:] if len(data) >= 512 else data
                offset += len(chunk)
    except Exception:
        pass
    return count, snippets


def search_parquet_file(file_path, pattern, max_matches=50, max_snippets=3):
    """
    Inspect Parquet files:
    First attempts using pyarrow/fastparquet/polars/duckdb if installed.
    Falls back to binary Thrift metadata & dictionary string extraction.
    """
    # 1. Try pyarrow
    try:
        import pyarrow.parquet as pq
        table = pq.read_table(file_path)
        # Search column names
        count = 0
        snippets = []
        for col_name in table.column_names:
            if pattern.search(col_name):
                count += 1
                snippets.append(f"ColName: {col_name}")
        # Search text columns (sample first 1000 rows for speed)
        df_sample = table.slice(0, 1000).to_pandas()
        for col in df_sample.select_dtypes(include=["object", "string", "category"]).columns:
            matches = df_sample[col].astype(str).str.contains(pattern.pattern, regex=True, na=False)
            m_count = matches.sum()
            if m_count > 0:
                count += int(m_count)
                for val in df_sample[col][matches].head(max_snippets - len(snippets)):
                    snippets.append(f"{col}: {clean_line_snippet(str(val))}")
        if count > 0:
            return count, snippets
    except Exception:
        pass

    # 2. Fast zero-dependency fallback: Parquet metadata / dictionary string scanning
    return search_binary_file(file_path, pattern, max_matches=max_matches, max_snippets=max_snippets)


def search_sqlite_file(file_path, pattern, max_matches=50, max_snippets=3):
    """Search SQLite database schemas and textual table entries."""
    count = 0
    snippets = []
    try:
        conn = sqlite3.connect(f"file:{os.path.abspath(file_path)}?mode=ro", uri=True)
        cursor = conn.cursor()
        
        # 1. Search schema / table names
        cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE sql IS NOT NULL")
        tables = []
        for row in cursor.fetchall():
            obj_type, name, sql = row
            if pattern.search(name) or pattern.search(sql):
                count += 1
                if len(snippets) < max_snippets:
                    snippets.append(f"Schema {obj_type} '{name}': {clean_line_snippet(sql)}")
            if obj_type == "table" and not name.startswith("sqlite_"):
                tables.append(name)

        # 2. Search rows in text/varchar columns (sample first 500 rows per table)
        for tbl in tables[:15]:
            try:
                cursor.execute(f"PRAGMA table_info('{tbl}')")
                cols = [c[1] for c in cursor.fetchall()]
                cursor.execute(f"SELECT * FROM '{tbl}' LIMIT 500")
                for r in cursor.fetchall():
                    row_str = " | ".join(str(item) for item in r if item is not None)
                    if pattern.search(row_str):
                        count += 1
                        if len(snippets) < max_snippets:
                            snippets.append(f"Table '{tbl}': {clean_line_snippet(row_str)}")
                        if count >= max_matches:
                            conn.close()
                            return count, snippets
            except Exception:
                continue
        conn.close()
    except Exception:
        # Fallback to binary search if sqlite driver fails or file is locked
        return search_binary_file(file_path, pattern, max_matches=max_matches, max_snippets=max_snippets)
    return count, snippets


def search_zip_archive(file_path, pattern, max_matches=50, max_snippets=3):
    """Search file names and internal text contents of ZIP / JAR / APK / WHEEL."""
    count = 0
    snippets = []
    try:
        with zipfile.ZipFile(file_path, "r") as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                # Search filename
                if pattern.search(info.filename):
                    count += 1
                    if len(snippets) < max_snippets:
                        snippets.append(f"ZipEntry: {info.filename}")

                # Search internal file if within safe size (< 10MB)
                if info.file_size < 10 * 1024 * 1024:
                    ext = os.path.splitext(info.filename)[1].lower()
                    if ext in [".txt", ".md", ".json", ".xml", ".yaml", ".yml", ".py", ".cs", ".java", ".kt", ".js", ".ts", ".html", ".css", ".csv", ".log"]:
                        try:
                            with z.open(info) as internal_f:
                                wrapper = io.TextIOWrapper(internal_f, encoding="utf-8", errors="replace")
                                in_count, in_snips = search_text_stream(wrapper, pattern, max_matches=10, max_snippets=1)
                                if in_count > 0:
                                    count += in_count
                                    for s in in_snips:
                                        if len(snippets) < max_snippets:
                                            snippets.append(f"{info.filename} -> {s}")
                        except Exception:
                            pass
                if count >= max_matches:
                    break
    except Exception:
        pass
    return count, snippets


def search_tar_archive(file_path, pattern, max_matches=50, max_snippets=3):
    """Search file names and internal contents of TAR archives (tar, tar.gz, tgz)."""
    count = 0
    snippets = []
    try:
        mode = "r:*"
        with tarfile.open(file_path, mode) as t:
            for member in t.getmembers():
                if pattern.search(member.name):
                    count += 1
                    if len(snippets) < max_snippets:
                        snippets.append(f"TarEntry: {member.name}")
                if member.isfile() and member.size < 5 * 1024 * 1024:
                    ext = os.path.splitext(member.name)[1].lower()
                    if ext in [".txt", ".md", ".json", ".xml", ".yaml", ".yml", ".py", ".cs", ".java", ".kt", ".js", ".ts", ".html", ".log"]:
                        try:
                            f = t.extractfile(member)
                            if f:
                                wrapper = io.TextIOWrapper(f, encoding="utf-8", errors="replace")
                                in_count, in_snips = search_text_stream(wrapper, pattern, max_matches=10, max_snippets=1)
                                if in_count > 0:
                                    count += in_count
                                    for s in in_snips:
                                        if len(snippets) < max_snippets:
                                            snippets.append(f"{member.name} -> {s}")
                        except Exception:
                            pass
                if count >= max_matches:
                    break
    except Exception:
        pass
    return count, snippets


def search_pdf_file(file_path, pattern, max_matches=50, max_snippets=3):
    """
    Search PDF files.
    First attempts pypdf / pdfplumber / fitz (PyMuPDF) if installed.
    Falls back to binary stream scanning for extracted stream text and literal matches.
    """
    # 1. Try pypdf
    try:
        import pypdf
        reader = pypdf.PdfReader(file_path)
        count = 0
        snippets = []
        for page_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            for line in text.splitlines():
                if pattern.search(line):
                    count += 1
                    if len(snippets) < max_snippets:
                        snippets.append(f"Page {page_idx + 1}: {clean_line_snippet(line)}")
                    if count >= max_matches:
                        return count, snippets
        if count > 0:
            return count, snippets
    except Exception:
        pass

    # 2. Try fitz (PyMuPDF)
    try:
        import fitz
        doc = fitz.open(file_path)
        count = 0
        snippets = []
        for page_idx, page in enumerate(doc):
            text = page.get_text()
            for line in text.splitlines():
                if pattern.search(line):
                    count += 1
                    if len(snippets) < max_snippets:
                        snippets.append(f"Page {page_idx + 1}: {clean_line_snippet(line)}")
                    if count >= max_matches:
                        return count, snippets
        if count > 0:
            return count, snippets
    except Exception:
        pass

    # 3. Fallback: binary scanning for text strings in uncompressed streams
    return search_binary_file(file_path, pattern, max_matches=max_matches, max_snippets=max_snippets)


def search_docx_file(file_path, pattern, max_matches=50, max_snippets=3):
    """
    Search Word (.docx) files.
    First attempts python-docx if installed.
    Falls back to inspecting word/document.xml inside the zip package without external dependencies.
    """
    # 1. Try python-docx
    try:
        import docx
        doc = docx.Document(file_path)
        count = 0
        snippets = []
        for p in doc.paragraphs:
            if pattern.search(p.text):
                count += 1
                if len(snippets) < max_snippets:
                    snippets.append(f"Paragraph: {clean_line_snippet(p.text)}")
                if count >= max_matches:
                    return count, snippets
        for table in doc.tables:
            for row in table.rows:
                row_str = " | ".join(c.text.strip() for c in row.cells)
                if pattern.search(row_str):
                    count += 1
                    if len(snippets) < max_snippets:
                        snippets.append(f"DocxTable: {clean_line_snippet(row_str)}")
                    if count >= max_matches:
                        return count, snippets
        if count > 0:
            return count, snippets
    except Exception:
        pass

    # 2. Zero-dependency fallback: DOCX is a ZIP container holding word/document.xml
    try:
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(file_path, "r") as z:
            if "word/document.xml" in z.namelist():
                xml_content = z.read("word/document.xml")
                root = ET.fromstring(xml_content)
                # Word XML namespaces
                ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                count = 0
                snippets = []
                for p in root.iterfind(".//w:p", ns):
                    texts = [t.text for t in p.iterfind(".//w:t", ns) if t.text]
                    full_p = "".join(texts)
                    if pattern.search(full_p):
                        count += 1
                        if len(snippets) < max_snippets:
                            snippets.append(f"Paragraph: {clean_line_snippet(full_p)}")
                        if count >= max_matches:
                            return count, snippets
                if count > 0:
                    return count, snippets
    except Exception:
        pass

    return search_zip_archive(file_path, pattern, max_matches=max_matches, max_snippets=max_snippets)


def search_epub_file(file_path, pattern, max_matches=50, max_snippets=3):
    """
    Search EPUB ebook files.
    First attempts ebooklib if installed.
    Falls back to inspecting internal HTML/XHTML chapters inside the zip package without external dependencies.
    """
    # 1. Try ebooklib
    try:
        import ebooklib
        from ebooklib import epub
        from html.parser import HTMLParser

        class HTMLTextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.lines = []
            def handle_data(self, data):
                s = data.strip()
                if s:
                    self.lines.append(s)

        book = epub.read_epub(file_path)
        count = 0
        snippets = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                extractor = HTMLTextExtractor()
                extractor.feed(item.get_content().decode("utf-8", errors="replace"))
                for line in extractor.lines:
                    if pattern.search(line):
                        count += 1
                        if len(snippets) < max_snippets:
                            snippets.append(f"{item.get_name()}: {clean_line_snippet(line)}")
                        if count >= max_matches:
                            return count, snippets
        if count > 0:
            return count, snippets
    except Exception:
        pass

    # 2. Zero-dependency fallback: EPUB is a ZIP container holding XHTML/HTML chapters
    try:
        count = 0
        snippets = []
        with zipfile.ZipFile(file_path, "r") as z:
            for name in z.namelist():
                lower_name = name.lower()
                if lower_name.endswith((".html", ".xhtml", ".htm", ".xml", ".txt")):
                    with z.open(name) as f:
                        for line in io.TextIOWrapper(f, encoding="utf-8", errors="replace"):
                            # Simple tag strip
                            clean_text = re.sub(r"<[^>]+>", " ", line)
                            if pattern.search(clean_text):
                                count += 1
                                if len(snippets) < max_snippets:
                                    snippets.append(f"{name}: {clean_line_snippet(clean_text)}")
                                if count >= max_matches:
                                    return count, snippets
        if count > 0:
            return count, snippets
    except Exception:
        pass

    return search_zip_archive(file_path, pattern, max_matches=max_matches, max_snippets=max_snippets)


def detect_and_dispatch(file_path, pattern, byte_pattern=None, max_matches=50, max_snippets=3):
    """
    Intelligently detect file format (by magic bytes + extension)
    and dispatch to specialized handler.
    """
    ext = os.path.splitext(file_path)[1].lower()

    # Read leading 64 bytes for magic header identification
    magic = b""
    try:
        with open(file_path, "rb") as f:
            magic = f.read(64)
    except Exception:
        return 0, []

    # Format dispatching
    if magic.startswith(MAGIC_PDF) or ext == ".pdf":
        return search_pdf_file(file_path, pattern, max_matches, max_snippets)

    if ext == ".docx":
        return search_docx_file(file_path, pattern, max_matches, max_snippets)

    if ext == ".epub":
        return search_epub_file(file_path, pattern, max_matches, max_snippets)

    if magic.startswith(MAGIC_SQLITE) or ext in [".sqlite", ".sqlite3", ".db"]:
        return search_sqlite_file(file_path, pattern, max_matches, max_snippets)

    if magic.startswith(MAGIC_PARQUET) or ext in [".parquet", ".pq"]:
        return search_parquet_file(file_path, pattern, max_matches, max_snippets)

    if magic.startswith(MAGIC_ZIP) or ext in [".zip", ".jar", ".war", ".apk", ".whl", ".nupkg"]:
        return search_zip_archive(file_path, pattern, max_matches, max_snippets)

    if ext in [".tar", ".tar.gz", ".tgz", ".tar.bz2"] or MAGIC_TAR_USTAR in magic:
        return search_tar_archive(file_path, pattern, max_matches, max_snippets)

    # Check if predominantly binary
    if b"\x00" in magic[:32] or ext in [".exe", ".dll", ".so", ".dylib", ".bin", ".dat", ".class", ".pyc"]:
        return search_binary_file(file_path, pattern, byte_pattern, max_matches, max_snippets)

    # Default to resilient plain-text stream
    return search_plain_file(file_path, pattern, max_matches, max_snippets)


# ---------------------------------------------------------------------------
# CLI & Traversal Engine
# ---------------------------------------------------------------------------

def optimize_regex_term(term):
    """
    Optimize regex patterns for unanchored line-by-line searches.
    Leading unanchored `.*` or `.*?` causes catastrophic quadratic backtracking in Python's
    regex engine when scanning long non-matching lines. Stripping it preserves identical
    search semantics in re.search() while avoiding severe CPU lockups.
    """
    pattern_str = term
    if not pattern_str.startswith(("^", r"\A")):
        if pattern_str.startswith(".*?") and len(pattern_str) > 3:
            pattern_str = pattern_str[3:]
        elif pattern_str.startswith(".*") and len(pattern_str) > 2:
            pattern_str = pattern_str[2:]
    return pattern_str


def main():
    parser = argparse.ArgumentParser(
        description="Universal Fast & Robust Investigation Search Utility for Autonomous Agents & Engineers."
    )
    parser.add_argument("--path", "-p", default=".", help="Root directory or file to search (default: current directory)")
    parser.add_argument("--term", "-t", required=True, help="Search term or expression")
    parser.add_argument("--regex", "-r", action="store_true", help="Treat --term as a regular expression")
    parser.add_argument("--case-sensitive", "-c", action="store_true", help="Case-sensitive search")
    parser.add_argument("--ignore-case", "-i", "--case-insensitive", action="store_true", help="Case-insensitive search (default)")
    parser.add_argument("--filter-path", "-f", help="Substring or pattern to filter file paths (e.g. project name, directory)")
    parser.add_argument("--ext", help="Comma-separated file extensions to include (e.g. .py,.json,.parquet)")
    parser.add_argument("--max-size-mb", type=float, default=100.0, help="Skip files larger than this size in MB (default: 100MB)")
    parser.add_argument("--sort", choices=["name", "date", "size", "matches"], default="matches", help="Sort order of results")
    parser.add_argument("--reverse", action="store_true", help="Reverse sort order (e.g. oldest first when sorted by date)")
    parser.add_argument("--limit", "-n", type=int, default=50, help="Maximum number of matched files to display (default: 50)")
    parser.add_argument("--snippets", "-s", action="store_true", default=True, help="Display context snippets beneath table")
    parser.add_argument("--no-snippets", action="store_false", dest="snippets", help="Omit context snippets")
    parser.add_argument("--json", action="store_true", help="Output raw JSON instead of ASCII table")

    args = parser.parse_args()

    target_path = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.exists(target_path):
        print(f"Error: Path does not exist: {target_path}", file=sys.stderr)
        sys.exit(1)

    # Compile regex pattern
    is_case_sensitive = args.case_sensitive and not args.ignore_case
    re_flags = 0 if is_case_sensitive else re.IGNORECASE
    try:
        if args.regex:
            opt_regex_term = optimize_regex_term(args.term)
            pattern = re.compile(opt_regex_term, re_flags)
        else:
            pattern = re.compile(re.escape(args.term), re_flags)
    except re.error as e:
        print(f"Error compiling regex '{args.term}': {e}", file=sys.stderr)
        sys.exit(1)

    # Compile byte pattern for raw byte scans if literal
    byte_pattern = None
    if not args.regex:
        byte_pattern = re.compile(re.escape(args.term.encode("utf-8")), re_flags)

    # Allowed extensions
    allowed_exts = None
    if args.ext:
        allowed_exts = {e.strip().lower() if e.strip().startswith(".") else f".{e.strip().lower()}" for e in args.ext.split(",")}

    max_bytes = int(args.max_size_mb * 1024 * 1024)

    # File discovery generator
    def scan_files():
        if os.path.isfile(target_path):
            yield target_path
            return

        for root, dirs, files in os.walk(target_path):
            # Prune noisy dependency / cache dirs to maximize search throughput
            dirs[:] = [d for d in dirs if d not in {".git", ".svn", ".hg", "node_modules", "__pycache__", ".tox", ".mypy_cache", ".pytest_cache"}]
            for fname in files:
                fpath = os.path.join(root, fname)
                yield fpath

    results = []
    scanned_count = 0

    for fpath in scan_files():
        scanned_count += 1

        # Apply path filter (e.g., project name)
        if args.filter_path:
            if args.filter_path.lower() not in fpath.lower():
                continue

        # Extension filter
        if allowed_exts:
            ext = os.path.splitext(fpath)[1].lower()
            if ext not in allowed_exts:
                continue

        # Size check
        try:
            st = os.stat(fpath)
            if st.st_size > max_bytes:
                continue
            mtime = datetime.fromtimestamp(st.st_mtime)
            size_kb = st.st_size / 1024.0
        except Exception:
            continue

        # Search the file
        count, snippets = detect_and_dispatch(fpath, pattern, byte_pattern=byte_pattern, max_matches=50, max_snippets=3)
        if count > 0:
            rel_path = os.path.relpath(fpath, target_path) if os.path.isdir(target_path) else os.path.basename(fpath)
            results.append({
                "path": fpath,
                "display_path": rel_path,
                "matches": count,
                "size_kb": round(size_kb, 1),
                "mtime": mtime,
                "date_str": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                "snippets": snippets
            })

    # Sorting
    if args.sort == "matches":
        results.sort(key=lambda x: x["matches"], reverse=not args.reverse)
    elif args.sort == "date":
        results.sort(key=lambda x: x["mtime"], reverse=not args.reverse)
    elif args.sort == "size":
        results.sort(key=lambda x: x["size_kb"], reverse=not args.reverse)
    elif args.sort == "name":
        results.sort(key=lambda x: x["display_path"].lower(), reverse=args.reverse)

    total_matches = len(results)
    if args.limit and args.limit > 0:
        display_results = results[: args.limit]
    else:
        display_results = results

    # JSON Output mode
    if args.json:
        out_data = {
            "query": args.term,
            "regex": args.regex,
            "path": target_path,
            "filter_path": args.filter_path,
            "scanned_files": scanned_count,
            "matched_files": total_matches,
            "results": [
                {
                    "path": r["path"],
                    "matches": r["matches"],
                    "size_kb": r["size_kb"],
                    "date": r["date_str"],
                    "snippets": r["snippets"]
                }
                for r in display_results
            ]
        }
        print(json.dumps(out_data, indent=2))
        return

    # Print summary header
    case_display = "Sensitive" if is_case_sensitive else "Insensitive"
    filter_msg = f" | Path filter: '{args.filter_path}'" if args.filter_path else ""
    ext_msg = f" | Ext: '{args.ext}'" if args.ext else ""
    print(f"\n[Universal Investigation Search]")
    print(f"Target: {target_path} | Term: '{args.term}' | Regex: {args.regex} | Case: {case_display}{filter_msg}{ext_msg}")
    print(f"Scanned files: {scanned_count} | Matching files: {total_matches} (showing top {len(display_results)})\n")

    # Render tabular output
    headers = ["#", "Date & Time", "Matches", "Size (KB)", "File Path"]
    rows = []
    for idx, r in enumerate(display_results, 1):
        rows.append([
            idx,
            r["date_str"],
            r["matches"],
            f"{r['size_kb']:,.1f}",
            r["display_path"]
        ])

    table_str = format_table(headers, rows, max_col_widths=[4, 19, 8, 12, 75])
    print(table_str)

    # Print context snippets if requested
    if args.snippets and display_results:
        print("\n--- Context Snippets ---")
        for idx, r in enumerate(display_results, 1):
            print(f"\n[{idx}] {r['display_path']} ({r['matches']} match(es), {r['date_str']}):")
            for snip in r["snippets"]:
                print(f"    * {snip}")


if __name__ == "__main__":
    main()
