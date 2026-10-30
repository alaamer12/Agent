# Anti-patterns

Each one is a real way these files fail, with the symptom that reveals it and the repair. Review a draft
against this list before showing it; the linter catches the mechanical subset.

| Anti-pattern | Symptom in the file | Why it hurts | Repair |
|---|---|---|---|
| **Encyclopedia drift** | sections explaining how the sync engine / diff algorithm / auth flow works | the file is loaded every session and now competes with the docs it should point to; it will be wrong first | one-line pointer + the duty to read it |
| **Invented defaults** | a package manager, env strategy, or branch rule with no evidence and no marking | the agent enforces a rule the user never chose, and the user cannot tell it apart from one they chose | mark `pending - not assumed`, or `(inferred from X)` |
| **Missing negative scope** | "read `v1/`" with no statement about `v2/` | reading is not permission - the agent adopts future requirements as current truth | the excluded column in the active-context table |
| **Directory as context** | "read everything in `docs/`" | 40 documents, none of them actually consulted; the agent skims and proceeds | list the specific files that govern decisions |
| **Index mistaken for content** | a table pointing only at READMEs, with no "follow the links" rule | the agent reads a summary and believes it read the spec | state that indexes are routers |
| **Block fork** | the subagent block edited by hand, body untouched (or vice versa) | every subagent inherits a different rulebook from the repo | regenerate the block from the body; lint clause-by-clause |
| **Mandated option list** | "use one of: Redux, Zustand, Jotai" with no escape hatch | closes the option space the user did not intend to close | bracket notation or "e.g." - options as examples |
| **Unrouted prohibition** | "do not edit `.env`" with no permitted route | the agent stalls or invents a route | prohibition + route + where the route is documented |
| **Vague obligation** | "write clean code", "be careful", "follow best practices" | unfalsifiable, so unenforced, and it eats the line budget | either a concrete rule or delete it |
| **Silent deletion during merge** | an old rule vanishes with no report line | the rule was probably added after an incident; it comes back as the same incident | the map table, and a report of anything dropped |
| **Dead references** | paths that do not resolve | trains the agent to ignore the file, and the gap stays invisible | run the link check; report missing targets with an owner |
| **Over-reach into other skills' work** | agents-md creates `docs/UNITS.md` or a `.repertoire/agents/` folder to make its pointers valid | a stub implies a capability that does not exist, and the ownership of the real thing gets muddied | report the gap; write only `AGENTS.md` |
| **Unbounded fan-out** | `x->2x->4x->8x` with no worker cap, no failure rule | cost surprises and a silent redo of failed leaves | depth cap + total-worker cap + failure reporting |
| **Parallel-write amnesia** | delegation rules never mention file ownership | two subagents append to the same lockfile/generated file and produce a corrupt merge | disjoint `SCOPE` per agent, sequencing for shared files |
| **Report overwrite by default** | reports keyed by role name with no collision policy | the second run deletes the first run's evidence, and audits lose their trail | decide the filename pattern explicitly in section 10 |
| **500-line creep** | the file grows a new section per incident | compliance dilutes: when everything is mandatory nothing is | move detail out, keep obligations, run the line check |
| **Stale active scope** | file still says `V1` while the project is on `V3` | every session starts in the wrong context, including every subagent | add the update duty as a rule; keep the table diff-visible at the top of section 2 |
| **Harness leakage** | machine- or tool-specific quirks written as project rules | teammates on other setups get nonsense constraints | split project rules (shared file) from machine rules (local file) |
| **Documentation of the agent's own tooling** | long explanations of how the CLI reads instruction files | the agent does not need the mechanism, and the facts change | a pointer, or drop it |
| **Aspirational tooling** | "run the visual regression suite to verify" when no such suite exists | the agent tries to invoke a capability that isn't there and reports a false verification | record only what the project actually has |

## The meta-failure

A rulebook that *looks* complete. Pending items hidden by plausible filler, dead references that read as
routes, a subagent block that disagrees with the body, and no way for the reader to tell which parts were
decided. The honest file is shorter, has a numbered pending list, and reports exactly what it does not yet
know - that is the difference between an artifact and a performance.
