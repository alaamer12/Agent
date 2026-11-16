# Diagnostic Audit, Testing Protocol & Remediation Lifecycle

This protocol defines the mandatory 5-stage lifecycle that the `scraper-optimizer` skill executes when auditing, stress-testing, diagnosing, and resolving memory instabilities in a codebase:

```text
[Stage 1: Deep Codebase Static Scan]
         │
         ▼
[Stage 2: Multi-Tier Dynamic Stress Testing] (Fast Probes → Draining Tests)
         │
         ▼
[Stage 3: Evidence-Based Audit Report & Hypothesis Scoring]
         │ (Generates diagnostic report & asks user for approval)
         ▼
   User Approval (Interactive Gate)
         │
         ▼
[Stage 4: Disciplined Surgical Remediation]
         │
         ▼
[Stage 5: Verification & Living Document Reconciliation]
         │ (Updates report with verified outcomes)
         ▼
   Final Resolution
```

---

## Stage 1: Deep Codebase Static Scan

Before running any code or proposing fixes, perform an exhaustive, multi-pass scan across all layers of the codebase to uncover memory-sensitive patterns:

1. **Queue & Concurrency Bounds:**
   - Scan channel, queue, and worker pool instantiations (e.g. `asyncio.Queue`, Go `chan`, Tokio `mpsc`, Node streams).
   - Verify whether bounds are based on **discrete item counts** (fragile) or **byte budgets** (robust).
2. **Buffer & I/O Materialization:**
   - Detect monolithic file reads/writes (e.g. `file.read()`, `await response.body()`, `ReadAll`, `to_parquet()`, `json.dump()`).
   - Flag any HTTP handlers or file transfers lacking fixed 64 KB streaming buffers or kernel zero-copy bypass.
3. **Data Accumulation & Collections:**
   - Search for long-lived in-memory collections, slices, or lists that append per-item records without an off-heap or disk spill mechanism.
4. **Lifecycle & Teardown Scopes:**
   - Inspect database connections, SQLite page caches, statement caches, and HTTP clients.
   - Verify whether cleanup is bound to deterministic scopes (`finally`, `defer`, `using`, RAII `Drop`) or left to non-deterministic garbage collectors.
5. **Runtime & Allocator Configurations:**
   - Check container manifests (`Dockerfile`, `docker-compose.yml`, K8s/Railway manifests) for allocator controls (`MALLOC_ARENA_MAX`, `GOMEMLIMIT`, `NODE_OPTIONS`, `DOTNET_gcServer`).
6. **Kernel Cache Eviction Hooks:**
   - Check if large write operations are followed by file sync and kernel page-cache invalidation (`posix_fadvise(DONTNEED)`).

---

## Stage 2: Multi-Tier Dynamic Stress Testing Protocol

Dynamic testing progresses through three tiered tiers to empirically confirm or disprove static hypotheses:

### Tier 1: Micro-Probe Benchmark (Seconds: 5s – 30s)
- **Objective:** Verify immediate memory scaling against the Relative Scaling Law:
  $$\frac{\text{PeakMemory}(4N)}{\text{PeakMemory}(N)} < 1.30$$
- **Method:** Run isolated unit workloads with synthetic dummy payloads (e.g. $N=250$ vs $4N=1,000$ records).
- **Metric:** Peak RSS and process private bytes. A ratio $> 1.5$ immediately confirms an in-memory accumulation defect ($O(N)$ heap growth).

### Tier 2: Intermediate Pipeline Soak Test (Minutes: 2m – 10m)
- **Objective:** Detect allocator arena fragmentation, un-evicted page cache accumulation, and byte variance instability.
- **Method:** Execute realistic multi-worker pipelines with variable payload sizes (2 KB to 5 MB) under rate-limited concurrency.
- **Metric:** Monitor Linux cgroup metrics (`memory.current` vs `memory.stat: file`). A growing discrepancy between `rss` and `memory.current` confirms kernel page-cache trapping.

