# Walkthrough: Applying the Testing Pillar

A walkthrough of one real-shaped suite: an order/checkout service with a REST API, a Postgres
database, a payment provider, and an existing test tree that "mostly works". The point is the
sequence of decisions, not the framework.

---

## Step 0: Recon (what the agent reads before asking anything)

```text
tests/
├── api/checkout.test.ts          ← 40 tests, 600 lines
├── db/orders.test.ts             ← creates its own tables with CREATE TABLE
├── e2e/checkout.spec.ts          ← 3 journeys, 8 minutes
└── helpers.ts                    ← seedTestData(), seedAdmin(), seedCart() ...

findings
────────
· "test@test.com" appears 23 times; 4 users share it
· user ids are "1", "2", "u1", "abc" depending on the file
· 11 × sleep(500) after seeding
· seedTestData() inserts 30 rows globally, never cleaned
· 3 tests pass only when run after checkout.test.ts
· the payment provider is mocked in 9 files, each with a different fake
· coverage is 91%, but 60% of tests have no assertion on the result
```

The recon output is the interview agenda. Nothing below is asked; it is inferred.

---

## Step 1: Lanes and budget (decided with the user)

| Lane | Folder | Environment | Timeout | Blocks merge |
|---|---|---|---|---|
| Unit | `tests/<module>/` | hermetic | 5 s | yes |
| Integration | `tests/db/`, `tests/api/` | local Postgres container | 60 s | yes |
| Contract | `tests/contract/` | real gateway, fake provider | 60 s | yes |
| End-to-end | `tests/e2e/` | full stack | 10 min | nightly |
| Live | `*.live.test.*` | real provider | 10 min | no |

Decision: **no network in the default run**. The payment provider is wrapped in a
`PaymentGateway` adapter; tests fake the adapter, never the SDK.

---

## Step 2: One data home

```text
tests/support/
├── generators/
│   ├── user.generator.ts
│   ├── order.generator.ts
│   ├── session.generator.ts
│   └── tenant.generator.ts
├── scenarios/
│   ├── member-with-expired-trial.ts
│   └── tenant-with-two-admins.ts
└── harness/
    ├── database.ts
    └── payment-gateway.fake.ts
```

Generator sketch (TypeScript; the Python/C#/Go equivalents are in
[fixtures-and-generators.md](../references/fixtures-and-generators.md) §3.2):

```ts
export const UserGenerator = {
  create(overrides: Partial<User> = {}): User {
    const key = nextKey("user");                     // "user-7"
    return {
      id: identity("usr", key),                      // "usr_user-7"
      name: `User ${key.split("-")[1]}`,
      email: `${key}@example.test`,                  // "user-7@example.test"
      role: Role.Member,
      tenantId: TenantGenerator.default().id,
      emailVerified: true,
      ...overrides,
    };
  },
  admin: (o: Partial<User> = {}) => UserGenerator.create({ role: Role.Admin, ...o }),
  suspended: (o: Partial<User> = {}) =>
    UserGenerator.create({ suspendedAt: CLOCK.now(), ...o }),
};
```

The identity rule is the whole design: `id`, `email`, `name`, and any session token derive from
`key`, so a failure that prints `usr_user-7` is immediately readable.

```text
BEFORE                                     AFTER
─────────────────────────────────────      ───────────────────────────────────────
const user = {                             const user = UserGenerator.create();
  id: "u1",                                const session = SessionGenerator.forUser(user);
  email: "alice@test.com",
  role: "admin",                           expect(session.userId).toBe(user.id);
};                                         expect(session.token).toContain("user-7");
const session = { userId: "u1", token: "abc" };
```

`alice@test.com` is gone, and the session is now provably that user's session rather than a string
that happens to be nearby.

---

## Step 3: Fixture lifecycle

```ts
// suite setup (once): one engine, one migrated template, shared read-only
const db = await startPostgres({ template: MIGRATED_TEMPLATE });

// per test: reset the mutable world, run, reset again even on failure
export async function withCleanDatabase<T>(fn: (db: Db) => Promise<T>): Promise<T> {
  await truncateAll(db);                                  // resets rows and sequences
  try {
    return await fn(db);
  } finally {
    await truncateAll(db);
  }
}
```

The alternative — wrapping each test in a transaction and rolling back — is faster, but it
silently fails when the service under test commits through its own pool. That is why this project
chose truncate over rollback; the choice is recorded in `testing-architecture.md` §4 rather than
rediscovered per test.

```text
isolation proof (runs every suite)
──────────────────────────────────
it("does not leak rows between tests", ...)
  1. insert one order
  2. end the test
  3. next test asserts orders.count() == 0
```

The old `seedTestData()` is deleted. Three scenarios replace it, each returning its handles:

```ts
const { user, plan, subscription } = Scenario.memberWithExpiredTrial();
expect(checkout(cart, user)).toEqual(Rejected(Reason.TrialExpired));
```

No `sleep(500)`: the seeder awaits the insert, and the checkout awaits the adapter. If a real async
boundary appears, poll the observable condition with a bounded timeout; never add a delay.

