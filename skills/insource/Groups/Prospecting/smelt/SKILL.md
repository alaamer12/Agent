---
name: smelt
version: 1.1.0
author: Amr
specialized: none
description: 'Turns a completed mine run — or any corpus of checkpoints, distillations, plans and witness notes — into a durable, evidence-linked knowledge base another agent can consume. Trigger on "/smelt", "smelt the mine", "build a knowledge base from these files", or any request to preserve what was learned across many large files. Works file by file into a running knowledge file, then reconciles folders globally. Verifies every URL the run left behind — exhaustively, never a sample — recording status, the address a redirect landed on, and how a dead link was handled, and reports each source file''s smelt yield. Writing is free-form — no template — and every claim stays traceable to its source. Never summarizes sources away, never deletes a finding, always keeps the evidence pointer. Keeps the run''s working material in a declared .work/ zone, and scripts/smelt_check.py measures what eyeballing cannot: redirect chains, every quote span vs the cached corpus, undeclared files, counts that disagree with the tree.'
argument-hint: "<source folder> into <destination>"
---

# Smelt

Take what a mining run learned and turn it into a knowledge base another agent can use without reopening fifty files.

The source folder is read-only. The destination folder is the product. Nothing is written back into the source.

## The two paths

The request names both:

```
/smelt the mine for payments-platform into kb/payments-platform
```

- **Source** — the run directory to read. If the path is a parent containing several runs, list them and ask which one; never guess.
- **Destination** — where the knowledge base is written. Create it if absent. If it already holds a knowledge base from the same run, resume it. If it is non-empty and is not a knowledge base, stop and ask.

There are no other settings. The shape of the source decides how the run is processed.

## The method

Read one file. Write what it taught. Read the next file. Return to the same knowledge file and integrate what is new, correct what now looks wrong, and merge what is the same. When the folder is complete, leave its knowledge file exactly as it stands and move to the next folder — no re-read, no compression. Only after every folder is done does the agent read all the folder knowledge files together, once, and integrate, correct, and reconcile them into the final knowledge base. That base may be one file or several: each file owns a unique body of knowledge and links to the files around it, so no file is an orphan.

```
experience/01-x.md ─┐
experience/02-y.md ─┼─▶ experience knowledge file ──┐
experience/03-z.md ─┘        (edited after each)    │
                                                    ├─▶ global reconciliation ──▶ YYY
distillation/….md  ──▶ distillation knowledge file ─┘
plan/….md          ──▶ scope notes ─────────────────┘
```

The running knowledge file is the agent's memory between files. It is why a later source can correct an earlier misunderstanding, and why two sources saying the same thing become one piece of knowledge instead of two.

**Compression here means removing duplication and correcting misunderstanding, never shortening for its own sake.** A sentence that carries a caveat, a number, a dissent, or a limit stays. If two pieces say the same thing, they become one piece with two pieces of evidence — not one piece with the second source deleted.

## What the agent is looking for

The material decides what matters. These are ways of noticing, not labels to fill in:

- a pattern, and the naive alternative it displaces
- a decision, what it replaced, and what it cost
- a constraint, and the failure it prevents
- a failure mode, and its warning sign
- a measurement, with its unit, measure, and denominator
- an entity, in countable terms
- an outlier, and what makes it different
- a contradiction, and what turns on it
- a gap, and what would settle it
- a technique, and the conditions it needs
- a term, and what it means in this corpus

## The writing

**There is no template.** No required headings, no fixed field order, no numeric ID scheme, no prescribed table. Write the knowledge the way a strong engineer would explain it to a peer who has not read the sources: in paragraphs, sections, tables, diagrams, or notes — whatever shape the knowledge actually has.

The same freedom `/mine` gives its checkpoints applies here. A mined checkpoint is free-form because a codebase and a design screen do not have the same things worth saying; a smelted knowledge file is free-form because a tenancy decision and a profiling bias do not either.

What every piece of knowledge must make answerable, in whatever form it takes:

1. **What is claimed.** One clear statement, not a gesture at a topic.
2. **How it works, why it is that way, and what it costs.** The mechanism and the tradeoff, not just the outcome.
3. **Where it came from.** File, section or line, and a verbatim quote.
4. **How it is known.** Stated by the source or inferred; and how far the source actually reached.
5. **Where it stops.** Limits, exceptions, disagreements, what it cannot support.
6. **What it connects to.** Related knowledge, named, in this file or another.

A piece that cannot answer 3 is not knowledge yet. It may be a question worth writing down, but it does not enter the base as a claim.

Length follows substance. A one-line fact may need one sentence; a mechanism that took a chapter to establish may need several paragraphs. Do not pad a thin source, and do not compress a rich one to look uniform.

## Transparency

Transparency is structural, not a disclaimer at the bottom:

