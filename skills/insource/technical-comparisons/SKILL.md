---
name: technical-comparisons
description: Write professional, well-reasoned comparisons between two or more technologies, tools, libraries, frameworks, products, or services of any kind (programming/frontend tooling, databases, note-taking apps, cloud providers, hardware, SaaS products, etc.). Use this skill any time the user asks to compare, evaluate trade-offs between, or choose between named options — even if they just say "which is better" or "help me decide between X and Y." Enforces real differentiators only (not just what each side's own marketing highlights), "why it matters" reasoning for every claim, current/verified information via search, careful grading of benchmark/performance claims, and a neutral, use-case-driven recommendation instead of a false absolute winner.
---

# Technical Comparisons

A skill for writing comparisons that engineers actually trust — the kind that gets referenced, not the kind that gets skimmed and closed. The core failure mode this skill exists to prevent: listing a feature as an "advantage" of A when B can achieve the same outcome a different way, and listing features without ever saying why they matter to the reader.

## Before writing anything

1. **Identify the real audience and their actual decision.** Not "compare X and Y" in the abstract — find out (from context, or by asking one question) what the person is actually deciding: a new project? migrating an existing one? evaluating for a team? This determines what counts as relevant.
2. **Research each side independently, not just from its own marketing.** Do at least one search per option that is NOT the vendor's own site: third-party blog posts, GitHub issues/discussions, Reddit/Hacker News threads, "X vs Y" posts written by unaffiliated developers, changelogs. The official site tells you what the vendor *wants* highlighted; independent sources tell you what actually bit real users, and surface genuine advantages the vendor doesn't bother to market (e.g. a smaller project's real strength is often invisible on its own homepage because it's competing against a bigger player's polish). Pull the full advantage list for **each** side this way before narrowing anything.
3. **Search for current information. Do not rely on memory for versions, benchmarks, or ecosystem claims.** Tech comparisons go stale fast — version numbers, performance benchmarks, and "market leader" claims change. Run web searches for each tool's current version/release notes and any specific performance or adoption claims before writing.
4. **List candidate differences before writing prose.** Draft a raw list of every difference you can find between the options, from both official and independent sources. You'll filter this list in the next two steps — don't filter while drafting, it causes premature narrowing.

## The differentiator test (apply to every single claim)

Before writing "X is an advantage of A," ask: **can B achieve the same outcome, even via a different mechanism?**

- If yes → this is NOT a real differentiator. Either cut it, or reframe it as "both support this, via different approaches" (only worth mentioning if the *mechanism* difference itself matters — e.g. build-time vs runtime, config vs code).
- If no → this is a real differentiator. State it, and then answer "so what?" — a feature name alone is not an advantage.

Common false-differentiator traps:
- Syntactic sugar / composition helpers that both tools support under different names or syntax
- Features that exist in both but one tool's marketing highlights it more
- Anything true of a specific plugin/preset/library/extension in that tool's ecosystem, presented as if it were true of the core tool
- Old benchmarks or version-specific limitations that have since been fixed upstream

See `examples/differentiator-test.md` for short worked examples of applying this test.

## The "Trust-Me-Bro Benchmark" filter

A "trust-me-bro benchmark" is a performance/superiority claim where the methodology is undisclosed, the comparison is against an unfair baseline (old version, misconfigured competitor, cherry-picked workload), or it simply cannot be independently reproduced — yet gets repeated as settled fact. This is extremely common in vendor blog posts ("100x faster," "50% smaller") because the vendor controls both the test and the write-up.

This does **not** mean ignore benchmarks. It means grade them before using them:

- **Green light — usable as a primary point:** methodology is disclosed (what was measured, what versions, what hardware/workload), and/or it's been independently reproduced or cited by a neutral third party, and/or multiple independent sources converge on roughly the same conclusion.
- **Yellow light — usable, but only as a side note with a caveat:** single-source, vendor-published, methodology partly disclosed. State the number *and* attribute it plainly ("Vendor X's own benchmark claims...") so the reader can weight it themselves. Don't present it with the same confidence as a green-light claim.
- **Red light — do not use, or explicitly debunk it:** undisclosed methodology, compares against a clearly outdated/unfair baseline, or is a bare marketing superlative with no numbers behind it ("blazing fast," "industry-leading"). If a claim like this is widely repeated (it often gets copied across dozens of comparison articles), it's worth actively flagging as unverified rather than silently omitting it — the reader has probably seen it elsewhere and will trust your comparison more for addressing it head-on.

**Weighting rule:** structure the comparison so the reader can tell primary points (green-light, structural, verifiable — e.g. "ships a Vite plugin vs. doesn't," "requires a build step vs. doesn't") apart from side points (yellow-light performance claims, minor ecosystem counts, single-source anecdotes). Lead each section with the primary point; fold side points in afterward, clearly framed as secondary and attributed to their source. Never let an unverifiable performance claim carry the same rhetorical weight as a verifiable structural fact.

## Every claim needs a "why it matters," not just a feature name

See `examples/why-it-matters.md` for a short before/after of a claim without reasoning vs. with it.

For every bullet or row in the comparison, silently check: *if I deleted the "why it matters" clause, would this line still tell the reader something they can act on?* If not, add the reasoning or cut the line.

## Structure

Default to **point-by-point (alternating) structure** for technical comparisons — organize by criterion (ecosystem, performance, flexibility, learning curve, etc.), discussing both/all options within each criterion. This is almost always better than block structure (all of A, then all of B) for technical audiences, because it puts the actual point of comparison directly next to itself instead of making the reader hold A's paragraph in their head while reading B's.

Recommended skeleton:
1. One-paragraph framing: what problem both/all options solve, and why someone would be choosing between them right now
2. 4-8 criteria sections, each: the difference → why it matters → (if relevant) any nuance or caveat
3. A short "for your case" or "pick A if / pick B if" section — concrete enough to act on
4. Skip padding: no filler intro history lessons, no restating the table in prose afterward, no "in conclusion, both are great tools"

## Stay neutral — recommend by use case, not by declaring an absolute winner

Avoid crowning one option "the winner" outright. Instead:
- State honest trade-offs for both sides, including real weaknesses of the option you'd lean toward
- Convert the decision into "pick A if [concrete situation], pick B if [concrete situation]"
- If the user's own context is known (their stack, their constraints), give a direct recommendation for *them* specifically, separate from the general-case answer

## Calibrate depth to the audience

If you don't know the reader's experience level from context, write for a competent practitioner who doesn't already know both tools deeply: define unfamiliar terms briefly on first use, but don't over-explain basics. Ask, rather than guess, only if the comparison would come out substantially different for a beginner vs an expert audience (e.g. "is this for someone new to CSS tooling, or an experienced dev deciding for a team?").

## Verification and honesty checklist (run before finalizing)

- [ ] Each side's advantage list was pulled from independent sources too, not just each vendor's own site
- [ ] Every "advantage" passed the differentiator test above
- [ ] Every claim has a stated reason it matters in practice
- [ ] Every benchmark/performance claim is graded (green/yellow/red per the Trust-Me-Bro filter) and presented with matching confidence — no undisclosed-methodology claim stated as flat fact
- [ ] Primary (structural, verifiable) points are visually/rhetorically distinguished from side points (single-source claims, minor stats)
- [ ] Version numbers, benchmarks, and adoption stats are from a current search, not memory — and dated if they might go stale
- [ ] Any benchmark older than ~1 year, or compared against an outdated baseline, is explicitly flagged as historical/unfair if included at all
- [ ] No absolute "X wins" claim without a stated use case attached
- [ ] Length is proportional to genuine differences — a comparison with 4 real differences should not be padded into 12 rows
- [ ] If sources were used, they're cited briefly (name + rough date), not presented as the model's own settled knowledge
