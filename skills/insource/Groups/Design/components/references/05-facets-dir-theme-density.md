# Facets: direction, theme, density

A **facet** changes the whole gallery — every component at once. A **state** changes one card. Mixing them up
produces either a card list that duplicates itself per theme, or a theme switch that only restyles the chrome
while the components stay light.

```text
facet  → global, in the URL, flips everything        ?dir=ltr&theme=dark&density=compact
state  → per card, declared in the registry          ?id=toggle&show-only=disabled
```

## Direction (`dir`)

The product's own direction is the **default**, not the interesting case. For an Arabic product, `dir=rtl` is
what every review sees and `?dir=ltr` is the probe that finds the bugs.

What actually breaks, in observed order:

1. **Physical properties.** `margin-left`, `padding-right`, `left: 12px`, `text-align: right`,
   `border-radius: 8px 0 0 8px`. Replace with logical: `margin-inline-start`, `inset-inline-start`,
   `text-align: start`, `border-start-start-radius`. This is why `stories.css` in the template uses logical
   properties everywhere, including the chrome.
2. **Icons with direction.** Chevrons, back arrows, breadcrumb separators must mirror. Glyphs that must *not*
   mirror: play, refresh, external-link, sort carets that encode ascending/descending numerically.
3. **Number and mixed runs.** Latin identifiers, URLs, and numbers inside Arabic sentences need bidi
   isolation (`unicode-bidi: isolate` or `<bdi>`) or the `q<<script>` example lands on the wrong side of the
   colon. Test with a value that starts with Latin letters.
4. **Asymmetry by design.** A card whose error slot sits on one side, a slider whose value label sits at the
   end — in RTL these must move together, or the label reads as belonging to the wrong control.
5. **Typography.** Arabic needs a font stack with Arabic coverage and more line-height; a Latin-only stack
   silently falls back and the card looks cramped. Never fix this per component — it belongs in `theme.css`.

Per-component exceptions are declared, not hardcoded:

```js
{ id: "code-editor", facets: { dir: ["ltr"] } }   // code is LTR regardless of product direction
```

## Theme (`light` / `dark` / `system`)

- Set `data-theme` on the root and let `theme.css` tokens do the work; `system` resolves via
  `prefers-color-scheme` and must be visibly distinct from both fixed values in the switch UI.
- `color-scheme: light dark` on the root so native controls (number spinners, scrollbars, form inputs) follow.
  A dark gallery with a white native dropdown is the classic miss.
- Components must not hardcode colors. Any hex inside `stories.css` or a component rule is a bug; the gallery
  is precisely the tool that makes it visible, because the same card renders twice under two themes.
- Contrast is checked in both. A disabled state that is legible on white is often invisible on the dark
  surface — and *disabled must stay readable*, which is a design requirement, not an accident.

## Density (`comfortable` / `compact`)

Drive it from tokens (`--story-gap`, control height, font size, radius) with one attribute on the root:

```css
:root[data-density="compact"] { --control-h: 28px; --story-pad: 12px; }
```

What density actually tests: text truncation, wrapping of long Arabic labels, whether an error message still
fits under its field, whether a chip row collapses gracefully, and whether an icon-only button keeps a 24px
hit target when the row shrinks. Those are the bugs it exists to find; a density switch that changes nothing
was not a facet the components were designed for — say so and drop it rather than keeping a dead switch.

## Composing facets with states

Facets are orthogonal: `?show-only=invalid&dir=ltr&theme=dark` must render the invalid card in LTR dark.
Two implementation rules make that cheap:

1. Facets live on the **root element**, never baked into a card's markup or class list.
2. Renderers are pure functions of `(props, stateKey)` — they must not read the theme to decide how to look.
   A renderer that branches on `document.dataset.theme` has duplicated what CSS already does, and it will
   disagree with the gallery on refresh.

Caching caveat: if a renderer's element is cached per `(component, state)` for performance, a facet change
must invalidate it or the theme switch appears broken for everything already on screen.
