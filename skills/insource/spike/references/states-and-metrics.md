# States and metrics

> A spike is only as honest as its state list and as broad as its sensors. Both are decided before
> anything is captured, and both are where a run quietly becomes a screenshot.

## 1. Derive the state list from code

Not from the three screens you remember. Walk the unit's own source and enumerate what it can render.

| Where a state hides | How to enumerate it | Easy to forget |
| --- | --- | --- |
| Declared variants / prop enums | read the prop or variant type, list every member | a member nobody uses in dev but the design system still renders |
| Conditional branches in the template | every `if` / ternary / switch that swaps subtree, not just swaps text | a branch that swaps a *wrapper*, so the styles look identical and the node inventory moved |
| Fact-driven cases | the unit's own request result: pending, settled-with-data, settled-empty, error, offline, unauthorized | the empty case for a list that renders a different component entirely |
| Interaction states | hover, focus, focus-visible, active, selected, disabled, drag | focus: it is a state, and it is the one nobody captures |
| Direction and locale | RTL vs LTR, a long-word locale, a numeric format that widens a column | the whole layout mirrors and your crop is at one width |
| Theme / contrast | light, dark, forced-colour, high-contrast | the ring that only exists in forced-colour mode |
| Viewport and DPR | each size the unit actually appears at, not one phone | the container query that changes the structure, not the size |
| Container / call site | every parent shape the unit appears in: a full-width footer CTA, inline in a row, inside a dialog, icon-only, an anchor dressed as a button | a `width: 100%` footer CTA stretched to a fixed bar hides the unit's intrinsic min-height and padding — the screen where it is stretched is the one screen that cannot fail |
| Data shape | missing image, 1-line title, 400-character description, zero, negative, huge | the fallback asset path that never renders in your fixture |

Two completeness checks worth the time:

- **Reachability audit.** For each state, can you actually get there deterministically (a query
  override, a fixture, a stubbed fact)? A state you cannot reach is a hole in the claim, so name it in
  the report instead of silently dropping it from the list.
- **Origin check.** If a state appears in the code but nothing in the product can produce it, say so:
  it may be dead branch, and measuring it proves nothing about the live tree.
- **Call-site inventory, before pricing a deletion.** Enumerate, mechanically, what every call site
  passes: props, attributes that land on the root (`type`, `name`, `aria-*`, `data-*`), slots, the
  ref API, and any class or selector a stylesheet or test targets. The cost of deleting an
  implementation is `N call sites × M attributes`, not its line count — and the inventory is also the
  list of behaviours the harness has to cover.

## 2. The sensors, and what each is blind to

| Sensor | Sees | Blind to | Notes |
| --- | --- | --- | --- |
| **Computed styles** (the resolved list on the unit root) | every resolved property value, including inherited ones | geometry consequences, anything on nodes you did not ask about | name the property list per state; a 24-property list is a decision, not a default |
| **Tight crop** (screenshot of the unit box) | what a person would call "different" | why it differs; anything off-screen; anything that only shows on interaction | the cheapest evidence and the most over-trusted |
| **Element geometry** (box) | position and size, so overflow and shift | appearance | a crop can look identical while the box moved 4 px and now overlaps a neighbour |
| **Node inventory** (child counts, tag tally to a depth) | structure: a wrapper appeared, a level deepened, an element was replaced | styling and meaning | the sensor that catches the change a pixel diff calls "nothing" |
| **Identity facts** (role, aria attributes, name source, disabled, hidden) | the accessible name and its route | the full computed accessibility tree | for the real tree use the driver's built-in snapshot, and say which you used |
| **Focus probe** (what receives focus, depth from the unit, resolved outline/box-shadow, N Tab presses) | where the ring is drawn, whether the keyboard reaches the unit, whether Tab walks into it | hover, drag, screen-reader announcements | the one the other sensors cannot substitute — it is `seam`'s intake step 4, measured |
| **Interaction fact** (a click or fill, then re-measure) | a state that only exists after the user acts | anything after a second navigation | drive it; do not screenshot a resting state and call the flow covered |

The rule that follows the table: **a sensor you did not run cannot exonerate the change.** "Nothing
else changed" is only about the properties and probes you asked for.

## 3. Selectors

Point at attributes you own (`[data-spike=unit]`), never at the unit's internal structure. A spike
that selects through a component's child nodes is measuring the very thing the change may replace, and
it will report "the element disappeared" as if that were a bug in the harness rather than the finding.

## 4. Capture hygiene

The same run must produce the same bytes, or drift means nothing.

- Wait for **fonts** (`document.fonts.ready`) and for image decode before capturing; a capture during
  loading is a false diff, and it is the most common one.
- **Kill motion**: disable animations, transitions, skeletons and autoplay; freeze relative time and
  random identifiers through the fixture, or accept that the run is noise.
- Fix **viewport, DPR, locale, timezone, scroll position**; a run that inherits whatever the browser
  defaults to is not comparable to itself.
- Serve the **same bundle** in both arms: rebuild once per arm, and record which build each run used.
- One unit per change. If the edit touches two components, drift cannot be attributed to either.
- **Canary.** Expect at least one drift you can explain (the property the change is supposed to move).
  A run with zero drift across every state usually means the change did not apply, the wrong build was
  served, or the state list never reached the code that changed.

## 5. Coverage that is stated, not implied

The manifest prints `statesRequested / statesCaptured / statesFailed`. A capture that could not reach a
state exits non-zero rather than reporting a smaller, prettier run. Read those counts before reading any
number: the whole report is conditional on them.
