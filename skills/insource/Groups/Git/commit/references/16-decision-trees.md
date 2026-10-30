# Decision trees

The whole guide, compressed to the paths you actually walk. Source citations live in the topic files
([`09`](09-when-to-commit.md)–[`15`](15-releases-tags-bumps.md)).

## When is it time to commit?

```text
Can you describe the change in one sentence?          -> commit now
Just finished and tested a function?                  -> commit
Just fixed a bug?                                     -> commit (its own commit, not inside the feature)
Only formatting changed?                              -> separate `style:` commit
~100 lines and still growing?                         -> commit before you lose the thread
"Too small to bother"?                                -> commit anyway: intent, not importance
500 lines in one blob?                                -> stop: split with git add -p
Half-done but harmless (flag-gated, inert)?           -> commit it honestly: "scaffold … (not active yet)"
```

## Which type?

```text
Observable behavior changed?
├─ new capability                     -> feat
└─ it was broken                      -> fix
Same behavior, better shape of logic  -> refactor
Same behavior, faster/lighter         -> perf   (json -> orjson is perf, NOT refactor)
Only formatting/lint/import order     -> style  (CSS is NOT style: see below)
Only what is tested changed           -> test
Only test structure/naming, same assertions -> refactor
Only text/comments                    -> docs
Build system / deps                   -> build ; CI config -> ci
Routine support: config, scripts, releases, .gitignore, __init__.py -> chore
CSS that *looks* different            -> fix (visual bug) / feat (new capability) / refactor (reorganized)
Answer needs the word "and"           -> two commits
```

## Which scope?

```text
One file or module touched        -> name it: fix(api/user.py), feat(auth), test(Button)
Several files, one shared concern -> name the concern: fix(reporting), refactor(parser)
Project-wide mechanical change    -> omit the scope: style: format all files, chore: update license headers
Tempted to write a.py+b.py        -> stop: that is the signal to split the commit
Repo pins an approved scope list  -> use it (CONTRIBUTING.md or the message-lint config)
```

## One commit or N, for many files at once?

```text
Each file substantive and distinct        -> one commit per file, scoped (per-file blame survives)
Boilerplate/placeholders, one sitting     -> one bulk commit with a descriptive message
Different people will own them later      -> separate commits
```

## A fix interrupted the feature?

```text
Can you switch branches?          -> temp fix/* branch + PR, then cherry-pick or rebase the feature
Cannot switch, but can commit?    -> local wip/fix-* branch (cleanest)
                                  -> or named stash: git stash push -m "fix: …"
                                  -> or a labeled commit: "wip-fix: … extract to fix/* later"
Should you just fold it into the feature commit?  -> never: adjacent is not related
Keep working on the fixed code?   -> yes. The door must work now, even if the report is filed later
```

## Squash or not?

```text
Solo work, steps worthless later, clean-main culture  -> squash (or squash-merge)
Shared branch (anyone else builds on it)               -> never rewrite; fix forward
R&D trace or bisect granularity has value              -> keep commits, squash only the noise
Big diff but genuinely one coherent thing              -> fine (800 lines of a rendering engine is one thing)
Several things glued for tidiness                      -> split
Understandable in 1-2 minutes?                         -> ship it; otherwise split
About to rewrite history at all                        -> backup ref first (see below)
```

## Something already committed is broken?

```text
Committed, local only      -> fix, git add, commit --amend
Pushed, branch is yours    -> rebase -i (with backup) then push --force-with-lease
Pushed, shared             -> new honest fix: commit. Always.
Hopeless for now           -> git stash push -m "broken-<feature>"
Two commits, same message  -> reword one; duplicate fixes are fine, duplicate messages are not
Fix A caused bug B         -> two fix commits (A, then the consequence fix B); one only if B is trivial
```

## The safety gate before any rewrite

```text
About to run: rebase -i | commit --amend | reset | filter-* | push --force*
  1. git branch backup/pre-<op>-<name>
  2. print git rev-parse --short backup/…
  3. do the rewrite
  4. git diff backup/… HEAD   -> MUST be empty (same content, different history)
  5. push --force-with-lease (never plain --force on shared branches)
  6. git branch -D backup/…   only after everything verifies
```

If step 4 is non-empty, you changed the code, not the history — that needs its own commit and its own review.
