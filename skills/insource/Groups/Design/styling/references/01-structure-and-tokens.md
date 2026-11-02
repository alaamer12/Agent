# Structure and tokens

Options in [brackets] are illustrative starting points, not mandates; pick the mechanism the
platform actually gives you.

## 1. No monolithic style file

One stylesheet for the whole app fails the same way on every platform: nobody can tell what a rule
affects, dead rules accumulate invisibly, and two unrelated pages fight over one selector.

The shape that survives growth:

```text
shared/
  tokens     one file: all values + theme maps
  base       reset/normalize, element defaults, font loading
  utilities  the small repeating patterns only
pages|modules/
  <module>   its own style scope, loaded with its module
```

Native scoping mechanisms — use the one your stack provides instead of inventing naming rituals:

- Web: [CSS Modules], [one plain stylesheet per page with a BEM/namespace convention], [framework
  co-located styles]
- Blazor: [`.razor.css` isolation — the compiler scopes each component's file automatically]
- MAUI/WinUI: [per-feature XAML `ResourceDictionary`/`Styles.xaml` merged in app-level or page
  level], not one 3,000-line App.xaml
- Qt: [one QML file per type is already the scope]; shared looks go through [Qt Quick Controls
  style overrides / a shared `QML Styles` module]

Rule of thumb: if deleting a page orphans style rules, those rules belonged to that page's file.
If a rule is used twice, it earns a place in the shared core — as a named utility, not a duplicate.
How the shared core itself is cut into layers (values, compiled tokens, mixins/functions, composed
styles) and which layer may import which: `04-layer-chain-and-naming.md`.

## 2. The token layer as single source of truth

Adopted from the same model `styleup` enforces for migrations; when writing new styling you get to
do it right on day one.

- **Role names, not value names.** `surface-raised`, `text-secondary`, `border-strong` — not
  `slate-900` or `blue-2`. A value named after itself invites a second copy under a new name when
  the design changes.
- **Full coverage, not colors only.** Color, type scale (sizes + line heights), spacing, radii,
  elevation/shadow, border widths, motion durations. The category you skip is the category that
  gets hardcoded.
- **Theme = role reassignment.** Light/dark/brand/tenant variants are maps that reassign the same
  role names ([`:root` + `[data-theme]` blocks], [MAUI dynamic resource dictionaries swapped per
  theme], [Blazor: a theme attribute driving different custom-property sets], [QML: a singleton
  object of role properties, or control `style` overrides]). No component contains theme logic.
- **Aliases only when the role genuinely differs.** Two roles with today's same value are fine;
  one role copied under two names because someone was nervous is not.
- **Non-style consumers read tokens too.** Chart libraries, canvas drawing, native chrome: resolve
  the token once per theme change through the platform's accessor ([getComputedStyle], [DynamicResource
  lookups], [QML property access]) — never re-typing the literal.

The token file is the only place a raw value may appear. Everything else references it. That is
the one-line version of this whole skill; `styleup` exists to retrofit projects that broke it.

## 3. Utilities: minimal, common, layered

Utilities are the shared vocabulary between the token layer and components. Keep them small and
honest:

- **Only patterns that repeat.** A utility used once is a component style in disguise.
- **Semantic intent, not raw property dumps.** `card` (surface + border + radius + padding as a
  role) is worth having; fifty `.mt-{n}` clones of the margin property are a parallel language
  that competes with tokens. [A numeric spacing scale utility is legitimate when spacing repeats
  everywhere; a color-arbitrary utility set usually is not.]
- **Layering via extension/composition, never duplication.** Define the base once, then thin
  upper classes:

```css
/* base: the common pattern, token-consumed */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: var(--space-4);
}

/* upper layers: only the delta from the base */
.primary-card   { border-color: var(--border-strong); box-shadow: var(--elevation-1); }
.secondary-card { background: var(--surface-muted); }
```

Same idea on the other platforms: [XAML `Style BasedOn`], [Blazor: apply `card` and add the
variant class], [QML: `inherit` / attached style properties / a base component the variants
configure]. The upper layer restates only what differs; if a variant redefines the whole base,
the base was wrong.

- **Variants are names, not flags.** A component exposes which variant it uses; the visual delta
  lives in the style layer. Ten boolean style props on a component (`raised`, `muted`, `bordered`,
  ...) are utilities leaking upward into the API.
