# Route Decision: <short name - what was blocked and what was chosen>

Status: accepted | proposed | superseded   Date: YYYY-MM-DD   Class: snag | blocker | consequential
Decided by: <agent on user request / user / team>   Re-check on: <date or condition>

## The goal, apart from the method

- **Goal:** <what must be true afterwards, in the user's language - do not name the blocked thing>
- **Value needed:** <the datum / behavior / guarantee / affordance, and where else it exists>
- **Acceptance test:** <the observation that proves the value landed, with the number to beat>

## The block

- **Blocked:** <what is unavailable>
- **Evidence:** <two or more independent signals, each with a source>
- **Confidence:** high | medium - <why>
- **Assumption challenged:** <what we believed that turned out not to be the requirement>

## Options considered

| Option | Family | Goal | Feas | Rel | Maint | Sec | Cost | Fit | Frag | Weighted | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| <name> | reroute/replace/rebuild/reshape/reduce | | | | | | | | | | chosen |
| <name> | | | | | | | | | | | vetoed - <hard line> |

Weights used: <goal x, feasibility x, ...> - and why they differ from the defaults, if they do.

## Chosen route and what it costs

- **Route:** <name and one-line mechanism>
- **Main trade-off accepted:** <the single cost you are knowingly taking on>
- **Reduced or cut:** <what the user does not get, stated plainly - "nothing" is a valid answer>
- **Access parity:** <how the route stays inside what an ordinary legitimate user would see or do>
- **Contextual restriction note:** <one line, only if a ToS/contract/licence matter genuinely applies here>

## Fragility and detection

- **Depends on:** <published contract | observed behavior | undocumented internals>
- **Breaks when:** <the concrete change that would break it>
- **We will notice by:** <the check, alert, or test that fails loudly>
- **Fallback when it breaks:** <the route to fall back to>

## Verification

- **Derived or substituted data checked against:** <the real thing, and the agreement measured>
- **Acceptance test result:** <number, baseline, pass/fail>
- **Held-out cases:** <count and where the result is weakest>

## Follow-ups

- <the legitimate access that would retire this workaround, and who asks for it>
- <the date or condition to re-check whether the block still exists>
- <what to delete when the supported path arrives - workarounds that outlive their block are debt>
