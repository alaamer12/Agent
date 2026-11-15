# The destination

The destination is not a dump of notes, and it is not a form. It is a knowledge base a fresh agent can open, navigate, and trust without ever seeing the mining run.

Everything the source contributed is either represented or recorded as deliberately excluded. Nothing is silently missing.

## Layout

```
YYY/
  INDEX.md                    entry point: what is here and where to look
  README.md                   what was smelted, from where, when; trust and scope
  knowledge/                  one or more files, named for what they hold
  provenance/
    fold/<relative-path>.md   the knowledge file produced for each source folder
    sources.md                every source file, its role, and its disposition
    merges.md                 what was merged, varied, contradicted, or corrected
    links.md                  every reference URL in the corpus, checked, with status and handling
    yield.md                  per-file smelted share, sorted top yield to bottom
```

The shape inside `knowledge/` is the writer's decision. It can be one file or many; by topic, by kind of knowledge, by product, or as one coherent essay. The material decides. What is fixed is only this: each file owns a distinct body of knowledge, files link to each other, and `INDEX.md` routes to all of them.

Do not create a file to satisfy a category. Do not create empty files. If a domain has only one good piece of knowledge, it can live inside a broader file.

## One base, one or more files

- **Each file owns a distinct body of knowledge.** If a file stops being navigable, split it along a real seam in the material — not at an arbitrary length.
- **Names are global.** A piece of knowledge is named once, and every other file points at it by that name plus its file. Two files never carry the same piece.
- **Files link both ways.** The top of a file says what it builds on; the end says what builds on it. A reader who enters anywhere can reach the rest.
- **No orphans.** Every file is reachable from `INDEX.md` and from at least one sibling. A file nothing links to is either missing a link or does not belong.
- **One file is legitimate** when the corpus is small. Split for navigation, never for appearance.

## `README.md`

Answer these in order, briefly and plainly:

1. **What this is** — the corpus that was smelted, the source path, and the date.
2. **What it covers** — the domains and questions the corpus actually addresses.
3. **What it does not cover** — unreachable sources, pre-plan areas, unmeasured fields, unresolved contradictions.
4. **How to trust it** — how evidence is shown, what stated versus inferred means, and how confidence was assigned.
5. **How it was made** — one paragraph: file-by-file fold into one knowledge file per folder, then a single global reconciliation across all folders, with the evidence chain preserved, every reference URL checked, and a per-file yield reported.

No marketing. No claims the corpus does not support.

## `INDEX.md`

This is what a consuming agent loads first. It routes; it does not teach. It should be readable in a comfortable context window.

It must make these findable:

- **How to use the base** — load the index, choose a file or route, open only what the question needs. Never load the whole base to answer one question.
- **The file map** — every knowledge file, what it holds, and what it depends on.
- **Topic routes** — subject → the files and pieces that cover it. This is how an agent finds knowledge by subject rather than by file.
- **Terms** — the corpus's own vocabulary, including terms that mean something narrower here than they do elsewhere.
- **Contradictions** — every unresolved disagreement, one line each, pointing at where both sides are written.
- **Gaps** — what the corpus does not establish, one line each.

The index is generated from what is actually written, not from memory. If it names a piece, that piece exists; if a piece exists, the index can reach it.

## `provenance/sources.md`

One line per file in the source run:

```
experience/05-atlas.md      read in full    contributed the extension-seam and authorization accounts
distillation/long-form.md   read in full    derived; cross-checked twelve claims, added none
sources/atlas/              skipped         clone payload; opened twice to verify quotes
sources/cache/*.json        skipped         derived tree dumps; no knowledge
witness/agent-fetches.tsv   read in full    confirmed 44 of 46 fetch claims
```

Each line says the path, what happened (`read in full`, `read in part`, `skipped`), and what it contributed or why it was skipped. A file that contributed nothing still gets a line saying it confirmed, repeated, or was empty.

This file is also the resume point. On re-entry, the first path not marked read is where the fold continues.

## `provenance/merges.md`

Append-only, written while the fold runs. One short block per change that affects more than one piece or corrects an earlier reading:

```
MERGE — "Tenant isolation enforced in the database" ← Atlas's account of extension isolation
Source: experience/05-atlas.md
Why: same subject, same scope, equivalent assertion; wording differed by example.
Effect: evidence combined; independent count 1 → 2.

CORRECTION — "Beacon's paths are stable"
Source: witness/parent-verification.tsv
Why: the branch was stale; the live default had moved.
Effect: the old reading stays visible, marked corrected; the current account carries the new evidence.
```

