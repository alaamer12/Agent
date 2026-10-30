# Atomicity and staging

A commit is atomic when it contains **everything needed for one change and nothing else**, and it leaves the
tree in a state the project could ship or revert on its own.

## Why it matters mechanically, not morally

- `git bisect` can only point at a cause if each commit is one cause. A commit that fixes a bug *and* renames
  twelve symbols makes the bisect result meaningless.
- Reverting is per-commit. If the useful fix lives in the same commit as the experiment that broke things,
  you revert both or neither.
- Review is per-commit. A 900-line diff with 800 lines of reformatting hides the 20 lines that matter, which
  is how those 20 lines get a bug through.
- Cherry-picks and backports to release branches need commits that map one-to-one to changes customers get.

## The partition test

Ask of each candidate group: *would a reviewer ask about these two things separately?* If yes, they are two
commits. Other reliable split signals:

- the subject needs "and" or "also"
- the type would differ (`fix` + `refactor` + `chore`)
- the audience would differ (users get the fix; maintainers get the lint config)
- one part can be reverted without the other still making sense
- the file sets do not overlap in purpose

## The standard order when one session produced several concerns

```text
1. build/dependency changes the rest relies on   chore(deps): …
2. pure refactor, no behavior change             refactor(x): extract …
3. the behavior change or fix                    fix(x): …            (+ its tests)
4. feature addition                              feat(x): …           (+ its tests, flags, docs)
5. formatting/lint-only                          style: …
6. documentation and CI housekeeping             docs: … / ci: …
```

Dependency and refactor steps first means each later commit's diff is only the interesting part. Some teams
prefer formatting-only commits **last** so they do not pollute the history of a hot file twice - either is
defensible, what is not defensible is mixing formatting into the behavior commit.

## Staging mechanics

```bash
git status --short                              # ground truth of what exists
git add path/to/file another/file               # named paths: the default
git add -p path                                 # split one file's hunks across commits
git add -e path                                 # edit the hunk selection when -p is too coarse
git restore --staged path                       # unstage, keep the working-tree edit
git diff --cached                               # READ THIS before writing the message
git diff --cached --stat                        # sanity: the intended files, only
git commit -F MSG                               # message from a file - no quoting damage
```

`git add -p` prompts per hunk with `y/n/s/e/q`; when a single statement mixes two concerns, `e` lets you
hand-edit the patch. This is the normal way to split a file, not an exotic trick.

## Never

- `git add .` / `git add -A` with more than one concern present. It stages scratch files, build output,
  `.env`, IDE junk, and other people's in-progress edits.
- `git commit -a` as a habit: it stages every tracked modification without you looking at it.
- `git commit --no-verify` to get past a failing hook. The hook is either telling you the change is not
  ready, or telling you the message does not match project rules. Fix the named problem; if a hook is
  genuinely broken, say so out loud and let the user decide - do not silently bypass.
- `git stash` in a shared worktree to clear the way for a commit. Another agent or person may be mid-edit.
  Re-check `git status` immediately before committing; if the tree moved underneath you, re-read it and
  adapt rather than "restoring" anything you did not change.

## What belongs in the same commit

- **Tests for the change**, always. A behavior change without its test is a half-finished unit of work; a
  test for a change that is not in the tree belongs in a branch, not in history.
- The migration file and the model change it corresponds to.
- The docs and the flag when they only make sense with the feature.
- Lockfile changes caused by the dependency edit in that commit.

## What belongs elsewhere

- Unrelated dead-code removal, formatting drive-bys, TODOs noticed while working, a rename you wanted for
  years: note them, and put them in their own commit or a follow-up. If the drive-by is required to make the
  change compile, it is part of the change.
- Files you did not read. Do not commit what you cannot describe.
- Generated artifacts, unless the project checks them in on purpose - then commit them **together with** the
  source that produced them, in the same commit, so the tree is never internally inconsistent.

## Size guidance

"2-5 commits per session" is a useful heuristic, not a target. Do not merge unrelated things to look tidy,
and do not slice one logical change into six commits to look granular. The correct number is the number of
things a reviewer would describe separately.
