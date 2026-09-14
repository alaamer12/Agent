---
name: docs-refactor
description: Reorganize a messy set of Markdown/text documentation into a clean, one-concern-per-file structure with a per-directory README acting as a local map. Use this when the user explicitly asks to refactor, reorganize, restructure, clean up, or de-duplicate a documentation set — phrases like "refactor these docs," "these files are a mess, can you reorganize them," "split this doc up," "our docs keep repeating the same stuff," or "give this folder a proper structure." Do not trigger on requests to just edit or fix content in a single existing file, or to write a brand-new doc from scratch — this skill is specifically for restructuring an existing multi-file (or single bloated-file) documentation set.
---

# Docs Refactor

A skill for taking documentation that has grown organically — usually AI-generated, usually across many sessions — and turning it into a set of files that each own exactly one concern, with a README at every directory level acting as a mini-map for whoever (human or AI) lands there next.

## Why this matters

Documentation written incrementally tends to accumulate two problems: **semantic duplication** (the same concept re-explained in different words across files, which drifts as one copy gets edited and the other doesn't) and **concern-mixing** (a file covering several unrelated things because they came up in the same conversation). Neither is catchable by matching text — both require reading for meaning.

The fix isn't a fixed template — it's a discipline: each file has one job, each directory has a README, and nothing is explained twice. Other docs link to the one place a concept lives rather than re-explaining it. Full detail on this discipline is in `references/structuring-conventions.md` — read it in Step 3, not before.

Neither problem is about file size. A long file can be perfectly healthy if it stays on one concern throughout — don't treat length alone as a reason to split something.

## When to use this

Trigger only on an explicit request to reorganize, refactor, restructure, or clean up an existing set of docs. Don't proactively suggest this mid-task — a one-line mention of bloat is fine, taking over the conversation isn't.

Not for: writing a new doc from scratch, fixing content in a single existing file, or converting file formats.

## The workflow

This is a **plan-then-execute** process. Never skip straight to rewriting files — the plan is the deliverable you get approved; execution only happens after the user signs off.

### Step 1: Read everything in scope

Read every file the user means, fully, before analyzing anything. Don't sample or skim — concern-mixing and semantic duplication are invisible unless you have the whole corpus in mind at once. For large sets, read in batches but keep running per-file notes (see Step 2) so earlier files aren't lost by the time you reach later ones.

### Step 2: Build a concept map, not a file list

For each file, note every distinct concept/concern it actually covers, in your own words — not just its title. A "concern" is something a reader would want to find by itself. While doing this, watch for: the same concern explained in multiple places (paraphrase counts as duplication), a file mixing unrelated concerns (can't summarize its purpose in one sentence without "and"), and concepts mentioned everywhere but properly explained nowhere.

**Length is not itself a signal.** A long file that stays on one concern the whole way through — even a repetitive one, like the same reference template applied to a dozen items in turn — is not a candidate for splitting. Splitting it would scatter one coherent reference across many files a reader would then have to hop between, which is worse than the long file it replaced. Only split on an actual finding from this step: real concern-mixing or real duplication, found by reading, not on line count or section count. See `examples/concern-mixing-examples.md` (Examples 7 and 8) for worked cases of a long file that should be left alone, and a split that shouldn't have happened even though every resulting file was individually clean.

Read `examples/concern-mixing-examples.md` now — it has small before/after-statement examples of exactly this pattern, drawn from real doc sets, and will calibrate what to look for (and what to leave alone) before you design anything.

Keep the map as working notes; you'll use it in Step 3.

### Step 3: Design the target structure

Now design where things should live. There's no fixed required shape — the shape of each file and README should follow from what serves this specific project's readers.

Read `references/structuring-conventions.md` for the full set of structural principles (one-concern-at-full-depth, mentioning vs. explaining, per-directory READMEs, the self-maintaining global index, every document's own opening contract) and naming/granularity conventions (flat files vs. directories, conventional category names like `tech`/`product`/`structure`, layering shared vs. scoped content like `base`/`v1`/`v2`). Apply what's relevant to this project; skip what isn't.

### Step 4: Draft the plan, self-check it, then present it — and stop

Draft the plan using `templates/plan-template.md` — it maps every source file to exactly one action (Split / Merge / Move / No change) plus the new supporting files (READMEs, global index), built from your Step 2 findings and Step 3 design.

Before showing it to the user, run the draft against `templates/self-check-checklist.md`. This catches two related failure modes: files that shouldn't exist at all — a split or a convention (a per-directory README, a naming pattern) applied for its own sake rather than because the content needed it (Check 0) — and files that exist for a good reason but whose content quietly reintroduces mixing or duplication in how it recombines things: a merged file that combines topically-adjacent-but-different concerns, a split that didn't go far enough, or (the sharpest version) content split out of one old file into two new ones that each independently re-explain the shared context between them (Checks 1-5). The checklist runs Check 0 first, then five quick content questions per file that survives it, and explicitly asks you to compare siblings from the same split against each other. Do this silently, revise the plan if anything fails, and fold the outcome into the plan's own "Self-check" section (one or two lines — what you checked, and what you fixed if anything).

Then present the filled-in plan and wait. Do not start writing new files until the user approves or adjusts it. A wrong split is expensive to redo once content is rewritten and cross-linked — get the shape approved, self-checked, before investing in prose.

### Step 5: Execute

Once approved:

1. Write the new files, migrating content — actually merging duplicated explanations into one, not copy-pasting the first occurrence found. Cross-link instead of re-explaining. Hold each file to its single concern at full depth; anything outside that concern becomes a one-line mention with a link, not a parallel explanation. Open every new file with a short contract under its title — what it is, and a mention (with a link) of any document a reader would need first or alongside it, especially when this document applies or builds on conventions defined elsewhere. See `references/example-readme.md` for a worked example of this contract.
2. Write each directory's README last, once its final contents are known.
3. Write or update the root-level global index (e.g. `docs/README.md`) with a one-line-per-doc listing and the standing instruction to keep it updated on any add/remove/move.
4. Handle old files per the Step 4 decision.
5. Final pass: re-run the `templates/self-check-checklist.md` checks — Check 0 (does each new file still earn its place, now that you can see what actually got written into it) and the five content checks — against what was actually written, not just what was planned. Execution can drift from the plan: a merge that turns out to need a paragraph of extra context, a split that got redrawn mid-write, a file that seemed to need splitting on paper but turned out thin once written, or two sibling files drafted independently enough that each grew its own explanation of something they should share. Pay particular attention to check 5 here — it's more likely to surface after real prose is written than during planning. Check each new file both earns its existence and is still true to a single concern at full depth, and skim for any explanation — of another concern, or of something explained elsewhere — that crept back in as more than a mention.

Report back with what was created/moved/removed, not a re-walkthrough of every file's content — the new README structure should now answer "where do I find X."
