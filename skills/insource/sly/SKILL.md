---
name: sly
description: 'Resourceful route-finding when the obvious path is blocked: capture the value, not the access. INVOKED ONLY WHEN THE USER ASKS - ''/sly'', ''be /sly and find a solution'', ''think /sly and tell me what to do'', ''be cunning about this'', ''how do we get X without Y''. Never self-activate on a missing capability: report it, offer /sly. Once asked, run the full hunt: separate the real goal from the proposed method, verify the block, state the value needed, then produce at least three materially different routes across the five families (reroute, replace, rebuild from observed behavior, reshape, reduce), gate them on access parity, score on eight axes, pick on merit not cleverness. Hard lines: never bypass authentication or protections, never use credentials or private data not yours, never exploit, never damage or overload a third-party system, never exceed the user''s own authorization - a route needing any of those is not a route. ToS/licensing are a trade-off note, not a gate. Derived data is verified, never faked.'
when_to_use: Only when the user explicitly asks for it - "/sly", "be /sly about that", "think /sly and tell me what we need to do", "be cunning, find another way", or "how do we get X without access to Y". Never self-activate on a blocked path.
argument-hint: "[what is blocked] + [what you actually need from it]"
---

# Sly - get the value when the door is shut

The moment an obvious path fails, most agents stop and report "not supported". That is a
category error: the unavailability of **one route** is not proof that the **outcome** is impossible.

> **Capture the value, not the access.**
> Do not ask "how do I get through?" Ask: *what do I actually need from this, and what other ways
> exist to get that same value?* Then find another route to the same goal.

Sly is cunning, not destructive. Everything below sits inside one gate: **access parity** — you may
use only what an ordinary, legitimate user of the system would see, receive, or be able to do.
Learn how a thing works and build your own version. Never break in.

## Who starts it - the user, always

Enter this skill **only** on an explicit ask: `/sly`, "be /sly and find a solution for that", "think /sly
and tell me what we need to do", "be cunning about this", "how do we get X without access to Y".

Stumbling on a blocked path is not a licence to start hunting. When something is unavailable and the user
has not asked: report the block in one line, name the most promising family to try, and offer that `/sly`
can look for another route. Then stop and wait.

Once the user asks, run the **whole** workflow - no half-measures, no "here's one idea" answer.

## Step 0 - Decide whether the hunt is worth it

Scale effort to the obstacle before spending anything ([`06`](references/06-effort-scaling-and-stop-rules.md)).

| The block is | Do this |
|---|---|
| a small snag (typo, missing flag, wrong URL, one 4xx) | one brief detour check, then continue |
| a blocker threatening the feature | real hunt: ≥3 routes, researched, compared |
| a decision with cost, legal, or architectural consequence | hunt, then **present options and ask** |

Do not run a deep investigation for trivial snags, and do not "quick-detour" past a blocker that
will still be there next sprint.

## Step 1 - Name the real goal, separate from the method

Write one sentence: *the user needs X, and the method proposed (the blocked thing) is only one way to
get X.* The proposed method is a means, not a mandate. If you cannot state the goal without naming the
blocked component, you have not extracted the goal yet — that is where lazy agents fail, and
[`01`](references/01-goal-and-value-extraction.md) is the drill for it.

Record three things before generating anything: the **goal**, the **value actually needed** (the specific
data, behavior, guarantee or affordance — not "access to the service"), and the **acceptance test** that
would prove the value was captured.

## Step 2 - Verify the block is real

A single failed attempt is not proof. Most "impossible" calls are a wrong endpoint, a missing scope, a
beta path, a header the SDK hides, a feature flag, a regional limit, or a wrong assumption about what the
tool accepts. Work the false-block catalog in [`02`](references/02-verifying-the-block.md) until the block
is confirmed, or disappears — and log what you tried so the same dead end is not re-attempted later with a
cosmetic variation.

## Step 3 - Generate routes from five different families

At least three options, and they must be **materially different**, not three flavors of the same attempt.
The families ([`00`](references/00-route-families.md), recipes per block type in
[`07`](references/07-playbook-by-block-type.md)):

- **Reroute** - same thing, another door: another endpoint, export, protocol, event stream, webhook, CLI,
  connector, file format, or scheduled pull instead of a push.
- **Replace** - different component doing the same job: alternative service, open-source equivalent,
  commodity library, local model, self-hosted piece.
