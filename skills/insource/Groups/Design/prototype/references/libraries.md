# Libraries — use real ones

> **What this owns:** when to reach for a library vs. hand-roll, the
> loading strategy for CDN-first prototypes, a reference catalog of
> recommended picks by category, and the fallback rules when external
> deps are off the table.

---

## The standing rule

**Default to production-quality libraries. Do not hand-implement what a
real library already does.**

A prototype's job is to look and feel real as fast as possible. Every hour
spent writing a hand-rolled icon renderer, a bespoke SVG chart, a custom
date formatter, or a DIY drag handler is an hour that produced an inferior
result — one that immediately reads as cheap to anyone who has used a real
product. The library exists, it is maintained, it is correct, it handles
the edge cases, and it loads from a CDN in one `<script>` tag.

The old guidance of "CDN is an option where it genuinely helps" is wrong
for prototypes. **The option is to NOT use a library — and that option
requires the user to explicitly ask for it.**

---

## Default loading strategy: CDN

The prototype has no bundler by default. CDN `<script>` tags or an
`importmap` are the fastest path to any library — no install, no build
step, works immediately in the dev server.

```html
<!-- UMD — globals available instantly after the script tag -->
<script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js" defer></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js" defer></script>

<!-- ESM — via importmap in <head> before any module script -->
<script type="importmap">
  { "imports": { "lucide": "https://cdn.jsdelivr.net/npm/lucide@latest/dist/esm/lucide.js" } }
</script>
```

**Pin major versions once the prototype is shared for review**
(`chart.js@4`, not `@latest`) so a CDN update between sessions does not
silently change the output.

**Node module installs** (`npm install`, `bun add`) are a last resort —
they add a build step and slow down setup. Only go that route when the
user asks for it or when the library has no usable CDN UMD/ESM bundle.

---

## Catalog — recommended picks by category

Pick the first entry in each category unless a specific preference or
constraint points elsewhere. If the user named a library, use it.

### Icons

| Pick | CDN | Notes |
|---|---|---|
| **Lucide** (default) | `cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js` | 1500+ icons, 2 px stroke, MIT, UMD + ESM. Call `lucide.createIcons()` after each DOM render cycle. |
| Phosphor | `cdn.jsdelivr.net/npm/@phosphor-icons/web@latest/src/index.js` | Five weights (Thin → Bold → Fill); good when weight variation is part of the visual language |
| Tabler Icons | `cdn.jsdelivr.net/npm/@tabler/icons@latest/dist/umd/tabler-icons.min.js` | 5000+ icons; UMD like Lucide; great for dense admin UIs |
| Heroicons | ESM only via importmap | Tailwind-paired; outline + solid variants |
| Bootstrap Icons | `cdn.jsdelivr.net/npm/bootstrap-icons@latest/font/bootstrap-icons.min.css` | Font-based (`<i class="bi bi-search">`); no JS needed |

> Do **not** hand-write SVG path data for icons. Even for a single icon.
> Lucide has it; load it.

### Charts & data visualisation

| Pick | CDN | Notes |
|---|---|---|
| **Chart.js** (default) | `cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js` | Responsive, 8 chart types, great defaults, no build step |
| ApexCharts | `cdn.jsdelivr.net/npm/apexcharts@latest` | Richer default styling, animated; good for executive dashboards |
| uPlot | `cdn.jsdelivr.net/npm/uplot@latest/dist/uPlot.iife.min.js` | 40 KB; ultra-fast for dense tables with many inline sparklines |
| ECharts | `cdn.jsdelivr.net/npm/echarts@latest/dist/echarts.min.js` | Maps, Sankey, heatmaps; use only when those types are needed |

> Do **not** hand-draw bar charts or area charts as raw SVG/polyline.
> Chart.js handles scales, axes, tooltips, legend, responsive resize,
> and animation correctly. A hand-drawn SVG bar chart does none of that.
>
> Exception: a pure trend sparkline with no axes and no labels inside a
> table cell — `uPlot` or the starter's tiny `sparkline()` utility is fine
> for that specific case.

