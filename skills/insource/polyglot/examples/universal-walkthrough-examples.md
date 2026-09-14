# Universal Walkthrough Examples: How to Author Polyglot Code Snippets

This document illustrates the practical authoring techniques used in `language-conventional` and `errors-handling` to provide diverse, universal, and idiomatically accurate code examples.

---

## Pattern 1: Applying Boundary Encapsulation Across 4 Languages

*Architectural Principle:* Never leak mutable collection handles across public API boundaries. Return read-only / immutable views while retaining fast internal mutation.

### 1. TypeScript
```typescript
// Anti-Pattern: External consumers can mutate array directly
export interface OrderService {
  getActiveOrders(): Promise<Order[]>;
}

// Polyglot Standard: Readonly array view with cooperative abort signal
export interface OrderService {
  getActiveOrders(signal?: AbortSignal): Promise<readonly Order[]>;
}
```

### 2. Python
```python
# Anti-Pattern: Lossy primitive and leaky mutable list
def get_active_orders(user_id: int) -> list[dict]:
    ...

# Polyglot Standard: Domain branded type and abstract immutable Sequence
from collections.abc import Sequence
from typing import NewType

UserId = NewType('UserId', int)

def get_active_orders(user_id: UserId) -> Sequence[OrderDto]:
    """Retrieves active orders without exposing internal list mutation."""
    ...
```

### 3. Go
```go
// Anti-Pattern: Pointer slices allowing caller in-place modification without cancellation
func (s *Service) GetActiveOrders() ([]*Order, error)

// Polyglot Standard: Value slice with context propagation
func (s *Service) GetActiveOrders(ctx context.Context) ([]Order, error)
```

### 4. C# / .NET
```csharp
// Anti-Pattern: Returns mutable List<T> with blocking or uncancellable signature
public Task<List<Order>> GetActiveOrdersAsync();

// Polyglot Standard: Read-only contract interface with cancellation token
public Task<IReadOnlyList<Order>> GetActiveOrdersAsync(CancellationToken ct = default);
```

---

## Pattern 2: Structuring Failure Contracts Across Different Paradigms

*Architectural Principle:* Failures must be explicit, typed, and structured to differentiate internal diagnostic context from consumer-facing messages.

### 1. Functional / Result Paradigm (TypeScript)
```typescript
export interface DomainError {
  readonly code: string;
  readonly internalMessage: string;
  readonly externalMessage: string;
  readonly fixMessage?: string;
}

export type Result<T, E = DomainError> =
  | { readonly ok: true; readonly value: T }
  | { readonly ok: false; readonly error: E };
```

### 2. Idiomatic Tuple / Error Return Paradigm (Go)
```go
type DomainError struct {
    Code            string
    InternalMessage string
    ExternalMessage string
}

func (e DomainError) Error() string {
    return fmt.Sprintf("[%s] %s", e.Code, e.InternalMessage)
}

func ProcessPayment(ctx context.Context, amount int) (*Receipt, error) {
    if amount <= 0 {
        return nil, DomainError{
            Code:            "PAY-001",
            InternalMessage: "Payment amount must be strictly positive",
            ExternalMessage: "Invalid transaction amount.",
        }
    }
    return &Receipt{ID: "rcpt_123"}, nil
}
```

### 3. Type-Safe Monadic Result with Pattern Matching (Rust)
```rust
#[derive(Debug, Clone)]
pub struct DomainError {
    pub code: &'static str,
    pub internal_message: String,
    pub external_message: String,
}

impl std::fmt::Display for DomainError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "[{}] {}", self.code, self.internal_message)
    }
}

pub fn validate_order(quantity: u32) -> Result<(), DomainError> {
    if quantity == 0 {
        return Err(DomainError {
            code: "ORD-001",
            internal_message: "Quantity cannot be zero".into(),
            external_message: "Please specify at least one item.".into(),
        });
    }
    Ok(())
}
```

---

## Pattern 3: Dynamic Strategy Framing (Non-Forced Inquiries)

When designing a conversational skill, never frame requirements as absolute mandates. Frame them as open design trade-offs:

```markdown
### Inquiring & Agreeing on Normalization Strategy
The agent inspects the application's domain and asks the user:
- What is the primary operational workload (write-heavy OLTP, read-heavy reporting, or event log)?
- Which normalization strategy aligns with performance constraints:
  - Strict 3NF / BCNF (zero redundancy, high consistency)
  - Pragmatic denormalization (selective pre-aggregated columns for high-throughput reads)
  - Hybrid relational-document model (structured relational core with JSON metadata)
The agent documents the user's decision along with explicit trade-offs.
```
