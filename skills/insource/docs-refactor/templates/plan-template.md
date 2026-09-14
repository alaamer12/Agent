# Refactor plan template

This is the shape the plan from Step 4 should take. Fill it in with the real findings from Steps 1-3 — don't leave placeholder-sounding text, and don't pad sections that have nothing to report.

The plan has three parts: what's wrong (from Step 2), what changes (mapped per source file), and the self-check (Step 4.5, see `templates/self-check-checklist.md`). Present all three together — the self-check isn't a separate follow-up, it's what makes the plan trustworthy enough to approve.

---

## Template

```markdown
# Refactor plan: <doc set name>

## Findings

<2-5 concrete findings from Step 2, each naming actual files and actual concepts —
not "there is some duplication" but "X, Y, and Z all explain <specific concept>,
with <specific difference>." One line per finding.>

## Changes per source file

<One entry per file currently in scope. Every existing file must appear exactly once.
Use these four kinds of entries — pick whichever applies:>

### `path/to/existing-file.md`
**Action:** Split
**Into:**
- `new/path/concern-a.md` — <one-line purpose>
- `new/path/concern-b.md` — <one-line purpose>
**Why:** <the concern-mixing finding this addresses, one line>

### `path/to/other-file.md`
**Action:** Merge into `existing-or-new/target.md`
**Why:** <the duplication finding this addresses — name what this file's content
duplicates and where the surviving explanation will live>

### `path/to/another-file.md`
**Action:** Move to `new/path/another-file.md`
**Why:** <regrouping reason — e.g. "groups with related tech concerns" —
one line, or omit this line if the move is purely a directory-convention change
from Step 3 (flat-to-nested, base/v1/v2 layering, etc.)>

### `path/to/unchanged-file.md`
**Action:** No change
<omit the Why line for unchanged files>

## New supporting files

<Files this plan creates that don't correspond to any single existing file —
directory READMEs and the root global index. One line each.>

- `new/path/README.md` — local map for `new/path/`
- `docs/README.md` — updated global index (or: created, if none existed)

## Self-check

<Filled from templates/self-check-checklist.md — see that file for what belongs here.>

## Old files

<State the Step 4 decision: "old files will be deleted once migrated" or
"old files will become redirect stubs pointing to their new location" —
whichever the user chose.>
```

---

## Notes on filling it in

- **Every existing file needs an entry, even "no change."** This makes the plan a complete map of what happens to the input, not just a highlight reel of the interesting changes — the user should never have to wonder "wait, what happened to `some-file.md`?"
- **One file can only take one action.** If a file is being both split and partially merged elsewhere, describe that as a Split whose parts happen to include a merge destination — don't invent a fifth action type.
- **Keep the "Why" lines short and specific.** They should trace back to an actual Step 2 finding. If you can't point to which finding justifies a change, that's worth re-examining before the plan goes out — it may be a convention applied for its own sake rather than because this project's content needed it.