---

## Step 4: The session rule in one assertion

```text
BEFORE                                        AFTER
────────────────────────────────────────      ────────────────────────────────────────
token = "test-token"                          const account = UserGenerator.create();
GET /me  Authorization: Bearer test-token     const auth = SessionGenerator.forUser(account);
expect(body.role).toBe("admin")               GET /me  Authorization: Bearer ${auth.token}

                                              expect(body.userId).toBe(account.id)
                                              expect(body.tenantId).toBe(account.tenantId)
                                              expect(body.role).toBe(account.role)
```

The old test passed for the wrong reason: a global token happened to map to an admin. The new test
fails if the session does not carry the user's identity, which is the actual contract.

Session expiry uses the injected clock, not arithmetic on `Date.now()`:

```ts
const expired = SessionGenerator.expiredFor(user);   // issuedAt = FIXED_NOW - 2h, expiresAt = -1h
expect(api.me(expired.token)).toEqual(Unauthorized(Reason.SessionExpired));
```

---

## Step 5: Contract and corpus

The payment adapter has one fake, built to the provider's published error shapes:

```ts
export class FakePaymentGateway implements PaymentGateway {
  constructor(private readonly behavior: "approve" | "decline" | "timeout" = "approve") {}
  async capture(intent: PaymentIntent): Promise<CaptureResult> { ... }
}
```

Contract tests drive the real HTTP gateway in-process against that fake, so routing, middleware, and
serialization are real while the third party stays deterministic:

```ts
const res = await app.fetch(new Request(`${base}/checkout`, {
  method: "POST",
  headers: { authorization: `Bearer ${SessionGenerator.forUser(user).token}` },
  body: JSON.stringify({ cartId: cart.id }),
}));
expect(res.status).toBe(402);
expect(await res.json()).toMatchObject({ reason: "card_declined" });
```

For a provider whose response bytes matter, replay from the corpus instead. The corpus has a
manifest, a digest test, and an orphan check (see
[test-organization.md](../references/test-organization.md) §7). The parser test asserts shape and
absence, never a price: the provider owns that value and it moves.

---

## Step 6: Executable architecture

Two conformance tests are enough to hold the new rules:

```ts
// tests/conformance/no-string.spec.ts
const DOMAIN_LITERAL = /(@(?:test|example)\.(?:com|test)|"usr_[^"]*"|"\d{4}-\d{2}-\d{2}")/;
const ALLOW = /no-string-ok:/;

it("discovers test sources", () => {
  expect(listTestFiles().length).toBeGreaterThan(50);     // sanity floor
});

it("test bodies contain no domain literals", () => {
  const hits = listTestFiles()
    .filter((f) => !ALLOW.test(read(f)))
    .filter((f) => DOMAIN_LITERAL.test(read(f)));
  if (hits.length) throw new Error(format(hits));         // file:line
});
```

```ts
// tests/conformance/schema.spec.ts
it("every required column has a generator default", () => {
  const required = requiredColumns("orders");             // read from the migration
  const built = OrderGenerator.create();                  // must satisfy every constraint
  for (const column of required) expect(built).toHaveProperty(column);
  expect(() => validateOrder(built)).not.toThrow();
});
```

The first prevents the string zoo from returning. The second is what makes a required-field change
cost one edit instead of forty. Both have sanity floors so a path typo cannot pass vacuously.

---

## Step 7: CI lanes

```yaml
# shape, not a vendor file
on: pull_request
  - run: <runner> --lane unit --lane integration --lane contract --randomize-order
  - run: tsc -p tests --noEmit            # test code is compiled too
  - run: <runner> --lane conformance

nightly:
  - run: <runner> --lane e2e
  - run: <runner> --lane stress
  - run: <mutation tool> --include "src/core/**"
  - run: <quarantine report> --fail-on-expired
```

The pull request never touches the network or a shared database. The nightly lane owns the expensive
proof. A quarantined test that passes its expiry fails the nightly, which is the only thing that
makes quarantine temporary.

---

## Step 8: Output

```text
docs/testing-architecture.md
  §2  lanes and budgets              ← the table above
  §3  directory and naming contract
  §4  harness and fixture isolation  ← template DB + rollback + isolation proof
  §5  generator registry             ← User, Order, Session, Tenant + identity rules
  §6  data ownership + No-String Rule ← owners table + scanner
  §7  doubles policy                 ← fake PaymentGateway, real app, injected clock
  §8  determinism contract           ← fixed clock, pinned locale/zone, no sleeps
  §9  conformance tests              ← no-string, schema defaults, corpus digest
  §10 corpus rules
  §11 quarantine policy
  §12 sync points
```

Registered in UNITS.md: `UserGenerator`, `SessionGenerator`, `Scenario`, `withDatabase`,
`FakePaymentGateway`, `no-string.spec`. Sync points: generator registry (doc + code + UNITS),
lane table (doc + CI), corpus rules (doc + corpus README).

The suite now has fewer tests than before. It also has fewer reasons to lie.
