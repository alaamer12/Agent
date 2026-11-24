---
name: blockiya-pattern
description: >-
  Architect, scaffold, refactor, review, and diagram component UI
  frontends using the Blockiya Pattern (v2.2.0, including Strict Blockiya and
  blockiya-core utilities) and the Blockiya UML Notation System (v2.0). The
  pattern is framework-agnostic—incubated and proven in React/TypeScript
  projects, expressed here in canonical React/TypeScript code, and portable to
  Svelte, Solid, Vue composables, or MAUI/Blazor C# (MVVM-adjacent). Use this
  skill whenever the user asks to design or build a Blockiya component,
  separate domain orchestration from presentational views, enforce zero-styling
  primitives or Emotion styled-system tokens, wrap third-party libraries in
  Adapters, scaffold or use blockiya-core helpers (If, Maybe, For, Repeat,
  Compose, useIntent, createIntent, composeIntents, useDerive,
  useDerivedState, useToggle, useDebounce, usePrevious, useStableCallback),
  generate Blockiya UML class or sequence diagrams, or audit components
  for Blockiya compliance and growth signals. Do not use for backend APIs
  or generic CSS styling tasks unrelated to Blockiya architecture.
license: MIT
metadata:
  author: Blockiya Architecture
  version: "2.2.0"
  uml-version: "2.0"
  standard: "agentskills.io"
---

# The Blockiya Pattern (v2.2.0)

Build, refactor, audit, and diagram applications using the **Blockiya Pattern**—a framework-agnostic architectural discipline where every layer knows only about the layer directly below it and fires intentions strictly upward. Incubated and proven in React/TypeScript projects; this skill's reference code is canonical React/TypeScript, and `references/methodology-and-rules.md` ("Blockiya beyond React") maps each role onto Svelte, Solid, Vue composables, or MAUI/Blazor C#.

Default to **Strict Blockiya (v2.1)** unless the user explicitly asks for the base/flexible variant.

**Named tools are illustrative, not mandated.** Where this skill names a specific library—Emotion, React Query, SWR, Zustand, Radix UI, Next.js, React Router—it exemplifies the architectural role that slot plays. Any tool filling the same role is acceptable, as is a hybrid; the Blockiya rules themselves (zero styling, derive before passing, intents upward) never change. React syntax (hooks, JSX) likewise is one stack's expression of the pattern, not the pattern—when working in another framework, port the roles and rules, not the syntax.

## Architectural Layer Stack

```text
Page
  └── Blockiya                        <- orchestrates domain state, talks to data, derives props
        ├── Child components           <- receive derived props, fire intents up
        ├── Behavioral Primitives      <- own interaction state internally (Dropdown, Modal)
        ├── Non-Behavioral Primitives  <- visual tokens only (Text, Box, Flex)
        ├── Adapters                   <- wrap third-party tools, translate tokens and events
        └── Utilities                  <- compatible helpers (If, useIntent, useDerive) — snap in, never steer
```

## Non-Negotiable Core Rules

Apply these rules across every Blockiya task:

1. **Zero styling in Blockiyas**: Never use `className`, `style`, inline CSS, or Tailwind classes inside a Blockiya. Route all visual output through `<<Primitive>>` and `<<Behavioral>>` components (recommended foundation: Emotion + `styled-system` + `shouldForwardProp`; use Emotion `<ClassNames>` only inside `<<Adapter>>` boundaries).
2. **Data only via hooks**: Never call `fetch()`, `invoke()`, or API clients directly in a Blockiya. Consume hooks from the feature's `queries/` layer.
3. **Derive before you pass**: Never pass raw API/domain models to presentational children. Transform data via a named module-scope deriver (and `useDerive` in Strict Blockiya) first.
4. **Fire intents and stop**: Emit upward callbacks (`onSaveIntent`, `onDeleteIntent`, etc.) and stop. Never show confirmation modals, navigate, trigger sibling refreshes, or decide post-action UX inside the Blockiya.
5. **3-7 props in, 3-7 intents out**: Treat >7 props or intents as a mandatory split/extraction signal.
6. **Compound components for behavioral primitives**: `<<Behavioral>>` primitives (`Dropdown`, `Modal`, `Tooltip`, `Tabs`, `Accordion`) must own interaction state (`isOpen`, focus trap, keyboard nav) internally via a compound API—never via a hook that leaks `isOpen` upward. Exception: **imperative primitives** (e.g., toasts via `showToast(...)`) must be documented explicitly as imperative.
7. **Adapters isolate third-party libraries**: Wrap external tools (CodeMirror, xterm.js, chart/avatar libs) in top-level `adapters/` components responsible for exactly three jobs: **token translation**, **event translation**, and **lifecycle management** (mount/destroy). Adapters never own domain state.

