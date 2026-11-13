# The Gallery Index

> In the `prototype` architecture the gallery is the project-root `index.html`,
> previews embed routed clean URLs (`src="/funds?open=error&error=permission"`), and chips
drive real iframe query params through the same state helper the pages use.
> Everything else below applies unchanged.
> **What this owns:** the `index.html` that ships alongside a multi-screen set — its anatomy, the three rules that keep it honest, and the acceptance test. The device dimensions a preview embeds at are [`viewport-frames.md`](viewport-frames.md)'s concern; the state model itself is [`query-param-states.md`](query-param-states.md)'s. This file assumes both and covers only the gallery.

When a mockup set has **two or more distinct screens**, deliver one extra file alongside them:
`index.html` — a single page that shows every screen live, every state of every screen, and the
notes that explain what each screen decides.

This is not a nice-to-have and not a "readme". It is the review surface. Without it, a set of
six screens is six tabs to click through and a state list that lives in someone's head; with it,
the whole set and all of its states are one scrollable page, and every cell of it is a URL you
can hand to somebody.

**Build it whenever the set has 2+ screens. Skip it for a single screen** — one card next to one
screen is noise, and that screen's own states are already reachable by URL.

## Anatomy

Four parts, in this order:

1. **Header** — what the set is, who it's for, and a link to the spec it implements (a docs
   file, a design system, a ticket). In a **Multi-App Suite**, the header states the suite's purpose
   and lists the participating applications (e.g. `Admin Portal`, `Operator Console`, `Mobile Web App`).
   One badge stating fidelity/source if that matters to the reviewer ("built to Material 3 density", "pixel-matched to staging").
2. **App Sections & Screen Cards.**
   - In a **Single App**: one scrollable list of cards, one card per screen.
   - In a **Multi-App Suite**: cards are grouped under clear section headers per application (`### Admin Portal (/admin)`, `### Operator Console (/operator)`). Each app section showcases its screens, viewport aspect ratio (desktop vs native mobile), and persona notes.
   - Each card, top to bottom:
     - a **live iframe preview** of the actual screen file (not a screenshot — a screenshot goes
       stale the moment you edit the screen);
     - a **tag** — where the screen sits in the product (`Tab 2 • /tabs/search`, `Sub-screen •
       /more/settings`, `Pre-tab • first launch only`, or `Admin • /admin/overview`);
     - **title**;
     - **notes** — 2–4 sentences on what this screen *decides*, in the product's real vocabulary;
     - an **Open Screen** link (full size, new tab);
     - a **state strip** — one chip per declared state preview, driving the preview's URL.
3. **A set-level notes panel** at the bottom — the rules that bind all the screens (tokens,
   laws, constraints), each with its source. In a multi-app suite, this explicitly details the
   shared design system tokens in `/shared/css/theme.css` and the theme differences between apps.
4. Nothing else. No nav, no sidebar, no filter UI on the gallery itself.

## The three rules that make it work

### 0. Layout — breathing room, no crowding

The gallery grid uses **at most 3 columns**. Use `repeat(auto-fit, minmax(320px, 1fr))` on the
grid container (never `minmax(240px, 1fr)` or narrower, which forces 4+ columns on wide viewports
and crowds the cards). Set `gap` to at least 24px and card body padding to at least 20px so each
card has genuine breathing room.

**Preview iframes must not show scrollbars.** The fix lives on the *screen*, not the gallery:
the screen's main scroll container applies `scrollbar-width: none` and `::-webkit-scrollbar { display: none; }`.
The gallery preview box adds `overflow: hidden` as a safety net. Neither side alone is sufficient;
both must be present.

```css
/* in the screen's own CSS */
.scroll-container {
  overflow-y: auto;
  scrollbar-width: none;        /* Firefox */
}
.scroll-container::-webkit-scrollbar { display: none; }  /* Chrome/Safari */

/* in the gallery CSS — safety net only */
.preview-box { overflow: hidden; }
```

### 1. The state list has exactly one owner

The gallery must never hand-type a list of state ids. If it does, it drifts from the screens
within an edit or two, and a drifting gallery is worse than no gallery — it lies with
confidence.

The screens have to render every component state standalone by URL anyway, which means the
state inventory must live in the data file the *pages* are built from. So: `specs.js` owns each
page's spec AND a `*_GALLERY` preview list of labeled state-URLs; the gallery imports that same
file purely to render one chip per entry. Adding a state to a page's tree then makes its chip
appear with no gallery edit.

