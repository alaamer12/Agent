# Worked example: a root README acting as a map

This is a real example of a root-level README doing its job well. Read it for what it's *doing*, not for its exact sections — your project's README should take whatever shape actually helps a reader navigate it, which may look nothing like this.

```markdown
# Mostaqlk

A Windows desktop app that watches [mostaql.com/projects](https://mostaql.com/projects) — the open-projects feed of Mostaql — and alerts the user within roughly a minute of a new project being posted, storing full project details locally for offline, searchable, permanent reference.

This is a wiki-style documentation set. Each concern has one home; other docs link to it rather than repeating it.

## Documents

| Doc | What it answers |
|---|---|
| [`system-components.md`](../system-components.md) | **Architecture map.** All major components, their purposes, boundaries, relationships, and implementation locations |
| [`MVP.md`](../../v1/product/README.md) | **Start here for build.** What actually ships first — parser/pipeline + storage + notifications only |
| [`diff-engine.md`](../../v1/tech/diff-engine.md) | The reusable compare abstraction — local scrape-vs-DB today, mobile peer-sync later |
| [`concurrency-model.md`](../../v1/tech/concurrency-model.md) | Thread-safe in-flight tracking, transaction boundaries, crash/restart behavior |
| [`worker-pool-and-rate-limiter.md`](../../v1/tech/worker-pool-and-rate-limiter.md) | Queue, worker pool, shared token-bucket rate limiter — with C# implementation |
| [`error-handling-and-resilience.md`](../../v1/tech/error-handling-and-resilience.md) | Failure handling per pipeline stage, retry/backoff policy |
| [`overview.md`](overview.md) | What is this, why does it exist, what ships in each version (MVP / v2 / v3) |
| [`architecture-pipeline.md`](architecture-pipeline.md) | How polling, the discovery queue, worker pool, and rate limiting actually work — including the concurrency race condition and its fix |
| [`data-model-schema.md`](data-model-schema.md) | The full embedded-DB schema: projects, owners, skills, assets, search index |
| [`configuration-reference.md`](../../v1/product/configuration-reference.md) | Every user-facing setting, its default, and its effect |
| [`ui-ux-design.md`](../../v1/product/ui-ux-design.md) | Window layout, tray behavior, unread highlighting, toast design |
| [`DESIGN.md`](DESIGN.md) | Visual design system — colors, light/dark theme, RTL, typography, icons, component base |
| [`search-and-filtering.md`](../../v2/product/search-and-filtering.md) | The dynamic query builder, sort options, fuzzy Arabic/English search, and the storage-engine decision behind it |
| [`roadmap-future.md`](../../v2/product/roadmap-future.md) | v3 stretch goals: mobile companion, LAN peer sync, FCM/APNs push |

## Quick facts

- **Platform:** Windows desktop app, tray-resident. Stack is likely C#/.NET MAUI for cross-platform reach (supersedes earlier Tauri/Rust references in [architecture-pipeline.md](architecture-pipeline.md) — read that doc's code-adjacent details as conceptual; [worker-pool-and-rate-limiter.md](../../v1/tech/worker-pool-and-rate-limiter.md) and [concurrency-model.md](../../v1/tech/concurrency-model.md) reflect the current C# direction)
- **Storage:** embedded single-file DB (SQLite or SQLite-compatible), no server, no cloud dependency in MVP/v2
- **Request budget:** configurable, default ~2 requests/minute against mostaql.com
- **Data policy:** [store-and-forget](architecture-pipeline.md#no-update-policy) — a project is scraped once and never re-fetched or updated
- **Language support:** Arabic-first (source site is Arabic), with English handled equally in [search](../../v2/product/search-and-filtering.md)

## Version scope at a glance

- **v1 (MVP):** poll → discover → enrich → store → notify → tray + window. See [overview.md § MVP](overview.md#v1-mvp-scope)
- **v2:** `query_params` override, `include_assets`, notification grouping, unread highlighting, full query builder + search. See [overview.md § v2](overview.md#v2-scope)
- **v3 (stretch):** mobile companion app, LAN pairing, two-way sync, push notifications. See [roadmap-future.md](../../v2/product/roadmap-future.md)
```

## What makes this work

