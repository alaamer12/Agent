---
name: contract
description: 'Documents who owns what across architectural layers as tiny, precise contract files in <docs>/contract/: one responsibility per file, ownership either OoU (exactly one layer owns it) or AoU (all defined layers share it — never dual), with the reason and trade-offs recorded as a durable micro-decision. Use when the user asks where a responsibility belongs ("where should filtering/validation/retries/caching happen", "who owns X", "should the frontend or backend do this"), asks to write, update, list, or check a contract, runs /contract, or when implementing would silently scatter the same logic across layers; also when a scenario needs an explicit exception to an existing rule (hot-path vs default). Layers default to Database(0), Backend(1), Frontend(2), extensible per project; "application-side" always means Backend or Frontend, not Backend alone. Not for full architecture documentation (architecture), goals and priorities (commitments-md), vocabulary (glossary-md), or general prose documents (document).'
when_to_use: A cross-layer responsibility is being decided (filtering, retry, validation, authorization, caching, formatting), a decision contradicts or extends an existing contract, or the user types /contract.
argument-hint: "[list|new <responsibility>|update <file>|check]"
---

# contract — responsibility ownership, written down

A contract is a **micro-decision document**: one responsibility, its owner, its reason. Ten to
twenty lines, no essays. The point is that the next human or agent touching that code finds the
decision already made, knows *why*, and cannot silently contradict it.

## The model

| layer | default | number |
|---|---|---|
| Database | the data layer | 0 |
| Backend | application-side | 1 |
| Frontend | application-side | 2 |

Three layers suffice even for large systems; add layers only when the project's actual
architecture demands them, and define them in `index.md` first. **"Application-side" = Backend
or Frontend.** Ownership is exactly one of:

- **OoU — One Of Us:** one single layer owns the responsibility.
- **AoU — All Of Us:** every defined layer shares it.

**Dual ownership is illegal**: a responsibility either belongs to one layer or to all of them —
never "mostly backend, sometimes frontend" inside one contract. When two scenarios genuinely
want different owners, that is two contracts with a `References` link, not one mushy contract.

## Where it lives

`<docs>/contract/` — the `contract` directory sits inside the project's docs root, wherever
that is (detect: AGENTS.md convention, existing `docs/`, `documentation/`; if none exists,
`docs/contract/` and say so once). Contents: `index.md` plus one file per contract. There is
never more than one `contract/` directory per project.

## Read the right reference before you act

| when | load |
|---|---|
| deciding or recording an ownership choice | `references/ownership.md` — the decision method and trade-off axes |
| writing or renaming a contract file | `references/anatomy.md` — naming law, file structure, template |
| touching `index.md` | `references/index-rules.md` — layers section, sync rules |
| seeing a whole set in context | `examples/contract-set/` — index, default rule, exception, AoU protocol, and the retry pair that must never co-own |

## Commands

| command | does |
|---|---|
| `/contract list` | shows layers from index, then every contract: name, ownership, one-line description |
| `/contract new <responsibility>` | the full workflow below — search, decide, write, index |
| `/contract update <file>` | changes ownership/description **and** records why; keeps index summary in sync |
| `/contract check` | consistency audit, report-only: orphans (file not in index, or index entry missing), contracts referencing layers the index doesn't define, generic or layer-named filenames, overlapping Descriptions that belong merged, dual-ownership phrasing |

`check` findings are judgments about consistency, never re-litigations of ownership.

## Workflow for a new contract

1. **Read `index.md`** (create it from `assets/index-template.md` if absent — layers first,
   always).
2. **Search existing contracts** for an overlapping Description. Covered → link or update it;
   do not duplicate. A narrower scenario with a *different* owner → its own contract that
   `References` the default one, exception made explicit.
3. **Name the file** for the exact responsibility/scenario (`search_query_filtering.md`), never
   for a layer, never generic (`filtering.md` is banned). Snake case, descriptive.
4. **Decide ownership** with `references/ownership.md` — trade-offs per layer, project-specific,
   no universal answer; pick OoU or AoU and be able to say the reason in two sentences.
5. **Write** from `assets/contract-template.md`: Description (scope + exclusions), Ownership,
   Reason; add `References` / `How To Do It` only when they carry real weight.
6. **Update `index.md`** — every contract must appear in `Documents`. This is not optional;
   an unindexed contract does not exist.

## Hard rules

- Short beats complete: 10–20 lines where possible; lists and paragraphs, not new section
  headings beyond the template's two optional ones.
- Ownership belongs in the `Ownership` declaration only — a filename containing `backend`,
  `frontend`, or `database` is a naming violation even if the text is right.
- Contracts reference layers exactly as `index.md` numbers them, and reference other contracts
  by title with a one-line "why relevant" — never by copying their content.
- Reason is mandatory. An ownership decision without trade-offs recorded is a decision nobody
  can audit or extend safely.
- Never script the ownership choice itself; a script may check consistency, only an agent (or
  the human) decides who owns what.