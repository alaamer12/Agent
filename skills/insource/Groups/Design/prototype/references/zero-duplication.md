# Zero duplication — three-layer styling and the ui.js catalog

Loaded before writing the first page module of any multi-page prototype, and whenever a second
copy of any class string, color, or markup block is about to exist.

## The measured failure

From a generated 42-page prototype (all numbers machine-counted after the fact, most undercounted
by the human report that triggered this file):

- **493** arbitrary Tailwind values (`text-[11px]` ×96, `min-h-[145px]` ×26…), **534** hardcoded
  hex uses across **118** distinct colors — while a `tailwind_config.js` with 12 tokens sat next
  to them, its dark palette not covering the light admin theme, so every page bypassed it.
- One KPI card's 140-character class stack pasted **26 times across 7 files**; ~67% of admin class
  strings of ≥25 chars were repeats appearing in 2+ files.
- ~38 of 42 page HTMLs were byte-identical skeletons except for title and route; one file's JSDoc
  header line — "High visual parity with overview.js" — sat verbatim in **6** page modules: the
  agent generated pages by cloning a sibling instead of extracting units.
- **79** inline `<svg>` in admin while a shared `icon()` existed and web/mobile used it 100+ times;
  **129** inline `onclick` (67 of them plain navigation).

The shared layer — state helper, shell builder — held up fine. **Every failure is at content
level**: each page module re-emitted its own glow block, toggle, page-title, and card grid by
copy-paste. Styling technology was never the cause, and changing it fixes nothing: SCSS would add
a compile step to a build-free project and merely *relocate* the duplication; `@apply` does not
work in ordinary `.css` under the Tailwind Play CDN.

## The rule

**Any visual pattern used twice exists in exactly one place.** Not "is refactored eventually" —
the second use is the moment of extraction. The agent working on page N+1 edits the shared
definition once; it does not perform the same edit on N earlier pages. `scripts/guards.mjs`
measures this; run it before declaring any batch done.

**Extend `ui.js` first; never paste class strings.** When a builder for the pattern doesn't
exist, write it once in `ui.js`, then use it on the current page and retrofit the earlier copies
in the same pass — the retrofit is the extraction; an unretrofitted pattern is two owners.

## Three layers

Load order stays the architecture's (`theme.css` → `components.css` → `_app.css` → `<page>.css`);
the layers decide *where a rule goes*:

