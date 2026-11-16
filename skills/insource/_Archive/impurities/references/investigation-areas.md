# impurities — investigation areas & how iterations get derived

Read during planning (§1–§3 of SKILL.md). **Neither list below is mandatory
or exhaustive** — they calibrate thinking about where impurities hide in a
project *like this one*; the assessment decides which deserve an iteration.

## Candidate areas to weigh during assessment

- **Runtime behavior** — startup/shutdown ordering, lifecycle events the
  code never handles, work done per-frame/per-request that should be
  done once, blocking calls on hot paths, timers/listeners never disposed.
- **Resource lifecycle & memory** — allocation churn, retained objects,
  caches without eviction, large buffers per operation, unbounded growth
  across sessions, native/memory leaks GC never sees.
- **CPU / disk / network consumption** — redundant computation, repeated
  file reads, unbatched or duplicate requests, missing caching, polling
  where events exist, logging that writes hot-path I/O.
- **Concurrency & threading** — races on shared mutable state, unbounded
  task spawning, locks held across I/O, cancellation not propagated,
  async errors swallowed, shutdown racing work in flight.
- **Dependency configuration & compatibility** — undeclared implicit
  requirements, version conflicts resolved by luck, deps duplicated across
  workspaces, wrong scope (runtime vs dev), abandoned-but-installed
  defaults; see the `packages` skill for the deep pass.
- **Build systems & dev tooling** — nondeterministic outputs, build steps
  that silently skip, watchers/scripts that leak, dev-only tooling
  reachable from production config.
- **Assets & resource organization** — missing variants (per-theme/density/
  DPI), embedded duplicates of one file, dead references, path assumptions
  that break on another platform, oversized media shipped uncompressed.
- **Configuration & environment drift** — behavior differing dev/staging/
  prod, defaults that mask missing config, secrets-ish values in code or
  committed configs (report severity honestly), env vars read but never
  documented.
- **Platform-specific requirements** — permissions, entitlements, native
  toolchains, file-path/encoding assumptions, case-sensitivity differences.
- **Component interactions** — integration seams where two correct
  components compose incorrectly: shared schema drift, event ordering,
  duplicated validation (or none at the boundary).

## Worked examples — how an iteration is derived (not selected from a list)

### Example: resource consumption

A desktop app constructs an XML object every frame. Logically correct per
frame; *repeated*, it may cause allocation churn, memory pressure, wasted
CPU, retained objects. Derived iteration investigates: why the object is
created per-frame · whether its lifetime matches its use · whether the work
must happen every frame at all · retention beyond intent · whether
reuse/caching/another design fits · **whether runtime profiling confirms the
suspicion**. Establish the actual issue before choosing the correction —
"looks wasteful" without measurement stays an optimization *opportunity*,
not a confirmed defect.

### Example: dependency integrity

A package no source file imports. It may still be consumed by build
tooling, CI pipelines, plugins, code generators, scripts, configuration,
runtime loading, other dependencies, or packaging/optimization steps.
Derived iteration: is it correctly declared, compatible, necessary, and
appropriately scoped — resolved through SKILL.md §2's six-step procedure.
Import-search-and-delete is the failure mode this example exists to prevent.

### Example: asset integrity

An app references a logo variant that doesn't exist, or the same SVG is
embedded in several source files. Derived iteration: resource existence
per variant/theme, import mechanics, duplication, path correctness — and
where a shared asset is appropriate, extract once into a dedicated resource
and update all references (verified by rebuilding the consumers, not by
grep count).

Each example shows the same shape: a *suspicion grounded in the project*, an
investigation that converts it to evidence or drops it, a remediation fitted
to the established cause, verification matched to the claim.

## Deriving your own iteration from an assessment observation

1. Name the observed smell and where exactly it lives (file/behavior).
2. Ask what would have to be true for it to be a real defect — that is the
   evidence bar (expected evidence in the iteration definition).
3. Ask what removing/changing it could break *implicitly* (§2 mechanisms).
4. Pick the cheapest investigation that raises or kills confidence
   (profiling, reproduction, config audit, run-once measurement).
5. If confirmed: fix at the cause; if not: it goes in the findings report
   as suspected/not-a-defect — never silently dropped, never silently fixed.