### Dates & times

| Pick | CDN | Notes |
|---|---|---|
| **Day.js** (default) | `cdn.jsdelivr.net/npm/dayjs@latest/dayjs.min.js` | 2 KB; moment-compatible API; plugins for relative time, timezone, etc. |
| date-fns | ESM via importmap | Tree-shakeable; prefer when only 1–2 functions are needed |

> Do not hand-roll `"2 hours ago"` or month-name arrays. Day.js relativeTime
> plugin does it in one line.

### Animation & motion

| Pick | CDN | Notes |
|---|---|---|
| **Motion One** | `cdn.jsdelivr.net/npm/motion@latest/dist/motion.js` | WAAPI-based, tiny; `animate(el, { opacity: [0,1] }, { duration: 0.3 })` |
| GSAP (free tier) | `cdn.jsdelivr.net/npm/gsap@latest/dist/gsap.min.js` | Full-featured; use when timeline control or ScrollTrigger is needed |

> Only add an animation library when the design explicitly benefits from
> it. Do not add one speculatively.

### Tables & data grids

| Pick | CDN | Notes |
|---|---|---|
| **Tabulator** | `cdn.jsdelivr.net/npm/tabulator-tables@latest/dist/js/tabulator.min.js` + matching CSS | Sortable, filterable, paginated grid; zero dependencies; UMD |
| AG Grid (community) | `cdn.jsdelivr.net/npm/ag-grid-community@latest/dist/ag-grid-community.min.js` | Enterprise-class grid; community edition is free |

> Only reach for a grid library when the screen genuinely has a
> sortable/filterable data table. Plain `<table>` with CSS is fine for
> read-only display.

### Forms & validation

| Pick | CDN | Notes |
|---|---|---|
| **Cleave.js** | `cdn.jsdelivr.net/npm/cleave.js@latest/dist/cleave.min.js` | Input masking (phone, card, date) |
| Floating UI | `cdn.jsdelivr.net/npm/@floating-ui/dom@latest/dist/floating-ui.dom.umd.min.js` | Anchored popovers, tooltips, dropdowns — correct positioning without hacks |

### Drag & reorder

| Pick | CDN | Notes |
|---|---|---|
| **SortableJS** | `cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js` | Drag-to-reorder lists and grids; no dependencies |

### Fonts

Load from Google Fonts or Bunny Fonts (privacy-friendly alternative):
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```
Declare in `theme.css`: `--font: "Inter", system-ui, sans-serif;`

---

## Practical loading pattern

UMD libraries load before the page module; call their APIs after each
DOM render cycle (not once at startup, because the page module re-renders
on every state change):

```html
<head>
  <script src="https://cdn.jsdelivr.net/npm/lucide@latest/dist/umd/lucide.min.js" defer></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js" defer></script>
</head>
```

```js
// In the page module's render():
function render(state) {
  app.innerHTML = buildDOM(state);           // sets data-lucide attrs + canvas els
  if (window.lucide) lucide.createIcons();  // icons — after every render
  requestAnimationFrame(() => initCharts(state)); // charts — after canvas is painted
}
```

---

## When the user bans external dependencies

If the user says "no CDN", "offline only", "no external libraries", or
equivalent — confirm it in the pre-build questionnaire and proceed with
the following fallbacks:

- **Icons:** extend the starter's `glyphs.js` with accurate SVG paths
  copied from a reference source. This is a maintenance burden; name it
  explicitly in the gallery set-notes so reviewers know.
- **Sparklines:** the starter's `charts.js` `sparkline()` is acceptable
  for simple polyline trends with no axes.
- **Full charts (bar/pie/area):** there is no good hand-rolled substitute.
  Raise this conflict with the user before building — a hand-drawn SVG
  bar chart is not an acceptable stand-in.
- **Dates, animation, grids:** implement only what the specific screen
  needs; do not build a general utility.

Record the constraint in the gallery's set-notes panel so reviewers
understand what they're looking at.
