---
name: components
description: 'Component-in-isolation half of a prototype project: a stories/ gallery beside prototype''s pages/, where every UI component is a JSON registry object (id, name, caption, states) rendered once per state as a card, showing component x state coverage instead of one happy screenshot. Reuses prototype''s architecture: thin HTML entry, JS-built DOM, one shared URL-state helper, layered CSS, clean-URL dev server. Live search shows only matched components; ''@state: disabled'' mirrors to ?show-only=disabled, rendering that state''s card only and hiding components lacking it; dir/theme/density are global facets. Root index.html becomes a two-card chooser over index.pages.html and index.stories.html. Asks whether stories import shared js/components/ renderers or clone them, and records the choice. Authors missing components (renderer, CSS, states), enforces state coverage (declared-but-unbranched and identical-props cards are defects; unreachable states are reported, never faked), and verifies by rendering every card URL.'
when_to_use: The user wants a component gallery / stories page, wants a component's states reviewed in isolation, mentions a registry of components with states, asks for `?show-only=` filtering, or is working inside a prototype project that has (or needs) a stories/ directory. Also /components.
argument-hint: "[project root] [component or facet to add]"
---

# Components - every component, every state, one page

`prototype` answers "what does the screen do?". This skill answers **"what does this component look like when
it is empty, disabled, validating, rejected, overflowing, or unknown?"** — which is the question a screen
screenshot can never answer, because a screen shows exactly one state at a time.

The unit of the page is **component × state**, rendered as a card. The page is a coverage matrix, not a
showcase: a component with three declared states and two cards is a defect with a visible hole.

## Where this lives — beside `prototype`, never inside it

```text
<project>/
├── index.html              # chooser: two cards -> Pages | Stories
├── index.pages.html        # prototype's gallery entry (was index.html)
├── index.stories.html      # THIS skill's entry: title, caption, search, cards
├── pages/                  # prototype: whole screens
│   └── <page>.html
├── stories/                # this skill: components in isolation
│   └── <component>.html    # optional per-component deep-link page (see 03)
├── js/
│   ├── _app.js             # shared bootstrap + THE ONE state helper (imported, not re-invented)
│   ├── components/         # shared renderers, if the project has them
│   ├── stories.registry.js # pure data: id, name, caption, states, facets, props
│   └── stories.js          # the shell: search, descriptor filter, section rendering
├── css/
│   ├── theme.css           # tokens (loaded first)
│   ├── _app.css            # shared
│   └── stories.css         # gallery chrome only — never component styles
└── serve.mjs               # clean URLs for all three entries, query preserved
```

Import and reuse everything `prototype` already provides. A second URL-state helper, a second theme, or a
copy of the button styles is the failure mode of this skill: the gallery must show **the** component, not an
impression of it.

## Step 1 - Read the project before writing anything

```bash
ls; ls js css pages stories 2>/dev/null; cat package.json 2>/dev/null
ls js/components 2>/dev/null                      # do shared renderers already exist?
grep -n "stateHelper\|URLSearchParams\|readState" js/_app.js | head
```

Establish: the existing state helper's API, the CSS layer order, the dev server's routes, the product's
default direction (an Arabic product is RTL by default — LTR is the variant), and which components the pages
already use.

## Step 2 - Ask the one decision that changes the architecture

**Renderer source.** If `js/components/` exists, the stories can import those renderers (single source of
truth: a component can never look different in a story than in a page) or clone/adapt them into
`stories/` (fast, and lets a story show states the pages never reach). **This is the user's call, not a
default** — ask it with the trade-off visible, and record the answer in the project. If there is no
`js/components/`, the question becomes: put renderers in a new shared layer now, or keep them story-local
until pages need them. See [`06`](references/06-integration-with-prototype.md).

Also ask only if genuinely ambiguous: which components belong in the first pass, and whether the project
wants per-component deep-link pages.

## Step 3 - Write the registry first, then the renderers

