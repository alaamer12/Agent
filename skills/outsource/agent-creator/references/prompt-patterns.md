# Agent Prompt Patterns Reference

Advanced patterns for agent system prompt design.

## Table of Contents

1. [Role Definition Patterns](#role-definition-patterns)
2. [Methodology Patterns](#methodology-patterns)
3. [Quality Standards Patterns](#quality-standards-patterns)
4. [Boundary Patterns](#boundary-patterns)
5. [Description Patterns](#description-patterns)
6. [Tool Selection Patterns](#tool-selection-patterns)

---

## Role Definition Patterns

### Expert Role Pattern

```markdown
# [Domain] Specialist

You are an expert [domain] specialist with [key characteristic]. Your mission is to [core objective] while [constraint/approach].
```

**Example:**
```markdown
# Security Analyst

You are an expert security analyst with zero tolerance for vulnerabilities. Your mission is to identify security risks before they reach production while providing actionable remediation guidance.
```

### Persona Pattern

```markdown
# [Role Title]

You are [persona description with key traits]. You [characteristic behavior]. You [approach to work].
```

**Example:**
```markdown
# Devil's Advocate Developer

You are a skeptical senior developer who questions everything. You find the gaps others miss. You ask uncomfortable questions that prevent future problems.
```

### Mission-First Pattern

```markdown
# [Role]

**Mission**: [One-line mission statement]

You [how you accomplish the mission]. Your output [what you deliver].
```

---

## Methodology Patterns

### Numbered Steps Pattern

```markdown
## Process

1. **[Step Name]**: [What to do]
   - [Sub-detail 1]
   - [Sub-detail 2]

2. **[Step Name]**: [What to do]
   - [Sub-detail 1]
   - [Sub-detail 2]
```

### Checklist Pattern

```markdown
## Before [Action]

- [ ] [Check 1]
- [ ] [Check 2]
- [ ] [Check 3]

Only proceed when all checks pass.
```

### Decision Tree Pattern

```markdown
## Approach Selection

**If [condition A]:**
- Use [approach 1]
- Focus on [aspect]

**If [condition B]:**
- Use [approach 2]
- Focus on [different aspect]

**Default:**
- Use [standard approach]
```

### Prioritized List Pattern

```markdown
## Priorities (in order)

1. **[Priority 1]**: [Why this is first]
2. **[Priority 2]**: [Why this is second]
3. **[Priority 3]**: [Why this is third]

Never sacrifice a higher priority for a lower one.
```

---

## Quality Standards Patterns

### Severity Classification

```markdown
## Issue Severity

- **Critical**: [Definition] - Requires immediate action
- **High**: [Definition] - Must fix before release
- **Medium**: [Definition] - Should fix, can defer
- **Low**: [Definition] - Nice to fix, not blocking
```

### Confidence Levels

```markdown
## Confidence Indicators

- **9-10/10**: Definitive conclusion with overwhelming evidence
- **7-8/10**: Strong conclusion with solid supporting evidence
- **5-6/10**: Moderate confidence, needs more investigation
- **<5/10**: Uncertain, presenting possibilities not conclusions
```

### Output Format Specification

```markdown
## Output Format

For each [item]:
- **[Field 1]**: [Format/content]
- **[Field 2]**: [Format/content]
- **[Field 3]**: [Format/content]

Example:
[Concrete example of proper output]
```

### Quality Gates

```markdown
## Quality Gates (ALL Must Pass)

- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

If ANY gate fails, do not proceed. Address the failure first.
```

---

## Boundary Patterns

### Hard Stop Pattern

```markdown
## YOUR ROLE ENDS HERE

**CRITICAL BOUNDARY**: You are strictly a [role]. Once you have [completed action]:

- Your work is COMPLETE
- DO NOT [prohibited action 1]
- DO NOT [prohibited action 2]
- DO NOT [prohibited action 3]

[Other role/agent] handles [out-of-scope actions].
```

### Scope Definition Pattern

```markdown
## Scope

### In Scope
- [Included responsibility 1]
- [Included responsibility 2]

### Out of Scope
- [Excluded responsibility 1] (handled by [X])
- [Excluded responsibility 2] (not needed)

### Gray Areas
- [Ambiguous case]: [How to decide]
```

### Handoff Pattern

```markdown
## Completion & Handoff

When you complete [task]:

1. Summarize [key deliverables]
2. List [items for next agent/user]
3. Note [any concerns or blockers]

Your output will be used by [next consumer] for [purpose].
```

---

## Description Patterns

### Standard Trigger Pattern

```yaml
description: [Role/capability]. MUST BE USED for [specific scenarios]. [Additional context]. Examples: "[trigger 1]", "[trigger 2]"
```

### Proactive Invocation Pattern

```yaml
description: [Role/capability]. Use PROACTIVELY when [automatic trigger conditions]. [What it does]. Examples: "[trigger 1]", "[trigger 2]"
```

### Detailed Example Pattern

```yaml
description: [Role/capability]. [When to use]. Examples: <example>Context: [situation]. user: "[user message]" assistant: "[how assistant responds]"</example>
```

### Negative Trigger Pattern

```yaml
description: [Role/capability]. MUST BE USED for [positive triggers]. NOT for [what it doesn't handle - use X agent instead].
```

---

## Tool Selection Patterns

### Read-Only Agent

```yaml
tools: Glob, Grep, Read, LS
```
Use for: Code review, analysis, exploration, documentation lookup

### Research Agent

```yaml
tools: Glob, Grep, Read, LS, WebFetch, WebSearch
```
Use for: Investigation, research, gathering context, documentation

### Planning Agent

```yaml
tools: Glob, Grep, Read, LS, Write, Edit, TodoWrite
```
Use for: Creating plans, documentation, specifications (no execution)

### Analysis + Documentation Agent

```yaml
tools: Glob, Grep, Read, LS, Write, Edit, WebFetch, WebSearch, TodoWrite
```
Use for: Research and documentation, no code execution

### Full Implementation Agent

```yaml
tools: Glob, Grep, Read, LS, Write, Edit, Bash, Task, TodoWrite, Skill
```
Use for: Full implementation capabilities (use sparingly)

### Orchestrator Agent

```yaml
tools: Glob, Grep, Read, LS, Task, TodoWrite
```
Use for: Coordinating other agents, minimal direct action

---

## Anti-Patterns to Avoid

### Vague Role

**Bad:**
```markdown
# Helper Agent
You help with things.
```

**Good:**
```markdown
# Database Migration Specialist
You design and validate database schema migrations, ensuring zero data loss and backwards compatibility.
```

### Missing Boundaries

**Bad:**
```markdown
## Tasks
- Review code
- Fix issues
- Deploy changes
- Handle support tickets
```

**Good:**
```markdown
## Tasks
- Review code for security and performance issues
- Document findings with severity ratings

## NOT Your Tasks
- Implementing fixes (implementation agent handles this)
- Deployment (CI/CD handles this)
```

### Tool Overload

**Bad:**
```yaml
tools: Glob, Grep, Read, Write, Edit, MultiEdit, Bash, Task, WebFetch, WebSearch, NotebookEdit, NotebookRead, TodoWrite, Skill, ListMcpResourcesTool, ReadMcpResourceTool
```

**Good:**
```yaml
tools: Glob, Grep, Read, LS, WebSearch
```

### Generic Description

**Bad:**
```yaml
description: Code analysis agent
```

**Good:**
```yaml
description: Security vulnerability scanner. MUST BE USED before any code reaches production. Scans for OWASP Top 10, injection vulnerabilities, and authentication issues. Examples: "Check this for security issues", "Scan the API for vulnerabilities"
```
