# Display Architecture — walkthrough (ops console, stat-card overflow + RTL pass)

One instance among many: a data-dense console whose dashboards were styled first and expressed
second. The numbers come from a real measured pass; the fix is the method, not the values.

## The failure as found

A KPI grid of fixed-size cards (`min-height` ~145px, value styled at a display size around
32px, one shared card pattern across 7 pages) rendered raw grouped integers. Fine with demo
data (`128`, `1,204`) — and at real magnitude (`5,000,000`, locale-de `5.000.000`, locale-ar
with Arabic-Indic digits, which render wider) the digits struck straight through the card's
boundary. Nobody had asked the display questions:

- What is the reader's question at a stat card? *About how many* — L2, never L1.
- What is the slot's budget at that style? *≈6 glyphs at 32px* — `5,000,000` is 9.
- What is the fallback? *None existed.* The container lost.

## The surface-class table, filled

| Surface class | Reader's question | Voice | Typeface + figures | Level | Budget | Fallback |
|---|---|---|---|---|---|---|
| Stat card | about how many? | terse, ops-professional | grotesk, tabular lining | **L2** | ≤ 6 glyphs @ 32px | tap → detail view shows L0 |
| Reconciliation table cell | exactly what? | neutral | same grotesk, tabular | **L0** | column ≤ 13 (widest locale) | column resize is a ui matter; ellipsis forbidden — L0 never compresses |
| Chart axis tick | scale at a glance | quiet | small tabular | **L2** | ≤ 4 | density step-up (1K/5K) before labels rotate |
| Notification text ("saved N items") | story | warm-simple | prose face | **L3** | sentence reflows freely | ICU plural categories carry it |
| Receipt / invoice total | exactly what do I owe? | exact | serif doc, tabular | **L0 pinned** | ≤ 16 | compact forbidden by rule |

Pairing checks that ran on the same table: ops voice + tabular figures + L2 chips corroborate
(each tells "engineering-trustworthy"); the receipt row was caught as a mismatch in draft —
serif voice with the dashboard's rounded display accent — fixed before authoring.

## The fixes, by mechanism

1. **Level assignment** in the display doc: stat cards get L2 with exact reachability —
   formatter (`Intl.NumberFormat` compact notation per locale: `5M` / `5 Mio.` / `٥٫٩م`)
   plus the L0 value in the detail view and an `sr-only` span.
2. **Budget + ladder** written per slot; tabular figures enabled app-wide for any number that
   aligns or animates; the count-up widget reserves its widest frame (no jitter, CLS rule from
   the ui pillar honored).
3. **Worst-case test strings** added to the component's demo states: `999,999,999,999`,
   `999.999.999.999`, `٩٬٩٩٬٩٩٬٩٩٬٩٩٬٩٩٩` — CI screenshot diff catches the next widening
   of the display size, because budgets are checked in CI as text, not remembered.
4. **RTL pass**: product decision recorded — Arabic-Indic numerals for consumer-facing
   surfaces, Western for machine-dense tables (a written split, not drift); every number in
   an Arabic sentence isolated (`dir="auto"` on generated-text spans); plural rule replaced by
   ICU categories, killing the `count > 1 ? 's' : ''` pattern that survived in three places.
5. **Sync block declared**: the surface-class table's homes = this doc, the design tokens file
   (display sizes), the AGENTS.md voice section row for "ops" register. Editing any one
   requires the others in the same change — recorded in the doc's §7 with locations.

## What the walkthrough is evidence for

The overflow was cosmetic only in the demo, architectural everywhere else: the same missing
decision (no level, no budget, no ladder, no locale worst-case) also produced the notification
that said "1 items", the receipt rounded to "5M", and the Arabic label that ate its own number.
Display architecture is the one place all four get decided together.