---
name: mistakes
description: 'A personal, growing log of mistakes already made or observed, with where each one shows up and how to fix it. Use when the user says mistakes, check my mistakes, audit for mistakes, avoid this, remember this mistake, log a mistake, add to my mistakes, lessons learned, I told you before, we already fixed this, or before data modeling, API design, migrations, auth, state management, UI, tests, or configuration. Invoked as /mistakes it audits the project against the active log, reports confirmed findings with file and line evidence, fixes the safe ones (docs, comments, README, tests) and proposes the risky ones (schema, migrations, API contracts, auth, secrets) for approval instead of editing them. It also loads only the rows that match the current task, applies their fixes before the work, runs their checks after it, and appends a new row only when the user asks. Not a style guide, not a generic best-practice list, and never a silent override of the project own documented decisions.'
---

# mistakes — failure patterns to avoid

A small log of mistakes that were actually made or observed. Each row says what the mistake is,
where it shows up, how to recognise it, why it hurts, how to fix it, and how to check the fix.
The goal is not to know every best practice; it is to stop repeating a known failure.

The log is deliberately short. A row earns its place by being specific, reproducible and
checkable. A hundred vague rows are worse than ten sharp ones.

---

## What this is not

- It is not a style guide or a linter. It does not block work.
- It is not a generic best-practice dump. If nobody made the mistake, it does not belong.
- It is not a replacement for the project's own docs, decisions or `AGENTS.md`.
- It is not a place to win arguments. It is a memory aid.

---

## Commands

| Command | What happens |
|---|---|
| `/mistakes` | Audit the whole project against every active row: report confirmed findings, then fix only the safe ones |
| `/mistakes <id>` | Audit for one row, e.g. `/mistakes mixed-type-field` |
| `/mistakes <keyword>` | Audit rows whose `id`, `mistake` or `tags` match the keyword |
| `/mistakes <path>` | Audit one directory or file, e.g. `/mistakes src/api` |
| `/mistakes add <description>` | Propose a new row from the description; append it after confirmation |

With no argument, the default is a full audit of the current repository. Filters combine:
`/mistakes mixed-type-field src/api` audits one row in one path.

---

## Files

| File | Owns |
|---|---|
| `SKILL.md` | How to load, apply, verify and record mistakes |
| `data.csv` | The log itself: one row per mistake |

**Why CSV, not JSON.** Each lesson is a flat record with the same fields. CSV is easy to append,
diff, review in a pull request, and filter with a search tool or a spreadsheet. JSON would nest
prose and make the log harder to scan; use it only if a row ever needs structured sub-records.

---

## The data file

```
id,category,mistake,where,signal,why,fix,check,scope,tags,source,confidence,status,added
```

| Column | Meaning |
|---|---|
| `id` | Stable kebab-case identifier; never renamed after it is referenced |
| `category` | `data-modeling`, `api`, `state`, `security`, `testing`, `process`, `migration`, `ui`, `config` |
| `mistake` | One-line name of the failure |
| `where` | Surfaces where it shows up: `db`, `api`, `ui`, `form`, `state`, `tests`, `ci`, `docs` |
| `signal` | How to recognise it by eye or by a quick search |
| `why` | The concrete consequence, not a principle |
| `fix` | The correct pattern, specific enough to apply |
| `check` | A verification that can fail: grep, schema rule, query count, test |
| `scope` | Stack or domain; `*` for universal |
| `tags` | Search terms and synonyms |
| `source` | Where the lesson came from (`project`, `review`, `incident`, `seed:review`) |
| `confidence` | `confirmed` (seen/reproduced) or `suspected` (plausible, verify first) |
| `status` | `active` or `retired` |
| `added` | Date the row was added, `YYYY-MM-DD` |

---

## How to use

### 1. Load only what matches

