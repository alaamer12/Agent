# Contract anatomy — naming, structure, minimalism

## File naming law

Filename = the exact responsibility or scenario. Nothing else.

- **Specific, not generic:** `search_query_filtering.md`, `hot_path_filtering.md`,
  `automatic_retry.md`, `manual_retry.md` — never `filtering.md`, `retry.md`, `search.md`.
  Two words when one compound responsibility exists; the name should survive being opened in
  an editor tab next to thirty siblings.
- **Never a layer name:** no `backend`, `frontend`, `database` in a filename. Ownership lives
  in the `Ownership` declaration; a filename that pre-answers the decision makes the
  declaration decorative.
- **snake_case, `.md`**, one file per contract, all directly in `<docs>/contract/` — no
  subdirectories; the index is the organizer, not the folder tree.
- **Different scenario, different ownership ⇒ different contract.** Do not force unrelated
  scenarios together because they share a vocabulary word; the general concept is not the
  unit of responsibility.

## Structure (the whole file)

Exactly: one H1 title, then the declaration block, then optional sections. Template at
`assets/contract-template.md`.

```
# {Specific Contract Name}

- **Description:** {The responsibility precisely defined — its scope, and its exclusions
  when a near-neighbor could be confused with it ("excluding authorization checks…").}
- **Ownership:** {OoU | AoU} — {Responsible layer(s), named and numbered exactly as
  index.md defines them.}
- **Reason:** {Why this owner, which trade-offs decided it, what was paid; plus any
  condition under which the ownership is permitted (safety clauses live here).}
```

Optional, only when they carry weight:

```
## References

- {Title of another contract} — {one line: why it is relevant — the default this
  exception bends, the scope it hands data to, the decision it depends on}.

## How To Do It

{General implementation approach in plain language or pseudocode: steps, restrictions,
considerations. NOT a code listing, NOT syntax. It explains how to handle the
responsibility, not how to write this module.}
```

## Minimalism rules

- 10–20 lines where possible. If a contract needs more prose than that, the responsibility is
  too coarse — split it, or the extra content belongs in a real doc elsewhere, referenced in one
  line.
- No section headings beyond the two optional ones. Bullets and short paragraphs inside the
  declaration.
- No implementation detail that will rot: no function names, no file paths of code, no
  snippets. The contract outlives refactors precisely because nothing in it refers to code.
- No restating another contract's content — link it under References instead.
- The exclusions in Description are load-bearing: naming what this contract does NOT cover is
  what stops the next agent from stretching it to fit a new problem.