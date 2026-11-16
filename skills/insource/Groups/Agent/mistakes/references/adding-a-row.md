# Adding a row

The admissibility gate, the weak/strong calibration table, the excluded
kinds, and the exact shape of a proposed row. Read this before appending
anything to `data.csv`.

## Admissibility

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

## Proposed row format

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
