---
name: summarize
description: "Use this skill whenever the user wants to shorten a piece of content without losing its meaning — summarize, condense, distill, recap, abridge, or extract the key points from an article, report, transcript, thread, email chain, or document, including requests for a TL;DR, executive summary, abstract, digest, or brief. Trigger even on a bare \"summarize this,\" \"shorten this,\" or \"give me the key points,\" with no further instruction. Also trigger when the user asks for the shortest, tightest, or most extreme possible version of something. Do not use for line-level copyediting or proofreading that keeps the original length — see process-business-writing for that."
license: Apache-2.0
---

# Document Summarization

Reduce a longer source into a shorter one **without losing the meaning the reader needs to walk away with.** This is not word-deletion — it is re-deriving the point from a position of having understood the whole, then rendering it in as few words as the requested mode allows.

> Compression asks: "which words can I remove?"
> Summarization asks: "what must the reader walk away knowing, and what's the shortest true way to say it?"

## What this skill includes

- Reading a source fully enough to identify its actual point (not just its topic) before writing anything.
- Deciding what content survives, in **two modes**: Normal (default) and Extreme.
- Choosing how to compress — rewriting in your own words vs. lifting exact wording — without drifting from what the source said.
- Structuring the result bottom-line-first, at a length calibrated to the reader.
- Verifying the summary against the source before delivery (faithfulness check).
- Delivering the result to the right place (file vs. chat) and reporting the size reduction.

## What this skill excludes

- **Prose polish that doesn't change length or content** — active voice, word choice, sentence rhythm. Use `process-business-writing` (a sibling skill, if present) for that; apply it *after* this skill's content decisions are locked.
- **Editing the user's own draft to improve it** at roughly the same length. That's editing, not summarizing — see `process-business-writing/references/06-editing.md`.
- **Translation, formatting conversion, or OCR.** Summarize the content, not the container — use `pdf`, `docx`, `pptx`, `xlsx`, or `file-reading` skills to get the content out first, then apply this skill.
- **Persuasive rewriting to a requested slant** ("make this sound better/worse"). Flag that this shifts the task toward persuasive writing — see references/05-faithfulness-check.md for where the line sits.

## The two modes

| | Normal (default) | Extreme |
|---|---|---|
| What survives | Must-keep + should-keep content | Must-keep content only |
| Form | Prose or light structure (paragraphs, a few bullets) | Flat list: term/label + one-line description |
| Repetition | Minor restatement for flow is fine | Zero — each point appears exactly once |
| Triggered by | Default; used unless Extreme is clearly requested | Explicit ask: "as short as possible," "bare minimum," "just the terms," "extreme summary" |

Full rules for both modes: **references/02-selection.md**.

## Workflow

1. Read the whole source; find its point, not just its topic. → **references/01-reading-for-the-point.md**
2. Sort content into must-keep / should-keep / can-cut, per the active mode. → **references/02-selection.md**
3. Compress by rewriting the idea, not shortening each sentence. → **references/03-compression-method.md**
4. Structure bottom-line-first, at a deliberate length. → **references/04-structure-and-length.md**
5. Check every claim against the source before delivering. → **references/05-faithfulness-check.md**
6. Deliver to the right place and report the size reduction. → **references/06-output-and-reporting.md**

Apply `process-business-writing` (if available) as a final pass once content is locked.

## Reference files

| File | Covers |
|---|---|
| `references/01-reading-for-the-point.md` | Reading the source; topic vs. point; load-bearing content |
| `references/02-selection.md` | Must-keep / should-keep / can-cut; Normal vs. Extreme mode rules |
| `references/03-compression-method.md` | Rewriting vs. lifting; compressing ideas, not sentences |
| `references/04-structure-and-length.md` | Bottom-line-first structure; length calibration table |
| `references/05-faithfulness-check.md` | Verifying the summary against the source before delivery |
| `references/06-output-and-reporting.md` | Where the summary goes (file vs. chat); size-reduction reporting |

## Templates

| File | Use for |
|---|---|
| `templates/tldr.md` | One- to two-sentence TL;DR |
| `templates/executive-summary.md` | Default register when no form is specified |
| `templates/structured-digest.md` | Longer or multi-topic sources |
| `templates/meeting-recap.md` | Transcripts, calls, long threads |
| `templates/extreme-digest.md` | Extreme mode output |

## Examples

`examples/normal-vs-extreme.md` — the same source summarized in both modes, side by side.

## Scripts

`scripts/size_report.py` — before/after line, word, and character counts plus % reduction; pure standard library. Fallback bash/PowerShell commands in `scripts/size_report_fallback.md` if Python is unavailable. Always run one of these for file-based summarization tasks — see references/06-output-and-reporting.md.

## Non-negotiables (apply regardless of mode)

- Never invent a fact, number, name, or date not in the source.
- Never silently drop a hedge, caveat, or piece of dissent that changes what the source is claiming.
- Never lift more than one direct quote per source, or any quote of 15+ words (standing copyright rule).
- A summary must be self-contained — readable and correctly understood with no access to the source.
