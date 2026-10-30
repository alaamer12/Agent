# Pattern extraction - rebuild the capability, not the asset

> If a capability is closed but its behavior is observable, study what goes in and what comes out, then
> reproduce the function in your own system.

This is legitimate reverse engineering of *behavior you are allowed to see*. It is not extraction of data
behind a lock. [`04`](04-access-parity.md) is the gate; this file is the method.

## What counts as observable

Anything an ordinary, legitimate user of the system receives without special privileges: what renders on
the screen, what a public page returns, what a downloaded file contains, what the app sends to *itself* over
the network with its own credentials, the order things appear in, the timing and shape of responses, error
messages, changelogs, talks, papers, patents, support answers, and the user's own export of their own data.

What is **not** observable: anything requiring you to present credentials that are not yours, defeat a
protection, or obtain a response the system would not give an ordinary user. If a route needs that, stop and
go back to the families - the behavior is not the only value available.

## The source ladder - most to least direct

Use the highest rung that answers the question, and only descend when it does not.

1. **Published material** - docs, API specs, format specs, RFCs, engineering blogs, conference talks,
   papers, patents. Cheapest and most honest; often complete for the rules you need.
2. **Open implementations of the same idea** - an OSS parser, ranking engine, protocol
   implementation. Read it for the structure and the parameters people found to matter.
3. **The user's own data and feedback loops** - their records, their own interaction history, their
   A/B outcomes. Frequently *better* than the original because it is fitted to their product, not to a
   global audience.
4. **Ordinary-user observation** - characterize what the system does by consuming it as a normal user would,
   at human-scale volumes, and inferring the rule.
5. **Commodity alternatives** - something off-the-shelf already covers most of the need. Sometimes the
   honest answer to "how do we get that behavior" is "we don't need to rebuild it at all".

## Characterizing a behavior

Five things make a pattern reproducible. Capture all five, or the rebuild will not survive contact with
reality.

| Dimension | Question | Recorded as |
|---|---|---|
| Input space | what does the system get: user state, context, candidates, recency | a feature list, not vibes |
| Output form | ordering, score, set, label, timing, placement | exact shape and cardinality |
| Structure | what groups/segments/pools appear, and how items enter them | a decomposition |
| Response to change | what moves the output when you change one input as a user would | sensitivity notes |
| Edge behavior | cold start, unknown item, empty context, extreme values, ties | an expectations list |

## Distilling a closed behavior

Some capabilities you admire are only reachable as a customer: a ranking, a filtering rule, a pricing
calculation, a moderation decision, a layout choice. You cannot get their implementation, and you do not need
it. You need the *function*: given this input, produce this output. So:

1. **Learn what matters** from published material and open implementations of the same idea - which signals
   people find predictive, which constraints the visible behavior respects, what magnitudes are typical.
2. **Build the corpus from the user's own side** - their objects, their history, their outcomes, with consent
   and inside their own product. This is what makes the result fit rather than mimic.
3. **Fit your own version**, smallest first. A handful of features plus a simple model usually beats an
   elaborate guess, and it stays explainable and swappable.
4. **Use ordinary-user observation for calibration, not for cloning** - consume the thing the way a person
   would, notice the qualitative rules its output obeys, and encode the *principle*. Bulk-harvesting the
   system's outputs to fit on is both a volume problem and a boundary problem, and it fails the parity test
   ([`04`](04-access-parity.md)).
5. **Evaluate on held-out cases from the user's own data**, and report the agreement honestly against a
   trivial baseline - including where it is weak.

What you end up with is not their system. It is your function, fitted to this data, which is what the product
actually wanted. `../examples/case-01-closed-personalization-behavior.md` walks the hardest version of this
case, including the route that dies at the gate.

Sketch of the honest shape - a strategy object plus an offline check, in three stacks, none of them calling
the closed system:

```python
# Python: features from our own records, evaluated on held-out outcomes we already have.
rows = [row(subject, features_for(subject, history, catalog)) for subject in subjects(history)]
model = fit(rows)
print(agreement_at(model, candidates=catalog.open(), held_out=history.next_chosen()))
```

```ts
// TypeScript: generate, score, then re-rank under the constraints our own product states.
const candidates = shortlist(ctx, catalog).slice(0, 200);
const chosen = applyConstraints(score(model, candidates), { perGroup: 3, preferFresh: 0.15 });
```

```csharp
// C#: the pattern is a strategy, so it stays swappable and provably better than the trivial baseline.
IReadOnlyList<Item> ranked = pipeline.Rank(ctx, candidates);
Debug.Assert(metrics.AgreementAt(10, ranked, heldOut) > metrics.AgreementAt(10, byRecency, heldOut));
```

## Reproducing a closed format or protocol

Same discipline, smaller scope: identify the envelope (magic bytes, header layout, framing), the field
semantics, the version variants, and the failure modes. Build a reader that accepts what real files
*actually* contain, keep a golden corpus of files the user legitimately has, and record unknown fields
rather than guessing them. When the format is documented but the writer is gone, the docs beat the
archaeology - check for a spec, an OSS writer, or a standards draft before parsing bytes.

## Validation before you call it a capability

- **Held-out agreement**: does your version reproduce the *rule* on cases you did not study? Report the
  number, including where it is weak.
- **Edge parity**: cold start, empty context, unknown entity, extreme input - does your version behave
  sensibly, and do you know what the original would do?
- **No silent fabrication**: a derived value is labelled derived wherever a human might trust it as real.
- **Fragility noted**: if the rule was inferred rather than documented, say so in the record - it is the
  first thing to break when the observed system changes.
