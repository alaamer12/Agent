# Naming

Nothing about a branch name is standard, so the convention is a decision — and once decided it becomes
load-bearing: CI path filters, protection rules, `Closes #` semantics and other agents' collision checks all read
it. `scripts/branch_name.py` validates and suggests; this file explains what to choose and why.

## What a name has to survive

| Constraint | Consequence |
|---|---|
| Refs are files under `.git/refs/heads/` | `Feature/x` and `feature/x` are **the same file** on macOS/Windows and two different branches on Linux → names must be lowercase or the repo behaves differently per clone |
| `/` separates hierarchy | `feature/login` and `feature/login/deep` can both exist; a ref cannot be both a file and a directory, so `a/b` blocks creating `a/b/c` as a branch |
| Shells, pathspecs, `sed`, URLs | no spaces, no `~`, no `^`, no `:`, no `?`, no `*`, no `\`, no `@{`, no trailing `.lock` |
| Humans reading `git log --oneline` and tab-completion | short, but not cryptic: a name is a sentence fragment, not a hash |
| Tooling that matches on prefixes (`release/*`) | one spelling, consistently typed |

## Schemes worth offering

| Scheme | Shape | Good when | Cost |
|---|---|---|---|
| **Conventional Branch** | `<type>/<description>` — `feature/add-login-page`, `fix/header-bug`, `hotfix/security-patch`, `release/v1.2.0`, `chore/upgrade-node-v20.11` | anything with CI that wants to key on intent; multi-person or multi-agent work | a type vocabulary to maintain; aliases (`feat`, `fix`) must be pinned to one |
| **Issue-first** | `1234-add-login-page` | the tracker is the spine; branch ↔ ticket is the only mapping that matters | the name says nothing without the tracker |
| **Owner-first** | `amro/feature/login-page`, `codex/fix-parser` | several people or agents in one repo — collisions become impossible by construction | ownership drifts when work is handed over |
| **Git-flow-ish** | `feature/`, `bugfix/`, `hotfix/`, `release/`, `develop` | a repo already shaped that way | implies the whole model, including `develop`, which is usually a liability now |
| **Flat** | `add-login-page` | solo, few branches, no CI matching | no signal about kind, no collision protection |

Recommend from the user's situation, not from fame. Solo + local merge → flat or Conventional Branch, and say
that the type prefix buys automation they may not need. Several agents → the prefix **plus** an agent segment is
what makes a collision self-explanatory.

## The type vocabulary (Conventional Branch v1.1.0)

Purpose types: `feature` (alias `feat`), `bugfix` (alias `fix`), `hotfix`, `release`, `chore`.
AI-source types: `ai` (vendor-neutral), `claude`, `codex`, `copilot`, `cursor`.
Trunk names — `main`, `master`, `develop` — take no prefix.

Description grammar: lowercase alphanumerics; words joined by single hyphens; dots allowed inside a segment
(`v1.2.0`), never leading, trailing, doubled, or touching a hyphen. Underscores are not part of the spec.

Team extensions are legitimate — `experiment/`, `dependabot/`, `wip/` — but must be **declared** (in the policy
block and in the validator), because "the spec allows what my tool allows" is how two validators start disagreeing
about the same branch.

## Agent identity in the name — the authorship decision

This is question 5 of the interview; it is a choice with three real settings, not a default:

| Setting | Shape | Use it when |
|---|---|---|
| **No agent segment** | `feature/login-page` | the human is the accountable author end to end; a tool is a tool, like an IDE. Provenance then lives (or does not live) in the commit trailer only |
| **Spec type** | `ai/login-page`, or `claude/fix-header-bug` | you want CI and reviewers to see machine-authored work at a glance, using a registered prefix |
| **Owner-style segment** | `qoder-qwen/feature/login-page`, `codex/fix-parser` | several agents run concurrently and the name must say **who is holding this**, which is also the cheapest collision avoidance there is |

Whatever is chosen: one spelling everywhere, checked by `branch_name.py`, recorded in `AGENTS.md`. Mixed usage is
worse than any single choice, because the pattern stops being readable.

Pair it with the commit side of the same decision (co-author trailer or none — see
[`commit`'s trailers reference](../../commit/references/05-trailers-and-footers.md)); an agent whose name appears in
the branch but never in the commit history, or the reverse, is an inconsistency the next reader has to debug.

## Validating and migrating

```bash
python <skill-dir>/scripts/branch_name.py check feature/login-page --convention conventional
python <skill-dir>/scripts/branch_name.py check fix/x --convention regex --regex '^(main|feature/[a-z0-9.-]+)$'
python <skill-dir>/scripts/branch_name.py suggest add login page --type feature --issue 1234
```

The validator reports **why** a name is rejected (uppercase, doubled hyphen, undeclared type), because a bare
"invalid" teaches nothing. It never installs a hook, a CI job, or a git config — enforcement is a separate,
asked-for change (`05-permanent-policy.md` says what to propose if the user wants it).

Migrating a convention already in use:

1. New branches follow the new pattern immediately; old ones keep their names until they die naturally. Renaming
   live branches mid-flight breaks the people and agents that have them checked out.
2. Publish both patterns in the policy block for the transition, with the cut-over date.
3. Bots are part of the convention: Renovate, Dependabot and release tooling all name branches; configure them
   to match, or the validator will fail the bot and the team will turn it off.