The registry is pure data and is the contract everything else obeys ([`01`](references/01-registry-schema.md)):

```js
{
  id: "numeric-field",
  name: "رقم ذو حدين",
  renderer: "numeric-field",
  caption: "قيمة رقمية + رسالة خطأ من الـ descriptor في الـ min/max/step",
  states: [
    { key: "valid",    label: "صحيح" },
    { key: "empty",    label: "فارغ" },
    { key: "invalid",  label: "خطأ",   note: "5000 فوق الحد 3600" },
    { key: "disabled", label: "معطل" }
  ],
  props: { valid: { value: 30, unit: "ثانية" }, invalid: { value: 5000 } }
}
```

Rules that keep it honest: `id` is kebab-case and stable (it appears in URLs); every state has a `key` the
renderer actually implements and a `label` in the product's language; `props` per state are realistic
subject matter — **never Lorem, never "Item 1"**; a state with no real trigger is not declared
([`04`](references/04-state-coverage.md)).

Then implement each renderer: one function, `(props, stateKey) => DOM`, using the project's tokens and the
same markup the pages use ([`07`](references/07-authoring-a-component.md)).

## Step 4 - Build the shell

`index.stories.html` is a thin entry; `js/stories.js` owns the DOM. Layout, top to bottom:

1. **Header** — theme toggles (light / dark / system), the gallery **title**, and a **caption** naming the
   model (each case has its own renderer and descriptor).
2. **Search box** — filters live; only matched components render, and the match covers `name`, `id`,
   `caption`, and state labels.
3. **Sections**, one per component: bold display name + a monospace identifier chip + caption, then the
   state-card grid.

Descriptor queries and URL state ([`02`](references/02-descriptors-and-url.md)):

| Input | URL | Effect |
|---|---|---|
| type in search | `?q=رقم` | only matching component sections render |
| `@state: disabled` (typed in the search box) | `?show-only=disabled` | every component renders **only** its disabled card; components without that state disappear |
| `@state: disabled, invalid` | `?show-only=disabled,invalid` | union of those cards |
| `@id: toggle` / `@name: مفتاح` | `?id=toggle` | that component only, all states |
| theme / `dir` / density switches | `?theme=dark&dir=ltr&density=compact` | whole gallery, including the components |

All of it flows through the shared state helper: initialize from the URL on load through the same render path
a click uses, write back on interaction, preserve unrelated params, invalid values fall to defaults, `replace`
history for keystrokes and `push` for discrete filter changes. A gallery URL is a review artifact — someone
must be able to paste `?show-only=error&dir=ltr` into a bug report.

## Step 5 - Facets: direction, theme, density

Components are styled with logical properties so `dir` is a real switch, not a re-render of the wrong
stylesheet; theme and density come from tokens, never from card-level overrides ([`05`](references/05-facets-dir-theme-density.md)).
Facets are **global** switches (`?dir=ltr` flips the gallery); states are **per-card**. A card that needs a
facet-specific variant declares it in the registry rather than duplicating markup in the shell.

## Step 6 - The root router

`index.html` becomes a chooser: two cards — **Pages** (screen prototypes) and **Stories** (components in
isolation) — each showing counts read from the registry/page list, linking to `/index.pages.html` and
`/index.stories.html`. Real `<a href>` navigation, clean URLs, query preserved; no redirect, no memory of the
last choice unless the user asks for it.

## Step 7 - Verify by looking, not by reasoning

```bash
node scripts/stories_check.mjs validate js/stories.registry.js   # schema, ids, states, props, duplicates
node scripts/stories_check.mjs coverage js/stories.registry.js --impl js/components
node scripts/stories_check.mjs urls     js/stories.registry.js --base http://localhost:5173 --out cards.txt
node scripts/stories_check.mjs --selftest                        # 14 checks on the tool itself
```

