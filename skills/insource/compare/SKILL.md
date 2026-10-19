---
name: compare
description: Write professional, well-reasoned comparisons between two or more subjects of any kind — technologies, files, projects, code modules, books, documents, biological processes, products, strategies, or any named options. Use whenever the user asks to compare, evaluate trade-offs, distinguish, or choose between things, including "which is better," "what's the difference," or "help me decide." Supports open-ended discovery of relevant aspects and dimension-based comparison on user-specified or researched criteria. Enforces real differentiators only, "why it matters" reasoning, independent research, graded quantitative claims, and neutral context-driven conclusions.
---

# Compare

Produce comparisons people actually trust. The core failure mode to prevent: listing a trait as an "advantage" of A when B achieves the same outcome a different way, and listing traits without saying why they matter.

This skill is general-purpose. Subjects may be technologies, files, code modules, projects, books/PDFs, processes, products, strategies, or anything with distinguishable traits.

## Mandatory Workflow

### 1. Capture decision context
Identify the real audience and decision (choose for a project? study a concept? evaluate two codebases?). From context or one clarifying question. This determines relevance and depth.

### 2. Select mode
- **Open-Ended** (default): discover the dimensions that actually matter, then compare on them.
- **Dimension-Based**: when the user names dimensions (or the subject type invites it), stay strictly inside those axes. If none given for files/modules/projects, derive a short high-signal set and state it up front.

See `references/modes.md` for full rules and when to switch.

### 3. Research or inspect each side independently
Never rely only on one side's framing.
- Named/external subjects → independent sources + primary sources.
- Local subjects (files, modules, projects) → actually read the artifacts.
- Books/documents → use provided files; if missing, ask the user. Never invent content.

See `references/subject-types.md` for inspection procedures per type.

### 4. List candidate differences raw
Draft every difference found. Do not filter while collecting.

### 5. Apply the quality filters (mandatory)
For every candidate claim:
1. **Differentiator test** — can the other side achieve the same outcome via a different mechanism? If yes, cut or reframe.
2. **Trust-Me-Bro filter** — grade superiority/magnitude claims green / yellow / red.
3. **"Why it matters"** — every kept difference must answer "so what?"

Full rules and traps: `references/quality-filters.md`.  
Worked examples: `examples/differentiator-test.md`, `examples/why-it-matters.md`.

### 6. Structure and write
Default to **point-by-point** (organize by criterion, discuss all subjects inside each).  
Skeleton and anti-padding rules: `references/structure.md`.

### 7. Conclude by context, not absolute winner
State honest trade-offs. Convert to "A fits if …, B fits if …". Give a direct recommendation only when the user's constraints are known.

### 8. Verification checklist
Run the checklist in `references/checklist.md` before finalizing.

## Progressive disclosure map

| Need | Load |
|------|------|
| Mode selection rules | `references/modes.md` |
| How to handle files / modules / projects / books | `references/subject-types.md` |
| Differentiator test, Trust-Me-Bro, why-it-matters | `references/quality-filters.md` |
| Output skeleton and length rules | `references/structure.md` |
| Final verification checklist | `references/checklist.md` |
| Worked differentiator examples | `examples/differentiator-test.md` |
| Worked "why it matters" examples | `examples/why-it-matters.md` |
| Sample comparison outlines | `examples/sample-outlines.md` |

## When to ask the user
- Books/PDFs referenced but not provided → request the files or specific sections.
- Local path given but inaccessible → request path or content.
- Decision context ambiguous and would change dimensions → one focused clarifying question.
- Dimension-based requested with no dimensions → derive a short set and state it, or ask which matter most.
