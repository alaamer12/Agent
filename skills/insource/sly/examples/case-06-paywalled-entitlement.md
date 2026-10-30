# Case 6 - the feature is behind a paid tier

**The ask:** "we need the audit-log export. It's on the enterprise plan and we're on the team plan."

## Goal, separated

```text
GOAL  : answer "who changed this record, and when" for any auditor or customer complaint
VALUE : an append-only trail of mutations, retained long enough to answer a question about the past
TEST  : for a set of known edits, the trail shows actor, timestamp, before and after
```

The word "export" in the ask is the method; the trail is the value.

## Class

**Consequential.** This route touches money and a contract, so the hunt ends in a question to the user, not a
commit.

## The one route that is dead immediately

Circumventing the plan check - a modified request that reaches the enterprise behavior, a stolen session, a
trial-reset trick. That is the entitlement working as designed, and defeating it is a hard line, not a
workaround. Nothing else in the case matters as much as this being said plainly.

Also dead: scraping another customer's data out of a shared endpoint to "reconstruct" logs. Not yours, not
accessible, not remotely similar to what an ordinary user gets.

## Live routes

| Route | Family | Trade-off |
|---|---|---|
| Buy the tier, or ask the owner to fund it for the quarter | reduce-the-problem | costs money; retires the workaround entirely |
| Ask support whether the trail is available on request or via a bulk compliance export | reroute | free, sometimes an hour of email, occasionally a formal request process |
| Emit our own audit trail at the application boundary: every mutation our code makes, logged to our store | rebuild | covers our actions, not the vendor's; often 80% of the real need |
| Derive a partial trail from record versions the team plan *does* expose | rebuild | gaps where versions are pruned; fragile but honest |
| Poll and snapshot the current state nightly, diff into history | reshape | you get history from tonight forward, never retroactively |
| Answer the question differently: a change ticket plus a required reason field | reshape | cheap, and sometimes what auditors actually accept |

## What gets presented to the user

Not a single answer - a choice with prices on it: pay, ask, or rebuild our own trail from here forward.
The record notes which one, the tolerance ("retroactive coverage for last year is impossible without the
vendor"), and the re-check condition ("if compliance export becomes available on our plan, snapshot diffing
can be dropped").

## What this case teaches

A paywall is not a puzzle. The skill's job is to find the value by another route - including the very real
route of asking and paying - and to name the one route that looks like ingenuity and is actually intrusion.
