---
name: deep-master-slave
description: Three-layer hierarchical multi-agent orchestration with parameterized agents. MUST BE USED for complex tasks spanning multiple disciplines. Uses exactly 3 agent types (great-master, team-leader, member) whose discipline/role personas are defined by task contracts, not separate agent files. Examples: "Build a full-stack feature with security audit and tests", "Orchestrate parallel implementation and review teams"
---

# Deep Master-Slave: Three-Layer Parameterized Hierarchy

Exactly **3 agent types** whose behavior is defined by **task contracts**, not separate files:

```
┌─────────────────────────────────────────┐
│         GREAT MASTER (1 agent)          │
│    Orchestrates. Owns final sign-off.   │
└─────────────────┬───────────────────────┘
                  │ task contract (with DISCIPLINE)
      ┌───────────┼───────────┐
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│TEAM      │ │TEAM      │ │TEAM      │
│LEADER    │ │LEADER    │ │LEADER    │
│(1 agent, │ │(1 agent, │ │(1 agent, │
│persona = │ │persona = │ │persona = │
│implementer│ │security │ │tester   │
└─────┬────┘ └─────┬────┘ └─────┬────┘
      │ task contract (with ROLE)
   ┌──┴──┐      ┌──┴──┐      ┌──┴──┐
   ▼     ▼      ▼     ▼      ▼     ▼
┌────┐┌────┐  ┌────┐┌────┐  ┌────┐┌────┐
│MEM ││MEM │  │MEM ││MEM │  │MEM ││MEM │
│(1  ││(1  │  │(1  ││(1  │  │(1  ││(1  │
│agent,    │  │agent,    │  │agent,    │
│role=ui   │  │role=SAST │  │role=unit │
└────┘└────┘  └────┘└────┘  └────┘└────┘
```

**Key insight**: One Team Leader agent, one Member agent — their discipline/role comes from the task contract's `DISCIPLINE` and `ROLE` fields.

## The Three Agents

| Agent | Layer | Purpose | Model |
|-------|-------|---------|-------|
| `great-master` | 1 | Decompose, orchestrate, verify, sign off | opus |
| `team-leader` | 2 | Adopt discipline persona, recruit members, verify, rollup | sonnet |
| `member` | 3 | Adopt role persona, execute, self-verify | sonnet |

## Task Contract Schema

Every delegation uses this fixed structure:

```
GOAL: [One clear sentence]
SCOPE: [Files/directories allowed]
OUT OF SCOPE: [Explicit exclusions]
ACCEPTANCE CRITERIA: [Verifiable conditions]
EXPECTED DELIVERABLE: [Output format]
DISCIPLINE: [For Team Leaders: implementer|security|tester|documentation|custom]
ROLE: [For Members: ui-builder|static-analyzer|unit-tester|etc.]
ISSUED BY: [agent name]
ASSIGNED TO: [agent name]
TASK ID: [XXX-NNN]
```

**Rule**: Every section present at every hop. Nothing dropped, only narrowed.

## Discipline → Member Role Mapping

| Discipline | Team Leader Persona | Member Roles |
|------------|---------------------|--------------|
| implementer | Deliver working code | ui-builder, services-builder, core-logic-builder, devops-builder |
| security | Find vulnerabilities | static-analyzer, threat-reviewer, dependency-auditor, auth-specialist |
| tester | Ensure quality | unit-tester, integration-tester, e2e-tester, performance-tester |
| documentation | Preserve knowledge | api-documenter, user-guide-writer, architecture-documenter |
| custom | Great Master defines | Great Master defines |

## Verification Rollup

Every non-Member returns:

```
DELIVERABLE: [Summary]
VERIFICATION EVIDENCE:
  Children reviewed: [IDs]
  Method: [How verified]
  Issues found and resolved: [List]
  Outstanding concerns: [List or "none"]
TASK ID: [ID]
PRODUCED BY: [agent]
```

## Team-Log

Append-only horizontal log between peer Team Leaders. Informational only — never bypasses verification chain.

## Files

- `SKILL.md` — This file
- `references/task-contract-template.md` — Copy-paste contract format
- `references/discipline-personas.md` — Full persona definitions for all disciplines/roles
- `references/rollup-template.md` — Verification format
- `references/team-log-protocol.md` — Horizontal communication
- `scripts/validate-contract.py` — Contract validator
