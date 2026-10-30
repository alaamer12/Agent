# What is the best way?

The question repeats on every decision, small or architectural. "Best" is not a feeling and not the most
sophisticated option — it is the strongest option **for this problem, this data, this team, this deadline**,
chosen after the alternatives were actually looked at.

```text
decide  →  implement  →  ask again: "what is the best way to do THIS next piece?"
                          ↑ the loop never runs once; it runs per decision
```

Two failures bookend it: shipping the first thing that works, and refusing to stop improving. Both are the
same defect — the alternatives were never compared on purpose.

## The trade-off ledger

For any decision with more than one plausible answer, write five lines before coding. Not a document — a
paragraph, or a decision record if it is lasting ([`03`](03-running-under-iwts.md)).

```text
Question   <the choice the work actually forced, as a sentence>
Options    A <one line> · B <one line> · C <one line>        (2-4 real ones, no straw men)
Criteria   <which of these matter HERE: correctness · robustness · reliability · maintainability
           · performance at the measured load · reversibility · consistency with this codebase
           · user-visible experience · cost of owning it>
Choice     C — because <the two criteria that decided it>
Accepted   <what C gives up, stated out loud>            ← a decision that sacrificed nothing is marketing
```

**Steelman the loser.** Write the strongest sentence for the option you rejected. If you cannot, you did not
understand it yet — that is the moment to reread it, not to proceed.

```text
Rejected A: "LIKE '%q%' is one line and zero moving parts."
           → it stays correct at 300 rows and silently becomes a 2 s full scan at 40 k.
             At this product's size (measured: 12 k, growing weekly) the failure is scheduled, not hypothetical.
Chose  B:  local FTS index — costs a rebuild-on-write path, buys a stable 40 ms and real tokenization.
```

## Best ≠ most complex

Complexity must be **paid for by a requirement that exists now**, not by one that is plausible later.

> The test: *which present requirement breaks under the simpler version?*

If you can name it, the machinery is earned. If you cannot, the simple version **is** the best solution and the
complex one is a liability with extra steps.

| Complexity | Verdict |
|---|---|
| an abstraction layer for a second implementation that exists today | earned |
| a plugin system because a second tenant "will come" | not earned — the second tenant will also change the interface |
| caching because the measured path is 1.9 s and users wait on it | earned |
| caching because a hot path might become a problem after launch | not earned — and it hides a correctness bug in the meantime |
| a queue, because a partner's outage must not lose deliveries | earned |
| a queue, because "we'll need it to scale" | not earned — and now the team operates infrastructure |

The opposite failure is equally expensive: **insisted-on simplicity where the problem genuinely needs
machinery.** "Just filter in the front end" for 2 M rows, "just retry the whole job" when a partial failure
costs an hour, "just use a global" when three screens write the same state. When the requirement forces
complexity, building it is the professional answer and the extra care is not scope creep — it is the job
([`01`](01-behind-the-visible-requirement.md)).

The question is always: *what solution provides the best result for this problem and this user?*

## Reversibility, the underrated criterion

Prefer designs where a later change touches one boundary rather than many. Ask while designing: *if this
changes later, how much must change?* The right answer is "only the adapter" far more often than teams
discover.

```text
  many call sites → concrete thing            a change fans out everywhere
  many call sites → narrow seam + one adapter a change lands in one place
```

In any stack the seam is the same idea — an interface in [TypeScript]/[Java]/[C#], a module or trait/protocol
in [Python]/[Rust], a package boundary in [Go], one function returning rows behind [SQL] views. What differs is
only the spelling.

**Reversible does not mean uncommitted.** Make the decision firmly, build against it, and keep the seam honest.
Accidental lock-in is the failure; earned lock-in is engineering. Some choices should be hard to reverse — a
data model, a public API, an event schema. Say plainly which ones you are committing to, and why the
commitment is still right.

## Edge cases worth designing for

Not exhaustive — the ones that actually break products. If one produces a user-visible state, that state is
part of the feature, not a follow-up.

```text
empty · single item · one huge item · 10k items · duplicate · missing optional field
hostile or unexpected input · unicode/emoji/RTL/accents · clock: timezone + DST + midnight boundary
partial failure · concurrent writes · retries arriving twice · network dies mid-request · permission denied
```

Pick the ones this feature can actually meet and handle them deliberately; note the ones it cannot as
findings. The list is a prompt for judgment, not a task list.

## Re-asking, and when to stop

**Ask again** before finishing any component: *is there a materially better way?* Usually the second look
finds one of three real things — an edge case unhandled, a seam missing, or a simpler version that solves the
same requirement. Those are worth the hour.

**Stop optimizing** when one of these is true, and say which:

- The remaining alternatives differ in taste, not in user-visible or operational consequence.
- The measured problem is solved with margin; further work defends against numbers the product does not have.
- The next improvement changes a requirement (caching semantics, staleness, an operational dependency) — that
  is not an implementation decision, it is the user's ([`00`](00-the-authority-line.md)).
- Time-box reached: the deadline is a real constraint and the honest move is a shipped-good version plus a
  named finding, not a half-migrated version of a better idea.

Under an autonomous run, "stop" also has a documented reason: an endless-optimization loop is activity, not
progress, and the user wakes to churn.

## Ties, and thin evidence

- **A genuine tie** → pick the option the existing codebase already knows how to maintain; consistency is a
  real criterion and second-order cost is first-order reality. Record that it was a tie, so a successor does
  not think there was a hidden reason.
- **Chosen on thin evidence** → proceed anyway (a decision is better than a stall), but write the uncertainty
  down: what was guessed, what measurement would overturn it, and how expensive overturning would be. That
  note is what turns a guess into revisable engineering.
- **Two options where one is better and much slower to build** → the cost of your time is not a reason to
  ship the weaker one; the cost of the *user's* schedule, complexity budget, or ownership is. Say which you
  are invoking.
