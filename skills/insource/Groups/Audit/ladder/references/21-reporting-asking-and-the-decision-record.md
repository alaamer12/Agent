# 21 — Reporting, asking, and recording the choice

The skill's output is a decision the user made, not a decision the agent guessed at. Three artifacts, in
this order: **findings report → options with trade-offs → written record**. Nothing gets coded between
them.

## 1. The findings report

Compact, evidence-first, no adjectives without a line number. Structure that survives being read in a
terminal:

```
Ladders found: 4 sites, 1 shared concern (failure classification)

1. src/payments/refund.ts:88-140   nested if-chain, depth 4, 7 rungs
   order source: written position        terminal rung: yes -> "manual-review"
   defect: severity inversion — `refund-ok` (allow) precedes `amount > limit` (deny),
          both hold for {amount: 5000, tier: "vip"}; test at refund.test.ts:210 pins today's answer
2. src/lib/http.ts:34-52           catch -> return null       defect: swallow (no cause kept)
...
Guarantee at stake: "no refund above the limit without review" — currently held only by ordering.
```

Then name the shape class once per site (`00`'s vocabulary) so the options below are comparable, and say
what was **not** inspected if the sweep was partial — an audit that quietly covers half the tree is worse
than one that says so.

## 2. Options with trade-offs, then the ask

Present the 2-3 shapes that genuinely fit — not all twelve. `16` has the situation→shape table; use it to
narrow, then present what survives narrowing. Every option gets the same five lines, because an option
without a cost is not an option:

| Option | Shape | What it fixes | Cost now | Cost later | Reversibility | Risk if wrong |
|---|---|---|---|---|---|---|
| A | tiers (deny > ask > allow), scopes inside | the inversion, permanently | refactor of 4 files, ~n steps | authors can't reorder safety; needs a conflict test | high — behaviour-preserving for every input that isn't the buggy one | a policy nobody chose: nearest-scope-allowed becomes deny-always |
| B | rules table + ids, reorder deny first, keep `first` | the inversion today, cheaply | 1 file | order stays a human duty; next broad rule re-breaks it | trivial | the same bug returns with the next contributor |
| C | closed-set dispatch on a discriminated union | totality plus the inversion | biggest diff; touches the type | adding a verdict = compile error | medium | over-engineering if the set stays at three |

Then **recommend one and say why in a line**, and ask. Use the harness's ask/elicitation tool where it
exists; otherwise ask in prose and stop. The question set that actually changes the design:

- Which guarantee must be unbreakable, and is that a tier (`13`) or a priority list (`07`)?
- Who is allowed to add a rung — code reviewers only, or config owners (`06`, `12`)?
- Fail-open or fail-closed on unknown input, and does that match the rest of the repo (`08`)?
- How much churn is acceptable now versus after the next release?

**Never implement before the answer.** If the user deflects ("you choose"), choose, say which axis you
weighted, and record it as their delegation, not your invention. If several sites share one concern and
the answers differ per site, that is a real finding: put both in the report rather than averaging them.

## 3. Recording the decision

Write it **where this project already writes such things** — discover the pattern before inventing one:

| Existing pattern | Write it there |
|---|---|
| `docs/adr/NNNN-title.md` or `adr/` | append the next number, copy an neighbour's heading order and voice |
| `docs/decisions/`, `docs/conventions/`, `rules/`, `design/` | same: match the front matter, section names, and ID format |
| Steering files (`.cursor/rules`, `.github/instructions`, `.repertoire/.steering/<app>/tech/*.md`) | the tech/ folder for the app in question, one file per concern |
| `AGENTS.md`, `CLAUDE.md`, or an agent instruction file | only the short operative rule; the rationale goes in a doc that file points to |
| Nothing at all | one file next to the code it governs, named for the decision, and say that you created the pattern |

Match the incumbent format even where you'd do it differently: heading depth, tense, whether they use
tables, whether status/date/deciders appear in front matter, British or American spelling. A decision doc
that doesn't match its neighbours gets ignored, and an ignored decision doc is how the ladder gets
re-litigated in six months.

Minimum content — short is fine, absent is not:

```markdown
## Ladder for refund approval — tiers, not position
Status: accepted (chosen by <user>, <date>) · Scope: src/payments/**
Guarantee: no refund over the limit without a human review, not overridable by any scope.
Chosen: fixed tiers (deny > ask > allow), tiers outside scopes. Rejected: rules table by position
        (order stays a human duty), closed-set dispatch (churn disproportionate to the 3 verdicts).
Consequences: adding a rule cannot weaken the guarantee; the price is a conflict test per pair of
        tiers, and deny-tier rules read first, so a slow deny check is now on every path.
Terminal rung: "ask/manual-review", reached in the normal case for unknown shapes.
Verification: ladder_audit clean (no shadow, no inversion, totality held) +
        refund.test.ts:210 updated to expect deny; see 15 for the matrix.
```

Then a one-line pointer from wherever developers look (the module's doc comment, the conventions index) —
a record nobody can find is a record nobody follows.

## 4. Handoff to implementation

The record is now the spec. Implement to it exactly, and if implementation reveals the choice was wrong
(a tier needs a verdict that doesn't exist, a config grammar turns out to be too small), **stop and
update the record with the reason** rather than silently deviating — the deviation is the thing that
surprises the next reader. See `22` for expressing it without nested conditionals and `15` for the tests
that make the guarantee hold.
