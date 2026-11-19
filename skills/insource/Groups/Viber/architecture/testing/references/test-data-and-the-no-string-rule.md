# Test Data and the No-String Rule

Test data is the largest, least reviewed part of most suites. It is also the part that decides
whether a change costs one edit or forty. This reference states the rule, the data ownership model
behind it, and how to enforce both without turning tests into an abstraction exercise.

---

## 1. The rule

> **No-String Rule.** A test body may not contain a literal that carries domain meaning.
> Identifiers, names, emails, statuses, amounts, dates, tokens, and expected domain strings are
> produced by a named generator, a named constant, or a value derived from an instance that was
> already built. The test names intent; the generator supplies value.

Inspired by functional programming's preference for composition over repetition: the value is not
the point, the relationship is. `"alice@test.com"` repeated in nine files is nine independent
decisions that happen to look alike. One generator is one decision with nine readers.

The rule applies to test bodies, fixture setup, scenario builders, and page objects. It does not
apply to production code, and it does not apply inside the generator's own defaults — those are the
one place a literal is *supposed* to live.

### 1.1 What the rule is not

- It is not "no literals anywhere". Boundary values, malformed inputs, and structural syntax are
  legitimate and often necessary (see §6).
- It is not "hide every value behind an abstraction". A named constant declared at the top of the
  test file is compliant and often better than a generator when the value has no domain identity.
- It is not "assert the variable you just passed in". That produces tautologies; see §5.3.

---

## 2. Why

| Cost of the hardcoded value | What it looks like | What the rule changes |
|---|---|---|
| **Change amplification** | A new required field or format change means editing every test file | one generator default changes; the suite follows |
| **Collision** | Parallel tests insert the same email/id and hit a unique index | identity is generated per call |
| **Lost meaning** | `id: "123"` next to `email: "alice@test.com"`; nothing ties them together | both derive from one key |
| **Unreviewable data** | A reviewer cannot tell which values matter to the test | overrides highlight exactly the relevant fields |
| **Oracle drift** | The expected string is a copy of the input; both change together, nothing is verified | expectations derive from the rule, not the object |
| **Search cost** | "Where is this user defined?" has no answer | one generator file, one grep |
| **Privacy risk** | Real names, emails, or customer ids pasted from production | synthetic data by construction |
| **Locale/timezone drift** | `"2024-01-01"` means different instants on different hosts | dates come from the clock/date generator |

The deeper reason is architectural: **a test is a specification, and a specification with magic values
is a specification nobody can review.** Naming the value is the same act as naming the rule.

---

## 3. Single source of truth

Test data is not one thing. It has five layers, and each needs exactly one home:

| Layer | The fact | One home | Example |
|---|---|---|---|
| **Schema** | What fields exist, their types, constraints | migration / schema definition | `users.email` is unique, required |
| **Vocabulary** | Statuses, roles, plans, error codes, limits | domain enum/constant module | `Role.Admin`, `Reason.SubscriptionExpired` |
| **Instance data** | A valid user, order, tenant, session | `<Aggregate>Generator` | `UserGenerator.create()` |
| **Scenario data** | A named business situation | `tests/scenarios/` | `memberWithExpiredSubscription()` |
| **Expected output** | The value the assertion compares against | derived from the rule, or a named fixture | `plan.priceFor(seats)` |

Rules that keep the layers honest:

1. **One fact, one home.** If the max seat count lives in a constant, a database check, a validator,
   and a test, the test must import the constant — not retype `4`.
2. **Tests import the authority; they do not paraphrase it.** Retyping an enum value as a string is
   a second definition, even when it is spelled identically today.
3. **Generators are the only instance factory.** A test that constructs a domain object by hand
   bypasses every default and every future field.
4. **No cross-layer copies.** The API test and the database test must agree because they use the
   same generator, not because someone updated both.
5. **Data files are data, not code.** A JSON/YAML/CSV case table is a valid home for parameterized
   cases; it still needs a schema and a loader, and it must not contain values that another
   generator already owns.

The failure this prevents is specific and common: a domain change lands, the compiler catches the
production call sites, and forty tests fail because each one independently encoded the old shape.
The compiler cannot see strings. The generator is how the test suite gets a compiler.

---

## 4. Semantic consistency

Numbers and strings are cheap; meaning is expensive. A suite is semantically consistent when every
value means the same thing everywhere it appears, and different things never share a value.

### 4.1 Identity derives from one key

```text
key    = "user-7"                 (unique, stable, greppable)
name   = "User 7"                 (display, derived)
id     = "usr_user-7"             (primary key, derived)
email  = "user-7@example.test"    (unique constraint, derived)
handle = "user-7"                 (routing, derived)
token  = "tok_usr_user-7_web"     (session, derived from id + scope)
tenant = "tenant_default"         (or TenantGenerator for a specific tenant)
```

