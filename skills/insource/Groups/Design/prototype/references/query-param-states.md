# The URL-State Contract

The core of the `prototype` skill: every meaningful UI state is reachable,
reproducible, and shareable by URL alone, and the live UI and the URL never
diverge. `/funds?tab=transactions&status=pending` renders exactly that;
clicking to that state writes exactly that; back returns from it.

This file owns: the component-state model, param naming, the central
state-helper spec, sync/history/validation rules, and the honest-state
rules. The starter's `_app.js` implements the helper mechanics; `specs.js`
owns each page's state trees; `test.mjs` verifies the mechanics.

## The model: per-component state trees, deeply queryable

The unit of state is **the component, not the screen**. Every interactive
component — bottom sheet, modal, dropdown, tab strip, filter set, wizard —
owns a state tree declared in the project's `specs.js`:

- a **mode** param covering whether it's engaged *and which content variant
  it shows*: `?open=plain|selection|loading|error`
- **sub-state** params refining a mode: `?loading=header|input-fields|all`
  (which region is arriving while `open=loading`), `?error=network|validation|permission`
  (which failure, while `open=error`)
- **subject** params naming what the component acts on: `?modal=transaction-details&transactionId=102`

**The deep-queryability rule: every meaningful combination a reviewer might
want must be reachable by URL** — not just "sheet open vs closed". A sheet
with a selection variant, three partial-loading regions, and three error
kinds has that many queryable states; exposing only an open flag fails the
contract. When enumerating a page's states, walk *each component* and ask:
what variants can this thing be in, and inside each variant, what can still
differ? That's the tree; all of it is queryable.

Naming conventions:

- Short role names, never `state1`: `?open`, `?sheet`, `?modal`, `?tab`,
  `?sort`, `?q`, `?step`.
- **One param per piece of state; components just coexist on one URL**
  (`?tab=transactions&open=plain&q=alpha`) — no mega-params coordinating
  everything.
- When two same-kind components could collide (two dropdowns), namespace by
  component (`?refresh-menu=open&export-menu=open`); single-instance
  components use bare names.
- Sub-states are ordinary validated params whose *meaning* depends on the
  parent mode (`?loading=` only matters when `?open=loading`) — the helper
  treats parent and sub-states mechanically alike; the renderer interprets
  the hierarchy.
- Boolean-ish params pick one convention (`open`/absent) and keep it
  project-wide.
- **List controls are just a component too**: the filter/sort/search/pager
  strip gets `?status`, `?sort`, `?direction`, `?q`, `?page`.

## The central state helper

One implementation in `_app.js` (mechanics only); pages declare **specs**
(pure data, in `specs.js`) — no page touches `URLSearchParams` directly:

```js
export const FUNDS_SPEC = {
  tab:      { default: "overview", values: ["overview", "transactions", "performance"] },
  status:   { default: null,       values: [null, "pending", "failed", "settled"] },
  sort:     { default: "name",     values: ["name", "nav", "chg"] },
  direction:{ default: "asc",      values: ["asc", "desc"] },
  q:        { default: "",          push: "replace" },
  // the bottom sheet: mode + sub-states — one tree, all queryable
  open:     { default: null,       values: [null, "plain", "selection", "loading", "error"] },
  loading:  { default: "all",      values: ["header", "input-fields", "all"] },
  error:    { default: "network",  values: ["network", "validation", "permission"] },
  modal:    { default: null,       values: [null, "transaction-details"] },
  transactionId: { default: null },
  toast:    { default: null },
};
```

Helper responsibilities, as **pure functions** (unit-testable, DOM-free):

1. `parse(search, spec)` → `{ state, foreign }`: each declared key
   validated against `values`/`parse`, invalid → declared default; unknown
   keys collected as foreign and **never dropped**.
2. `toQuery(state, spec, foreign)` → search string: defaults omitted (clean
   URLs), non-defaults written, foreign preserved.
3. `patch(state, changes)` → new state: merge only changed keys — updating
   one component **preserves unrelated active states** (req 8).
4. History policy: `push` for discrete moves (sheet opens, tab switches),
   `replace` for continuous streams (search keystrokes) via the key's
   `push: "replace"` declaration.
5. `mountState(spec, render)` binds it all: parse on load → `render(state)`;
   handlers call `sync(changes, {key})` → patch → write URL → re-render;
   `popstate` re-parses and re-renders. **`render(state)` is the single
   update path** — URL-initialized and click-driven states are the same
   code, hence pixel-identical by construction.

**Invalid-and-missing handling:** every key has a `default`; there is no
error path for a bad URL — `/funds?open=banana` renders a closed sheet with
a warning-free page. Validation must never blank or throw the page.

**What stays out of the URL:** transient implementation details (hover
position, scroll offset, focus) get no params; the target is *every
meaningful state of every component, nothing beyond*.

## Data fidelity: `?filled`

