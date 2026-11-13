# One instance among many — deduplicating a page head by structure, not by copied markup

The before/after below is drawn from a real 42-page generated prototype (numbers measured, copy
anonymized). Read it as **the extraction decision**, not as markup to copy: the builders named
here are one project's `ui.js` — yours will differ; the *shape* of the move is the point.

## Before: the page head that exists 8 times

Each admin page module opened its `render()` by pasting the same three blocks into its own
template string:

```js
// — every page file carries this, with the class soup spelled out each time —
const head = `
  <div class="absolute -top-10 right-0 left-0 h-96 pointer-events-none overflow-hidden -z-10">
    <div class="… blur-3xl …"></div><div class="… blur-2xl …"></div>       <!-- glow, 8 copies -->
  </div>
  ${isFilled ? `
    <a href="?" class="inline-flex items-center gap-1.5 px-4 py-2 rounded-full bg-slate-100
       text-slate-700 border border-slate-300 text-xs font-bold hover:bg-slate-200">
      ↺ clear data (sparse state)                                          <!-- prototype chrome, 8 copies -->
    </a>` : ''}
  <h1 class="text-[32px] font-black …">Users</h1>
  ${KPI.map(k => `
    <div class="relative overflow-hidden bg-white rounded-2xl p-5 shadow-sm border
                border-slate-200/80 hover:shadow-md transition-shadow min-h-[145px]
                flex flex-col justify-between">                            <!-- card stack, 26 copies -->
      …
    </div>`).join('')}
`;
```

Three separate diseases in one snippet:

1. **The glow block** — a decorative *pattern*, pasted 8×. Changing its height meant 8 edits.
2. **The filled-toggle** — not a product control at all: prototype chrome wearing product
   markup, pasted 8×, and already drifting (one copy had lost its suffix). No number of
   extractions into `ui.js` makes this right — it doesn't belong in a page *anywhere*.
3. **The KPI card** — the highest-count offender (26 uses of one 140-char class stack), where
   the fix is genuinely just a builder.

Also visible: `text-[32px]` — an arbitrary value bypassing the type scale, and a conditional
`isFilled` branch leaking the data-fidelity mechanism into content.

## After: three owners, three moves

```js
// ui.js — written once, at the moment the second copy would have been pasted
export function pageGlow()      { /* one function; geometry from tokens, not literals */ }
export function pageHeader(title) { /* h1 + actions slot; no meta-controls, ever */ }
export function kpiCard({ label, value, delta, spark }) { /* structure + `kpi` component class */ }

// definePage owns the mount/shell prologue each page used to repeat
definePage({
  spec: USERS_SPEC,
  render: ({ state, data }) => `
    ${pageGlow()}
    ${pageHeader(t('users.title'))}
    ${stateGate(state, {
      filled: data.KPI.map(kpiCard).join(''),
      empty:  emptyState(t('users.empty')),
    })}
  `,
});
```

```css
/* components.css — the 140-char stack becomes one class with token parts */
.kpi { border-radius: var(--r-xl); padding: var(--s-5); box-shadow: var(--shadow-sm);
       min-height: var(--kpi-h); display: flex; flex-direction: column; justify-content: space-between; }
```

```
/* the filled toggle is gone from the page. Its UI is the dock's States tab:
   one control, all pages, writing ?filled= — see references/prototype-dock.md */
```

Each disease got the move that matches what it *is*:

| was | is | owner |
|---|---|---|
| pasted glow markup ×8 | `pageGlow()` + `.glow` | ui.js / components.css |
| pasted toggle link ×8 | one dock tab writing `?filled=` | **the dock** — never the page |
| pasted card soup ×26 | `kpiCard()` + `.kpi` | ui.js / components.css |
| `text-[32px]` literals | `--h1` size step | tokens |
| per-page `isFilled` ternaries | `createData` + `stateGate` | data layer |

## How to tell which move applies

Ask, in order: **(a)** Is this control about the *prototype* (data mode, inspection, theme,
app hopping)? Then it is dock or URL — extraction into `ui.js` is the wrong fix, the page must
lose it entirely. **(b)** Is it a visual pattern used twice? One component class + one builder.
**(c)** Is it a raw size or color that recurs? A token. Only what survives all three questions
may be written inline — once.

`node scripts/guards.mjs all <project>` flags exactly (b) and (c) mechanically; (a) is the
judgment guard can't make for you — it reads like product markup, which is why it survived 8
copies. The test that catches it: *would this control exist in the shipped product?*