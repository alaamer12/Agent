# Example Hypotheses (Illustrative)

These examples show the expected depth and style. Adapt to the actual request.

---

## Example 1 — Explicit Requirement

```markdown
# Hypothesis 01 — Support Concurrent Uploads

## User Requirement Statement
"Users should be able to upload multiple files at the same time."

## Interpolation
The system must accept concurrent file uploads from a single client session without serializing them on the server. Each upload should be tracked independently (progress, cancellation, error isolation). The design must respect existing authentication and rate-limiting middleware already present in the project. Prefer the concurrency primitives already used elsewhere in the codebase (e.g. worker pools or async tasks) rather than introducing a new concurrency model.

## Supporting Evidence
- **Local**
  - `src/api/middleware/rateLimit.ts` — existing per-user rate limits
  - `src/workers/` — existing background job pattern
- **Research**
  - Current Node.js / Go / Python async best practices for streaming uploads (prefer streaming over full buffering)
- **Assumptions**
  - Uploads are authenticated; anonymous multi-upload is out of scope
  - Maximum concurrent uploads per user will be governed by the existing rate limiter

## Open Questions
- Should failed uploads automatically retry, or is that left to the client?
- Is there a hard size limit per file or per concurrent set?
```

---

## Example 2 — Implicit Constraint

```markdown
# Hypothesis 02 — Backward Compatibility with Existing Clients

## User Requirement Statement
(No direct statement; inferred from the presence of a public API and the request to "improve the upload endpoint".)

## Interpolation
Any change to the upload endpoint must remain compatible with the current public API contract used by existing mobile and web clients. New optional fields or query parameters are acceptable; removing or renaming existing fields is not. Response shape for successful and error cases should stay stable unless a versioned migration path is explicitly planned.

## Supporting Evidence
- **Local**
  - `docs/api/v1/uploads.md` — published contract
  - Client SDKs in the monorepo that call the endpoint
- **Research**
  - Semantic versioning and API evolution guidelines commonly used for public APIs
- **Assumptions**
  - The project treats the current API as stable
  - A major version bump is not desired for this change

## Open Questions
- Is there an existing deprecation policy or API versioning strategy that must be followed?
```

---

## Example 3 — Scalability & Robustness

```markdown
# Hypothesis 03 — Graceful Degradation Under Load

## User Requirement Statement
(Implicit; good engineering practice for any user-facing upload feature.)

## Interpolation
Under high concurrent load the system should degrade gracefully: reject excess requests with a clear 429/503 rather than queue-out or corrupt partial uploads. Resource limits (memory, file descriptors, disk) must be bounded. Temporary storage for in-progress uploads should be cleaned up on both success and failure paths.

## Supporting Evidence
- **Local**
  - Existing resource limits and circuit-breaker patterns in the codebase
- **Research**
  - Common failure modes of multipart / streaming upload services
- **Assumptions**
  - The deployment environment has finite resources; unbounded buffering is unacceptable

## Open Questions
- What is the acceptable latency and success-rate SLO for the upload path?
```
---