**Non-optional.** Every page spec declares `filled: { default: null }`. Every gallery
strip carries a `Filled` chip linked to `?filled=1` (or the project's default seed).
An agent that ships a prototype without working `?filled` has shipped an incomplete prototype.

One cross-page param every project declares in each spec:
`filled: { default: null }`.

- **Default (absent):** sparse, realistic placeholder data — a handful of
  rows, gaps, the shape of a nearly-empty product. Sparse by default is
  honest: a prototype that always renders 200 tidy rows hides the wrapping,
  scrolling, and density problems real data causes.
- **`?filled` / `?filled=<seed>`:** a FULL random dataset — long tables,
  crowded charts, long names — generated by a seeded PRNG
  (seed from the value; bare `filled` uses a project default seed).
  **Seeded, never unseeded:** an unseeded `Math.random()` breaks the skill's
  first promise — refresh would show different data and a shared link would
  not reproduce. `?filled=17` must look identical every time it opens;
  `?filled=18` is a different draw. Different seeds *are* the randomness.
- Generation is pure data code (`seededFunds(seed)` in a page's data
  section), never side-effectful; the same render path paints sparse and
  filled alike, and the gallery carries a filled chip.
- The generator deliberately includes **adversarial rows**: a 90-character
  name, a missing/null field, an unrecognized category value — so that
  edge-case handling is forceable and reviewable, not hidden in the happy path.

## Deriving the states — how to find them all

**A component's default behavior is to lie confidently:** code built for the
happy path renders *something* for every input, so "it doesn't crash" is
never evidence that a state was found. Enumeration is a hunt, not a recital —
and the generic pending/empty/error list is the failure mode: states must be
derived from **this** screen's actual dependencies, or the inventory is
decoration.

Two passes find them:

1. **Rotate stances over each component.** Look at it as the reliability
   engineer (what fails upstream? which of those failures has a surface here
   — provider down vs degraded vs throttled vs maintenance are *different
   renders* if the copy or recovery differs), the first-run novice (what does
   this look like with nothing configured, no data, mid-tutorial?), the
   reviewer with three seconds and one hand (partial data? one very long
   value? a state whose only exit is a scroll?), and the auditor (does every
   state say honestly what happened — or does an error wear the empty
   state's clothes?).
2. **Walk the axes the component actually touches**, single-axis first, then
   edges: data (sparse/partial/stale/unknown-shaped) · backend/provider
   status (the semantic kinds — never bind a state to a status code) ·
   in-flight (action pending, interrupted mid-submit, resolves while the
   sheet is half-open) · viewer (permission variants of the *same* data) ·
   time (loading-more, maintenance windows). An edge state earns its own
   param only if it needs a *different message or recovery*; otherwise it
   merges into a named state listing its causes ("unavailable — provider or
   permissions" with one Retry) — the distinctness test, not taste.

**Filter every candidate through four gates:** *evidence* — the design/mockup
shows or implies this state (a screen that can't actually be offline has no
offline state; inventing one teaches reviewers a lie); *reachability* — a
reviewer would plausibly land here; *distinctness* — different message or
recovery than a sibling, else merge; *consequence* — left unhandled, the
reviewer is misled (false success, stuck spinner, silent blank). Then order
the survivors by *how likely × how misleading × how hard to recover* — that
decides which states get gallery chips front-loaded, which ride along at the
end. The gallery strip **is** the coverage matrix: it enumerates the
inventory, so a state missing there is a state unclaimed.

**Unknowns render as unknown (fail-closed).** Give every enumeration-ish
param a default branch and every data renderer a designed response to values
outside the vocabulary — a missing field, a 90-character name, an
unrecognized category. The happy path is not the fallback; "Unknown"/
"-"/em-dash in the cell, an "unrecognized state" strip for stray param
values, and *never* a crash or a fabricated normal-looking row. Seed
generation should deliberately include such adversarial rows under `?filled`
so the handling is forceable and reviewable like any other state.

## Honest states — per component

The carried-over discipline, now scoped to each state tree:

**Never skeleton chrome.** A shimmer marks content that hasn't arrived.
Sub-states like `?loading=header|input-fields|all` exist precisely to make
this honest at component granularity: the shimmer occupies exactly the
declared region and nothing else. Static parts of a sheet (its title, a
close button) must not shimmer even while `?loading=all` shimmers its
fields — and where arriving content has no stable shape, a plain "Loading"
line beats an invented skeleton.

**A state with no real trigger doesn't get a mockup.** If the sheet can
actually fail in three ways, all three error kinds are queryable; if it
cannot fail at all, it gets no `error` mode at all — faking one teaches a
reviewer a lie. If the product has a spec for where failures surface
(error-mapping table, surface law), read it first and let it decide which
component owns which error kind.

## Keeping the contract honest (project-level)

- **One owner per mechanism**: URL mechanics → `_app.js`; each page's state
  tree → `specs.js`; if a gallery exists, its chips are GENERATED from the
  same `specs.js` preview lists (`FUNDS_GALLERY`…) — adding a state to a
  page's declared tree makes its chip appear with no gallery edit; deleting
  it makes the chip vanish. A hand-typed gallery list is the drift this
  rule kills (gallery-index.md rule 1).
- **Enumeration review**: before delivering, walk every interactive
  component and ask "which modes? which sub-states per mode? which
  subjects?" — anything the design can show must be in the spec. The
  gallery is the visible proof of completeness: its chips *are* the state
  inventory.
- **Acceptance test**: append each declared param (valid, invalid,
  combined) to every page URL — the render must match the spec; every
  interaction must leave the URL where the same interaction reached;
  `node js/state.test.mjs` guards the mechanics. This walkthrough is the
  acceptance test of the whole skill, not an optional nicety.
- **Direct loading**: `/funds?open=error&error=permission` must work with
  no prior visit to `/` and no click sequence, every time.