1. **Tokens** — every color, radius, font size, and spacing step in one place: CSS custom
   properties in `theme.css` mirrored into `tailwind_config.js` (one source, two renders — keep
   the JS config generated-from or checked-against the CSS list, never independently edited).
   Light/dark via `[data-theme="light|dark"]` blocks so admin and web/mobile share identical
   component rules; `?theme=` (the dock's Theme tab) flips them. **A theme in active use must be
   covered by the token set** — the 534-hex leak started exactly where tokens stopped matching
   the pages being built.

   **The Palette Law.** No prototype writes page code before its full color design exists in
   `theme.css`: a brand hue ramp, a neutral ramp, surface/ink pairs per theme, and semantic
   tones (`--tone-success|warn|danger|info` — the feed `--tone` variants need), each present in
   both `[data-theme]` blocks. If the person supplied a brand guide, encode it; if not, **design
   one and state it before scaffolding** — "I picked a deep teal brand ramp with warm neutrals
   because the domain is finance-meets-friendly" — as part of the build report, not silently.
   Every color anywhere resolves through this list: components use `var(--…)`, the dock adapts
   its own accent to the detected brand token, and a hex outside a token file is a `guards.mjs
   tokens` finding. The dock's Theme tab renders the token set as live swatches — if that list
   is empty, page work has started too early; stop and do the palette first.
2. **Component classes** — repeated visual patterns as named plain-CSS classes with
   custom-property variants: `.badge` + `--tone`, `.btn` + `--variant`, `.card`, `.kpi`,
   `.table`, `.glow`. No `@apply`; plain rules over the variables. This is what kills the
   per-tone emerald/amber/sky class-string triples: one `.badge` whose color is
   `var(--tone, ...)`, fed from an enum map.
3. **Utilities** — Tailwind-style utilities for genuine one-offs: one-off flex tweaks, a
   spacing nudge used exactly once. If a utility value recurs, it is either a token (a size
   scale step) or a component (a visual pattern) — decide which, and move it.

## The ui.js catalog

`shared/js/ui.js` (single-app: `js/ui.js`) holds the content-level builders that the shared
shell already proved they need. Build the catalog **from the second use, never pre-emptively** —
but when that second use happens, the builder is written first and both uses call it.

| layer | builders | kills |
|---|---|---|
| **Page bootstrap** | `definePage({ spec, data, render })` — owns mountState + shell + page head so page files carry only `render` | per-page boot prologue, N near-identical HTML skeletons (serve or generate pages from one template) |
| **Layout** | `pageHeader(title, actions)`, `pageGlow()`, `section(title, ...)`, `grid(cols, ...)` | the 8× glow block, per-page title/glow paste |
| **Cards / data** | `card()`, `kpiCard({ label, value, delta, spark })`, `chartCard()`, `dataTable({ columns, rows })`, `progressBar()`, `sparkline()` | the 26-copy KPI stack, hand-repeated `<table>`/`<th>` markup |
| **Badges / enums** | `badge(tone, text)`, `tierBadge()`, `statusBadge()` over `TIER`/`STATUS` maps | pasted color triples; enum copy that drifts per page |
| **Controls** | `button()`, `linkButton()`, `filterPills()`, `tabs()`, `searchInput()`, `select()`, `field()`, `toggle()` | the ~100 hand-written `<button>`s and repeated form markup |
| **Overlays** | `modal()`, `drawer()`, `bottomSheet()`, `toast()` | repeated fixed-inset blocks; `alert()` stubs |
| **Page states** | `loadingState()`, `errorState()`, `emptyState()`, `stateGate(state, { ok, loading, error, empty })` | the isLoading/isError branch repeated per page |
| **Icons** | use the shared `icon()` everywhere — inline `<svg>` is a defect when a glyph map exists | 79 inline SVGs |
| **Data / logic** | `createData(state, { sparse, filled })`, `formatMoney/Number/Percent/Date`, `NAV` array, `STRINGS` via `t()` | scattered `filled` ternaries, 40+ `toLocaleString` calls, hardcoded nav flags, duplicated copy |
| **Behaviour** | delegated `data-go` / `data-toast` handlers bound once in `definePage` | inline `onclick` per button (67 were navigation) |

Prototype chrome is **not** in this catalog — it is the dock (`prototype-dock.md`). `ui.js` builds
product surface; the dock builds tool surface. A builder that appears in the wrong file is the
same mistake as the pasted toggle, one layer up.

## Order of work

1. **Guards first.** `node scripts/guards.mjs all <project>` before writing page two; on a
   migration, run it to get the baseline numbers, then drive them down.
2. **Tokens + theme blocks** — decide both themes' palettes up front, cover every theme the
   pages will actually use.
3. **`components.css`** — the classes you already know repeat (card, badge, btn, table, glow).
4. **`ui.js` + first page through it** — the pilot proves the builders; write the builders as the
   pilot demands them, not beyond.
5. **Data layer** — `createData`, formatters, enum maps, `NAV`, `STRINGS`.
6. **`definePage` + page generation** — skeletons come from one template; page files shrink to
   spec + render.
7. **Behaviour** — delegated handlers; a UI framework (e.g. Alpine) only if real reactivity is
   still missing after these.
8. **Enforce** — guards in `--strict` as the exit criterion; screenshots per page via the
   `parity` skill (`/parity`) to catch visual drift during the migration.

## What the guards check

`scripts/guards.mjs` (zero-dep, same CLI style as `stories_check.mjs`; `--strict` for CI-style
failure):

| subcommand | finding |
|---|---|
| `dupes` | a class string ≥25 chars or markup block appearing in 2+ files / 3+ times |
| `tokens` | hex colors and `[...]` arbitrary values used outside token files |
| `svg` | inline `<svg>` while a glyph/icon helper exists |
| `onclick` | inline handlers, flagging navigation ones as `data-go` candidates |