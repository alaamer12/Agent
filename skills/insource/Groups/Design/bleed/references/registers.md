# Registers — grammar and conversion moves

Read the register that matches the target, plus the one the file is currently in.

## page (full-bleed)

Grammar checklist — extract this from the sibling files, do not invent it:

- fixed chrome: side rail / nav of a known width; content starts after it, ends at the viewport edge.
- a sticky or static **page header** spanning the content, usually 3 zones (actions · title · identity).
- one scroll container holding the body; the body is a plain block, **no max-width cap, no outer card**.
- sections as direct children of that block, each = `section-head` (sticky, title + kicker, bottom
  hairline) then a `section-block` (uniform horizontal padding, bottom hairline).
- separation is **hairlines and whitespace**, never borders around content.
- one page-level footer action row (primary + secondary), aligned to the same padding as the blocks.
- tokens: `--surface`, `--line`, `--ink-*`, `--brand*` — sections read the page's surface, not their own.

## framed (cards)

- a capped, centered column (`max-width` + `margin: auto`) inside the viewport.
- every block is a card: own background, border, radius, internal padding; gaps between cards.
- headers belong to cards, not to the page; the page may have a title band above the grid.
- grids of cards are the primary structure; comparison and selection happen by pointing at a card.
- good for: dashboards of independent objects, pickers, settings groups, anything the user scans as
  separate items.

## hybrid

- full-bleed page **plus** exactly one framed object where the content genuinely is one object
  (a scoreboard row, a summary panel, a selected entity).
- the test is stated in SKILL.md: a card is right when its content is one thing the user can point at.
- if every section is a card, that is `framed`, not hybrid. If none is, that is `page`.

## Conversion moves

### framed → page

1. Delete the max-width wrapper and any outer card element; promote its children.
2. Replace each card's border/radius/background with: a sticky head (title + kicker + bottom hairline)
   and a block with the shared padding scale.
3. Move the page title into the header's centre zone; move the action buttons into a footer row.
4. Collapse duplicate chrome: if the card had its own header *and* the page has one, the card's
   becomes a section head.
5. Keep multi-column layouts *inside* a block — full-bleed describes the block, not its internals.
6. Reuse the sibling files' class names verbatim. Do not coin `page-section` when the set says
   `section-head`.

### page → framed

1. Introduce the cap and centering; pick the gap scale from the sibling set.
2. Wrap each independent object in a card; move its heading inside.
3. Remove sticky section heads — a card header that sticks inside a scrolling card is a bug.
4. Keep charts and tables untouched; only their container changes.

## What never changes in a register pass

Component internals, tokens, state parameters, scripts, copy, and data. If the diff touches a chart's
markup, the pass has gone too far.
