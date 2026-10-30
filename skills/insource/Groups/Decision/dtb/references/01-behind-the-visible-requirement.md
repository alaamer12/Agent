# Behind the visible requirement

The requirement is a symptom of a complete problem. Your job is to solve the problem, not to tick the sentence
off — and the user should never have to name an internal system for it to exist.

```text
"I need search."
   ↓ the sentence is one component; the outcome is a behavior that holds every time
   ↓
what must be true for that sentence to work in THIS product, on the user's real data, at 3 a.m.?
```

## Step 1 — restate the ask as an outcome

Write one sentence about the user's result, not the feature. If the sentence is a paraphrase of the request,
you have not gone deep enough.

| Typed requirement | Weak restatement | Outcome restatement |
|---|---|---|
| "add search" | a box that filters the list | a visitor finds the right item in under two seconds from a partial, misspelled, or over-specific query — and gets a useful answer when nothing matches |
| "show a chart of revenue" | draw a line chart | the reader can tell whether this month is up, and drill into what caused it, on a phone, with their own currency and month boundaries |
| "let users export CSV" | dump rows to a file | a manager can take the export into Excel and get the columns, ordering, numbers and totals they expect, for a range that may be large |
| "add a webhook" | POST to a URL when things happen | deliveries arrive once, in order-ish, and a partner's outage does not lose events or block our queue |

Each outcome sentence immediately names systems the typed sentence hid: the search row implies tokenizing,
ranking, filters, empty-state behavior, and a data route; the CSV row implies column contracts, locale and
number formats, and a size limit.

## Step 2 — enumerate, then prune with the relevance test

Enumerate the systems that could stand behind the outcome — **then cut the list**. The catalog below is
illustrative, never a checklist to satisfy.

| System | It exists to answer | Visible symptom when it is missing |
|---|---|---|
| indexing | how do we find things fast without scanning everything | slow at 10 k rows; timeout at 1 M |
| filtering | how does the user narrow without re-searching | chips do nothing; combined filters produce nonsense |
| sorting / ranking | which of the matches comes first | exact matches buried under popular ones; "best" looks random |
| matching / scoring | what counts as a hit (synonyms, typos, language, stemming) | "color" finds nothing for "colour"; one typo empties the page |
| data collection / ingestion | where the searchable data comes from and how fresh it is | results silently miss new items |
| processing / normalization | what shape the data is in when compared | accents, units, dates and casing fragment every query |
| caching | what is expensive to recompute per request | every keystroke is a full scan |
| pagination / streaming | what happens when there are many results | a 40 MB response; a spinner for nine seconds |
| observability of the engine | do we know when it silently degrades | it has been broken since the schema change and nobody saw |

A system belongs **only if a present requirement breaks without it.** Three questions, and one "yes" is enough
to keep it:

1. **Behavior:** does the feature behave *wrong* — not just slower — without it, on the data this product
   actually has?
2. **Surface:** does a failure here show up on a screen the user can see? (If yes, it needs an empty/error
   state in the approved style, not a stack trace.)
3. **Dependence:** does another required feature quietly consume it? (Export consumes the same filters;
   recommendations consume the index.)

Everything else is a **finding**, not a task. Write it down, say it in one line, move on: *"typo-tolerance
would help, nothing in the current data needs it yet — noted, not built."* Building unneeded machinery is
scope creep in a quality costume ([`00`](00-the-authority-line.md), §"Improvement-shaped scope creep").

## Step 3 — size it by this product, not by the idea of the feature

The same ask justifies wildly different machinery. Read the actual numbers before choosing — a table count, a
payload size, a query you can time — and let the measurement pick the tier.

```bash
# cheap sizing, any stack: how big is the data that must be searched?
python - <<'PY'
import sqlite3; c=sqlite3.connect("app.db")
print(c.execute("select count(*), max(length(title)) from items").fetchone())
PY
```

| True here | Consequence |
|---|---|
| hundreds of rows, single user | in-process filter is the *correct* engineering answer; an external search service would be a defect |
| tens of thousands, reads dominate | a local index (e.g. [SQLite FTS5], [Postgres] `tsvector`, an in-memory inverted index) with a rebuild-on-write path |
| millions, or multi-node | a dedicated engine becomes the honest requirement, and its operational cost is part of the decision to surface to the user |
| one language, plain words | naive normalization is fine |
| several languages, accented text, compound words | normalization/tokenization stop being optional — this is a *behavior* difference, not a polish one |
| the data changes under the user | freshness is a requirement: define when results stop being stale |
| mobile, or flaky network | payload size and retry behavior are part of the feature |

Sketch of the pipeline shape that survives any tier — swap the engine, keep the stages:

```text
collect → normalize/tokenize → index → query(parse+validate) → rank → hydrate → page
                                       ↓
                            (empty / error / no-match → a state the design already has)
```

Each arrow is a decision boundary. In [Postgres] the index may be a generated column plus a GIN index; in
[SQLite] an FTS virtual table; in a [Python] service an in-memory dict built at startup; in a [JS] front end a
client-side index over a fetched payload. **None of these is "the" answer** — the answer is whichever tier the
measured data forces, with the seams in the same place so the tier can change later.

## Step 4 — the prototype's unwritten behaviors

When the input is a design, the visible screens define the intended experience and you define what makes it
coherent. A prototype never draws these, and their absence is not a requirement:

- **Empty** (no data at all) and **no-results** (data exists, this query found none) are *different* states with
  different jobs; both need to exist in the design's voice.
- **Loading** — first paint, and a slow subsequent query; the skeleton should match the layout, not shift it.
- **Error** and **offline** — say what failed and what the user can still do.
- **Partial success** — a query that works but whose enrichment failed: degraded results beat an error screen,
  but the user should not be lied to.
- **Permission and empty-by-privacy** — the same screen, different message.
- **Boundaries** — 0 results, 1 result, 10,000 results; one page, one very long title, an emoji or RTL string.

Do all of this **inside** the approved direction: same type, spacing, tone, and components. The design tells
you what the product looks like when it works; you decide what it looks like when it doesn't, and that answer
is what makes it feel professional or amateur.

## The bar

Not *"does it work?"* but:

> **Is this the best appropriate way to make the complete feature work — for this data, at this size, in this
> product, with this team maintaining it?**

Choosing among the answers you just enumerated is [`02`](02-what-is-the-best-way.md).
