# Surfaces: how env actually loads (and the trap on each)

Detect which of these exist, then apply only those sections. The central lesson: **the loading mechanism differs per surface**, so one naive `process.env` helper is wrong on at least half of them.

## Contents
- Backend / scripts / tests (Node, Bun)
- SSR framework with server + browser (Nuxt/Nitro, Next)
- Static SPA built by a framework (Nuxt generate, Vite)
- Vite client app
- Cloudflare Worker / edge
- Mobile (Capacitor, Gradle, Xcode)
- Orchestrator (turbo/nx)

## Backend / scripts / tests (Node, Bun)
- Mechanism: true in-process `process.env`, hydrated at boot by the layered dotenv seam.
- Trap: a live developer `.env` leaking into the test runner; intentionally empty shell overrides clobbered by file values.
- Do: one `config` module validates env through the factory, builds a per-instance config object (do not mutate global state when tests pass overrides), fails boot on forbidden mode combinations.
- Guard: dev-login, test outbox, fake-token paths, fixture-feed endpoints behind capability helpers. Enable auth rate limiting for every production-behavior mode (staging included). Debug fields in error responses only where `shouldExposeErrorDebug()`.
- CORS: build allowed origins from the env module, not from literals; include native WebView origins if mobile exists.
- Look for double-wrapped responses on routes you touch (wrapper applied twice) - a bug found incidentally in the original run.

## SSR framework (Nuxt 4 + Nitro, Next)
- Mechanism: dual phase. Server-private config on Nitro; public config serialized into the page and re-read in the browser on hydration.
- Trap: reading `process.env` inside components; assuming container env overrides are visible to the client bundle.
- Do: three small files - a public config seam (used by the app), a plugin that initializes the env early (name it so it sorts first, e.g. `00-env`), a server util that builds the server env from the request event. Put mode, URLs and business identity in `runtimeConfig.public`, secrets in private `runtimeConfig`.
- Guard internal endpoints (cache purge etc.) with a constant-time secret comparison whenever `isProdBehavior()`.
- Use `alignLoopback()` for every client-side navigation/API URL so `localhost:3001` never jumps to `127.0.0.1:5173`.
- Wrong prefix check: the old var `NUXT_PUBLIC_SITE_URL` vs what config reads (`NUXT_PUBLIC_MARKETING_URL`) is the typical drift.

## Static SPA built by a framework (Nuxt generate, plain Vite SPA)
- Mechanism: **build-time bake**. Only public-prefixed values; no runtime server, no secrets.
- Trap: believing a `.env` change after build affects the deployed bundle.
- Do: document it in the registry as `build-time-static`; validate only public vars.

## Vite client app
- Mechanism: static AST replacement of the literal expression `import.meta.env.VITE_X`.
- Trap: `Reflect.get(import.meta, "env")`, `import.meta.env?.[key]`, destructuring or dynamic keys compile to `undefined` in production builds, and work in dev so nobody notices.
- Do: a single `config/env.ts` that lists every `import.meta.env.VITE_*` as a literal dot-access, feeds them to the factory (`clientPrefix: "VITE_"`, strict runtime map), and calls `initEnvironment` before router/store creation. Update `env.d.ts` for every var. Inject static HTML values (OG image URL) with a `transformIndexHtml` plugin instead of hardcoding in `index.html`. Register the shared env export in the bundler alias.
- Also search packages (shared UI/composable libs) for the same dynamic-access trap.

## Cloudflare Worker / edge
- Mechanism: per-request `env` parameter (`fetch(request, env)`); no `process`, no `fs`, no dotenv.
- Trap: top-level `process.env.NODE_ENV !== "production"` is `undefined !== "production"` => treated as dev => debug leaks to production. Any shared code that reads `process.env` defensively has this bug on the edge and in browsers.
- Do: build the environment from the per-request env object; mode comes from a `vars` entry in wrangler config per environment block (`[env.staging]`, `[env.production]`); default to the safest mode (production) when unset. Replace hardcoded origins and `app.` subdomain heuristics with builders.

## Mobile (Capacitor, Gradle, Xcode)
- Respect toolchain variables (see SKILL.md Step 1). Read-only.
- Sync script generates build fragments from the mode: Capacitor config, Android Gradle properties, iOS xcconfig. It must not export SDK paths.
- Per mode: `dev` -> verbose logging, WebView debugging on, loopback/LAN API allowed. `staging`/`production` -> logging none, WebView debugging off, strict `https://` API and marketing origins, loopback rejected with the forbidden-in-mode error. Exit non-zero on violation (test this negative path).
- `capacitor.config.ts`: app id from the business module; correct Google/OAuth client id variable name (a typo between `*_CLIENT_ID` and `*_WEB_CLIENT_ID` was a real bug); keep `server.hostname: "localhost"` - that is the WebView's own origin, not an env leak; allowlist it in the gate.
- Native origins: Android WebView serves from `https://localhost`, iOS from `capacitor://localhost`. Backend CORS must include both in every mode or the shipped app is blocked in production.
- API client: never apply "rewrite loopback to proxy" logic when `platform.isNative`; `isLoopback("localhost")` is true inside the WebView and rewriting breaks every request.
- Universal-link files (apple-app-site-association, assetlinks.json) are built from the app id plus team id / cert fingerprint env vars, not literals.

## Orchestrator (turbo / nx)
- Variables that change build output go in the hashed list; pass-through is for runtime-only values. Wrong placement lets cached `dev` output be reused for production.
- Verify against the registry: no dead names, no missing names. Make this a gate rule.
