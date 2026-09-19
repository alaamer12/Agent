# Deep Master-Slave: Three-Layer Parameterized Agent Hierarchy

A multi-agent orchestration system using **exactly 3 agent types** whose discipline/role personas are defined by task contracts.

## Architecture

```
Great Master (1 agent, Layer 1)
    │
    │ task contract with DISCIPLINE field
    │
    ├── Team Leader (1 agent, Layer 2) — persona: implementer
    │       ├── Member (1 agent, Layer 3) — role: ui-builder
    │       ├── Member (1 agent, Layer 3) — role: services-builder
    │       └── Member (1 agent, Layer 3) — role: core-logic-builder
    │
    ├── Team Leader (1 agent, Layer 2) — persona: security
    │       ├── Member (1 agent, Layer 3) — role: static-analyzer
    │       ├── Member (1 agent, Layer 3) — role: threat-reviewer
    │       └── Member (1 agent, Layer 3) — role: dependency-auditor
    │
    └── Team Leader (1 agent, Layer 2) — persona: tester
            ├── Member (1 agent, Layer 3) — role: unit-tester
            ├── Member (1 agent, Layer 3) — role: integration-tester
            └── Member (1 agent, Layer 3) — role: e2e-tester
```

**Key insight**: Same Team Leader agent, same Member agent — different behavior based on DISCIPLINE/ROLE in the task contract.

## The 3 Agents

| Agent | Layer | Purpose | Model |
|-------|-------|---------|-------|
| `great-master` | 1 | Decompose, orchestrate, verify, sign off | opus |
| `team-leader` | 2 | Adopt discipline persona, recruit, verify, rollup | sonnet |
| `member` | 3 | Adopt role persona, execute, self-verify | sonnet |

## Disciplines & Roles

| Discipline | Team Leader Focus | Member Roles |
|------------|-------------------|--------------|
| implementer | Deliver working code | ui-builder, services-builder, core-logic-builder, devops-builder |
| security | Find vulnerabilities | static-analyzer, threat-reviewer, dependency-auditor, auth-specialist |
| tester | Ensure quality | unit-tester, integration-tester, e2e-tester, performance-tester |
| documentation | Preserve knowledge | api-documenter, user-guide-writer, architecture-documenter |
| custom | Great Master defines | Great Master defines |

## Quick Start

```bash
# Install agents
cp agents/*.md ~/.claude/agents/

# Use the skill
# "Use deep-master-slave to build X with security audit and tests"
```

## Files

```
deep-master-slave-v2/
├── README.md
├── agents/
│   ├── great-master.md      # Layer 1: Orchestrator
│   ├── team-leader.md       # Layer 2: Parameterized by DISCIPLINE
│   └── member.md            # Layer 3: Parameterized by ROLE
└── deep-master-slave-skill/
    ├── SKILL.md
    ├── references/
    │   ├── discipline-personas.md   # All persona definitions
    │   ├── task-contract-template.md
    │   ├── rollup-template.md
    │   └── team-log-protocol.md
    └── scripts/
        ├── validate-contract.py
        └── init-registry.sh
```
