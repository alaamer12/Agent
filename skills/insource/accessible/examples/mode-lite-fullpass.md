# Lite mode: a full pass, assembled

The individual move files (`stat-encoding.md`, `inline-warning.md`, `chart-ink.md`, etc.) each show one move in isolation. This file shows what it looks like when several Lite-tagged moves are applied *together* to the same input, so the combined shape of a real Lite pass — not just each move separately — is visible. As with every file in this folder, no specific framework, markup shape, or palette is prescribed; this is a structural walkthrough.

## Starting point

A generalized dense admin screen: one page, one long table. Each row: an identifier, several small pill/tag objects for configuration, a run-on stat sentence, an occasional warning squeezed into the same cell as other content, a lone action control. Small type throughout (12–13px), tight spacing, harsh full-contrast background.

## What a Lite pass touches, and in what order

1. **Typography and spacing first**, because it's the move most Lite passes should lean on hardest (see `SKILL.md`'s note on pushing this further than feels natural). Base type moves up a full step, line-height opens, padding around every cell/card roughly doubles from its cramped starting point. This alone should already make the screen feel different before any other move is applied.
2. **Stat encoding, in place.** The run-on stat sentence in each row becomes a small proportional visual (bar/ring/sparkline) plus a legend, still inside the same cell it was already in — not moved to a new section, not moved to a summary area elsewhere on the page.
3. **Inline warnings, promoted within their own row.** A warning previously squeezed as a caption under other content in a cell becomes its own clearly bounded sub-block (icon, bold claim, one sentence, optional action) — but it stays exactly where that row already lives on the page. It does not get pulled out into a shared "attention" section at the top of the page; that would be a Medium-level relocation, not a Lite one.
4. **Action zones, tidied within each row.** Wherever a row's own action control(s) currently sit, they move into one consistent trailing cluster for that row — a purely local rearrangement, not a new shared toolbar pulling actions in from multiple rows.
5. **Chart-junk removed, if any chart already exists.** Any existing chart on the page gets stripped of decoration that doesn't answer a specific question — this doesn't require the chart to move, just to render more cleanly where it already sits.
6. **Icons, for the identity-defining chrome only.** Any placeholder-style glyphs in primary navigation become a proper small icon system; icons deep in the row-level detail can stay pragmatic (see the icon move's own reasoning).

## What a Lite pass explicitly does not do

- It does not group rows, rebuild rows into fewer/different responsibilities, or introduce new zoom levels (glance/context/detail) — the row still tells the same list of things it told before, just more legibly.
- It does not touch the color system beyond incidental contrast fixes needed to hit WCAG AA at the new type sizes — no new tonal ramp, no re-assignment of which region gets which color treatment.
- It produces exactly one output file/page, matching the input's page count exactly.

## How to tell if a "Lite" result actually stayed Lite

After the pass, compare page count and section count to the original: they should be identical. If a new section, a new summary zone, or a new page appeared anywhere, the pass drifted into Medium territory without saying so — that's a real risk on this mode specifically, because several Lite-tagged moves (stat encoding, warning promotion) produce new markup, and it's easy to let "new markup" quietly become "new *location*" without noticing the line was crossed.