### Strict Blockiya v2.1 Requirements (Recommended Default)

When operating in Strict Blockiya mode, enforce all base rules plus:

- Wrap every async handler with `useIntent`—never write manual `isLoading`/`error` `useState` pairs or repeated `try/catch` blocks.
- Perform all read-only prop derivation with `useDerive` (module-scope deriver) and all editable server-seeded drafts with `useDerivedState`—never use inline `useMemo` or inline object derivation in the Blockiya body.
- Express conditional, null-safe, iterative, skeleton, and provider-wrapping rendering explicitly via `<If>`, `<Maybe>`, `<For>`, `<Repeat>`, and `<Compose>`—replace inline `{cond && <X />}`, ternaries, and `.map()` calls.
- Import all utilities solely from the single public barrel of the utilities package — never from internal subpaths. `blockiya-core` is the author's recommended name for that package (`@/shared/blockiya-core`); the rule binds the single-barrel contract, not the name.

## Stereotype Quick Map

| Stereotype | Role | Scope / Placement |
| --- | --- | --- |
| `<<Page>>` | Top-level route & post-intent orchestrator | `features/<name>/routes/` or `app/` |
| `<<Feature>>` | Large multi-step workflow orchestrator (5+ children) | `features/<name>/blockiyas/` |
| `<<Compound>>` | Multi-component Blockiya (2-5 child blocks) | `features/<name>/blockiyas/` |
| `<<Atomic>>` | Single-purpose leaf Blockiya | `features/<name>/blockiyas/` |
| `<<Primitive>>` | Non-behavioral visual token component | `shared/ui/primitives/` |
| `<<Behavioral>>` | Interactive compound component (internal state) | `shared/ui/behavioral/` |
| `<<Context>>` | Context object provider for shared feature/form state | `features/<name>/blockiyas/<Block>/context.ts` |
| `<<Hook/Query>>` | Data fetching/mutation hook | `features/<name>/queries/` |
| `<<Adapter>>` | Third-party wrapper (tokens, events, lifecycle) | `adapters/<tool>/` |
| `<<Utility>>` | Compatibility slot — any helper that works alongside Blockiya without contradiction or taking over control (domain-free, visual-free) | `shared/blockiya-core/` or any compatible package |

## Resource Routing (Just-in-Time Loading)

Load only the reference file(s) required for the current task:

