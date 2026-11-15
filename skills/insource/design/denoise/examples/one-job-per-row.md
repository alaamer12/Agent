# Move 2: a unit doing one job vs. many

## The shape of the "before"

A single repeating unit — a table row, a list item, a card, a header bar — carries several unrelated responsibilities at once: identifying the item, showing its configuration, showing a status or metric, carrying a warning, and hosting an action control, all packed into one cramped container with no clear separation between which part is doing which job. A header in particular often shows this: a title, a description, a filter control, and two buttons all sharing one line or one tight block.

Diagnostic question, applied to a planned or existing unit: list out, in plain words, every distinct thing this one unit currently tells the reader or lets them do. If that list has more than about two items and none of them has its own clearly separated space, the unit is doing too many jobs at once.

## The shape of the "after"

Give each responsibility its own clearly separated slot within the unit — its own line, its own column, its own small sub-block — rather than letting several compete inside one shared space. Where a responsibility has been redistributed elsewhere in the interface already (per move 1 — a warning promoted to its own callout, an aggregate stat moved to a summary section), the unit simply drops that responsibility rather than trying to summarize it in miniature. What's left, after that redistribution, is usually one or two responsibilities per unit: identify the item, and let the reader act on it — with any remaining secondary attributes either folded into a single quiet line (per move 3) or given their own clearly bounded sub-line, never re-mixed back into one shared paragraph.

Section/card headers follow the identical discipline at a different scale: a title, optionally one small piece of context (a count, a filter, a timeframe) — and nothing else. If a header currently needs a description *and* a filter *and* multiple actions, that's usually a sign the section itself is trying to do more than one job, not just that the header needs more room.

What makes this reasoning-driven rather than a fixed layout rule:
- "One or two responsibilities" is a description of what redistribution (move 1) tends to leave behind, not a hard cap to enforce mechanically — some genuinely complex units legitimately need more slots, as long as each slot is clearly separated and dedicated to exactly one thing, rather than several things sharing one slot.
- The physical mechanism for giving each responsibility its own slot (a table column, a flex/grid child, a stacked sub-line, a separate component entirely) depends completely on the layout system already in use — there's no universal "correct" container to reach for.

## A minimal, illustrative sketch (not a template to copy)

```
[unit: row / card / list item]
  [slot 1: identity — name, primary label]
  [slot 2, if still needed after redistribution: the one or two remaining
   attributes this unit is actually responsible for, each in its own
   clearly bounded sub-line or column — never remixed into one shared block]
  [slot 3: action(s), in the interface's existing consistent action zone —
   see move 9]
```
