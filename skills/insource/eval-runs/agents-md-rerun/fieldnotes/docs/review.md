# Named Review Tasks - Full Definitions

The always-first pass (hunt AGENTS.md/golden-rule violations, in code AND docs) and the one-line
task index live in AGENTS.md section 19; the full bodies live here.

## Docs
- Read the entire `docs/` set end to end, plus every doc AGENTS.md routes to.
- Violations: stale passages contradicting current code; docs nothing links to (an orphan the
  routing chain cannot reach); any single doc over 500 lines - it becomes a folder named after the
  doc, split one concern per file, with `index.md` as its local map.
- Fix or report each finding in the same change; a report is not deferred.

## DB
- Learn every table in the SQLite database (schema, row counts, who writes each).
- Violations: hardcoded or mocked data in code that the tables could answer - literals, fixture
  lists, faked currency tables - judged against AGENTS.md section 18. Seeds, not a quota.
