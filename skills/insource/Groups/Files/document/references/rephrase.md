# Job E — Rephrase text

The procedure for "rephrase this", "word these sentences better", "fix the awkward phrasing" - improve the
saying, never the said. This is **not** a paraphrase-tool job: those merge sentences, restructure arguments
and vary length freely. Rephrasing works strictly **inside each sentence**.

Works in any source language; the output stays in the source's language unless the user asks otherwise
(this is not translation - translation is a different request).

## Procedure

1. **Infer the source first**, before touching it: its language, its tone, its register, its characteristic
   phrasing - the words and rhythms that make this author recognizably themselves. Those are parameters of
   the job, not obstacles to smooth over.
2. **Work sentence by sentence.** For the current sentence only, improve: grammar, naturalness, syntax,
   word choice, flow, concision. Reorder clauses inside the sentence when useful. Never move information
   between sentences - sentence 3's content stays in sentence 3.
3. **Do not add fluff.** No new claims, explanations, examples, transitions, headings, or context. An
   improvement that adds information is a violation, not a style.
4. **Anti-AI Gate (when audience is external or human-facing).** Check if the prose will be read by
   someone other than the author, or if the user asked to de-AI/humanize the text. Apply the rules from
   `references/anti-ai-gate.md`:
   - Strip em-dashes (`—`) completely (replace with period, comma, colon, or parentheses).
   - Strip AI filler, negation-pivot antithesis ("not just X, but Y"), and stock buzzwords (*delve, leverage, seamless, robust*).
   - Eliminate mid-sentence bolding (`**critically**`, `**the key insight**`).
   - Ground abstract vagueness into plain verbs and concrete terms while protecting genuine factual caveats.
5. **Final pass - the skeleton check.** Compare the result against the source's structural skeleton:
   paragraph and line grouping, heading set, list membership, sentence count and boundaries, sentence
   order, each sentence's claim and its weight. Anything drifted that the sentence-level work did not
   require - a merged pair, a softened claim, a re-ordered argument - is **restored toward the source**,
   even at the cost of a less polished line.

## Preserve (unless the user explicitly requests otherwise)

- paragraphs, headings, list items, line groupings, and their order;
- sentence count, sentence boundaries, and sentence order;
- each sentence's claim, purpose, emphasis, and **degree of certainty** ("may" stays "may"; a hedge is
  content);
- tone, formality, perspective, and the author's recognizable voice;
- established terminology, vocabulary, and characteristic phrases when they are already natural;
- factual content and the approximate level of detail.

## Forbidden

- merging or splitting sentences;
- reorganizing the argument;
- standardizing the voice into generic polished prose;
- removing intentional informality merely because another style would read smoother - the informality is
  the author's choice, not an error;
- anything that job D does: shortening, selecting what survives, restructuring into a digest. "Rephrase"
  never means "make it smaller".

## Output

Return **only the rephrased text** - no preface, no commentary, no change log, no alternative versions -
unless the user asks for one of those. The deliverable replaces the source; everything else is noise the
user did not request.

## If the user's request exceeds this job

Say so in one line and hand it off, rather than quietly becoming a different job:

| What they actually asked | What it is | Where it goes |
|---|---|---|
| "rephrase and make it shorter" | rephrase + summarize | this job, then job D (`references/summarize.md`) |
| "rephrase it formally" (register change requested) | rephrase with an explicit override of the tone-preservation rule | this job, register per user |
| "remove the AI-sounding bits" / "de-AI this" | rephrase with anti-AI gate | this job (`references/rephrase.md` + `references/anti-ai-gate.md`) |
| "reorganize these paragraphs" | not rephrasing at all | job B territory (`references/reorganize.md`) |
| "translate this" | translation - no job needed, agents do it natively | SKILL.md §"Translation is not a job": skeleton preserved, code/paths/numbers verbatim, glossary terms consistent |
