# Keeping the rulebook current

`AGENTS.md` is not a document you write once. It is the envelope around the agent, and the envelope changes
whenever the project's rules change — so the file is updated **in the same change as the decision**, or the
next session starts with a wrong instruction that reads like an authoritative one.

This is the difference between the rulebook and the docs. Technical detail goes in docs and is referenced; a
*rule* change goes here, immediately.

## The duty, stated as the file should state it

> Every session that changes a project rule updates this file in the same change. Not a follow-up, not next
> sprint, not "I'll do it after the release".

Pair it with a review marker the linter can check:

```markdown
## 15. Rulebook Maintenance
**Last reviewed:** 2026-10-27
```

## What counts as a project rule (and what does not)

| Changed | Update AGENTS.md? |
|---|---|
| A new channel appeared (`stable` → `stable` + `canary`) | **yes** — section 2 gains a dimension, its active value, and what is excluded |
| A new version line started (`v1` → also `v2`), or `v2` became current | **yes** — the active/excluded fence flips |
| A new mandatory document was created | **yes** — a row with its one-line purpose |
| A document was renamed, moved, merged, or split | **yes** — fix every pointer to it, in the same change that moved the file |
| A document became obsolete | **yes** — remove it or fence it explicitly |
| Branch or promotion policy changed | **yes** — section 3 |
| A units index now exists (or moved) | **yes** — section 4 |
| A new design/prototype directory, or scope moved from MVP to post-MVP | **yes** — section 5 |
| The shell, package manager, or command-chaining restriction changed | **yes** — section 6 |
| Environment strategy changed (new schema layer, new secret provider, new generation step) | **yes** — section 7 |
| Debug permissions changed (new environment is inspectable, new tool available) | **yes** — section 8 |
| Startup steps changed | **yes** — section 9 |
| Delegation rules changed | **yes** — section 10, **and regenerate the pasteable block** |
| A dependency/local-environment rule changed, or a global install became an allowed exception | **yes** — section 12, exception and rule in one place |
| An authority setting changed (ask-per-session vs fixed), or a grant was given/revoked | **yes** — section 13, with its reason and scope |
| A git rule changed (operation tier, stash policy, commit author identity) | **yes** — section 16, **and regenerate the block's GIT clause**; the `commit`/`branch` skills read this section before asking anything about authorship |
| A skill gains (or loses) a project-specific usage note | **yes** — section 14, one row: condition + pointer |
| A path became private, or a privacy rule changed (hidden tool ⇒ its outputs, binary ⇒ install note elsewhere) | **yes** — section 11, **and the `.gitignore` entry in the same change**; if the path was already tracked, ask the user before clearing the cache — never silently |
| A function was renamed inside the product | no — that is the units index / code |
| An architectural decision about the diff engine | no — that is an ADR, referenced from section 2 |
| A dependency was bumped | no — that is history and the lockfile |

The test: **does this change what an agent must read, may do, or must not do?** If yes, it belongs here. If it
changes how the system works, it belongs in a doc and this file keeps the pointer.

## The habit, per session

1. **Read the review date first.** If it is stale relative to what you know about the project, verify the two
   highest-risk lines before doing anything else: the active-scope fence (section 2) and the branch/version
   policy (section 3). Those two are where a stale rulebook actively misleads.
2. **Notice the moment a rule is being made.** It usually arrives as a sentence in a conversation: "from now on
   canary gets the new schema first", "all UI work goes through the units index", "don't touch `.env` anymore,
   use the generator". That sentence is a rule, and it has no home until this file gains it.
3. **Write it in the same change as the decision.** A rule that lives only in chat history is invisible to the
   next session and to every subagent.
4. **Fix pointers when files move.** A rename that leaves a dead reference in section 2 is the most common
   drift, and the most damaging: the agent either skips the document it was required to read, or learns to
   ignore the file.
5. **Report the update** alongside the code change: which section changed and why. It makes the rulebook's
   evolution auditable without turning it into a changelog.

## Drift, with its symptoms

| Drift | Symptom | Prevention |
|---|---|---|
| Stale active scope | the file says V1 while V2 is in development | review date + verify section 2 first each session |
| Missing dimension | a channel exists in practice, not in the file | the decision→section table above |
| Dead references | agents stop honoring mandatory reading | `agents_lint.py` link check; report, do not stub |
| Block/body divergence | subagents follow rules the repo abandoned | regenerate 10.4 whenever 1–9, 11, or 16 change; the linter traces clauses |
| Rulebook creep | the file absorbs technical docs and passes 500 lines | the "does it change what the agent must do?" test; move out, keep a pointer |
| Unowned updates | everyone assumes someone else keeps it current | make the duty explicit in section 15, and in the delegation contract for subagents |
| Ignored-in-name privacy | section 11 declares paths private while they stay committed or still tracked | a privacy edit updates `.gitignore` in the same change; the linter checks both duties in the section; the already-tracked case raises the ask-before-cache-clear question |

## Subagents and maintenance

A subagent cannot edit the parent's rulebook reliably, and should not try. Instead:

- The **main agent** carries the maintenance duty; when it delegates a change that will alter a rule, it says
  so in the brief and applies the update itself after the result lands.
- A **subagent that discovers a stale or missing rule** returns it as a finding in its report — "section 2
  still lists `stable` only; the project has `canary`" — rather than silently working around it or editing the
  file. The parent reconciles.

## What "up to date" does not mean

It does not mean the file is long, exhaustive, or a log. It means: every rule currently in force is written,
every written rule is still true, and every pointer resolves. When a rule retires, delete it — a file that
accumulates obsolete rules is more dangerous than an empty one, because the agent cannot tell which half still
applies.
