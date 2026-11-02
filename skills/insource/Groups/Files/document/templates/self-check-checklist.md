# Self-check checklist (Step 4.5)

Run this against your own plan, after drafting it and before presenting it. The failure mode this guards against: the plan correctly breaks up the *old* concern-mixing, but the *new* structure quietly reintroduces it — either within a single new file (mixing concerns at a finer grain than before), or, more subtly, **across siblings that came from the same split** (a file gets correctly broken into Doc B and Doc C, but B and C each independently re-explain the shared context they both need, recreating the original duplication between the two new files instead of inside one old one), or by **creating files that shouldn't exist at all** — a split or a convention applied for its own sake rather than because the content actually needed it. A split that isn't re-checked against its own output can just relocate the original problem instead of fixing it, or replace one bloated file with several unnecessary thin ones.

Do this check silently as part of preparing the plan — don't show your work, just fold the result into the "Self-check" section of the plan (see `templates/plan-template.md`).

## Check 0: does this new file need to exist?

Ask this before the five content checks below, and ask it of every new file — not just splits. A new file earns its place only if it holds real, substantial content on its own concern. Watch for:

- **A directory README (or index) created for a directory that doesn't need one.** If a directory only ends up with one or two files, its README is likely restating what a one-line note in the *parent* README could say just as well — see Step 4's flat-vs-directory convention in `references/structuring-conventions.md`. Don't create the nested README just because "every directory gets one" — that rule exists to serve directories that actually need local navigation, not as a checklist to complete.
- **A split fragment too thin to justify itself.** If splitting a concern out produces a file that's mostly a pointer to another file, with barely any content of its own, that's not a concern with its own home — it's a link wearing a file's clothes. Fold it back into whichever file it's really serving, or into that file's parent, instead of giving it its own path.
- **A new file whose only justification is "the old file was long."** Per Step 2's length-is-not-a-signal principle: if you can't point to an actual concern boundary this file exists to hold — only that splitting made things shorter — don't create it. See `examples/concern-mixing-examples.md` (Example 8) for a worked case of exactly this.
- **Two files doing the same navigational job.** A directory shouldn't end up with both a `README.md` and a separate summary/index file covering the same ground — pick one.

If a proposed file fails this check, the fix is usually to fold its content back into a neighbor (the parent, the sibling it was split from, or the file it mostly just points to) rather than leaving a thin file in the tree.

## The five content checks

Run these against whatever new files survive Check 0.

**1. Can you state its concern in one sentence, without "and"?**
Try to write the one-line purpose you're about to put in the tree. If it needs "and" to join two things that aren't obviously the same concern, this new file is mixing concerns on arrival — go back and split it further, or reconsider which old content actually belongs together.

**2. If this file merges content from multiple old files, did the merge stay in-concern?**
Merging is meant to consolidate *one* concept's duplicate explanations into one home — not to combine everything that happened to mention a similar topic. Two old files can both mention "topic X" while having different actual concerns (one technical, one conceptual); merging them because they share a keyword recreates mixing under a new name. Check that everything landing in a merged file is actually the same concern, not just topically adjacent.

**3. Does anything in this file's draft content explain something outside its stated concern at more than a mention?**
This is the same test as Step 3's mentioning-vs-explaining principle (`references/structuring-conventions.md`), applied to the *new* files specifically. If you're imagining a paragraph of context that isn't this file's job, that's the split not going far enough, or a piece of content assigned to the wrong destination.

**4. Are any two new files about to independently explain the same thing, unrelated to any split?**
Easy to miss when content gets redistributed — two new files can each end up needing to reference the same underlying concept and both explain it in passing, recreating duplication that didn't exist in the original single file. Check that only one of them owns the explanation and the other links to it.

**5. When one old file was split across several new files, did the split itself reintroduce duplication between the pieces?**
This is the sharpest version of the failure and the easiest to miss, because it looks like progress while it's happening. File A gets correctly split into new Doc B and new Doc C — but B and C each need some of the *same shared context* to make sense on their own, and since they're being drafted somewhat independently, each one quietly re-explains that shared context to be self-contained. The result: the duplication that used to live inside one file (findable by re-reading that file) now lives *between* two new files (much harder to spot, because nothing prompts you to compare them side by side — they don't look related from their names or locations). Concretely: if Doc B and Doc C both descend from the same source file, open them side by side and check whether either one is carrying a paragraph of context that actually belongs to the other, or to a third shared file neither of them is. The fix is usually the same tool used elsewhere in this skill — pull the shared context into its own home (existing or new) and have both B and C mention it with a link, rather than each explaining it independently.

## If a check fails

Don't present a plan you know fails one of these — revise it before showing it to the user. It's fine (expected, even) to iterate on the target structure a couple of times internally before landing on one that passes Check 0 and all five content checks; that's cheaper than the user catching it after approval, and much cheaper than after execution. Check 0 is worth running first and separately — it's faster to decide a file shouldn't exist than to content-check a file you're about to delete anyway. Check 5 is worth doing deliberately rather than trusting it'll surface on its own — for every old file being split into more than one new file, explicitly list the new files it produced and compare them against each other, not just against the rest of the tree.

## What to put in the plan's "Self-check" section

Keep it short — this isn't a place to re-explain the checklist. State the outcome plainly:

```markdown
## Self-check

Ran Check 0 (does each new file need to exist) and the five content checks
against everything that survived it, including comparing siblings from the
same split against each other (check 5). <One line noting anything notable —
e.g. "Dropped a planned `tech/README.md` — the directory only ends up with
one file, so a note in the parent README covers it instead" or "Doc B and
Doc C, both split from File A, were each drafting a paragraph re-explaining
<shared concept> — pulled it into <shared home> instead" — or, if nothing
notable came up:> No issues found.
```

If the check caught and fixed something, naming it briefly here is more useful to the user than silently fixing it — it shows the plan was actually stress-tested, not just drafted once and shipped.
