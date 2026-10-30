# The shell: `index.stories.html` and `js/stories.js`

The shell owns chrome and routing. It owns **no component markup and no component styles** — the moment it
starts hand-building a "nice looking" card body, the gallery is showing the shell's opinion of the component.

## Page anatomy, top to bottom

```text
┌ controls: facet switches (dir · theme · density) ─────────────┐
│ Title                                    (h1, one line)        │
│ Caption        "renderer + descriptor لكل حالة"               │
│ [ search box ]                       count: 4 / 16 components  │
├────────────────────────────────────────────────────────────────┤
│ SectionHeader  `section-header`                    ← name + id │
│ caption one line                                               │
│   ┌ card: صحيح ─┐   ┌ card: معطل ─┐   ┌ card: خطأ ─┐          │
├────────────────────────────────────────────────────────────────┤
│ … one section per matched component …                          │
└ empty state when nothing matches ──────────────────────────────┘
```

The header is rebuilt on each render because the count and the active facet buttons change. Two consequences
that must be handled or the page feels broken:

- **Focus loss.** After `replaceChildren()`, restore focus and caret to `#stories-search` if it was the active
  element, or typing one character moves the cursor to the end of a fresh input and eats the next keystroke.
- **No flicker on keystrokes.** Search filtering is a re-render of the same tree; keep it cheap (see
  performance below) and write the URL with `replace`.

## The thin HTML entry

Only metadata, stylesheet links in layer order, `<body data-page="stories">`, a `<noscript>`, and one module
script. No markup for cards, sections, or the header — the shell builds all of it. This is `prototype`'s rule
and the gallery is not an exception to it.

```html
<link rel="stylesheet" href="/css/theme.css">
<link rel="stylesheet" href="/css/_app.css">
<link rel="stylesheet" href="/css/components.css">
<link rel="stylesheet" href="/css/stories.css">
```

`components.css` before `stories.css`: component styles are the subject; gallery chrome sits on top and must
never win a specificity fight against a component.

## Search behavior

Match against `id`, `name`, `caption`, and every state's `key`, `label`, `note`. Case-insensitive; for Arabic,
normalize the light-hamza and tatweel variants so `اكدا` finds `الإعدادات` — over-normalize and you get
matches nobody asked for, so keep it to: casefold, strip tatweel, collapse repeated diacritics, and match
substring. No fuzzy matching: a reviewer who typos should see the empty state and correct it, not a list of
near-misses they must re-verify.

A match on a **state label** must not silently filter cards: typing `معطل` narrows which *components* appear
but shows all their states, while `@state: disabled` narrows the *cards*. The distinction is visible in the
header count and in the URL (`?q=` vs `?show-only=`), and it is the one interaction people mis-guess — so
label the search placeholder with both forms.

## Card rendering

```js
function renderComponent(component, stateKey) {
  const props = component.props?.[stateKey] ?? {};
  try { return resolveRenderer(component)(props, stateKey); }
  catch (err) { return errorCard(component, stateKey, err); }   // one broken card never blanks the gallery
}
```

Three rules:

1. **A missing renderer is a visible failure**, not an empty box: a dashed placeholder naming the renderer id
   and where to add it. Silent empties are how a gallery ends up with 60 cards and 12 components.
2. **A throwing renderer is contained.** Catch per card, name the component and state, keep the rest of the
   page alive. The error card is also a finding for the report.
3. **Every card carries a permalink** to `?id=…&show-only=…` with the active facets preserved. That link is how
   a design review becomes asynchronous.

## Per-component pages (optional)

`stories/<component>.html` gives a component its own clean URL (`/stories/toggle`) — useful when a review
thread is about one component. It is the same shell with `?id=` applied by the page itself, not a second
implementation:

```html
<body data-page="story" data-component="toggle">
```

and the shell reads `document.body.dataset.component` as the default `id`. Skip these until someone asks for a
linkable single-component view; a directory of 40 near-identical HTML files is the chaos this skill exists to
prevent.

## Performance

The gallery renders from a data array; keep it boring until it hurts.

- Under ~50 components, full re-render on every keystroke is fine.
- Beyond that: debounce the input (~120 ms), build sections lazily with `requestIdleCallback` or chunked
  `requestAnimationFrame`, and skip rendering cards below the fold with one shared `IntersectionObserver`.
- Never virtualize the *first* screen: the point of the page is to be scanned visually, and a virtualized
  gallery that re-renders while scrolling makes state comparison impossible.
- If a renderer is expensive (charts, big tables), cache its element per `(component, state)` and reuse it
  when the same view is re-rendered — but invalidate the cache when a facet changes, or the theme switch will
  appear to do nothing.
