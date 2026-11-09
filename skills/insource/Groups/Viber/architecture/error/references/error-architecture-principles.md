# Universal Error Architecture Reference

This reference guide establishes the structural foundation of error handling across applications. It details error handling contract models, customizable payload architectures, placement strategies, and observability principles.

---

## 1. Error Contract Philosophies: Architectural Options

Rather than assuming one contract model fits all applications, the agent evaluates the following architectural paradigms with the user:

### Model A: Pure Monadic Result / Either
- **Concept:** Every function that can fail returns `Result<T, E>` or `Either<L, R>`. Exceptions are disabled or reserved solely for unexpected process panics.
- **Pros:** Compiler-enforced handling of all branches; zero unhandled crashes; explicit data flow.
- **Cons:** Boilerplate propagation in deep call stacks (unless monadic bind / `?` operator is native).
- **Best Suited For:** Rust, Go, functional TypeScript, high-reliability payment systems.

### Model B: Typed Domain Exceptions with Layer Boundaries
- **Concept:** Modules throw custom, strongly typed domain exceptions (e.g. `OrderNotFoundException`, `InsufficientFundsException`). Middleware or controller boundaries catch and map them to HTTP/UI responses.
- **Pros:** Minimal boilerplate in internal service layers; idiomatic in Java, C#, Python.
- **Cons:** Invisible failure paths in type signatures; runtime crashes if boundary handlers are omitted.
- **Best Suited For:** REST APIs, microservices with global exception filters.

### Model C: Three-Contract Taxonomy (Throw / Result / Neither)
- **Concept:** Explicit operational segregation:
  - **Throw:** Fatal infrastructure or startup invariant failures (unrecoverable).
  - **Result:** Expected domain failures, validations, and business rule rejections.
  - **Neither:** Best-effort side effects (telemetry, background cache sync) swallowed with structured warning logs.
- **Pros:** Clear cognitive boundaries between fatal bugs and standard user/operational rejections.
- **Cons:** Requires team discipline to choose the right contract for each method.
- **Best Suited For:** Complex desktop applications, distributed pipelines, local-first stores.

---

## 2. Error Payload Shapes: Design Spectrum

Error payload shapes are tailored to the application's consumer requirements:

```text
Lightweight Code ───► Standard Problem Details ───► Multi-Part Segregated Payload
 (Microservices)           (Public Web APIs)               (Rich UI / Desktop)
```

### Shape Option 1: Lightweight Code & Message
```json
{
  "code": "AUTH_001",
  "message": "Invalid credentials provided."
}
```
- **Use When:** Internal RPC, high-throughput microservices, minimal payload overhead.

### Shape Option 2: RFC 7807 Problem Details
```json
{
  "type": "https://api.example.com/errors/out-of-credit",
  "title": "You do not have enough credit.",
  "status": 403,
  "detail": "Your current balance is 30, but that costs 50.",
  "instance": "/account/12345/msgs/abc"
}
```
- **Use When:** Public REST APIs, standardized third-party HTTP integrations.

### Shape Option 3: Segregated 4-Part Payload (Internal / External / Fix)
```json
{
  "code": "HTTP-001",
  "internalMessage": "HTTP request to 'https://api.site.com/data' failed: connection reset",
  "externalMessage": "Unable to connect to the server.",
  "fixMessage": "Please check your internet connection and try again.",
  "cause": "SocketException"
}
```
- **Use When:** Applications requiring localized user-facing feedback, actionable self-healing prompts, and strict isolation of technical secrets from end users.

---

## 3. Placement Architecture: Per-Module Errors vs Centralized Registries

Applications select an error placement strategy suited to their scale:

### Option A: Per-Module Error Factories (Recommended for Modularity)
- Every module or package owns an authoritative `errors` file (e.g. `errors.ts`, `errors.py`, `errors.go`, `Errors.cs`).
- **Invariant:** Direct ad-hoc error construction in business logic is prohibited. All error instances must originate from the module's error factory.
- **Advantage:** Modules maintain high cohesion; error codes and messages live right beside the domain logic that produces them.

### Option B: Centralized Error Registry (Recommended for Small Services / Gateways)
- All domain error codes, categories, and catalogs are centralized in a core shared module.
- **Advantage:** Global visibility into all application error codes, simplifying localization dictionary extraction.

---

## 4. Machine-Readable Error Code Taxonomy

Codes must be uppercase, prefixed by the bounded domain, and zero-padded:

```text
{DOMAIN_PREFIX}-{NUMERIC_ID}
```
- E.g., `NET-001`, `AUTH-012`, `STORAGE-105`, `BILLING-003`.
- Ensures zero ambiguity in APM query dashboards (`where error.code = "BILLING-003"`).
