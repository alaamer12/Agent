# Reading the numbers

> The script prints arithmetic. A report is a person deciding what the arithmetic means, and saying
> the part that is inconvenient. This file is how to do that without fooling the reader or yourself.

## 1. Drift categories

Five categories, chosen because they carry different weight in a decision and are produced by
different sensors. The script **labels which sensor moved, never which category it belongs to** — the
category is the argument, and an argument cannot be delegated to a formatter.

| Category | Definition | Typical sensor | Weight in a decision |
| --- | --- | --- | --- |
| **Cosmetic-neutral** | a value changed, the render is indistinguishable | computed styles only, crop identical | usually accepted, listed once |
| **Visual** | the render differs, and a person can see it | crop, plus the style that explains it | the fight the claim predicted; judge per state |
| **Structural** | the composition changed: a wrapper appeared, a level deepened, an element was replaced | node inventory, geometry | often the cause of a *later* visual or behavioural bug |
| **Behavioural** | what the unit *does* changed: focus target, ring, accessible name, keyboard reach, scroll | focus probe, identity facts | the category that a visual spike cannot see, and the one that ships broken |
| **Economic** | the cost of carrying the change: states covered, call sites and attributes the sweep must touch, bundle/CSS delta, time spent | the manifest, the call-site inventory, the build | bounds what you may claim to have proven |

Two facts about the boundaries:

- **Structural drift frequently arrives alone.** The change adds a wrapper, the crop is identical, the
  styles barely move — and three weeks later a spacing rule that assumed direct children stops
  matching. Report a node-inventory change even when the visual answer is "nothing".
- **Behavioural drift is invisible to every sensor except the ones that require interaction.** If no
  focus probe ran, you did not measure behaviour, and the correct line in the report is "unproven", not
  "no change".

## 1.1 When the claim is "we can delete our code", the deletion is its own arm

A swap usually promises two things at once: it looks the same, *and* we may now delete what it
replaces. Those are different measurements, and the second one is missing from a plain before/after
whenever our own stylesheet, tokens or reset are still global — the new component is still being
dressed by the code the plan removes, so "identical" may be a loan from the 180 lines about to go.

Measure three states, and never fold the third into the drift table:

| Arm | What renders | What it tells you |
| --- | --- | --- |
| A | ours | the baseline |
| B | theirs, our CSS still applying | today's claim, and what the screenshots show |
| C | theirs, our CSS no longer reaching it | the state the plan actually creates |

If B matches and C does not, the honest sentence is "identical **while we keep** our stylesheet" —
which is the opposite of the claim being argued. If C also matches, that is the strongest result the
spike can produce, and it is worth the extra arm.

Before trusting arm B at all, read what was actually captured: if the new node still carries our class
or our CSS custom properties, the run measured our stylesheet on their element and says nothing about
the component. Check the rendered `outerHTML`, not the intent.

For arm C, **set the values to something loud before you delete them** — magenta, 13 px, 7 px radius.
Deletion fails silently into a framework default that may look plausible; a sentinel makes every
consumer announce itself, including the ones the browser never renders (a value read by JS, a colour
that only appears in a share card or the status bar).

## 2. Reading procedure

For each state, ask in this order:

```
1. Did the capture reach this state at all?          (counts first, numbers second)
2. Did the crop change?                              visual, or nothing to see
3. Did the style list change but not the crop?       cosmetic-neutral, or a state you did not render
4. Did the node inventory or geometry change?        structural; find the rule that depends on it
5. Did the focus probe or identity facts change?     behavioural; this is a defect candidate
6. Did any expected drift fail to appear?            suspect the build, the fixture, or the state list
```

Step 6 is the one that saves a wasted decision: a run with zero drift across every state is far more
often a measurement that did not happen than a change that had no effect.

## 3. Report shape

```
Claim            the sentence tested, in its falsifiable form, and what would refute it
Unit + states    the thing measured and the full state list, with any state you could not reach named
Method           driver, viewport, DPR, locale, build, what the sensors were, how the change was made
Drift            one row per state: category, how many properties, the two or three that matter
Behaviour        the focus and identity findings, as a section of their own, never folded into "style"
Attribution      failures that are not caused by this change, and whose they are
Cost             time spent, states covered, what a sweep over the whole tree would touch
Unproven         states not reached, interactions not driven, viewports not covered, the sensor gaps
Verdict          on the CLAIM only, in the same sentence as the half that survived
```

The order is deliberate: **Unproven comes before Verdict**, so nobody can write a conclusion that
silently outruns the measurement.

## 4. The rules that keep a report honest

- **Category, not just count.** "Fourteen properties drifted" is unrankable; "thirteen are
  cosmetic-neutral on states that render identically, one is the focus ring moving to a node two
  levels down" is a decision.
- **Report the refuting half.** If the claim was "the swap costs a look fight and nothing else", and
  the look fight did not happen but the focus path broke, the verdict is that the claim was half wrong
  — and the half that was wrong is the half the plan depends on.
- **Attribute precisely.** If the run is also red for reasons that belong to someone else's change, say
  whose. Otherwise the spike absorbs the bug and the report becomes unfalsifiable.
- **Zero offenders is not proof.** Print how many units and states were captured. Absence of drift and
  absence of measurement look identical in the output until you say the count.
- **Numbers are illustrative.** Any figure quoted in a skill or a template is a shape, not a
  measurement of your tree. Only the run directory holds real numbers.

## 5. Handing off

A spike that finds drift worth acting on hands work to another skill and stops:

| Finding | Hand to |
| --- | --- |
| the unit reaches the vendor around the seam, or the seam is not the only place the name lives | `seam` |
| the mockup and the render disagree (this is not a before/after question) | `parity` |
| the component's model is being forced into the project's shape | `treat` |
| the change is accepted and the tree must be swept | `seam` (migration) and `commit` |

The spike itself never proposes the sweep. It reports what the claim was worth.
