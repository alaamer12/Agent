# Query-Param-Controlled Interactive States

The core contract of the `design-mockup` skill: any component with a visible/hidden or selected/unselected state must be reachable by URL alone, on top of working normally via clicks. This lets a specific state be linked, screenshotted, or handed to a reviewer directly — `mockup.html?sheet=filters&tab=2` should render exactly that state on load, with no interaction required.

## Naming convention

Pick short, readable param names tied to the component's role in the screen, not generic ones like `state1`. One param per independent piece of state.

- `?sheet=<id>` — which bottom sheet is open (omit or empty = none open). If there's only ever one sheet on the screen, `?sheet=open` / `?sheet=1` is fine.
- `?drawer=open` — side drawer / nav drawer open or not. Boolean-style params use presence or `open`/`closed` — pick one convention and use it consistently across the whole file.
- `?modal=<id>` — which modal/dialog is showing.
- `?tab=<index-or-slug>` — active tab.
- `?dropdown=<id>` — which dropdown/select is expanded (rare to need this open-on-load, but support it the same way if the component exists).
- `?accordion=<id>` or `?accordion=<id1>,<id2>` — which accordion section(s) are expanded.
- `?toggle-<name>=on|off` — state of a named switch/checkbox where the initial state matters to what's being shown.
- `?step=<n>` — current step in a stepper/wizard.
- `?toast=<id>` — a toast/snackbar shown on load (useful for reviewing success/error states without triggering the action).
- `?state=<id>` — **the screen's own lifecycle state**: `loading`, `empty`, `error`, and whatever else the screen can legitimately be in. This is the one param that is *not* a component's visibility state — it describes the whole screen's relationship to its data — so it gets its own name rather than overloading `?tab`/`?modal`. See "Screen-level states" below.

## Screen-level states (`?state=`)

Component params above cover sheets, tabs and toggles. Separately, most real screens can also be
in a state that belongs to no single component: it hasn't loaded, it loaded and there's nothing to
show, or it failed. Model these as one param, `?state=<id>`, on every screen that reads data.

The useful set is usually some subset of:

| id | When the screen legitimately has it |
|---|---|
| `loading` | content is on its way |
| `loading-more` | the first page is on screen and the next one is arriving |
| `empty` | it loaded, and there is nothing to show |
| `error` | it tried and failed — the "failed after loading" case |
| `no-connection` | the app-level gate, if the product requires a connection to open |
| `blocked` / `unavailable` | one item on the screen can't be used while the screen works |
| `toast-error` | an unexpected fault whose surface is a transient notice, not the screen |

Two rules keep this honest:

**Never skeleton chrome.** A shimmer marks content that has not arrived yet. A like button, a
share icon, a fixed filter chip, a settings row, a tab bar — those exist from the first frame and
never load, so giving them a skeleton is a lie about the product. A shimmer occupies the exact box
the arriving content will occupy, and nothing more. Where the arriving content has no stable shape
(a list of unknown length), show a plain "Loading" line instead of inventing a skeleton.

**A state with no real trigger doesn't get a mockup.** If the screen can't actually enter it,
don't add a chip for it — a settings screen made of static local rows usually has no loading
state, and faking one teaches a reviewer a lie.

If the product has a spec for where failures surface (a three-surface law, an error-mapping
table), read it first and let it choose the surface per state — full-screen, inline in the failed
region, or a toast. Do not invent a per-screen preference.


Multiple independent components on one screen just get multiple params — they don't need to be coordinated into one mega-param. Keep each param scoped to exactly one component's state.

## The bootstrap pattern

One function, called once via `DOMContentLoaded` (or run inline at the bottom of `<body>`, after the elements it targets exist), reads `location.search` and applies each param to its component using the *same* open/close functions that clicks use — never a separate code path. This guarantees the query-param-triggered state is pixel-identical to the click-triggered state, and that the file only has one set of open/close functions to maintain.

```html
<script>
  const params = new URLSearchParams(location.search);

  // --- reusable open/close fns, same ones wired to onclick handlers ---
  function openSheet(id) {
    document.querySelectorAll('.bottom-sheet').forEach(el => el.classList.remove('open'));
    document.getElementById('sheet-backdrop')?.classList.add('open');
    document.getElementById(`sheet-${id}`)?.classList.add('open');
  }
  function closeSheet() {
    document.querySelectorAll('.bottom-sheet').forEach(el => el.classList.remove('open'));
    document.getElementById('sheet-backdrop')?.classList.remove('open');
  }
  function openDrawer() {
    document.getElementById('drawer')?.classList.add('open');
    document.getElementById('drawer-backdrop')?.classList.add('open');
  }
  function setTab(index) {
    document.querySelectorAll('.tab-btn').forEach((el, i) => el.classList.toggle('active', i == index));
    document.querySelectorAll('.tab-panel').forEach((el, i) => el.classList.toggle('hidden', i != index));
  }

  // --- bootstrap: apply query params on load using the SAME fns ---
  function applyInitialState() {
    const sheet = params.get('sheet');
    if (sheet) openSheet(sheet);

    if (params.get('drawer') === 'open') openDrawer();

    const modal = params.get('modal');
    if (modal) openModal(modal);

    const tab = params.get('tab');
    if (tab !== null) setTab(tab);

    const accordion = params.get('accordion');
    if (accordion) accordion.split(',').forEach(id => expandAccordion(id));

    const step = params.get('step');
    if (step !== null) goToStep(parseInt(step, 10));

    const toast = params.get('toast');
    if (toast) showToast(toast);
  }
  applyInitialState();
</script>
```

Keep this bootstrap block near the bottom of the file, after all the open/close/set function definitions, so it can call them directly.

## Per-component patterns

### Bottom sheet (mobile pattern, see uploaded reference file for full example)
- Markup: a backdrop div + a sheet div with `translateY(100%)` default, `.open { transform: translateY(0) }`.
- A drag handle (`touchstart`/`touchmove`/`touchend`) is a nice-to-have realism detail, not required unless the user wants the sheet to feel truly native — include it by default for mobile mockups since it's cheap and reads as authentic.
- Param: `?sheet=<id>` calls the exact same `openSheet(id)` the handle/backdrop-click/trigger-button use.

### Drawer / side nav
- Markup: fixed-position panel translated off-canvas, backdrop behind it.
- Param: `?drawer=open`.

### Modal / dialog
- Markup: centered card over a backdrop, or full-screen on mobile.
- Param: `?modal=<id>` when there's more than one possible modal on the screen, else `?modal=open`.

### Tabs
- Param: `?tab=<index>` (0-based) or `?tab=<slug>` if tabs have meaningful ids — slug is preferable for readability when tab count might change.

### Dropdown / select
- Usually doesn't need to persist open-on-load (it's a transient overlay), but if the mockup is specifically about reviewing the open dropdown's contents, support `?dropdown=open` the same way as a sheet.

### Accordion
- Param: `?accordion=<id>` or comma-separated list for multiple expanded sections.

### Toggle / switch
- Only expose via param when the *initial* value matters to reviewing the screen (e.g. showing the "on" state's dependent UI). Param: `?toggle-notifications=on`.

### Stepper / wizard
- Param: `?step=<n>`, 1-based is more natural for a stepper than 0-based.

### Toast / snackbar
- Param: `?toast=<id-or-type>` to preview a specific toast without triggering its action — useful for reviewing success/error/warning states.

## Testing the contract

Before delivering, mentally (or actually, if you can render/screenshot) walk through appending each param to the file's path and confirm the described state renders — this is the acceptance test for the whole skill, not an optional nicety.
