# Cutting a job into slices

A slice is a unit of work one agent can finish, verify, and hand back without needing another slice's files. Cut by deliverable and ownership, never by topic.

## The slice test

A slice is ready when all of these are true:

1. **One deliverable** — a file, a module, a page, a migration, a test suite. If the summary needs "and", cut again or merge.
2. **Owned paths** — an explicit list of files it may write. Everything else is read-only for it.
3. **A verification it can run** — its own test, build, or check that proves the slice done. "Looks right" is not a check.
4. **No interface it must invent** — every contract it consumes already exists (see below).
5. **Bounded reading** — it can find what it needs without reading the whole repository.

## Interfaces before slices

Decide and write down, before launch:

- types, function signatures, API shapes, event names, schema fields, file formats;
- naming conventions and error shapes at the boundaries between slices;
- the one place each shared concept lives.

If slice B consumes something slice A produces, the interface goes into both briefs as fixed text. "A will figure it out" is how two agents produce two incompatible answers to the same question. The main agent decides open questions once, centrally — never twice, independently.

## Shared-file traps

These break ownership even when the slices look independent:

| Trap | Fix |
|---|---|
| Lockfiles, package manifests | One owner, or the main edits them after the wave |
| Index/registry files (routes, exports, catalogs) | Main owns the index; slices hand it entries |
| Config and environment files | Main serializes them |
| Generated files | Regenerate once after the wave, never per slice |
| Formatting on save | The slice formats only its own files; no repo-wide formatter run |
| Database schema / migrations | A single owner slice, and it runs first |

## Dependency shapes

```
FAN-OUT      A ─┬─> B          independent slices, no cross-reads
                ├─> C
                └─> D

FAN-IN       A ─┬─> C          slices produce, one integration step consumes
             B ─┘

PIPELINE     A ──> B ──> C     strictly ordered; only parallelize inside a stage

DIAMOND      A ──> B, C ──> D  shared foundation, parallel middle, shared end
```

- Fan-out is the cheapest and the default.
- Fan-in needs the integration owner named up front — usually the main agent.
- Pipelines are serial by nature; splitting a stage across agents is the only parallel move.
- Diamonds hint at the right shape: interface first (A), parallel slices (B, C), main integrates (D).

## Sizing

- Too small: the brief costs more than the work. Fold it into a neighbor or into the main's own slice.
- Too large: it collides with everything, takes a whole wave, and its failure loses the most. Split along a natural seam.
- Rough guide: a slice is well-sized when its brief fits on one screen and its verification runs in minutes.

## Cuts that look right and are not

- **By layer for one feature** — "one agent does the UI, one the API, one the tests": the feature's shape lives in all three, so all three invent it differently. Cut by feature, or fix the interface first.
- **By file count** — ten agents for ten files in one module: every agent needs the module's conventions, and the merge is the actual work.
- **By buzzword** — "one agent per concern" when the concerns are interleaved in the same functions.
- **Cleanup as a slice** — deletions and rewrites are destructive; keep them with the main agent (see `03-main-agent-work.md`).
