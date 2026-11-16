---
name: mermaid
version: 1.0.2
author: Amr
specialized: mermaid
description: Mermaid flowchart authoring discipline — a diagram shows what exists and how things connect; documents carry the policy and sentences. Use when writing or editing any .mmd or embedded mermaid flowchart, when a diagram "looks trash" or reads crowded, when adding nodes/legends/panels, or when extracting a diagram out of a document. Node labels are a name plus at most 1-2 words; status is color, not text; legends are swatches, not sentences; one node per entity; no placeholder nodes.
when_to_use: Creating or editing a mermaid flowchart, reviewing a cluttered diagram, moving a diagram into its own .mmd file, adding a legend, naming a subgraph.
argument-hint: "[the diagram file or node block]"
---

# mermaid — draw the graph, not the story

The one test for every mark on a diagram: **does it say *what exists / how it connects* (belongs), or *why / under what rule / what comes later* (document)?** A diagram that explains is a document that got arrows.

## Label law

- A node is a **name**. Add at most 1–2 qualifier words, and only for what the panel cannot carry (order: `step · first`; state: `OFF`).
- A subgraph title is a **name**, not a purpose sentence. `01 — INTAKE`, not `01 — INTAKE · where raw records are validated before storage`.
- **Never repeat the panel inside its nodes.** `review / Reviewer Skill` inside a panel titled `REVIEWERS` says it twice; the title says it once.
- No sentences. If a label needs a clause, the document owns that clause — leave the node short.

## Meaning lives on edges

- Label an edge when the **link** carries meaning; leave plain sequence arrows silent.
- **One node per entity.** A role serving two areas is one independent node with two labeled edges (`-. docs .->`, `-. code .->`) — never twins named by their target (`helper · docs`, `helper · code`).
- Cross-cutting influence is dotted edges from outside the sections, not clones placed inside each section.

## Color and legend

- Classification (status, severity, mandatory/optional) travels on **classDef color**, set in the `class` lines — not as words inside labels.
- A legend is **swatch nodes reusing the very same classes** (`["Mandatory"]:::` the mandatory class). Text legends ("■ green = Mandatory…") are banned: they name colors that rot the moment the palette changes.
- **No placeholder nodes** for members that do not exist yet ("future X goes here"). A diagram renders existence; the document registers growth rules.

## Files and mechanics

- Every flowchart lives in its own `.mmd`; the source document keeps a heading and a one-line pointer.
- Escape HTML in labels: `<` → `&lt;`, `>` → `&gt;`. Raw angle brackets inside node text break or swallow labels.
- Node **ids stay stable** across edits — labels change, ids feed the edges and `class` lines.
- After any edit, verify mechanically:
  1. `subgraph` count equals `end` count;
  2. every id appears in exactly one `class` line, and no `class` line references a removed id (ghosts survive renames);
  3. every arrow target id still exists;
  4. chain entries not left dangling: if a step is added mid-chain, rewire the connector, don't hang it off the end.

## Checklist — run before calling it done

1. Any label repeating its panel title? Cut it.
2. Any sentence in a node? Move it to the doc.
3. Any status word that could be a color? Color it.
4. Any duplicated entity, one per context? One node + labeled edges.
5. Any text legend or ASCII glyph? Replace with swatch nodes.
6. Any "future/placeholder" node? Delete; the doc carries registration.
7. Angle brackets escaped? ids/classes verified against the four checks above?

## Boundaries

| Need | Go instead |
|---|---|
| What the flow *means*, the rules behind an arrow | the owning document |
| Sequencing of steps (numbered procedure) | the document; the diagram shows one path |
| Making diagrams | other renderers; this skill is flowchart authoring discipline only |