For a two-screen set with three states each and no shared file, a literal table in the gallery
is acceptable — but it must be the copy the screens read from, not a transcription.

```js
// gallery: chips are generated, never typed
const previews = PREVIEWS[page.url];             // same specs.js the page modules read
previews.forEach(p => makeChip(p.label, p.query));
```

### 2. Preview at the real viewport, then scale — never squeeze

The classic failure: a 480px-tall iframe box holding a screen that lays itself out to `100vh`.
The page believes the phone is 480px tall, so absolutely-positioned headers and pill rows collide
with content that has nowhere else to go, and the reviewer is judging a composition that does not
exist. The preview must be the device's real viewport, scaled down as an image.

```css
.preview-box { aspect-ratio: 412 / 850; overflow: hidden; }   /* true device ratio */
.preview-box iframe {
  width: 412px; height: 850px;                                 /* real viewport */
  transform: scale(0.62); transform-origin: top left;          /* shrink the bitmap */
  border: 0; pointer-events: none;                             /* scroll stays with the page */
}
```

Set the scale from the card width, and keep the ratio matching what the screens were sized for
(see `viewport-frames.md`). `pointer-events: none` is correct — the gallery is for looking;
interaction happens in the opened tab. If the screens post navigation messages to a parent,
the gallery should listen and route them, or the protocol is dead code.

### 3. Screens stay chrome-free; the gallery carries the controls

Never put a state switcher, a debug bar, or a "STATE: error" ribbon inside a screen file. In
multi-app suites, **never put cross-app navigation buttons in the page's main layout**. The
screen must screenshot clean, because screenshots of these files get pasted into specs and PRs.
The gallery is the primary place with UI about UI, while live cross-app switching is handled by
the Dev Dock's Apps tab (`?dock=hide` removes it — see [`prototype-dock.md`](prototype-dock.md)). The one exception in the gallery is the `Open Screen` link,
which lives in the card and simply carries the currently-selected state through:

```js
launch.href = page.url + previews[i].query;      // chip click updates both preview and link
// urls are CLEAN routes ("/funds"), not file paths
```

## Notes: what goes in them

Card notes describe **decisions and constraints**, not appearance. "Vertical swipe feed, topic
pills, no subscribe-plus — following is topics, not creators" is a note. "Dark theme with a
bottom nav" is a caption, and worthless.

Write them the way you'd want them written if you were implementing the screen and had never
seen it: which law it satisfies, which data it reads, what deliberately isn't there and why.
Every note should be traceable to a spec, or it's an opinion.

Ground all labels and copy in the real subject matter — the same rule as everywhere else in this
skill. If the app has an i18n file, quote its actual strings rather than paraphrasing them.

## Naming and placement

- The gallery is `index.html`, in the same folder as the screens, so relative `src="search.html"`
  and `assets/…` paths just work and the whole folder can be served or opened from disk.
- Screens link back to it with a relative `href="index.html"` if they carry any chrome that
  invites comparison; otherwise leave them self-contained.
- Shared kit files (`specs.js`, `theme.css`, tokens) are loaded by the gallery exactly as the
  screens load them — that shared ownership is what keeps rule 1 true.

## Acceptance test

Before delivering a set with a gallery:

1. Open `index.html`. Every screen renders at its true aspect ratio, nothing overlapping.
   The grid has **at most 3 columns**; cards have visible breathing room.
2. **No scrollbar is visible inside any preview iframe.** If one appears, the screen's
   scroll container is missing `scrollbar-width: none` / `::-webkit-scrollbar { display:none }`.
3. Click each chip in each strip. The preview changes **and** the iframe's URL query changes to
   match — a chip that changes the DOM without changing the URL is not reachable by link, which
   breaks the skill's core contract. Deep component states (`?open=loading&loading=header`) must
   each have a chip: the strip is the visible state inventory.
4. Click the **`Filled`** chip on every card. The preview must show a **full** dataset —
   long tables, many rows, crowded content, wrapped names. If the preview looks almost
   identical to the empty state, `?filled` was not implemented.
5. Copy a preview's URL into a fresh tab. It renders that state with no clicks.
6. Delete a preview entry from `specs.js`. Its chip must disappear from the gallery on reload
   with no gallery edit. If it doesn't, the inventory has two owners — fix that first.
