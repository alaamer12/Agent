---
name: units-md
description: 'Generates, refreshes, and audits a project''s UNITS.md - the index of reusable units an agent reads before implementing, so it extends what exists instead of building a parallel one. Each entry is one row of facts: name, responsibility, where it lives (a path that must exist), what it depends on, what it replaces, its status, and the date the claim was checked; the header carries the four duties agents-md section 4 promises - read it in full first, reuse or extend with a stated reason, add a new reusable unit in the same task, and name who updates it. Built from the code, never from what docs claim or from plausible guesses. Use for "make a UNITS.md", "build the units index / component catalog", "we keep reinventing things that exist", "refresh UNITS.md", "does this already exist", when AGENTS.md section 4 points at a units file that does not exist, or before a fan-out so workers reuse instead of duplicating. Not a task list, not a backlog, not architecture documentation, and it never edits AGENTS.md itself.'
when_to_use: The user asks to create, regenerate, refresh, or audit a units/component/registry index (often `docs/UNITS.md`); AGENTS.md's units duty points at a file that does not exist; work is being delegated in parallel and duplication is the risk; or the user complains that the project keeps rebuilding what it already has.
argument-hint: "[generate|refresh|audit] [project root, defaults to current repo]"
---

# units-md

`UNITS.md` answers one question before any code is written: **does something here already do this?** It is an
index of the project's reusable units, not documentation about them, and not a to-do list.

`agents-md` owns the *duty* ("read the units file first, reuse or extend, update it in the same task") and the
pointer in `AGENTS.md` §4. **This skill owns the file the pointer aims at.** It never writes `AGENTS.md`.

## What counts as a unit

The test, all three: **someone starting work would look for it before building it; it has a boundary you can
point at (a path); its responsibility is nameable in one line.** Boundary rules, examples across shapes and
stacks, and what is *not* a unit: [`references/00-what-a-unit-is.md`](references/00-what-a-unit-is.md).

## What the file is not

| Not this | Go instead |
|---|---|
| Work breakdown, backlog, task list, sprint units | the project's tracker or a plan document |
| Architecture narrative, ADRs, design rationale | the project's docs; `document` |
| The project's rules and obligations | `agents-md` |
| The reusable patterns an *agent* follows in this catalog | `bequest/` (`heir` reads it) |
| A list of anti-patterns to avoid | `antipattern` |
| A component gallery or design-token sheet | design docs; `capture design` extracts tokens |

## The entry

One heading per unit, four required fields, three optional. Full definitions, id and ordering rules, status
vocabulary, and how to merge into a project's existing convention:
[`references/01-the-file.md`](references/01-the-file.md).

```markdown
### U-007: Cart pricing rules
- **Purpose:** The one implementation of discount and total rules.
- **Where:** src/pricing/rules.py
- **Depends on:** U-004
- **Reuse instead of:** per-handler discount math
- **Status:** active
- **Verified:** 2026-10-20
```

## Workflow

Copy and track:

```
- [ ] 1. Mode: generate, refresh, or audit
- [ ] 2. Scope: which project, which packages, what is excluded
- [ ] 3. Discover the units from the code
- [ ] 4. Set granularity
- [ ] 5. Write or merge the file
- [ ] 6. Verify, then report
```

1. **Mode.** Look before deciding: `find . -maxdepth 3 -iname "UNITS.md" -o -maxdepth 3 -iname "*units*.md"`,
   and read the `AGENTS.md` §4 pointer. A file exists → **refresh** (add what is new, correct what moved, never
   renumber). None, but §4 points at one → **generate**. Both exist and the user doubts it → **audit**.
2. **Scope.** One repo, or a monorepo package? Vendored, generated, build output, fixtures and `.git` are out:
   listing them turns the index into noise. Say what was excluded in the file's header line.