- **Rebuild from the pattern** - the capability is closed but its behavior is observable, so characterize
  the behavior and implement your own version ([`03`](references/03-pattern-extraction.md)).
- **Reshape** - change the architecture so the blocked dependency is no longer needed: move logic to the
  other side of the boundary, add an adapter or bridge, process locally, introduce a queue or sync job.
- **Reduce** - deliver the most valuable subset when the full goal truly cannot be met, and say plainly
  what was cut.

Research what you do not know; prefer primary sources, and confirm that a route actually supports the
operation you need before recommending it. Evidence over speculation.

## Step 4 - Apply the access-parity gate

Filter before scoring. A route is dead if it requires any hard line
([`04`](references/04-access-parity.md) has the test questions and the borderline cases):

- bypassing authentication or authorization, or defeating protections (including DRM and rate limits
  implemented as a protection);
- using credentials, tokens, sessions or private data that the user is not entitled to;
- exploiting a vulnerability to gain access;
- damaging, overloading, or degrading a third-party system;
- acting beyond what the user is actually authorized to do.

**Terms of service and licensing are not a universal gate** — many tasks have none. When a chosen route
clearly depends on a restriction that matters to the user (a commercial product, a contract, a licensed
API), add one line to the trade-off summary and continue. Only the hard lines stop a route.

## Step 5 - Score the survivors

Rate each route on the eight axes: achieves the real goal, feasibility, reliability, maintainability,
security and privacy, cost and complexity, fit with existing architecture, and **fragility** (how much it
leans on undocumented or unstable behavior). Axes, weights and the worked table are in
[`05`](references/05-scoring-and-tradeoffs.md). `scripts/routes.py` ranks a route file and refuses to let
a parity-breaching route into the ranking.

Choose a route because it is the best way to reach the goal under real constraints — **never merely
because it is clever.**

## Step 6 - Proceed, or ask, or report the dead end

- Trade-off is technical and reversible → state it in one line and proceed.
- Trade-off is the user's to make (cost, product behavior, risk, scope) → **one focused question**, with
  the options and what each costs. Never implement before the answer.
- Nothing viable exists → report what was investigated, what remains blocked and why, and the reduced or
  alternative goals that are still possible. That is a legitimate outcome; concealing it is not.

For consequential routes, write the decision down: `assets/templates/route-decision-record.md`, placed
where this project already records decisions (ADR folder, steering docs, conventions file). Match the
project's incumbent documentation format even where you would do it differently.

## Step 7 - Verify the value actually landed

The hunt is not over when code exists.

- **Verify, don't fake.** Any derived, inferred, substituted or approximated data must be checked for
  correctness and completeness. Never silently swap in wrong information to make a feature look alive.
  Fake success is worse than a blocked feature: it hides the problem from everyone downstream.
- Run the acceptance test from Step 1. If a rebuild-from-pattern route is involved, measure it against
  the observed behavior on cases you held out, and report the agreement rate honestly.
- Be transparent about the assumptions, the fragility, and the part that is your approximation.

## Core invariants

1. Goal over method. 2. Persistence over premature refusal. 3. Diversity over repetition.
4. Evidence over speculation. 5. Practicality over cleverness. 6. Transparency over concealment.
7. **Understand and rebuild, never break in.** 8. Proportionate effort.

## References - update this table in the same change that adds, removes or renumbers any file