Every merge, variant, contradiction, and correction appears here. The log is what makes "nothing was lost" checkable rather than asserted.

## `provenance/links.md`

One row per unique URL the corpus references, filled from the sweep, statuses set by the verify pass:

```
https://…/pricing-api          experience/03.md, distillation/biblio.md   alive (200)      2026-11-14   —
https://…/spec-v2              experience/05.md                           redirect→v3      2026-11-14   cited both
https://…/blog-post            witness/notes.md                           dead             2026-11-14   archive copy found; claim cites live+archive
https://…/internal-metrics     experience/07.md                           dead             2026-11-14   no recovery; confidence lowered, gap written
```

Rules: no row stays `unchecked` at delivery; dead-with-recovery keeps the claim and cites both; dead-without-recovery downgrades the claim's provenance at the citation point and appears in the gaps. The pointer is never quietly deleted — the dead link is knowledge (an unreachable citation is a fact about the corpus).

## `provenance/yield.md`

The accounting of how much was smelted, sorted highest yield to lowest:

```
experience/05-atlas.md        80%  (10 units: 7 new · 2 merged · 1 corrected · noise excluded)
experience/09-cli.md          62%  (8 units: 5 new · 3 merged; low: much duplicated 05)
distillation/long-form.md     35%  (derived; confirmed 12 claims, added 2)
experience/02-nav.md           0%  (navigation boilerplate — recorded, contributed nothing)
```

Each row: file, smelted share (meaning-share: substantive units represented ÷ substantive units), the tally behind it, and the reason when the number is low. Header line: total files read, corpus-weighted yield. This is what lets the next agent judge whether a gap is "the corpus didn't know it" or "smelt missed it" — the fold tallies, not memory, are the source of the percentages.

## `provenance/fold/<relative-path>.md`

The knowledge file for each source folder, including every nested folder, named after the folder's relative path (`experience__atlas.md`, `distillation__themes__authorization.md`). Each is kept exactly as its fold left it. Entries were corrected file by file as later sources arrived, but the file was not re-read or compressed at the folder boundary; that happened once, globally, after every folder was closed.

A parent folder's file contains only that folder's own files. It does not absorb its children; the child files stand on their own and meet the rest only in the global pass.

Do not edit these after the global pass. They are history. The delivered knowledge lives in `knowledge/`.

## Writing the knowledge files

No template. Each file opens with whatever the reader needs to orient: what it holds, its scope, what it depends on, and what depends on it. After that, the writer chooses the shape.

Inside a file:

- Group related knowledge so a reader can follow the material's own logic.
- Keep pieces separable enough to be linked and deduplicated, but do not chop a single mechanism into fragments to look atomic.
- Put evidence next to the claim it supports, not in a distant appendix.
- Mark corrections where they happened, so the reader sees what changed.
- End with the files and pieces this one connects to, if the opening did not already say.

Professional standards, once more: lead with the claim, carry the mechanism and the cost, quote exactly, separate observation from inference, use measured numbers, and say plainly what the corpus does not establish.

## Quality bar

Before calling the destination complete:

- **Every claim is traceable.** A reader can find the source, the location, and the exact words without trusting the writer.
- **Every quote is verbatim** at the cited location. Spot-check across files.
- **Every source file has a disposition** in `sources.md`, and a smelted yield with its tally in `provenance/yield.md` — sorted, low yields explained, total stated.
- **Every reference URL is checked.** `provenance/links.md` has a status for every unique URL — no `unchecked` rows, no sampling; dead links are recovered-and-cited or downgraded-and-gapped, never silently dropped.
- **No knowledge is duplicated.** Same subject, scope, and assertion appear once; variants are linked; contradictions are shown side by side.
- **Lineage is honest.** Derived evidence is marked, and no confidence rests on it alone.
- **The file graph closes.** Every file is linked from `INDEX.md` and from at least one sibling; every cross-file reference resolves.
- **Gaps are explicit**, including the reasons the run itself gave.
- **The cold read passes.** `INDEX.md` plus the knowledge files answer the corpus's own questions without opening the source.
- **The destination is portable.** Paths are relative to the source root; nothing depends on the machine that built it.
- **The writing is clear.** A reader does not need the source to understand what the knowledge file says.