### Tier 3: Full Long-Horizon Draining Soak Test (Hours: 30m – 1h+)
- **Objective:** Detect slow, subtle leak vectors—such as long-lived connection pool buildup, goroutine leaks, event listener retention, LOH fragmentation, or un-reclaimed SQLite WAL page caches.
- **Method:** Continuous end-to-end load test simulating production scale (e.g. 50,000+ entities) with simulated network latency and upstream jitter.
- **Metric:** Monitor memory sawtooth stability. A healthy system exhibits a bounded sawtooth pattern returning to baseline at every batch/run teardown, with zero monotonic baseline drift.

---

## Stage 3: The Audit Document & User Approval Gate

Upon completing the static analysis and dynamic test tiers, the skill **does NOT make speculative code modifications**. 

Instead, it drafts a formal, structured audit file (e.g. `MEMORY_AUDIT_REPORT.md` or `docs/MEMORY_OPTIMIZATION_AUDIT.md`) containing:
1. **Executive Summary & Cgroup Profile:** Container memory limit, current peak usage, and breakdown of anonymous heap vs page cache vs allocator overhead.
2. **Empirical Test Findings:** Exact numbers and memory ratios from Tier 1, Tier 2, and Tier 3 tests.
3. **Hypothesis Evaluation & Scoring:**
   - Each suspected memory leak vector is cataloged and assigned a confidence score (**Confirmed**, **Refuted**, or **High Risk**) based on test evidence:
     * *Live Reference Accumulation ($O(N)$ List/Map)*: [Confirmed / Refuted]
     * *Allocator Arena Fragmentation (Glibc/Jemalloc)*: [Confirmed / Refuted]
     * *Page Cache Pollution (Un-evicted File I/O)*: [Confirmed / Refuted]
     * *Item-Count Channel Overflow*: [Confirmed / Refuted]
     * *Resource Lifecycle Leak (DB Pool/Socket)*: [Confirmed / Refuted]
4. **Proposed Surgical Action Plan:**
   - Step-by-step architectural remediations prioritized by impact (e.g., implementing `ProfileSpill`, adding 64 KB chunking, setting container env vars, adding scoped `finally` teardowns).
   - Expected post-fix memory baseline and risk assessment.

### The User Approval Gate
The agent presents the findings and prompts the user:
> *"The comprehensive static scan and dynamic memory tests are complete and documented in `<audit-file>`. I have identified the root causes and scored all hypotheses. Please review the proposed remediation plan and approve execution."*

---

## Stage 4: Disciplined Surgical Remediation

Once the user grants explicit approval, the agent applies the planned fixes strictly adhering to the universal invariants:
- **Never apply broad refactors:** Target only the verified root causes.
- **Preserve domain semantics:** Do not alter parsing logic, rate limiters, or data contracts.
- **Enforce Layered Backpressure:**
  * Wrap in-flight channels with byte-budgeted semaphores.
  * Convert monolithic file reads to 64 KB streams.
  * Introduce sparse index disk spills for accumulated collections.
  * Inject container allocator environment flags.
  * Add deterministic `finally` / `defer` cleanup hooks.

---

## Stage 5: Verification & Living Document Reconciliation

After implementing the fixes, the agent validates the solution:
1. **Re-run the Dynamic Test Suite:**
   - Execute the Tier 1 Micro-Probe and Tier 2 Soak Tests to demonstrate that the memory ratio has returned to flat baseline ($\le 1.15\times$).
   - Verify that page cache is evicted immediately upon file sync.
2. **Reconcile and Update the Audit Document:**
   - The agent returns to the audit file created in Stage 3 and updates it with the final resolution section:
     * **Resolution Summary:** Concrete modifications made.
     * **Before vs. After Telemetry:** Side-by-side comparison of peak RSS, container memory, and page cache.
     * **Permanent CI Assertions:** Added regression tests ensuring future changes do not reintroduce $O(N)$ memory scaling.
3. **Present Final Verification:**
   - Deliver the final summary to the user with references to the reconciled audit artifact.
