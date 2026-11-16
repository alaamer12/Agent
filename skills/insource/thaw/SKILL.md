---
name: thaw
version: 1.0.1
author: Amr
specialized: none
description: Anti-rigidity posture for drafting and design sessions. Hold docs, doctrines, and the user's prior answers as provisional material, not law; separate stable invariants from draft mechanisms; keep re-validating and aim for iteratively better. Use when an agent reifies a draft into a hard constraint, prunes options by citing draft docs, anchors on its own earlier recommendation, or settles at "good enough" — or when the user says "thaw", "thaw this", "we're drafting", "don't treat the docs as law", "question my answer", "aim for better", or "re-validate yourself". Pairs with close-topics, techstack, grill-me, and steering.
when_to_use: During drafting/design, when a draft doc, doctrine, or prior answer is being treated as fixed law, options are pruned by draft constraints, or improvement stops at "good enough"; or on an explicit "thaw" / "we're drafting" / "aim for better" / "re-validate".
argument-hint: "[the doc, decision, or recommendation to thaw]"
---

# Thaw — drafts are clay, not law

> We are drafting. A good doc is the **best so far**, not the final word. We can write something
> good, find something better, then find something better still — that is the lifecycle. The docs
> are not forced; they are trying to reach a better point. So nothing here is fixed rigid solid:
> not the files, not the doctrines, and **not the user's answers either**. Aim for better, and
> re-validate yourself.

A draft freezes when an agent starts treating it as law — citing it to kill options, defending its
own earlier pick, or stopping at "good enough". **Thaw** melts it back to a workable state so it can
be reshaped toward better. The name is the move: *thaw this spec, thaw that decision, we're drafting
— thaw it.*

## The failure it corrects

Watch for an agent (you) doing any of these mid-draft:

- **Reifying a draft** — "the doctrine mandates a specific mechanism, so option X is eliminated." The doctrine
  is a draft mechanism, not a law of nature.
- **Pruning by draft constraint** — killing a candidate because it conflicts with a doc that is itself
  still being designed.
- **Anchoring on your own pick** — defending last turn's recommendation because you said it, not because
  it is still the best.
- **Treating the user's answer as non-questionable** — taking a reply as a settled mandate instead of
  the current best input, open to a better framing.
- **Stopping at "good enough"** — closing a topic when a materially better design is reachable.

## When to thaw

- **Explicit ask:** `/thaw`, "thaw this", "we're drafting", "don't treat the docs as law", "question my
  answer", "aim for better", "re-validate yourself", "make the better even more better".
- **Self-trigger:** the moment you notice yourself doing any failure above during a drafting/design
  session. You do not need permission to re-validate your own reasoning.

Do **not** thaw genuinely settled ground (see Hard lines). Thaw is for the provisional, not the closed.

## The move — re-validation

1. **Notice the freeze.** Name the thing you are treating as law: a doc, a doctrine, a constraint, your
   own recommendation, the user's last answer. Say it plainly: "I froze X."
2. **Split invariant from mechanism.** Ask the tier test: *if the whole stack were rewritten, would this
   still be true?* The stable business truth (the **invariant**) stays; the technical **mechanism** that
   enforces it is draft and revisable. Most "hard constraints" in a draft are mechanisms wearing an
   invariant's clothes. Lens: [`references/invariant-vs-mechanism.md`](references/invariant-vs-mechanism.md).
3. **Re-open the option set.** Put the candidates you pruned back on the table. A draft doctrine cannot
   eliminate an option; only a real invariant or a real user constraint can.
4. **Question both sides.** Steelman your own pick, then attack it. And question the user's answer — not
   to contrarian them, but to check it still serves the goal now that the frame changed. New evidence
   beats old answers, yours and theirs. Moves: [`references/revalidation-moves.md`](references/revalidation-moves.md).
5. **Aim for better — then better still.** Reach the best design reachable *now*, knowing a later pass
   may beat it. "Best so far" is the target, not "final".
6. **Re-close provisionally.** A thawed topic still closes (pair with `close-topics`): in **Draft**, write
   it as a revisable steering note — alternatives, trade-offs, open ends — not a formal ADR. Provisional
   closure is closure, not limbo. The form follows the project state (see below).

## Hard lines — what thaw is NOT

- **Not "ignore the docs."** Docs are evidence and the best current thinking — read them, respect them,
  then hold them loosely. Thaw re-opens; it does not discard.
- **Not relitigating the closed.** Stable perception-tier invariants (business truth) and decisions the
  user has genuinely settled are not reopened for sport. New evidence or a changed direction reopens a
  topic; boredom does not.
- **Not endless churn.** Thaw until the decision is the best reachable now, then close. The lifecycle
  iterates across passes, not within one paralyzed moment.
- **Not contrarian for its own sake.** Question to reach better, not to perform doubt. If the current
  answer is still the best, say so and keep it.
- **Decisions still belong to the user.** You own the re-validation and the reasoning; they own the call.
  Recommend plainly, never decide the requirement yourself.

## Project state sets the form

Thaw is the **Draft [DR]** posture — deciding and refining before implementing. The project moves
through three states, and the state decides how a decision is written down:

- **DR (Draft)** — clay. A thawed decision re-closes as a **provisional, revisable steering note**,
  never a formal ADR / `decisions/` record. Casting a draft into a formal record is itself a freeze.
- **IP (In-Progress)** — implementation, testing, launching. Drafting has ended; decisions settle into
  code and may be cast into formal records (ADRs). This is when bronze is appropriate.
- **PP (Post-production)** — first release live. Decisions are settled history.

So thaw keeps the draft workable in DR; formalizing into `decisions/` is correct only once the project
advances to IP/PP. Do not formalize a draft prematurely — that is the freeze this skill exists to prevent.

## Pairing

- `close-topics` — thaw re-opens a frozen topic; close-topics walks it to a provisional close and writes
  it down. Thaw is the stance, close-topics is the cadence.
- `techstack` / `grill-me` — thaw keeps their option sets honest: no candidate killed by a draft, no
  recommendation defended past its evidence.
- `steering` — the invariant/mechanism split maps to its perception (stable) vs tech (evolvable) tiers.

## Resources

| File | Owns | Read when |
|---|---|---|
| [`references/invariant-vs-mechanism.md`](references/invariant-vs-mechanism.md) | The tier test, how to tell stable invariant from draft mechanism, worked splits | Step 2, whenever a "hard constraint" appears |
| [`references/revalidation-moves.md`](references/revalidation-moves.md) | The frozen-signs catalog, how to question your pick and the user's answer, the better-still loop, stop rules | Steps 1, 4, 5 |

## Examples — cases, not templates

One case per file. The stance above stands on its own; these show what thawing looks like. Read a case
only after you have named your own frozen thing — importing someone else's framing is how you thaw the
wrong problem.

| Case | The freeze | What it settles |
|---|---|---|
| [`examples/case-01-draft-doctrine-as-law.md`](examples/case-01-draft-doctrine-as-law.md) | a draft mechanism used to eliminate options | the invariant was the requirement; the mechanism was draft |
| [`examples/case-02-anchored-recommendation.md`](examples/case-02-anchored-recommendation.md) | defending your own earlier pick | new evidence and a changed goal outrank last turn's answer |