# Scaffolding `blockiya-core` — Tool-Agnostic Guidelines

How to place the complete v2.1.0 `blockiya-core` utility package into a project. This guide defines **what** to create and **the invariants it must satisfy**; **how** you create the files is yours to choose — hand-write them, let the agent emit them directly, use the bundled `scripts/scaffold_blockiya_core.py` as one convenience option, or write an equivalent generator in whatever scripting language the project already has. No particular tool is mandated.

Canonical source of truth for each file's implementation: [blockiya-core-reference.md](blockiya-core-reference.md). This document only adds the assembly and verification procedure so no intermediate generator script is required.

---

## Prerequisites

- A React + TypeScript project — this guide assembles the canonical React/TS package. The pattern itself is framework-agnostic: on Vue, Svelte, Solid, or MAUI/Blazor, re-implement the roles natively per "Blockiya beyond React" in [methodology-and-rules.md](methodology-and-rules.md) instead of porting these 15 files.
- Target location: `src/shared/<utilities-package>/` — `blockiya-core` is the author's recommended name; the location is conventional, the barrel-import rule below is not negotiable.
- Path alias configured so consumers import from a single public barrel, e.g. `@/shared/blockiya-core` (map it through `tsconfig.json` `paths`, a bundler alias, or the project's equivalent mechanism).

## Manifest

Create exactly this tree — 15 files, four category folders plus the barrel:

| File | Category | Implementation source |
| --- | --- | --- |
| `index.ts` | Barrel | `blockiya-core-reference.md` § index.ts |
| `structural/If.tsx` | Structural | § `If` |
| `structural/Maybe.tsx` | Structural | § `Maybe` |
| `structural/For.tsx` | Structural | § `For` |
| `structural/Repeat.tsx` | Structural | § `Repeat` |
| `structural/Compose.tsx` | Structural | § `Compose` |
| `intents/useIntent.ts` | Intents | § `useIntent` |
| `intents/createIntent.ts` | Intents | § `createIntent` |
| `intents/composeIntents.ts` | Intents | § `composeIntents` |
| `derivation/useDerive.ts` | Derivation | § `useDerive` |
| `derivation/useDerivedState.ts` | Derivation | § `useDerivedState` |
| `hooks/useToggle.ts` | Interaction | § `useToggle` |
| `hooks/useDebounce.ts` | Interaction | § `useDebounce` |
| `hooks/usePrevious.ts` | Interaction | § `usePrevious` |
| `hooks/useStableCallback.ts` | Interaction | § `useStableCallback` |

## Assembly rules (invariants)

1. **Barrel-only surface.** `index.ts` re-exports every value and type utility; consumers import solely from the package barrel, never from `structural/`, `intents/`, etc. The internal layout is free to change only because this rule holds. Export types (`UseIntentResult`, `Intent`, `IntentCreator`) alongside their values.
2. **No cross-category dependencies inside the package.** Each utility stands alone; `useIntent` internally stabilises its handler rather than importing `useStableCallback`. Keep it that way — the package must have zero dependencies beyond `react` (and `react` types).
3. **One file per utility, named exactly as the export.** `For.tsx` exports `For`, `useIntent.ts` exports `useIntent`. `.tsx` for components that emit JSX, `.ts` for hooks and plain functions.
4. **Copy the reference implementation verbatim** rather than re-deriving it — the reference encodes deliberate decisions (module-scope deriver contract in `useDerive`, ref-stabilised `fire()` identity in `useIntent`, `Object.is` reset detection in `useDerivedState`). Deviating silently breaks Strict Blockiya guarantees.
5. **Idempotency.** If the target already contains a `blockiya-core/`, do not overwrite it — reconcile file by file (missing files added, existing files diffed against the reference) and report differences. A project may carry a locally extended version; clobbering it is a regression.

## Verification checklist

After assembly, confirm:

- [ ] `npx tsc --noEmit` (or the project's typecheck command) passes with the package present.
- [ ] A smoke Blockiya imports `{ If, useIntent, useDerive } from '@/shared/blockiya-core'` and renders.
- [ ] The barrel is the only import path used anywhere in the codebase (grep for deep imports into `blockiya-core/` subfolders — zero hits expected).
- [ ] `python scripts/audit_blockiya.py <block.tsx> --strict` passes on a Blockiya consuming the package (the audit enforces the barrel rule mechanically; use `--core-name <name>` when the package carries a name other than the recommended `blockiya-core`; if the project prefers another language for its tooling, replicate the barrel-rule check there).

## Drift policy

When the reference doc gains a utility (future `blockiya-core` versions), add it to: the manifest above, `index.ts`, and the project's copy — in that order. The reference document owns the implementation; this document owns the assembly procedure; the project copy is disposable and re-derivable from both.
