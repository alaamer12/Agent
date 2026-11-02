# What a unit is

> **Illustrative, not exhaustive.** The shapes below are examples to reason from. A project's real boundary is
> whatever its developers would look for before writing code — that, not the list, is the test.

## The three-part test

A thing is a unit when **all three** hold:

1. **Looked-for first.** Someone starting related work would check whether it exists before building it.
2. **Pointable.** Its boundary is a path (or a small set of paths) in the repository — the `Where` field resolves.
3. **Nameable in one line.** Its responsibility fits one sentence without the words "various", "misc", "helpers",
   or "everything related to".

Two out of three is not a unit; it is a folder, a dependency, or a paragraph of documentation.

## Shapes units take

| Kind of project | What typically counts as a unit |
|---|---|
| Web front end | a shared component ([button, data grid, modal shell]), a state/store slice, a route guard, a form-binding layer, the API client, the theme token source |
| Mobile ([React Native], [Flutter], native) | a screen or feature module, a navigation registry, a device-capability wrapper, an offline sync unit, a design-token mapper |
| Backend service | a use case / interactor, a domain rule module (pricing, eligibility), a repository or data-access unit, an outbound integration client, an auth/session unit, a queue consumer, a scheduled job |
| Data platform | a schema or model group, a source-to-target pipeline stage, a transformation library, a lineage or seed-data utility, the migration mechanism (not each migration) |
| CLI or library | each command, the public API surface module, the config loader, the output/formatting layer, the plugin/extension point |
| Desktop ([.NET], [Qt], [Electron]) | a window/view model, a platform-bridge unit, a settings store, an update mechanism, a licensing check |
| [Rust], [Go], [Java] systems | a crate/module with a stated contract, an internal package that others import, a transport adapter, a metrics/health unit |
| Infra and deployment | a module per deployable surface, the naming/tagging convention unit, a secret-access unit, an environment factory |
| Cross-cutting | retry and timeout policy, error mapping, logging setup, feature-flag registry, clock/id providers, the shared test harness and fixtures |

The same responsibility in different stacks is still one unit per project: `Where` points at the file, not at the
idea.

## What is not a unit

| Not a unit | Why | Where it belongs |
|---|---|---|
| A third-party dependency ([requests], a UI kit, a DB driver) | you do not own it, and `import x` is self-documenting | the manifest |
| A framework primitive or language feature | nothing to reuse-decide about | the docs, at most |
| A folder, layer, or directory name | a location is not a responsibility | nothing — folders are not listed |
| Generated code, build output, vendored trees | regenerated, not reusable decisions | excluded, and stated as excluded |
| A single private function inside a unit | too small; nobody searches for it | the unit's own file |
| A one-off script run twice | not reusable until it has been needed a third time | propose promoting it, then list it |
| A DTO, type alias, or constant alone | no behavior; part of the unit that owns it | inside that unit's entry |
| Tests, unless they are a shared harness | a test file tests, it does not serve | "shared test harness" as one unit |
| A plan, spec, or ADR | documentation, not something to call | the project's docs |
| A task, ticket, or work item | the index is not a backlog | the tracker |

## Granularity

The file fails in two opposite directions:

- **Too coarse** ("Everything about payments in `src/payments/`") → the index hides what exists, so the next
  contributor builds a second discount calculation next to the first. Split when the contents change for
  **different reasons**: an adapter, a rules module and a persistence unit are three rows even in one folder.
- **Too fine** (one row per function) → nobody reads past page two, so nobody reads it at all. Merge when things
  are **always used together, have one owner, and change together**.

Useful targets:

- a row earns its place only if a searcher would thank you for it;
- if a name has to say "and" twice, it is two units;
- a file exporting a dozen unrelated things is a dumping ground: list the real sub-units you can point at, and
  record the split as a finding rather than pretending the folder is one unit;
- the whole index should be readable in one sitting. For a large monorepo, scope it to the packages work actually
  touches and say so in the header — a partial honest index beats a complete one nobody opens.

## Naming

Name the **responsibility**, not the location: "Cart pricing rules", not `rules.py`; "Session store", not
"auth folder". Names drawn from `utils`, `helpers`, `common`, `misc`, `core`, `shared`, `base` describe a bucket,
not a boundary — `units_lint.py --strict` flags those when they span more than one path, because a bucket is
exactly where parallel implementations hide.

## What to exclude, and how to say so

Vendored dependencies, generated files, build output, caches, fixtures and sample data, and (usually) migration
history. Record the exclusion in the header line — "Generated client code and `vendor/` are out of scope" — so a
later reader knows the index is deliberately narrow rather than accidentally incomplete.

## When the boundary is contested

Some projects disagree about what counts as reusable (is every screen a unit, or only the shared ones?). Do not
settle it alone: show the two candidate lists, ask which the team would search, and write down the answer in the
header. The index is only useful if it matches how the team works — the file records the convention, it does not
invent one.
