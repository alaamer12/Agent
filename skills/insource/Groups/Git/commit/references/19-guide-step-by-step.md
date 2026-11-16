# Mode 1 — Guide, step by step

The six steps of a guided run in full: the commands to read the tree with, the table that decides which
convention to adopt, the staging traps, the message shape, and the check-then-commit sequence.

## Step 1 — Know what changed before you describe it

Prefer the context you already have; if this session produced the work, don't re-read a 3,000-line diff to
rediscover it. Otherwise inspect cheaply and summarize, never dump:

```bash
git status --short          git diff --stat          git diff --cached --stat
git diff -- <path>          # read only the files that decide the message
```

If you cannot say what the change accomplishes, you are not ready to write its message. A message invented
from filenames is where "update code" comes from.

## Step 2 — Adopt the repository's convention, do not import one

```bash
git log --oneline -20                              # the style actually in force
git log -3 --format='%n--- %h ---%n%B'             # the shape of a real body
ls .githooks .husky .pre-commit-config.yaml .commitlintrc* commitlint.config.* 2>/dev/null
grep -rilE "commit message|conventional commit" CONTRIBUTING* README* docs/ .github/ 2>/dev/null | head
```

| What the repo shows | Do this |
|---|---|
| a message linter, hook manager, or release tool configured (any ecosystem) | obey it exactly; run its check before committing |
| history is Conventional (`feat(scope): …`) | use it, matching its type vocabulary and casing |
| history is sentence style (`Fix rounding in invoice total`) | use that; do not convert the project |
| ticket prefixes (`APP-1234 …`) | include the key as the project does — trailer, not subject |
| fresh repo, no history, no config | Conventional Commits as the default, and say you chose it |

A convention the surrounding commits don't use is noise in `git log`; a tool-enforced convention you ignored
is a failed CI job.

## Step 3 — Split into atomic, change-based commits

- Mixed concerns (`fix` + `refactor` + `formatting` + `dependency bump`) become separate commits
  ([`03`](03-atomicity-and-staging.md)).
- A change and the tests that prove it belong together; a test for work you haven't written does not.
- Formatting-only and lint-only edits ride alone, so a behavior change stays reviewable.
- Order them so each intermediate commit is sensible — the reader and `git bisect` walk them in sequence.
- Split when a reviewer would ask "why are these two things in the same commit?"

## Step 4 — Stage deliberately

```bash
git add <paths>            git add -p            # named paths; hunk-by-hunk for a mixed file
git restore --staged <p>   git diff --cached     # fix staging; READ the source of the message
```

- Never a blind `git add .`/`-A` with more than one concern present — it sweeps in `.env`, scratch files,
  build output, and someone else's in-progress edits.
- Scan the staged diff for secrets, keys, tokens, debug printers, commented-out blocks, large binaries.
- In a shared worktree, re-check `git status` immediately before committing; another agent's work stays theirs.

## Step 5 — Write it

```text
<type(scope)!: subject, imperative, <= 50 where possible>     <- or the repo's shape
<blank>
<body: what and why, wrapped at 72; the constraint that made this the right choice>
<blank>
<trailers: Closes #123, Co-authored-by:, Reviewed-by:, BREAKING CHANGE: …>
```

1. **Imperative mood** — it composes with git's own `Merge…`/`Revert…` output.
2. **What changes for the reader**, not which files you touched.
3. **Short enough to survive `--oneline`** — 50 is the budget, 72 the ceiling; the rest belongs in the body.
4. **No trailing period**, no filler (`WIP`, `update`, `fix bug`).
5. **Body when the why isn't obvious** — motivation, the alternative rejected, the risk accepted.
6. **Never fabricate** — no "all tests pass" you didn't run, no "fixed" for a cause you didn't find.

## Step 6 — Check, commit, report

```bash
python scripts/commit_lint.py --file MSG      # format + clarity; exit 1 on findings
python scripts/commit_lint.py --staged        # secrets / junk in what is staged
git commit -F MSG                             # multi-line safe
git show --stat --no-patch HEAD               # the intended files, and only those
```

If the project lints messages in a hook, let it run and **fix the message** — never `--no-verify`. Do not
push, amend a published commit, or rebase shared history as part of "committing" ([`07`](07-history-hygiene-and-hooks.md)).
Then report the short hashes, one line each, and anything deliberately left uncommitted.
