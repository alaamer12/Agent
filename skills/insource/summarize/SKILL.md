---
name: summarize
description: "Use this skill whenever the user wants to shorten content without losing its meaning — summarize, condense, distill, recap, abridge, or extract key points from an article, report, transcript, thread, email chain, conversation, or document, including TL;DR, executive summary, abstract, digest, or brief requests. Trigger even on a bare \"summarize this\" with no further instruction, and when the user wants the shortest/most extreme version. Also trigger for conversation/Q&A summarization with role-specific instructions (\"keep my questions, summarize the agent's answers\") and for requests specifying a custom output structure (\"put questions on top under headers, answers below\") — this skill decides whether the request preserves the source's shape or needs a new one. Not for line-level copyediting/proofreading at the same length — see process-business-writing."
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

## Reserved structure vs. custom structure

Before applying mode or selection, check whether the request also specifies how the *output* should be arranged — this matters most for conversations, Q&A threads, and other multi-turn sources with distinct roles (user/agent, interviewer/interviewee, etc.).

- **Reserved structure (default).** The request describes a *content operation* — what to compress, what to keep verbatim, what to focus on — with no different arrangement implied. The source's own shape carries over unchanged (e.g., a conversation stays turn-by-turn, in order). Example: *"Summarize this, keeping my questions and just summarizing the agent's answers."*
- **Custom structure (explicit).** The request describes a *layout* — a new grouping, ordering, or set of sections/headers that doesn't mirror the source's shape. Build directly to that spec. Example: *"Write all my questions on top, tagged with header sections, then the agent's answers below."*

Full rules, the content-vs-layout test, role-aware compression, and how to keep questions/answers traceable once separated: **references/07-conversation-and-custom-structure.md**.

## Workflow

1. Read the whole source; find its point, not just its topic. → **references/01-reading-for-the-point.md**
2. Decide reserved vs. custom structure, especially for conversational/multi-role sources. → **references/07-conversation-and-custom-structure.md**
3. Sort content into must-keep / should-keep / can-cut, per the active mode (per role, if structure is reserved and roles are treated differently). → **references/02-selection.md**
4. Compress by rewriting the idea, not shortening each sentence — except a role the user asked to preserve, which is lifted, not rewritten. → **references/03-compression-method.md**
5. Structure bottom-line-first at a deliberate length (reserved structure) or to the requested layout (custom structure). → **references/04-structure-and-length.md**
6. Check every claim against the source before delivering. → **references/05-faithfulness-check.md**
7. Deliver to the right place and report the size reduction. → **references/06-output-and-reporting.md**

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
| `references/07-conversation-and-custom-structure.md` | Conversations/roles; reserved vs. custom output structure; keeping split content traceable |

## Templates

| File | Use for |
|---|---|
| `templates/tldr.md` | One- to two-sentence TL;DR |
| `templates/executive-summary.md` | Default register when no form is specified |
| `templates/structured-digest.md` | Longer or multi-topic sources |
| `templates/meeting-recap.md` | Transcripts, calls, long threads |
| `templates/extreme-digest.md` | Extreme mode output |
| `templates/conversation-role-preserving.md` | Reserved-structure conversation summaries (e.g., keep questions, summarize answers) |

For a custom structure the user specifies directly (a new layout, not one of the above), build to their spec rather than forcing it into one of these templates — see references/07-conversation-and-custom-structure.md.

## Examples

- `examples/normal-vs-extreme.md` — the same source summarized in both modes, side by side.
- `examples/reserved-vs-custom-structure.md` — the same conversation summarized once with structure reserved and once with a user-specified custom layout, side by side.

## Scripts

`scripts/size_report.py` — before/after line, word, and character counts plus % reduction; pure standard library. Fallback bash/PowerShell commands in `scripts/size_report_fallback.md` if Python is unavailable. Always run one of these for file-based summarization tasks — see references/06-output-and-reporting.md.

## Non-negotiables (apply regardless of mode)

- Never invent a fact, number, name, or date not in the source.
- Never silently drop a hedge, caveat, or piece of dissent that changes what the source is claiming.
- Never lift more than one direct quote per source, or any quote of 15+ words (standing copyright rule).
- A summary must be self-contained — readable and correctly understood with no access to the source.
