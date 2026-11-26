---
name: environment
description: Audit, unify and enforce a single source of truth (SSOT) for environments in any codebase - environment modes (dev/test/staging/production), env vars, URLs/origins/ports, loopback and cookie handling, business identity (domain, support email, app id), dev/test shortcuts, and mobile build env - then fix every violation, add an enforcement gate, and document it. Use this skill whenever the user mentions environments, env vars, .env files, NODE_ENV, dev vs staging vs production, "production-like", hardcoded domains/localhost/ports/emails, process.env or import.meta.env scattered everywhere, dev-login or test-only routes leaking into production, localhost vs 127.0.0.1 cookie/CORS bugs, turbo/Vite/Nuxt/Capacitor/Cloudflare Worker env loading, or says "unify/centralize/fix the environment" or "/environment" - even if they never say "single source of truth". Also trigger for Arabic requests such as "وحّد البيئات", "بيئة موحدة", "صلّح الـ env".
---

# Environment SSOT

Turn a repo's scattered environment handling into one typed, enforced, documented Single Source of Truth. This skill encodes a workflow that was proven on a large multi-surface monorepo (backend + Nuxt SSR site + Nuxt SPA admin + Vite/Ionic/Capacitor app + Cloudflare Worker + scripts + tests). It adapts to smaller repos by skipping surfaces that do not exist.

The outcome, whatever the stack:

1. One canonical **mode** variable with four modes, kept separate from toolchain variables.
2. One **capability matrix** that says what each mode may do (dev shortcuts, test mocks, rate limits, debug output, seeded data...).
3. One **env module** (pure, dependency-light) exposing ergonomic helpers; everything else imports from it.
4. One **seam per surface** where raw env is read; nowhere else.
5. A **gate** (static check + conformance test) that fails on any new violation, proven red-first.
6. **Docs and records** updated in the same change so code and documentation cannot drift.

**Before starting, read `references/worked-example.md`** - it shows a finished run role by role (what each file does, wave order, test inventory, done-evidence). `references/reference-implementation-diff.md` is the raw diff of that run for lookup when you need to see how a specific kind of file ended up. Names there are project-specific; copy roles, never names or values.

Why this order matters: environment bugs are silent. A `process.env.NODE_ENV !== "production"` check evaluates to "dev" in a browser or Worker where `process` is undefined; a `?devMode=true` flag works in production because nobody guarded it. The only reliable fix is to make the violation machine-detectable first, then migrate until the detector is quiet.

## Step 0 - Orient and confirm decisions

Before touching code, read the repo's own governance docs if any exist (AGENTS.md, CLAUDE.md, architecture/ADR folders, steering docs, a decisions index, error catalogs). Their rules override the defaults below; this skill adapts to them, not the other way around.

Then detect the surfaces present (read `references/surfaces.md` for per-surface loading mechanics) and run the baseline audit:

```bash
python <skill-dir>/scripts/audit_env.py <repo-root> --domains example.com --emails support@example.com --out env-audit.md
```

Pass the project's real domains/emails/app ids so hardcoded business literals are caught. The audit is a heuristic map, not the gate; it tells you the shape of the problem and which surfaces to parallelize.

Ask the user to confirm only the decisions that change the design (batch them in one message, propose a default for each):

- **Mode names.** Default: `dev | test | staging | production`. Accept aliases (`development`, `prod`, `stage`) at the parsing boundary only. If the user says "production-like", map it to `staging` unless they want a distinct fifth behavior; two names for one behavior caused churn on the original project.
- **Who gets shortcuts.** Default: dev shortcuts (dev-login, `?devMode=`, preview flags, debug overlays) in `dev` only; test mocks (outbox endpoints, fake ID tokens) in `test` only. Some teams allow test mocks in `dev` as well; ask once, record the answer in the ADR.
- **Seeded/fixture data** allowed in which modes (default: dev, test, and local staging; never production).
- **Third-party upstreams** (payment, data provider, auth) that need a per-mode connection rule, e.g. "production must use live HTTP, never fixture, never loopback".
- **Default locale/other app-behavior defaults** that the audit surfaced as env-adjacent bugs. Ask only if relevant.

