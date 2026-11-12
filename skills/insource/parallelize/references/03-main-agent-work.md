# What the main agent keeps

The main agent is the most capable context in the run: it holds the whole plan, the user's intent, and every slice's boundaries. Delegating that away to save an hour costs more than it saves. The main keeps the work where a mistake is expensive or invisible to a slice's own checks.

## Work that stays with the main

| Kind | Examples | Why it cannot be delegated |
|---|---|---|
| Architecture and interfaces | module boundaries, type/API contracts, data shapes shared by two slices | One decision constrains several slices; two agents deciding means two answers |
| Security-sensitive code | auth, permissions, secrets handling, payment paths, input trust boundaries | A wrong slice may pass its own tests and still be exploitable |
| Destructive operations | deletes, migrations, history rewrites, mass renames | Reversible only with effort; blast radius is the whole repo |
| Shared files | lockfiles, indexes, config, generated registries | Every agent touching them collides |
| Final integration | merge, conflict resolution, cross-slice cleanup | Requires the whole picture at once |
| Judgment calls | trade-offs the user has not decided | Silence is not agreement; a subagent must never decide for the user |

## Work that goes to subagents

- Independent files or modules with a settled interface.
- Mechanical but voluminous work: repeat one proven pattern across N files, write tests for one module, port one component.
- Investigation with a narrow question and a clear output contract.
- Anything whose failure is cheap to detect and re-run.

## Working alongside the waves

The main is not idle between launches:

1. **Before the wave:** settle interfaces, shared files, and the snapshot. This is the work only it can do, and it unblocks everything else.
2. **During the wave:** do its own slice — the sensitive work — with the same discipline as any slice: owned paths, done-when, verification.
3. **Between waves:** integrate the previous wave in dependency order, adjust the next wave's plan with what was learned, then launch.
4. **At the end:** run the cross-slice review and the final report.

If the harness blocks the main while a wave runs, front-load the sensitive work before spawning, or shrink the wave so the main's slice fits the gap.

## Never hand these away

- The decision the user has not made. A subagent sees a fragment; ask the user or decide explicitly, and record it.
- The definition of done. If the main cannot state it, no brief can.
- The review of another slice's correctness. A subagent can run checks; only the main can judge whether the slice did what the plan needed.

## The cost of doing it right

Keeping the sensitive work means the main finishes its slice later than some subagents. That is the point: the sequence is "the hard part is done well", not "everything ends at the same time". Report the main's slice in the final summary so the user can see what was not delegated.
