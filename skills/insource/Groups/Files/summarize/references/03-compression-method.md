# Compression method: how to shrink, not just cut

Selection decides *what* survives (02-selection.md); this decides *how* it's rendered in fewer words.

## Abstractive by default, verified after

- **Extractive** (lifting existing sentences) is faithful but often disjointed — sentences written to sit inside a longer piece read oddly once stitched to other lifted sentences.
- **Abstractive** (rewriting in your own words) is coherent and compresses further, but risks drifting from what the source actually said.

Default: **rewrite in your own words, then run the faithfulness check** (05-faithfulness-check.md). Pure lifted-sentence collage is an anti-pattern, not a lightweight version of this skill.

## When to lift instead of rewrite

- The **exact wording is the point** — a legal commitment, a quote whose phrasing is the news, a precise definition.
- **Numbers, dates, proper nouns, technical terms** — copy exactly, never paraphrase into an approximation.
- The source is **already too short** to compress without loss.

Copyright limits always apply regardless of summarization goals: quotations under 15 words, at most one direct quote per source, no reproduction of lyrics/poems even in part.

## Compress the idea, not the sentence

The weak version of abstractive summarization shortens each sentence a little. The strong version collapses several source sentences into one, because they were all serving one idea.

> Source (3 sentences): considered three vendors; A cheapest but weak support; B best support but priciest; picked C for balance of price/support and integration with existing systems.
>
> Weak: still three shortened sentences, same order, same structure.
>
> Strong (one sentence): "The team chose Vendor C over cheaper or better-supported alternatives because it integrated with the existing system without custom work."

The strong version surfaces what actually mattered (the integration point) rather than mechanically shortening in original order.

## Techniques

- **Merge parallel points sharing one structure** — but only if the source itself intends the link; don't manufacture causation.
- **Replace description with its conclusion** when the build-up isn't load-bearing.
- **Generalize a list** when the reader needs "there were delays," not which specific ones.
- **Use one strong verb instead of a clause** ("canceled" instead of "made the decision to cancel").

## Guard against meaning drift during compression

- **Dropped hedges** — "preliminary data suggest X" compressed to "X" changes epistemic status, not just length.
- **Dropped scope** — "in the three markets studied" dropped turns a bounded claim into an apparently universal one.
- **Collapsed distinctions** — "users who upgraded" and "all users" are different populations.
- **Invented causation** — "X happened, and separately Y happened" is not "X caused Y."

## In Extreme mode

Compression goes further: a whole paragraph becomes a term + one-line description, not a shorter paragraph. See 02-selection.md's Extreme mode section and templates/extreme-digest.md. The faithfulness constraints above still apply in full — extreme brevity is not license to drop a hedge or invent a connection.

## Quality checks

- [ ] Written in your own words by default; lifting reserved for the cases above.
- [ ] No sentence merely shortens a source sentence when several source sentences could collapse into one idea.
- [ ] Numbers, names, dates copied exactly.
- [ ] Hedges, scope, and causal precision from the source survive compression.
- [ ] Any direct quotation respects the copyright limits.
