# Reference implementation diff (Kabrha monorepo) - LOOKUP ONLY

This is the real diff of a completed run of this workflow (116 files, +5425/-932). Use it to see
*what a finished result looks like* per file role. Names (Kabrha, SNDUK, KABRHA_ENV, Capacitor app ids)
are project-specific: map each file to its role in the target repo, do not copy names or values.
Roles are summarized in `worked-example.md`; read that first.

## Contents
- Summary by wave (table)
- Wave 2b: layered dotenv seam, CLI runner, mobile sync, templates
- Wave 4: ADR + governance docs (AGENTS.md, USAGE.md, ledgers)
- Wave 3 workers: admin/edge, backend, client/mobile/vue-core, marketing, scripts/tests
- Wave 2: shared env core, error codes, locales, unit tests
- Wave 1 & 4: gate + conformance spec

---

# Environment SSOT Plan — Diff Summary Report

> **Commit Range:** `61a7b8e^..HEAD`  
> **Files Matched (Env SSOT Plan):** 116  
> **Total Line Delta:** `+5425 / -932`  

## Summary by Plan Wave

| Wave | Files | Added | Deleted |
|---|---:|---:|---:|
| Wave 2b — Layered dotenv Seam, CLI Runner, Mobile Sync & Templates | 11 | +639 | -22 |
| Wave 4 — Golden Rule #7, ADR 008 & Documentation | 5 | +58 | -21 |
| Wave 3 (Worker C) — Admin & Cloudflare Edge | 5 | +149 | -33 |
| Wave 3 (Main) — Backend Env, SNDUK & Auth/Health Guards | 21 | +645 | -307 |
| Wave 3 (Worker B) — Client, Mobile Capacitor & vue-core | 16 | +419 | -180 |
| Wave 3 (Worker A) — Marketing Nuxt SSR/Nitro Env Migration | 21 | +537 | -115 |
| Wave 2 — @kabrha/shared/env Core, VAL-010..016 & Locales | 20 | +2298 | -69 |
| Wave 3 (Worker D) — Scripts & Test Harnesses | 14 | +272 | -185 |
| Wave 1 & 4 — Environment SSOT Gate & Conformance | 3 | +408 | -0 |

## File-by-File Diff Breakdown

### Wave 2b — Layered dotenv Seam, CLI Runner, Mobile Sync & Templates

| Status | File | Delta |
|---|---|---:|
| `A` | `.env.dev.example` | `+26 / -0` |
| `M` | `.env.example` | `+34 / -19` |
| `A` | `.env.production.example` | `+29 / -0` |
| `A` | `.env.staging.example` | `+27 / -0` |
| `A` | `.env.test.example` | `+22 / -0` |
| `A` | `scripts/lib/dotenvSeam.ts` | `+127 / -0` |
| `A` | `scripts/lib/scriptEnv.ts` | `+120 / -0` |
| `A` | `scripts/sync-mobile-env.ts` | `+121 / -0` |
| `A` | `scripts/with-env.ts` | `+87 / -0` |
| `M` | `turbo.json` | `+45 / -3` |
| `M` | `vitest.config.ts` | `+1 / -0` |

<details><summary>Key additions in <code>.env.dev.example</code></summary>

```ts
KABRHA_ENV=dev
VITE_KABRHA_ENV=dev
NUXT_PUBLIC_KABRHA_ENV=dev
# SNDUK_PROVIDER_MODE=http
# SNDUK_API_URL=http://127.0.0.1:8000
# SNDUK_API_TOKEN=<local-snduk-dev-token>
```

</details>

<details><summary>Key additions in <code>.env.example</code></summary>

```ts
# Four canonical modes (`KABRHA_ENV`): dev | test | staging | production
KABRHA_ENV=dev
VITE_KABRHA_ENV=dev
NUXT_PUBLIC_KABRHA_ENV=dev
```

</details>

<details><summary>Key additions in <code>.env.production.example</code></summary>

```ts
# Forbids SNDUK_PROVIDER_MODE=fixture, loopback client URLs, dev shortcuts, test mocks, and error debug dumps.
KABRHA_ENV=production
VITE_KABRHA_ENV=production
NUXT_PUBLIC_KABRHA_ENV=production
SNDUK_PROVIDER_MODE=http
SNDUK_API_URL=https://api.snduk.com
```

</details>

<details><summary>Key additions in <code>.env.staging.example</code></summary>

```ts
KABRHA_ENV=staging
VITE_KABRHA_ENV=staging
NUXT_PUBLIC_KABRHA_ENV=staging
SNDUK_PROVIDER_MODE=http
SNDUK_API_URL=https://staging-api.snduk.com
SNDUK_API_TOKEN=
```

</details>

<details><summary>Key additions in <code>.env.test.example</code></summary>

```ts
KABRHA_ENV=test
VITE_KABRHA_ENV=test
NUXT_PUBLIC_KABRHA_ENV=test
SNDUK_PROVIDER_MODE=fixture
SNDUK_API_URL=http://127.0.0.1:4000/internal/snduk-fixture
```

