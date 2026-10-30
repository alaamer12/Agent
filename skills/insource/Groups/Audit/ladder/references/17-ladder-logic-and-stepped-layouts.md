# 06 — Ladder logic (IEC 61131-3) and stepped UI layouts

Two more meanings of "ladder" that show up in requirements conversations. One is a real, safety-critical
programming language; the other is a layout pattern. Both carry transferable rules.

## Ladder logic: the original rails and rungs

Structured-text-adjacent graphical language for PLCs, standardized in **IEC 61131-3** as Ladder
Diagram (LD). Program = two vertical rails (power) with horizontal **rungs**; each rung holds
**contacts** (conditions: NO/NC, edge, timer) and ends in a **coil** (output) or a box instruction.
It looks like relay wiring because it *is* relay wiring made software, so electricians read it.

Execution semantics, which is where the transferable lessons are:

- **Scan cycle**: read physical inputs into an *input image table* → execute the program → write the
  *output image table* to physical outputs → repeat (typically milliseconds). The program never sees
  inputs mid-scan; consistency comes from snapshotting.
- **Traversal order**: rungs top-to-bottom, contacts left-to-right within a rung. Deterministic, no
  author-facing priority field — position is the order, exactly like an if-chain.
- **Duplicate coils**: if two rungs drive the same output bit, the **last one executed wins** in
  classic scan semantics — and this is the documented source of "the machine ignores my rung". IEC's
  LD semantics treat multiple rungs driving one coil as a logical OR, and vendors differ, so the
  correct answer to "what happens when two rungs write the same coil" is *read the manual for this
  controller*, never assume. That is the same rule as any cascade: nearest/last/first-wins is
  configuration, not intuition.
- **Set/reset coils** and latching rungs exist because a pure "last write wins" output cannot express
  stateful behavior; state machines in PLCs are usually built from them or from step instructions.
- **Safety is structural**: physical outputs are de-energized on fault (scan stop, watchdog), and
  interlocks are placed as rungs that *break power flow* before any enable rung, not ordered hoping.
  That's the tier idea in electrical form.

Transferable:

| PLC fact | Software ladder lesson |
|---|---|
| Inputs snapshotted into an image table | Freeze the facts once per evaluation; don't re-read mutable state mid-ladder |
| Position is order; last-write-wins on a shared bit | Two rules writing one output field is a bug you must detect, not document |
| Interlocks break power flow | Safety rungs go before enables, or in a deny tier that is checked first |
| Scan time is bounded | Ladders must be bounded: no re-entry loops without a hop limit |
| Vendor semantics differ | Write down which convention your engine uses (first/last/strictest, nearest/deepest) |

## Laddering in research (means-end chain)

Covered in `18` alongside the other thinking ladders; summarized here for completeness: repeated
"why is that important to you?" probes climbing attribute → functional consequence → psychosocial
consequence → value, with a documented failure mode (empty answers at the top, the "3-year-old why"
effect) and a stop rule (when the value no longer informs a build decision).

## Stepped / staircase UI layouts

A visual pattern: content items offset along a diagonal — timelines, process steps, progress flows,
pricing tiers. It reads as movement, which is why it is chosen for sequential narratives.

Engineering constraints worth knowing before implementing one (this skill covers the *structure*, not
the styling; the `impeccable`/`prototype` skills own the visual work):

- **Order must survive the staircase.** If the layout is a decision or a flow, the DOM/source order
  must match the reading order; the visual offset is a transform, not a reflow. Screen readers and
  keyboard focus follow the DOM, not the pixels.
- **RTL and vertical space**: a diagonal layout has to invert for RTL and degrade to a vertical list
  on narrow screens; that is a *different rung*, not a broken one. Handle it as a state, not a hack.
- **Contrast on gradients**: staircases usually sit on diagonal backgrounds, which breaks flat
  contrast checks; test per-item, not per-page (this is the accessibility failure the pattern is known
  for).
- **Progress semantics**: if the steps mean "you are here", publish `aria-current="step"` and give
  completed/upcoming/past states distinct text, not just color — an unhandled-state bug in disguise
  (see the `stateful` skill).

## Disambiguating a request that says "ladder"

Ask (or infer) which: a **decision** ladder (this skill, `00`–`16`), **PLC ladder logic** (safety
control), a **laddering interview** (research), a **ladder of abstraction/inference** (problem
framing), or a **stepped layout** (visual). The five share the shape, not the tooling; picking the
wrong one means writing a rule engine when someone wanted an interview script.

## Sketches you can run

**Scan semantics in 20 lines** — the two PLC rules that transfer to software ladders: inputs are
snapshot before the walk, and the last write to an output wins.

```python
def scan(rungs, inputs, outputs):
    """rungs: list of (contacts, coil). contacts is a predicate over the snapshot."""
    image = dict(inputs)                       # snapshot: read once, not per rung
    for contacts, coil in rungs:               # top to bottom
        outputs[coil] = contacts(image)        # later rung overwrites: last write wins
    return outputs

scan([
    (lambda i: i["start"] and not i["stop"], "motor"),
    (lambda i: i["overtemp"], "motor"),        # this rung alone decides the motor bit
])                                          # -> {"motor": True} even if start was released
```

That is the duplicate-coil hazard, playable: rung 1 turns the motor off on `stop`, rung 2 silently turns
it back on. The interlock fix is structural, and transfers to a software ladder as a deny tier (`13`):

```python
scan([
    (lambda i: not i["e-stop"] and not i["overtemp"], "enable"),   # breaks power flow first
    (lambda i: i["enable"] and i["start"] and not i["stop"], "motor"),
    (lambda i: i["enable"] and i["overtemp"], "motor"),            # cannot energise without enable
])
```

**Set/reset instead of last-write** — when two rungs must both affect one output without overwriting:

```python
for contacts, coil in rungs:
    if contacts(image):
        state[coil].mode("set" if coil not in latched else "reset")
        state[coil].value = True
```

PLC practice is the same advice as `15`: prefer one rung per output; if two must write one output, make
the combination a named operator (`OR`, `set/reset`, tier) instead of a position in a list.

## Stepped layout, the accessible form

The staircase is a transform, not a reflow: DOM order stays reading order.

```html
<ol class="steps" aria-label="Rollout plan">
  <li class="step" aria-current="step">Draft reviewed</li>
  <li class="step">Staged to 10%</li>
  <li class="step">Full rollout</li>
</ol>
```

```css
.steps { list-style: none; padding: 0; }
.step  { margin-inline-start: calc(var(--i, 0) * var(--step-offset, 1.5rem)); }
.step:nth-child(2) { --i: 1; }
.step:nth-child(3) { --i: 2; }

/* narrow screens: the staircase flattens, the order is still correct */
@media (max-width: 40rem) { .step { margin-inline-start: 0; border-inline-start: 2px solid; } }
```

Three things this gets right, and the three the pattern usually gets wrong:

- `aria-current="step"` publishes "you are here" instead of leaving it to colour.
- `margin-inline-start` flips for RTL; a `left:` offset does not.
- States are `past / current / upcoming`, each with its own text treatment - not one grey.
- Usual failures: DOM reordered to draw the stairs (screen readers and tab order follow the DOM), text
  on a diagonal gradient (contrast fails per item, not per page), and a step that is only a different
  colour of the same text.
