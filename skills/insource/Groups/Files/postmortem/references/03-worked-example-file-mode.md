# Worked example — file mode (condensed)

> Invented incident for teaching. A real file-mode postmortem keeps all 18 sections; this shows the shape and
> the sentences that carry the weight. Snippets below are abbreviated with `…`.

**Request.** "Write a postmortem for last night's login outage. File is fine, we don't have artifacts saved."

**Output:** `postmortems/2026-10-12-auth-refresh-storm.md`

```markdown
# Postmortem: Auth service — token refresh storm — 2026-10-12

**Status:** final · **Severity:** SEV-2 · **Incident ID:** INC-2411
**Authors:** <names> · **Reviewers:** <name> · **Sign-off:** <name, 2026-10-13>

## 1. What the problem was

**Summary.** A clock-skew guard added in 4.2.0 treated already-refreshed tokens as expired, so every client
re-entered the refresh path on each request. At 03:14 UTC the refresh endpoint saturated, and logins queued
behind it for 38 minutes. 1,842 of 12,000 active sessions (15.4%) hit a 502 during that window. Rollback to
4.1.9 restored service at 03:52Z; the guard was rebuilt and shipped in 4.2.2.

**Exact symptom.**
```text
auth-api 03:14:07Z ERROR refresh: token skew guard rejected iat (now=..., iat=..., skew=+410ms)
auth-api 03:14:08Z WARN  pool: waiting=1,204 active=200 max=200
gateway 03:14:09Z ERROR upstream 502 /api/session (auth-api timeout 5000ms)
```

## 2. When and where — traceability

| Field | Value |
|---|---|
| First bad commit | `9c1f0a4e7b2d5c8f1a3e6b9d0c4f7a2e5b8d1c3f` — feat(auth): reject tokens minted before skew guard |
| Last good commit | `37b4e2c9a1d6f8b0e3c5a7d9f1b4e6c8a0d2f5b7` — chore: bump lockfile |
| Fix commit(s) | `c4a8d1f6e2b9c7a5d3f0e8b6c2a9d7f4e1b3c5a8` — fix(auth): compare against server clock only |
| Versions affected / fixed | 4.2.0–4.2.1 / 4.2.2 |
| Release channel | stable |
| Build ID | `auth-4.2.0+20261011.3` |
| Artifact hash | `sha256:6f1e…` |
| Dependencies | lockfile `sha256:0b9c…`; jwt lib 8.4.1 |
| Feature flags | `auth.skew_guard=true` (default on in 4.2.x) |
| OS / build | Ubuntu 22.04, kernel 5.15.0-91 |
| Container digest | `sha256:aa31…` |
| Reproduces where? | yes on 4.2.0/4.2.1 with `skew_guard=true`; no on 4.1.9 |

## 3. When it started and how long it lasted

| Milestone | UTC | Evidence |
|---|---|---|
| Introduced | 2026-10-11T18:22:00Z | `9c1f0a4` merged (deployed 22:10Z) |
| First occurrence | 2026-10-12T03:14:07Z | first guard rejection in `evidence/auth-0314.log` |
| Detected | 2026-10-12T03:19:41Z | alert `auth_5xx_rate > 5%` |
| Fixed (rollback) | 2026-10-12T03:52:10Z | deploy `d-8841` |
| **Exposure window** | **37 min 63 s** | first occurrence → rollback complete |

## 4. The interval in which the pattern occurs

Window: **immediately after any clock correction ≥ 250 ms**, i.e. between 0 s and ~2 s after the client's next
request; the storm then persists until the client is forced to re-authenticate.
min/median/max: 0.4 s / 0.9 s / 2.1 s · n = 1,842 rejected refreshes
Why: the guard compared the token's `iat` to the *client-reported* clock, so an NTP step made every freshly
minted token look old — not a timing bug in the refresh itself.

## 8. How it happened

| Element | Statement |
|---|---|
| Symptom | 502s on `/api/session` for 15.4% of active sessions |
| Trigger | A routine NTP correction on the client fleet at 03:14Z |
| Root cause | The skew guard used the client-supplied timestamp as its reference instead of the server clock |
| Latent conditions | No test covered "token just minted + clock jumped forward"; the guard was flag-on by default |

Causal chain: 1. NTP steps +410 ms → 2. `iat` now older than `now - skew` → 3.
[`auth/token_guard.py#L41-L58`](https://…/blob/c4a8d1f…/auth/token_guard.py#L41-L58) rejects → 4. client
retries refresh on every request → 5. pool saturation → 6. gateway 502s.

Five whys → 5th: *the system had no rule that a clock-sensitive comparison must be made against one clock*.

## 9. Cause category

**Primary:** code-side. **Confidence:** proven (V4 reproducer). Alternatives rejected: "jwt-lib bug" — the
library echoes the value it is given (`investigation/jwt-echo-check.py`); "pool too small" — the pool saturated
*as a consequence* of 1,842 doomed refreshes.

## 13. Heuristic or verified?

**V4 — deterministic reproduction.** `verification/repro_skew_guard.py` sets the client clock forward 410 ms,
mints a token, and asserts rejection on the old build (fails 20/20) and acceptance on the new one (passes
20/20). Not V5: the guard still performs a cross-clock comparison; it now uses the server clock as the sole
reference, which removes this failure but not the class (§16 A2).

## 16. Prevention

| ID | Action | Type | Priority | Owner | Due | Ticket | Definition of done | Status |
|---|---|---|---|---|---|---|---|---|
| A1 | Regression test for "minted now + clock step forward" | prevent | P1 | <name> | 2026-10-20 | <link> | test fails on `9c1f0a4`, passes on `c4a8d1f` | open |
| A2 | Lint rule: clock comparisons must reference the server clock | prevent | P2 | <name> | 2026-11-03 | <link> | CI job `clock-guard` green on repo | open |
| A3 | Alert on refresh-rejection rate, not just 5xx | detect | P1 | <name> | 2026-10-20 | <link> | alert fires in a staged test | open |
```

**What made this example work:** every claim has a SHA, a timestamp, a count or a file; the fix section says
`V4, not V5` and names the remaining class; the five whys ends at a *system property*, not a person; and the
rollback time is a fact, not "quickly".

**What would have been rejected:** "the developer forgot to use the server clock" (a person as cause), "many
users were affected for a while" (no numbers), "tested and confirmed fixed" (no level, no N).
