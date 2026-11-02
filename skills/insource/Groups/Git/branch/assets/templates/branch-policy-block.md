# Branch policy — block for `AGENTS.md` §3 (Development Workflow)

`agents-md` owns `AGENTS.md`; this is the content to hand it. Keep it as obligations and pointers, in the file's
existing voice. Delete nothing around it, renumber nothing, and if a pinned/managed block overlaps, hand that
region through untouched.

Replace every `<…>`. Anything left as `<…>` is an unanswered decision — say so in the report rather than
inventing an answer.

```markdown
## Branching

**Trunk:** `<main>`. Everything else is temporary.

**Naming:** `<type>/<description>`, lowercase, hyphens between words, no underscores, no uppercase.
Examples: `feature/add-login-page`, `fix/parser-crash`, `release/v1.2.0`, `chore/upgrade-node-v20.11`.
Allowed types: `<feature|feat|bugfix|fix|hotfix|release|chore>` (+ team extensions: `<experiment|dependabot|wip>`).
Validate before pushing: `python <skill>/scripts/branch_name.py check "$BRANCH" --convention <conventional>`.

**Authorship (do not decide this silently, either direction):**
- commits: `<Co-authored-by: <Product> (<Model>) <noreply@…> | no co-author trailer — the human is the author>`
- branches: `<agent segment, e.g. <product>-<model>/feature/x, or the registered ai/claude/codex prefix> | no agent segment>`
- existing practice in history: `<what git log shows>` — if this line and the history disagree, raise it, do not
  "fix" the history.

**Where merges happen:** `<locally into <main> after tests | a PR on origin, merged by <who/what>>`.
Merge method: `<--no-ff merge commit | squash | rebase-and-merge>`; `<delete the branch after merge | keep>`.

**Lifetime:** merge within `<a working day>`; `<n>` active branches maximum. Delete or retire anything older than
`<m>`. A branch that is merged is deleted the same day.

**Fixes:** `<a fix always gets its own fix/* branch, cherry-picked to the trunk and to every supported release>`
|`<a fix may be committed inside the feature branch that exposed it; use the ladder in
<docs/committing.md> when the fix must interrupt unfinished work>`.

**Agents and shared worktrees (skip if this repository has only one writer):**
- before creating a branch in a repository that other agent sessions may be using:
  `python <skill>/scripts/branch_claim.py acquire --branch <name> --role <session> --ttl <4h> --note <scope>`
- one branch and one worktree per agent session; a session never switches branches mid-task, never `stash`es or
  `reset --hard` to clear the way, and never takes a name the ledger says is held — a collision is renegotiated
  (rename, split scope, serialize), not resolved by force
- worktrees live in `<../<project>-<task> | <repo>/.worktrees/<task>>`; that path is ignored via `<.gitignore entry
  | .git/info/exclude>`
- teardown order: integrate → `git worktree remove` → delete branch → `branch_claim.py release` → `git worktree prune`

**Ask before doing any of these:** force-pushing a shared branch (`--force-with-lease` at minimum), deleting a
branch you did not create, rewriting published history, retiring or renaming a long-lived branch, changing this
section.
```

## Notes for whoever writes it in

- **Keep it a rulebook.** Full explanations belong in `docs/branching.md`; here it is the duty and the pointer.
- **Check the claims.** Every path and command above must exist in the project — the linter that runs on
  `AGENTS.md` reports dead references, and a policy pointing at a script nobody installed is worse than no policy.
- **Name the enforcement separately.** If the user wants CI or a `pre-push` hook running the validator, that is a
  proposal with its own approval; this block documents the rule, it does not install the machinery.
- **Authorship lines get stale deliberately rarely.** If the project later decides to stop (or start) attributing
  agent work, the change is a one-line edit to this section plus a note in the changelog — not a silent shift in
  what agents emit.
- **Review date.** Put this section's date in the file's maintenance section so drift is measurable.
