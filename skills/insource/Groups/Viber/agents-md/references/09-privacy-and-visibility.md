# Privacy and visibility (section 11)

AGENTS.md decides what the agent *does*; the Privacy section decides what the agent *reveals and leaves
visible*. A project's private machinery - the agent skills it runs, the plans and run records they produce,
the binaries it ships - is often exactly what should not reach version control or artifacts that leave the
repo. Undeclared, those things leak by default, because "commit what the task touched" is every agent's
normal behavior.

**Privacy here is visibility policy, not secret management.** Actual secrets belong to section 7. This
section answers: *which paths, and the things generated from them, stay out of the repo and out of
anything that travels?*

## The four duties the section must state

1. **The list.** Which paths are private - skill folders, plan/working directories, run records, scratch
   output, selected binaries - written as paths or patterns, each with a one-clause reason. "No privacy
   restrictions" is a valid entry; silence is not.
2. **The cascade.** Hiding a producer hides its outputs. If the agent skills are private, the folders the
   skills write are private too - `/revoke`'s sanitized copies, `.iwts/` run records, `agents/` reports,
   caches - even though no one typed those paths by hand. When the user declares a tool folder private,
   ask what that tool writes and fold the answer into the same section. The cascade prevents the failure
   mode where a hidden skill happily commits its own output under a fresh path every run.
3. **Binaries: hide the file, keep the need.** A hidden dependency like `tools/pocketbase.exe` must not
   vanish into unavailability: the section records that the binary stays out of the repo **and** where the
   install/obtain instruction lives ("install note in docs/setup.md"). Hidden-but-undocumented binaries are
   how a private rule breaks the next clone.
4. **Sync + the cache question.** `.gitignore` is the mechanism; the section is the intent. Whenever this
   section is written or updated, check each private path against `.gitignore`:

   - missing there → the rule is decoration; say so and add it (or hand the user the line to add);
   - **tracked before being declared private** → ignoring does not untrack. The removals
     (`git rm --cached <path>`, deleting local generated copies of cascaded outputs) are **proposed and
     asked for, never performed silently** - they touch the user's work tree, and agents-md's own "no
     silent deletion" rule extends to cache clearing. State the ask plainly: *"these paths are now private
     but remain in git's cache; clear them? (their working files stay on disk)"*.

## What good looks like

```markdown
## 11. Privacy

- Private paths - never commit, never quote in anything leaving this repo:
  - `skills/` (project agent skills) and everything they write: `.iwts/`, `agents/<run>.md` reports
  - `plans/` working plans and fan-out briefs
  - `tools/pocketbase.exe` - install note lives in `docs/setup.md`; keep the need, not the binary
- Every path above must appear in `.gitignore`; if one is missing there or still tracked, ask the user
  before clearing the cache - never delete silently.
```

## Audit-time behavior

When auditing an existing AGENTS.md: content of a Privacy section moves *within* the section format, never
into other sections; if the project has private machinery but no Privacy section, that is a finding for the
map table and an interview question, not something to fill in with an invented policy. A "pending - not
assumed" line is honest; guessing what the user wants hidden is exactly the invented default agents-md
forbids.

## Subagents inherit nothing - restate the rule

Subagents do not read AGENTS.md by default; the baseline block (section 10) carries a compressed PRIVACY
clause - private paths and the cascade in one line, plus "write your outputs only into those." A subagent
that reports "created `plans/x.md`" about a private path into a public channel is a leak the block clause
exists to prevent.
