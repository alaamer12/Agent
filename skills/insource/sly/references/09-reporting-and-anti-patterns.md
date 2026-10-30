# Reporting, records, and the defect list

The hunt is only finished when someone else can see what was blocked, what was chosen, why, and what is now
true that was not true before. A workaround nobody can explain is a liability.

## The report

Put this at the top of your answer when the user asked for a hunt, then implement if the choice was yours to
make. Keep every line short - this is a decision summary, not a diary.

```text
BLOCKED  <what was blocked> - verified: <2+ independent signals>          class: snag | blocker | consequential
GOAL     <what is actually needed, without naming the blocked thing>
VALUE    <the datum / behavior / guarantee needed, and where else it exists>
ROUTES   <n> options across <families touched>     gate: <n> rejected on access parity
CHOSEN   <route> - <one-line reason>               TRADE-OFF <the main cost you are accepting>
TEST     <the acceptance check that proves the value landed>  STATUS <pass/fail + measured number>
CUT      <what was reduced, if anything>           FRAGILE <what breaks this and how you will notice>
```

When nothing viable exists, that same shape is still the report: `ROUTES 0 survive`, `CHOSEN - none`, plus
what legitimate access would unblock it and what reduced goal is available now.

## The decision record

Write one when the route is fragile, costly, contractual, load-bearing, or the second workaround in that
area. Use `assets/templates/route-decision-record.md`.

Put it where the project already keeps decisions - the ADR folder, the conventions or steering docs, the
architecture notes. Discover the incumbent pattern before inventing one, and match its format even where you
would do it differently; a decision record nobody can find is a decision nobody remembers.

## Anti-patterns

Each of these has been shipped by a competent agent. They are the failure modes of resourcefulness.

| Defect | What it looks like | Why it is bad | Instead |
|---|---|---|---|
| **Fake success** | the feature renders; the data is a placeholder, a guess, or a stale copy | hides a hole from every downstream consumer, and the user finds out in production | label derived/approximated/absent values; unknown renders as unknown |
| **Method worship** | "impossible because X has no API" | confuses one route with the outcome | restate the goal without naming X ([`01`](01-goal-and-value-extraction.md)) |
| **Monoculture routes** | three options that are one option in three costumes | the comparison is theater | force two different families, check mechanism-level difference |
| **Cleverness bias** | picking the intricate route because it is impressive | complexity you must maintain forever | score it; if cleverness is the only argument, it loses |
| **Gate-after-score** | a parity-breaching route ranked first, then quietly dropped from the summary | the ranking was a lie, and the temptation is re-served to the next reader | filter first; vetoed routes never enter the ranking |
| **Silent scope cut** | Reduce ships without naming what was dropped | the user believes they have the feature | say what was cut, in the report and the UI |
| **Stale workaround** | the hack outlived the block; the vendor shipped the endpoint years ago | doubles maintenance and hides the supported path | record the re-check condition, review it on a date |
| **Retry loop** | same method, new parameter, again | burns the budget and proves nothing new | two strikes, then a different family ([`02`](02-verifying-the-block.md)) |
| **Unflagged fragility** | a route resting on undocumented internals presented as solid | breaks at the worst possible time, with no detection | score fragility, say what will notice the break |
| **Boundary drift** | "just this once" access beyond the ordinary-user path | it is not a route, and the framing makes it feel minor | stop, name the line, ask for the legitimate access |
| **Assumed consent** | the user's data or account used in a way they did not agree to | trust and, sometimes, law | ask, or don't |
| **Effort inversion** | an afternoon on a snag, two minutes on a blocker | proportionality is a skill, not a mood | classify at Step 0 and state the class |

## Verification obligations

- Substituted, inferred or derived values are checked against something real before anything is deleted,
  overwritten, or migrated. Prove it on a known case first.
- The acceptance test from the goal line is run, and the number is reported - including when it is low.
- Anything monitored-by-hope is instead monitored by a check that fails loudly.
- The route is reversible, or the record says who signed off on irreversibility.

## When the right answer is to stop

Some goals need the owner's permission, a contract, a purchase, a partner endpoint, or a data-sharing
review. Obtaining that is the workaround. Report what is blocked, what you need, and what you can ship
meanwhile - then ship the meanwhile.
