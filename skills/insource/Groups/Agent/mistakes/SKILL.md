---
name: mistakes
version: 1.1.1
author: Amr
specialized: none
description: 'A personal, growing log of mistakes already made or observed, with where each one shows up and how to fix it. Use when the user says mistakes, check my mistakes, audit for mistakes, avoid this, remember this mistake, log a mistake, add to my mistakes, lessons learned, I told you before, we already fixed this, or before data modeling, API design, migrations, auth, state management, UI, tests, or configuration. Invoked as /mistakes it audits the project against the active log, reports confirmed findings with file and line evidence, fixes the safe ones (docs, comments, README, tests) and proposes the risky ones (schema, migrations, API contracts, auth, secrets) for approval instead of editing them. It also loads only the rows that match the current task, applies their fixes before the work, runs their checks after it, and appends a new row only when the user asks. Not a style guide, not a generic best-practice list, and never a silent override of the project own documented decisions.'
argument-hint: "[<id|keyword|path> | add <description>]"
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

`data.csv` is never skimmed or hand-read: its columns, the reason the log is CSV, and the
intent-to-filter mapping live in [`references/data-schema.md`](references/data-schema.md).

---

## How to use

### 1. Load only what matches

Never paste the whole file into context. Filter by the task's surfaces, stack, category and
keywords, using whatever search tool is available (`rg`, `grep`, `Select-String`, a spreadsheet,
or the agent's own search tool):

The five standard intents (schema work, money/units, a named stack, the flagship id, a phrase
the user remembers) are listed in [`references/data-schema.md`](references/data-schema.md).

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
explicitly says "add it", appending is the confirmation. The proposed-row shape, the admission
gate, the weak-vs-strong calibration and the do-not-add list:
[`references/adding-a-row.md`](references/adding-a-row.md).

### 5. Audit the project (`/mistakes`)

Read the active log, search the project for real instances of each pattern, report what is
confirmed, and fix only what is safe — the eight-step procedure, the A/B/C fix-safety tiers,
the hard rules and the report format: [`references/audit.md`](references/audit.md).

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

---

## Reference index

| File | Load when |
|---|---|
| `data-schema.md` | reading or writing `data.csv`: columns, format rationale, filter-by-intent |
| `audit.md` | any audit — the procedure, fix-safety tiers, hard rules, report format |
| `adding-a-row.md` | logging a mistake: admissibility gate, weak vs strong, do-not-add, row shape |
| `mixed-type-field.md` | composite values: the flagship pattern and the full split table |
