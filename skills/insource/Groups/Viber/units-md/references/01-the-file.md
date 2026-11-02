# The file

Shape, fields, and how to survive contact with an existing project's conventions.

## Why one heading per unit

The canonical form is a Markdown section per unit (`### U-007: Cart pricing rules`) with bold-labelled fields,
grouped under `##` area headings — not one giant table row per unit. Reasons that matter later:

- **Diffable.** One unit changed → one hunk. A table row edit rewraps the whole table and buries the change.
- **Greppable and quotable.** A commit message or a postmortem can cite `U-007` and a reader lands on exactly one
  block.
- **Fields can breathe.** "Reuse instead of" often needs a clause; a table cell punishes that.
- **Order is stable.** Entries stay where they were; ids never shift.

A compact table is fine as a *summary above* the entries (id, name, path), if the project wants a scannable
index. It is not the record.

## Fields

| Field | Required | What it prevents |
|---|---|---|
| **Purpose** | yes | one line, the responsibility. "Various HTTP helpers" prevents nothing |
| **Where** | yes | the project-root-relative path (or a few, comma-separated) that exists today. `src/net/http.py`, not `http stuff` and not `C:\repo\...` |
| **Status** | yes | one of `active`, `deprecated`, `experimental`, `pending`, `unknown` |
| **Verified** | yes | the ISO date this claim was last checked against the code |
| **Depends on** | optional | unit ids, not free text. Makes the graph checkable and cycles visible |
| **Used by** | optional | when it is not obvious that a unit is load-bearing |
| **Reuse instead of** | optional | the parallel implementations this unit replaces — the field that stops duplication |
| **Owner** | optional | who updates the row, when that is not "whoever changes the code" |
| **Notes** | optional | constraints, gotchas, "single instance assumed", "do not call from request path" |

Rules that keep those fields honest:

- **No path, no row.** If you cannot point at a file that exists, the unit is not in the index — it is `pending`,
  in the report, not in the file.
- **No undated claims.** `Verified` is a date. An entry copied from a document that may be stale inherits the
  document's uncertainty, so it gets re-checked or it gets `unknown`.
- **The entry is a pointer, not an essay.** Past ~30 lines, the detail belongs in the unit's own README or doc;
  the index links to it.

## Ids, ordering, grouping

- Ids are `U-001`, `U-002`, … monotonic per file. Never renumber, never reuse a retired id, never alphabetize by
  name (that shuffles every cross-reference on every rename).
- Group under `##` area headings that match the project's own vocabulary (features, layers, packages, bounded
  contexts). Inside a group, order by first use in a typical reading path, then keep it stable.
- New units get the next free id and land in their group. A deprecated unit keeps its id and its place, with the
  pointer to its replacement — history is what makes the index trustworthy.

## Status vocabulary

| Status | Meaning | What it obligates |
|---|---|---|
| `active` | the implementation the project routes through | extend it rather than building a second |
| `deprecated` | kept for references, must not be used for new work | name the replacement in the row |
| `experimental` | real code, unresolved contract | say what would make it `active` |
| `pending` | decided but not built yet | do not list as a unit; keep it in the report until the path exists |
| `unknown` | exists, but its contract was not verified | re-check before relying on it |

`units_lint.py` rejects values outside this set, because a bespoke vocabulary ("shipped", "stable-ish") is how an
index stops being machine-checkable.

## Size budget

Soft 400 lines, hard 1200; one entry ≤ 30 lines. An index that exceeds the budget is being read by nobody, and
an unread index is worse than none — it teaches agents that pointers can be ignored. Split by package, or narrow
the scope and say so in the header.

## The four duties (the header is the contract)

The file's opening section states the duties `AGENTS.md` §4 relies on. Without them the file is a list, not a rule:

1. **Read in full before implementing or planning.** Not "skim", not "search". An index read partially is an index
   ignored.
2. **Reuse or extend.** If a unit covers or partly covers the need, use it. Building a parallel component requires
   stating the reason in the change — that sentence is what makes duplication visible in review.
3. **Add new units in the same task.** A reusable unit created by a change has its entry in that same change. Not
   as a follow-up: a follow-up is a different day, a different context, and a different owner, and it will not
   happen.
4. **Named owner for the update.** Who edits the file when a unit moves — usually whoever changes the code; for
   delegated work, the master agent merges the row a worker reports, so two workers never fight over one file.

## Merging into a convention that already exists

The project's existing format outranks this document. Adapt, do not reformat:

| Incumbent form | How to work with it |
|---|---|
| A single Markdown table | keep the table as the summary; if entries need prose, propose the heading-per-unit form as a change the user agrees to — with the table's ids preserved |
| A machine-readable catalog ([JSON], YAML, CSV) with a generated Markdown view | edit the source of truth, regenerate, and point `Where` checks at the source file |
| One file per unit under `units/` with an index at `docs/UNITS.md` | the index carries id, name, purpose, path to the doc, status; the per-unit files keep the detail |
| Code-owner or `CODEOWNERS`-style registry | owners already live there — reference them, do not duplicate them |
| ADR folder | decisions belong there; a unit row links to the ADR that explains the boundary |
| Something vague ("see the docs") | resolve it to a path or mark it `unknown`; a pointer that cannot be checked is not an index entry |

Never create a second competing units file, never renumber what exists, and never silently delete an entry you
disagree with — report it.
