# The verdict format

The verdict is a recommendation the user decides on - the agent does not enact it. It must let the user
re-derive or challenge the choice, not just swallow it. Structure it top-down: the pick first, then the
grounds, then the caveats that matter.

## The shape

```text
VERDICT: <choice> is likely the best fit for us.
Based on:
  - <criterion>: <measurement or finding, with the number/source>
  - <criterion>: ...
Confidence: <high | medium | low> - <one clause on what makes it that level>
Runner-up: <option> - loses on <the deciding criterion> by <gap>; becomes the pick if <the condition that flips it>
Flips if:  <the data/scale/requirement change that would change the answer>
Untested:  <what was decided without measurement, and why that's acceptable>
Chosen-out: <the constraint-killed options, one line each, so the user sees the filter was honest>
```

## Wording rules

- **"likely the best fit for us", never "objectively best".** "Best" is always relative to the success bar
  and constraints set in Step 1; say whose best it is.
- **Numbers carry units and conditions**: "18ms/query at 12k points, normal mode (GC on)" - not "much
  faster". A measurement without its conditions is a claim, not evidence.
- **Cite for the version.** "SQLite 3.45 docs / context7, for the pinned version" - a fact about a moving
  dependency is only true for the version it was checked against.
- **Confidence is stated, not implied.** High = measured on real data with the deciding gap clear; medium =
  one key criterion judged without measurement, or the gap was inside the noise; low = the evidence was thin
  or indirect. Never let a low-confidence verdict read like a high one.
- **The runner-up is the honesty test.** If you cannot name the condition that would flip the verdict, you
  probably did not actually compare - you confirmed a favorite.

## The deciding-gap discipline

Rank criteria by how much they decided the answer and lead with those. A verdict that lists every
measurement flat invites the user to overweight a criterion that didn't actually swing the result. Name the
one or two things that chose the winner; the rest is support.

## Reporting what went wrong

Say the negatives plainly where they belong, not hidden:

- a benchmark you couldn't run and why (no access, budget, realistic data unavailable) - and what that
  costs the verdict's confidence;
- a documented fact you couldn't confirm - marked as assumption, so the user can check it;
- if the constraints turned out to eliminate *every* option the user expected, that is itself the finding:
  say so rather than crowning a constraint-violating winner.

## When the recommendation is "don't"

Sometimes the evidence says the status-quo or a standard-library feature already wins, or that no option
meets the success bar and the real fix is elsewhere (a data-model change). That is a valid verdict - the
job is to find the best answer, not to pick the best of what was handed in.

## Hand it, then stop

Deliver the verdict and wait for the user's decision. Do not install, import, scaffold, or "go ahead with
the winner" - the recommendation is the deliverable. Log the user's actual choice; if it differs from the
recommendation, record it as the decision (their priorities may include things the evidence couldn't
measure) and move on without re-arguing.
