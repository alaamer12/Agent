# Fixtures and Generators

Tests fail for two reasons that look alike and are not: the behavior is wrong, or the world the test
built is wrong. This reference makes the second impossible to confuse with the first. It covers the
lifecycle of the test world (fixtures), the construction of the things in it (generators), and the
identity rules that keep instances and sessions meaningful across the suite.

---

## 1. Vocabulary

| Term | Definition | Owns |
|---|---|---|
| **Harness** | The process-level environment a suite runs in | runner, container, server, browser, temp root |
| **Fixture** | The seeded world a test starts from, plus its teardown | schema, reference data, flags, clock, config |
| **Generator** (factory, builder, Object Mother) | A named way to build one domain instance on demand | defaults, overrides, identity, special states |
| **Scenario** | A named business situation composed from generators | "expired subscription for a member", "tenant with two admins" |
| **Test double** | A stand-in for a dependency | adapters for payment, mail, clock, network |

A generator is not a fixture. A fixture has a lifecycle and may be shared; a generator has neither
and is called as often as the test needs. Most "fixture hell" is a lifecycle problem; most "brittle
data" is a generator problem. Diagnose which one before fixing.

---

## 2. Fixture lifecycle

### 2.1 Fresh by default, shared by exception

**Fresh fixture** — built for one test, discarded after. Isolation is absolute, order cannot matter,
parallel execution is safe. This is the default and should be the rule for anything a test can write.

**Shared fixture** — built once for a file, class, or suite. Fast, but every test now shares mutable
state, and the first test that forgets to clean up becomes the next test's mystery failure.

Share only what is **expensive and read-only**:

- the database engine / container,
- the migrated schema (a template database),
- a compiled grammar, a loaded dictionary, a browser binary,
- a reference catalogue the suite never mutates,
- an immutable clock or config object (copy-on-write per test if a test changes it).

Never share: rows a test inserts, in-memory caches, mutable singletons, feature-flag maps, auth
sessions, temp directories, or anything whose teardown a test might skip.

### 2.2 Isolation strategies

Pick per resource, and write the choice into `testing-architecture.md`. Each has a failure mode.

| Strategy | How it works | Strength | Failure mode |
|---|---|---|---|
| **Transaction rollback** | Open a transaction per test; roll back at the end | Fast, perfect isolation | SUT commits or opens its own connection → the write escapes |
| **Truncate / reset** | Delete or truncate mutable tables between tests | Simple, works with commits | Slow on large schemas; misses sequences unless reset |
| **Template database** | Migrate once, clone per test or per worker | Fast startup, real schema | Clone cost; template drift if migrations run conditionally |
| **Namespace / tenant per test** | Unique schema, prefix, or tenant per test | Parallel-safe without cloning | Every query must respect the namespace; leaks if a query bypasses it |
| **In-memory engine** | SQLite `:memory:` or equivalent | Very fast, hermetic | Dialect drift from the production engine; not a parity proof |
| **Ephemeral container** | One container per worker or suite | Real engine, real version | Startup cost; port collisions; cleanup on crash |
| **Temp directory** | Fresh root per test, deleted after | Real filesystem semantics | Path length, case sensitivity, separator differences |
| **Archived bytes** | Replay recorded responses from a content-addressed corpus | Deterministic, offline, reviewable | Corpus drift; must be re-captured deliberately |

Two cross-cutting rules:

1. **The creator closes.** A harness that starts a process returns a handle whose teardown is
   registered in the same place (`afterAll`, `yield`, `defer`, `try/finally`). A test must never be
   responsible for infrastructure cleanup it did not create.
2. **Prove the isolation, once.** A conformance test inserts a row, ends the test, and asserts the
   next test sees zero rows. Isolation nobody has watched fail is an assumption.

### 2.3 Fixture teardown is part of the fixture

A fixture without teardown is a leak with a friendly name. Teardown must be:

