# Command reference

Every command this guide relies on, grouped by what you are doing. Annotations state the trap, because most of
these are commands people run confidently and get wrong once.

## Inspect before staging

```bash
git status                    # what exists, including untracked
git status --short            # compact
git diff                      # unstaged changes — review yourself first
git diff --cached             # what is about to be committed: the actual message source
git diff --stat               # line counts; watch a commit getting too big
git diff -- <path>            # one file, when the whole diff is too large to read
git show <sha> --stat         # what a past commit actually contained
```

## Stage selectively

```bash
git add <file>                # the normal case: named paths
git add -p <file>             # hunk-by-hunk; keys y n q a d s e ?
git add -e <file>             # edit the patch directly
git add -u                    # tracked modifications and deletions only (no new files)
git restore --staged <file>   # unstage, keep the working-tree edit
git reset -p                  # unstage by hunk
git restore <file>            # DISCARD working changes — back up first, this one is not undoable
```

Never a blind `git add .` / `-A` when more than one concern is present: it sweeps in `.env`, scratch files,
build output, and someone else's in-progress edits.

## Commit

```bash
git commit -m "type(scope): description"
git commit -F MSG             # multi-line message from a file: no shell quoting traps
git commit --amend            # fold into the LAST commit — local only, never pushed/shared
git commit --amend -m "…"     # reword the last commit only
git commit -am "msg"          # add -u + commit: modified/deleted TRACKED files only, NOT new files
git commit -S -m "…"          # GPG/SSH-sign the commit (who authored it)
git commit -s -m "…"          # add Signed-off-by (DCO: the right to submit) — different thing
git commit --trailer "Closes #123"   # structured trailer, placement handled for you
```

## Undo and split (pre-push territory)

```bash
git reset HEAD~               # undo the commit, KEEP the changes staged-then-unstaged
git reset --soft HEAD~        # undo the commit, keep changes staged
git reset --mixed HEAD~       # undo the commit, keep changes unstaged (default)
git reset --hard <ref>        # DESTROYS working changes — backup ref first
git revert <sha>              # a new commit undoing one: safe on shared branches
git revert -m 1 <merge-sha>   # undo a merge, keeping the first parent
git stash push -m "wip: …"    # NAMED, always
git stash list                # find it again
git stash apply stash@{0}     # apply, keep the stash (safer than pop while unsure)
git stash drop stash@{0}      # delete it once integrated
```

## Reorganize (backup ref first — see below)

```bash
git rebase -i HEAD~n              # pick / squash / drop / edit the last n commits
git rebase -i origin/main         # tidy everything on this branch before the PR
git rebase -i --autosquash origin/main   # apply prepared `fixup!` commits in place
git commit --fixup <sha>          # "this belongs to that commit" — autosquash picks it up
# in an `edit` stop: change code -> git add <file> -> git commit --amend -> git rebase --continue
git rebase --abort                # bail out of a rebase you no longer understand
```

## Move work between branches

```bash
git cherry-pick <sha>             # copy a commit here (the fix that belongs on fix/*)
git checkout -b fix/x main        # branch the fix off the right base
git push origin fix/x             # publish the branch, not your local main
```

## Push and release

```bash
git push                          # branches only — never pushes tags
git push --follow-tags            # annotated tags attached to pushed commits: the correct default
git push --tags                   # ALL local tags, including orphans — usually wrong
git push -f                       # force: never on shared branches; also does not push tags
git push --force-with-lease       # force, but refuses if the remote moved: the only acceptable variant
<project version command>         # bump + commit + tag together; find it in package.json/Makefile/docs
git tag v1.2.4                    # lightweight tag
git tag -a v1.2.4 -m "release"    # annotated tag — required by --follow-tags
```

## The backup sequence (before any history rewrite)

```bash
git branch backup/pre-rebase-my-feature
git rev-parse --short backup/pre-rebase-my-feature     # print it into the transcript
# … rewrite …
git log --oneline origin/main..HEAD
git diff backup/pre-rebase-my-feature HEAD             # MUST be empty
git push --force-with-lease
git branch -D backup/pre-rebase-my-feature             # delete only after verification
```

Why a branch and not the reflog: reflog entries expire (`gc.reflogExpire`, default 90 days) and `git gc`
prunes unreachable objects. A named ref keeps the commits alive and visible to anyone who needs to recover.

## Inspect history

```bash
git log --oneline                     git log --oneline --graph
git log -3 --format='%n--- %h ---%n%B'   # the real message shape of this repo
git log --grep=wip-fix                # find the parked TODOs you labeled honestly
git log --format='%s' | grep -cE '^[a-z]+(\(.+\))?!?:'   # how Conventional is this repo?
git log --all --format='%(trailers)' | sort -u           # which trailers the project uses
git blame -L 120,140 <file>           # who/what commit introduced this line
git shortlog -sn HEAD                 # authorship summary
```

## Find the mistakes before someone else does

```bash
python scripts/commit_lint.py --file MSG          # lint a message before committing
python scripts/commit_lint.py --staged            # secrets/junk scan of what is staged
python scripts/commit_lint.py --history           # the repo's style + outliers
python scripts/commit_lint.py --history --shared origin/main   # staging prefixes that reached a shared branch
git config --global alias.wip '!git add -A && git commit -m "wip: save progress"'   # convenience only
```

## Recovery when something went wrong

```bash
git reset --hard backup/pre-rebase-my-feature   # undo your own rewrite
git reflog                                      # last-resort: local history of HEAD positions
git fsck --lost-found                           # find dangling commits (do not automate this)
git checkout --ours <file> / --theirs <file>    # conflict resolution: name which side you chose
```

`git reflog` saves an uncommitted-then-reset mistake far more often than people expect — check it before
declaring work lost, and note that it is local-only: it does not exist on a fresh clone.
