# Failure Modes and Anti-Patterns

A catalog of the ways settings and plugin systems go wrong, how each looks in production, and the
check that catches it. Use it for review, for a migration plan, and for the "what did we miss" pass.

---

## 1. Failure Modes

| # | Failure | Symptom | Root cause | Fix | Check |
|---|---|---|---|---|---|
| 1 | **Dead setting** | Turning it off changes a number on disk; behavior ignores it | A row was added, its consumer never was | Add the reader, or delete the row | Every key has a call-site consumer |
| 2 | **Hidden setting** | A magic constant changes behavior; no row exposes it | A consumer was added after the catalog froze | Add a descriptor, or document why it is fixed | Every magic config value has a row or a decision |
| 3 | **Scope drift** | A row says "all platforms" but edits one | Caller chose `get` versus `getGlobal` by hand | Route every read through the scope seam | Literal scopes at call sites equal the catalog |
| 4 | **Default drift** | The row advertises 60; the service defaults to 30 | Two literals for one fact | One shared constant or a context fact | Catalog defaults equal service fallbacks |
| 5 | **Copy drift** | The hint describes behavior the code does not have | Copy outlived a behavior change | Copy lives on the row; a test pins the behavior | Consumer test asserts the described effect |
| 6 | **Same-specificity collision** | A label flips depending on registration order | Order used as a tie-breaker | Fail loudly, name both layers, add a tie-breaker | Two patches on one field throw |
| 7 | **Stale override crash** | Deleting a base row breaks a module | Override assumes the key exists | Drop and report ignored overrides | Removing a base row keeps the host green |
| 8 | **Ghost row** | A removed plugin still shows a row or route | Registry not rebuilt from live contributions | Enumerate the registry; never cache a removed item | Deleting a contribution removes its surface |
| 9 | **Boolean explosion** | N feature flags with impossible combinations | One boolean per feature instead of a mode | A single state or enum; one writer | No impossible combination is representable |
| 10 | **Set invariant split** | A crash can leave every platform disabled | N booleans for one set invariant | Store the disabled set atomically | Crash test cannot produce an empty enabled set |
| 11 | **Type loss** | A boolean comes back as the string "true" | Key-value store coercion | Typed reads plus a stored value kind | Round-trip type test |
| 12 | **Composite value** | `$12` and `12 USD` in one column; sums fail | Formatting stored as data | Split amount and currency; unit and value | No symbol or unit word in storage |
| 13 | **Secret in settings** | A token appears in an export or a log | Settings used as a secret store | Store a reference; secret lives in a manager | Secret scan of store, export, logs |
| 14 | **Silent enum drift** | A stored ordinal now means another option | Ordinals persisted; enum reordered | Store stable names or codes | Reordering options does not change meaning |
| 15 | **Unknown value fatal** | A removed platform id crashes the page | Parser treats unknown as invalid | Unknown is inert; skip and report | Unknown id fixture renders normally |
| 16 | **Renderer branch leak** | Shared UI contains `if platform == "x"` | A row needed special handling | Add a shape or a visibility flag | Shared renderer contains no concrete names |
| 17 | **Runtime code on mobile** | Review rejection or a broken update | Downloadable executable plugin | Build-time code; runtime data only | Release target has no dynamic code path |
| 18 | **Unsigned plugin** | Arbitrary code runs with host authority | Trust assumed, not enforced | Signature, allowlist, capability tokens | Unsigned or unlisted plugin fails closed |
| 19 | **Version skew** | A plugin calls a removed host method | No contract version or window | Versioned contract, compatibility check | Oldest supported plugin passes CI |
| 20 | **Plugin takes host down** | One failure stops the app loop | No boundary, timeout or breaker | Isolate, time out, disable with a reason | Fault-injection test keeps the host alive |
| 21 | **Order by registration** | Output differs between builds | Dictionary or file order | Explicit rank plus stable key tie-break | Shuffled registration yields the same list |
| 22 | **Migration overwrite** | A scope move discards the user's value | Harvest wrote over a newer global value | Explicit value wins; harvest is idempotent | Fixture with both values keeps the newer |
| 23 | **Read-time rewrite** | A read mutates the store or loses data | Migration in the read path without fallback | Read-through then write-on-first-save | Read is side-effect free |
| 24 | **Validation mismatch** | The UI accepts 16; the pool rejects above 4 | Row and consumer disagree on bounds | Bounds come from one source | Range test across both layers |
| 25 | **Config precedence ambiguity** | Two layers disagree; behavior changes by load order | Undocumented precedence | Document defaults, env, context, user order | Precedence test per layer |
| 26 | **Catalog made executable** | A remote row injects a template or query | "It is just data" assumption | Validate schema; never evaluate data as code | Remote catalog with a malicious field is rejected |
| 27 | **Hot reload leak** | Timers and listeners multiply | Activation not paired with cleanup | Lifecycle with idempotent deactivate | Reload N times; count stays constant |
| 28 | **Orphan key** | Renamed setting leaves old values forever | No alias or cleanup window | Read alias, migrate on write, retire later | Old key fixture still reads |

---

## 2. Anti-Patterns

### 2.1 The God Settings Class

One class holds every value, serializer, default and validation rule. It grows without bound and every
feature edits it.

- Symptom: merge conflicts in one file; unrelated tests fail together.
- Fix: descriptor rows plus per-domain consumers; the class becomes a thin facade or disappears.

### 2.2 The Hand-Built Settings Page