If the user is unavailable, choose the defaults, state them in the plan, and continue.

## Step 1 - Core rules (apply everywhere)

**Respect system-owned variables.** `NODE_ENV`, `TZ`, `LANG`, `CI`, `PORT`, `HOST`, `VITEST*`, `ANDROID_HOME`, `ANDROID_SDK_ROOT`, `JAVA_HOME`, `GRADLE_OPTS`, `ORG_GRADLE_PROJECT_*`, Xcode `CONFIGURATION`/`SDKROOT`/`DEVELOPMENT_TEAM` belong to the OS, runtime or toolchain. Never overwrite or repurpose them. `NODE_ENV` stays `development | test | production` because bundlers (Vite/Rolldown, Vue, Nuxt) pick optimization paths from it; setting it to a custom value silently breaks production builds. The project's own mode lives in a prefixed variable (e.g. `<APP>_ENV`) and maps down: `staging` -> `NODE_ENV=production` so staging runs real production code paths.

**One mode variable per exposure class.** Browser bundles only see prefixed vars (`VITE_`, `NUXT_PUBLIC_`, `NEXT_PUBLIC_`, ...), so you need the same mode mirrored per surface (`<APP>_ENV`, `VITE_<APP>_ENV`, `NUXT_PUBLIC_<APP>_ENV`). The CLI runner sets all mirrors from one `--env=` flag so they cannot disagree.

**Never put secrets in client-exposed prefixes**, and never read a surface's prefix on the wrong surface (`VITE_*` in a Nuxt app is a bug). The registry (Step 3) encodes this so it is checked, not remembered.

**Capabilities, not mode comparisons.** Call sites ask `canUseDevShortcuts()` or `shouldRateLimitAuth()`, never `mode === "dev"`. This keeps the matrix editable in one place and makes the gate simple.

## Step 2 - Gate first (red-first proof)

Write the enforcement gate **before** migrating any app code, run it on the untouched repo, and record the baseline. A gate never observed failing is presumed broken. Read `references/gate-rules.md` for the rule set and the planted-violation self-test pattern.

Minimum rules:

| Rule | Catches |
|---|---|
| `RAW_DOMAIN_OR_CONTACT_LITERAL` | hardcoded domains, support/noreply emails, app ids, deep-link schemes outside the env module (include locale/translation JSON) |
| `RAW_LOOPBACK_OR_PORT_LITERAL` | `127.0.0.1`, `localhost`, `::1`, known dev ports outside the env module and explicit allowlist |
| `DIRECT_ENV_ACCESS_OUTSIDE_SEAM` | `process.env`, `import.meta.env`, `useRuntimeConfig`, `NODE_ENV`, dotenv imports outside the one seam file per workspace |
| `ENV_DRIFT` | var names that differ between `.env.example`, build-orchestrator config (turbo/nx), framework config, type declarations, mobile config |
| `UNGUARDED_NON_PROD_ROUTE_OR_HOOK` | dev-login, test outbox, fixture feeds, fake-token hooks, cache-purge endpoints not behind a capability helper |

Also add two cheap structural checks that the reference run found valuable: (a) the template `.env.example` declares the mode variable, and (b) the orchestrator's hashed env list includes the mode variable (otherwise a cached build from one mode is reused in another - cache poisoning).

Deliverables: the gate script, a conformance test that runs it, and synthetic planted-violation tests so each rule keeps proving it can fail after the repo reaches zero. Wire the gate into the repo's existing aggregate check command. Record the baseline count (it is the headline number in the final report).

## Step 3 - Build the core env module

Place it in the shared package (or `src/env/` in a single-app repo). Keep it **pure TypeScript + the repo's existing validator** (Zod etc.); no `dotenv`, no `node:fs`, no `process.env` reads inside it, so the same code runs in Node/Bun, browser, Nuxt SSR, Capacitor, and Workers. Read `references/core-module.md` for the file layout and contracts. Pieces:

