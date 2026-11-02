# Coordinating agents on one repository

The three situations are not variations of one problem; they differ in what you can *know* about the other writer.

| Situation | Other writer | What you can rely on |
|---|---|---|
| **A — alone** | nobody | nothing needed |
| **B — other agent processes** | another session: another terminal, another tool (Claude Code + Codex), possibly an older clone, possibly a person | only what is **in the repository**: refs, the claim, branch names — never their intentions |
| **C — your own subagents** | workers you spawned, in this process | your own bookkeeping, because you are the single writer of coordination state |

## A — working alone

Skip all ceremony. The only failure worth guarding against is the branch that never dies: after merge, delete it
(`git branch -d`, `git push origin --delete`), or the active-branch count silently invalidates the strategy that
was chosen. Two worktrees are still useful — one for the experiment, one for the thing you must not disturb.

## B — other agent processes share the repository

### What actually collides

Two sessions in the same working directory: file edits land in each other's trees, `git add` races on one index,
each reads the other's half-finished state as if it were project truth, and both commit to whatever branch
happens to be checked out. Worktrees fix the first three (see `04-worktree-playbook.md`). **Branch collision is
not fixed by worktrees**: two worktrees can each check out a different branch and still both decide,
independently and reasonably, to create `feature/login-page`.

That is the problem the claim exists for.

### The claim

```bash
python <skill-dir>/scripts/branch_claim.py acquire \
  --branch feature/login-page --role claude-code --worktree ../proj-login --ttl 4h \
  --note "routes + backend; do not touch src/ui/"
```

It writes two things:

| Artifact | Why |
|---|---|
| `<common git dir>/agent-branch` | a readable ledger: **what this session acquired** and **what another acquirer must do** (the collision policy, the default TTL, the scope note) |
| `refs/agent/<slug>` | the actual lock, created with `git update-ref <ref> <oid> 0000…` — git refuses when the ref already exists, so two processes cannot both win, and there is no window between checking and taking |

Why both and not just the file: a plain file edited by two processes is a lost update, and a hand-rolled
`open(..., O_EXCL)` lock cannot be inspected by tools that already speak git. The ref is atomic, is shared by
every worktree, survives a deleted file, and shows up in `git for-each-ref refs/agent`. The file is the part a
human reads. When they disagree, the script reports the mismatch rather than trusting either.

`--cwd` targets the repository; the path is resolved through `git rev-parse --git-common-dir`, so a linked
worktree reads and writes the **same** ledger as every sibling. (Relative output from git is a real trap: resolve
it against the repo, never against the process working directory.)

### What happens when another agent wants what you have

That is the only interesting case. The script answers it mechanically and the policy says what it means:

| Outcome | Meaning | What the next acquirer does |
|---|---|---|
| exit 0 `FREE` | nobody holds it | acquire it; you now own the name |
| exit 3 `HELD` | active claim by another session | **do not take it.** choose a different name, split the scope, or serialize |
| exit 4 `STALE` | claim exists, TTL expired | still not yours: the holder may be alive and slow. Renew with them, or `takeover` with a reason |
| exit 5 `ALREADY MINE` | this session holds it | keep working; `renew` if the TTL is short |

`no-steal` is the default and is not configurable away: `takeover` requires a `--reason`, refuses an **active**
claim by someone else even with that reason, and records the act in the ledger note. A dead session's stale claim
is the case takeover exists for — and its honest form is "the holder's process is gone and I verified it", not "I
want that name".

The alternatives after a collision, in the order that costs least:

1. **Rename.** `codex/login-page` vs `claude/login-page` — free, and the reason an agent segment in the naming
   convention (`02-naming.md`) pays for itself.
2. **Split the scope.** The claim carries a `note`; if the overlap is a directory, one of you takes the other half.
3. **Serialize.** One session waits, or works on the trunk and merges first; the other rebases onto it.
4. **Escalate to the human.** Two agents fighting over one branch means the *task* was not decomposed. Fix that,
   not the name.

What is never correct: silently `git checkout -B` over the other's branch, force-pushing it away, or deleting the
ref. Those destroy work rather than resolving a claim, and they are the exact actions
[`SKILL.md`](../SKILL.md#boundaries-and-gates) gates behind a confirmation.

### Etiquette for a repo that may be opened by a tool you do not control

- Claim **before** creating. `branch -b` first, `checkout -b` after, is a race you will lose occasionally.
- One branch per session per task; a session holding three unrelated branches is three claims, and each is fine —
  say so in the note.
- Release when the branch is merged, not when the session ends: an unreleased claim with a merged branch is how
  the next agent learns to ignore the ledger.
- `status` at the start of any session in a shared repo. It costs one command and answers "is someone already
  doing this?", which is otherwise answered by duplicating the work.
- Do not trust the absence of a claim as proof of absence of another agent — check
  `git worktree list --porcelain` and the branch's recent commits too.

## C — your own subagents, same process

You are the only writer of coordination state, so do not let workers negotiate with each other:

1. **Allocate before dispatching**: for each worker, pick its branch (and worktree), acquire the claim yourself,
   and put both in the brief. A worker that invents its own branch name has already broken the convention.
2. **Workers never switch branches.** The brief says: you are on `<branch>`, in `<path>`; do not `checkout`,
   `switch`, `stash`, or `reset --hard`; if the tree looks wrong, report it — it may be someone else's.
   (This is the same discipline `commit` enforces when it re-checks `git status` before staging.)
3. **One integrator.** Only you merge. Workers report their branch and the outcome; you integrate in dependency
   order (`01-strategies.md#integrating-parallel-work`), then release each claim as it lands.
4. **Isolation where the harness supports it.** This CLI's agent tool accepts `isolation: worktree`, which is
   exactly the pattern above, provisioned for you. Where no such option exists, do it by hand with
   `git worktree add -B` per worker. Same-process does not mean same-working-tree.
5. **Do not let a worker write the ledger.** `acquire --role <worker-name>` by the parent keeps a single writer;
   a worker appending to a shared file is situation B behaviour with extra steps.

## What about the permanent case

Claims are **session state**: they answer "who holds this branch right now", they expire, and they are invisible
to a fresh clone until someone looks. A lifecycle strategy is the opposite — names, trunk, merge point,
lifetime, the fix rule, and where agents must claim — and it belongs in `AGENTS.md`, not in
`.git/agent-branch` ([`05-permanent-policy.md`](05-permanent-policy.md)). When the user asks for "a fixed
permanent branches strategy for the whole project lifecycle", write the policy file and let the claim stay what
it is: the ephemeral ledger underneath it.
