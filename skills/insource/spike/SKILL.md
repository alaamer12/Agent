---
name: spike
description: Turn "will this break it?" into numbers. A measurement, not a decision - pick the smallest renderable unit that carries a claim, derive its state list from code, capture computed styles, tight crops, node inventories and interaction facts before and after one reversible change, and report drift by category, including the drift that refutes the claim. Use when someone is about to win an argument by asserting something measurable, before adopting or swapping a component, or when a pixel-perfect diff is being cited as proof about behaviour.
argument-hint: "<the claim being tested>"
---

# Spike

Turn "will this break it?" into numbers. A spike is a **measurement, not a decision**: it changes one
thing on one branch of the tree, measures the smallest renderable unit in each of its states before and
after, and reports drift — including the drift that refutes the person who asked.

_Use it when someone is about to win an argument by asserting something measurable._

## Scope

**Includes**
- Choosing the smallest unit that carries the claim (one component in one state, not a page).
- Enumerating that unit's states from the code, not from imagination.
- Capturing computed styles, tight crops, node inventories and interaction facts per state, before and
  after a reversible change.
- Reporting drift as a table: how many units, which properties, which kinds, and what it means.
- Reverting the change and leaving the evidence behind.

**Excludes**
- Deciding whether to adopt anything — the spike ends with a verdict on the **claim**, not the plan.
  ("The look survives; the focus ring does not.")
- Design fidelity against a mockup: that is `parity`. Before-vs-after against your own baseline is here.
- Auditing who may import or name what: that is `seam`. A spike often triggers one; it never writes one.
  What a spike's step 6 finds belongs to `seam/examples/case-03-ownership-transfer.md`.
- Permanent tests. A spike's script is disposable; a spike that must keep passing becomes a test.
- Building the app or serving it. The caller supplies a running URL; the script measures.

## Setup

Needs a headless browser the project can already drive. Discover, don't assume: use the browser channel
the repo's e2e config uses, and reuse its server and port discipline rather than inventing one. Never
run a spike and the project's full gate concurrently if both own a build directory or a port.

## Workflow

Copy this checklist and tick it off:

```
- [ ] 1 Claim: the sentence being tested, what result would refute it, and the acceptance
      rule (what counts as pass) — all written before the first capture
- [ ] 2 Unit: the smallest thing that carries it, and its state list derived from code
- [ ] 3 Before: build and serve (the caller's job), capture styles, crops, nodes, interaction facts
- [ ] 4 Change: one reversible edit; nothing else. Prefer the narrowest shared point
      (the wrapper or seam the call sites all go through) over editing each call site:
      one file to revert, and every call site exercises the change
- [ ] 5 After: recapture identically; diff; read the numbers, including the inconvenient ones
- [ ] 6 Behaviour: is anything the crops cannot see? (focus, roles, keyboard, scroll) — drive it
- [ ] 7 Revert + report: verdict on the claim, cost, what stayed unproven
```

`scripts/spike.mjs` does the capture and the arithmetic (`capture <run> --spec … --base <url>`, then
`diff <before> <after>`), driven by a spec file like `assets/spec.example.json`. The caller serves the
bundle; the script never starts a browser server, binds a port, builds, or decides anything.

Step 6 is where spikes get believed wrongly. A computed-style and pixel diff is blind to anything that
needs an interaction: focus visibility, accessible name, keyboard reach, scroll behaviour. If the
change could plausibly break one, drive it — focus the element and inspect the ring and the node list;
do not report "nothing else changed" about something you could not see.

## Rules that prevent the usual failures

- **Revert is part of the spike.** An un-reverted spike is an unreviewed change to the trunk.
- **State list comes from code** (props, variants, conditional branches), not from the three screens
  you remember. Missing states are how a spike lies by omission.
- **Name the falsifiable version of the claim.** "Adopting X costs a look fight" is testable;
  "adopting X is better" is not.
- **Report the category, not just the count.** A display change on ten units that are pixel-identical
  is structural noise; one broken focus ring is a defect. Both are drift, and they do not belong in
  the same sentence of the report. The script lists; the person categorises.
- **Attribute precisely.** If the run also fails for reasons unrelated to the change, say whose failure
  it is; otherwise the spike absorbs someone else's bug.
- A pass with zero offenders is not proof the measurement ran. Print how many units were captured, and
  fail loudly on any state the capture could not reach.
- **State what the method cannot see.** Every report ends with the unproven list: the states not
  reachable, the interactions not driven, the viewports not covered. An empty list is a claim about
  coverage, so it has to be true.
- **Write the acceptance rule before the data.** A threshold chosen after seeing the numbers is
  taste with a table under it; pre-registering also makes "the result says adopt it" a legal outcome
  rather than a concession.
- **A green suite is not evidence the change is covered.** If the project has tests, plant the fault
  the change would cause (a `type` that stops submitting, a disabled element that stays clickable) and
  require red. A suite that stays green through a deliberate fault is blind to this change.
- **Identity is not correctness.** Two units can be identically wrong — the same sub-44 px touch
  target, the same failing contrast. Matching tells you they agree, not that either is right.
- **Measure the state the plan creates, not only the state between the arms.** If the prize is
  deleting our code, an "identical" result captured while our stylesheet still applies to the new
  component is a loan from the code being deleted; run that comparison again with our CSS no longer
  reaching it (references/reading-the-numbers.md §1.1).
- A verdict holds for the version it measured. Say which one; the next dependency bump is a new spike.
- One unit, one change. If the edit touches two components, the drift cannot be attributed to either.

## Resources

| File | Read when |
| --- | --- |
| [references/states-and-metrics.md](references/states-and-metrics.md) | steps 2, 3 and 6: deriving the state list from code; what each sensor can and cannot see |
| [references/reading-the-numbers.md](references/reading-the-numbers.md) | steps 5 and 7: drift categories and the report shape |
| [examples/case-01-seam-swap.md](examples/case-01-seam-swap.md) | a whole worked spike in which half the claim was refuted by the measurement |
| [examples/case-02-blind-to-interaction.md](examples/case-02-blind-to-interaction.md) | a clean pixel diff that missed a real defect because nothing was focused |
| [assets/spec.example.json](assets/spec.example.json) | the capture spec: routes, locators, properties, interactions, ignore lists |
| `scripts/spike.mjs` | `capture` + `diff`; arithmetic only, never a verdict (`--help`) |
