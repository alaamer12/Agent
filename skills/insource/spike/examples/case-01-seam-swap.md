# Case 01 — a whole spike where half the claim was refuted

*Every number, name and path in this file is illustrative — a shape, not a measurement of any tree.
Re-run the shape on your own unit and let the numbers be yours.*

## The claim, made out loud

"We should replace our hand-rolled card with the framework's card. It will cost a **look fight** — the
shadows, the radius, the padding rhythm. That's why we've put it off."

Written falsifiably: *adopting the framework card produces visual drift we would have to argue about.*
Refuting result: no meaningful visual drift. That is a real outcome, and it was the true one, which is
exactly why the spike was worth an afternoon.

## Step 2 — the unit and its state list

Unit: one card component in one screen, selected by `[data-spike=unit]`. The state list came from
reading the card's source, not from memory:

| State | Origin in code |
| --- | --- |
| default | populated fixture |
| empty | the `if no items` branch |
| pending | the request-in-flight branch |
| variant=compact | the declared variant enum, second member |
| keyboard-focus | focus is a state; it needs its own row |
| pressed | the `:active`-equivalent the component applies on pointer down |

One state was **not reachable**: the error case had no fixture hook and no query override. Named in the
report as unproven rather than dropped from the list.

## Steps 3-5 — before, one change, after

```
node scripts/spike.mjs capture runs/before --spec spec.json --base <the already-running url>
#   captured 6/6 states into runs/before
#   edit: the seam's card wrapper now returns the framework card. nothing else. one file, 9 lines.
node scripts/spike.mjs capture runs/after  --spec spec.json --base <the same url, rebuilt once>
node scripts/spike.mjs diff runs/before runs/after --attention outline-width,outline-style,box-shadow
```

The diff's own output (illustrative):

```
spike diff — 6 states compared, 0 not comparable
style properties changed: 14 | states with node/geometry change: 3 | states with focus/identity change: 1
  unit-default: 3 style, crop bytes
      display: "flex" -> "grid"
      box-shadow: "0 1px 2px rgba(0,0,0,.16)" -> "0 2px 8px rgba(0,0,0,.12)"
      line-height: "1.3" -> "1.35"
  unit-empty: no drift detected by any sensor
  unit-loading: 6 style, node inventory
  unit-variant-compact: 2 style
  unit-keyboard-focus: 1 style, focus path, identity/accessible name
      * outline-width: "2px" -> "0px"
      focus: afterFocus tag "button" insideUnit true depth 0 -> tag "div" insideUnit true depth 2
      identity: ariaLabel "Card title" -> null
  unit-pressed: 3 style
```

## Step 6 — behaviour, the part the crops could not see

Read the two lines above `unit-keyboard-focus` before reading any styling row.

- The ring went from `2px` to `0px`: the framework card is not the focus target — it renders an inner
  element that takes focus, and the old wrapper's outline rule no longer lands on anything visible.
- `afterFocus.depth 0 → 2`: focus moved two levels *inside* the unit, so every rule and test that
  assumed the focused node was the unit root is now wrong.
- The accessible name disappeared: it came from an attribute the wrapper set on its own root, and the
  framework card puts fallthrough attributes somewhere else.

None of this is in a screenshot of a resting card. The visual half of the claim — the look fight —
largely did not happen: thirteen of the fourteen drifted properties were cosmetic-neutral on states
that render identically, and the one a designer would mention (the shadow) is a two-line token change.

## Step 7 — revert and report

Reverted the nine-line edit, kept both run directories.

**Verdict on the claim:** half refuted. The adoption does **not** cost a look fight; it costs a focus
and identity fight, which nobody was bracing for, and the sweep it implies is not a styling pass but a
per-component intake (`seam/references/ownership-transfer.md`).

**Cost measured:** one afternoon, 6 states captured, 1 unreachable, two files of evidence.

**Unproven:** the error state; hover; a narrow viewport; a right-to-left locale; every other component
inside the seam. The verdict is scoped to the card, and the report says so — the transfer of ownership
is per component, so this spike proves nothing about the next one.

## What the method owed the run

- The state list came from code, so the focus state existed as a row to measure. It would not have been
  invented after the fact.
- The sensors named the failure because the focus probe and the node inventory ran. A crop-only run
  would have reported "no drift detected" for the state where the defect lived.
- The change was nine lines in one file. Attribution was possible because nothing else moved.
