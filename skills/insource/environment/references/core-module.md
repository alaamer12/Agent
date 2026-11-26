# Core env module: layout and contracts

```
<shared>/src/env/
  modes.ts        <APP>_ENV-style enum, ALIASES, normalizeMode(raw), capabilities(mode)
  registry.ts     ENV_REGISTRY descriptors (see below)
  errors.ts       buildEnvValidationFailure, throwForbiddenInMode, buildEnvInvalidAccessFailure
  factory.ts      createT3Env wrapper -> maps library hooks to errors.ts (no secret echo)
  urls.ts         SURFACE_PORTS, DEFAULT_LOCAL_HOST, buildDefaultSurfaceUrls, buildAllowedCorsOrigins
  loopback.ts     extractHostname (handle IPv6 "::1"), isLoopbackHost, alignLoopbackHostname
  cookies.ts      resolveCookieDomain, resolveUseSecureCookies
  business.ts     BusinessIdentity schema + defaults (ONE place for literals) + legal identity view
  mobile.ts       buildMobileBuildConfig, resolveCapacitorOrigins
  shorthands.ts   createEnvironment / initEnvironment / getEnvironment + every shorthand
  index.ts        re-exports
```

## Descriptor contract
```ts
interface EnvVarDescriptor<T> {
  key: string;
  ownerSurfaces: Surface[];            // backend | client | marketing | admin | edge | scripts | mobile-build
  exposure: "server-secret" | "server-config" | "client-public" | "mobile-build" | "system-readonly";
  loadingPhase: "runtime-server" | "ssr-runtime-hydrated" | "build-time-static" | "edge-per-request";
  description: string;                  // purpose and runtime impact
  valueType: string;                    // e.g. "HTTP(S) origin, no path"
  accepted: string[];
  rejected: { example: string; reason: string; violationCode: string }[];
  schema: ZodType<T>;
}
```
Use the registry to (a) feed the factory, (b) verify/generate `.env.example` comments, (c) verify the orchestrator env lists, (d) detect wrong-surface prefixes, (e) write a registry-completeness unit test.

## Violation catalog (one atomic code per distinct truth; never merge them)
- missing var -> `{key, ownerSurface, loadingPhase, description, acceptedExamples}`
- malformed origin -> `{key, receivedHostOrScheme, reason, acceptedExamples}`
- invalid mode -> `{key, received, acceptedModes}`
- forbidden in mode -> `{key, activeMode, forbiddenValue, reason}`
- surface prefix mismatch -> `{key, attemptedSurface, allowedSurfaces, expectedPrefix}`
- weak secret -> `{key, minLength, actualLength}` (never the secret)
- port out of range -> `{key, received, minPort, maxPort}`
Retry class: alarm/non-retryable (boot misconfig never succeeds on retry). Provide localized messages if the repo is i18n'd; wrap LTR tokens in bidi isolates for RTL locales. Developer boot diagnostics should name variable, owning app, loading phase, why rejected, accepted examples - so nobody has to investigate what the app already knows.

## Rules
- The factory must be strict (eager, no defaults on required vars, empty string = missing). See SKILL.md "Strict validation".
- No reads of `process.env`/`import.meta.env` in this module (callers pass values in). Exception-free purity is what lets it run on the edge and in browsers.
- Live getters where legacy constants exist (e.g. a legacy legal-identity constant should delegate to the env module instead of duplicating literals).
- Replace defensive `globalThis.process?.env?.NODE_ENV` checks anywhere in shared code (e.g. a debug/duck-typing helper) with `canUseDevShortcuts()`.
