# Structuring conventions

Detail for Step 3 (design the target structure) and Step 4 (naming/granularity) of the main workflow. Read this once you're ready to actually design the target tree — not needed for Steps 1-2 (reading and concept-mapping).

## Core structural principles (Step 3)

- **One file, one concern, at full depth — everything else is a mention, not an explanation.** If your concept map found a file mixing N unrelated concerns, it becomes N files (or gets absorbed into N existing/new homes). Within its own concern, a file should go deep — a tech-implementation file should fully explain the tech; a product-facing file should fully explain the product behavior. Anything outside that file's concern (product/business context inside a tech doc, theory inside an implementation doc, marketing framing inside either) gets reduced to, at most, a one-line mention with a link — never a parallel mini-explanation. A useful test: could this sentence be replaced by a link without losing anything the reader needed from *this* document? If yes, replace it. If you notice yourself writing two or three sentences of context about a concern that isn't this file's concern, that's drift from mentioning into re-explaining. See `examples/concern-mixing-examples.md` (Example 5) for what this drift looks like caught in the act.
- **One home per concept, everywhere else links to it.** Where you found the same concept explained multiple times, pick (or write) the best single explanation, and make every other mention a link/reference to it instead of a re-explanation.
- **Group by relationship, not by chronology.** Directories should reflect how concerns relate to each other (e.g., architecture vs. product-facing vs. reference), not the order things were written in.
- **A README per directory, acting as a local map.** Every directory in the new structure gets a README whose job is: tell a reader (human or AI) landing in this directory what's here, what each file/subdirectory is for, and where to go for what. This is navigational, not a duplicate of the content — it should never re-explain what a linked doc explains, only point to it and say why someone would want it. Keep these short. A README's own shape can vary by directory — a directory of reference docs might warrant a table, a directory with a clear reading order might warrant a numbered list, a directory with one entry point might need only a paragraph and a link. Let the directory's actual contents dictate the shape. See `references/example-readme.md` for a worked example.
- **Nested READMEs compose.** A subdirectory's README only needs to make sense within its own directory; the parent README's job is to tell the reader that subdirectory exists and roughly why, not to repeat its contents.
- **One global index that stays current.** Alongside the per-directory READMEs, the root of the doc set (e.g. `docs/README.md`) should hold a single index of every document with a one-line description of what it covers — the full-set equivalent of the doc table in `references/example-readme.md`. This file only works if it's kept accurate, so end it with an explicit standing instruction future contributors (human or AI) will actually see, e.g.: *"You must update this file whenever a document is added, removed, or moved."* Without that instruction stated plainly in the file itself, the index quietly goes stale the same way the original docs did — the whole refactor is pointless if the map rots the same way the territory did. See `examples/concern-mixing-examples.md` (Example 6) for the failure mode this guards against.
- **Every document opens with a short contract, not just a title.** Directly under the H1, one to a few lines (a blockquote works well) should state: what this document is and covers, and — if a reader would plausibly need to visit another document first or alongside this one to make sense of it — a mention of that document, with a link, in the same one-line-mention style as everything else in this skill (state that it exists and why, don't re-explain its content). This is especially worth doing when the current document is built *on top of* another one — e.g. a document applying conventions defined elsewhere to a specific case should say so and point at the source, rather than leaving the reader to infer the relationship or rediscover the source convention independently. A one-line note on the document's own internal shape (e.g. "for each item: X → Y → Z") is also useful here if the document has a repeating structure, since it tells the reader what to expect before they start scrolling. Keep this contract to a few lines — it's an orientation, not a summary of the content that follows.

## Naming and granularity conventions (Step 4)

Two decisions repeat across almost every documentation set, regardless of domain, and are easy to get wrong by default. Apply both when shaping the tree.

### A. Don't create a directory for content that fits in a file

A directory only earns its keep once there's enough inside it to need its own local map (a README) to navigate. A single concern that fits comfortably in one file should stay a flat file at its natural location — turning it into `concern/README.md` plus `concern/concern.md` adds a layer of indirection and an extra file to maintain for no navigational benefit, and burns tokens on every future read for nothing gained.

```
Prefer:              Over (when there isn't enough content to justify it):
structure.md          structure/
                         ├── README.md
                         └── structure.md
```

Promote a flat file into a directory only once it's actually grown enough concerns that a single file would start mixing them — that's the same one-concern-per-file trigger from Step 2, just applied prospectively. Until then, resist creating the directory pre-emptively "for consistency."

### B. Reach for conventional category names before inventing new ones

Most software projects converge on a similar small set of top-level documentation categories because most projects have the same basic kinds of things to document. Default to this vocabulary when it fits, rather than inventing bespoke names per project:

- **`structure`** — the directory/module layout and high-level boundaries of the codebase itself (often small enough to stay a single flat `structure.md`, per convention A above).
- **`tech`** — implementation-level conventions and internals: architecture, algorithms, data models, coding conventions, infra.
- **`product`** — user/business-facing concerns: scope, UX, configuration, what ships and for whom.

These are defaults, not requirements — if a project's actual concerns don't map onto `tech`/`product`/`structure` cleanly, don't force them into it. But before inventing a new top-level name, check whether one of these conventional ones already fits; a reader (especially an AI agent working across many repos) benefits from recognizing familiar category names on sight instead of re-learning a bespoke taxonomy every time.

### C. Layer shared vs. scoped content explicitly, if the project has versions or variants

If the documentation set describes something that changes across versions, environments, or variants (a product with v1/v2/v3 scope, or platform-specific behavior, etc.), separate what's permanent from what's scoped rather than interleaving them:

- A **shared/base layer** — content that's true regardless of version and should always be read (architecture that doesn't change, core conventions). A common convention is naming this directory `base/`.
- **One layer per scope** — a directory per version/variant (`v1/`, `v2/`, ...) containing only what's specific to that scope, mirroring the same `tech`/`product`/`structure` categories inside each if useful.

The point isn't the exact names `base`/`v1`/`v2` — it's making the always-read layer structurally distinct from the scoped layers, so a reader (or an agent instruction file) can say "read `base/` always, read the current scope's layer, ignore the rest" without ambiguity. If the project has no versioning concept, skip this entirely — don't invent scope layers that don't correspond to anything real. See `references/example-readme.md` for a real example of `base`/`v1`/`v2` layering combined with the flat-file convention from A.
