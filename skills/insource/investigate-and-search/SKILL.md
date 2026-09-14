---
name: investigate-and-search
description: Universal, robust, and high-precision investigation and search methodology across heterogeneous file formats (plain text, massive source trees, binary blobs, raw bytes, Parquet, SQLite, archives ZIP/TAR/JAR, JSON/JSONL). Use when searching through thousands of files, diagnosing unfamiliar architectures, extracting needles from complex data stores, or synthesizing findings into structured tabular reports with reusable search scripts.
---

# Universal Investigation & Search Skill

A comprehensive methodology and executable toolkit for autonomous agents and engineers conducting high-stakes investigations across complex file systems, massive datasets, and diverse data formats. It guarantees **robustness and precision** (never missing subtle needles or edge cases) combined with **high throughput** (leveraging smart pruning, early filtering, streaming I/O, and zero-dependency dispatching).

---

## When to Use This Skill

- Searching across thousands or millions of files without overflowing memory or timing out.
- Investigating heterogeneous or unfamiliar data formats: binary executables, raw byte buffers, Parquet datasets, SQLite databases, JSONL event logs, or compressed archives (`.zip`, `.jar`, `.apk`, `.tar.gz`).
- Diagnosing complex problems where initial queries must adapt based on emerging contextual clues (e.g. cross-referencing metadata to infer project scopes, sessions, or timestamps).
- Formulating robust multi-pass search strategies: coarse triage -> scoped contextual filtering -> deep dissection -> verified extraction.
- Consolidating manual, exploratory terminal one-liners into a clean, reusable CLI search script featuring structured ASCII tabular output, regex/literal options, sorting, and context snippet extraction.

---

## Core Investigation Principles

### 1. Robustness & Precision First
- **Never guess format by extension alone**: Verify magic bytes (e.g., `PAR1` for Parquet, `SQLite format 3`, `PK\x03\x04` for ZIP, `\x7fELF`/`MZ` for native binaries).
- **Encoding resilience**: Always fallback across encodings (`UTF-8` -> `Latin-1` -> `Raw Bytes`) rather than crashing or dropping files silently.
- **Normalize and trim**: Strip non-printable control characters, collapse multi-line spans, and remove trailing whitespace to ensure clean snippet matching.

### 2. High-Throughput & Smart Pruning
- **Directory noise elimination**: Instantly prune dependency caches and VCS metadata (`.git`, `node_modules`, `obj`, `bin`, `__pycache__`, `.tox`).
- **Implicit Contextual Filtering**: Infer boundary criteria from the problem domain (e.g., restricting searches to specific projects, timestamps, user sessions, or module paths) to reduce candidate spaces by orders of magnitude.
- **Streaming over Buffering**: Use generators and stream iterators line-by-line or chunk-by-chunk to analyze gigabyte-scale logs without out-of-memory errors.

### 3. Iteration to Automation (The 2-Phase Lifecycle)
- **Phase 1: Exploratory Triage**: Run targeted inline probes, inspect file signatures, sample entries, and uncover the real metadata schema.
- **Phase 2: Formalized Tooling**: Codify the successful investigative workflow into a clean CLI script that provides customizable flags (`--path`, `--term`, `--regex`, `--sort`, `--filter-path`, `--limit`) and formats output in human-readable ASCII tables.

---

## Dynamic Adaptation: Task-Driven Library and Tool Selection

**Autonomous Agent Directive: Never hardcode libraries, tools, or rigid code templates.**
An agent must analyze each task contextually and adapt its approach dynamically:

1. **Assess System Environment & Available Tooling**:
   - Inspect what CLI tools, system packages, and Python libraries are already installed or available in the environment (e.g. via `discover_tools`, checking imports, or CLI `--version`).
   - If an optimal library is present (e.g., `duckdb`, `pyarrow`, `fitz` / `PyMuPDF`, `pypdf`, `python-docx`, `ebooklib`, `pandas`, `sqlite3`), dynamically import and leverage it for maximum throughput and fidelity.
   - If a library is missing, evaluate whether installing it or synthesizing a specialized zero-dependency fallback (e.g., standard library `zipfile`, `xml.etree.ElementTree`, `struct`, raw byte chunking) best fits the task constraints.

2. **Tailor the Search Strategy to Data Formats & Task Intent**:
   - Match the tool to the specific artifact: e.g., SQL engine for relational stores, streaming XML/HTML parsers for document packages, vectorized readers for tabular columnar data, memory-mapped byte iterators for binary dumps.
   - Do not force every problem into a single pre-baked algorithm or fixed script template. Structure the script's arguments, data models, filters, and output views based on what the user specifically seeks (e.g., chronological sorting, project scoping, score ranking, or domain-specific metadata aggregation).