Never paste the whole file into context. Filter by the task's surfaces, stack, category and
keywords, using whatever search tool is available (`rg`, `grep`, `Select-String`, a spreadsheet,
or the agent's own search tool):

```text
Filter by intent:
- data modeling or schema work   -> category is data-modeling or migration
- money, units, measurements     -> tags contain money, currency, unit, measure or price
- a specific stack               -> scope contains react and status is active
- the flagship example           -> id is mixed-type-field
- a phrase the user remembers    -> search mistake, signal and tags for their words
```

Match on `scope`, `where`, `category` and `tags`. Prefer exact matches; use fuzzy matches only
when they clearly apply.

### 2. Apply before the work

State the matched rows in one line each, then apply their `fix` while designing or coding:

```text
Matched mistakes (2):
- mixed-type-field — split money into price_amount + price_currency; never a formatted string.
- timezone-naive — store UTC instants; keep local timezone separately.
```

If nothing matches, say so in one line and continue. Do not force an unrelated lesson.

### 3. Verify after the work

For every applied row, run its `check`. Report which checks passed and which could not be run.
A check that cannot be run is stated honestly, not assumed.

### 4. Record a new mistake only when asked

Triggers: "remember this", "log this mistake", "add it to mistakes", "add to my mistakes",
"update your mistakes", `/mistakes add`.

Propose one row, show it in the schema, and append it after the user confirms. When the user
explicitly says "add it", appending is the confirmation.

```text
Proposed row:
id: nullable-boolean-consent
category: data-modeling
mistake: A boolean used where consent has three states
where: db; api; form
signal: has_consent is false for both "declined" and "never asked"
why: Cannot distinguish refusal from absence; compliance reports are wrong
fix: Nullable boolean with documented semantics, or an explicit tri-state enum plus timestamp
check: A "not asked" fixture behaves differently from a "no" fixture
scope: *
tags: consent;boolean;tristate;compliance
source: user
confidence: confirmed
status: active
added: 2026-11-09
```

### 5. Audit the project (`/mistakes`)

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

#### Fix safety

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

#### Audit report format

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

---

## Matching rules

1. **Exact before fuzzy.** A row tagged `react` does not apply to a Vue project.
2. **Zero matches is a valid result.** Do not invent relevance.
3. **`suspected` is a warning, not a rule.** Verify before using it to block or rewrite.
4. **`retired` never applies.** It stays in the file for history, not for use.
5. **Project docs win.** If `AGENTS.md`, a decision record or the user explicitly chooses the
   other path, state the conflict once, cite the row `id`, and comply. Do not silently override.
6. **Fewer, stronger matches.** Five rows is usually too many; one to three is the norm.

### Precedence

1. The user's explicit instruction in this session.
2. The project's documented decisions and constraints.
3. This log.
4. Generic best practice.

If the log and the project disagree, the log loses, but the disagreement is worth one sentence
because it may reveal a real exception.

---

## Adding a row

A row is admissible only if all of these are true:

- **It actually happened.** A real codebase, review, incident or reproduction. Not "someone
  might".
- **It is one lesson.** Do not bundle three fixes into one row.
- **The signal is observable.** A reader can find it with a search, a schema look, or a test.
- **The fix is applicable.** Not "be careful"; a concrete pattern.
- **The check can fail.** If it always passes, it is not a check.
- **The id is stable and unique.** Kebab-case, descriptive, never reused.

Merge duplicates instead of adding near-copies. If a row is wrong, set `status=retired` and say
why in the conversation; do not delete history.

### Weak vs strong

| Weak | Strong |
|---|---|
| "Use best practices for money" | "Store `price_amount` as integer minor units + `price_currency` as ISO 4217; format only in the UI" |
| "Be careful with timezones" | "Store UTC instants; keep the IANA timezone separately; test a DST boundary" |
| "Tests are flaky" | "A retry hides a race; reproduce with parallelism and fix the shared state" |
| "Validate input" | "Validate at the server boundary with the same schema the client uses" |
| "Don't duplicate state" | "One owner; derive the rest; a test mutates the source and observes every consumer" |

### Do not add

- Style preferences ("use tabs").
- Framework fashion ("always use X").
- Anything the project has explicitly decided otherwise.
- A mistake that only exists in theory.
- A row without a `check`.

---

## Worked example — the flagship row

The pattern behind `mixed-type-field`: **if a value encodes more than one primitive, split it.**

Money is the common case:

```text
Bad:  price = "$12.50"        price = "12 USD"       price = 12
Good: price_amount = 1250     price_currency = USD
```

The same test applies to anything with a value and a unit or a second dimension:

| Composite value | Split into |
|---|---|
| Money | `amount` (integer minor units or decimal) + `currency` (ISO 4217) |
| Duration | `value` + `unit` (`ms`, `s`, `min`, `h`) |
| Distance / weight | `value` + `unit`, canonical at storage |
| Temperature | `value` + `unit` (`C`, `F`, `K`) |
| Range | `min` + `max` (and inclusivity if it matters) |
| Phone | `e164` + optional `extension` |
| Address | `line1`, `line2`, `locality`, `region`, `postcode`, `country` |
| Person name | `display_name` + optional `given_name` / `family_name` |
| Geo point | `latitude` + `longitude` (and precision if needed) |
| Percentage | `ratio` (0–1) or `basis_points`, never an ambiguous `5` |

Formatting belongs at the presentation layer. Parsing belongs at the boundary. Storage stays
atomic.

---

## Maintenance

- Keep the log small. Prune rows that no longer teach anything.
- Merge duplicates and keep the older `id` as the canonical one.
- Re-verify `suspected` rows before promoting them.
- Retire, never delete, a row that turned out to be wrong.
- Update `added` only when the row is created; use the conversation for later notes.

---

## Triggers

| The user says | The skill does |
|---|---|
| `/mistakes`, "mistakes", "check my mistakes", "audit for mistakes" | Run a full audit: probe the repo for every active row, report confirmed findings, fix tier A only |
| `/mistakes <id, keyword or path>` | Run the same audit limited to that row, keyword or path |
| "avoid this", "don't repeat this" | Match the current task, apply the relevant rows, verify |
| "remember this mistake", "log it", "add to my mistakes" | Propose a row, append after confirmation |
| "I told you before" | Search `id`, `mistake`, `tags`, and the conversation for the lesson |
| "we already fixed this" | Find the row and its `check`; confirm the check still passes |
| Nothing, but the task touches data/API/auth/state/tests | Silently match and apply the relevant rows, stating them in one line |
