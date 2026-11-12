# Worked case: a web app (CSS + TypeScript)

One case, not a recipe. See `maui-token-layer.md` for a different paradigm (compiled desktop/mobile).

## Starting point (measured)

- Three themes (light, dark, a tenant brand) toggled by a `data-theme` attribute on `<html>`
- ~240 hardcoded hex values across CSS Modules/SCSS; ~60 inline styles in TSX; two canvas charts
  painting `#...` literals read at draw time
- No token file; a few “theme” constants duplicated between CSS and TypeScript
- Playwright already in the repo, but no visual baseline

## Decision: native CSS custom properties

Step 0 found no styling system in use — plain CSS Modules, inline styles, and literals — so the five
tests applied. Necessity failed for a styling library: custom properties plus `[data-theme]` already
provide reactive tokens. A CSS-in-JS theme provider was considered and rejected for this stack
(runtime/build coupling did not buy a missing capability); a component suite would be a separate
design decision, not a token decision. Recorded with the five tests.

If this project had already used Emotion or UnoCSS, Step 0 would have closed the question: the work
would have been to extend that library's theme/token config and migrate literals into it, not to
debate whether a library is appropriate.

## What was built

1. **One token table** (`tokens.css`): semantic roles (`--surface`, `--surface-raised`,
   `--text-primary`, `--border`, `--space-3`, `--radius-md`, `--motion-fast` …). Every value copied
   verbatim from current rendering; identical values collapsed; tenant-only values became scoped
   overrides on the same role names.
2. **Theme maps**: `:root` (light), `[data-theme="dark"]`, `[data-theme="tenant-x"]` — only role
   assignments, never component styles.
3. **Typed access for non-CSS consumers**: a small generated module exports the token names; canvas
   code resolves current values once per theme change (`getComputedStyle(document.documentElement)`),
   not per frame.
4. **Migration slices**: token file + theme maps → shared components → pages → inline styles → canvas
   drawing → native browser-chrome-adjacent styles (scrollbars, selection).
5. **Guards** in the existing harness: stylelint bans raw colors and numeric spacing in component
   CSS; an ESLint rule bans color literals in inline styles; a test asserts every `var(--token)` used
   in the repo resolves to a declared token; a token-shape test checks uniqueness and parses. Each
   check has a scanned-count floor.
6. **Parity**: Playwright captures at 3 themes × 4 pages × 2 viewports, with `reducedMotion: "reduce"`,
   a frozen clock, and seeded data. Baseline captured twice; the two-run delta identified one live
   clock and one animated gradient region, which were masked in a tracked file. The final diff was
   zero outside them.

## Before / after

```css
/* before: the value is decided at the consumption site */
.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
}

/* after: the value is named once, written once */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
}
```

```tsx
// before
<div style={{ color: "#0f172a", padding: 12 }} />
// after
<div className={styles.body} />
// body { color: var(--text-primary); padding: var(--space-3); }
```

## Portable lessons

1. **Identical-value mapping is the safety mechanism.** Mechanical conversion, never hand-typed values.
2. **Theme maps assign roles; components consume roles.** A component that names a raw color is a bug,
   even if it lives in a theme file.
3. **Non-CSS consumers need an accessor.** Canvas, WebGL, and chart libraries must resolve tokens once
   per theme change, not per frame.
4. **A mask requires proof.** Only mask regions that differ between two runs of the same build.
5. **Guards belong in the existing linter/test harness**, with a floor so a scan cannot pass vacuously.
6. **Spot-check the final build.** The capture build and the shipped build can differ.

## Same invariant elsewhere

Whether the platform is [CSS custom properties], [MAUI/WinUI dynamic resources], [Compose theme +
composition locals], [React Native theme context], or [SwiftUI environment values], the shape is the
same: values exist once, consumers reference roles, and a source check makes new literals fail the
build.