</details>

<details><summary>Key additions in <code>scripts/lib/dotenvSeam.ts</code></summary>

```ts
export interface LoadDotenvOptions {
export interface LoadedDotenvResult {
export function resolveRepoRoot(startDir = process.cwd()): string {
export function loadKabrhaDotenv(options: LoadDotenvOptions = {}): LoadedDotenvResult {
target["KABRHA_ENV"] ??
key: "KABRHA_ENV",
```

</details>

<details><summary>Key additions in <code>scripts/lib/scriptEnv.ts</code></summary>

```ts
createKabrhaT3Env,
initEnvironment,
export interface ScriptEnv {
* `createKabrhaT3Env` + `ENV_REGISTRY`, initializes `@kabrha/shared/env`, and returns typed config.
export function loadScriptEnv(options: LoadDotenvOptions = {}): ScriptEnv {
const validated = createKabrhaT3Env({
```

</details>

<details><summary>Key additions in <code>scripts/sync-mobile-env.ts</code></summary>

```ts
const resolvedMode = normalizeKabrhaEnvMode(process.env["VITE_KABRHA_ENV"] ?? mode) ?? mode;
`KABRHA_ENV=${resolvedMode}`,
`KABRHA_ENV = ${resolvedMode}`,
```

</details>

<details><summary>Key additions in <code>scripts/with-env.ts</code></summary>

```ts
const requestedMode = modeArg ?? process.env["KABRHA_ENV"] ?? "dev";
key: "KABRHA_ENV",
KABRHA_ENV: mode,
childEnv["VITE_KABRHA_ENV"] ??= mode;
childEnv["NUXT_PUBLIC_KABRHA_ENV"] ??= mode;
```

</details>

<details><summary>Key additions in <code>turbo.json</code></summary>

```ts
"KABRHA_ENV",
"VITE_KABRHA_ENV",
"NUXT_PUBLIC_KABRHA_ENV",
"SNDUK_SYNC_COUNTRY",
```

</details>

### Wave 4 — Golden Rule #7, ADR 008 & Documentation

| Status | File | Delta |
|---|---|---:|
| `M` | `.viber/docs/decisions/008-environment-tiers-and-origin-handoff.md` | `+13 / -6` |
| `M` | `.viber/docs/steering/tech/shared/doctrine/error-ownership.md` | `+8 / -0` |
| `M` | `.viber/learnt.md` | `+1 / -0` |
| `M` | `AGENTS.md` | `+23 / -11` |
| `M` | `USAGE.md` | `+13 / -4` |

<details><summary>Key additions in <code>.viber/docs/decisions/008-environment-tiers-and-origin-handoff.md</code></summary>

