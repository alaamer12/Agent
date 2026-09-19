# Storage, Disk-Spill, & Checkpoint Architecture

Maintaining flat memory during large-scale web scraping requires decoupling state persistence from in-memory objects.

---

## 1. The Single Store of Truth Rule

### The Anti-Pattern: Duplicate Multi-Store Persistence
A common root cause of storage and page cache explosion is storing raw HTML or payloads in multiple locations (e.g. compressing HTML in SQLite while simultaneously appending raw HTML to a JSONL checkpoint). If each raw HTML page is 150 KB and 100,000 entities are scraped:
$$100,000 \times 150\text{ KB} = 15\text{ GB uncompressed write}$$
This causes severe write amplification, burns flash endurance, and consumes the entire container page cache.

### The Single Store Rule
Heavy blobs (>1 KB) must be persisted **exactly once** into compressed storage:
```
[Scraper Worker]
       │
       ├───> [Payload Storage] ───> SQLite BLOB (zstd level 3) [Single Source of Truth]
       │
       └───> [Checkpoint Stream] ──> Manifest-Only Record (JSONL / NDJSON)
                                      ├── url (string)
                                      ├── content_hash (xxhash64)
                                      ├── status (uint16)
                                      └── storage_key (int64 / uuid)
```
The manifest required to resume an interrupted crawl requires only ~128 bytes per entity. 100,000 items generate a ~12.8 MB manifest rather than 15 GB of raw JSONL.

---

## 2. Sparse Indexing & The Disk-Spill Pattern (`ProfileSpill`)

When an extraction or parse phase needs to collect entities for subsequent multi-format export, storing all parsed objects in a heap list (`results: List[Record]`) causes $O(N)$ linear memory growth.

### The Sparse Index Architecture
1. **Append-Only Compressed Log:** As each parsed record is produced, serialize it immediately to an on-disk append log.
2. **In-Memory Sparse Index:** Store only `Identifier -> (file_offset, payload_length)` in RAM:
   - Fixed 64-bit integer offset + 32-bit integer length $\approx$ 12 bytes per record in RAM.
   - 1,000,000 records require only ~12 MB of heap index!
3. **Re-Iterable Views:** The disk spill structure exposes streaming generator/iterator interfaces. Each exporter (CSV, Parquet, JSON) streams through the backing file sequentially without loading records into heap collections.

---

## 3. Storage Engine Trade-Off Matrix

| Engine | Storage Efficiency | Write Throughput | Concurrency Model | Best Fit Workload |
| :--- | :--- | :--- | :--- | :--- |
| **SQLite + WAL + zstd** | Very High (~75% compression) | Moderate (2k–10k writes/s) | Multi-reader, single-writer lock | Single-node scrapers up to 10M records; structured queries; resume checkpoints. |
| **LSM-Tree (Pebble / RocksDB)** | Moderate-High | High (20k–100k writes/s) | High concurrent writes via MemTable | High-ingest key-value pipelines with frequent point updates. |
| **Chunked Segment Log (WAL)** | High (block compressed) | Maximum (>150k writes/s) | Append-only sequential lockless | Pure sequential streaming archives; external pipeline ingestion. |
| **Embedded OLAP (DuckDB)** | Very High (columnar Parquet) | High (vectorized chunks) | Out-of-core vectorized engine | Complex analytical queries and in-situ aggregations on scraped data. |

---

## 4. SQLite Engine Discipline in Long-Lived Services

When using SQLite for checkpoint storage in long-running services:
1. **Cap Page Cache:** Set `PRAGMA cache_size = -8000;` (-8 MB). Default unconstrained caches can consume 64 MB+ per connection.
2. **Control WAL File Growth:** WAL mode (`PRAGMA journal_mode = WAL;`) can grow without bound if open read handles prevent checkpointing. Enforce:
   `PRAGMA wal_autocheckpoint = 4000;` and issue `PRAGMA wal_checkpoint(TRUNCATE);` at task completion to reset the file size to 0 bytes and drop kernel cache.
3. **Deterministic Teardown:** Explicitly close all connection pools and thread-local handles in a `finally` / `defer` block.

---

## 5. Storage Retention Policies & Disk Budgets

Long-lived scraper containers accumulate historical run directories over time. To prevent disk exhaustion and residual page cache pinning:
- **Disk Budget Enforcer:** Inspect total directory size. When total size exceeds `DISK_MAX_BYTES`, sort historical runs by `mtime` ascending and prune oldest completed runs.
- **Evict Before Delete:** Always invoke `posix_fadvise(DONTNEED)` on files before unlinking to instruct the kernel to immediately reclaim page cache.
