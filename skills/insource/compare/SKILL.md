---
name: compare
description: Write professional, well-reasoned comparisons between two or more things in any field — technologies, biological processes, historical events, medical treatments, business strategies, legal frameworks, scientific theories, consumer products, or any other named options. Use this skill any time the user asks to compare, evaluate trade-offs between, or choose/distinguish between named options — even if they just say "which is better," "what's the difference between X and Y," or "help me decide between X and Y." Enforces real differentiators only (not just what each side's own advocates highlight), "why it matters" reasoning for every claim, current/verified information via search when the domain calls for it, careful grading of quantitative or superiority claims, and a neutral, context-driven conclusion instead of a false absolute winner.
---

# Compare

A skill for writing comparisons people actually trust — the kind that gets referenced, not the kind that gets skimmed and closed. The core failure mode this skill exists to prevent: listing a trait as an "advantage" of A when B achieves the same outcome a different way, and listing traits without ever saying why they matter to the reader.

This skill is domain-agnostic. "Options" below can mean two frameworks, two cell-division processes, two historical treaties, two medications, two investment strategies, or two of anything else with distinguishable traits. Every instruction is written to apply regardless of field — substitute your own domain's vocabulary as you go rather than treating any example item (e.g. "benchmark," "vendor," "GitHub issue") as literal or mandatory. Where this file gives illustrative examples, they are marked as such and are not a closed list.

## Before writing anything

1. **Identify the real audience and their actual decision.** Not "compare X and Y" in the abstract — find out (from context, or by asking one question) what the person is actually deciding: choosing one for a project? understanding a concept for study? deciding between treatments? forming an opinion on a debate? This determines what counts as relevant.
2. **Research each side independently, not just from its own advocates.** For fields where claims can go stale or be one-sided (technology, medicine, current events, products, markets), do at least one search per option that is NOT the option's own promotional or primary source: independent analysis, practitioner or expert discussion, critical commentary, comparisons written by unaffiliated third parties. The primary or promotional source tells you what its subject *wants* highlighted; independent sources tell you what actually holds up under scrutiny, and surface genuine strengths that don't get marketed (e.g. a less prominent option's real strength is often invisible in its own framing because it's competing against a more prominent alternative's visibility). For fields that are settled and don't change (most classical science, historical fact, well-established academic concepts — e.g. mitosis vs meiosis), rely on accurate domain knowledge and search only to verify specifics you're unsure of. Pull the full list of distinguishing traits for **each** side this way before narrowing anything.
3. **Search for current information when the domain can go stale. Do not rely on memory for figures, claims, or standing that change over time.** Some domains move fast (technology versions, market data, medical guidance, current events); others are stable (biology fundamentals, historical fact, mathematics). Judge which kind of comparison this is, and search accordingly — don't skip verification for a fast-moving domain, and don't force unnecessary searches on a settled one.
4. **List candidate differences before writing prose.** Draft a raw list of every difference you can find between the options, from both primary and independent sources where relevant. You'll filter this list in the next two steps — don't filter while drafting, it causes premature narrowing.

## The differentiator test (apply to every single claim)

Before writing "X is an advantage of A," ask: **can B achieve the same outcome or reach the same state, even via a different mechanism?**

- If yes → this is NOT a real differentiator. Either cut it, or reframe it as "both do this, via different mechanisms" (only worth mentioning if the *mechanism* difference itself matters — e.g. one produces genetically identical results and the other introduces variation, one requires a prescription and the other doesn't, one runs at compile-time and the other at runtime).
- If no → this is a real differentiator. State it, and then answer "so what?" — a trait name alone is not an advantage.

Common false-differentiator traps:
- A capability both options have, just under a different name or through a different process
- Traits that are true of both but one side's framing or advocates emphasize more
- Anything true of a specific variant, sub-case, edition, or context, presented as if it were true of the general case
- Outdated claims or edge-case limitations that no longer hold (a fixed bug, a superseded study, a since-revised guideline)

See `examples/differentiator-test.md` for short worked examples of applying this test across different fields.

## The "Trust-Me-Bro Claim" filter

A "trust-me-bro claim" is a superiority or magnitude claim — performance, effectiveness, significance, size, impact — where the methodology or basis is undisclosed, the comparison is against a weak or unfair baseline (an old version, an atypical case, a cherry-picked scenario), or it simply can't be independently checked — yet gets repeated as settled fact. This is common wherever one side has an interest in being seen favorably (marketing, advocacy, self-report) because that side controls both the claim and its framing.

This does **not** mean ignore such claims. It means grade them before using them:

- **Green light — usable as a primary point:** the basis is disclosed (what was measured or observed, under what conditions), and/or it's been independently corroborated or is established consensus, and/or multiple independent sources converge on roughly the same conclusion.
- **Yellow light — usable, but only as a side note with a caveat:** single-source, self-reported, or partially disclosed. State the claim *and* attribute it plainly ("Company X's own figures suggest...", "one small study found...") so the reader can weight it themselves. Don't present it with the same confidence as a green-light claim.
- **Red light — do not use, or explicitly debunk it:** undisclosed basis, compared against a clearly weak or unfair baseline, or a bare superlative with nothing behind it ("industry-leading," "clinically proven" with no citation). If a claim like this is widely repeated, it's worth actively flagging as unverified rather than silently omitting it — the reader has probably seen it elsewhere and will trust the comparison more for addressing it head-on.

**Weighting rule:** structure the comparison so the reader can tell primary points (green-light, structural, verifiable — e.g. "requires X vs doesn't," "produces N vs producing M") apart from side points (yellow-light claims, minor or single-source figures). Lead each section with the primary point; fold side points in afterward, clearly framed as secondary and attributed to their source. Never let an unverifiable claim carry the same rhetorical weight as a verifiable structural fact.

## Every claim needs a "why it matters," not just a trait name

See `examples/why-it-matters.md` for a short before/after of a claim without reasoning vs. with it.

For every bullet or row in the comparison, silently check: *if I deleted the "why it matters" clause, would this line still tell the reader something they can act on or understand?* If not, add the reasoning or cut the line.

## Structure

Default to **point-by-point (alternating) structure** — organize by criterion, discussing both/all options within each criterion. This is almost always better than block structure (everything about A, then everything about B) because it puts the actual point of comparison directly next to itself instead of making the reader hold A's section in their head while reading B's.

Recommended skeleton:
1. One-paragraph framing: what the options are, what question or need they both relate to, and why someone would be comparing them right now
2. A handful of criteria sections (illustrative range: 4–8; fewer for a simple comparison, more for a genuinely complex one), each: the difference → why it matters → (if relevant) any nuance or caveat. Example criteria families to draw from depending on domain — not a checklist to fill: mechanism/process, outcome/result, cost or resource demands, timing or lifecycle, context of use, risk or failure modes, prevalence or standing.
3. A short "for your case" or "X fits if / Y fits if" section — concrete enough to act on. For a purely academic or descriptive comparison (e.g. two biological processes) this can instead be a short "how to tell them apart" or "why the distinction matters" close, since there's no decision to make.
4. Skip padding: no filler intro history lessons, no restating the table in prose afterward, no "in conclusion, both are important."

## Stay neutral — conclude by context, not by declaring an absolute winner

Avoid crowning one option "the winner" outright, except where the comparison is genuinely about a factual asymmetry with a real answer (e.g. one process is haploid-producing and the other isn't — that's not false balance, it's a fact). Where the comparison is actually a judgment call:
- State honest trade-offs for both sides, including real weaknesses of the option you'd lean toward
- Convert the decision into "A fits if [concrete situation], B fits if [concrete situation]"
- If the user's own context is known (their constraints, goals, or situation), give a direct recommendation for *them* specifically, separate from the general-case answer

## Calibrate depth to the audience

If you don't know the reader's background from context, write for a curious, competent non-specialist: define unfamiliar terms briefly on first use, but don't over-explain basics the question implies they already know. Ask, rather than guess, only if the comparison would come out substantially different for a beginner vs an expert audience (e.g. "is this for someone studying for an exam, or a clinician making a treatment choice?").

## Verification and honesty checklist (run before finalizing)

- [ ] Each side's trait list was pulled from independent or authoritative sources too, not just one side's own framing
- [ ] Every "advantage" passed the differentiator test above
- [ ] Every claim has a stated reason it matters in practice or understanding
- [ ] Every superiority/magnitude claim is graded (green/yellow/red per the Trust-Me-Bro filter) and presented with matching confidence — no undisclosed-basis claim stated as flat fact
- [ ] Primary (structural, verifiable) points are visually/rhetorically distinguished from side points (single-source or minor claims)
- [ ] Figures, standings, or claims that can go stale are from a current search where the domain warrants it, not memory alone — and dated if they might go stale
- [ ] Any outdated or superseded claim is explicitly flagged as historical if included at all
- [ ] No absolute "X wins" claim without either a stated use case attached, or a genuine factual asymmetry backing it
- [ ] Length is proportional to genuine differences — a comparison with 4 real differences should not be padded into 12 rows
- [ ] If sources were used, they're cited briefly (name + rough date), not presented as the model's own settled knowledge