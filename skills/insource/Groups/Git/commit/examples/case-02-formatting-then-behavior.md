# Case 2 - one file, two concerns: formatting then behavior

**Situation:** while fixing a null-handling bug in `pricing.js`, the editor reformatted the whole file. The
working tree is now a 612-line diff in which 4 lines matter.

Committed as one blob, the reviewer either reads 612 lines or skips the diff - and the 4 lines that carry the
bug are exactly what a skimmer misses. This is the most common avoidable failure in real commits.

## Splitting one file across two commits

```bash
git diff --stat src/pricing.js            # 612 +-: almost all whitespace
git add -p src/pricing.js                 # select ONLY the 4 behavior hunks -> stage the fix
# prompts: y/n/s/e/q  - 's' splits a hunk, 'e' hand-edits the selection when 's' is not enough
git stash push --keep-index -- src/pricing.js   # park the formatting, keep the staged fix
git commit -F /tmp/fix-msg                 # commit 1 = the behavior change only
git stash pop
git diff --stat src/pricing.js            # now formatting-only, as expected
git add src/pricing.js && git commit -F /tmp/style-msg   # commit 2 = the reformat
```

In a shared worktree, skip the `stash` step (it can collide with another agent's edits): stage the fix, commit
it, then stage the rest and commit that - same result, no stash.

## Commit 1

```text
fix(pricing): treat a missing tax rate as zero, not null

`rates[jurisdiction]` returned undefined for jurisdictions without a configured
rate, and the null propagated into the invoice total as NaN. Invoices for those
jurjectories were silently wrong rather than failing loudly.

A missing rate now resolves to zero and the total is computed normally; unknown
jurisdictions are logged once per request. Test included for both the missing
rate and the unknown-jurisdiction path.
```

## Commit 2

```text
style: run prettier 3.3 over pricing.js

No logic changes - the file predates the 3.3 formatting rules. Committed
separately from the null-handling fix so that fix stays reviewable and
`git blame` on the four changed lines points at the fix, not at this reformat.
```

That last clause is the reason for the split: `git blame` attribution. One blended commit sends every future
reader of those four lines to a formatting change.

## If the two concerns are already committed together

Local and unpushed: `git rebase -i HEAD~1`, then `edit` the commit and re-split it with
`git reset HEAD^` + two `git add -p` passes. Pushed or shared: do not rewrite it - add a follow-up commit
that separates formatting from behavior going forward, and say so in the PR description.
