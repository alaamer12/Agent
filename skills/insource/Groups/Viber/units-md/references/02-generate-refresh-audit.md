# Generate, refresh, audit

> **Illustrative, not exhaustive.** Commands and file names below are examples to reason from; the procedure is
> the same in any language, build system or layout. Adapt the discovery step to what the repository actually is.

## Contents
- Discover
- Evidence rule
- Generate
- Refresh
- Audit
- Delegated work and ownership
- Wiring into `AGENTS.md` §4
- Reporting and limits

## Discover

The index is built from the code, in this order:

1. **The shape of the project.** Manifests and build files (`package.json`, `pyproject.toml`, `go.mod`,
   `Cargo.toml`, `pom.xml` / `build.gradle`, `*.sln`, `composer.json`, `Gemfile`, `mix.exs`), workspace members,
   entry points, the dependency graph between packages.
2. **What is already public.** Exported API surface, module indexes, router/navigation registries, component
   barrels, DI registrations, command registrations, exported hooks, the OpenAPI/schema definitions. What a
   project deliberately exports is what it considers reusable.
3. **The repeated responsibilities.** For each of these, look for the one place the project already does it —
   outbound HTTP, retry and timeout policy, auth/session, configuration and secrets access, storage or database
   access, validation and error mapping, logging and telemetry, dates, money and unit conversion, feature flags,
   serialization, queue/workers, scheduled jobs, shared UI components, the theme/token source, the test harness.
4. **The duplicates.** The same rule computed in two places, two similar clients, three slightly different retry
   loops. Each duplicate is either a missing row, or a finding about the unit that should have absorbed it.
5. **What is off-limits.** Vendored code, generated clients, build output, caches, fixtures, migration history.
   Exclude and state the exclusion.

Cheap starting moves, in any stack:

```bash
# structure and manifests first
find . -maxdepth 3 -name "*.json" -o -maxdepth 3 -name "pyproject.toml" -o -maxdepth 3 -name "go.mod" | head
# repeated responsibilities, by name pattern (adjust per language)
grep -rniE "retry|timeout|fetch|session|logger|auth|client" --include="*.py" --include="*.ts" --include="*.go" -l . | head -30
# what the project exports
grep -rn "^export\|^public func\|pub fn\|__all__" -l . | head -20
```

## Evidence rule

A unit enters the file only after you **opened the file it points at** and saw what it does. For a "single
implementation" claim, also check the callers — one function used from thirty places is a contract, and that
changes its `Purpose` line. "It should be in `src/net/`" is a guess; `src/net/http.py` existing and exporting a
client is evidence. The `Verified` date records which of the two you had.

## Generate

1. Read `AGENTS.md` §4 if it exists: it already states the duty and the intended path. Write the file **at that
   path** — inventing a second location is the fastest way to end up with two indexes.
2. Header first: what the file is, what is excluded, `Last refreshed: <date>`, and the four duties from
   [`01-the-file.md`](01-the-file.md) (copy them from [`../assets/templates/UNITS-template.md`](../assets/templates/UNITS-template.md)).
3. Entries grouped by area, one responsibility each, ids monotonic from `U-001`.
4. Run the linter: `python <skill-dir>/scripts/units_lint.py docs/UNITS.md --strict --max-age 90`. Fix what it
   reports; do not "fix" the linter's expectations by weakening the entry.
5. Spot-check: open three entries at random and re-verify the claim against the code. A single confident wrong row
   costs the file its authority.
6. Report count, scope, exclusions, and what was not covered.

## Refresh

Triggered by a change that added or moved a unit, or as a scheduled pass.

| Drift | Detection | Action |
|---|---|---|
| Path moved or deleted | linter `paths` error | update `Where` to the new path (or mark `deprecated` with the replacement) |
| Unit split into several | one row, three responsibilities in the code | keep the original id for the primary one, add new ids for the others, note the split |
| Units merged | two rows, one file | keep one id, mark the other `deprecated` pointing at it |
| Unit gone | dead path plus no caller found | mark `deprecated` (or delete only if the user agrees and git history is enough) |
| New unit not listed | code has an exported unit no row covers | add it, next free id, in its group |
| Dependency changed | code imports differ from `Depends on` | update; a new cycle is a finding about the design, not about the file |
| Status changed | experimental code that everyone depends on | move to `active` and say why |
| Claim unverified | no `Verified` date, or code contradicts the row | re-read the code; if it cannot be checked now, mark `unknown` |

Never renumber, never reorder for cosmetics, never replace the project's format with "the standard one".

## Audit

When the file exists and someone doubts it — or before a big fan-out — reconcile in **both** directions:

- **File → code:** every `Where` exists, every `Depends on` resolves, statuses are real, purposes describe
  responsibilities rather than folders, entries are not essays.
- **Code → file:** pick the areas where work is happening now and check that their real units are listed. Missing
  coverage is the failure that matters, and it is the one a linter cannot see: an index can be perfectly valid and
  still omit the three things everyone duplicates.

Say what coverage means: "audited the two packages in the change set (14 units, 12 listed); the other eleven
packages were not opened." A percentage you did not measure is not a finding. Report a keep / fix / deprecate /
merge map, and let the user decide the merges — collapsing two units is an ownership question, not a clerical one.

## Delegated work and ownership

For parallel work, `UNITS.md` is a **read-mostly contract**:

- Every worker reads the file in full before implementing, and gets it in the brief along with the duty text.
- Workers do **not** edit the shared file (concurrent writes to one file are exactly the collision the delegation
  contract exists to avoid). Each reports a row: name, purpose, path, deps, status, verified date.
- The parent merges the reported rows, assigns ids in one pass, and runs the linter once at the end.
- If the task genuinely requires a new unit that another worker is building, that is a coordination decision to
  raise before implementation, not a duplicate to discover afterwards.

## Wiring into `AGENTS.md` §4

`agents-md` owns `AGENTS.md`; this skill owns the file it points at. So the handoff is a proposal, not an edit:

```text
AGENTS.md §4 currently says: "pending - no units index in this project yet"
Suggested line: 1. Read docs/UNITS.md in full.   (file now exists: 14 units, refreshed 2026-10-20)
Owner: whoever changes a unit updates its row in the same change; subagents report the row, the master merges it.
```

Do not write into `AGENTS.md`, do not touch another tool's managed block, and do not create a stub `UNITS.md` to
make a pointer resolve — an empty file converts a visible gap into an invisible one.

## Reporting and limits

Report: mode, scope and exclusions, entries added/changed/kept/deprecated, linter output, dead paths or drift
found, and **pending** items (areas not opened, claims not verified). Limits are part of the deliverable: an
index that silently omits half the project is worse than a narrow one that says what it covers.
