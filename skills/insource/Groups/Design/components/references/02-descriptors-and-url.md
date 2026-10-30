# Descriptors and URL state

Two input channels, one state. The search box accepts **descriptors** (`@state: disabled`) as well as plain
text, and every effective view is written into the URL (`?show-only=disabled`). The URL is the durable form;
the box is a convenience that regenerates itself from it.

## Grammar

```text
@<facet>: <value>[, <value>…]        →  filter or switch, never a text search
<free text>                           →  text search
```

| Descriptor | URL | Effect |
|---|---|---|
| `@state: disabled` | `?show-only=disabled` | each component renders **only** its disabled card; components without it disappear |
| `@state: invalid, error` | `?show-only=invalid,error` | union of those states |
| `@id: toggle` | `?id=toggle` | that component only, all its states |
| `@name: مفتاح` | `?q=مفتاح` | text search (name is not unique, so it is a query) |
| `@dir: ltr` | `?dir=ltr` | facet switch, whole gallery |
| `@theme: dark` | `?theme=dark` | facet switch |
| `@density: compact` | `?density=compact` | facet switch |
| unknown `@foo: bar` | `?q=@foo: bar` | treated as text and reported as an unmatched descriptor in the empty state |

Rules:

- **State keys are language-neutral; labels are not.** `?show-only=disabled` works in an Arabic product; the
  badge reads `معطل`. Searching the label text must also find the state, so `matchesQuery` includes state
  labels and notes, while `show-only` matches `key` only.
- **Unknown state value:** render the empty state and name the bad value — never fall back to "show
  everything", which turns a typo into a false full pass.
- **`id` and `show-only` compose:** `?id=toggle&show-only=disabled` is the permalink form of a single card.
- Facet values must be in `meta.facets`; anything else falls to `meta.defaults` without breaking render.

## Filtering semantics (the part that gets built wrong)

```text
components → [id filter] → [text query] → [per-component state filter] → sections with ≥1 card
```

The state filter removes **cards**, and a section with zero cards is removed. So `?show-only=disabled` is not
"hide non-disabled components" and not "grey out other cards" — it is "one card per capable component". The
header count reports both numbers so the view is never ambiguous: `4 / 16` components shown of total.

## State helper: import, never re-invent

`prototype`'s rule is one central helper in `js/_app.js` and no page touching `URLSearchParams`. The stories
shell obeys it: the template carries a small local wrapper **only so it runs standalone**, and the header
comment says to delete it and import the project's helper. The wrapper's contract mirrors what the project
expects:

```js
state.read(key, fallback)                 // "" and null both mean "absent"
state.write({ key: value }, { replace })  // null/"" deletes the param; unrelated params survive
```

Requirements on top of that, identical to the prototype contract:

1. **Initialize from the URL** through the same render path a click uses — one code path, so a URL-loaded
   gallery is pixel-identical to the same view reached by typing.
2. **Write back on interaction** — every current view is bookmarkable, including the search box contents
   (regenerate the descriptor text from the params on load).
3. **Preserve unrelated params** — clearing `q` must not silently reset `theme`.
4. **Validate** — unknown facet values, unknown state keys, absurd lengths: fall back to defaults, keep
   rendering.
5. **History policy** — `replace` for keystrokes (a search box must not create 40 back-stops), `push` for
   discrete moves (facet switch, descriptor applied, permalink clicked), and `popstate` re-renders so
   back/forward restore the exact view.
6. **Re-render must not lose focus** — the shell rebuilds the header each render; restore focus and caret to
   the search input when it was the active element, or typing becomes impossible. That is the bug every
   URL-driven gallery hits once.

## What the URL is for

Review links. The delivery report should include a handful of ready URLs rather than "open it and click
around":

```text
/index.stories.html                                  everything
/index.stories.html?show-only=disabled               the disabled sweep
/index.stories.html?show-only=invalid,error          everything that can go wrong
/index.stories.html?dir=ltr                          the same gallery, opposite direction
/index.stories.html?id=numeric-field&show-only=invalid&theme=dark   one card, one bug report
```

`node scripts/stories_check.mjs urls js/stories.registry.js --base <dev-url> --out cards.txt` generates one
line per card so the force-every-card sweep is a loop, not an act of imagination.
