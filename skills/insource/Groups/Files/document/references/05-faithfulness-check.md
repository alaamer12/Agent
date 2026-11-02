# The faithfulness check

The step most often skipped, because a fluent summary *feels* finished. It isn't, until checked against the source for a specific set of failure modes — this matters more for AI-generated summaries, since abstractive rewriting is exactly where confident-sounding but ungrounded content creeps in. Applies in both Normal and Extreme mode; Extreme's brevity is not license to skip it.

## Why this is a separate pass

Drafting optimizes for fluent, well-weighted prose — a goal that can quietly produce sentences that sound right without being checked against the source. Treat verification as a distinct pass after the draft is otherwise complete.

## Five checks per claim

1. **Attribution** — is this actually in the source, not just "consistent with the topic"?
2. **Epistemic status preserved** — if the source hedged ("may," "preliminary," "one study found"), does the summary still hedge? Turning "preliminary results suggest X" into "X" manufactures false confidence — the most common failure mode.
3. **Scope preserved** — a bounded claim (specific population, time window, condition) shouldn't silently generalize.
4. **Numbers and names exact** — every figure, date, percentage, proper noun matches the source exactly.
5. **No manufactured connections** — check every "because/so/as a result" — did the source actually assert that link, or did compression introduce it?

## Checking for omission

Faithfulness also means not silently dropping what the source treated as important. Confirm:
- Stated caveats/limitations made it in.
- Disagreement or dissent is represented, not resolved into false consensus.
- The conclusion's actual strength matches the source (tentative stays tentative).

## The reverse-trace technique

For any summary of meaningful length: take each summary sentence (or, in Extreme mode, each term/line) and locate where it comes from in the source. If you can't point to it, it's either a reasonable synthesis of several passages (fine — be able to name which) or invented during compression (not fine — cut or correct it).

## Summarizing to a stated slant

A request to summarize "to sound more positive/negative" shifts toward persuasive writing. Selecting which true content to lead with is fine; inventing unstated benefits, fully suppressing a material caveat, or asserting something the source doesn't support is not. Flag the distinction if a request risks crossing into distortion.

## When the source itself is wrong

Summarize what the source claims, attributed as the source's claim — don't silently "correct" it into something it never said, but flag a clear discrepancy briefly if useful to the reader.

## Final checklist

- [ ] Every claim traces to a specific place in the source.
- [ ] Every hedge/qualifier survives at the same strength.
- [ ] Every number, date, and proper noun matches exactly.
- [ ] No causal/logical connective asserts a link the source didn't make.
- [ ] Material caveats, limitations, and dissent are represented, not smoothed away.
- [ ] Nothing is invented to fill a gap or sound more concrete.
