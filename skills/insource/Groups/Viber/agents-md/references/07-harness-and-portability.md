# Harness and portability

`AGENTS.md` is a cross-tool convention: an open, vendor-neutral name several agent CLIs and editors read from
a repository root or a directory (closest file wins in that scheme). But the surrounding details differ per
harness, and the file must not encode them as if they were universal.

**Working rule for agents-md:** record what the *project* does. Where a fact belongs to the tool, phrase it as a
pointer or a hedge, and verify it in the harness actually in use. Tool internals change between versions; a
rulebook that documents them becomes quietly wrong and the agent cannot tell.

## Discover before writing

```bash
# which instruction files exist, and what the project already treats as authoritative
ls AGENTS.md AGENTS.local.md CLAUDE.md QODER.md .cursorrules 2>/dev/null
ls .cursor/rules .claude .junie .qoder 2>/dev/null
# skill and command roots per harness (do not assume .cursor)
find . -maxdepth 3 -type d \( -name skills -o -name commands -o -name agents \) 2>/dev/null | head
# is the instruction file referenced from docs, CI, or a README?
grep -rIl "AGENTS.md" --exclude-dir=.git . 2>/dev/null | head
```

If more than one instruction file exists, decide with the user which is authoritative and make the others
pointers - two rulebooks is how contradictions get introduced, and the agent has no way to pick.

## Project rules vs machine rules

The split that keeps a shared file honest:

| Belongs in the shared `AGENTS.md` | Belongs in a local/machine file (or in the user's global instructions) |
|---|---|
| Branch and version policy | "PowerShell hangs *on my box*" if that is a local environment quirk |
| Package manager, env strategy, units duty | personal editor or shell preferences |
| Debug permissions | local paths, tool installs, machine-specific ports |
| Delegation contract | anything a teammate on Linux would find wrong |

Some harnesses support a local override file (this environment's own conventions include one); others do not.
When unsure, write the rule conditionally and state the scope: *"if your shell hangs on X, do Y"* rather than
asserting a project-wide rule about one laptop.

## When the user keeps global personal preferences

Some users maintain a personal instruction file loaded into every project (the `personalize` skill owns those
lines and the precedence ladder - brief plus pointer, do not restate it here). The project rulebook's duty:
**the project inherits and respects the user's preferences; where it must differ, the override is written
here explicitly** - "This project overrides a global preference: [what], because [why]" - so no agent ever
faces a silent contradiction between the two files, which is the one shape neither file gets trusted.

## What not to encode as fact

- Which files the tool auto-loads, precedence order, or memory locations - verify, or describe the *duty*
  ("read this file first") which works regardless of the mechanism.
- Slash-command syntax and skill invocation forms beyond the project's own documented ones. If the project
  defines commands (e.g. a `.cursor/commands/` file), reference it by path; do not transcribe its syntax.
- Marker formats owned by other tools. If a managed block exists, preserve it verbatim and say who owns it -
  do not document how it is generated.
- Line-count or token budgets of the harness's context. `AGENTS.md`'s own ~500-line budget is a project choice
  that happens to align with attention, not a platform limit.

## Skills that touch the same file

Expect cohabitation and define the boundary in the report rather than silently overwriting:

| Other skill | What it owns in `AGENTS.md` | agents-md's duty |
|---|---|---|
| A skill-pinning tool | a managed block between two comment markers | pass the region through verbatim; never edit inside the markers; mention it in the report |
| [`units-md`](../../units-md/SKILL.md) | `UNITS.md` and its generation, incl. the UI builder profile | reference the file and the duty; do not generate or stub the file |
| A subagent-brief skill | the content of one delegation prompt | own the *contract* (section 6) that such prompts must satisfy; do not write briefs |
| A docs/steering skill | the documents section 2 points at | keep pointers accurate; report dead paths for that skill to fix |

The general principle: agents-md writes the rulebook's **structure and obligations**. Every mechanism the
rulebook references is somebody else's implementation, and pretending otherwise produces two files that both
claim to own the same rule.

## Portability check before finishing

1. Every relative path resolves from the repository root, and no absolute or foreign-project path appears.
   (`scripts/agents_lint.py` enforces both.)
2. Nothing depends on a tool-specific loader to make the rules work - each rule is written as an obligation the
   agent performs, so it survives switching harnesses.
3. Machine-specific quirks are scoped as such.
4. The subagent block is self-contained: pasted alone into a prompt with no other context, it still tells a
   subagent what to read, how to run commands, and what to report.
