# Task Contract Template

Copy this template for every delegation. Fill in every section — never drop one.

```
GOAL:
[One clear sentence: what must be achieved]

SCOPE (you may read/write within):
- [Directory or file path 1]
- [Directory or file path 2]
- [Specific operations allowed, e.g., "may modify existing files, may create new test files"]

OUT OF SCOPE (do not touch or assess):
- [Explicit exclusion 1]
- [Explicit exclusion 2]
- [Any file outside the SCOPE list]

ACCEPTANCE CRITERIA (your deliverable must satisfy all of these):
- [Verifiable condition 1 — e.g., "No hardcoded secrets"]
- [Verifiable condition 2 — e.g., "All tests pass"]
- [Verifiable condition 3 — e.g., "Coverage ≥ 80% on modified files"]

EXPECTED DELIVERABLE:
A rollup report + evidence log in the format specified in SKILL.md.
Return this in your final message — do not just say "done."

ISSUED BY: [your agent name]
ASSIGNED TO: [recipient agent name]
TASK ID: [TEAM-NNN for teams, TEAM-NNN-M for members]
```

## Examples

### Great Master → Team Leader

```
GOAL:
Implement the user authentication system with login, signup, and password reset.

SCOPE (you may read/write within):
- src/auth/**
- src/middleware/**
- tests/auth/**

OUT OF SCOPE (do not touch or assess):
- UI components (src/components/**)
- Database migrations (handled by separate task)
- Email service integration (mock only)

ACCEPTANCE CRITERIA:
- All endpoints return correct HTTP status codes
- Passwords hashed with bcrypt (12 rounds)
- JWT tokens expire per SECURITY.md §4
- Unit tests cover all auth flows

EXPECTED DELIVERABLE:
A rollup report + evidence log (see "Verification Rollup Chain" format).
Return this in your final message — do not just say "done."

ISSUED BY: great-master
ASSIGNED TO: team-leader-implementer
TASK ID: IMPL-001
```

### Team Leader → Member

```
GOAL:
Implement the password reset flow: request reset, validate token, update password.

SCOPE (you may read/write within):
- src/auth/password-reset.ts
- src/auth/password-reset.test.ts

OUT OF SCOPE (do not touch or assess):
- Login/signup flows (other Members own these)
- Email sending (mock the email service)
- Database schema (use existing User model)

ACCEPTANCE CRITERIA:
- POST /auth/reset-request returns 200 always (no user enumeration)
- POST /auth/reset-confirm validates token expiry
- POST /auth/reset-confirm updates password and invalidates sessions
- Tests cover: valid flow, expired token, invalid token, reused token

EXPECTED DELIVERABLE:
Code + self-verification notes in the standard format.

ISSUED BY: team-leader-implementer
ASSIGNED TO: implementer-services
TASK ID: IMPL-001-2
```
