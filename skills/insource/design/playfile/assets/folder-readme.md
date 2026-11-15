# V[n] — [wave theme]

> **→ Implementation requirements live in [`.steering/vN/….md`](../…)** — read them before writing any
> code; they supersede improvisation. *(Remove this block if the project keeps no requirement docs.)*

> **Status: design proposal for review.** All numbers, titles, budgets and stats are illustrative design
> data.

[Two to four sentences: what this wave changes about the product's shape, written so a newcomer gets the
frame before opening a file.]

## Provenance

Screens enter `vN-[theme]/` the **first time vN changes them**. Until then this wave links to the shipped
folder (`../vN-1/[page].html`) rather than copying it — the shipped design stays single-sourced and nothing
drifts. When a linked screen is edited, copy it here and pull its inbound links back.

## Files

| File | What to try |
|------|-------------|
| [`[page].html`](./[page].html) | [The review path: what to click, what each force-param shows — `?state=…`, `?step=1..n`, `?filled=1`, `?theme=dark` (mark reviewer-only params).] |

## Mechanics *(optional — only for interactions a reviewer needs to trust)*

- [How the notable behavior works, 3-6 bullets. Enough to verify it is real, not an implementation guide.]

## Identity system *(optional — only if this wave introduces tokens/palettes)*

| Token | [variant A] | [variant B] |
|-------|-------------|-------------|
| `--brand` | `#…` | `#…` |

[State colors never change with brand or theme — brand color is identity, state color is truth.]

## Decisions

1. **[What was ruled] ([YYYY-MM-DD]).** [Why — the reason, not just the fact.]
2. **[Decision] — REVERSED [YYYY-MM-DD], see #N.** [Spent decisions stay visible; the trail is the value.]

## Open questions

1. [A question whose answer is a decision, phrased so replying changes a screen — name which.]

## CDN note

Mockups load [Tailwind/FontAwesome/fonts] from CDNs without SRI. Review artifacts only; the product renders
these states from its own design tokens, not from this HTML.
