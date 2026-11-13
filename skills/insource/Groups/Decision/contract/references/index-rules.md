# index.md — the contract directory's constitution

`index.md` is the only file every contract depends on: it defines which layers exist and
enumerates which contracts exist. A contract referencing an undefined layer, or an existing
contract missing from the index, is a `check` finding by construction.

## Required shape (template: `assets/index-template.md`)

1. **Title** — `{Project} Contracts`.
2. **Short description** — 1–3 sentences: this collection documents responsibility ownership
   across the layers below; every cross-layer responsibility has exactly one contract.
3. **`## Layers`** — one bullet per layer: number, name, one-line scope. Default numbering is
   frozen: 0 Database, 1 Backend, 2 Frontend. Extra layers get the next numbers (3, 4…) and
   must describe a real, distinct layer in this architecture — not an aspiration. If the
   project has no frontend (a CLI, a batch system), the Layers section says what exists; the
   defaults are a starting vocabulary, not a mandate.
4. **`## Documents`** — one bullet per contract, title + one-line description, matching each
   file's H1 and Description closely enough to identify relevance without opening it.

## Sync rules

- Creating a contract → add its Documents entry in the same pass. Same for update (summary
  follows the change) and removal (entry dies with the file).
- A contract's `Ownership` may name only layers defined here; `check` verifies against the
  Layers section, case-insensitively on names, exactly on numbers.
- No duplicate responsibilities: before adding an entry, search existing Descriptions for
  overlap — narrower scenario gets a References link to the general one, not a rewrite.
- Sort Documents alphabetically by title; the index is a lookup table, not a history.
- The index lists, it does not decide: no ownership language belongs in the Layers bullets.