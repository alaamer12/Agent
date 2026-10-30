# History hygiene, amending, and enforcement

Where the professional line is most often crossed by agents: a message is easy to fix afterwards, history is
not.

## Amending
Amend and rebase are the two operations that can destroy work. Before either, create the backup ref and prove the rewrite was content-neutral — the full gate is in [`14`](14-repairing-history.md).


```bash
git commit --amend -F MSG        # reword only, or fix the last local commit
git add missed/file && git commit --amend --no-edit
```

Amend is for the **last commit that nobody else has**. After that:

```bash
git rebase -i HEAD~5                     # local, unpushed only: squash / fixup / reword
git rebase -i --autosquash origin/main   # apply prepared `fixup!` commits in place
```

**Never** amend, rebase, or `reset --hard` commits that have been pushed to a shared branch, a PR others are
reviewing, or a branch someone else is working in — that rewrites their base and forces a destructive push.
If the user asks for it, confirm explicitly in the current session and check the working tree is clean first
(`git status`). Otherwise: new commit, new message.

Fixing a *message* on an already-pushed commit is possible without rewriting history only in limited setups
(forge UIs let you edit the display text of a commit; the object itself is immutable). Treat a bad pushed
message as something to explain in the next commit or the PR description, not as a license to force-push.

## Making the history readable before it merges

| Situation | Move |
|---|---|
| Long branch of `wip`/`fix typo` commits | squash into logical commits with `rebase -i` before opening the PR |
| Review fixes belonging to an earlier commit | `git commit --fixup <sha>` then `rebase -i --autosquash` |
| Branch should stay granular, project prefers one commit per PR | squash-merge, and write the merge commit message for the reader (title = the change, body = the why; the PR link goes in) |
| Revert then re-apply later | keep both commits; the second references the revert ([`05`](05-trailers-and-footers.md)) |

**Merge vs squash-merge vs rebase-merge is a project policy**, not a judgment call you make per commit. Find
the setting (GitHub's repo config, the contributing guide, or the last ten merged PRs) and follow it. Do not
switch strategy mid-branch because you prefer a tidier log.

## Enforcement that keeps messages honest

Enforcement is a **role**, not a product: something must check the message at commit time and something must
offer the structure while you type. Which tool fills the role depends on the stack, and the tool-neutral
implementation is git itself — a committed hook needs no package manager, no runtime, and no lockfile.

```bash
mkdir -p .githooks && git config core.hooksPath .githooks     # one line, documented in CONTRIBUTING
```

| Role | What it does | Illustrative options (any stack, or none) |
|---|---|---|
| Message check at commit time | rejects a message that breaks the project's shape | a `commit-msg` hook running this skill's `commit_lint.py`; [commitlint], [lefthook], [pre-commit], [gitleaks-style] hooks, a CI job that re-checks the range |
| Structure offered while typing | prompts for type/scope/subject/body and assembles a valid message | `git commit --template`, an editor snippet, [commitizen]/`git cz` and its adapters, [cz-style] prompters, a shell function |
| Staging-time content check | blocks secrets, junk, and debug leftovers | a `pre-commit` hook over the staged diff (`commit_lint.py --staged`), [lefthook], [pre-commit] |
| Merge-time policy | stops `wip:`/`temp:` reaching a protected branch | branch protection + a CI check on the commit range, since local hooks are trivially bypassed |

Two rules that hold regardless of tooling: **the check must live in the repository** (a hook each developer
installs locally is a hook half the team has), and **a local hook is a courtesy, a CI check is a policy** —
`--no-verify` defeats the first, never the second.

### A working `commit-msg` hook (new material, not recovered from the source)

The source names the idea in one line — "pre-commit hooks to block accidental `wip:` commits from going to
production branches" — and never writes the script. This is the script, authored here, git-native:

```bash
#!/bin/sh
# .githooks/commit-msg  -  enforce message shape and keep staging vocabulary off protected branches
msg_file="$1"
subject=$(sed -n '1p' "$msg_file")
branch=$(git symbolic-ref --quiet --short HEAD || echo detached)

case "$subject" in
  "") echo "commit-msg: empty subject"; exit 1 ;;
esac

case "$subject" in
  wip:*|wip-*:|temp:*|debug:*|try:*|checkpoint:*|save:*)
    case "$branch" in
      main|master|dev|develop|release/*)
        echo "commit-msg: '$subject' is checkpoint vocabulary and this is a protected branch."
        echo "            squash or reword first (see references/13), or commit on a feature branch."
        exit 1 ;;
    esac
    # allowed here: staging vocabulary is intentionally non-conventional, so skip the type check
    # (the length rule still applies)
    printf '%s
' "$subject" | awk 'length > 72 {print "commit-msg: subject is " length " chars (max 72)"; exit 1}' || exit 1
    exit 0 ;;
esac

# Conventional-shaped subjects: type must be known when the repo uses types
if printf '%s' "$subject" | grep -Eq '^[a-z]+(\([^)]*\))?!?:'; then
  type=$(printf '%s' "$subject" | sed -E 's/^([a-z]+).*/\1/')
  case "$type" in
    feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert) : ;;
    *) echo "commit-msg: unknown type '$type'"; exit 1 ;;
  esac
fi

printf '%s
' "$subject" | awk 'length > 72 {print "commit-msg: subject is " length " chars (max 72)"; exit 1}' || exit 1
exit 0
```

`chmod +x .githooks/commit-msg`, then test both directions: a `wip:` message on `main` must fail, and the same
message on `feat/x` must pass. A hook nobody has seen fail is a hook that may not be running.

Useful local checks in a `commit-msg` hook: subject length, blank line after the subject, body wrap width,
known types and scopes, trailer format, and a secret pattern scan on the staged diff. `scripts/commit_lint.py`
in this skill does those and can be called from a hook.

Two rules about hooks:

1. **Do not bypass them.** `--no-verify` hides the very signal that keeps the history consistent. If the hook
   fails on something legitimate, the fix is the project's rule or the message, decided with the user.
2. **A lint enforces shape, not quality.** `feat(x): update` passes every formatter and says nothing. Review
   the sentence, not just the regex.

## Templates and editor help

```bash
git config commit.template ~/.gitmessage        # pre-filled skeleton with commented rules
git config --global core.editor "…"
```

```text
# <type>(<scope>): imperative, <= 50 chars, no period
#
# Body: what and why, wrapped at 72. Leave blank if the subject says it all.
#
# Refs #
# BREAKING CHANGE:
```

Templates raise consistency in teams where half the members forget the rules; they do nothing for a message
written with `-m` from a script.

## Verification before you call the commit done

```bash
git show --stat --no-patch HEAD          # the intended files, and only those
git show --format=%B --no-patch HEAD     # read the rendered message, including blank lines
git log --oneline -5                     # does this read sensibly in a list?
git status --short                       # what did you deliberately leave out?
```

Report the hashes plus one line each, and name what stayed uncommitted. If tests, typecheck, or a build were
**not** run, say that plainly — the project's own instructions may forbid running them by default, in which
case "not run" is the honest status line rather than a silent omission.
