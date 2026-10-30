# Factories & Fixtures — Polyglot Walkthrough

**Principle:** Every test owns its data. Hard-coded literals are a defect. Data is produced by role-named factories or fixtures that live in a conventional location and document “how to construct X”.

## Anti-pattern (any language)
```text
// Hard-coded values scattered through tests
assert(validateEmail("john@example.com") === true)
assert(validateEmail("not-an-email") === false)
```

## Polyglot standard

### TypeScript
```typescript
// tests/factories/email.ts
export const EmailFactory = {
  valid: () => `user-${crypto.randomUUID()}@example.com`,
  invalid: () => `user-${crypto.randomUUID()}-example.com`, // missing @
};

// test
import { EmailFactory } from '../factories/email';
expect(validateEmail(EmailFactory.valid())).toBe(true);
expect(validateEmail(EmailFactory.invalid())).toBe(false);
```

### Python
```python
# tests/factories/email.py
from uuid import uuid4

class EmailFactory:
    @staticmethod
    def valid() -> str:
        return f"user-{uuid4()}@example.com"

    @staticmethod
    def invalid() -> str:
        return f"user-{uuid4()}-example.com"  # missing @

# test
from tests.factories.email import EmailFactory
assert validate_email(EmailFactory.valid()) is True
assert validate_email(EmailFactory.invalid()) is False
```

### Go
```go
// tests/factory/email.go
package factory

import "fmt"
import "github.com/google/uuid"

func ValidEmail() string {
    return fmt.Sprintf("user-%s@example.com", uuid.NewString())
}

func InvalidEmail() string {
    return fmt.Sprintf("user-%s-example.com", uuid.NewString()) // missing @
}

// test
email := factory.ValidEmail()
assert.True(t, ValidateEmail(email))
```

### Rust
```rust
// tests/factory.rs
use uuid::Uuid;

pub struct EmailFactory;

impl EmailFactory {
    pub fn valid() -> String {
        format!("user-{}@example.com", Uuid::new_v4())
    }
    pub fn invalid() -> String {
        format!("user-{}-example.com", Uuid::new_v4()) // missing @
    }
}

// test
let valid = EmailFactory::valid();
assert!(validate_email(&valid));
```

### C#
```csharp
// Tests/Factories/EmailFactory.cs
public static class EmailFactory
{
    public static string Valid() => $"user-{Guid.NewGuid()}@example.com";
    public static string Invalid() => $"user-{Guid.NewGuid()}-example.com"; // missing @
}

// test
Assert.True(ValidateEmail(EmailFactory.Valid()));
Assert.False(ValidateEmail(EmailFactory.Invalid()));
```

## Key points across languages
- Role-named methods (`valid`, `invalid`, `expired`, `withItems(n)`).
- Prefer domain types over primitives when the language supports them.
- Generation is deterministic or thread-safe when tests run in parallel.
- Factories live in a conventional location so they become the living contract of “how to test X”.
