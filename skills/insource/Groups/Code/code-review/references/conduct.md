# Review conduct — honest, prioritized, fast

## Honesty rules (all authors: human, your own, or another agent's)

- **Don't rubber-stamp.** "LGTM" without evidence of review helps
  nobody — an approval is a claim you verified.
- **Don't soften real issues.** "A minor concern" about a
  production-hitting bug is dishonest labeling; severity labels exist
  so softening has nowhere to hide.
- **Quantify when possible.** "~50ms added per list item" beats "could
  be slow".
- **Push back with an alternative.** Sycophancy is a failure mode of
  reviews; if the approach has a problem, say so directly and propose
  the other shape.
- **Comment on the code, not the person** — reframe any personal
  critique into the artifact.
- **Accept override gracefully.** When the author has full context and
  disagrees, defer to their judgment; you advised, they decide.

## The disagreement hierarchy

1. Technical facts and data override opinions and preferences.
2. Style guides are absolute authority on style matters.
3. Design questions are evaluated on engineering principles, not
   personal taste.
4. Codebase consistency is acceptable when it doesn't degrade overall
   health.

**Never accept "I'll clean it up later."** Deferred cleanup rarely
happens. Require it before submission unless it's a genuine emergency;
if surrounding issues can't fit this change, require a filed,
self-assigned bug — then the deferral is tracked instead of hopeful.

## Review speed

Slow review imposes waiting on everyone; the context-switch cost of
reviewing is cheaper than the block you cause.

- Respond within **one business day** — maximum, not target.
- Prefer fast individual responses over quick final approval; several
  fast rounds beat one slow verdict.
- A change too large to review responsively: send it back to be
  split (see `remedies.md` §change sizing), don't review it badly.

## Multi-model pattern

Different reviewers have different blind spots; the pattern that
catches what a single model misses:

```
author writes → second model reviews (correctness, architecture,
conventions) → author addresses → human makes the final call
```

A review subagent's prompt carries the spec, the standards, and the
severity vocabulary — then its findings go through the same aggregation
rules as a human's (no cross-axis reranking).

## Approval, finally

Approve when the change **definitely improves overall code health** —
imperfect is fine, "not how I would have written it" is not a blocker.
Request changes only for Critical/Required items; everything else was
labels' job. State the verdict explicitly; "seems good" is neither a
verdict nor evidence.
