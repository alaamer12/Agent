# Build-Time vs Runtime Loading

The build-time versus runtime decision is **per axis**, not per application. One product often needs
build-time code, a runtime catalog, runtime values and build-time consumers at the same time. Decide
each row separately and write the reason down.

---

## 1. The Axes

| Axis | Typical payload | Safe default |
|---|---|---|
| **Code** | Parsers, commands, integrations, UI extensions | Build-time |
| **Catalog** | Which settings/plugins exist, sections, copy, order | Runtime data is acceptable |
| **Values** | User or tenant configuration | Runtime by nature |
| **Defaults** | Shipped fallback per row | Build-time constant, overridable by data |
| **Feature flags** | Temporary rollout and kill switches | Runtime with an owner and expiry |
| **Secrets** | Tokens, keys, credentials | Secret manager, never either catalog |
| **Contracts** | Descriptor schema, host API, lifecycle | Build-time and versioned |

A runtime catalog whose rows name build-time shapes is normal. A runtime catalog that injects new
executable behavior is a plugin host, with all of its costs.

---

## 2. Decision Matrix

Score each criterion for the code you are considering. The first column is the safer default.

| Criterion | Build-time wins when | Runtime wins when |
|---|---|---|
| **Author** | First-party team | Third parties or customers author extensions |
| **Change cadence** | Follows app releases | Must change without redeploy |
| **Trust** | Code is reviewed with the app | Code is signed, allowlisted, sandboxed |
| **Target** | Mobile store, AOT, trimming, single-file | Server, desktop, browser with CSP allowance |
| **Isolation** | A crash may fail the app | One plugin must not take the host down |
| **Type safety** | Compile-time checking matters | Contract plus serialization checks suffice |
| **Compatibility** | Everything ships in lockstep | Old and new versions coexist |
| **Discovery** | DI, static registration, linker roots | Manifest scan, dynamic import, remote catalog |
| **Latency** | Startup must be predictable | Install/activate can pay a cost |
| **Support** | The team can support an API | A plugin ecosystem is the product |

When the columns tie, choose build-time. It fails at compile time instead of in production.

---

## 3. Platform Constraints

### Mobile app stores

Apple's App Store rules and Google Play policy restrict downloading and executing code that changes
the app's primary functionality. Interpreters and downloadable scripts are narrow exceptions, not a
plugin strategy.

- A mobile app should treat plugins and executable extensions as **build-time**.
- A runtime *catalog*, copy, defaults and feature flags are fine; they are data.
- A "hot update" that downloads code is a review risk, not an architecture.

### Desktop

Runtime assembly loading, dynamic libraries and bundled runtimes are practical. Still decide trust:
a desktop plugin can read the user's files and network unless the host isolates it.

- Prefer signed packages and an explicit allowlist.
- Load in a child process when the plugin is untrusted.
- Never load an unsigned plugin into the UI process.

### Server and multi-tenant SaaS

Runtime is common but must be tenant-scoped: a plugin activated for tenant A must not see tenant B's
data or mutate the host.

- Enforce tenant identity at the host API, not inside the plugin.
- Give plugins a capability token, not ambient authority.
- Apply resource limits: CPU, memory, time, outbound network.

### Browser

Dynamic `import()` and workers are possible, but CSP, CORS, supply-chain integrity and third-party
script risk apply. Prefer build-time bundling with runtime *configuration*; if runtime code is
required, serve it from your own origin with Subresource Integrity and a strict CSP.

### Serverless and edge

Cold starts and package limits make runtime loading expensive. Build-time wins; runtime data should
be cached and validated.

---

## 4. Discovery Mechanisms

| Mechanism | Fits | Risks |
|---|---|---|
| Constructor injection / DI collection | Build-time, first-party | None significant; linker must keep registrations |
| Static registry in source | Build-time, small sets | Manual list can drift; test it |
| Assembly or package scan | Desktop/server | Reflection, trimming, load failures |
| Dynamic import by path | Browser/Node | CSP, path traversal, version skew |
| Manifest file on disk | Desktop/on-prem | Trust, signing, path traversal |
| Remote catalog (JSON) | Any, data only | Schema drift, tampering, offline behavior |
| Remote code fetch | Trusted server only | Supply chain, sandbox escape, store policy |

A **manifest** is the boundary between data and code. The manifest may be runtime; the code it names
is build-time unless the platform and trust model explicitly allow otherwise.

---

## 5. Contract Versioning

Runtime loading without versioning is a delayed outage.

1. **Version the contract, not the plugin.** `contractVersion` in the manifest; the host declares the
   range it supports.
2. **Additive first.** New optional fields and new extension points; never repurpose an existing field.
3. **Compatibility window.** State how long old plugins remain supported and when they are disabled.
4. **Fail closed on unknown major versions.** Do not guess.
5. **Record the resolved set.** Log plugin id and version at activation; support needs it.
6. **Test the oldest supported plugin** against the current host in CI.

For settings descriptors, the same rules apply in miniature: a stored enum name, not an ordinal; a
stable key; a documented default; unknown keys preserved or ignored, never crashed on.

