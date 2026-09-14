# Polyglot Walkthrough: Designing errors-handling for an Application

This walkthrough demonstrates how an AI agent executes the open, context-driven discovery and specification of `errors-handling` with the user.

---

## Step 1: Contextual Discovery of Failure Contracts

The agent evaluates the application's runtime, language idioms, and architectural goals, synthesizing tailored options with pros and cons:
- *Example Option:* Monadic `Result<T, E>` (for strict compile-time safety and explicit handling).
- *Example Option:* Hierarchical Domain Exceptions caught at middleware/controller filters (for minimal boilerplate in web frameworks).
- *Example Option:* Multi-tier taxonomy (e.g. Throw for unrecoverable fatal invariants, Result for expected operational rejections, Neither for best-effort swallowed warnings).
- *Example Option:* Event-driven error channels or callback observers (for reactive or streaming architectures).

The agent presents the relevant options and helps the user choose the paradigm that best aligns with the system's needs.

---

## Step 2: Contextual Discovery of Error Payload Shapes

The agent investigates who or what consumes errors produced by this application (e.g. end-user UI, third-party API clients, background APM alerts):
- *Example Shape:* Lightweight Code + Message (minimal overhead for internal microservices).
- *Example Shape:* RFC 7807 Problem Details (industry standard for public HTTP REST APIs).
- *Example Shape:* Multi-part segregated payload (isolating internal diagnostics from localized user-facing copy and actionable fix instructions).
- *Example Shape:* Domain-specific rich error (including validation field maps or retry backoff metadata).

The agent and user determine the exact fields required.

---

## Step 3: Determining Organization & File Distribution

The agent analyzes codebase size, modularity, and team structure:
- *Example Strategy:* Per-module / per-package error files (high cohesion, keeps error definitions beside feature code).
- *Example Strategy:* Centralized error registry (single source of truth, ideal for microservices or centralized localization).
- *Example Strategy:* Feature-sliced error definitions (domain entities own their typed errors).

The chosen distribution pattern is recorded.

---

## Step 4: Polyglot Implementation Examples

### Example 1: TypeScript Web App (Using Monadic Result + Segregated Payload)
```typescript
// modules/auth/auth-errors.ts
export interface DomainError {
  readonly code: string;
  readonly internalMessage: string;
  readonly externalMessage: string;
  readonly fixMessage?: string;
}

export type Result<T, E = DomainError> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };

export function userNotFound(id: string): DomainError {
  return {
    code: "AUTH-001",
    internalMessage: `User record '${id}' not found in DB`,
    externalMessage: "Account could not be found.",
    fixMessage: "Please verify the username and try again."
  };
}
```

### Example 2: Go Microservice (Using Compact Code + Message with (T, error))
```go
// pkg/orders/errors.go
package orders

import "fmt"

type OrderError struct {
    Code    string
    Message string
}

func (e OrderError) Error() string {
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func ErrInventoryExhausted(sku string) error {
    return OrderError{
        Code:    "ORD-002",
        Message: fmt.Sprintf("Inventory exhausted for SKU %s", sku),
    }
}
```

### Step 5: Output Artifact
The agent writes the agreed error conventions to:
`.repertoire/.steering/<app-name>/tech/errors-handling.md`