- `modes`: mode enum, alias normalization, capability matrix (`references/mode-matrix.md`).
- `registry`: one typed descriptor per variable (key, owner surfaces, exposure, loading phase, description, value type, accepted examples, rejected examples with violation codes, schema). `.env.example` comments and the orchestrator's env lists should be generated or verified from this so they cannot drift.
- `urls`: surface ports, default local host, builders for every surface URL, allowed CORS origins (including native WebView origins when mobile exists).
- `loopback` + `cookies`: `isLoopback` (localhost, 127.0.0.1, ::1), `alignLoopback(url, currentHost)` so a page on `localhost` never calls an API on `127.0.0.1` (this split silently breaks cookies and CORS), cookie-domain resolution (host-only on loopback, `.rootDomain` on real domains), secure-cookie rule tied to protocol, not just mode.
- `business`: product/operator names, root domain, canonical origin, support/partnership/noreply emails, optional phone, mobile app id, deep-link scheme, legal dates. Read from env with a single documented default.
- `shorthands`: the ergonomic API (`isDev()`, `isProdBehavior()`, `canUseDevShortcuts()`, `apiUrl()`, `supportEmail()`, ...). No call site should need an object ceremony.
- `errors`: if the repo has an error catalog, give each distinct config failure its own atomic code (missing var, malformed origin, invalid mode, forbidden-in-mode, wrong surface prefix, weak secret, port out of range). Never echo secret values in messages or params. If there is no catalog, throw typed errors with the same fields.
- `factory`: a thin wrapper over `@t3-oss/env-core` / `@t3-oss/env-nuxt` (or equivalent) mapping validation failures to those codes. Use the library only inside this seam.

Register the new package export in every place the repo resolves workspace aliases (package.json exports, root index, test-runner alias, bundler alias). Missing one of these is the most common "works in tsc, fails at runtime" trap.

### Strict validation: fail at boot, never limp along

A validation library does not make you strict by itself. In the reference run, the env-library wrapper was in place but still let missing keys slide (defaults on required vars, empty strings accepted, lazy checks), so a bad deployment started and failed later or silently behaved like dev. Make the factory strict on purpose:

1. **Validate eagerly at the seam, at import/boot time**, not on first property access. A missing key must stop the process (or the build) before it serves anything.
2. **Required means required.** Mark each variable required/optional **per mode** in the registry. Required-in-this-mode variables have no `.default()` and no fallback literal. Defaults are allowed only for genuinely optional, non-critical values, and the default lives in the registry, not at the call site.
3. **Treat empty string as missing** (`emptyStringAsUndefined: true` in the library, or `.min(1)` in the schema) - `FOO=` in a template or CI secret must not pass as a value. The only exception is a variable the registry explicitly declares as "intentionally empty" (e.g. a cookie domain meant to be host-only).
4. **Never enable `skipValidation`** (or equivalent) except in a clearly named build step that does not produce a deployable artifact, and have the gate flag any use.
5. **The mode variable itself is strict in deployed contexts.** A silent `default("dev")` is dangerous: a forgotten variable in staging/production would run as dev. Allow the fallback to `dev` only when running an explicit local-dev command; in a production build or deployed runtime (`NODE_ENV=production`), a missing/invalid mode fails boot. Where a runtime literally cannot fail (a per-request edge handler), default to the safest mode (production), log it, and prefer setting it explicitly in each environment block of the deploy config.
6. **Use the library's strict runtime map and surface prefixes**: list every variable explicitly (`runtimeEnvStrict` or equivalent), set the client prefix, and wire the invalid-access hook so server-only variables read from client code throw instead of returning `undefined`. Check option names against the installed version of the library.
7. **Forbidden-in-mode and cross-variable rules are part of validation**, not later runtime checks: fixture upstream in production, loopback URL in staging/production, missing OAuth client id in production, secret in a client-exposed prefix. Use refinements or a post-validation step that throws the forbidden-in-mode error.
8. **Test it**: for every required variable and every mode, a unit test deletes the variable (and separately sets it to `""`) and asserts boot throws the expected violation code with the right params and no secret in the message. Add a gate rule that flags `.default(` on registry entries marked required.

## Step 4 - Loader, CLI runner, templates, orchestrator