---

## 6. Lifecycle

```text
discover -> verify -> resolve dependencies -> validate manifest
        -> activate -> configure -> run
        -> deactivate -> unload -> migrate or retire
```

At each step define:

- **Failure policy:** skip, retry, quarantine, disable, or fail the host.
- **Idempotency:** activation after a crash must not duplicate state.
- **Cleanup:** subscriptions, timers, file handles, workers, listeners.
- **State ownership:** plugin state is keyed and removed on uninstall; host state is never deleted by
  a plugin.
- **Rollback:** keep the last-known-good set; a failed update reverts.

For build-time contributions the lifecycle collapses to: register, compose, validate, render, apply.
Keep the same failure vocabulary so the design scales if runtime ever arrives.

---

## 7. Trust Model

Runtime is a trust decision before it is a technical one.

| Question | Required answer for runtime code |
|---|---|
| Who signed it? | A key the host trusts |
| What can it reach? | Only capabilities granted by token |
| What data can it see? | Scoped by tenant and user, enforced by the host |
| What resources can it consume? | Bounded by quotas and timeouts |
| How is it revoked? | Disable by id and version, effective immediately |
| How is it audited? | Activation, capability use, failure, data access |
| How is it updated? | Signed update with a compatibility check |

If any answer is missing, runtime code is not ready. A settings catalog needs none of this because it
cannot execute; keep it that way.

---

## 8. Failure Isolation

A plugin host must survive a bad plugin.

- **Per-plugin boundary:** catch at the host API, return a typed failure, never let an exception cross
  into another plugin or the core loop.
- **Timeouts:** every call from the host into a plugin has a deadline.
- **Circuit breaker:** repeated failure disables the plugin and surfaces a reason.
- **Bulkheads:** separate pools or processes for untrusted work.
- **Last-known-good:** on startup, if the resolved set fails, fall back to the previous set.
- **Observability:** one log line per activation, failure and disable, with id and version.
- **No partial writes:** a failed activation must not leave half-registered routes or rows.

For settings, the analogue is: a bad row is dropped with a visible diagnostic; an override that names
a missing key is ignored; an unknown enum value falls back safely; one malformed row never blanks the
page.

---

## 9. Hybrid Patterns That Work

1. **Build-time code, runtime catalog.** Compile the shapes and consumers; load rows, copy and
   defaults from validated data. This is the best default for settings.
2. **Signed manifest, build-time code.** The manifest chooses which compiled modules activate for a
   tenant; no code is downloaded.
3. **Feature flags with expiry.** Runtime flags gate build-time behavior; each has an owner and a
   removal date.
4. **Remote config with local fallback.** Last-known-good cached locally; boot never depends on the
   network.
5. **Capability tokens.** A plugin receives only the interfaces it needs; the host enforces scope.
6. **Tiered plugins.** First-party compiled, second-party signed packages, third-party sandboxed.
   Do not force one tier's machinery onto all three.

---

## 10. Recommendation by Product Type

| Product | Code | Catalog and values | Notes |
|---|---|---|---|
| Mobile app | Build-time | Runtime data allowed | Store policy forbids downloaded code |
| Desktop app | Build-time first-party; signed runtime second-party | Runtime | Child process for untrusted |
| Web SaaS | Build-time bundle; runtime workers if needed | Runtime | Strict CSP and SRI for any remote code |
| On-prem enterprise | Build-time core; signed runtime integrations | Runtime, local | Customer-controlled trust and updates |
| Marketplace with ecosystem | Runtime host | Runtime | Full lifecycle, trust, billing, support |
| CLI or library | Build-time | File or env at runtime | No plugin host unless an ecosystem exists |
| Embedded or IoT | Build-time | Provisioned data | No dynamic code; memory and update constraints |

---

## 11. Red Flags

- Runtime executable loading in a mobile store build.
- Unsigned code, or a signature checked only at install.
- A plugin with ambient access to the database or filesystem.
- A plugin that can change another plugin's state.
- A remote catalog with no schema validation, no version and no fallback.
- A feature flag with no owner and no expiry, used as a permanent setting.
- Hot reload enabled in production.
- A plugin failure that stops the host loop.
- A settings key that stores a secret, a connection string or a token.
- A runtime catalog that can introduce a **new shape** the renderer does not know.
- "It is data, so it is safe" when the data is evaluated as code, a template or a query.

---

## 12. Decision Record Template

```text
Axis:            <code | catalog | values | flags | secrets>
Choice:          <build-time | runtime | hybrid>
Payload:         <what moves>
Author/trust:    <who writes it, how it is trusted>
Platform:        <target and any policy constraint>
Discovery:       <DI | scan | manifest | remote | none>
Versioning:      <contract version, compatibility window>
Isolation:       <failure policy, limits, rollback>
Fallback:        <offline/last-known-good behavior>
Reason:          <why runtime is required, and why the safer option was rejected>
Revisit when:    <trigger>
```

Write one block per axis. A design without these blocks is an undocumented platform dependency.
