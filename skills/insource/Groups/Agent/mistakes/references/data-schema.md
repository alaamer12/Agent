# The data file: schema, rationale, and how to query it

The log itself is `data.csv`. This is the format rationale, the column
contract, and the intent-to-filter mapping used when loading rows.

## The format

**Why CSV, not JSON.** Each lesson is a flat record with the same fields. CSV is easy to append,
diff, review in a pull request, and filter with a search tool or a spreadsheet. JSON would nest
prose and make the log harder to scan; use it only if a row ever needs structured sub-records.

## The columns

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

## Filtering by intent

```text
Filter by intent:
- data modeling or schema work   -> category is data-modeling or migration
- money, units, measurements     -> tags contain money, currency, unit, measure or price
- a specific stack               -> scope contains react and status is active
- the flagship example           -> id is mixed-type-field
- a phrase the user remembers    -> search mistake, signal and tags for their words
```
