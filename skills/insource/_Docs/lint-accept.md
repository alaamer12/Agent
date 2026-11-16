## Accepting lint findings (`lint-accept`)

Sometimes a skill intentionally breaks a lint rule and should stay that way — for example a genuine hybrid that is part Battery-Skill and part Meta-Skill. Rather than weakening the rule for every skill, mark the exception on that skill with a `lint-accept` frontmatter mapping of **rule id → reason**:

```yaml
---
name: architecture
version: 2.0.0
specialized: none
lint-accept:
  mixed-composition: "Intentional hybrid: accessibility/display/plugin are independent pillars; the other five are internal methods. Keep as-is."
description: ...
---
```

The reason is required and non-empty: an acceptance is a recorded decision, not a silent mute. `lint-accept` is a nested mapping, so it needs PyYAML (the same dependency full lint validation already uses).

**Rule ids you can accept:**

| Rule id | Finding it waives |
|---|---|
| `mixed-composition` | Independent sub-skills and internal modules in one parent (the hybrid case) |
| `frontmatter` | Missing / unreadable / invalid YAML frontmatter |
| `version` | Missing or invalid `version` on a non-tracked skill |
| `specialized` | Missing, invalid, multi-value, or non-canonical `specialized` |
| `name` | Missing or invalid `name` |
| `name-mismatch` | `name` does not match the folder name |
| `duplicate-name` | Another registry skill already uses this `name` |
| `description` | Missing description |
| `description-multiline` | Description is not a single line |
| `description-length` | Description over the character limit |
| `skill-length` | `SKILL.md` at or over 200 lines in a skill that has other files ([skill-length.md](skill-length.md)) |
| `argument-hint` | Skill shows commands/modes by structural evidence yet declares no `argument-hint` ([argument-hint.md](argument-hint.md)) |

**Behavior:**

- An accepted finding is removed from the skill-warning count and no longer fails `lint --strict`. It is still shown under `--verbose` in an **accepted findings** table with its reason, and counted in the summary, so the waiver stays auditable.
- Acceptance waives only the named rule, only for that skill. Every other rule still applies.
- A malformed acceptance is itself a warning: an unknown rule id, an empty/missing reason, or a `lint-accept` value that is not a mapping. A typo therefore cannot silently mute nothing.
- Scope is the skill-level metadata/structure findings above. Synchronization issues, version-bump suggestions, and README findings are separate subsystems and are not waivable here.
- `report` and `find` still show the skill's real structure and composition issues; acceptance is a lint decision, not a reclassification.
