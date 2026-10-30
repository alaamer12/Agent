---
name: scraper-optimizer
description: Universal systems engineering standards, architectural patterns, and cross-runtime playbooks for high-throughput, memory-bounded web scrapers and data ingestion pipelines across Python, Go, Node.js, Rust, C#, and Java.
---

# Scraper Optimizer

Design, profile, and optimize high-throughput web scrapers and stream pipelines that maintain a flat $O(\text{concurrency})$ memory footprint regardless of dataset volume ($O(N)$), preventing container OOM kills (Railway, Kubernetes, Fly.io).

---

## 1. Universal Invariants

1. **The Concurrency-Memory Law:** Memory residency must strictly equal $O(\text{concurrency})$, never $O(\text{dataset})$. Any accumulation proportional to total items processed is an architectural defect.
2. **Byte-Budgeted Flow Control:** Bound in-flight channels, worker queues, and ingest buffers by **bytes**, never by discrete item counts. Heterogeneous payloads vary by $10^2$–$10^4\times$.
3. **Single Store of Truth:** Persist heavy response bodies (raw HTML/DOM/blobs) into compressed storage once. All channels, checkpoints, and IPC pipelines transport lightweight manifests or sparse pointers only.
4. **Three-Layer Accounting:** Linux containers charge **Anonymous Heap + Kernel Page Cache + Slab/Tmpfs** against the cgroup limit (`memory.current`). Optimizing the heap while writing un-evicted files guarantees OOM.
5. **Deterministic Scoped Lifecycles:** Bound database connection pools, statement caches, and telemetry modifications to explicit task scopes with teardown in `finally` / `defer` / `Drop`.
6. **Audit-Before-Remediation Discipline:** Never apply speculative code changes. Conduct deep static scans and dynamic multi-tier tests (from seconds micro-probes to hour draining tests), score leak hypotheses in an audit document, obtain user approval, and reconcile the living audit report with post-fix verification.

---

## 2. Quick Diagnostic Checklist

| Symptom Observed | Primary Suspect Mechanism | Diagnostic Action & Remedy | Deep-Dive Reference |
| :--- | :--- | :--- | :--- |
| **Flat staircase growth across runs** | Leaked run-level resources / thread-local DB pools | Check thread-local connection caches, module-level DataFrames; enforce run-scoped teardown. | `references/storage-and-spill.md` |
| **Instant SIGKILL during export/download** | Buffered full-file I/O or multi-copy serialization | Replace `read()` / `to_parquet()` with constant 64 KB stream chunks and row-group iterators. | `examples/zero-cache-streaming-io.md` |
| **OOM while process RSS reports low usage** | Kernel page-cache accumulation charged to cgroup | Read `/sys/fs/cgroup/memory.current`; call `fdatasync` + `posix_fadvise(DONTNEED)`. | `references/runtime-tuning.md` |
| **Heap does not drop after GC runs** | Allocator arena fragmentation (glibc/jemalloc) | Pre-set `MALLOC_ARENA_MAX=2` in container environment; trigger `malloc_trim(0)`. | `references/runtime-tuning.md` |
| **Bursty memory spikes under high load** | Item-count bounded queues with oversized payloads | Switch to byte-budgeted semaphore channels (`max_bytes` ceiling). | `examples/byte-budgeted-pipeline.md` |

---

## 3. Core Architecture: Layered Backpressure Pipeline

```text
[Network Ingest Stream]
        │
        ▼
[Byte-Budgeted In-Flight Channel] (Token-bucket / semaphore permits)
        │
        ▼
[Concurrent Parsing Worker]
        │
   ┌────┴───────────────────────────┐
   ▼                                ▼
[Compressed Payload WAL]     [In-Memory Sparse Index] (Offset/Length/Hash)
(SQLite+zstd / Segment Log)         │
   │                                ▼
   ▼                         [Streaming Exporter] (Row Groups / NDJSON)
[posix_fadvise(DONTNEED)]           │
                                    ▼
[Cgroup Reactive Governor] ───> [Zero-Buffer Egress / Socket Stream]
```

---

## 4. Workflows & Progressive Routing

- **To execute the audit, testing, user approval & remediation workflow:** Read `references/diagnostic-and-remediation-workflow.md` and use `assets/templates/memory-audit-report-template.md`.
- **To architect queues & streaming pipelines:** Read `references/core-principles.md` and check `examples/byte-budgeted-pipeline.md`.
- **To review language-specific hazards (C#, Go, Python, Node, Rust, Java):** Read `references/language-and-runtime-quirks.md`.
- **To review formal state machines, failure modes, & deep study:** Read `references/architecture-study.md`.
- **To configure Docker, allocators, and cgroups:** Read `references/runtime-tuning.md` and apply `assets/templates/docker-allocator.env`.
- **To implement disk spills, manifests, and checkpoints:** Read `references/storage-and-spill.md` and inspect `examples/disk-spill-and-indexing.md`.
- **To write CI assertions that prevent memory regressions:** Read `references/profiling-and-verification.md` and use `assets/templates/test-memory-bounded-template.md`.
