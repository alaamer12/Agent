---
name: dashboard
description: Build calm, production-grade admin and analytics dashboards using a reusable collapsible-rail shell, 1-column full-width tonal zone stack, smooth UI easing, and synchronized ApexCharts animations. Use whenever the user asks to design, scaffold, prototype, or build a dashboard, admin panel, analytics console, KPI view, reporting interface, or data-heavy web app, or wants an HTML/React dashboard with charts, tables, and polished motion.
---

# Dashboard

Build structured, zero-glare admin and analytics dashboards anchored by a reusable HTML template (`templates/dashboard-template.html`), disciplined tonal surface layering, crisp exponential ease-out transitions, and coordinated chart animations. Customize the color palette and main section components freely for each domain while keeping the layout grammar and motion feel consistent.

## When to Use

- Building a new admin panel, analytics workspace, operations console, or executive reporting dashboard.
- Prototyping an interactive single-file HTML dashboard with live charts, filterable tables, modals, and state previews.
- Standardizing layout rhythm, responsive navigation, and animation behavior across multi-view data interfaces.
- Designing dashboards that need Production, Empty, and Loading states out of the box.

## Core Design and Layout Architecture

Start from `templates/dashboard-template.html` and adapt its routes, components, and CSS tokens to the user's domain.

### 1. Application Shell

- **Collapsible Left Rail**: Fixed sidebar (`280px` expanded, `76px` collapsed icon-only mode). In collapsed mode, nav labels turn into dark floating flyout pills on hover or keyboard focus.
- **Mobile Drawer (`< 960px`)**: Sidebar slides off-canvas (`translateX(-100%)` to `0`) behind a dimmed backdrop with keyboard `Escape` support and focus management.
- **Sticky Topbar (`68px`)**: Displays the active monospace route slug, an optional status/refresh pill, and a 3-option segmented state switcher (`Production`, `Empty`, `Loading`) for instant state previews.
- **Elevated Page Surface**: Main work area centers a `max-width: 1360px` canvas containing a single `.page-surface` card (`border-radius: 18px`), page title/subtitle header, and a **1-column full-width vertical stack** (`.page-stack`, `gap: 24px`).

### 2. Zero-Glare Tonal Layering and Flexible Palette

Avoid harsh `#FFFFFF` glare and heavy drop shadows. Instead, establish a 4-step tonal ramp via `:root` CSS variables so any color palette stays calm and legible:

1. `--canvas-bg`: Outermost page canvas (cool/warm neutral tint).
2. `--surface-bg`: Main page sheet elevated with a subtle border (`rgba(..., 0.08)`) and whisper shadow.
3. `--zone-bg`: Full-width `.wf-zone` section bands (`border-radius: 16px`, `padding: 28px`) that group related controls, charts, or tables.
4. `--chart-surface`: Cleanest inner layer for `.chart-surface`, `.data-card`, and `.table-wrap` containers.

**Swapping the palette**: Replace `--rail-*`, `--canvas-bg`, `--surface-bg`, `--zone-bg`, `--chart-surface`, `--ink-*`, `--accent*`, and `--status-*` tokens in `:root`, and mirror the updated accent/neutral hex values in chart `colors` arrays. Keep the same luminance steps and contrast ratios (minimum 4.5:1 for body text) whether using slate-indigo, warm stone-terracotta, forest-emerald, ocean-teal, or a dark surface ramp.

### 3. Typography and Tabular Precision

- **UI Font**: Geometric sans (`Plus Jakarta Sans` or similar clean sans) at `15px` base, `1.6` line-height, and tightened headings (`letter-spacing: -0.025em`).
- **Metrics and Slugs**: Monospace (`JetBrains Mono`) paired with `font-variant-numeric: tabular-nums` on KPI values, route slugs, timestamps, percentages, and numeric table columns so numbers align cleanly during updates.

## Motion, Easing, and Chart Animation System

Motion should feel crisp, damped, and purposeful - never bouncy or sluggish.

### 1. UI Easing and Timing Tokens

- **Primary curve**: `--ease-out: cubic-bezier(0.22, 1, 0.36, 1)` (fast start, smooth decelerated settle with zero overshoot).
- **Standard UI duration**: `--t-ui: 160ms` for sidebar collapse (`width`, `margin-left`, `transform`), drawer backdrop fade, button/tab backgrounds, and nav active states.
- **Floating tooltips**: `140ms var(--ease-out)` combining opacity and a `4px` vertical rise (`translateY(4px)` to `0`).
- **Toast notifications**: `200ms var(--ease-out)` entrance (`translateY(10px)` to `0`) and `180ms ease` fade-out on dismiss.
- **Reduced motion**: Always include `@media (prefers-reduced-motion: reduce)` to disable non-essential transitions and chart animations when requested by the user's OS.

