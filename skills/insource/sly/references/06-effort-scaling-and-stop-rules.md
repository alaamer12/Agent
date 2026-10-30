# Effort scaling, timeboxes and stop rules

The hunt costs time. The whole point of Step 0 is to spend it where it changes the outcome, and to stop
where it does not.

## Triage

| The obstacle | Class | Effort | Stop when |
|---|---|---|---|
| typo, missing flag, wrong URL, one 4xx you can explain | **snag** | one detour check, a few minutes | fixed, or the explanation says otherwise |
| documented capability you cannot reach with your access or config | **near blocker** | confirm with two independent signals | confirmed blocked, then one family explored |
| a feature the system genuinely does not expose | **blocker** | full hunt: 3+ routes, researched, scored | a route chosen, or nothing viable found |
| the route changes cost, product behavior, scope, or a contract | **consequential** | hunt, then ask | the user answers |
| the block is peripheral to the user's actual goal | **non-block** | do not hunt | you noticed it is irrelevant |

Misclassification is the failure. Treating a snag as a blocker burns an afternoon on a typo in a query
parameter; treating a blocker as a snag ships a feature that will silently do nothing next month.

## Timeboxes

Default budgets, adjust for the project's size and the feature's value:

```text
snag              10 min      confirm or reject the simple explanation
near blocker      25 min      prove or disprove the block with evidence
blocker hunt      60-90 min   goal extraction + 3 families + research + scoring
pattern rebuild   first slice in 1 day, then measure before investing more
consequential     hunt inside the budget, then STOP at the question
```

A pattern-extraction route scales infinitely by accident. Cap the characterization phase, ship a thin
version, measure it against the acceptance test, and only then decide whether the next hour is worth it.

## Stop rules

Stop hunting and go to Step 6 (ask or report) when any of these is true:

- **Two strikes on one method.** The same target through the same mechanism failed twice with cosmetic
  differences. That is repetition, not persistence.
- **Every remaining route crosses a hard line.** Say which line blocks which route, and ask for the
  legitimate access instead.
- **The evidence contradicts the premise.** The block was real, but your read of the goal was wrong -
  return to [`01`](01-goal-and-value-extraction.md), do not keep building.
- **Cost has passed value.** The workaround will cost more than the feature is worth. This is a legitimate
  finding and an honest report, not a failure.
- **You are three hours in with no scored options.** Almost always means you have been refining one route
  instead of generating three.
- **Research depth exceeds the decision's weight.** A reversible choice does not need a literature review.

## Anti-repetition mechanics

The ledger in [`02`](02-verifying-the-block.md) is what makes "don't repeat failures" checkable instead of
a slogan: every attempt gets a row, a repeat is detected by matching target plus mechanism, and
`scripts/routes.py` flags rows whose signature duplicates an earlier failure. Write rows as you go - a hunt
with no ledger is a hunt you cannot defend or resume.

## Proportionate effort, stated out loud

Say which class you assigned and what you will spend. It prevents the two opposite complaints: "why did you
spend four hours on this" and "why did you give up in two minutes".
