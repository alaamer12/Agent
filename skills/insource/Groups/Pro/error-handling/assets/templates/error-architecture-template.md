# Universal Error Architecture Template

Use this universal template when generating an application's error handling conventions steering document.

```markdown
# Error Architecture & Handling Conventions — <Application Name>

> **Scope:** Error contracts, structured error codes, payload formats, and placement strategy for `<Application Name>`.
> **Philosophy:** <Explicit failure contracts and structured, leak-free error diagnostics>.

---

## 1. Error Contract Philosophy

The application follows the agreed contract paradigm:

**Chosen Contract Paradigm:** `<Model A: Pure Monadic Result / Model B: Typed Domain Exceptions with Boundaries / Model C: Three-Contract (Throw/Result/Neither)>`

| Operational Category | Expected Failure Behavior | Handling Mechanism | Boundary Supervisor |
|---|---|---|---|
| **Fatal / Unrecoverable** | Fatal crash / panic / stop | `<Native throw / panic>` | Top-level host / request boundary |
| **Expected Domain Rejection** | Typed error return | `<Result<T, E> / Either / Custom Domain Exception>` | Caller handles branch or controller maps to status |
| **Optional Side-Effect** | Logged fallback | Log warning + fallback default | Handled locally without breaking primary flow |

---

## 2. Structured Error Representation (Payload Shape)

**Chosen Payload Shape:** `<Option 1: Code + Message / Option 2: RFC 7807 Problem Details / Option 3: Segregated Multi-Part (Internal / External / Fix)>`

```text
<!-- Provide diagram or schema of agreed payload -->
```

### Invariants:
1. **Zero Information Leakage:** Technical diagnostics (DB traces, internal IPs, raw parameters) must never be exposed to public/client consumers.
2. **Actionable Feedback:** Where user interaction is required, error feedback must explain what went wrong and how the user can recover.

---

## 3. Organization & File Distribution

**Chosen Distribution Strategy:** `<Option A: Per-Module Errors File / Option B: Single Centralized Registry / Option C: Entity/Subsystem Slices>`

### Strategy Trade-offs & Layout:
- **File Structure:**
  ```text
  <!-- Illustrate agreed layout e.g.
  apps/web/src/
  ├── auth/errors.ts
  ├── billing/errors.ts
  OR
  shared/errors/registry.ts -->
  ```

### Rules:
1. **No Ad-Hoc Construction:** Constructing error objects inline with raw strings inside business logic is prohibited.
2. **Factory Functions:** All errors must be created through dedicated factory functions defined in the authoritative error file(s).
3. **Visibility & Scope:** Error codes and categories are exported for callers; internal technical details are encapsulated.

---

## 4. Machine-Readable Error Code Registry

Format: `{DOMAIN_PREFIX}-{NUMERIC_ID}` (e.g. `AUTH-001`, `PAY-023`).

| Prefix | Domain / Module | Subsystem / Layer |
|---|---|---|
| `<PREFIX_1>` | `<Module 1>` | `<Layer / Service>` |
| `<PREFIX_2>` | `<Module 2>` | `<Layer / Service>` |
| `<PREFIX_3>` | `<Module 3>` | `<Layer / Service>` |

---

## 5. Aggregation & Flattening

When executing batch or parallel operations:
- Collect individual `Result` failures into a composite domain error without losing individual item identifiers.
- Flatten nested causal chains cleanly for log indexing.
```
