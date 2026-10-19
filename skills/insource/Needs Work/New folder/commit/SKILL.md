---
name: commit
description: Writes professional atomic Conventional Commits by analyzing staged or unstaged changes. Use when the user asks to commit, write a commit message, create commits, stage and commit, or after completing code changes that need committing. Supports context-aware mode (skip diff if work is already understood) and always splits mixed changes into separate type-scoped commits.
---

# Commit

Produce clean, atomic Conventional Commits. Never create one bulk commit that mixes unrelated concerns.

## Decision — Context vs Diff

1. **Context-aware mode** (preferred when possible)  
   If the conversation already contains a clear understanding of the work just completed (what was added, fixed, refactored, and why), do **not** re-read the full diff. Use that knowledge directly to plan and write the commits.

2. **Diff mode** (fallback)  
   If the work is unknown, ambiguous, or the user simply says "commit", inspect the working tree:
   - `git status`
   - `git diff --stat` (and `git diff --cached --stat` if anything is staged)
   - For large changes, sample key files with `git diff -- <path>` or `git diff --cached -- <path>`
   Never dump a multi-thousand-line diff into context; summarize by file and concern.

## Core Rules — Atomic Commits

- **One logical concern per commit.** A commit must be a single, self-contained unit of work that leaves the tree in a working state.
- **Never mix types.** A `feat` change, a `fix`, a `refactor`, a `chore`, a `docs` update, etc. each get their own commit.  
  Exception: tests that exclusively cover the change in the same commit may ride along with that `feat`/`fix`/`refactor`.
- **Group related files.** All files that belong to the same logical change go into the same commit. Do not commit file-by-file when they implement one feature.
- **Split when the answer to "Would I explain these separately in review?" is yes.**
- Prefer 2–5 focused commits over one giant commit or dozens of tiny ones.
- Order commits so each intermediate state is sensible (dependencies first).

## Commit Message Format

```
type(scope): description in present simple
```

- **type** (required): `feat` | `fix` | `refactor` | `docs` | `style` | `test` | `chore` | `perf` | `ci` | `build`
- **scope** (recommended): short noun — filename without extension, module name, feature name, or directory. Keep to one or two words. Omit only when the change truly spans the whole project.
- **description**: present-simple imperative, lower-case after the colon, no trailing period, ≤72 characters. State **what** was done and **why** when the why is not obvious from the type.

Examples of good subjects:
- `feat(auth): add OAuth2 login with Google provider`
- `fix(api): prevent duplicate webhook deliveries on retry`
- `refactor(db): extract query builder into standalone module`
- `chore(deps): upgrade React from 18.2 to 19.1`
- `docs(readme): document local environment setup`

Optional body (when useful):
- Explain the motivation or the non-obvious consequence.
- Wrap at 72 characters.
- Footer for `BREAKING CHANGE:` or issue references (`Closes #123`).

## Workflow

1. Decide context vs diff mode.
2. Inventory all changes (staged + unstaged + untracked that belong to the work).
3. Partition into logical groups by concern and type.  
   Typical partitions:
   - pure feature implementation (+ its tests)
   - pure bug fix (+ its regression test)
   - pure refactor
   - pure docs / style / chore / CI
4. For each group:
   - Stage only the relevant paths (`git add <paths>` or `git add -p` when a file contains mixed hunks).
   - Write the Conventional Commit message.
   - Present the planned message (and the files that will be included) to the user.
   - After confirmation, run `git commit`.
5. If the user has not asked for confirmation, still show the planned commits before executing them so the user can stop or adjust.
6. After all commits, show a short summary (`git log --oneline -n <count>`).

## Staging Hygiene

- Never `git add .` or `git add -A` when multiple concerns exist.
- Prefer explicit paths or interactive hunks (`git add -p`).
- Leave unrelated or incomplete work unstaged.
- Scan staged content for secrets, debug leftovers, or generated files that should be ignored.

## Breaking Changes

If a public API is removed, renamed, or its contract changes incompatibly, mark the commit:
- `feat(api)!: ...` or
- Footer `BREAKING CHANGE: <explanation>`

## Anti-patterns (never do)

- One giant commit that says "update code" or "fix stuff".
- Mixing a feature and an unrelated bug fix in the same commit.
- Committing formatting-only changes together with behavior changes.
- Vague subjects ("fix bug", "update", "wip").
- Capitalizing the first letter after the colon or ending the subject with a period.
- Committing without understanding the change (always use context or a minimal diff first).