Every downstream value is a function of the key. That is what makes a failure message readable: a
401 for `tok_usr_user-7_web` names the actor, the tenant, and the scope without a lookup.

### 4.2 Same meaning, same value; different meaning, different value

| Situation | Wrong | Right |
|---|---|---|
| Two different users in one test | both `"test@test.com"` | `UserGenerator.create()` twice |
| The same user across API and DB assertions | API builds one, DB builds another | one instance, passed through |
| A user and their session | unrelated `userId` and `token` | `SessionGenerator.forUser(user)` |
| A tenant and its members | members with no `tenantId` | `UserGenerator.inTenant(tenant)` |
| An order and its owner | `customerId: "cust_1"` | `OrderGenerator.forUser(user)` |

The failure mode this prevents is subtle: a query that joins on email returns the wrong row because
two fixtures share the value, and the test passes for the wrong reason. Duplicate hardcoded values do
not just make edits expensive; they make assertions ambiguous.

### 4.3 Hardcoded values defeat parallel execution

Parallel runners amplify any shared literal. Two workers inserting `"admin@test.com"` collide on the
unique index; one test's cleanup deletes the other's row. Generated identity with a per-worker or
per-test sequence removes the class of failure entirely. This is one of the few testing decisions
that is cheaper *and* more correct.

---

## 5. Applying the rule

### 5.1 Before and after

```text
BEFORE                                          AFTER
──────────────────────────────────────────      ──────────────────────────────────────────
const user = {                                  const user = UserGenerator.create();
  id: "u1",                                     const admin = UserGenerator.admin();
  email: "alice@test.com",                      const session = SessionGenerator.forUser(admin);
  role: "admin",
};
const session = { userId: "u1", token: "abc" };

await api.post("/users", {                      await api.post(Routes.users(), {
  email: "bob@test.com",                          email: UserGenerator.create().email,
  role: "member",                                 role: Role.Member,
});                                             });
```

The second version says what the test is about. The reader can see that the email is irrelevant
(any valid one) and that the role is the subject. The first version makes both look equally
important, which is false.

### 5.2 The three compliant sources of a value

1. **A generator** — when the value belongs to a domain instance. `UserGenerator.create().email`.
2. **A named constant or enum** — when the value is a vocabulary fact. `Role.Admin`,
   `MAX_SEATS`, `Routes.users()`.
3. **A derivation from an existing instance** — when the value is a property of something already
   built. `user.email`, `order.id`, `session.userId`.

Anything else is a literal that must justify itself (§6).

### 5.3 The tautology trap

Replacing a literal with a generator can produce an assertion that cannot fail:

```text
OK    expect(created.email).toBe(KNOWN_EMAIL)        // a named, known value
BAD   expect(created.email).toBe(created.email)      // asserts nothing
BAD   expect(result).toEqual(UserGenerator.create()) // two generated users never match
```

Two rules keep the rule honest:

- **Assert a rule, not a copy.** If the expected value must equal the input, make the input a named,
  known value (a boundary, a fixed fixture) and state why. Round-trip tests are legitimate; copying
  the object under test into both sides is not.
- **Derive the expectation independently.** For a price, compute `unitPrice * quantity` from named
  values; do not read the total back from the result and compare it to itself.

The No-String Rule is about where values come from. It is not permission to stop thinking about
what the assertion means.

### 5.4 Parameterized cases

When the same rule has many inputs, use a case table with named columns. The table is the single
source of truth for those cases; each row names the boundary it represents.

```ts
const SEAT_PRICE = Money.usd(10);
const CASES = [
  { name: "zero seats",       seats: 0,            expected: Rejected.RequiresSeat },
  { name: "one seat",         seats: 1,            expected: Ok(SEAT_PRICE) },
  { name: "plan maximum",     seats: MAX_SEATS,    expected: Ok(SEAT_PRICE.times(MAX_SEATS)) },
  { name: "one past maximum", seats: MAX_SEATS + 1, expected: Rejected.TooManySeats },
];

for (const c of CASES) {
  it(`prices ${c.name}`, () => {
    expect(checkout(c.seats)).toEqual(c.expected);
  });
}
```

The loop is the runner's parameterization, not control flow in a test body. The case name appears in
the failure output, which is the point.

### 5.5 Custom behavior without spreading changes

This is the payoff: because values live in generators, new behavior is added once and inherited
everywhere:

| Change | Without the rule | With the rule |
|---|---|---|
| Add a required `displayName` field | edit every construction site in every test | one generator default; conformance test proves it |
| Change the default tenant | hunt through fixtures | one `defaults()` entry |
| Add a "trial expired" state | inline date arithmetic in five tests | one `trialExpired()` state method |
| Switch currency formatting | update expected strings across suites | one money generator / formatter constant |
| Introduce a new role | retype the string in each suite | one enum value; tests that must change fail loudly |
| Change the ID scheme | mass find/replace with false positives | one `identity()` function |

