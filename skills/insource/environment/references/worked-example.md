# Worked example: what a finished run contains (role -> file -> what it does)

Source: the Kabrha run. Full diff in `reference-implementation-diff.md`. Map roles, not names.

## Contents
- Shape and size
- Role inventory
- Execution waves actually used
- Test inventory
- Verification evidence that counted as "done"
- Things the first agent had to discover the hard way

## Shape and size
~116 files touched (+5.4k / -0.9k lines): ~20 core-module files incl. a 573-line unit test file, 11 loader/CLI/template/orchestrator files,
~21 backend files, ~16 client+mobile, ~21 marketing, 5 admin+edge, 14 scripts/tests, 3 gate files, ~15 doc/ledger files.
Expect a repo of this size to take several waves; a small single-app repo is a fraction of it.

## Role inventory
| Role | Reference file(s) | Contract |
|---|---|---|
| Mode + capabilities | shared `env/modes.ts` | enum, alias map, `normalize`, `EnvCapabilities` per mode |
| Registry | shared `env/registry.ts` (~430 lines) | descriptor per var incl. SNDUK upstream vars |
| Error mapping | shared `env/errors.ts`, `errors/val.ts`, 3 locale JSONs | codes 010..016 + localized messages |
| Library wrapper | shared `env/t3Factory.ts` | `createKabrhaT3Env`, used by every seam |
| URLs/ports | shared `env/urls.ts` | `SURFACE_PORTS`, `DEFAULT_LOCAL_HOST`, builders, default upstream URL |
| Loopback/cookies | shared `env/loopback.ts`, `cookies.ts` | `extractHostname`, `isLoopbackHost`, `alignLoopbackHostname`, `resolveCookieDomain`, `resolveUseSecureCookies` |
| Business | shared `env/business.ts`, `schemas/legalIdentity.ts` | schema + defaults; legal identity delegates live |
| Mobile | shared `env/mobile.ts` | `buildMobileBuildConfig`, `resolveCapacitorOrigins` |
| Shorthands | shared `env/shorthands.ts` | `createEnvironment/initEnvironment/getEnvironment` + all helpers |
| Debug helper fix | shared `errors/duckDebugger.ts` | uses `canUseDevShortcuts()` and port constants |
| dotenv seam | `scripts/lib/dotenvSeam.ts` | layered precedence, test skips `.env`/`.env.local` |
| Script env | `scripts/lib/scriptEnv.ts` | `loadScriptEnv()` = seam + factory + `initEnvironment`; every script uses it |
| CLI runner | `scripts/with-env.ts` | `--env=<mode> -- cmd`; sets mode + `VITE_`/`NUXT_PUBLIC_` mirrors, NODE_ENV mapping |
| Mobile sync | `scripts/sync-mobile-env.ts` | writes build fragments; throws forbidden-in-mode on loopback in staging/prod |
| Templates | `.env.example` + `.env.{dev,test,staging,production}.example` | per-mode documented values; `.gitignore` allows templates |
| Orchestrator | `turbo.json` | mode keys + build vars in `globalEnv`, runtime in pass-through |
| Backend seam | `apps/backend/src/config.ts` | seam + factory; per-instance config, no global mutation on test overrides; boot guards |
| Backend guards | `routes/auth.ts`, `health.ts`, `auth/google.ts`, `auth/recovery.ts`, `email/service.ts`, `middleware/*`, `app.ts` | capability helpers; each accepts an injected `config.environment?.capabilities` first, falls back to global helper (testable) |
| Marketing seams | `src/config/env.ts`, `app/plugins/00-env.ts`, `server/utils/env.ts` | public vs server env; `nuxt.config.ts` validates mode and fills runtimeConfig |
| Marketing guard | `server/api/internal/purge-cache.post.ts` | constant-time secret check in prod-behavior |
| Admin seam | `apps/admin/src/config/env.ts` + nuxt config | public-only; local loopback helper deleted in favor of shared |
| Edge | `infra/edge/worker.ts`, `wrangler.toml` | mode from `KABRHA_ENV` var per env block; default production |
| Client seam | `apps/client/src/config/env.ts`, `env.d.ts`, `main.ts` | literal `import.meta.env.VITE_*`; init before router/store |
| Client fixes | `bffClient.ts`, `preferences.ts`, google auth (web+native), router paths, dev preview composables, `capacitor.config.ts`, `vite.config.ts`, `index.html` | see pitfalls |
| UI lib fix | `vue-core/.../useFeatureFlags.ts` | no `Reflect.get(import.meta)`; query override only with dev shortcuts |
| Test support | `tests/support/envFactory.ts` | single test env + backend config factory replacing 3 duplicates |
| Gate | `scripts/gates/gate-environment-ssot.ts`, conformance spec, registered in aggregate check | see gate-rules |
| Docs | ADR (matrix table), architecture docs, steering docs, USAGE, CHANGELOG, agent-instructions file (AGENTS.md rule), settled/learnt ledgers | see Step 7 |

## Execution waves actually used
1. Gate written and run red on untouched repo (baseline 132 violations).
2. Core module + errors + locales + registry + unit tests.
3. Loader, CLI runner, templates, orchestrator, mobile sync.
4. Backend migrated by the main agent; docs and ledgers drafted in parallel.
5. Four parallel workers: marketing; client+vue-core(+mobile); admin+edge+locales; scripts+tests.
6. Reconcile: gate re-run found stragglers (loopback helper, duck debugger, envFactory, snduk test, gate false positives), fixed, then full verification.
7. Re-run tests after every config fix; format touched files with the repo's linter; record outcomes in ledgers; final doc/orphan check.

## Test inventory (shared unit test file, ~10 tests)
- mode normalization and aliases; capability matrix for all 4 modes
- loopback detection incl. IPv6, alignment between localhost/127.0.0.1
- cookie domain and secure flag cases
- mobile origins (Android/iOS native origins included)
- each violation code produces the expected params and never echoes a secret
- registry completeness (every var has owner, exposure, phase, schema)
- legal identity delegation is live, not snapshot
Backend: boundary test per mode (prod rejects fixture upstream, rejects loopback upstream, requires token; dev-login/outbox/fixture routes 404 outside allowed modes). Conformance: planted-violation spec for the gate. Mobile: sync passes in dev, fails with loopback in staging.

## Verification evidence that counted as "done"
gate 132 -> 0 across ~600 files; aggregate seams check green except named pre-existing violations; conformance subset green; unit 75/75 incl. 10 new; integration 11/11; contract green; client + marketing staging builds exit 0 via the CLI runner; mobile sync dev pass / staging-loopback fail exit 1; doc orphan check 0; viber/ledger lint 0 errors.

## Things the first agent had to discover the hard way
- The env-library wrapper was not strict enough at first: required keys had defaults / empty values passed, so a missing key did not fail at boot. See "Strict validation" in SKILL.md; do it from the start.
- Unit/integration tests broke after the backend config became validated: tests must build config through the test env factory, not hand-rolled objects.
- Gate false positives on IPv6 hostname extraction and on config files that run before the seam; fix the rule narrowly.
- Duplicated config mocks in several tests hid drift until merged into one factory.
- A formatting-only pass after edits can invalidate "ran before formatting" results: re-run gate and tests after formatting.
- Missing binary asset in working tree caused unrelated conformance failures: classify, do not chase.