- **Evidence is visible.** Every claim sits next to the source that supports it — file, location, exact words. A reader can check any claim without trusting the writer.
- **Observation stays separate from inference.** Say when the source states something and when you concluded it. Never let an inference read like a quotation.
- **Reach limits travel with the claim.** If the source read 15 files of a 30,000-file tree, the claim carries that denominator. "Not measured" is written down, never left blank.
- **Nothing is deleted.** A correction marks what was believed before, what replaced it, and why. The old reading stays legible.
- **Disagreement stays visible.** Two sources that conflict are shown side by side, with what turns on the difference. They are not averaged into a tidy middle.
- **Gaps are first-class.** What the corpus could not establish, and what would settle it, is part of the knowledge, not an omission from it.
- **Coverage is accounted for.** Every source file is listed with what it contributed, confirmed, or why it was skipped — and with its **smelt yield**: the share of that file's knowledge that entered the base (e.g. `80% of experience/05-atlas.md`), computed from the fold ledger, sorted top yield to bottom, with a one-line reason wherever the yield is low. `provenance/yield.md`.
- **References are verified, all of them.** Every URL a mining file cites — checkpoint ledgers, bibliography, inline sources — gets checked before delivery, exhaustively, not by sampling: alive, redirected, or dead, with the date and what was done about it (recovered from an archive, the claim's confidence marked down, a gap written). A dead reference is stated at the claim it supports, never quietly dropped. `provenance/links.md`.
- **Every merge is recorded.** What was combined, what was kept apart, and what changed the writer's mind.

## The package is part of the product

The knowledge is the deliverable; the run also generates a sweep's output, an audit's unmatched spans, and the scripts that computed a table. That working material is kept — it is what makes a number re-checkable — but in `.work/`, declared in the INDEX layout with a line saying a reader need not open it. Nothing sits in the package undeclared, no two artifacts answer one question without the delivered ledger naming its source, and every count in prose is emitted from the rows that hold it rather than typed from memory. Full rules: `references/output.md` → "Two zones, and everything declared".

`scripts/smelt_check.py` measures the half of the verify pass that is measurable — `package`, `quotes`, `links --sweep` — because a claim that survives at 352 URLs and a megabyte of prose does not survive eyeballing. It is advisory: each finding is fixed or waived with a reason. It never decides whether knowledge is right, and a clean report is not a pass.

## Writing standards

- Lead with the claim, then the mechanism, then the cost.
- Prefer precise nouns and measured numbers over adjectives.
- Quote exactly. Paraphrase everywhere else.
- Distinguish what the source says from what you conclude.
- No filler, no marketing, no performance of thoroughness.
- Do not inflate confidence because several files repeat one source's claim.
- Do not smooth a real contradiction into a consensus.
- Say "the corpus does not establish this" when it does not.

Clear, plain, professional prose is the deliverable. If a reader needs the source to understand the knowledge file, the writing failed.

## What to read, what to skip

Read the folders that carry knowledge, in this order unless the request names a different starting folder:

1. The plan — `plan/` or `sources/plan.md`, wherever the run keeps it. It supplies scope, vocabulary, and the questions the run set out to answer.
2. `experience/` — the primary knowledge. Read every file in full.
3. `distillation/` — read last, as a cross-check. It is derived; it can reveal what extraction missed, but it cannot add a source.
4. `witness/` — provenance. Read the text and tables; they settle which claims were verified.
5. `tools/` — what the run could reproduce, not what it concluded.

Do not bulk-read `sources/`, `cache/`, clones, tree dumps, or binaries. They are evidence, not knowledge. Record them in `sources.md` and open a specific file only to verify a quote.

A folder whose files are not readable text (images, recordings, datasets) is recorded as skipped with the reason. Missing knowledge is written as a gap, never invented.

## Starting, stopping, resuming

- **Start** by inventorying the source and writing `sources.md` with what will be read, what will be skipped, and why. Do this before reading any file, so the coverage is honest from the first page.
- **Stop** a folder only when every file in it is either folded in or recorded as skipped with a reason. Leave the knowledge file as it stands and move on; the single compression pass happens after all folders are done.
- **Resume** by reading `sources.md` for processed files and the folder knowledge files for accumulated knowledge. Continue at the first unprocessed file. Do not restart a finished folder.

## Before delivery

Read the knowledge base cold, as a consumer would. It must answer, without opening the source: what this corpus knows, how confident it is, where each claim came from, what it contradicts, and what it does not cover. Every file must be reachable from `INDEX.md` and from at least one sibling. The link ledger must show every unique URL checked (counts must match the sweep, or the pass is incomplete) and the yield table must cover every read file. If any of that requires the source, the package is incomplete.

## References

| File | Read it when |
|---|---|
| `references/workflow.md` | Running the fold: URL sweep and check ledger, per-file integration with fold tallies, closing a folder, the single global reconciliation, large files, resume |
| `references/knowledge-model.md` | Deciding whether something is new, duplicate, a variant, a contradiction, or a correction |
| `references/output.md` | Writing the destination: layout, the two zones, index, provenance, and the quality bar |
| `scripts/smelt_check.py` | The verify pass, step 5 — `package` (declarations, counts, receipts, duplicates, file graph), `quotes` (every span against the cached corpus), `links --sweep` (status, redirect chains, archive recovery, retained receipts). Stdlib Python, no dependencies, no network unless `--sweep` is passed |
| `tests/test_smelt_check.py` | Before trusting a report from the checker: mutation-tests every check — builds a clean package, injects one defect per check, requires it to fire, and requires the clean package to stay silent. `python tests/test_smelt_check.py` (`--no-network` skips the local-server half) |