### 2. Chart Animation Rules (ApexCharts)

Use a shared `baseChartOpts(height)` factory so every visualization speaks the same motion language:

- **Initial mount animation**: `animations: { enabled: true, easing: 'easeinout', speed: 320, animateGradually: { enabled: true, delay: 45 }, dynamicAnimation: { enabled: true, speed: 240 } }`. Keep speeds between `240ms` and `360ms` so charts feel responsive rather than slow.
- **Respect reduced motion**: Check `window.matchMedia('(prefers-reduced-motion: reduce)').matches` inside `baseChartOpts` and set `animations.enabled = !prefersReducedMotion`.
- **Clean lifecycle teardown**: Track mounted chart instances in an `activeCharts` array and call `destroyCharts()` before every route change or full re-render to prevent memory leaks and orphaned resize observers.
- **Smooth sidebar-collapse reflow**: After toggling desktop rail collapse (`160ms` transition), dispatch `window.dispatchEvent(new Event('resize'))` after a `200ms` timeout so all visible charts smoothly animate to the new container width without mid-transition jank.
- **Consistent visual chrome**: Use transparent chart backgrounds (`background: 'transparent'`), subtle dashed horizontal gridlines (`strokeDashArray: 4`, low-alpha border), top-left legends, `borderRadius: 4` to `6` on bars, `curve: 'smooth'` for trend lines (or `'stepline'` for survival/step data), and hidden toolbars unless export is explicitly needed.

## Adapting Main Sections

Swap the inner `.wf-zone` blocks to match the user's domain rather than forcing fixed widgets:

- **KPI Strips**: 4-column responsive grid (`grid-cols-1 sm:grid-cols-2 xl:grid-cols-4`) of `.data-card` items inside a top `.wf-zone`.
- **Charts**: Mixed bar+line pulse charts, multi-series area charts with threshold annotations, bubble/scatter matrices, dumbbell range comparisons, 100% stacked composition bars, and 24x7 heatmaps inside `.chart-surface`.
- **Data Tables**: Fixed-layout tables (`.calm-table.calm-table-fixed`) inside `.table-wrap` with single-line truncation (`.cell-truncate`) wired to a single body-level `#global-tooltip` (`position: fixed; z-index: 9999`) so hover previews never clip inside scrollable containers.
- **Interactive Controls**: Filter pills, search inputs, range sliders, CSV export actions, detail inspection modals, and configuration forms.

## Workflow Steps

1. **Read the user's domain requirements**: Identify the navigation groups/routes, target palette mood, key metrics, chart types, and interactive filters needed.
2. **Inspect the starter template**: Reference `templates/dashboard-template.html` for the complete shell, CSS tokens, tooltip engine, chart lifecycle helpers, and state switcher.
3. **Customize the palette tokens**: Update `:root` variables and chart series colors to fit the requested brand or visual mood while preserving the 4-tier tonal ramp and contrast.
4. **Compose domain sections**: Replace demo routes, KPI cards, charts, tables, and controls with domain-specific components. Keep every section inside full-width `.wf-zone` containers.
5. **Verify motion and responsiveness**: Confirm `destroyCharts()` runs on view switch, resize reflow fires after rail collapse, `#global-tooltip` works on truncated table cells, Empty and Loading states render cleanly, and `prefers-reduced-motion` is respected.

## Gotchas

- **Do not trap tooltips inside `.table-wrap`**: Overflowing horizontal scroll containers clip child tooltips. Always use the viewport-positioned `#global-tooltip` helper with `data-tooltip` attributes.
- **Do not skip `destroyCharts()`**: Re-mounting ApexCharts onto the same or replaced DOM nodes without destroying prior instances causes broken hover tooltips and choppy animations.
- **Do not over-animate charts**: Setting animation speed above `500ms` or using bouncy easing (`elastic` / `bounce`) makes analytical dashboards feel toy-like and slows down filter exploration.
- **Keep contrast intact when re-theming**: If switching to a dark palette, invert the tonal ramp so `--canvas-bg` is deepest, `--surface-bg` is slightly lighter, `--zone-bg` and `--chart-surface` step upward cleanly, and ApexCharts `tooltip.theme` switches to `'dark'`.
