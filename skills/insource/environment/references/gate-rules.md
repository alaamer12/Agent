# Gate design

Implement as a script (`scripts/gates/gate-environment-ssot.ts` or repo equivalent) that scans tracked source files and prints `file:line RULE_CODE message`, exit 1 on any violation. Add a conformance test that executes it, and register it in the repo's aggregate check command.

## Scan scope and exclusions
Scan: apps/, packages/, infra/, scripts/, locale JSON. Exclude: node_modules, dist/build output, lockfiles, the env module itself, `.env*.example`, edge config (`wrangler.toml`), tests/fixtures (but still ban raw `process.env` in tests unless they go through the test env factory), and explicit allowlist entries.

## Allowlist discipline
Each entry: path + rule + one-line reason (e.g. "Capacitor WebView hostname must be literal localhost"). No directory-wide or rule-wide wildcards.

## Rule details
1. RAW_DOMAIN_OR_CONTACT_LITERAL: regex built from the project's domains, emails, app id, deep-link scheme (read from `.env.example`/business defaults, not hand-copied).
2. RAW_LOOPBACK_OR_PORT_LITERAL: `127.0.0.1`, `localhost`, `[::1]`, `0.0.0.0` and the project's dev ports in non-test runtime sources.
3. DIRECT_ENV_ACCESS_OUTSIDE_SEAM: AST or regex for `process.env`, `import.meta.env`, `useRuntimeConfig(`, `NODE_ENV`, `from "dotenv"`, `@t3-oss/env-`. A map `{workspace -> seam file}` defines the only allowed locations. Config files that run before the seam exists (vite/nuxt/capacitor config) are listed explicitly.
4. ENV_DRIFT: set-compare names across `.env.example`, orchestrator config, framework runtime config, `env.d.ts`, mobile config, registry.
5. UNGUARDED_NON_PROD_ROUTE_OR_HOOK: list of sentinel strings (route paths, global hook names); each occurrence must be within N lines of or inside a block using a capability helper.

## Red-first protocol
1. Run on the untouched repo; save output; count by rule and by surface. This is the baseline.
2. Spot-check 5 known problems by hand to confirm each appears in the report (missing = rule bug).
3. After migration, run again: 0.
4. Planted-violation self-tests: in a temp dir, write one tiny file per rule that violates it, run the gate's scanner function on it, assert the exact rule code fires. Keeps the gate honest forever.

## Pre-existing violations
If other gates (not env) fail on files you did not touch, list them in the final report as out of scope instead of widening this task.
