# Worktree playbook

Worktrees are how two checkouts share one object store: each gets its own `HEAD` and index, all of them see the
same commits, refs and (by default) config. For agents this is the difference between "isolated workspace" and
"two processes editing one staging area".

## The commands that matter

```bash
git worktree add -B agent/login ../proj-login main   # new-or-reset branch + directory, based on main
git worktree add ../proj-readme feature/docs         # existing branch in a new directory
git worktree add -d ../scratch HEAD                  # detached HEAD: throwaway experiment, no branch to clean up
git worktree add --lock --reason "usb drive" ../mnt  # prevent pruning of a not-always-mounted tree
git worktree list --porcelain                        # stable machine-readable inventory
git worktree remove ../proj-login                    # only if clean; --force twice if locked
git worktree prune                                   # after a directory was deleted by hand
git worktree repair ../proj-moved                    # after anything was moved without `git worktree move`
```

Rules worth memorizing:

- **One branch, one worktree.** `git worktree add` refuses to check out a branch another worktree already has —
  that refusal is a *feature*: it is git telling you two agents were about to collide. Override with `-f` only
  when you know what you are doing, which is rarely.
- `git worktree add path` **without** `-b/-B/--detach` silently creates a branch named after the directory's last
  component. Convenient, and a convention violation waiting to happen: always pass `-b` (or `-B`).
- `add --lock` beats `add` then `lock`: the docs say it does it *without a race condition*.
- `remove` requires a clean tree; `rm -rf ../proj-login && git worktree prune` is the fast path on big trees —
  `remove` walks and unlinks every file, which on a tree with `node_modules` is minutes of syscalls. Prune or the
  metadata lingers in `.git/worktrees/`.
- Submodules in multiple worktrees are documented as incomplete; **do not** fan agents out over worktrees of a
  superproject with submodules.

## What is shared, what is not

| Shared across worktrees | Per worktree |
|---|---|
| object store (all commits, blobs) | `HEAD`, index, working files |
| `refs/**` — including the `refs/agent/*` claims | `refs/bisect`, `refs/worktree`, `refs/rewritten` |
| `.git/config` (unless `extensions.worktreeConfig` is on) | `config.worktree` when that extension is enabled |
| hooks, `.gitignore`, remotes, stash list | — |

Two consequences for agent work:

1. **A claim written in one worktree is visible in all of them** — that is why coordination uses a ref and the
   common git dir, and why the path must come from `git rev-parse --git-common-dir`, never from a hand-built
   `.git/...` string (a linked worktree's `.git` is a *file* pointing at `.git/worktrees/<name>`).
2. **Nothing that lives in the working tree is isolated by a worktree**: installed dependencies, build output,
   `.env`, local databases, running dev servers. Each needs its own handling.

## Layout

| Layout | Shape | Notes |
|---|---|---|
| sibling | `../proj-login`, `../proj-codex` | outside the repo, so nothing leaks into status; easy to `rm -rf`; the default recommendation |
| nested | `<repo>/.worktrees/login` | everything under one root, which is what agent tools do (Claude Code uses `<repo>/.claude/worktrees/<name>` and names the branch `worktree-<name>`); **must** be gitignored, and the ignore line is itself a repo write — ask, or put it in `.git/info/exclude` (local, untracked) |

Name the directory after the task, not the tool, and let the ledger connect directory → branch → owner.

## Per-worktree setup, and the things that will bite

```bash
git worktree add -B agent/login ../proj-login main
cd ../proj-login
cp ../proj-login/.env.example .env.local         # never copy a real .env with secrets
npm ci                                            # deps are per working tree; disk cost multiplies
```

| Hazard | Symptom | Fix |
|---|---|---|
| Ports | second dev server fails to bind | derive a port from the worktree index: `git worktree list \| grep -n "$PWD"`, then `3000+index`; or make the port come from `.env.local` |
| Database | two agents run migrations against one dev DB and corrupt it | one database/schema per worktree (prefix by branch), or SQLite file per worktree, or a container |
| Docker | name collisions | compose `-p <branch>` project prefix, or unique container names |
| Build caches | monorepo caches (Nx, Bazel, Turbopack, Vite) written by two builds at once | per-worktree cache dirs, or accept slower and serialize the builds |
| Disk | N × working tree, N × `node_modules`, N × `dist` — reported at ~10 GB in 20 minutes on a 2 GB repo with auto-created worktrees | cap concurrency (8–10 worktrees is where overhead beats the gain), delete after merge, symlink/pnpm store where possible |
| Config | `core.sparseCheckout`, `core.worktree`, `core.bare` leaking to all worktrees | enable `extensions.worktreeConfig` and set them with `git config --worktree` |
| Lint/format hooks | a hook in the main tree is "missing" in a worktree | hooks are shared (they live in the common dir); that is usually what you want — say so if it surprises someone |

## Cleanup discipline

```bash
git -C ../proj-login status --porcelain          # anything uncommitted before teardown?
git -C ../proj-login log origin/main..HEAD --oneline
git switch main && git merge agent/login        # or the integration order in 01-strategies.md
git worktree remove ../proj-login && git branch -d agent/login
python <skill-dir>/scripts/branch_claim.py release --branch agent/login
git worktree prune
```

Order matters: **integrate → remove worktree → delete branch → release the claim → prune.** Releasing first
would let another session claim a branch that still has unmerged work in it.

An orphaned `refs/agent/*` with no live session is the residue of a crash; `branch_claim.py status` prints them.
Clear them with the release command, not by deleting refs by hand — the ledger and the ref should agree on the
way out, exactly as they did on the way in.
