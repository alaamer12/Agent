---
name: bleed
description: Convert a web UI between layout registers - full-bleed page, framed cards, or hybrid - and fix the "document inside an app" smell where a page wraps itself in a max-width card. Use when a page or mockup "looks like sections inside a page", when asked to make content take the full page or full width, remove the outer box or card around everything, match the layout grammar of sibling files, stop nesting cards, or conversely to contain a page into cards; also when reviewing a screenshot that shows a narrow centered column with dead margins.
argument-hint: "[page|framed|hybrid] <file>"
---

# Bleed

## Overview

Every UI is written in one of three **layout registers**. Most framing complaints are not style
disagreements — they are a register mismatch: the file is written in one register and the reader
expects another. Name the registers, pick the target, convert structure, leave components alone.

## The three registers

| Register | Content width | Section separation | Signature |
|---|---|---|---|
| **page** (full-bleed) | viewport minus fixed chrome, no cap | sticky section header + hairline divider | one canvas; sections are the page |
| **framed** (cards) | capped column, centered | gap between card borders | every block is an object with its own box |
| **hybrid** | full-bleed with one framed object | hairlines, plus a card where the object is genuinely one thing | a leaderboard row, a checkout summary, a player card |

Full grammar and per-register checklists: `references/registers.md`.

## The smell to fix

A page that has **both** its own outer chrome (rail, header, footer, scroll container) **and** an inner
max-width wrapper or rounded card holding the whole body is a document inside an app. The tell in a
screenshot: large dead margins that are not responsive behaviour, and a visible outer border that
duplicates the page edge. The tell in source: a `.container`/`.canvas`/`.sheet` with `max-width`
wrapping every section, or a single card element whose children are the page.

Reverse smell (page → framed): sections separated only by hairlines when each block is a distinct
object the user selects, compares, or acts on independently.

## Procedure

1. **Read the siblings first.** Open 2–3 files from the same set and extract their incumbent grammar
   into a checklist: fixed chrome width, header structure, scroll container, section-head pattern,
   padding scale, divider style, footer action row, and whether any max-width wrapper exists. The
   target register is almost always already decided by the set — the new file just drifted.
2. **Name both registers.** Say which register the file is in and which the request asks for. Match
   the user's wording against `references/vocabulary.md` first — several common complaints *sound* like
   framing problems and are not (density, hierarchy, chart quality). The disambiguating test: **does
   the content already reach its container's edges?** If yes, the register is fine and the complaint
   is about something else. If the request is genuinely ambiguous ("clean it up", "make it look
   right"), ask one question offering `page` / `framed` / `hybrid` with a one-line consequence each.
   Never guess between registers — it is the one decision the whole pass turns on.
3. **Convert structure, not decoration.** For page: delete the max-width wrapper and the outer card;
   hoist each section to be a direct child of the scroll canvas; replace card chrome with a sticky
   section head + bottom hairline; move the action row to the page footer. For framed: wrap each
   independent object in a card, add the cap, give the grid a gap.
4. **Do not touch inner components.** Charts, pills, tooltips, tables, tokens, state params and
   scripts survive the move unchanged. A register pass is invisible below the section boundary.
5. **Verify by measurement, then look once.** Probes in `references/verification.md`: content width
   equals viewport minus chrome, **page-level** caps are zero (a cap wrapping a chip row or a tooltip is
   correct code — scope the assertion to elements that contain a section block), sticky head count
   matches section count, no horizontal overflow at two widths, no console errors. Then one screenshot —
   measurement catches structure, only the eye catches rhythm, inline collisions and class-name clashes.
   Expect the document to get **taller**; that is the conversion working, not failing.

## Rules

- **The card legitimacy test:** a card is correct when its content is one object the user can point at
  ("this project", "this competitor"). It is wrong when it merely wraps the page.
- **Hybrid is not a cop-out.** Full-bleed page + one framed object is often the right answer; state
  which boundary is the object.
- **Utility frameworks own short class names.** Renaming a class can change its meaning: a single-word
  class may already be a framework utility (`ring`, `grid`, `container`, `stack`, `card`, `col`) and
  inherit unexpected styling. Prefer a prefixed name (`arc`, `section-head`, `mx-stack`).
- **Directional layouts need a bidi pass.** In RTL, `inset-inline-start` flips, and query strings or
  file names inside Arabic sentences mirror — wrap Latin fragments in `dir="ltr"`.
- **Never claim a parameter works without loading the page.** State params are the contract of a
  mockup; verify each one renders.

## Invocation

Explicit: `/bleed page <file>`, `/bleed framed <file>`, `/bleed hybrid <file>`. The file alone
(`/bleed <file>`) means: diagnose the register, report it, and ask before changing.

Auto-trigger — phrasings that mean a register problem, collected because users cannot name it:
"make it a page not sections", "it looks like a section inside a page", "a card inside a page",
"take the whole page dimensions", "full width / full bleed / edge to edge", "remove the box around
it", "stop wrapping everything in a card", "use section headers and dividers instead", "make it
consistent with the other files", "this doesn't look like the rest of the app", "put it in cards",
"make it a dashboard", "match the layout of `X.html`", "why are there empty margins here".

## Resources

- `references/vocabulary.md` — the phrases users actually say, mapped to registers, plus the near-miss
  table of complaints that sound like framing but are density, hierarchy or chart quality.
- `references/registers.md` — per-register grammar checklists and the conversion moves.
- `references/verification.md` — measurement probes and the screenshot pass.
- `examples/case-01-page-vs-cards.md` — a framed page converted to full-bleed: real before/after
  numbers, the probe false positive that rewrote an assertion, and two defects only a screenshot found.