3. **Synthesize Custom, Task-Specific Artifacts**:
   - Build or adapt standalone scripts per task needs rather than relying on static boilerplate.
   - Maintain core invariants across all customized scripts: **robustness and precision**, **memory safety (chunked/streaming I/O)**, **user-requested CLI flags**, and **clean, well-aligned tabular formatting**.

---

## The 4-Stage Universal Investigation Workflow

```
[1. Triage & Signature Scan] ──> [2. Contextual Boundary Pruning] ──> [3. Multi-Format Deep Extraction] ──> [4. Reusable Script & Tabular Report]
```

### Stage 1: Triage & Signature Scan
Identify target scale, directory topology, and artifact types:
1. Sample the top-level structure and count candidates.
2. Probe file signatures using magic byte detection rather than blind text assumptions:
   - Parquet: `PAR1` at offset 0
   - SQLite: `SQLite format 3\x00`
   - Archives: `PK\x03\x04` (ZIP/JAR/APK), `ustar` (TAR)
   - Binaries: `MZ` (PE/Windows), `\x7fELF` (Linux), `\xca\xfe\xba\xbe` (Java Class)

### Stage 2: Contextual Boundary Pruning
Apply domain-specific filters before executing heavy content operations:
1. **Metadata Cross-Referencing**: Locate indexing files (`history.jsonl`, `manifest.json`, database catalogs) to map targets to logical owners or projects.
2. **Path & Extension Guardrails**: Restrict searches to the relevant subset of files or directories using substring matching or regex guards.
3. **Chunked & Sampled Probes**: Read header blocks (first 2,000–5,000 bytes) to confirm whether a file or directory belongs to the target domain before scanning full contents.

### Stage 3: Multi-Format Deep Extraction
Execute format-specific search strategies:
- **Plain Text & Code**: Stream line-by-line with compiled regexes, recording line numbers and context snippets. Strip redundant leading wildcards (e.g. unanchored `.*` or `.*?` before terms) to prevent catastrophic quadratic backtracking on long lines in Python's regex engine.
- **Documents & Ebooks (PDF, DOCX, EPUB)**:
  - *PDF*: Extract page text via `pypdf`, `pdfplumber`, or `fitz` (PyMuPDF); fallback to uncompressed stream scanning.
  - *Word (.docx)*: Extract paragraphs and table cells via `python-docx`; zero-dependency fallback parses `word/document.xml` directly from the zip container.
  - *EPUB*: Extract chapters via `ebooklib`; zero-dependency fallback unpacks internal XHTML/HTML chapters from the archive.
- **Columnar & Parquet**: Inspect schema metadata first. Query columnar slices directly (via PyArrow/DuckDB or string dictionary scanners).
- **SQLite Databases**: Query table schemas from `sqlite_master`, then scan text/varchar columns across user tables.
- **Compressed Archives**: Stream directory listings and uncompress candidate text entries in-memory without extracting archives to disk.
- **Raw Bytes & Binaries**: Scan for printable ASCII/UTF-8 strings and byte regex patterns using sliding-window chunk iterators.

### Stage 4: Reusable CLI Script & Tabular Report
Transform manual investigative trials into a standalone, production-ready utility:
1. Provide essential CLI flags:
   - `--path` / `-p`: Target file or directory
   - `--term` / `-t`: Search string or regex
   - `--regex` / `-r`: Enable regular expression matching
   - `--case-sensitive` / `-c` & `--ignore-case` / `-i`: Explicit case sensitivity control
   - `--filter-path` / `-f`: Substring or project filter
   - `--sort`: Chronological, match density, file size, or name
   - `--limit` / `-n`: Top result pagination
   - `--snippets` / `-s`: Display clean context snippets beneath results
2. Render findings into a well-aligned ASCII table with dynamic column budgeting and clean line trimming.

---

## Bundled Toolkit

- **`scripts/universal_search.py`**: A complete, zero-dependency, cross-platform CLI search tool implementing format auto-detection (Text, Parquet, SQLite, ZIP/JAR/TAR, Raw Bytes), implicit path filtering, regex engine, sorting, and ASCII tabular formatting.
- **`references/data-formats-and-recipes.md`**: Specialized command recipes and code snippets for Parquet, SQLite, large byte buffers, and high-throughput streams.

---

## Example Usage of Bundled Utility

```bash
# Standard project-scoped search across thousands of files
python C:\Users\amrmu\.junie\skills\investigate-and-search\scripts\universal_search.py --path "C:\Users\amrmu\.junie\sessions" --term "UNITS.md" --filter-path "MostaqlK" --sort date --reverse

# Regex search on binary/parquet/text files with limit
python C:\Users\amrmu\.junie\skills\investigate-and-search\scripts\universal_search.py --path ./data --term "error_[0-9]+" --regex --limit 15

# Search specifically inside sqlite and archives with snippets
python C:\Users\amrmu\.junie\skills\investigate-and-search\scripts\universal_search.py --path ./artifacts --term "user_session" --ext .sqlite,.db,.jar,.zip
```
