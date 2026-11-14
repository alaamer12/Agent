# Agenda — JavaScript, Plain (no UI framework)

Scope: JS projects with no UI framework — backends, worker fleets, CLIs, services. React/Vue-specific conventions belong in their own future folders; the spectra in `../../../decision-spectra.md` still apply there too.

TypeScript is this language's typing layer, not a separate stack — every idiom note below assumes `.ts` by convention; a plain-`.js` project drops only the type-only artifacts (interfaces, `.d.ts`), never the underlying decision.

This file does not re-argue *why* a spectrum's endpoints matter — that reasoning lives once in `../../../decision-spectra.md`. It says how this ecosystem typically expresses a choice on each spectrum. Before applying any of it, check `../../../principles.md`'s requirement-fidelity rule first: if the user already stated an answer to a question below, their answer wins outright — nothing here is a substitute for it.

## Idiom notes, mapped to the spectra

- **Repo boundary** → Bun or pnpm workspaces make a single-repo choice mechanically cheap; npm workspaces works but is weaker on hoisting/speed at scale.
- **Deployable boundary** → conventionally expressed as `apps/` (independently deployed) vs. `packages/` (imported only) — a naming pair, not a new argument; the underlying test is still "does deleting this change what deploys."
- **Shared-ground threshold** → conventionally `packages/<domain>` once a second consumer needs the same answer.
- **Cross-engine query duplication** → conventionally a small typed filter/query language in a shared package, compiled per engine, protected by a differential test. See `examples/cross-engine-query-duplication.md`.
- **Isolation cost** → check the actual stated deploy target before assuming either way — a specific named platform's own requirements outrank any general convention about containerization. See `examples/skip-containerization-lockfile-deploy.md`.
- **Naming** → role-based directory names (`rules/`, `computations/`) over type-based ones (`utils/`, `helpers/`) applies with no ecosystem-specific twist.
- **Worker/fleet language commitment** → default single-language fleets are a convention, not a requirement — if the user states a language-agnostic requirement, the fleet is split by language from the start, not forced uniform. See `examples/language-agnostic-worker-requirement.md`.

## Examples

- **`examples/skip-containerization-lockfile-deploy.md`** — requirement-substitution: a stated Railway deploy target got answered with an unrequested Dockerfile instead of Railway's own config.
- **`examples/cross-engine-query-duplication.md`** — cross-engine duplication spectrum: why hand-duplicated query logic across two storage engines is a decision-duplication risk that doesn't read as one, and the single-filter-language fix.
- **`examples/language-agnostic-worker-requirement.md`** — requirement-substitution: a stated "any language" worker requirement got overridden by an unstated single-language convention in the first draft.