3. **Discover from the code.** Manifests and entry points first, then the shapes a newcomer would repeat:
   outbound HTTP, retry, auth/session, storage access, validation, date/money handling, logging, feature flags,
   shared UI components, the domain rules. Per-stack discovery hints:
   [`references/02-generate-refresh-audit.md`](references/02-generate-refresh-audit.md) §Discover. A unit enters the
   file only when you have opened the file it points at.
4. **Granularity.** One responsibility per row. Too broad → the index hides what exists and people duplicate it;
   too fine → nobody reads it. Merging and splitting tests: `00-what-a-unit-is.md` §Granularity.
5. **Write or merge.** Start from [`assets/templates/UNITS-template.md`](assets/templates/UNITS-template.md) only
   when there is no incumbent format. If the project already has a units/component/registry file, follow its
   headings, ids and ordering, and add entries — never renumber or reformat what exists, and never create a
   competing second file.
6. **Verify.** Run `python <skill-dir>/scripts/units_lint.py <path-to-UNITS.md>` (add `--strict`, `--max-age 90`).
   It checks ids, required fields, that every `Where` path exists inside the project, dependency ids and cycles,
   status vocabulary, two rows claiming one path, entry size, placeholders left behind, and the four duties.
   Then confirm the file is *true*: open three random entries and check the claim against the code.

## Rules

- **The code is the source.** A unit is listed because the path exists and does what the row says. Nothing gets
  in because a doc, a plan, or a memory claims it exists.
- **`Verified` is a date, not a feeling.** It is the day the claim was checked against the code; the header's
  `Last refreshed` is the day the whole pass ran. An undated claim is a guess wearing a citation.
- **Reuse beats re-listing.** When two names cover one thing, keep the entry that the code actually routes
  through, and mark the other deprecated with a pointer — do not add a second row for the same file
  (the linter calls that a duplicate).
- **The same-task duty.** A new reusable unit created during a task means its entry goes in that same change.
  A units index nobody updates dies in one quarter. When a subagent built the unit, the parent merges the entry —
  workers report the row, they do not edit the shared file.
- **Read the file before writing the file.** On refresh, re-read what exists first; the index itself is subject
  to its own reuse rule.
- **No stubs.** Generating an empty or decorative `UNITS.md` to make a pointer valid is worse than a missing
  file: it turns a visible gap into an invisible one.
- **Size beats completeness.** A 40-line index that is read beats a 900-line inventory that is skipped. When the
  project is huge, scope the file to the packages work actually touches and say so in the header.

## Reporting

Return, in this order: mode and scope (what was excluded), the unit count added/changed/kept, dead paths or
drift found, entries deliberately merged or deprecated and why, linter result, and what is **pending** — areas
you did not open. If `AGENTS.md` §4 has no target or points elsewhere, hand back the exact line to fix it, but do
not edit that file here: `agents-md` owns it.

## Files

| Path | Owns |
|---|---|
| [`references/00-what-a-unit-is.md`](references/00-what-a-unit-is.md) | the boundary test, shapes across stacks, non-units, granularity, exclusions |
| [`references/01-the-file.md`](references/01-the-file.md) | entry fields, ids, ordering, status vocabulary, size budget, the four duties, merging into an existing convention |
| [`references/02-generate-refresh-audit.md`](references/02-generate-refresh-audit.md) | discovery by stack, refresh and audit procedures, drift handling, ownership, wiring into `AGENTS.md` §4 |
| [`references/03-ui-units-profile.md`](references/03-ui-units-profile.md) | the presentation-layer profile: components, adaptive concepts, builder functions, grouping, and how UI statuses map onto the vocabulary |
| [`assets/templates/UNITS-template.md`](assets/templates/UNITS-template.md) | the skeleton, when to use it instead of the project's own format |
| [`examples/case-01-generate-and-refresh.md`](examples/case-01-generate-and-refresh.md) | a worked pass: scope, the duplicate that justified the file, what stayed out, the linter, the delegated refresh |
| `scripts/units_lint.py` | mechanical checks; `--strict`, `--max-age`, `--root`, `--fixtures`, no arguments = self-test |
