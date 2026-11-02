# Case — generating the index, then keeping it alive

A mid-size product repo: three packages, six months old, no `UNITS.md`. Two features had just been built twice,
and `AGENTS.md` §4 reads `pending - no units index in this project yet`.

## Mode: generate, scoped

Run the discovery order from
[`../references/02-generate-refresh-audit.md`](../references/02-generate-refresh-audit.md): manifests → exported
surface → repeated responsibilities → duplicates.

```bash
ls; cat package.json | head -20
find . -maxdepth 2 -name "pyproject.toml" -o -maxdepth 2 -name "package.json" -not -path "*/node_modules/*"
grep -rniE "retry|timeout|session|logger|client" --include="*.py" --include="*.ts" -l . | head -30
```

**Scope decided and written in the header:** `packages/reporting` and `packages/api` — where the work happens —
plus the shared `packages/platform`. `apps/legacy-admin` was **not** opened; the header says so, and the report
says so. Vendored code and generated API clients excluded.

## What the pass found

34 candidate files → 19 units. Three examples, including the finding that motivated the work:

```markdown
### U-004: Outbound HTTP client
- **Purpose:** Single outbound HTTP path: timeout, retry with backoff, error mapping to `IntegrationError`.
- **Where:** src/platform/net/http.py
- **Depends on:** U-006
- **Status:** active
- **Verified:** 2026-10-30

### U-009: Cart discount rules
- **Purpose:** The one implementation of bulk-discount and total rules.
- **Where:** src/domain/pricing/rules.py
- **Reuse instead of:** the copy in `src/reporting/totals.py` (diverges at quantity boundary)
- **Status:** active
- **Verified:** 2026-10-30

### U-014: Reporting totals
- **Purpose:** Report-side totals. Currently re-implements U-009.
- **Where:** src/reporting/totals.py
- **Depends on:** U-009
- **Status:** experimental
- **Notes:** do not extend until it calls the shared rules; kept listed so the duplication is visible
```

`U-014` is the point of the exercise: an index that only lists the *good* unit hides the duplicate. Listing both,
with `Reuse instead of` and an honest status, is what makes the next contributor fix it instead of joining it.

Two things did **not** get entries: `src/utils/` (a bucket, not a responsibility — reported as a finding to split)
and the generated API client (excluded scope).

## Verification

```bash
python <skill-dir>/scripts/units_lint.py docs/UNITS.md --strict --max-age 90
# 19 unit(s) checked in docs/UNITS.md
# OK
```

Then the spot-check: three random rows re-opened against the code. One was wrong — `U-011` claimed "single
storage access point" while a second module opened its own connection. Fixed to name both paths and mark the
consolidation `experimental`. A linter proves structure; only reading proves truth.

## Handoff to `agents-md`

`AGENTS.md` §4's pointer is `agents-md`'s to write, so this skill reported the line instead of editing it:

```text
1. Read docs/UNITS.md in full.   (exists: 19 units, refreshed 2026-10-30, scope: platform/api/reporting;
   legacy-admin not covered)
Owner: whoever changes a unit updates its row in the same change; subagents report the row, the master merges it.
```

## Two weeks later: refresh during delegated work

A fan-out of three subagents, each briefed with `docs/UNITS.md` and the duty text. Workers did not edit the file —
each reported a row in its summary. The parent:

```text
merged 2 new rows (U-020 export job, U-021 webhook verifier)
1 duplicate reported twice by two workers -> one row kept, the other became a note under U-014
1 dead path -> the file moved during a rename; corrected, Verified bumped to 2026-11-13
cycle check: clean
```

One worker had built a second CSV writer next to `U-007`. The row existed, the brief included it, and the worker
still duplicated — so the fix was not more documentation but the reuse reason: the change now states why
`U-007` did not fit, and that reason turned out to be wrong. The team deleted the second writer as a follow-up
decision; `units-md` reported the duplication and stopped there, because changing application code is not this
skill's job. That is the whole value of the index: the duplication becomes a decision someone can see, instead of
a second file nobody notices.