| File | Owns | Read when |
|---|---|---|
| [`00-route-families.md`](references/00-route-families.md) | The five families, what each looks like in practice, how to tell a real alternative from a rephrasing | Step 3 |
| [`01-goal-and-value-extraction.md`](references/01-goal-and-value-extraction.md) | Separating the mandate from the means, naming the value needed, writing the acceptance test | Step 1, always |
| [`02-verifying-the-block.md`](references/02-verifying-the-block.md) | The false-block catalog, how to confirm a block with evidence, the failure ledger | Step 2 |
| [`03-pattern-extraction.md`](references/03-pattern-extraction.md) | Characterizing observable behavior and rebuilding it: corpus, format, timing, edge cases, held-out validation, the source ladder | Step 3, any "rebuild" route |
| [`04-access-parity.md`](references/04-access-parity.md) | The hard lines, the parity test questions, borderline cases, ToS as context, what to do when every route crosses a line | Step 4, and whenever tempted |
| [`05-scoring-and-tradeoffs.md`](references/05-scoring-and-tradeoffs.md) | The eight axes with anchors, weights, the worked table, fragility and reversibility, how to present the choice | Step 5 |
| [`06-effort-scaling-and-stop-rules.md`](references/06-effort-scaling-and-stop-rules.md) | Snag vs blocker vs consequential decision, timeboxes, stop rules, anti-repetition | Step 0 and when the hunt drags |
| [`07-playbook-by-block-type.md`](references/07-playbook-by-block-type.md) | Recipes keyed to the block type: no endpoint, no SDK, closed behavior, framework limit, browser/OS sandbox, rate limit, closed format, missing data, cost | Step 3 |
| [`08-anatomy-of-a-hunt.md`](references/08-anatomy-of-a-hunt.md) | The domain-neutral spine, the eight ways a hunt goes wrong with the detector for each, and the three cheap checks that catch most of them | When a hunt is going badly, or to find which step was skipped |
| [`09-reporting-and-anti-patterns.md`](references/09-reporting-and-anti-patterns.md) | The report shape, what goes in the decision record, and the defect list (fake success, method-worship, monoculture routes, silent scope cuts) | Step 6-7 |

## Examples - cases, not templates

One case per file in `examples/`, each walking the full spine on a different kind of block. The rules above
stand on their own; these exist to show what following them looks like. **Read a case only after you have
written your own goal/value/test lines** - importing someone else's framing is how a hunt ends up solving
the wrong problem.

| Case | Block type | Families exercised | The thing it settles |
|---|---|---|---|
| [`case-01-closed-personalization-behavior.md`](examples/case-01-closed-personalization-behavior.md) | a behavior you can watch but not call | rebuild, reroute, replace, reduce | distilling the function is fair; harvesting the outputs wholesale is not |
| [`case-02-sdk-lags-the-api.md`](examples/case-02-sdk-lags-the-api.md) | "the SDK has no method" | reroute, replace, rebuild, reshape | most reported blocks are not blocks |
| [`case-03-credential-cannot-live-in-the-browser.md`](examples/case-03-credential-cannot-live-in-the-browser.md) | a secret in the wrong tier | reshape, replace, reduce | the blocker was the security axis, not the platform |
| [`case-04-legacy-format-with-no-reader.md`](examples/case-04-legacy-format-with-no-reader.md) | a format nobody can open | rebuild, reroute, reduce | verify the reader on a golden set before converting anything |
| [`case-05-air-gapped-environment.md`](examples/case-05-air-gapped-environment.md) | no outbound network | reshape, reroute, reduce | an org policy is a hard stop; "live" is usually "current enough" |
| [`case-06-paywalled-entitlement.md`](examples/case-06-paywalled-entitlement.md) | feature behind a paid tier | reroute, rebuild, reshape, reduce | a paywall is not a puzzle; asking and paying are routes |
| [`case-07-rate-limit-is-capacity-not-protection.md`](examples/case-07-rate-limit-is-capacity-not-protection.md) | throttling at volume | reroute, reshape, reduce | name the kind of limit before choosing around it |
| [`case-08-every-route-crosses-a-line.md`](examples/case-08-every-route-crosses-a-line.md) | nothing is legitimately reachable | reduce | stopping is a deliverable; the reduced goal plus the access request |
| [`case-09-platform-background-restriction.md`](examples/case-09-platform-background-restriction.md) | OS refuses continuous work | reshape, reroute, reduce | sanctioned mechanisms beat circumvention, and often measure better |

## Script and asset

- `scripts/routes.py` - audits a route plan (JSON, or the YAML subset shown in the script header): requires
  goal, value, acceptance test and a proven block with two signals; enforces route diversity across
  families; **vetoes any route flagged beyond access parity** and keeps vetoed routes out of the ranking;
  catches cosmetic retries, goal drift (the goal still naming the blocked thing), unscored axes, unflagged
  fragility, and an unstated trade-off on a consequential route. Exit 1 on findings, 2 on schema errors;
  `python scripts/routes.py` with no argument runs its self-test over ten fixtures. On Windows use `python`,
  not `python3`.
- `assets/templates/route-decision-record.md` - the record to write when a route carries real trade-offs,
  fragility, or a contract question.
