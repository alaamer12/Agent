# Remedies, sizing, descriptions, dependencies — the change author's half

## Structural remedies: propose the move, not just the problem

A review that only says "this is complex" leaves the author guessing.
For each structural finding, name the restructuring:

- Replace a chain of conditionals with a typed model or explicit
  dispatcher.
- Collapse duplicate branches into a single clearer flow.
- Separate orchestration from business logic so each reads alone.
- Move feature-specific logic out of a shared module into the package
  that owns the concept.
- Reuse the canonical helper instead of the bespoke near-duplicate.
- Make a type boundary explicit so downstream branching disappears.
- Delete the pass-through wrapper that adds indirection without
  clarifying the API.
- Extract a helper, or split a large file into focused modules.

Prefer the remedy that **removes moving pieces** over one that spreads
the same complexity around.

## Change sizing

```
~100 lines changed   → good — reviewable in one sitting
~300 lines changed   → acceptable if one logical change
~1000 lines changed  → too large — split it
```

Watch **file size, not just diff size**: a small diff can push a file
past a healthy boundary (~1000 *total* lines per file is a common
inspection signal, not a hard cap). When a change materially grows an
already-large file, ask whether to extract helpers/submodules *first*.

**"One change"** = one self-contained modification addressing one
thing, with its tests, keeping the system functional after submission —
one part of a feature, not the whole feature.

Splitting strategies when too large:

| Strategy | How | When |
|---|---|---|
| Stack | submit small, base next on it | sequential dependencies |
| By file group | separate changes per reviewer area | cross-cutting concerns |
| Horizontal | shared code/stubs first, then consumers | layered architecture |
| Vertical | smaller full-stack feature slices | feature work |

Acceptable exceptions: complete file deletions and automated
refactoring where the reviewer verifies intent, not every line.

**Separate refactoring from feature work.** Refactor + new behavior =
two changes. Small cleanups (renames) may ride along at reviewer
discretion.

## Change descriptions (what review checks in history too)

The description must stand alone in version control.

- **First line**: short, imperative, standalone — "Delete the FizzBuzz
  RPC", not "Deleting…" or "Fix bug". Informative enough to find the
  change without reading the diff.
- **Body**: what is changing and why; context and decisions not
  visible in code; links to issues/benchmarks/design docs; honest
  about approach shortcomings.
- **Anti-patterns**: "Fix bug", "Fix build", "Add patch", "Moving code
  from A to B", "Phase 1", "Add convenience functions".

(The repo's own commit conventions win; `commit` skill authors the
message — review only checks it survives `git log --oneline`.)

## Dependency discipline

Part of every review that adds a package:

1. Does the existing stack already solve this? (Often yes.)
2. Size / bundle impact?
3. Actively maintained? (last commit, open issues)
4. Known vulnerabilities? (the ecosystem's audit command)
5. License compatible with the project?

Rule: prefer standard library and existing utilities; every dependency
is a liability. The workshop's `pick`/`packages`-style tooling can
answer 2–4 with evidence when adoption data matters.

## Dead-code hygiene

After refactoring or implementation:

1. Identify code now unreachable or unused.
2. List it explicitly, with what replaced it:
   `formatLegacyDate() in utils/date.ts — replaced by formatDate()`
3. **Ask before deleting** — never silently remove what you're not
   sure of. Doubt goes to the author as a question, not an action.

Dead code left behind confuses future readers *and* future agents.
