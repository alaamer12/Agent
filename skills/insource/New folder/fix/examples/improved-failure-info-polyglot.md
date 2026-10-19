# Improving Failure Information — Polyglot Walkthrough

**Principle (Fix skill):** After solving the root cause, improve the relevant implementation so the same class of problem becomes cheaper to identify next time. One common form is more precise failure information.

## Before (generic error)
```text
Database insertion failed
```

## After — precise, actionable errors

### TypeScript
```typescript
// Domain error with location and context
export class UserCreationError extends Error {
  constructor(
    public readonly step: 'validate' | 'hash' | 'insert' | 'index',
    public readonly cause: unknown,
    public readonly userIdAttempt?: string,
  ) {
    super(`User creation failed at step '${step}'${userIdAttempt ? ` for ${userIdAttempt}` : ''}`);
    this.name = 'UserCreationError';
  }
}

// usage
throw new UserCreationError('insert', dbError, email);
```

### Python
```python
class UserCreationError(Exception):
    def __init__(self, step: str, cause: Exception, user_id_attempt: str | None = None):
        self.step = step
        self.cause = cause
        self.user_id_attempt = user_id_attempt
        msg = f"User creation failed at step '{step}'"
        if user_id_attempt:
            msg += f" for {user_id_attempt}"
        super().__init__(msg)
```

### Go
```go
type UserCreationError struct {
    Step           string
    Cause          error
    UserIDAttempt  string
}

func (e *UserCreationError) Error() string {
    msg := fmt.Sprintf("User creation failed at step '%s'", e.Step)
    if e.UserIDAttempt != "" {
        msg += fmt.Sprintf(" for %s", e.UserIDAttempt)
    }
    return msg
}

func (e *UserCreationError) Unwrap() error { return e.Cause }
```

### Rust
```rust
#[derive(Debug, thiserror::Error)]
pub enum UserCreationError {
    #[error("User creation failed at step '{step}'{}", .user_id_attempt.as_ref().map(|id| format!(" for {id}")).unwrap_or_default())]
    Failed {
        step: &'static str,
        #[source]
        cause: Box<dyn std::error::Error + Send + Sync>,
        user_id_attempt: Option<String>,
    },
}
```

### C#
```csharp
public sealed class UserCreationException : Exception
{
    public string Step { get; }
    public string? UserIdAttempt { get; }

    public UserCreationException(string step, Exception cause, string? userIdAttempt = null)
        : base($"User creation failed at step '{step}'{(userIdAttempt is null ? "" : $" for {userIdAttempt}")}", cause)
    {
        Step = step;
        UserIdAttempt = userIdAttempt;
    }
}
```

## Notes
- The improved error names the **exact step** and, when useful, the relevant identifier.
- This is only one possible form of improvement. Logging, structural clarity, or making the invalid state unrepresentable may be higher leverage in other situations.
- Always keep the improvement inside the relevant context of the original problem.