- **unconditional** — it runs on failure, timeout, and cancellation;
- **idempotent** — safe to call twice;
- **ordered** — children before parents (stop the app before dropping the schema);
- **honest** — a teardown failure is reported, not swallowed. A swallowed teardown error is how the
  next test inherits a corrupted world.

---

## 3. Generators

### 3.1 The contract

Every aggregate gets one generator, named `<Aggregate>Generator`, in one file, under
`tests/support/generators/` (or the project's equivalent). It exposes:

| Member | Contract |
|---|---|
| `create(overrides)` | A valid instance; defaults for every field; overrides win |
| `<state>()` | Explicit business states: `admin()`, `suspended()`, `expired()`, `unverified()` |
| `with<Relation>()` | Relationship composition: `withOrders(3)`, `inTenant(t)` |
| `defaults()` | The canonical values, exported so other layers can agree |
| `identity(name)` | The deterministic id/email/key derivation used by every instance |

The invariant: **`create()` with no arguments always produces a valid instance that satisfies every
schema and domain constraint.** A generator that can build an invalid default is a bug factory.

### 3.2 Defaults, overrides, special states

Defaults exist so a test can say only what it cares about. Special states exist so a test says
`admin()` instead of `withRole("admin")` — the business word is the API, and when the definition of
"admin" changes, one method changes.

```ts
// tests/support/generators/user.ts
export const UserGenerator = {
  defaults: () => ({
    role: "member" as Role,
    tenantId: TenantGenerator.default().id,
    emailVerified: true,
  }),

  create(overrides: Partial<User> = {}): User {
    const name = overrides.name ?? nextName("user");       // "user-7"
    return {
      ...UserGenerator.defaults(),
      id: overrides.id ?? identity("usr", name),            // "usr_user-7"
      name,
      email: overrides.email ?? `${slug(name)}@example.test`,
      ...overrides,
    };
  },

  admin: (o: Partial<User> = {}) => UserGenerator.create({ role: "admin", ...o }),
  suspended: (o: Partial<User> = {}) =>
    UserGenerator.create({ suspendedAt: FIXED_NOW, ...o }),
};
```

```python
# tests/support/generators/user_generator.py
from dataclasses import replace

class UserGenerator:
    @staticmethod
    def create(**overrides) -> User:
        name = overrides.pop("name", None) or next_name("user")
        base = User(
            id=identity("usr", name),
            name=name,
            email=f"{slug(name)}@example.test",
            role="member",
            tenant_id=TenantGenerator.default().id,
        )
        return replace(base, **overrides)

    @staticmethod
    def admin(**overrides) -> User:
        return UserGenerator.create(role="admin", **overrides)
```

```csharp
public static class UserGenerator
{
    public static User Create(Action<UserDraft>? customize = null)
    {
        var name = Names.Next("user");
        var draft = new UserDraft
        {
            Id = Identity.For("usr", name),
            Name = name,
            Email = $"{Slug.Of(name)}@example.test",
            Role = Role.Member,
        };
        customize?.Invoke(draft);
        return draft.Build();
    }

    public static User Admin(Action<UserDraft>? customize = null) =>
        Create(d => { d.Role = Role.Admin; customize?.Invoke(d); });
}
```

```go
func NewUser(t *testing.T, opts ...UserOption) User {
    t.Helper()
    name := generator.NextName("user")
    u := User{
        ID:    generator.Identity("usr", name),
        Name:  name,
        Email: generator.Slug(name) + "@example.test",
        Role:  RoleMember,
    }
    for _, opt := range opts {
        opt(&u)
    }
    return u
}
```

Three platform notes, not rules: an overrides object is the cheapest cross-language shape; a fluent
builder is idiomatic where the language expects it (C#, Java, Kotlin); a functional options list is
idiomatic in Go. The contract is identical in all three.

### 3.3 Object Mother, builder, or generator?

All three are the same idea at different maturity levels. Choose deliberately:

| Pattern | Shape | Good for | Breaks when |
|---|---|---|---|
| **Object Mother** | Static methods per canned case: `createActiveCustomer()` | Very small domains; three or four fixed cases | A test needs one field different → method explosion, or mutable objects to patch |
| **Test Data Builder** | Fluent builder over defaults: `new UserBuilder().WithEmail(x).Build()` | Complex objects; tests that override one or two fields | It exposes every column and turns into a second schema |
| **Generator** | Function/object with defaults, overrides, and named states | Most application suites; a single vocabulary across unit, API, and E2E tests | It hides the fields that matter, or grows business logic of its own |

The recommended default is the **generator** with an overrides object and named state methods. It
scales from one field to a whole aggregate graph and works in every language without inheriting a
builder's ceremony. Adopt a fluent builder only when the host language's idiom (or an existing
codebase) already expects it; do not maintain both.

### 3.4 Identity and uniqueness

Generators must satisfy two properties at once:

- **Unique within a run** — parallel tests that insert users must not collide on a unique index.
  Use a monotonic counter, a test-scoped sequence, or a seeded deterministic suffix. Never a fixed
  `"test@test.com"`.
- **Stable across runs and layers** — the same generated user must have the same id/email/name in
  the API test, the database assertion, and the log line. Derive all of them from one key:

```text
name  = "user-7"
id    = "usr_user-7"
email = "user-7@example.test"
slug  = "user-7"
token = "tok_usr_user-7_web"       # session, derived from id + scope
```

This is **semantic consistency**: the values mean the same thing everywhere because they come from
the same key. A hardcoded `id: "123"` next to `email: "alice@test.com"` is semantically incoherent —
nothing about the row says those two values belong together, and the next person to read a failure
cannot tell which user `123` was.

Rules:

- **One key per instance.** Derive id, email, handle, display name, and any scoped key from it.
- **Unique per call, unless the test asks otherwise.** `UserGenerator.create()` twice gives two
  users; `UserGenerator.same(user)` is an explicit, rare operation.
- **Never reuse a fixed value across entities.** Two different users with `test@test.com` make
  aggregation, joins, and uniqueness assertions meaningless.
- **Namespace by lane or worker when parallel.** A prefix derived from the worker id keeps
  cross-process runs honest without weakening the identity rule.
- **Determinism beats prettiness.** `user-7` is better than a random adjective-noun pair: it is
  greppable, ordered, and reproducible. Use a seeded real-name library only when the domain needs
  realistic names (locale collation, display tests), and still derive the id from the sequence.

### 3.5 Relationships and scenarios

A generator builds one aggregate. A scenario builds the business situation:

```ts
export const Scenario = {
  memberWithExpiredSubscription() {
    const user = UserGenerator.create();
    const plan = PlanGenerator.monthly();
    SubscriptionGenerator.expiredFor(user, plan);
    return { user, plan };
  },
};
```

Rules:

- A scenario returns handles to everything the test may assert on. A scenario that hides the user
  forces the test to re-query, which couples it to the persistence layer.
- Scenarios compose; they do not mutate globals, set environment variables, or register teardown.
  Those belong to fixtures.
- Name the scenario in business language, not in database language: `tenantWithTwoAdmins`, not
  `insertTwoRowsIntoMemberships`.

### 3.6 Generators must not depend on the code under test

The subtle killer: a generator that calls the production factory, validator, or serializer to build
its own input.

```text
UserGenerator.create()  →  UserFactory.create(...)  →  applies business rules
test                    →  asserts the business rules on that user
```

The oracle and the implementation now agree by construction. The test is a tautology: it will pass
even if the rule is deleted, because the input was shaped by the same rule. Build inputs from plain
data and the generator's own defaults. Reuse production code only where it is genuinely dumb
(constructors, value objects, ID types) and say so in the generator's header comment.

---

## 4. Sessions and identity

"Sessions" means two different things in a test suite, and conflating them produces some of the
strangest failures in the genre.

| Kind | What it is | Who owns it | Naming rule |
|---|---|---|---|
| **Auth session** | The authenticated actor: token, cookie, claims, tenant, roles | `SessionGenerator` | `authSession`, `session` |
| **Test/DB session** | The lifecycle container for a test: transaction, connection, scope | Fixture/harness | `dbSession`, `testScope` |

Keep the names distinct in code. A `session` variable that sometimes means a cookie and sometimes
means a database transaction is a semantic bug waiting for a reader.

**Auth sessions must be derived from the user, never invented:**

```ts
export const SessionGenerator = {
  forUser(user: User, scope: SessionScope = "web"): AuthSession {
    return {
      userId: user.id,
      tenantId: user.tenantId,
      token: `tok_${user.id}_${scope}`,       // deterministic, traceable
      scope,
      issuedAt: FIXED_NOW,
      expiresAt: plusHours(FIXED_NOW, 1),
    };
  },
};
```

Why this matters:

- A hardcoded `token: "test-token"` for two different users makes an authorization test pass for
  the wrong reason — the session does not actually identify anyone.
- A session that carries `userId` but a tenant from somewhere else breaks multi-tenant tests in a
  way that looks like a permissions bug.
- A token derived from the user id makes failures readable: `tok_usr_user-7_web` tells you exactly
  whose request failed.
- Expiry is a domain fact. Generate it from the injected clock (`expiredFor(user)`,
  `expiringIn(user, minutes(5))`) rather than `Date.now() + 3600`, which silently changes meaning
  as the suite runs.

If the product rotates tokens on every issue, model that explicitly (`SessionGenerator.rotated()`),
and keep the stable identity (`userId`) as the assertion target. Never assert a random token value.

---

## 5. Anti-patterns

| The shortcut | Why it hurts | Correction |
|---|---|---|
| One `seedTestData()` for the whole suite | Everything depends on everything; one edit breaks all | Fixtures per concern + generators per instance |
| Shared mutable rows | Order dependence; parallel collisions | Fresh rows per test |
| Generator with required arguments for every field | Tests repeat the schema; noise hides intent | Valid defaults + overrides |
| Generator that exposes 40 setters mirroring columns | Second schema to maintain; leaks storage into tests | Named states + only the fields tests legitimately vary |
| Fixed `"test@test.com"` / `id: 1` | Collisions, meaningless joins, unreadable failures | Derived, unique identity |
| `Date.now()` inside a generator | Non-deterministic expiry and ordering | Injected `Clock`; fixed instant |
| Random names without a seed | Irreproducible failure, ungreppable logs | Counter or seeded sequence; print the seed |
| Generator calls the SUT to build input | Tautological test | Build from plain data |
| Fixture class with 300 lines of setup | Nobody knows what matters; slow | Split by resource; scenarios for situations |
| Teardown "best effort" that swallows errors | Next test inherits corruption | Report teardown failure loudly |
| Session token shared across users | Authorization tests pass for the wrong reason | Derive from user identity |
| `sleep` after seeding "to let it settle" | Flaky and slow | Await the write / poll the condition |
| Test re-queries what the generator returned | Couples test to persistence; hides generator bugs | Return the built instance |
| Generator defaults drift from schema | Valid-looking input rejected at runtime | One schema-derived source; a conformance test |

---

## 6. Review checklist

- [ ] Every aggregate has exactly one generator, in one home.
- [ ] `create()` with no arguments is valid against the current schema.
- [ ] Identity (id, email, handle, token) is derived from one key and unique per call.
- [ ] Special states are named in business language, not status strings.
- [ ] Sessions are generated from a user and carry that user's tenant and roles.
- [ ] No generator calls the code under test to build its input.
- [ ] Fixtures share infrastructure only; mutable state is fresh per test.
- [ ] Teardown runs on failure, is idempotent, and never swallows errors.
- [ ] No fixed sleep anywhere in setup.
- [ ] A conformance test fails when a required field is added without a generator default.
