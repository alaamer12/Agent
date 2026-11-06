# Case 02 — the clean pixel diff that missed the defect

*Every number, name and path in this file is illustrative — a shape, not a measurement of any tree.*

## The claim

"Swapping the list row for the framework's row is safe: it looks the same."

## What was run

A before/after capture across four states, with computed styles and tight crops. That is the whole
method as it was run: two sensors, neither of which can interact with anything.

```
node scripts/spike.mjs capture runs/before --spec spec.json --base <url>
#   captured 4/4 states into runs/before
node scripts/spike.mjs diff runs/before runs/after
#   spike diff — 4 states compared, 0 not comparable
#   style properties changed: 6 | states with node/geometry change: 0 | states with focus/identity change: 0
```

The report said: six properties drifted, all cosmetic-neutral, and the crops are byte-identical on
every state. A reader who does not know what a sensor cannot see will call that "safe".

## What was actually broken

The row now rendered a native disclosure element inside itself. Consequences, none of them visible on
a resting row:

| Symptom | Why the diff could not see it |
| --- | --- |
| Tab stopped on the row and then jumped past its two actions | the run never pressed Tab: no focus probe, so no measurement of the tab order at all |
| the visible ring appeared on the row's outer box while the inner element was focused | `outline-*` was not in the state's property list — the styles were measured on the unit root only |
| the row's accessible name became the first action's label | identity facts were not captured in this spec; the crop is identical because the text is identical |
| the disclosure opened on Space but not on Enter | the only interaction the spec drove was a click |

The crops were **correct**. Every one of these is a behavioural fact about an element in a state that
was never entered, by a sensor that was never run.

## What changed in the method afterwards

1. **Focus is a state row.** A spec that lists `default / empty / loading` and no
   `keyboard-focus` row has a hole, and the hole is exactly where this defect lived.
2. **The probe runs, it does not observe.** A `focusProbe` plus a couple of Tab presses produces the
   active-element tag, its depth from the unit root, and its resolved outline — enough to catch "the
   ring is on the wrong box" as a *before → after* pair instead of a bug report.
3. **Identity facts are captured** (role, aria attributes, name source), because a component swap can
   move an accessible name while keeping the same visible text.
4. **"Byte-identical crops" is not a verdict about behaviour, and the report has to say so.** The
   Unproven section came before the Verdict section from then on, so the reader cannot miss the sensor
   gap.

## The shape to recognise

A claim about **behaviour**, tested with **appearance**. It looks rigorous because the numbers are real
and the diff is clean. The tell is a sentence in the report that could not have been produced by any of
the sensors that ran — "nothing else changed", "the interaction is fine", "it is safe".

The connection to the other skill is direct: what this run missed is exactly the bill that
`seam/references/ownership-transfer.md` says adoption hands you — focus mechanics, the child nodes a
component adds, prop-flag precedence, attribute fallthrough destination. A spike that adopts a
component and does not drive it has measured one of the four and reported on all of them.
