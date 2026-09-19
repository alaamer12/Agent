# Team-Log Protocol

The horizontal channel for peer Team Leaders. Append-only, informational, never bypasses verification.

## Format

```markdown
# team-log.md

[ISO-8601 timestamp] [sender] → [recipient(s)]:
  [Message body — concise, actionable, informational]

[ISO-8601 timestamp] [recipient] → [sender]:
  [Acknowledgment or response]
```

## Rules

1. **Append-only** — Never edit or delete existing entries
2. **One writer per entry** — No collaborative editing
3. **Timestamp everything** — ISO-8601 format (YYYY-MM-DDTHH:MM:SSZ)
4. **Be concise** — This is a coordination channel, not a discussion forum
5. **Informational only** — Does NOT replace task contracts or verification rollups

## What Belongs in Team-Log

- Cross-team findings that affect another team's work
- Scope clarifications between peers
- Scheduling/coordination (e.g., "I'll be done with X by 14:00")
- Warnings about potential conflicts

## What Does NOT Belong

- Task assignments (use task contracts)
- Verification results (use rollups)
- Requests for approval (escalate to Great Master)
- Code reviews (use your team's internal process)

## Example Session

```markdown
[2026-09-15T10:14:00Z] security-leader → all:
  Found: session middleware in src/auth/session.ts uses fixed-window rate limiter,
  not sliding-window required by SECURITY.md §4. Flagging for implementer-leader
  awareness — not blocking, will file as SEC-002-c if not addressed by merge.

[2026-09-15T10:16:00Z] implementer-leader → security-leader:
  Ack. This file predates the refactor scope (out_of_scope for IMPL-001).
  Filing as separate follow-up task, not blocking current merge.

[2026-09-15T11:22:00Z] tester-leader → implementer-leader:
  Heads up: integration tests for auth are failing on the reset-password flow.
  Looks like a race condition in token invalidation. Can you take a look?

[2026-09-15T11:25:00Z] implementer-leader → tester-leader:
  On it. Found the issue — token cleanup is async but test doesn't await.
  Fix incoming in 10 min.
```
