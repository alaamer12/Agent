# Integration with `prototype`

This skill is a second entry into the *same* project. It does not create a parallel app: it adds a directory,
two entries, and a router — and reuses everything else.

## The file contract

```text
<project>/
├── index.html              # chooser: two cards (Pages | Stories) — replaces the old gallery entry
├── index.pages.html        # prototype's gallery, renamed from index.html
├── index.stories.html      # this skill's entry
├── pages/                  # prototype (unchanged)
├── stories/                # this skill: optional per-component deep links only
├── js/
│   ├── _app.js             # THE state helper — imported here, never copied
│   ├── components/         # shared renderers, if the project has them
│   ├── stories.registry.js # pure data
│   ├── stories.renderers.js# the seam (imports, or the cloned implementations)
│   └── stories.js          # shell
├── css/
│   ├── theme.css → _app.css → components.css → stories.css
└── serve.mjs               # routes for all three entries, query preserved
```

Rename `index.html` → `index.pages.html` **only** after adding routes for all three, or every existing
bookmark 404s. `serve.mjs` needs:

```js
"/":            index.html
"/pages":       index.pages.html      // and /<page> → pages/<page>.html as before
"/stories":     index.stories.html
"/stories/<c>": stories/<c>.html       // only if per-component pages exist
```

Query strings pass through unchanged — the gallery is useless without `?show-only=` surviving the server.

## The renderer question — ask, do not assume

**This is the user's decision, and the agent must ask it** before writing any renderer.

| Mode | When it fits | What it costs |
|---|---|---|
| **A. Shared** — `js/components/<id>.js`, imported by both pages and stories | the project already has `js/components/`, or the components are genuinely reused | pages must be refactored to consume the shared module; the first pass is slower |
| **B. Cloned** — implementations live in `js/stories.renderers.js`, copied from the page markup | the component exists only inside a page module today, and extracting it now would touch code the user did not ask to touch | drift: the gallery can show a state the real page cannot produce, and it looks authoritative |
| **C. Hybrid** — shared by default, story-local only for states the pages never reach | a component with a real state the product cannot currently trigger | needs the exception marked per card, or the gallery becomes a lie with good manners |

How to ask it, concretely, once the repo has been inspected:

> `js/components/` does not exist; `toggle` is currently built inline in `pages/settings.js:88`. Either (A) I
> extract it into `js/components/toggle.js` and have the page import it — the gallery and the settings screen
> then cannot disagree, but the page file changes; or (B) the story clones the markup now and we accept that
> the two can drift until someone extracts it. Which do you want?

If the user picks B, mark it in code (`fn.storySource = "cloned-from:pages/settings.js:88"`) and list every
cloned component in the delivery report as drift risk. `stories_check.mjs coverage --impl <bundle-file>` prints
that warning automatically.

## What to reuse, aggressively

| Thing | Reuse rule |
|---|---|
| State helper | import from `_app.js`. Two helpers means two ideas of what `?theme=` means; the template's local wrapper is deleted on integration |
| Theme tokens | `theme.css` only. A story-level color literal is a bug |
| Component CSS | `components.css` (or the project's equivalent) — `stories.css` styles the *chrome*, never the subject |
| Glyphs, charts, formatters | the existing shared modules; do not re-implement an icon set for a card |
| Viewport/frame rules | `prototype`'s `references/viewport-frames.md` — frameless, same dimensions |
| `?filled` | if the project uses seeded fill, stories inherit it: a card's props may reference the seeded generator rather than hardcoding a long string |
| Package manager, dev server, tests | the project's, detected from the lockfile |

## Boundaries with the sibling skill

- `prototype` owns screens, flows, page modules, and the screen-vs-state judgement.
- This skill owns the registry, the gallery shell, descriptor filtering, and component-level state coverage.
- Neither owns the component's *design*; both consume it.
- When `prototype`'s gallery (`index.pages.html`) already shows state chips in iframes, that is screen state.
  The stories page shows **component** state. Keep the two concepts in different files, and never let a story
  chip point at a page URL — the permalink for a card is `?id=&show-only=`.

## Migrating an existing project

1. Add `index.stories.html`, `js/stories.*`, `css/stories.css`. Nothing else changes yet.
2. Register the components that already exist, cloning renderers if that is the mode chosen.
3. Only then rename the root entry and add the chooser. Do it last, because it is the only step that can break
   an existing link.
4. Re-run the dev server's route checks (`curl -o /dev/null -w "%{http_code}"` per entry, with a query string,
   and after refresh).
