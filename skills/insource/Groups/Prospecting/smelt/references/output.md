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
  .work/                      this run's own working material (see "Two zones")
```

The shape inside `knowledge/` is the writer's decision. It can be one file or many; by topic, by kind of knowledge, by product, or as one coherent essay. The material decides. What is fixed is only this: each file owns a distinct body of knowledge, files link to each other, and `INDEX.md` routes to all of them.

Do not create a file to satisfy a category. Do not create empty files. If a domain has only one good piece of knowledge, it can live inside a broader file.

## Two zones, and everything declared

A smelt run makes more than the tree above, and it should: the raw output of the URL sweep, the unmatched spans from the quote audit, the script that computed a table. That material is what lets a number be re-checked a month later, so it is kept — but it is process, not product, and the package says so structurally.

| Zone | What is in it | Who reads it |
|---|---|---|
| **Deliverable** | `INDEX.md`, `README.md`, `knowledge/` | every consumer, by route |
| **Published audit trail** | `provenance/` | a consumer checking a claim |
| **Working material** | `.work/` — sweep output, audits, intermediate data, this run's scripts | nobody, unless a number is doubted |

Four rules hold the boundary, and they come from what a real package looked like when the boundary was left implicit: one third of its bytes were undeclared scripts, and the entry point never mentioned them.

- **Nothing exists that the INDEX does not declare.** Every directory in the tree appears in the Layout block with one line on what it is for — including `.work/`, and including a line saying a reader should *not* open it. A file that appears in no route and no layout entry is invisible to the consumer who navigates by following links, which is exactly how an agent reads a package. Naming something inside a fenced tree diagram is a description, not a route: the audit files a consumer may need get a real link.
- **The deliverable outweighs the scaffolding.** If working material is bigger than the knowledge it produced, the package's centre of gravity has moved out of the thing it exists to ship. Keep what re-checks a number; drop what only records that an attempt was made.
- **One measurement, one artifact.** When a second pass improves a measurement, it *replaces* the file rather than standing beside it (`x.py`, `x2.py`; `_audit.json`, `_final_audit.json`). Two artifacts holding the same set and disagreeing about it are not a draft history — they are an unanswered question the reader has to adjudicate. Where the delivered ledger's numbers come from one of them, name that one in the ledger.
- **An empty directory is an abandoned idea taking up a path.** Fill it, delete it, or write down what it was going to hold.

**Every count in prose is emitted from the artifact that holds the rows, never typed.** The index is already required to be "generated from what is actually written, not from memory" — the same obligation covers every number that describes the package: file counts, URL tallies, the disposition table's per-row counts, merge and correction totals. A count is a claim the tree can falsify, and it is usually carried by the entry point, where a reader has no way to check it. Say "18 files" only because something counted 18; when a sentence cannot inherit its number from an artifact, drop the number and let the layout say it once.

**A claim that something was fetched needs the bytes.** "The two header paths were corrected, confirmed by fetching, and `DEFAULT_EQ_SEL` is present" is a fetched claim, and a JSON summarising the run's own conclusion about it is a ledger entry, not a receipt — it records the answer, not the evidence. Anything a fetch establishes gets its raw response cached under `.work/receipts/` and named in the ledger row beside the claim, the same way a quotation is worth what the cached source text makes it worth. A status-only check is honest and is labelled as one: *`checked: HTTP status for 352 URLs; content not compared`* is a reach line, and a reach line is expected — an unlabelled one is what misleads.

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

Three more things the row has to carry, because a status code answers less than it appears to:

- **Where a redirect actually landed.** `redirect→v3` is a note, not a record: write the final address, and say whether the page at the end of the chain still documents the claim the citation supports. A 200 that arrives at a homepage, a cookie wall, or a marketing page that mentions the topic is a citation that no longer says what it said. Measured on a real base: of 276 live citations, 29 resolved to a different address and 7 to a different host, and the ledger recorded none of them because the sweep that checked them had code to record it and never called it.
- **What the check proved.** State the sweep's depth once at the top of the file — `status only`, `status + title identity`, `status + bytes retained` — so a reader knows what "alive" is worth here. Depth is a budget decision and any of the three is legitimate; an unlabelled one is not.
- **Tool failure kept apart from source failure.** A URL the checker could not parse, could not encode, or died on in its own exception says something about the checker. It is not a 404, not "unreachable", and not evidence about the source. Give it its own row value and re-check it after fixing the tool.

The denominator is the number of *addresses*, not the number of strings a URL regex found. Prose that mentions an address in passing gets swept up by any extractor — a path truncated to an ellipsis, a shell placeholder like `mr_url`, a bare domain inside a sentence — and each one then inflates the count the ledger reports as "every URL the corpus cites". Validate, and publish both numbers: candidates found, non-addresses rejected (with the list), addresses checked.

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
- **Every quote is verbatim at the cited location — audited, not sampled.** Run the whole delivered package's quoted spans against the corpus's cached bytes (`scripts/smelt_check.py quotes`) and account for every span that matches nowhere. A sample finds a typo; a full sweep finds that a span was invented. The residuals are what need reading — a scare quote around a term and a quotation between two quote marks are both legitimate and neither is self-evident, so the number is not the answer, the list is.
- **The package declares itself.** No directory sits undeclared, no directory is empty, working material does not outweigh the knowledge, and no two artifacts answer one question differently without one of them being named as the source of the ledger.
- **The numbers in prose are counted, not remembered.** Every count describing the package traces to the artifact that holds the rows.
- **Fetched claims hold their bytes.** Anything a live request established has a retained response beside it, and the sweep's depth is stated where a reader will meet it.
- **Every source file has a disposition** in `sources.md`, and a smelted yield with its tally in `provenance/yield.md` — sorted, low yields explained, total stated.
- **Every reference URL is checked.** `provenance/links.md` has a status for every unique URL — no `unchecked` rows, no sampling; dead links are recovered-and-cited or downgraded-and-gapped, never silently dropped.
- **No knowledge is duplicated.** Same subject, scope, and assertion appear once; variants are linked; contradictions are shown side by side. Near-verbatim text is the one part a script can decide; shared-evidence pairs it hands back as a list to read, because four in ten of those are the base citing one source line for two claims — which is correct, and not something a threshold can tell apart.
- **Lineage is honest.** Derived evidence is marked, and no confidence rests on it alone.
- **The file graph closes.** Every file is linked from `INDEX.md` and from at least one sibling; every cross-file reference resolves.
- **Gaps are explicit**, including the reasons the run itself gave.
- **The cold read passes.** `INDEX.md` plus the knowledge files answer the corpus's own questions without opening the source.
- **The destination is portable.** Paths are relative to the source root; nothing depends on the machine that built it.
- **The writing is clear.** A reader does not need the source to understand what the knowledge file says.
