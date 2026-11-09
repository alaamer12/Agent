# Session walkthroughs

Three entries, one pipeline. Real shapes of what the user types and what gets written.

## 1. Statement mode - `/personalize that i like bun and bunx`

Read the global file first: it has no package-manager line. Nothing to refine, nothing to
replace. Distill:

```markdown
- **JS tooling:** `bun`/`bunx` always; never `npm`/`npx` - unless the repo's config names another
  manager or the user orders otherwise in the current session.
```

Append under `## Working preferences`. Report: the line, the section, one precedence reminder.
No interview - the statement was complete, and re-asking "are you sure?" for a tool the user just
named is the idiot-agent shape this skill exists to remove.

## 2. Bare mode - `/personalize`

Ask ONE question: "What do you want to personalize?" - with the current lines listed under it:

```text
Current global preferences:
- Do not run typecheck by default ...
- Other agents may be editing the same working tree ...

Add a new one, or amend one of these?
```

Answer: "amend the first - typecheck never, even at the end, I run it myself". Refine the
existing line in place (it is the same fact, now sharper); do NOT add a second typecheck line.
Report the before/after of the one edited line.

## 3. Promotion mode - `/personalize the section "Execution and Tool Usage" in current AGENTS.md into global AGENTS.md`

Read the project section; sort every line:

| Project line | Verdict | Destination |
|---|---|---|
| "Prefer cmd; PowerShell hangs" | personal truth wearing project clothes (it is the machine/user, not the code) | global line, with its exception boundary |
| "`bun` only; other managers rewrite the lockfile" | personal default | global line |
| "work lands on `beta`" | project decision | stays - stated in the report |
| "scratch scripts under `scratch/`, delete after" | project layout choice | stays |

Default is COPY: the project file is not touched unless the user said "move" - and then the
promoted lines are deleted from the project file in the same change, so exactly one owner per
fact remains. If a promoted line would contradict an existing global line, stop and ask which
one the user actually lives by; promotion never silently wins a fight between two files.