- **Layered dotenv seam** (Node/Bun only, one file): precedence `OS env > .env.<mode>.local > .env.<mode> > .env.local > .env`. Honor intentionally empty shell values (`COOKIE_DOMAIN=""` must win). In `test`, skip `.env` and `.env.local` so a developer's real machine config never leaks into the suite. Collapse duplicate hand-rolled `.env` parsers into this one.
- **Script env helper** (`scriptEnv`): one function that runs the dotenv seam, validates through the factory, calls `initEnvironment`, and returns typed config. Every script, e2e config and playwright/test-runner config uses it instead of reading env itself.
- **CLI runner** (`with-env`): `--env=<mode> -- <command>` sets the mode and all prefixed mirrors, maps `NODE_ENV`, loads layers. This replaces cross-env and works on Windows, macOS, Linux.
- **Templates**: `.env.example` plus one `.env.<mode>.example` per mode; fix any name mismatches discovered (see `references/pitfalls.md`); update `.gitignore` so templates are tracked and real files are not.
- **Orchestrator config** (turbo/nx): build-affecting variables belong in the hashed list (`globalEnv`), not pass-through, otherwise a cached `dev` build can be replayed for `production`. Remove dead entries, add missing ones. Add package scripts: `dev`, `dev:staging`, `build:staging`, `build:prod`, `check:env`, and `mobile:env:sync` if mobile exists.

## Step 5 - Migrate surfaces

Parallelize by surface when subagents are available (one worker per surface, each told: seam file path, helpers to use, gate command, and "do not edit files outside your surface"); otherwise go surface by surface. Order: backend first (it owns secrets and guards), then web surfaces, then edge/scripts/tests. Per-surface mechanics live in `references/surfaces.md`. For every surface:

1. Create exactly one seam file that reads raw env and calls `initEnvironment`.
2. Replace every other raw read with a shorthand/capability call.
3. Replace hardcoded domains, emails, loopback URLs, ports with builders.
4. Guard every non-production route/hook with the matching capability, and fail boot on forbidden combinations (e.g. fixture upstream in production, loopback origin in staging/production).
   Make guards testable: a guard reads capabilities from the injected app config first (`config.environment?.capabilities.x`) and only falls back to the global helper, so tests can exercise each mode without global state.
5. Run the gate and that surface's build/tests before moving on.

Parameterize business literals inside translation/locale files (`{domain}`, `{supportEmail}`, `{operator}`, `{year}`) and make sure bidi-sensitive tokens (URLs, ports, codes) are isolated in RTL locales.

Unify duplicated test config mocks into a single env factory in the test-support folder.

Expect the gate to surface a few edge-case false positives (IPv6 `::1` hostname extraction, WebView hostnames that must stay `localhost`). Fix the rule or add a narrow, commented allowlist entry; never loosen a rule globally.

## Step 6 - Mobile (only if Capacitor/Gradle/Xcode exists)

Read `references/surfaces.md` section "Mobile". Key points: never touch SDK/toolchain vars; sync build fragments from the mode via a script; per-mode logging/debuggable flags; reject loopback API origins in staging/production; correct client-id variable names; include native WebView origins (`https://localhost` for Android, `capacitor://localhost` for iOS) in backend CORS; never rewrite native WebView loopback hosts as if they were a dev browser.

## Step 7 - Documentation in the same change

Agent-instructions file first: if the repo has an AGENTS.md (or CLAUDE.md, CONTRIBUTING.md, or any file agents are told to read first), add a short environment section there in whatever format that file already uses: the four modes, mode-vs-`NODE_ENV` separation, the capability matrix, the rule "read env only through the seam, never `process.env`/`import.meta.env` directly", and any upstream-connection rule. Future agents read that file before anything else, so this is what keeps the SSOT from being undone. If the file already has numbered/named rules, add one in that style; do not invent a new rule system.

Update whatever the repo uses to record decisions: an ADR describing modes, mode-vs-NODE_ENV separation, loading lifecycles per surface, seams, mobile rules and the shorthand API; architecture/steering docs that list seams or settings; usage docs with commands for each mode; changelog; any decision or lessons-learned logs the repo keeps; and run the repo's doc-link/orphan checker if it has one. Add the new seams (dotenv, env library) to any seam/dependency register.

## Step 8 - Verify and report

