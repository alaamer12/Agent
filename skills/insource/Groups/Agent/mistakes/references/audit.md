# Audit mode — `/mistakes` over a project

The full audit procedure, the fix-safety tiers that decide what may be
edited, the hard rules, and the report format.

## Audit the project (`/mistakes`)

A bare `/mistakes` means: read the active log, search the project for real instances of each
pattern, report what is confirmed, and fix only what is safe.

1. **Scope.** The whole repository by default. Narrow by `id`, keyword or path when given.
2. **Select rows.** Only `status=active`; skip `retired`. Skip rows whose `scope` names a stack
   or domain this project does not use (`*` always applies). A `suspected` row must be confirmed
   by reading code before it is reported.
3. **Probe.** Turn each row's `signal`, `tags` and `where` into a short set of searches. Search
   only surfaces that exist: schema and migrations, API handlers, components, state, tests,
   config, docs. Do not search the same pattern twice.
4. **Confirm.** A search hit is a lead, not a finding. Read the surrounding code and cite
   `file:line` with the exact snippet. Drop anything you cannot confirm.
5. **Classify.** Assign each finding a fix tier (below).
6. **Report.** One findings table with a tier column, plus a clean list and an unverified list.
7. **Fix.** Apply tier A, show the diff. Propose tier B. List tier C without editing.
8. **Verify.** Run the row's `check` where possible; state pass, fail, or cannot-run.

### Fix safety

| Tier | Examples | Action |
|---|---|---|
| **A — safe** | Docs, comments, README, changelog, docstrings, example config | Fix immediately, then show the diff |
| **B — local code** | One-file rename, splitting a composite value inside one module, adding a missing validation, adding a regression test | Show the proposed diff first; apply after approval |
| **C — report only** | Schema or migration, data backfill, public API contract, auth or permission logic, secrets, dependency upgrade, cross-cutting refactor | Never edit; report with a plan |

Hard rules:

- Never run a database migration, backfill or destructive query.
- Never rotate, print or move a secret; report its location only.
- Never change a public API contract or an auth rule without explicit approval.
- Never fix a `suspected` row.
- Stop and ask when a "safe" fix would touch more than one concern.

### Audit report format

```text
mistakes audit — <repo or path> — <date>

Applied rows (6): mixed-type-field, float-money, timezone-naive, ...

Findings (3)
| # | row | location | evidence | tier | action |
|---|-----|----------|----------|------|--------|
| 1 | mixed-type-field | src/db/schema.sql:42 | `price TEXT` stores "$12" | C | report only |
| 2 | timezone-naive   | docs/api.md:18      | example uses local time | A | fixed |
| 3 | n-plus-one       | src/api/orders.ts:88 | query inside a loop | B | proposed |

Clean (3): secrets-in-client, duplicated-state, client-validation-only — checks passed.
Unverified (1): <id> — could not run <check> because <reason>.
```

Report only what you actually found. "No findings" is a valid, useful result; never pad it.
When the project documents a deliberate exception, list the finding once under "Known exceptions"
with the citing decision and move on.
