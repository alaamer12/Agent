---
name: code
description: Mandatory pre-coding protocol before ANY task that writes, modifies, or implements code - language-agnostic. Three gates, in order: (1) a coding brief naming the app/module being coded and which stack-agnostic concerns it touches (interfaces, styling, a11y, navigation, forms, persistence, platform, concurrency, errors, build); (2) root inspection to detect the real toolchain (lockfile decides - bun.lock->bun, package-lock.json->npm, Cargo.lock->cargo, go.mod->go, uv/poetry.lock->python; binding project rules outrank inference); (3) targeted grounding of ONLY the touched concerns in CURRENT official docs for each ecosystem, via the `scrape` skill when available (cache + grep over re-fetching; WebFetch fallback), with trade-off questions to the user instead of silent picks. Use before scaffolding/editing source in any stack (TypeScript frameworks, Rust, Python, Go, ...) - it exists to stop coding from model memory that went stale. Chain with project standards skills when present.
---

# Code — brief, toolchain, docs-grounded, then write

## Overview

Never let a code edit start from memory. Every ecosystem drifts - Rust editions and trait APIs churn, Python frameworks deprecate whole patterns, JS component APIs get renamed between majors, Go stdlib gains context-aware variants - so a confident-looking API from training time is a latent bug. Three gates precede the first edit to source. The invariant: **grounding beats guessing, in any language.**

## Gate 1 — Coding brief (state it before touching code)

```
CODING BRIEF
scope      : <app / module / component under change>
stack      : <language + framework/runtime>
touches    : <concerns from the checklist>
docs need  : <concern -> its official-docs target>
```

Concern checklist — stack-agnostic categories; the tags drive Gate 3's targeting:
- `interfaces` — public API usage: functions, methods, options/arguments, properties/attrs, events/signals, return contracts
- `styling` — theming, design tokens, visual customization surfaces
- `a11y` — accessibility semantics of the touched components/endpoints
- `navigation` — routing, lifecycle, back handling
- `input` — forms, validation, keyboard/user input surfaces
- `persistence` — storage, caching, state management
- `platform` — device/OS/runtime capabilities: plugins, syscalls, FFI, external services
- `concurrency` — async tasks, jobs, cancellation, shared-state safety
- `errors` — failure contracts: exceptions, results, status mapping
- `build` — dependencies, scripts, CI -> resolved by Gate 2

Repo instance: `scope` values come from the project's own maps (MuslimTube: `Docs/v1/mob/structure.md` / `Docs/v1/OW/structure.md` define the two apps). Small change? The brief is still required, even 3 lines — it is the audit trail.

## Gate 2 — Detect the root and the real toolchain

1. Read the actual project root (not memory): list lockfiles and manifests.
2. Toolchain = what the root declares:

| Evidence in root | Toolchain | Install / run |
|---|---|---|
| `bun.lockb` / `bun.lock` | Bun | `bun install`, `bunx <tool>` |
| `package-lock.json` | npm | `npm install`, `npx <tool>` |
| `yarn.lock` | yarn | `yarn`, `yarn dlx` |
| `pnpm-lock.yaml` | pnpm | `pnpm`, `pnpm dlx` |
| `Cargo.lock` / `Cargo.toml` | cargo | `cargo add` / `cargo run` (single manager - just use it) |
| `go.mod` | go | `go get` / `go run` |
| `uv.lock` / `poetry.lock` / `requirements.txt` | uv / poetry / pip | match the lockfile |
| `Gemfile`, `mix.exs`, `composer.json` | bundler / mix / composer | ... |

3. **Binding project rules outrank lockfile inference.** Repo instance: AGENTS.md mandates bun + bunx for all JS/TS - a stray `package-lock.json` is a decision-duplication defect to flag, not a reason to switch.
4. Never install at Gate 2. Adding a dependency is a separate deliberate step naming why it is justified.

## Gate 3 — Ground the touched concerns in current docs (targeted, not bulk)

Only for the concerns the brief flagged: theming task -> only theming docs. For each ecosystem, the canonical source:

| Ecosystem | Grounding target | Mechanism |
|---|---|---|
| JS/TS framework docs (Docusaurus, MkDocs, Sphinx sites) | official site subtree | `scrape` registered command (e.g. `ionic`) or `--auto START_URL --verify` |
| Rust | std/core via doc.rust-lang.org (BFS-proven), crates via docs.rs | `scrape --auto`/`--url`, or `cargo doc -p <crate>` + read local target/doc |
| Python | the library's docs site (FastAPI-proven) | `scrape --url`/`--auto` the needed pages |
| Go | pkg.go.dev page for the exact package/version | `--url` the doc page, or `go doc <pkg> <symbol>` |

1. **Cache-first:** if a docs cache exists (`scratch/docs-<name>/`), grep it instead of re-fetching:
   `grep -rn "<symbol>" scratch/docs-<name>/ -l`
   No cache for a registered framework? build it once (scrape verifies server-rendered content before writing). Unregistered site -> `--auto ... --verify`, then scrape only the needed subtree. No `scrape` available -> WebFetch the exact pages; same targeting rule.
2. **Every API symbol about to be typed** (function, method, option, attribute, command flag) **must hit the docs before it hits code.** Memory-only usage is a defect until grounded. Note version drift when the cache is older than today.
3. **Trade-offs, not silent picks:** if grounding surfaces several viable choices (two APIs for one job, sync vs async pattern, deprecated vs replacement path), present options + trade-offs to the user and record the decision - don't pick silently.
4. Cite `file.md:line` of the cache for nontrivial decisions so diffs are reviewable against sources.

## Execution and reporting

- Paste the Gate 1 brief before the first edit; finish by listing what could NOT be grounded - ungrounded API use gets cut, not shipped.
- State which skills were used (`code` + `scrape`/project standards skills) per AGENTS.md.
- Repo instance: same-change obligations (UNITS.md sync, UI construction chain, docs-in-diff) still apply - these gates precede them, they don't replace them.

## Anti-patterns

- Writing API usage from memory "because I know this one" - in ANY language.
- Muscle-memory `npm install` / `pip install` / `cargo add` against what root evidence says.
- Mass-fetching a whole docs site for a one-symbol fix, or re-fetching when a cache exists.
- Silently choosing among viable APIs the grounding revealed instead of asking.
- Treating a green compile/tests as grounding: they check syntax and logic, never currentness.

## Resources

- `examples/polyglot-briefs.md` — three complete gate runs (TypeScript/Ionic, Rust, Python/FastAPI), naive-vs-grounded.
