# Scope and modes

## Contents
- Reading the request
- Mode rules in detail
- Conflicts and edge cases
- Where to write

## Reading the request

Treat the scope as **user specified** (Mode A) when the request names any of: a specific pattern ("unnecessary casts", "duplicated business rules"), a layer or area ("anti-patterns in the payment integration"), or a concern ("things that make linters pass without fixing the problem"). A focused request stays focused. Do not turn "check type suppressions" into a full-project audit; at most mention in one line that you noticed something outside scope, and offer to cover it.

Treat it as **undefined** when the request is general ("what anti-patterns should we avoid?", "audit this repo for bad patterns", "set up ANTIPATTERN.md") and discovery finds nothing.

## Mode rules in detail

**Mode A, user specified.** Investigate the requested scope. Existing docs, if any, are context and the place to write results. No `/inquire` round-trip is needed because the user already decided the scope. If a named pattern is ambiguous in a way that changes the investigation, ask one short question in chat.

**Mode B, existing documentation.** Read every spec file and anti-pattern section that `discover_scope.py` reports. Treat them as the project's current decisions.
1. Look for evidence of each documented rule: is it being followed, violated, or untestable as written?
2. Look for gaps only where the evidence is concrete.
3. Report violations and gaps in chat. Do not silently edit or reorder existing rules. Add proposed rules to the document only after the user agrees, or when the user asked you to update it.

**Mode C, undefined.** Full path: research, investigate, `/inquire`, report, spec. Nothing is written into project docs until the user has chosen.

## Conflicts and edge cases

| Case | Handling |
|---|---|
| User scope and existing docs disagree | User scope wins for what to investigate. Existing docs remain the write target. |
| Several `ANTIPATTERN.md` files (monorepo) | Treat each as scoped to its directory. Add to the nearest one. Never create a root file that competes with package-level files. |
| Anti-pattern text lives inside AGENTS.md / CLAUDE.md / CONTRIBUTING.md | Update that section instead of creating `ANTIPATTERN.md`. |
| Existing doc is stale or contradicts the code | Report the contradiction. Do not rewrite history. Propose the correction. |
| Only a lint config or ADR addresses the topic | Counts as evidence of intent, not as an anti-pattern doc. Stay in Mode C but skip questions those files already settle. |
| Very large repo | Ask the user (or infer from the request) which package or service to cover. State the limitation in the methodology. If the whole tree genuinely must be covered, split it into **non-overlapping, read-only** passes — by package, component, or concern — and say plainly that a sampled architecture review is not exhaustive coverage. |
| Empty or tiny project | Say so. Report few findings rather than inventing some. |

## Splitting a large audit (optional)

When the tree is genuinely too big to trace in one pass, delegate **bounded, read-only** investigations — one
package, layer, or concern each — and consolidate yourself:

- Give each worker a non-overlapping scope, the candidate list it may test, and the fields to return: name,
  evidence location, measured versus interpreted, impact, confidence, caveats, source.
- Prohibit edits and prohibit final inclusion decisions. A worker proposes; the main pass decides.
- Re-open every proposed finding against the current files before it enters the report. A worker's conclusion is a
  lead, never accepted evidence.
- Merge candidates that share one cause or one remediation into a single finding, keeping the strongest evidence.
- If a `subagent` skill exists in this environment, read and follow it before delegating.

## Where to write

1. The existing anti-pattern document or section, if there is one.
2. Otherwise `ANTIPATTERN.md` at the root of the analyzed project (or package, in a monorepo).
3. In Mode C, the HTML report goes wherever the `/inquire` workflow places its output. Do not put a second copy of the spec in the repo.