- **The doc table is the whole point.** One row per file, and the second column answers "what question does this file answer" rather than restating the filename. A reader scans this table, not the files, to find where something lives.
- **Nothing here re-explains what's in the linked files.** The "Quick facts" section states facts, it doesn't summarize any linked doc's reasoning — if you wanted the reasoning behind the storage choice, you'd follow the link, not find a paraphrase of it here.
- **It states its own rule out loud:** *"This is a wiki-style documentation set. Each concern has one home; other docs link to it rather than repeating it."* That sentence is doing real work — it tells every future contributor (human or AI) the norm to maintain, not just describes the current state.
- **It admits drift honestly** rather than hiding it — the note about the C#/.NET MAUI stack superseding earlier Tauri/Rust references, with an explicit pointer to which docs are now stale in their code-level detail. A map that pretends everything is current when it isn't stops being trustworthy.
- **Cross-directory links work like a real map**, not just links within one folder — because this README's job is to orient the reader across the *whole* doc set, not just its own directory.

## What to adapt, not copy

Your project may not need a "Quick facts" section, may not have distinct versions, may have five files instead of fourteen. The structural moves worth keeping are:
1. A one-line project description at the top.
2. An explicit statement of the no-duplication norm, if the doc set is large enough that contributors might forget it.
3. A scannable index where the second column (or line) is "what this answers," not "what this is called."
4. Honesty about anything stale or in-flux, rather than silence.

A directory with three files and an obvious reading order might just need a short paragraph and a numbered list — building a table for three items is over-structuring.

## A second example: scope layering + flat vs. directory

A real project's `.steering/` tree looked like this:

```
.steering/
├── base/
│   ├── product/README.md
│   └── tech/README.md
├── v1/
│   ├── product/README.md
│   └── tech/README.md
├── v2/
│   ├── product/
│   └── tech/
└── structure.md
```

Two conventions from Step 4 of the main skill are visible here at once:

- **`base/` vs `v1/`/`v2/`** — `base/` holds whatever is true regardless of version (architecture, core conventions) and is meant to always be read; `v1/` and `v2/` hold version-scoped content, and the project's own agent instructions are explicit that `v2/` should be ignored while v1 is current. The directory boundary *is* the "always read this / only read this if relevant" signal — no need to say it in prose inside every file, the structure says it.
- **`structure.md` stayed flat.** It sits directly under `.steering/` rather than becoming `structure/{README.md, structure.md}` — there wasn't enough content in it to need its own local map, so it didn't get one. Compare that to `tech/` and `product/`, which *did* get directories (with their own `README.md`) because each covers enough distinct concerns to need an index.

The lesson isn't "always name things `base`/`v1`/`v2`" — it's that when a project actually has a permanent layer and scoped layers, making that structural rather than relying on a reader to remember which doc is current is worth the extra directory, while a single-concern doc like `structure.md` isn't worth one.

## A third example: the document's own opening contract

Every document produced by this skill — not just README/index files — should open with a short contract right under its title. A real example, the opening of a document applying a project's SQL conventions to its specific schema:

```markdown
# Table Reference: Normalization and SQL Conventions

> This document applies the normalization principles (3NF+) and SQL conventions (`docs/sql-conventions.md`) specifically to every table in MostaqlK's schema.
> For each table: purpose → functional dependencies → normalization proof → DDL → column reference → canonical queries.
```

Two things are happening in these two lines, and both matter:

- **It mentions the document it's built on, without re-explaining it.** This document applies conventions from `docs/sql-conventions.md` — it doesn't restate what 3NF means or repeat the SQL naming rules, it just says "here's where those come from" and links. A reader who already knows the conventions skips straight to the tables; a reader who doesn't knows exactly where to go first. This is the mentioning-not-explaining principle applied to a document's very first lines, where it matters most — before the reader has invested any time, they already know whether they're missing a prerequisite.
- **It states its own internal shape.** "For each table: purpose → FD → normalization proof → DDL → columns → queries" tells the reader what pattern repeats through the rest of the document, so they're not surprised by the structure and can jump straight to the section they need (e.g. "I just want the DDL for `projects`") instead of reading linearly to find out how the document is organized.

Not every document needs both lines — a document with no real prerequisite doesn't need to invent one, and a document with no repeating internal structure doesn't need to describe one. But the "what is this and what does it assume" half is worth including almost always; it's the difference between a reader discovering a document's relationship to the rest of the set by trial and error versus being told outright in the first two lines.
