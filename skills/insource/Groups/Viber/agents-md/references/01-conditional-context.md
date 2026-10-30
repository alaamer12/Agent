# Conditional context - versions, channels, and everything else

`AGENTS.md` states **which context is active** and **which files that context requires**. Everything conditional
hangs off that one table. This is the mechanism with the highest failure rate in real rulebooks, because the
negative half is usually missing.

## Version and channel are separate dimensions

Do not collapse them. They differ in what they select:

| Dimension | Selects | Typical values | How the agent detects it |
|---|---|---|---|
| **Version** | which feature set and spec is in force | `v1`, `v2`, `mvp`, `post-mvp` | the steering directory it is told to read; sometimes the branch or a version file |
| **Channel** | which build/release behavior applies | `stable`, `canary`, `dev` | the current branch, a build flag, `Channel=canary` in CI |
| **Other** | whatever else changes the rules | platform (windows/linux), tenant, `experiment/x`, `read-only/ask` mode | branch name, env var, config value, CLI flag |

A project can have V1 docs and V2 docs, each shipping on stable and canary, with different rules per cell. That
is a matrix, and the file must say **which cell is active now** and how to tell.

## The fence has two sides

```md
### Active context
| Dimension | Active | Out of scope - do not read or apply |
| Version   | V1     | v2/ - future features only        |
| Channel   | canary | stable-only rules where they differ |
```

**The excluded column is the rule.** "Read `base/` and `v1/`" leaves the agent to decide whether `v2/` is
harmless background. It is not: an agent that has read future requirements starts implementing them, or worse,
resolves a conflict by picking the newer-sounding document. Write it as a prohibition: *treat excluded-context
files as absent*.

Corresponding duties:

- **Conflicts resolve toward the active context**, never toward "newer" or "more detailed".
- **Reading is not permission.** Seeing a V2 design does not authorize building for V2; if work appears to
  require it, that is a question for the user.
- **Detection is stated.** If the agent must infer the channel from the branch, say so; if from a file, name
  the file. An unstated detection method becomes a wrong guess at 2am.

## The routing table

```md
| File | Purpose |
|---|---|
| .repertoire/.steering/base/structure.md | Directory structure and top-level boundaries |
| .repertoire/.steering/base/tech/README.md | Index of unchanging tech conventions (C#, SQL, errors, UI) |
| .repertoire/.steering/v1/product/README.md | Index of V1 scope, UX, configuration |
```

Rules that keep this table working:

1. **List files, not directories.** "`docs/` is required reading" is 40 documents. One entry per document that
   actually governs decisions, with a one-line purpose.
2. **Indexes are routers.** State that explicitly: *follow the links to the document that answers your
   question; do not treat the index as sufficient.* Without this line, an agent skims a README and concludes
   it has read the spec.
3. **Keep the base/current split.** Base = does not change with version; per-version = the diff. The agent
   reads base always, and only its active version's diff.
4. **Conditional deeper context belongs behind the pointer, not in the table.** "If the task touches the
   pipeline, also read `worker-pool-and-rate-limiter.md`" is a *task-scoped* rule - and per
   [`05`](05-delegation-and-subagents.md), it is exactly the line a master agent must copy into a subagent's
   prompt, because the subagent has no other way to know.

## Design and prototype references use the same mechanism

```md
| Location | Scope | Use for |
| .repertoire/design/mvp/ | active | current shipping UI |
| .repertoire/design/post-mvp/ | excluded from current work | future-scope design only |
```

Plus the discriminating instruction: *before treating a mockup as current spec, confirm which directory it
lives in.* A stale mockup treated as truth produces confidently wrong UI work, which is the most expensive
category of mistake this section can prevent.

## Dead references

A rulebook that points at a file that does not exist trains the agent to ignore the rulebook. After writing,
resolve every relative path (the linter does this). When a path is missing, report it with an owner:

```text
DEAD REFERENCE: docs/UNITS.md does not exist.
  -> the units index is another skill's job; until it exists, section 4's duty cannot be honored.
  -> either generate it, or set section 4 to: "pending - no units index in this project yet".
```

agents-md does not create the target. Creating a stub would turn a visible gap into an invisible one.

## Drift and promotion

When a version or channel changes, the table changes - and the excluded column changes with it. Two habits
keep this honest:

- Put the version/channel table **at the top of section 2**, where a diff shows it.
- Record the update duty as a rule: *"if the active version changes, update section 2 before any other edit."*
  Otherwise the file keeps pointing at a version that shipped a year ago, and every session starts in the
  wrong scope.