The generator is also the place to encode *behavioral* helpers that would otherwise be duplicated:
`withOrders(n)`, `inTenant(t)`, `withExpiredTrial()`, `asSuspended()`. Those are not test logic; they
are the vocabulary of the domain's states. Adding one does not require editing any existing test.

The limit: do not move assertion logic into generators. A generator that asserts is a test with a
misleading name, and its failures point at the wrong file.

---

## 6. Legal literals

Three classes are allowed, and each should still be obvious to a reader:

1. **The value under test.** `0`, `-1`, `""`, `MAX_SEATS + 1`, `i32::MAX`, `null`. The literal *is*
   the boundary being probed. Name it when it is not self-evident.
2. **The malformed value whose wrongness is the point.** `const MISSING_AT = "not-an-email";`,
   `const NEGATIVE = "-1";`. Name it; never inline it, because a bare malformed value looks like a
   typo.
3. **Structural syntax.** Route templates (`"/api/users"` — preferably from a route registry), regex
   patterns, SQL fragments, format strings, file extensions. These describe shape, not domain data.

Everything else is a finding. The review question is not "is this string a literal?" but **"does
this literal carry a fact the project already knows somewhere else?"** If yes, it must come from
that home. If no, it may become a named constant in the test file — and if it is used twice, it
belongs in the shared vocabulary.

---

## 7. Enforcement

A rule that lives only in a document is a preference. Enforce it at three levels, cheapest first:

1. **Review checklist.** One line: "Does this test contain a domain literal that a generator,
   constant, or derivation should own?" This catches semantics a machine cannot.
2. **Conformance test (preferred).** A test that scans test sources for patterns that are almost
   always violations — email literals, UUID literals, ISO dates, `user_`/`usr_` ids, `test@` — and
   fails with file and line. Allow an explicit escape comment with a reason:

   ```ts
   const MALFORMED = "not-an-email"; // no-string-ok: the malformed value is the subject
   ```

   The scanner is a test like any other: it must prove it can fail (see the sanity-floor rule in
   [test-organization.md](test-organization.md)).
3. **Lint rule / CI gate.** A lint rule that bans string literals in `tests/**` outside an allowlist
   is the strictest form; it is worth it only after the suite has been migrated. During migration,
   use a **ratchet**: a conformance test that counts violations and fails when the count rises. A
   ratchet converts a legacy suite without a big-bang rewrite and without accepting new debt.

Migration order that works:

```text
1. Create tests/support/generators/ and one generator for the most duplicated aggregate.
2. Convert the tests that already fail most often; they pay back immediately.
3. Add the conformance scanner with a baseline count.
4. Convert one module per change; lower the baseline each time.
5. When the baseline reaches zero, flip the scanner to a hard gate.
```

Do not attempt a suite-wide mechanical rewrite first. It destroys the ability to tell which test
protected which rule, and it hides real regressions inside a thousand-line diff.

---

## 8. Anti-patterns

| Pattern | Symptom | Fix |
|---|---|---|
| **String zoo** | Every test invents its own user, order, email | One generator per aggregate |
| **Copy-paste fixture** | The same 20-line object in six files, drifting | Import the generator; override one field |
| **Magic id** | `id: 1`, `"u1"`, `"123"` with no meaning | Identity derived from a key |
| **Shared literal across entities** | Two users with one email | Unique per call |
| **Expected-value copy** | Assertion compares the object to itself | Derive the expectation from the rule |
| **Generator as oracle** | Generator calls production logic to build input | Build from plain data |
| **Abstraction for its own sake** | A `StringFactory` for `"USD"` | Use the domain constant directly |
| **Hidden default that matters** | Test depends on a default the reader cannot see | Override it in the test; defaults are for irrelevance |
| **Case table with anonymous rows** | Row 7 failed; nobody knows what row 7 is | Name every case |
| **Data file with stale schema** | Fixture parses but fields are ignored | Schema-validate the file; conformance test |
| **Test data from production** | Real PII in the repo; brittle values | Synthetic generators |

---

## 9. Checklist

- [ ] Every domain value in a test traces to a generator, a named constant, or a derivation.
- [ ] Each aggregate has one generator and one identity rule.
- [ ] Two different entities never share an id, email, or token.
- [ ] Expected values are derived from the rule, not copied from the result.
- [ ] Parameterized cases have named rows.
- [ ] Legal literals (boundaries, malformed inputs, syntax) carry a name or an escape comment.
- [ ] A conformance test or lint gate can fail on a new hardcoded domain value.
- [ ] Changing a generator default updates the whole suite without touching test bodies.
