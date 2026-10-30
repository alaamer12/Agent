# Debug State Simulation: Reaching Any UI State On Demand

The convergence loop (`SKILL.md`) can only run unattended if every screen/state in scope can be reached programmatically — no manual clicking, no manual navigation, no manual "open the dropdown then screenshot." This file covers the four pieces that make that possible.

## Table of contents
1. ItC (Interact-to-Change) component inventory
2. Instrumenting a static mockup for state forcing
3. Hosting the mockup correctly
4. The dummy-data fixture plan
5. Obstacle bypass (splash/onboarding/permissions)
6. The real-app deep-link/launch-flag mechanism

---

## 1. ItC (Interact-to-Change) component inventory

**Definition**: an ItC component is anything that looks visually different depending on interaction — clicking, hovering, focusing, pressing — as opposed to a component that's static regardless of interaction. Dropdowns, drawers/side-menus, modals/dialogs, tooltips, accordions, tab switches, toggles, and hover/focus/pressed button states are all ItC components.

**Why this matters**: a naive capture pass only ever screenshots the *default* state of each screen. Every ItC component's non-default state (the dropdown open, the drawer open, the modal active) is a visual surface the naive pass never even attempts to match — and it's exactly the kind of thing that gets "fixed" ad hoc and inconsistently later, or never verified at all, if it isn't in scope from the start.

**Procedure**:
1. Walk every screen in scope and list every ItC component on it.
2. For each one, list its distinct visual states (a dropdown: closed / open; a modal: hidden / visible; a toggle: off / on; a tab group: one entry per tab).
3. This list is what feeds the capture-matrix calculation in `SKILL.md` Step 0 (`base screens × ItC-state combinations × theme × language`) — an inventory done after the matrix is estimated will under-count the real scope.

## 2. Instrumenting a static mockup for state forcing

Most mockups (a static HTML/CSS export) have no built-in way to jump straight to "dropdown open" — that state normally only exists transiently, mid-interaction, in a real browser session. To make it capturable deterministically:

- Add a small amount of JavaScript to the mockup that reads query parameters on page load and forces the corresponding ItC components into the requested state — e.g. `?dropdown=open&drawer=open&modal=confirm-exit&theme=dark&lang=ar` applying the same CSS classes/attributes the component would normally get from a real click, directly on load, before the first paint if possible (to avoid capturing a transition mid-flight — see `motion-parity.md` for why the *transition itself* still needs separate handling even though captures should skip past it).
- Keep this instrumentation additive and isolated (e.g. a single small script tag) so it's trivial to confirm it doesn't alter the mockup's actual default-state appearance when no query parameters are present.
- Apply the same approach for theme (`?theme=dark`) and language (`?lang=ar`) if the mockup supports either, so every entry in the capture matrix is reachable via one URL, not a manual toggle click.

## 3. Hosting the mockup correctly

**Always serve the mockup over a real local HTTP server — `python -m http.server` (or any equivalent static server) — never open it directly via a `file://` URL.** Query-string parsing, relative asset paths, and any script-driven dummy-data loading are unreliable or silently broken over `file://` in most browsers' security models. This is an easy setup mistake to make once and then spend an entire loop run chasing symptoms that are actually just "the query parameters never reached the page."

## 4. The dummy-data fixture plan

Mockups almost always contain placeholder content — fake names, fake numbers, lorem ipsum text, placeholder images. **Comparing a mockup's fake content against the real app's real data will never converge**, no matter how correct the real layout is — a text-length or content difference will keep registering as a mismatch that no amount of layout fixing can close.

**Procedure**:
1. Extract the mockup's literal dummy content — the exact strings, numbers, and image references it uses per screen/state.
2. Build a matching fixture/seed dataset for the real app: the same names, the same numbers, the same (or equivalently-sized) placeholder images.
3. Wire this fixture into the real app **only through the debug/launch-flag mechanism** (§6 below) — never something reachable in a normal production build. The moment a debug build is launched with the parity-testing flag, it should load this fixture data instead of hitting real data sources.
4. Keep the fixture data in sync with the mockup — if the mockup's dummy content changes, the fixture needs updating too, or captures will start silently comparing against stale content.

## 5. Obstacle bypass (splash/onboarding/permissions)

**Definition**: an obstacle is any screen that sits between app launch and the target screen/state that isn't itself part of what's being measured — splash screens, onboarding carousels, permission-request prompts, login walls.

Obstacles are not something the loop should navigate through manually each run, and getting stuck inside one (repeatedly capturing a splash screen, failing to advance past onboarding) is a bug in the automation, not a legitimate blocker — see `SKILL.md`'s "obstacles are not stop conditions" note.

**Procedure**:
1. Inventory every obstacle between launch and each target screen (this is usually a small, finite list, even if it multiplies across many target screens).
2. Build a debug-flag bypass for each: skip the splash screen's minimum-display timer in debug/test builds, mark onboarding as already-completed, pre-grant or stub out permission prompts, pre-authenticate past a login wall.
3. Route every deep-link/launch-flag target (§6) through these bypasses automatically — the loop should never need to know an obstacle exists, because it's already been routed around.
4. If an obstacle genuinely cannot be bypassed (a permission dialog that must legally show, an app-store-mandated screen), that's a real, narrow blocker worth flagging explicitly — not something to keep re-attempting manually.

## 6. The real-app deep-link/launch-flag mechanism

Expose a debug-only mechanism to launch the real app directly into any screen/state/fixture-data combination from the matrix, bypassing normal navigation entirely. The concrete mechanism is platform-specific:
- **Android**: intent extras passed via `adb shell am start` (or equivalent), read by the app on launch to select screen, ItC states, theme, and fixture dataset.
- **iOS**: a custom URL scheme or launch arguments read at startup.
- **Desktop**: command-line arguments.
- **Web**: query parameters, the same mechanism as the mockup itself (§2) — which conveniently keeps both sides of the comparison using an analogous state-forcing approach.

This mechanism should accept the full matrix dimensions from `SKILL.md` Step 0 as parameters (screen, ItC state(s), theme, language, fixture dataset) so any single capture in the loop is one deterministic launch command, not a sequence of manual steps.
