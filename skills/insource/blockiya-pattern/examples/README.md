# Blockiya Across Frameworks — Full Worked Examples

One identical scenario, implemented end to end in each framework, so the mapping from [methodology-and-rules.md § "Blockiya beyond React"](../references/methodology-and-rules.md#blockiya-beyond-react) becomes real code instead of a table row.

## The shared scenario: `UserProfileBlock`

A profile screen fragment that:

1. Fetches a raw `User` through the data layer (never inline).
2. Owns `isEditing` and an editable `draft` seeded from server data.
3. Derives `DisplayUser` before passing anything to presentational children (Pattern #11).
4. Renders a display view and an edit form as stateless children; the form uses a context/composable bundle (Patterns #1 + #8) with controlled fields (Pattern #3).
5. Wraps a third-party avatar library in a `<<Behavioral>>`-friendly `<<Adapter>>` (token + event + lifecycle translation).
6. Exposes a `<<Behavioral>>` compound `Dropdown` — `isOpen` never leaks.
7. Fires `onEditIntent` / `onDeleteIntent` / `onSaveIntent` upward and **stops** — the Page decides on confirmation, navigation, toasts.
8. Enforces zero styling in the Blockiya: all visual output through primitives.

Every file below shows **primitives → behavioral → adapter → dumb views → Blockiya → Page**, mirroring `references/annotated-code-example.md`.

## The set

| File | Framework | Paradigm family | Key translation |
| --- | --- | --- | --- |
| [react.md](react.md) | React + TypeScript (canonical) | OOP-flavoured component model + hooks | Reference implementation |
| [vue.md](vue.md) | Vue 3 + TypeScript | Reactive props/emits, `<script setup>` composables | Hooks → composables; provider → `provide/inject` |
| [maui.md](maui.md) | .NET MAUI + C# | Compiled MVVM, XAML binding | Component → `ContentView`; intent → event; tokens → dynamic resources |

Deliberately different paradigm families (per polyglot rule 4), all three complete — not sketches.

## Cross-framework invariants checklist

After reading any file, verify the same contract held:

- [ ] Blockiya talks to data **only** through its data layer (hook / composable / service-backed command).
- [ ] Children receive a **derived** view type (`DisplayUser`), never the raw model.
- [ ] Async handlers carry lifecycle state owned by a single named utility (intent runner), not hand-rolled per handler.
- [ ] `Dropdown`/modal interaction state is **invisible** outside the behavioral primitive.
- [ ] The third-party avatar is unknown to the Blockiya — only the adapter knows its name.
- [ ] After save/delete the Blockiya **stops**; the page shows the confirm, toast, or navigation.
- [ ] 3–7 props in, 3–7 intents out.
- [ ] No raw CSS/style markup inside the Blockiya body — primitives only.

If a port breaks any line, the port changed the pattern — fix the code, not the checklist.

> The examples import from `@/shared/blockiya-core` — the author's recommended package name. Any name is valid as long as the single-barrel contract holds (the audit's `--core-name` covers the rest).