Run, in this order, and fix until green: the new gate (must go from baseline N to 0), the repo's aggregate check, conformance tests, unit tests (including a 4-mode matrix test, diagnostics tests per violation code, planted-violation tests, loopback/cookie tests), integration/contract tests, staging builds of every web surface via the CLI runner, mobile env sync (and a negative test: loopback under staging must fail), doc checks. Do not run a full typecheck if the user's standing preferences say not to; say so in the report.

Final report: baseline vs final violation count; files changed by area; behavioral bugs fixed (list them, they are the real value); commands run with pass/fail; pre-existing failures that are out of scope, named precisely so nobody mistakes them for regressions.

## Working style

- Plan briefly, then execute; do not stall for approval on decisions with sensible defaults.
- Prefer fixing root causes in the module over patching call sites.
- Keep the user's language for conversation; write code, docs and comments in the language the repo already uses.
- Pre-existing violations unrelated to environment (other gates) are reported, not silently "fixed".

## Guardrails for weaker or less-informed agents

If you are a smaller model or have no prior context, follow these literally; they are what makes the result reproducible.

1. **Do the steps in order and do not skip the gate.** Without the baseline you cannot tell when you are done.
2. **Checkpoint after each step**: run the gate, record the count, and write one line in your running notes ("step 5 backend: gate 132 -> 71"). If the count goes up, stop and find why.
3. **Never edit by guessing names.** Read `env.d.ts`, `.env.example`, the framework config and the orchestrator config before choosing variable names; copy the exact names the code already reads, and fix mismatches deliberately (record each in the report).
4. **One seam file per workspace, no exceptions.** If you feel the urge to read env somewhere else, add a field to the env module and a shorthand instead.
5. **Do not widen the gate to make it pass.** Fix code, or add a single narrow commented allowlist entry.
6. **Re-run after every formatter/linter pass.** Results from before formatting are not evidence.
7. **Separate regressions from pre-existing failures** by running the failing check on a clean stash/branch or by checking whether the failing files are ones you touched. Report pre-existing ones by name.
8. **Do not invent behavior for the matrix**; use `references/mode-matrix.md` and the user's confirmed decisions. When a decision is open, pick the default, state it, continue.
9. **Large repos**: split by surface and delegate if you can; each worker gets the seam path, helper list, gate command and a boundary ("only your surface"); reconcile at the end with a full gate + test run.
10. **Keep the final report factual**: numbers, commands, pass/fail. No claims you did not run.

## Definition of done

Tick every box (or state why N/A) before reporting completion:

- [ ] Agent-instructions and governance docs read; any rule conflicts resolved in their favor
- [ ] Baseline audit + gate baseline recorded; gate observed failing red-first
- [ ] Mode variable + aliases + capability matrix implemented; NODE_ENV untouched except the documented mapping
- [ ] Registry covers every variable (owner, exposure, phase, schema, accepted/rejected)
- [ ] Strict validation: eager at boot, no defaults on required vars, empty string rejected, no `skipValidation`, missing-var tests per mode
- [ ] Violation codes (or typed errors) for all 7 failure kinds; no secret ever echoed
- [ ] Core module is pure; package export registered in every alias location
- [ ] Layered dotenv seam, script env helper, CLI runner, per-mode templates, orchestrator lists, package scripts
- [ ] Every surface has exactly one seam; no other raw env reads (gate proves)
- [ ] Every dev/test/fixture/purge route and hook guarded; forbidden combos fail boot
- [ ] Loopback alignment and cookie/secure rules used by every surface; CORS includes native origins if mobile
- [ ] Business literals removed from code and locale files
- [ ] Test env factory replaces duplicated mocks
- [ ] Mobile sync works in dev and rejects loopback in staging/production (if mobile)
- [ ] Gate at 0 with planted-violation self-tests; registered in aggregate check
- [ ] 4-mode matrix tests, diagnostics tests, integration tests green; staging builds of all web surfaces pass via the CLI runner
- [ ] ADR, architecture/steering docs, usage, changelog, agent-instructions file, decision/lessons logs updated; doc link/orphan check clean
- [ ] Final report: baseline -> final, bugs fixed, commands run, pre-existing failures named