Then the part a script cannot do: **render every URL and look at it** (browser or screenshot). A state is
verified when seen, not when coded. Feed hostile input too — `?show-only=nonexistent`, a 90-character value, a
missing prop — the gallery must render an honest empty/unknown state and never fabricate a normal-looking card.
Full checklist: [`08`](references/08-verification.md).

## Boundaries

- **Never fake a state.** No shimmer where nothing loads, no disabled look applied by CSS filter to a
  component that has no disabled logic, no card that renders the same pixels under two different state keys —
  that is a duplicate declaration, and the checker reports it.
- **Never duplicate the component.** If a story needs different markup from the page, that is a finding about
  the component, not a license to fork it silently.
- **Never touch `pages/`** except to add the router link and, with permission, to consume a component the
  stories introduced.
- **No framework, no bundler.** ES modules, the project's own dev server, its package manager per lockfile.
- **Respect the prototype skill's rules** where they overlap (thin HTML, one state helper, CSS layer order,
  clean URLs, seeded `?filled` if the project uses it). This skill adds the gallery; it does not re-litigate
  the architecture.

## References

| File | Owns | Read when |
|---|---|---|
| [`00-what-a-story-is.md`](references/00-what-a-story-is.md) | Component×state cards, why isolation beats screen review, what a story is *not* (docs, marketing, a second page set) | Always, once |
| [`01-registry-schema.md`](references/01-registry-schema.md) | The registry object: fields, state entries, props, facets, naming and stability rules, validation contract | Writing or editing the registry |
| [`02-descriptors-and-url.md`](references/02-descriptors-and-url.md) | `@facet:value` grammar, `show-only` semantics and unions, search matching, URL write-back, defaults, history | Any filtering or URL work |
| [`03-shell-and-search.md`](references/03-shell-and-search.md) | `index.stories.html` + `js/stories.js`: header, caption, search behavior, section/card rendering, counts, empty states, per-component pages, performance | Building the shell |
| [`04-state-coverage.md`](references/04-state-coverage.md) | Deriving a component's state set, the coverage matrix, declared-vs-rendered defects, unreachable states, duplicate-pixel detection | Before claiming a component is done |
| [`05-facets-dir-theme-density.md`](references/05-facets-dir-theme-density.md) | RTL/LTR with logical properties, theme and density tokens, facet switches vs per-card variants, mixed-content pitfalls | Any dir/theme/density work |
| [`06-integration-with-prototype.md`](references/06-integration-with-prototype.md) | Shared vs cloned renderers (the question to ask), the three-entry router, routes, CSS order, avoiding a second state helper, what to import from `prototype` | Step 2 and Step 6 |
| [`07-authoring-a-component.md`](references/07-authoring-a-component.md) | Renderer signature, real states (attributes not paint), a11y and focus, copy rules, the story entry that proves it | Writing a new component |
| [`08-verification.md`](references/08-verification.md) | The check commands, the force-every-card sweep, hostile input, the delivery report | Before saying it works |

## Assets and script

- `assets/templates/` — `index.stories.html`, `index.html` (the two-card chooser), `js/stories.js`,
  `js/stories.registry.js`, `js/stories.renderers.js`, `css/stories.css`. Copy and adapt to the project's
  existing `_app.js` API; the template's local state wrapper exists only so it runs standalone and is deleted
  on integration. The template registry validates clean and its 16 cards pass the coverage check, so it is a
  working reference, not a sketch.
- `scripts/stories_check.mjs` — one Node tool, no dependencies. `validate` checks the registry contract (ids,
  state keys, labels, props keyed to declared states, unknown fields, facet defaults, and two states sharing
  identical props); `coverage` cross-checks every declared state against the renderer source — `--impl` takes a
  directory of per-component renderers or a single bundle file, and a state driven purely by data declares
  `via: "props"` so the tool checks the props differ instead of demanding a dead branch; `urls` emits one URL
  per card for the screenshot sweep. Exit 0 clean, 1 findings, 2 usage or import error; `--selftest` runs 14
  checks against the tool itself. ASCII output.