```ts
| Mode (`KABRHA_ENV`) | Standard `NODE_ENV` | PocketBase & Data | **SNDUK (`صندوق`) Upstream Connection** | Auth, Rate Limits & Dev Shortcuts | Origins, Loopback & Cookies | Mobile Native Builds (`@kabrha/client`) |
| **`dev`** | `development` | Local PB (`127.0.0.1:8090`) + seeded/local data | `fixture` (`${apiUrl}/internal/snduk-fixture`) **or** `http` (`http://127.0.0.1:8000` local `../snduk` + `SNDUK_API_TOKEN`) | `allowDevShortcuts`, `allowTestMocks`, `allowLocalSeededData`, `exposeErrorDebug` ON; `enforceAuthRateLimit` OFF | `127.0.0.1` ↔ `localhost` aligned automatically; host-only cookies | `loggingBehavior: "debug"`, `webContentsDebuggingEnabled: true`, loopback allowed |
| **`staging`** | `production` | Staging PB / local PB (no live prod secrets) | `http` (`SNDUK_API_URL` = staging SNDUK e.g. `https://staging-api.snduk.com` or local `http://127.0.0.1:8000`) + `SNDUK_API_TOKEN` | **`isProductionBehavior: true`**, `enforceAuthRateLimit: true`; **all** dev shortcuts, test mocks, `_debug`, & cache-purge bypasses OFF | Staging domains (`staging.kabrha.com`) or local aligned; `Secure` + purge secret enforced | `loggingBehavior: "none"`, `webContentsDebuggingEnabled: false`; loopback `VITE_API_URL` forbidden (`VAL-013`) |
| **`production`** | `production` | Live production PB (`PB_URL` volume) | **`http` ONLY** (`SNDUK_API_URL` = `https://api.snduk.com` or internal + `SNDUK_API_TOKEN` required; `fixture`/loopback forbidden → `VAL-013`) | Full `isProductionBehavior`, `enforceAuthRateLimit`, CSRF `Origin`, Turnstile, `Secure` cookies | Canonical `https://kabrha.com`, `https://app.kabrha.com`, `https://api.kabrha.com`; `Domain=.kabrha.com` | `loggingBehavior: "none"`, `webContentsDebuggingEnabled: false`, `VITE_GOOGLE_WEB_CLIENT_ID` required (`VAL-010`), loopback forbidden (`VAL-013`) |
Because Kabrha sources Egyptian mutual fund catalogs and NAV ticks from **SNDUK (`صندوق`)**, `SNDUK_PROVIDER_MODE`, `SNDUK_API_URL`, `SNDUK_API_TOKEN`, and `SNDUK_SYNC_COUNTRY` are first-class members of `ENV_REGISTRY` and `@kabrha/shared/env` (`SURFACE_PORTS.snduk = 8000`, `defaultSndukApiUrl()`, `sndukApiUrl()`, `sndukProviderMode()`, `sndukSyncCountry()`, `isSndukLiveHttp()`):
- **Local `../snduk` (`dev` or local `staging`):** Set `SNDUK_PROVIDER_MODE=http` and `SNDUK_API_URL=http://127.0.0.1:8000` (default when `SNDUK_PROVIDER_MODE=http` outside `production`) with `SNDUK_API_TOKEN`. Leave `SNDUK_PROVIDER_MODE=fixture` in `dev`/`test` for offline seeded runs (`${apiUrl}/internal/snduk-fixture`).
```

</details>

<details><summary>Key additions in <code>.viber/learnt.md</code></summary>

```ts
| 34 | **External Error Copy Leakage (`errors.*.admin` vs default `errors.*`)**: Even when `renderError` never sends `internalMessage` over the wire, default `errors.*` locale templates containing `{operation}`, `{collection}`, `{recordId}`, `{path}`, `{status}`, or infra terms (`Database service`, `Atomic batch`, `SNDUK_API_URL`) leak developer internals to end users in Production as well as Dev. Separating calm user copy in `errors.*` from diagnostic `errors.*.admin` overrides, routing frontend HTTP failures to `NET-005`/`NET-006`/`NET-007` instead of `NET-001`, and enforcing all 4 rules via `scripts/gates/gate-error-governance.ts` eliminates the leak structurally. | Screenshot audit + 4-gate AST conformance implementation (2026-11-25). | Never put `{operation}`, `{collection}`, `{recordId}`, `{path}`, `{status}`, or infra jargon in default `errors.*` keys; place them in `errors.*.admin` and enforce with `bun run check:errors`. | 2026-11-25 |
```

</details>

<details><summary>Key additions in <code>AGENTS.md</code></summary>

```ts
- **Four Canonical Modes (`KABRHA_ENV`):** `dev | test | staging | production` (Golden Rule #7, §14). System/toolchain env vars (`NODE_ENV`, `TZ`, `LANG`, `CI`, `ANDROID_HOME`, `JAVA_HOME`, `GRADLE_OPTS`, Xcode `CONFIGURATION`) remain unconflicted; `NODE_ENV` stays `"development" | "test" | "production"`.
- **SNDUK (`صندوق`) Connection:** `SNDUK_PROVIDER_MODE`, `SNDUK_API_URL`, `SNDUK_API_TOKEN`, and `SNDUK_SYNC_COUNTRY` govern upstream connectivity across local (`fixture` or `http://127.0.0.1:8000`), `staging`, and `production` (`http` + non-loopback `SNDUK_API_URL` + `SNDUK_API_TOKEN` required; `fixture`/loopback fail boot with `VAL-013`).
| `KABRHA_ENV` | Standard `NODE_ENV` | PocketBase & Data | SNDUK (`صندوق`) Upstream (`SNDUK_PROVIDER_MODE` / `SNDUK_API_URL`) | Auth, Rate Limits & Dev Shortcuts | Origins, Loopback & Cookies | Mobile Native Builds (`@kabrha/client`) |
| **`staging`** | `production` | Staging PB / local PB (no live prod secrets) | `http` (`https://staging-api.snduk.com` or local `http://127.0.0.1:8000`) + `SNDUK_API_TOKEN` | **`isProductionBehavior: true`**, `enforceAuthRateLimit: true`; all dev shortcuts, test mocks, `_debug`, & purge bypasses OFF | Staging domains (`staging.kabrha.com`) or local aligned; `Secure` + purge secret ON | `loggingBehavior: "none"`, debuggable OFF; loopback `VITE_API_URL` forbidden (`VAL-013`) |
| **`production`** | `production` | Live production PB (`PB_URL` volume) | **`http` ONLY** (`https://api.snduk.com` or internal + `SNDUK_API_TOKEN` required; `fixture`/loopback → `VAL-013`) | Full `isProductionBehavior`, `enforceAuthRateLimit`, CSRF `Origin`, Turnstile, `Secure` cookies | Canonical `https://kabrha.com`, `https://app.kabrha.com`, `https://api.kabrha.com`; `Domain=.kabrha.com` | `loggingBehavior: "none"`, debuggable OFF, `VITE_GOOGLE_WEB_CLIENT_ID` required (`VAL-010`), loopback forbidden (`VAL-013`) |
```

</details>

<details><summary>Key additions in <code>USAGE.md</code></summary>

```ts
SNDUK_PROVIDER_MODE=http
SNDUK_API_URL=http://127.0.0.1:8000
SNDUK_API_TOKEN=<snduk_integration_api_key>
- **Deployed `staging`:** Set `SNDUK_API_URL=https://staging-api.snduk.com` and `SNDUK_API_TOKEN`.
- **Deployed `production`:** `SNDUK_PROVIDER_MODE=http`, a non-loopback `SNDUK_API_URL` (`https://api.snduk.com` or `http://snduk.railway.internal:8000`), and a non-empty `SNDUK_API_TOKEN` are strictly required at boot (`fixture` and loopback URLs fail boot with `VAL-013`).
```

</details>

### Wave 3 (Worker C) — Admin & Cloudflare Edge

| Status | File | Delta |
|---|---|---:|
| `M` | `apps/admin/nuxt.config.ts` | `+36 / -4` |
| `A` | `apps/admin/src/config/env.ts` | `+82 / -0` |
| `M` | `apps/admin/src/plugins/transport.ts` | `+11 / -24` |
| `M` | `infra/edge/worker.ts` | `+12 / -5` |
| `M` | `infra/edge/wrangler.toml` | `+8 / -0` |

<details><summary>Key additions in <code>apps/admin/nuxt.config.ts</code></summary>

```ts
normalizeKabrhaEnvMode(process.env.NUXT_PUBLIC_KABRHA_ENV ?? process.env.KABRHA_ENV) ?? "dev";
```

</details>

<details><summary>Key additions in <code>apps/admin/src/config/env.ts</code></summary>

```ts
createKabrhaT3Env,
initEnvironment,
export interface AdminRuntimeEnv {
* Validates Nuxt public runtime config through `createKabrhaT3Env` (`NUXT_PUBLIC_*`),
export function initAdminEnvironment(): AdminRuntimeEnv {
const validated = createKabrhaT3Env({
```

</details>

<details><summary>Key additions in <code>infra/edge/worker.ts</code></summary>

```ts
readonly KABRHA_ENV?: string | undefined;
const edgeMode = normalizeKabrhaEnvMode(env.KABRHA_ENV) ?? "production";
```

</details>

<details><summary>Key additions in <code>infra/edge/wrangler.toml</code></summary>

```ts
KABRHA_ENV = "production"
KABRHA_ENV = "staging"
```

</details>

### Wave 3 (Main) — Backend Env, SNDUK & Auth/Health Guards

| Status | File | Delta |
|---|---|---:|
| `M` | `apps/backend/src/app.ts` | `+5 / -1` |
| `M` | `apps/backend/src/config.ts` | `+303 / -129` |
| `M` | `apps/backend/src/email/service.ts` | `+4 / -1` |
| `M` | `apps/backend/src/lib/oauth2/jwks-cache.ts` | `+3 / -2` |
| `M` | `apps/backend/src/lib/oauth2/verify-id-token.ts` | `+4 / -3` |
| `M` | `apps/backend/src/middleware/auth.ts` | `+10 / -31` |
| `M` | `apps/backend/src/middleware/error-handler.ts` | `+3 / -1` |
| `M` | `apps/backend/src/realtime/pbSync.ts` | `+3 / -1` |
| `M` | `apps/backend/src/routes/admin.ts` | `+228 / -62` |
| `M` | `apps/backend/src/routes/auth.ts` | `+5 / -3` |
| `M` | `apps/backend/src/routes/auth/google.ts` | `+10 / -9` |
| `M` | `apps/backend/src/routes/auth/helpers.ts` | `+1 / -3` |
| `M` | `apps/backend/src/routes/auth/recovery.ts` | `+12 / -5` |
| `M` | `apps/backend/src/routes/health.ts` | `+10 / -0` |
| `M` | `apps/backend/src/routes/leagues.ts` | `+2 / -1` |
| `M` | `apps/backend/src/seo/og/layers.ts` | `+2 / -2` |
| `M` | `apps/backend/src/seo/og/render.ts` | `+5 / -2` |
| `M` | `apps/backend/src/seo/ssr.ts` | `+6 / -13` |
| `M` | `apps/backend/src/services/activity.ts` | `+11 / -3` |
| `M` | `apps/backend/tests/integration/snduk-bridge.test.ts` | `+3 / -35` |
| `M` | `apps/backend/tests/unit/env-boundaries.test.ts` | `+15 / -0` |

<details><summary>Key additions in <code>apps/backend/src/config.ts</code></summary>

```ts
createKabrhaT3Env,
initEnvironment,
export interface BackendConfig {
readonly KABRHA_ENV: KabrhaEnvMode;
readonly SNDUK_PROVIDER_MODE: "fixture" | "http";
readonly SNDUK_API_URL: string;
```

</details>

<details><summary>Key additions in <code>apps/backend/src/email/service.ts</code></summary>

```ts
import { canUseTestMocks, isProdBehavior } from "@kabrha/shared/env";
const mocksEnabled = allowTestMocks ?? canUseTestMocks();
```

</details>

<details><summary>Key additions in <code>apps/backend/src/routes/auth.ts</code></summary>

```ts
import { canUseDevShortcuts } from "@kabrha/shared/env";
deps.config.environment?.capabilities.allowDevShortcuts ?? canUseDevShortcuts();
```

</details>

<details><summary>Key additions in <code>apps/backend/src/routes/auth/google.ts</code></summary>

```ts
import { canUseTestMocks, deepLinkScheme, isLoopback } from "@kabrha/shared/env";
const mocksAllowed = config.environment?.capabilities.allowTestMocks ?? canUseTestMocks();
```

</details>

<details><summary>Key additions in <code>apps/backend/src/routes/auth/recovery.ts</code></summary>

```ts
import { canUseTestMocks } from "@kabrha/shared/env";
deps.config.environment?.capabilities.allowTestMocks ?? canUseTestMocks();
```

</details>

<details><summary>Key additions in <code>apps/backend/src/routes/health.ts</code></summary>

```ts
import { canUseLocalSeedData, throwForbiddenInMode } from "@kabrha/shared/env";
deps.config.environment?.capabilities.allowLocalSeededData ?? canUseLocalSeedData();
"SNDUK_PROVIDER_MODE",
deps.config.KABRHA_ENV,
```

</details>

<details><summary>Key additions in <code>apps/backend/tests/unit/env-boundaries.test.ts</code></summary>

```ts
SNDUK_API_URL: "https://api.snduk.com",
SNDUK_API_TOKEN: "prod_snduk_integration_token_ok",
expect(prodCfg.SNDUK_PROVIDER_MODE).toBe("http");
KABRHA_ENV: "production",
SNDUK_API_URL: "http://127.0.0.1:8000",
SNDUK_API_TOKEN: "prod_snduk_integration_token_ok",
```

</details>

### Wave 3 (Worker B) — Client, Mobile Capacitor & vue-core

| Status | File | Delta |
|---|---|---:|
| `M` | `apps/client/capacitor.config.ts` | `+34 / -7` |
| `M` | `apps/client/index.html` | `+1 / -1` |
| `A` | `apps/client/src/config/env.ts` | `+128 / -0` |
| `M` | `apps/client/src/env.d.ts` | `+5 / -0` |
| `M` | `apps/client/src/main.ts` | `+3 / -0` |
| `M` | `apps/client/src/platform/index.ts` | `+2 / -1` |
| `M` | `apps/client/src/platform/native/googleAuth.ts` | `+5 / -3` |
| `M` | `apps/client/src/platform/web/googleAuth.ts` | `+11 / -7` |
| `M` | `apps/client/src/router/index.ts` | `+2 / -3` |
| `M` | `apps/client/src/router/navigations.paths.ts` | `+7 / -15` |
| `M` | `apps/client/src/services/bffClient.ts` | `+47 / -37` |
| `M` | `apps/client/src/shared/composables/useDevJuniorPreview.ts` | `+2 / -1` |
| `M` | `apps/client/src/shared/composables/useFeatureFlags.ts` | `+7 / -4` |
| `M` | `apps/client/src/stores/preferences.ts` | `+11 / -5` |
| `M` | `apps/client/vite.config.ts` | `+144 / -82` |
| `M` | `packages/vue-core/src/composables/useFeatureFlags.ts` | `+10 / -14` |

<details><summary>Key additions in <code>apps/client/capacitor.config.ts</code></summary>

```ts
normalizeKabrhaEnvMode(process.env["VITE_KABRHA_ENV"] ?? process.env["KABRHA_ENV"]) ?? "dev";
```

</details>

<details><summary>Key additions in <code>apps/client/src/config/env.ts</code></summary>

```ts
canUseDevShortcuts,
canUseLocalSeedData,
canUseTestMocks,
createKabrhaT3Env,
initEnvironment,
const validatedViteEnv = createKabrhaT3Env({
```

</details>

<details><summary>Key additions in <code>apps/client/src/env.d.ts</code></summary>

```ts
readonly VITE_KABRHA_ENV?: string;
```

</details>

<details><summary>Key additions in <code>apps/client/src/platform/index.ts</code></summary>

```ts
import { canUseDevShortcuts } from "@kabrha/shared/env";
return canUseDevShortcuts();
```

</details>

<details><summary>Key additions in <code>apps/client/src/platform/native/googleAuth.ts</code></summary>

```ts
import { canUseTestMocks } from "@kabrha/shared/env";
if (canUseTestMocks() && typeof window !== "undefined") {
```

</details>

<details><summary>Key additions in <code>apps/client/src/platform/web/googleAuth.ts</code></summary>

```ts
import { canUseTestMocks } from "@kabrha/shared/env";
if (canUseTestMocks() && typeof window !== "undefined") {
```

</details>

<details><summary>Key additions in <code>apps/client/src/shared/composables/useDevJuniorPreview.ts</code></summary>

```ts
import { canUseDevShortcuts } from "@kabrha/shared/env";
const isDevMode = canUseDevShortcuts();
```

</details>

<details><summary>Key additions in <code>apps/client/src/shared/composables/useFeatureFlags.ts</code></summary>

```ts
import { canUseDevShortcuts } from "@kabrha/shared/env";
allowQueryOverride: canUseDevShortcuts(),
```

</details>

<details><summary>Key additions in <code>apps/client/vite.config.ts</code></summary>

```ts
loaded["VITE_KABRHA_ENV"] ??
loaded["KABRHA_ENV"] ??
process.env["VITE_KABRHA_ENV"] ??
process.env["KABRHA_ENV"] ??
```

</details>

<details><summary>Key additions in <code>packages/vue-core/src/composables/useFeatureFlags.ts</code></summary>

```ts
import { canUseDevShortcuts } from "@kabrha/shared/env";
const allowOverride = options?.allowQueryOverride ?? canUseDevShortcuts();
```

</details>

### Wave 3 (Worker A) — Marketing Nuxt SSR/Nitro Env Migration

| Status | File | Delta |
|---|---|---:|
| `M` | `apps/marketing/app/error.vue` | `+6 / -3` |
| `M` | `apps/marketing/app/middleware/locale-country.global.ts` | `+9 / -7` |
| `A` | `apps/marketing/app/plugins/00-env.ts` | `+6 / -0` |
| `M` | `apps/marketing/nuxt.config.ts` | `+73 / -10` |
| `M` | `apps/marketing/server/api/internal/purge-cache.post.ts` | `+35 / -2` |
| `M` | `apps/marketing/server/api/public-bootstrap.get.ts` | `+4 / -1` |
| `M` | `apps/marketing/server/middleware/01-surface-redirect.ts` | `+7 / -6` |
| `M` | `apps/marketing/server/routes/api/v1/media/[...path].ts` | `+3 / -5` |
| `M` | `apps/marketing/server/routes/og/[...path].ts` | `+3 / -5` |
| `M` | `apps/marketing/server/routes/robots.txt.ts` | `+3 / -4` |
| `M` | `apps/marketing/server/routes/sitemap.xml.ts` | `+4 / -5` |
| `M` | `apps/marketing/server/utils/backendFetch.ts` | `+16 / -14` |
| `A` | `apps/marketing/server/utils/env.ts` | `+147 / -0` |
| `M` | `apps/marketing/src/composables/useMarketingContext.ts` | `+12 / -18` |
| `A` | `apps/marketing/src/config/env.ts` | `+161 / -0` |
| `M` | `apps/marketing/src/features/trust/views/AboutView.vue` | `+2 / -1` |
| `M` | `apps/marketing/src/features/trust/views/ContactView.vue` | `+8 / -4` |
| `M` | `apps/marketing/src/features/trust/views/NotFoundView.vue` | `+1 / -1` |
| `M` | `apps/marketing/src/features/trust/views/PrivacyView.vue` | `+15 / -8` |
| `M` | `apps/marketing/src/features/trust/views/TermsView.vue` | `+11 / -8` |
| `M` | `apps/marketing/src/services/marketingApi.ts` | `+11 / -13` |

<details><summary>Key additions in <code>apps/marketing/nuxt.config.ts</code></summary>

```ts
createKabrhaT3Env,
const rawMode = process.env.NUXT_PUBLIC_KABRHA_ENV ?? process.env.KABRHA_ENV;
const validated = createKabrhaT3Env({
NUXT_PUBLIC_KABRHA_ENV: KabrhaEnvSchema.default("dev"),
NUXT_PUBLIC_KABRHA_ENV: normalizedMode,
const mode = validated.NUXT_PUBLIC_KABRHA_ENV;
```

</details>

<details><summary>Key additions in <code>apps/marketing/server/utils/backendFetch.ts</code></summary>

```ts
export function getInternalBackendClient(event?: H3Event) {
```

</details>

<details><summary>Key additions in <code>apps/marketing/server/utils/env.ts</code></summary>

```ts
createKabrhaT3Env,
initEnvironment,
export interface MarketingServerEnv {
export function initMarketingServerEnv(event?: H3Event): MarketingServerEnv {
asOptionalString(process.env.NUXT_PUBLIC_KABRHA_ENV) ??
asOptionalString(process.env.KABRHA_ENV);
```

</details>

<details><summary>Key additions in <code>apps/marketing/src/config/env.ts</code></summary>

```ts
createKabrhaT3Env,
initEnvironment,
export interface MarketingPublicRuntimeConfig {
export interface MarketingRuntimeConfigInput {
export interface MarketingEnvState {
export function initMarketingEnv(runtimeConfig?: MarketingRuntimeConfigInput): MarketingEnvState {
```

</details>

### Wave 2 — @kabrha/shared/env Core, VAL-010..016 & Locales

| Status | File | Delta |
|---|---|---:|
| `M` | `packages/shared/package.json` | `+3 / -1` |
| `A` | `packages/shared/src/env/business.ts` | `+71 / -0` |
| `A` | `packages/shared/src/env/cookies.ts` | `+48 / -0` |
| `A` | `packages/shared/src/env/errors.ts` | `+76 / -0` |
| `A` | `packages/shared/src/env/index.ts` | `+10 / -0` |
| `A` | `packages/shared/src/env/loopback.ts` | `+63 / -0` |
| `A` | `packages/shared/src/env/mobile.ts` | `+54 / -0` |
| `A` | `packages/shared/src/env/modes.ts` | `+78 / -0` |
| `A` | `packages/shared/src/env/registry.ts` | `+427 / -0` |
| `A` | `packages/shared/src/env/shorthands.ts` | `+367 / -0` |
| `A` | `packages/shared/src/env/t3Factory.ts` | `+37 / -0` |
| `A` | `packages/shared/src/env/urls.ts` | `+125 / -0` |
| `M` | `packages/shared/src/errors/duckDebugger.ts` | `+53 / -13` |
| `M` | `packages/shared/src/errors/val.ts` | `+131 / -0` |
| `M` | `packages/shared/src/index.ts` | `+1 / -0` |
| `M` | `packages/shared/src/locales/ar-EG.json` | `+49 / -15` |
| `M` | `packages/shared/src/locales/ar.json` | `+49 / -15` |
| `M` | `packages/shared/src/locales/en.json` | `+49 / -15` |
| `M` | `packages/shared/src/schemas/legalIdentity.ts` | `+34 / -10` |
| `A` | `packages/shared/tests/environment.test.ts` | `+573 / -0` |

<details><summary>Key additions in <code>packages/shared/src/env/business.ts</code></summary>

```ts
export const BusinessIdentitySchema = z.object({
export type BusinessIdentity = z.infer<typeof BusinessIdentitySchema>;
export interface EnvLegalIdentityView {
export const DEFAULT_BUSINESS_IDENTITY: BusinessIdentity = {
export function toLegalIdentityView(biz: BusinessIdentity): EnvLegalIdentityView {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/cookies.ts</code></summary>

```ts
export function resolveCookieDomain(
export function resolveUseSecureCookies(
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/errors.ts</code></summary>

```ts
export function buildEnvValidationFailure(
if (key === "KABRHA_ENV" || key === "VITE_KABRHA_ENV" || key === "NUXT_PUBLIC_KABRHA_ENV") {
export function throwForbiddenInMode(key: string, activeMode: string, reason: string): never {
export function buildEnvInvalidAccessFailure(surface: EnvSurface, key: string): never {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/loopback.ts</code></summary>

```ts
export function extractHostname(input: string): string | null {
export function isLoopbackHost(hostnameOrUrl: string | undefined | null): boolean {
export function alignLoopbackHostname(rawUrl: string, activeHostname?: string | null): string {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/mobile.ts</code></summary>

```ts
export const MobileBuildConfigSchema = z.object({
export type MobileBuildConfig = z.infer<typeof MobileBuildConfigSchema>;
export function resolveCapacitorOrigins(config: {
export function buildMobileBuildConfig(opts: {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/modes.ts</code></summary>

```ts
export const KABRHA_ENV_MODES = ["dev", "test", "staging", "production"] as const;
export type KabrhaEnvMode = (typeof KABRHA_ENV_MODES)[number];
export const KABRHA_ENV_ALIASES: Readonly<Record<string, KabrhaEnvMode>> = {
export const KabrhaEnvSchema = z.enum(KABRHA_ENV_MODES);
export interface EnvCapabilities {
export function normalizeKabrhaEnvMode(raw: string | undefined | null): KabrhaEnvMode | null {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/registry.ts</code></summary>

```ts
export type EnvSurface =
export type EnvExposure =
export type EnvLoadingPhase =
export interface EnvRejectedExample {
export interface EnvVarDescriptor<T = unknown> {
export const ENV_REGISTRY = {
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/shorthands.ts</code></summary>

```ts
export interface ResolvedEnvironment {
export interface CreateEnvironmentInput {
export function createEnvironment(input: CreateEnvironmentInput = {}): ResolvedEnvironment {
export function initEnvironment(
export function getEnvironment(): ResolvedEnvironment {
export const envMode = (): KabrhaEnvMode => activeEnvironment.mode;
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/t3Factory.ts</code></summary>

```ts
export function createKabrhaT3Env<
```

</details>

<details><summary>Key additions in <code>packages/shared/src/env/urls.ts</code></summary>

```ts
export const DEFAULT_LOCAL_HOST = "127.0.0.1";
export const SURFACE_PORTS = {
export const OriginUrlSchema = z
export interface SurfaceUrls {
export function buildDefaultSurfaceUrls(
* Returns `undefined` in `production` so missing `SNDUK_API_URL` fails loudly instead of
```

</details>

<details><summary>Key additions in <code>packages/shared/src/errors/duckDebugger.ts</code></summary>

```ts
import { canUseDevShortcuts } from "../env/shorthands.ts";
if (canUseDevShortcuts()) {
if (canUseDevShortcuts()) {
export interface DevDiagnosticHint {
export function buildDevDiagnosticHint(opts: {
if (!canUseDevShortcuts()) return undefined;
```

</details>

<details><summary>Key additions in <code>packages/shared/src/errors/val.ts</code></summary>

```ts
code: "VAL-010",
code: "VAL-011",
code: "VAL-012",
internalMessage: "KABRHA_ENV mode value is unrecognized",
code: "VAL-013",
internalMessage: "Environment variable value is forbidden in the active KABRHA_ENV mode",
```

</details>

<details><summary>Key additions in <code>packages/shared/src/locales/ar-EG.json</code></summary>

```ts
"errors.syn.upstream_auth_failed.admin": "بوابة Snduk رفضت مفتاح الربط بتاع السيرفر ({reason})؛ راجع إعدادات SNDUK_API_URL و SNDUK_API_TOKEN.",
```

</details>

<details><summary>Key additions in <code>packages/shared/src/locales/ar.json</code></summary>

```ts
"errors.syn.upstream_auth_failed.admin": "رفضت بوابة Snduk مفتاح التكامل للخادم ({reason})؛ تحقّق من إعدادات SNDUK_API_URL و SNDUK_API_TOKEN.",
```

</details>

<details><summary>Key additions in <code>packages/shared/src/locales/en.json</code></summary>

```ts
"errors.syn.upstream_auth_failed.admin": "SNDUK gateway rejected server integration credentials ({reason}); verify SNDUK_API_URL and SNDUK_API_TOKEN.",
```

</details>

<details><summary>Key additions in <code>packages/shared/tests/environment.test.ts</code></summary>

```ts
/** Protects: ADR 008, Settings/Error/Display/Seams Architectures — mode isolation, loopback alignment, cookie scoping, mobile origins, VAL-010..016 diagnostics, ENV_REGISTRY completeness, and LEGAL_IDENTITY dynamic delegation */
canUseDevShortcuts,
canUseLocalSeedData,
canUseTestMocks,
createKabrhaT3Env,
initEnvironment,
```

</details>

### Wave 3 (Worker D) — Scripts & Test Harnesses

| Status | File | Delta |
|---|---|---:|
| `M` | `playwright.config.ts` | `+4 / -1` |
| `M` | `scripts/bootstrap-browser.ts` | `+7 / -7` |
| `M` | `scripts/create-user.ts` | `+5 / -5` |
| `M` | `scripts/gates/check-e2e-content-integrity.ts` | `+4 / -1` |
| `M` | `scripts/lib/pbAdmin.ts` | `+5 / -5` |
| `M` | `scripts/parity-admin.ts` | `+10 / -9` |
| `M` | `scripts/pocketbase-lib.ts` | `+6 / -16` |
| `M` | `tests/e2e/admin.e2e.ts` | `+11 / -26` |
| `M` | `tests/e2e/north-star-pages.e2e.ts` | `+11 / -8` |
| `M` | `tests/e2e/two-platform-master.e2e.ts` | `+5 / -7` |
| `M` | `tests/e2e/workspace-calibration.e2e.ts` | `+22 / -20` |
| `M` | `tests/support/dbHarness.ts` | `+7 / -37` |
| `A` | `tests/support/envFactory.ts` | `+173 / -0` |
| `M` | `tests/support/inMemoryPb.ts` | `+2 / -43` |

<details><summary>Key additions in <code>scripts/pocketbase-lib.ts</code></summary>

```ts
export const HTTP_ADDR = `${DEFAULT_LOCAL_HOST}:${SURFACE_PORTS.pocketbase}`;
export const PB_URL = pbUrl();
```

</details>

<details><summary>Key additions in <code>tests/support/envFactory.ts</code></summary>

```ts
initEnvironment,
export interface TestRuntimeEnv {
export function initTestEnvironment(
return initEnvironment({
export function createTestBackendConfig(
KABRHA_ENV: env.mode,
```

</details>

### Wave 1 & 4 — Environment SSOT Gate & Conformance

| Status | File | Delta |
|---|---|---:|
| `M` | `scripts/check-seams-gates.ts` | `+2 / -0` |
| `A` | `scripts/gates/gate-environment-ssot.ts` | `+358 / -0` |
| `A` | `tests/conformance/goldenEnvironmentSingleSource.spec.ts` | `+48 / -0` |

<details><summary>Key additions in <code>scripts/gates/gate-environment-ssot.ts</code></summary>

```ts
if (!/\bKABRHA_ENV=/.test(rawExample)) {
message: "Missing canonical KABRHA_ENV declaration in .env.example",
snippet: "KABRHA_ENV=dev",
if (!globalEnv.includes("KABRHA_ENV")) {
"turbo.json globalEnv must include KABRHA_ENV to prevent cross-mode build cache poisoning",
snippet: '"globalEnv": ["KABRHA_ENV", ...]',
```

</details>

<details><summary>Key additions in <code>tests/conformance/goldenEnvironmentSingleSource.spec.ts</code></summary>

```ts
`export const a = "https://kabrha.com";\nexport const b = "http://127.0.0.1:4000";\nexport const c = process.env.API_URL;\n`,
```

</details>

