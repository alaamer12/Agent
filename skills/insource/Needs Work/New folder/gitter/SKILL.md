---
name: gitter
description: Structures git workflow practices. Use when making any code change, committing, branching, resolving conflicts, splitting uncommitted work into atomic commits, opening or reviewing a PR, pushing, organizing parallel streams, cutting a release, choosing a semantic version bump, tagging, or writing a changelog.
metadata:
  original: "addyosmani/agent-skills: Production-grade engineering skills for AI coding agents."
---

# Gitter

Git is the safety net. Treat commits as save points, branches as sandboxes, and history as documentation. With agents generating code at high speed, disciplined version control keeps changes manageable, reviewable, and reversible.

## When to Use

Always. Every code change flows through git.

## Core Principles

### Trunk-Based Development (Recommended)

Keep `main` always deployable. Work in short-lived feature branches that merge back within 1–3 days. Long-lived branches accumulate merge risk. Prefer feature flags over long-lived branches for incomplete work. Release branches are acceptable when stabilizing a release while main continues.

```
main ──●──●──●──●──●──●──●──●──●──  (always deployable)
        ╲      ╱  ╲    ╱
         ●──●─╱    ●──╱    ← short-lived feature branches (1-3 days)
```

### 1. Commit Early, Commit Often

Each successful increment gets its own commit. Pattern: Implement slice → Test → Verify → Commit → Next slice. Never accumulate large uncommitted changes.

### 2. Atomic Commits

Each commit does one logical thing. See `references/commit-discipline.md`.

### 3. Descriptive Messages

Messages explain the *why*, not just the *what*. Format: `<type>: <short description>` with optional body. Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`. Full guidance in `references/commit-discipline.md`.

### 4. Keep Concerns Separate

Do not mix formatting with behavior changes, or refactors with features. Separate commits (and ideally separate PRs). Small cleanups may ride along at reviewer discretion.

### 5. Size Your Changes

Target ~100 lines per commit/PR. Over ~1000 lines → split. Details in `references/commit-discipline.md`.

## Branching

Branch from `main`. Name: `feature/`, `fix/`, `chore/`, `refactor/` + short description. Keep short-lived, delete after merge. Full rules and worktree workflow for parallel agents: `references/branching-and-worktrees.md`.

## The Save Point Pattern

```
Agent starts work
    │
    ├── Makes a change
    │   ├── Test passes? → Commit → Continue
    │   └── Test fails? → Revert to last commit → Investigate
    │
    └── Feature complete → Clean incremental history
```

Never lose more than one increment. `git reset --hard HEAD` returns to the last known-good state.

## Change Summaries

After any modification provide:

```
CHANGES MADE:
- path: what changed

THINGS I DIDN'T TOUCH (intentionally):
- path: reason out of scope

POTENTIAL CONCERNS:
- any assumptions or side-effects worth flagging
```

## Pre-Commit Hygiene & Generated Files

Before every commit: review staged diff, scan for secrets, run tests/lint/types. Details and generated-file policy: `references/hygiene-and-debugging.md`.

## Release & Versioning

For anything with consumers use semantic versioning, annotated tags, and a human-readable changelog. Full contract: `references/release-and-versioning.md`.

## Checklists

Common rationalizations, red flags, and verification lists live in `references/checklists.md`. Load them when reviewing a commit or release.

## References

- `references/commit-discipline.md` — atomic commits, message format, concern separation, sizing
- `references/branching-and-worktrees.md` — branch rules, naming, git worktrees for parallel agents
- `references/release-and-versioning.md` — semver, tagging, changelogs
- `references/hygiene-and-debugging.md` — pre-commit checks, generated files, bisect/blame recipes
- `references/checklists.md` — rationalizations, red flags, verification
