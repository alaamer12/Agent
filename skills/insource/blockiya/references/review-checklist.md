# Blockiya Review Checklist

Use this checklist when reviewing existing code, generating new Blockiyas, or refactoring toward the pattern.

## Identity

- [ ] Component that owns domain state or data fetching is treated as a Blockiya (or extracted into one).
- [ ] Stereotype is declared and matches reality (`<<Atomic>>` vs `<<Compound>>` vs `<<Feature>>`).
- [ ] Naming follows conventions (`…Block`, `…Adapter`, `on…Intent`).

## Zero styling

- [ ] No `class bindings, style objects, utility classes`, `class bindings, style objects, utility classes`, class bindings, style objects, utility classes utilities, or CSS modules inside the Blockiya body.
- [ ] All visual output goes through primitives or adapters.

## Data & state

- [ ] No direct `fetch` / `invoke` / API client calls — only hooks from `queries/`.
- [ ] Domain state lives in the Blockiya (or via Strict utilities).
- [ ] Server state uses data layer (queries/composables/stores) (or equivalent) via hooks.
- [ ] Shared feature state uses Context Object, not a premature global store.

## Derivation

- [ ] Raw API / domain shapes never reach presentational children.
- [ ] Derivers are named functions at module scope.
- [ ] Under Strict mode: every derivation goes through `derive utility` or `derive utilitydState`.

## Intents

- [ ] User actions are translated into upward intents.
- [ ] After firing an intent the Blockiya stops (no confirm, navigate, toast, sibling refresh).
- [ ] Under Strict mode: every async handler uses `intent utility`.
- [ ] Prop / intent count stays in the 3–7 range; otherwise extract.

## Children & composition

- [ ] Presentational children receive only derived props and fire intents upward.
- [ ] Presentational children own zero domain state.
- [ ] Behavioral primitives use compound-component API; callers never manage `isOpen`.
- [ ] Adapters perform only token translation, event translation, and lifecycle management.
- [ ] Adapters live in top-level `adapters/` and own no domain state.
- [ ] Imperative primitives (toasts) are not owned by Blockiyas.

## Structure & visibility

- [ ] Blockiya lives under `features/<feature>/blockiyas/<Name>Block/`.
- [ ] Private children live under `children/` (`○`).
- [ ] Public surface is correctly exported (`●`).
- [ ] No cross-feature private imports.
- [ ] Queries live under the feature's `queries/` folder.

## Strict mode extras

- [ ] `If` / `Maybe` / `For` / `Repeat` / `Compose` used instead of inline conditionals and `.map()`.
- [ ] No manual `isLoading` / `error` `useState` pairs.
- [ ] No inline `useMemo` for derivation.

## Diagram / documentation

- [ ] Stereotype + visibility markers present.
- [ ] ▼ props and ▲ events both shown for callback-bearing blocks.
- [ ] Relationships use correct symbols (`*--` vs `..>` vs context arrows).

## Growth & health

- [ ] Props or intents > 7 → extraction planned.
- [ ] Multiple domains in one Blockiya → split planned.
- [ ] Stereotype still accurate.
- [ ] Private child reused by a second consumer → promotion planned.

## Quick rejection phrases

- "This Blockiya is making a UX decision that belongs to the Page."
- "Raw shape is leaking to a presentational child — derive first."
- "Styling belongs in a primitive, not here."
- "Interaction state must stay inside the behavioral primitive."
- "Adapter is carrying domain logic — move it up."
- "Ceiling breached — extract a child Blockiya."
- "Visibility is wrong — this should be private under children/."
