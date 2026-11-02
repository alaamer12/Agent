# Job A — Reorganize a set

The full procedure for the request "this folder of docs is a mess / these files overlap / give this a proper structure". SKILL.md routes here; load `references/restructuring-rules.md` alongside this file, and nothing from the other jobs.

Documentation that grew organically — usually agent-generated, usually across many sessions — accumulates two defects that text-matching cannot find:

- **Duplication**: the same concept re-explained in different words in several files, which drifts apart the moment one copy gets edited and the other doesn't.
- **Concern-mixing**: one file covering several unrelated things because they came up in the same conversation.

Both are caught only by reading. Neither is caught by file size: a long file that stays on one subject the whole way through is healthy, and splitting it into pieces the reader now has to hop between is a regression. Split on findings from Step 2, never on line counts.

## Step 1 — Read everything in scope

Read every file in scope, fully, before designing anything. Duplication and concern-mixing are visible only with the whole set in mind at once. With a large set, read in batches and keep running per-file notes so the early files are still in hand when the later ones arrive; those notes are Step 2's input, so reading and mapping are one pass, not two.

## Step 2 — Build a map of concerns, not a file list

For each file, record the distinct concepts it actually covers, in your own words rather than its title. A "concern" here is anything a reader would look for on its own. While doing that, mark:

- the same concept explained in more than one place — any paraphrase counts, that is the duplication;
- files holding several unrelated concerns;
- concepts referenced everywhere and properly explained nowhere.

**Length is not a signal.** A long file that stays on one subject is not a splitting candidate; a short file that mixes three subjects is. The map records what the design needs: which file owns which concern, and which concerns have no owner.

`examples/concern-mixing-examples.md` has before/after statements of exactly this pattern, including the cases where the right answer was to leave a long file alone. Read it when the map is borderline and you need calibration.

## Step 3 — Design the target structure

Design where things should live. There is no required shape: the shape of each file and each README follows from what serves this particular project.

Read `references/structuring-conventions.md` now — not earlier, it assumes the map exists. It covers: one file, one concern, at full depth, with everything else a mention rather than an explanation; one home per concept with links from everywhere else; grouping by relationship rather than chronology; a README per directory acting as a local map; how nested READMEs compose; one global index that stays current; the short opening contract every document gets; and the recurring naming and granularity decisions — file versus directory, conventional category names, and `base`/`v1`/`v2` layering when the project actually versions.

## Step 4 — Draft the plan, self-check it, present it, then stop

Fill in `templates/plan-template.md` from the Step 2 map and the Step 3 design: what is wrong, then every source file mapped to exactly one action (Split / Merge / Move / Change), plus the new supporting files (READMEs, index).

Before showing it, run the draft against `templates/self-check-checklist.md`: Check 0 (does each proposed file need to exist at all) and the five content checks (each new file stays on one concern; a merge did not unite topically adjacent but different concerns; no two siblings from the same split quietly re-explain shared context). Fold the outcome into the plan's two-line "Self-check" section. Revise until it passes, silently — the checklist itself is not shown as work.

Then present the filled template and **stop**. Do not write new files until the user approves or adjusts. A split the user rejects after the prose has been rewritten is expensive to unwind; the shape is cheap to change now.

## Step 5 — Execute

Once approved:

1. Write the new files, **migrating** content: actually merge duplicated explanations into their one home instead of pasting parallel copies, and hold each file to its single concern at full depth. Anything outside that concern becomes a one-line mention with a link. Open every new file with the short contract under its title — `references/example-readme.md` shows the shape.
2. Write each directory README last, once that directory's final contents are known.
3. Write the global index at the root of the doc set (e.g. `docs/README.md`): one line per document, plus the standing instruction to update it on any add, removal, or move. Without that line the index rots the same way the docs did.
4. Handle the old files per the plan's decision — deleted, left alone, or kept as a pointer — and never discard content the plan did not account for.
5. Re-run the self-check against **what was actually written**, not against the plan. Execution drifts: a merge that turned out to need an extra paragraph of context, a split redrawn mid-write, a file that looked necessary on paper and reads thin once written, two siblings drafted independently enough that each grew its own explanation of what they should share. Check 5 is the one most likely to surface here.
6. Report what was created, moved and removed — not a walkthrough of every file's content. The new README structure now answers "where do I find X".
