# Keeping the rulebook current

`AGENTS.md` is not a document you write once. It is the envelope around the agent, and the envelope changes
whenever the project's rules change — so the file is updated **in the same change as the decision**, or the
next session starts with a wrong instruction that reads like an authoritative one.

This is the difference between the rulebook and the docs. Technical detail goes in docs and is referenced; a
*rule* change goes here, immediately.

## The duty, stated as the file should state it

> Every session that changes a project rule updates this file in the same change. Not a follow-up, not next
> sprint, not "I'll do it after the release".

Pair it with a review marker a later agent can check:

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
| A units index now exists (or moved) | **yes** — section 2 |
| A new design/prototype directory, or scope moved from MVP to post-MVP | **yes** — section 4 |
| The shell, package manager, or command-chaining restriction changed | **yes** — section 3 |
| Environment strategy changed (new schema layer, new secret provider, new generation step) | **yes** — section 3 |
| Debug permissions changed (new environment is inspectable, new tool available) | **yes** — section 3 |
| Startup steps changed | **yes** — section 5 |
| Delegation rules changed | **yes** — section 6, **and regenerate the pasteable block** |
| A dependency/local-environment rule changed, or a global install became an allowed exception | **yes** — section 8, exception and rule in one place |
| An authority setting changed (ask-per-session vs fixed), or a grant was given/revoked | **yes** — section 9, with its reason and scope |
| A version-control rule changed (the VCS named, a tier, parked-work policy, change identity) | **yes** — section 12, **and regenerate the block's VCS clause**; the `commit`/`branch` skills read this section before asking anything about authorship |
| The user changed how they want to be asked (Exact/Broad/both, the named Exact list, the pre-anonymous rule), or the decision-record convention moved (docs folder renamed, ADR numbering adopted) | **yes** — section 13 |
| A golden rule was added, retired, or reworded | **yes** — section 14, **and regenerate the block's GOLDEN clause**; the loudest change in the repo |
| A named review task changed (routine, docs budgets, table list) | **yes** — section 15 |
| A version policy changed (pattern, bump rule or who, a new declaration site, an attachment, dual-versioning) | **yes** — section 3, **and the versioning doc's procedure in the same change** |
| The docs root moved or was declared for the first time | **yes** — section 2's path and every pointer that hangs from it |
| Verification contradicted a training/prior belief during any task | **yes** — section 16: append the dated bullet (believed / actual / proven) in the same change; its paragraph stays fixed text |
| A finished task revealed a step that should have been mandatory (or a ritual proved noise) | **yes** — section 17: add/remove that phase's bullet; guide paragraph fixed, bullets grow for the life of the project |
| The voice changes (the chosen register, the user's own register, or how it reflects into written docs) | **yes** — section 18, **and regenerate the block's VOICE clause**; a voice that only governs chat while reports drift back to default is half a voice |
| A sync block's meaning changed on one side, a home moved (line anchor stale), or a new multi-home content was discovered | **yes** — section 19: EVERY row of that block's table in the same change, anchors re-set; the audit finding an unlisted duplicate is a defect report, not a note - and if it is the version number's homes, section 3's pointer is what routes it here |
| A skill gains (or loses) a project-specific usage note | **yes** — section 10, one row: condition + pointer |
| A path became private, or a privacy rule changed (hidden tool ⇒ its outputs, binary ⇒ install note elsewhere) | **yes** — section 7, **and the `.gitignore` entry in the same change**; if the path was already tracked, ask the user before clearing the cache — never silently |
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
| Dead references | agents stop honoring mandatory reading | read the links back at review time; report, do not stub |
| Block/body divergence | subagents follow rules the repo abandoned | regenerate 10.4 whenever 1-9, 11, or 16 change; compare clause topics against the sections |
| Rulebook creep | the file absorbs technical docs and gets hard to scan | the "does it change what the agent must do?" test; propose a split (conventionally `rules/...`) or keep it inline if that is the user's choice - size is advisory |
| Unowned updates | everyone assumes someone else keeps it current | make the duty explicit in section 11, and in the delegation contract for subagents |
| Ignored-in-name privacy | section 7 declares paths private while they stay committed or still tracked | a privacy edit updates `.gitignore` in the same change; re-check both duties in the section; the already-tracked case raises the ask-before-cache-clear question |

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