- **Full methodology, Emotion/TypeScript token setup, state placement, React pattern toolkit, Blockiya-beyond-React framework mapping, growth signals, battle-tested edge cases, project layout, and version history**: Read `references/methodology-and-rules.md`.
- **Complete `blockiya-core` v2.1 utility implementations, signatures, usage patterns, comparison tables, and Draft notes**: Read `references/blockiya-core-reference.md`.
- **UML Notation System v2.0 (ASCII & Mermaid class diagrams, visibility/flow/relationship markers, BillingOverview diagram, and 17-step TodoBlock sequence flow)**: Read `references/uml-notation-and-diagrams.md`.
- **Full annotated TypeScript/React reference implementation (`UserProfileBlockSmart`, `ProfileDisplayDumb`, `ProfileEditFormDumb`, `UserAvatarAdapter`, pattern tags #1/#2/#3/#8/#11)**: Read `references/annotated-code-example.md`.
- **Same `UserProfileBlock` scenario fully implemented in other frameworks — `examples/react.md` (canonical), `examples/vue.md` (composables), `examples/maui.md` (MVVM/C#), each primitives → behavioral → adapter → views → Blockiya → Page, with `examples/README.md` holding the shared scenario spec and cross-framework invariants checklist**: Read when porting Blockiya to a non-React stack or proving the mapping in the methodology.
- **Tool-agnostic `blockiya-core` scaffolding guidelines (manifest, assembly invariants, verification checklist, drift policy)**: Read `references/scaffold-blockiya-core.md`.
- **Visual sequence diagram reference image (`TodoBlock` edit/save flow)**: Inspect or bundle `assets/todo-edit-sequence-diagram.png`; canonical text source `assets/todo-edit-sequence-diagram.mmd` (re-render to any raster via a Mermaid-compatible renderer, e.g. kroki.io or mermaid-cli — tool choice is illustrative).
- **Starter Mermaid templates**: Copy from `assets/mermaid-class-diagram-template.mmd` or `assets/billing-overview-diagram.mmd`.

## Core Workflows

### Workflow 1: Design & Implement a New Blockiya

1. **Classify the stereotype and scope**: Decide whether the unit is `<<Atomic>>`, `<<Compound>>`, or `<<Feature>>`, and place it in vertical feature slice `src/features/<feature>/blockiyas/<Name>Block/`.
2. **Place state using the 3-question rule** (see `references/methodology-and-rules.md` for the full State Complexity Decision Table):
   - Used by only one component? -> Local `useState` (or `useToggle`/`useDerivedState`).
   - Synced with a server? -> Server-state hook ([React Query], [SWR], or equivalent) in `features/<feature>/queries/`.
   - Shared across unrelated features? -> Global store (e.g., Zustand) outside `features/`.
   - Shared only within one feature or multi-field form? -> Scoped `<<Context>>` provided by parent Blockiya.
   - Survives refresh (filters/pagination)? -> URL search params via router.
3. **Define typed contracts**:
   - Declare raw domain type(s) and derived view type(s) (`Display*`).
   - Write a module-scope deriver function (`deriveDisplay*(raw)`).
   - Keep inputs to 3-7 props and outputs to 3-7 `*Intent` callbacks.
4. **Scaffold `blockiya-core` if missing**: Follow `references/scaffold-blockiya-core.md` (tool-agnostic assembly guidelines — manifest, invariants, verification). The bundled `python scripts/scaffold_blockiya_core.py <target-dir>` is one optional convenience if Python is present; otherwise emit the 15 files directly per the guide.
5. **Implement boundaries cleanly**:
   - Put third-party wrappers in `src/adapters/<lib>/` (`*Adapter`).
   - Put private stateless presentational children in `<Name>Block/children/` (use Controlled Components for inputs; use Context Object + Compound Components for multi-field forms).
   - Wire async actions through `useIntent` (Strict Blockiya) and pass derived props via `useDerive` / `useDerivedState`.
   - Render exclusively with `<<Primitive>>`, `<<Behavioral>>`, `<<Adapter>>`, and `<<Utility>>` components—zero CSS/className/style.
6. **Mount in `<<Page>>`**: Connect the Blockiya's `*Intent` callbacks at the route/page level to handle navigation, confirmation modals, toasts, or sibling refreshes.
7. **Audit before finishing**: Run `python scripts/audit_blockiya.py <path-to-block.tsx> --strict` (omit `--strict` for base Blockiya) and resolve all reported violations.

### Workflow 2: Refactor an Existing Component into Blockiya

1. Read `references/methodology-and-rules.md` (especially "How a Blockiya grows" and "Battle-tested situations") and `references/annotated-code-example.md`.
2. Audit the existing component for responsibilities:
   - Extract direct `fetch`/`invoke` calls into `queries/use*.ts`.
   - Extract third-party widget setup/theming/events/teardown into `adapters/<tool>/*Adapter.tsx`.
   - Replace inline styles / `className` with typed token primitives (`Box`, `Flex`, `Text`, `Button`).
   - Move confirmation dialogs, navigation, and toast triggers up to the parent `<<Page>>` via `*Intent` props.
   - Convert hook-driven dropdowns/modals leaking `isOpen` into compound `<<Behavioral>>` primitives.
   - Split raw-to-display transformations into module-scope derivers + `useDerive` (or `useDerivedState` for editable drafts).
   - Extract private presentational views (`children/`) if stateless, or child `*Block` components if they carry independent domain state/queries or are reused.
   - If props exceed 7 or two domains coexist, split into a `<<Compound>>` parent + `<<Atomic>>` child Blockiyas.
3. Run `python scripts/audit_blockiya.py <refactored-file.tsx> --strict` to verify compliance.

### Workflow 3: Generate Blockiya UML Diagrams

1. Read `references/uml-notation-and-diagrams.md` for the exact symbol tables, 4-section block structure, callback `▼`/`▲` distinction, and Mermaid configuration.
2. For architecture / structural diagrams, start from `assets/mermaid-class-diagram-template.mmd` (`look: handDrawn`, `layout: elk`) or ASCII block format, enforcing:
   - Stereotypes: `<<Page>>`, `<<Feature>>`, `<<Compound>>`, `<<Atomic>>`, `<<Primitive>>`, `<<Behavioral>>`, `<<Adapter>>`, `<<Context>>`, `<<Hook/Query>>`, `<<Utility>>`.
   - Contextual visibility: `●` Public, `○` Private, `◆` Internal.
   - Flow direction: `▼` Props/data inflow (including received callback props), `▲` Events/intents outflow (invoked callbacks).
   - Relationships: `*--` Composition (owns), `..>` Dependency (uses), `⊙--` Context provision, `··>` Context consumption.
   - Naming: `*Block`, `*Adapter`, host-language types on props (TypeScript, C#, etc.), `*Intent()` suffix on events.
3. For runtime interaction flows (intent lifecycle, `useDerivedState` resets, `useIntent` loading/disable cycles), mirror the 17-step `TodoBlock` sequence pattern in `references/uml-notation-and-diagrams.md` (visual reference: `assets/todo-edit-sequence-diagram.png`).

### Workflow 4: Audit & Review Code for Blockiya Compliance

1. Run `python scripts/audit_blockiya.py <file-or-dir> --strict` for deterministic static checks.
2. Perform architectural review against `references/methodology-and-rules.md`:
   - Check growth signals: >7 props/intents, merged domains, `<<Atomic>>` accumulating children, private child reused by two Blockiyas.
   - Check Strict Blockiya rules: no manual `isLoading`/`error` pairs, no inline derivation/`useMemo`, explicit `<If>`/`<Maybe>`/`<For>`/`<Repeat>`/`<Compose>`, barrel-only imports from the utilities package (recommended name `blockiya-core`; pass the actual name to the audit via `--core-name`).
   - Check intent purity: Blockiya fires intent and stops; no confirmation/navigation/side-effect decisions leaked downward.
   - Check behavioral primitive encapsulation: zero `isOpen` state leaked into Blockiyas or views.

## Bundled Scripts

- `scripts/scaffold_blockiya_core.py <output_dir>`: Optional convenience that generates the complete v2.1.0 `blockiya-core/` directory (`structural/`, `intents/`, `derivation/`, `hooks/`, `index.ts`) with exact typed implementations. The language-agnostic procedure lives in `references/scaffold-blockiya-core.md` — use it when Python isn't available or the project prefers its own tooling.
- `scripts/audit_blockiya.py <target_path> [--strict] [--core-name NAME]`: Runs automated static checks on `.ts`/`.tsx` Blockiya files for styling leaks, direct API calls, prop-count ceiling (>7), `isOpen` leaks, direct subpath imports, and (with `--strict`) inline `useMemo`, manual `isLoading`/`error` state, and raw `.map()`/`&&` rendering. `--core-name` sets the project's utilities-package name (defaults to the recommended `blockiya-core`).
