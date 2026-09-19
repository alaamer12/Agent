# Verification Rollup Template

Every non-Member agent returns this format. Members return a simpler self-verification.

## Full Rollup (Team Leaders, Great Master)

```
DELIVERABLE:
[Summary of what was produced, key decisions, file list]

VERIFICATION EVIDENCE:
Children reviewed: [list all child task IDs]
Method: [How you verified each child's output — be specific]
  - [Child 1]: [What you checked, how you checked it]
  - [Child 2]: [What you checked, how you checked it]
Issues found and resolved:
  - [Issue 1]: [How it was caught, how it was resolved]
  - [Issue 2]: [How it was caught, how it was resolved]
Outstanding concerns: [none | list with severity and recommended action]

TASK ID: [your task ID]
PRODUCED BY: [your agent name]
```

## Member Self-Verification (Members)

```
DELIVERABLE:
[What you built, key files, design decisions]

SELF-VERIFICATION:
[How you tested your work, what you checked]
- [Check 1]: [Result]
- [Check 2]: [Result]

ISSUES OR CONCERNS:
[Anything the Team Leader should know — blockers, ambiguities, risks]

TASK ID: [your task ID]
PRODUCED BY: [your agent name]
```

## What Makes Good Evidence

**Bad evidence** (unverifiable):
> "Reviewed the code and it looks good."

**Good evidence** (verifiable):
> "Reviewed SEC-002-a's findings against acceptance criteria. Re-ran static analysis on flagged files (3 findings). Confirmed 2 were false positives (test-only code). Escalated 1 true positive (hardcoded API key in config.ts:42) — implementer notified via team-log."

## Spot-Check Questions

The layer above may ask:
- "You said you re-ran tests — show the output."
- "You said you verified coverage — what's the percentage?"
- "You said you checked security — what specific vulnerability classes?"

Be ready to answer with specifics.