Each row is a control in a layout; adding a setting edits the layout, the view-model and every
platform's layout.

- Symptom: two layouts drift; a row exists on desktop and not mobile.
- Fix: descriptor catalog plus a closed renderer vocabulary.

### 2.3 The `if Platform` Page

The shared renderer branches on a platform, tenant or setting name.

- Symptom: a new platform needs a renderer edit; a name appears in shared code.
- Fix: data on the row (`shape`, `visibilityFlag`, options), or a module contribution.

### 2.4 Feature Flags as Settings

A temporary rollout switch lives on the user settings page forever, with no owner and no expiry.

- Symptom: dozens of toggles nobody understands; no one dares remove one.
- Fix: a flag service with owner and expiry; the settings page shows only user-facing preferences.

### 2.5 Settings as a Secret Store

A token, connection string or cookie is persisted as an ordinary preference.

- Symptom: a secret appears in an export, a backup, a log or a screenshot.
- Fix: secret manager plus a reference; the row edits the reference through a dedicated flow.

### 2.6 The Settings Blob

One JSON column holds everything, untyped and unvalidated.

- Symptom: a typo silently becomes a new key; no one knows the schema.
- Fix: typed rows or a validated document with a version and a schema.

### 2.7 The Plugin That Edits the Host

A contribution mutates the base list, unregisters another plugin, or writes host state.

- Symptom: activation order changes behavior; removal deletes unrelated rows.
- Fix: immutable contributions; the registry owns the only collection; patches are field-scoped.

### 2.8 Runtime Everything

Every behavior is dynamically loaded "for flexibility", including on mobile, with no signature.

- Symptom: startup failures, review rejection, unreproducible builds.
- Fix: build-time by default; runtime only with a written reason and trust model.

### 2.9 The Silent Merge

Two contributions set the same field and one wins by chance.

- Symptom: a label or bound is wrong on one context, intermittently.
- Fix: same-specificity failure; explicit tie-breaker layer.

### 2.10 The Copy-Paste Second Page

A new platform or tenant gets a forked settings page.

- Symptom: fixes must be applied twice; features diverge.
- Fix: contribution registry; shared renderer.

### 2.11 The Row With No Owner

A read-out, stat or action row has no module, no command and no data source.

- Symptom: renders empty forever; tests assert an empty string.
- Fix: each row names its owner (a descriptor source or a command); delete it otherwise.

### 2.12 The Consumer Without a Row

A hardcoded constant controls behavior and is invisible to the user.

- Symptom: "why is it 30 seconds?"; support cannot change it.
- Fix: expose it as a row, or record a decision that it is deliberately fixed.

---

## 3. Review Checklist

### Host

- [ ] The host imports no concrete contribution by name.
- [ ] The registry is the only collection of contributions.
- [ ] Composition is one pure function with a deterministic result.
- [ ] The renderer draws a plain composed list; no composition inside the renderer.
- [ ] The shape and scope vocabularies are closed and documented.

### Contribution

- [ ] A contribution only adds rows or patches declared fields.
- [ ] Module-local keys live in the module.
- [ ] A contribution can be deleted without touching shared code.
- [ ] A contribution names no other contribution.

### Settings

- [ ] Every key has one descriptor and at least one reader.
- [ ] Every rendered row comes from the catalog.
- [ ] Every default is shared with the consumer.
- [ ] Every bound matches the consumer's real limit.
- [ ] Visibility is a named predicate, not a renderer branch.

### Storage

- [ ] Every read goes through the scope seam.
- [ ] Values are typed and atomic; no formatted composite.
- [ ] A legacy read-through and a first-write migration exist where scope changed.
- [ ] A set invariant is one atomic value.
- [ ] Unknown ids and keys are inert.
- [ ] Secrets are not in the store, export or logs.

### Growth

- [ ] Adding the Nth setting changes only the catalog and its consumer.
- [ ] Adding the Nth module changes only its file and the composition root.
- [ ] Adding a shape or scope is a deliberate host change with tests.
- [ ] Shuffled registration order produces the same output.

### Runtime (if used)

- [ ] The platform permits it.
- [ ] Code is signed and allowlisted.
- [ ] The contract is versioned with a compatibility window.
- [ ] Failures are isolated, timed out and revocable.
- [ ] A last-known-good set exists.
- [ ] Reload does not leak listeners, timers or workers.

---

## 4. Detection Recipes

Tool-agnostic; use the search tool the project has.

| Target | Search intent |
|---|---|
| Shared code naming a platform | The concrete names in the host and renderer |
| Hand-built rows | UI row construction outside the catalog or renderer |
| Direct container choice | Reads and writes that bypass the scope seam |
| Dead keys | A catalog key with no reference outside the catalog |
| Hidden constants | Numeric or string config near a consumer, not in a descriptor |
| Secret leakage | Key, token, password, cookie and connection-string terms in store and logs |
| Renderer leaks | `if`/`switch` on a setting key, platform or tenant inside shared UI |
| Order dependence | Sort without a stable final tie-break |

A search hit is a lead. Read the code and confirm before reporting it.

---

## 5. Post-Incident Questions

After a settings or plugin incident, answer these in the decision record:

1. Which law or failure mode was violated?
2. Why did no check catch it? Add the check, not just the fix.
3. Was the fix at the seam or at the symptom?
4. Did the fix preserve the OCP gate, or add another special case?
5. Is there a migration or compatibility step still owed?
6. Does the catalog, copy and consumer now agree?
