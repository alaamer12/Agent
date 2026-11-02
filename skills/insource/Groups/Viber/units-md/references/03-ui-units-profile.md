# Profile: UI builder units

Carried over from `like-a-pro`'s old system-creator "Mode B", now folded into units-md. A specialization of the
units index for the presentation layer: reusable visual components, adaptive concepts,
design-system primitives, and builder functions. Everything in
[`01-the-file.md`](01-the-file.md) still applies — same entry form, same ids, same required fields, same linter.
This file only adds what is UI-specific: what qualifies, how to group, and which statuses mean what here.

> **Illustrative, not exhaustive.** The framework names below are examples. The criteria are structural: reusable,
> named, pointed at a path. Apply them to whatever UI stack the project actually uses ([React], [Next], [Vue],
> [Svelte], [React Native], [Flutter], [SwiftUI], [Compose], [.NET MAUI]/[WPF]/[Avalonia], [Angular], Web
> Components, server-rendered templates, vanilla DOM, or anything else).

## What qualifies

A unit here is any reusable, named UI building block: a base/primitive component, a composite/block component, an
adaptive/platform concept, a design-system primitive (token set, theme, effect), or a **builder function**.

**Builder function** does not mean the GoF Builder pattern (`Builder.SetFoo().Build()`). It means: any function,
factory, layout composer, render helper, or markup-producing utility that is **reusable across call sites**,
rather than a private single-use helper tied to one screen.

| Stack family | Typical shapes |
|---|---|
| [React] / [Next] / [Vue] / [Svelte] | layout factories and compound view builders (`createModalShell(...)`), table/column builders, hooks that assemble a component, presentation formatters used across features (`formatCurrencyBadge(...)`) |
| [Flutter] / [Dart] | widget-building helpers (`buildActionChip(...)`, `createStatusBadge(...)`), adaptive scaffolds |
| [SwiftUI] | `@ViewBuilder` functions, `ViewModifier`s that encode a house style |
| [Compose] / [Android] | reusable composable factories, slot APIs (`AppScaffold(...)`, `renderProjectItem(...)`) |
| [.NET] (MAUI, WPF, Avalonia) | layout factories (`NavigationControl.Build(rail, content)`), platform selectors (`PlatformSelect.For<T>(...)`) |
| [Web] / vanilla | DOM/HTML builders, template-tag functions, custom element factories |

### Include

- Reusable views, controls, widgets, containers, shells, dialogs, form groups, list cards.
- Adaptive/platform concept mappers that swap layout or interaction paradigms under one name.
- Composition and layout builders, view composers, slot/template constructors.
- Presentation formatters and normalizers used by more than one feature.
- Design-system primitives: tokens, themes, typography scales, motion/effect utilities, skeletons and shimmer
  loaders, debouncers and similar behavior helpers that carry a house convention.
- System and shell integrations that are reused: navigation controllers, tray or menu-bar surfaces, modal hosts,
  notification presenters.

### Exclude

- A private helper used by one screen or one component: it is part of that unit, not a unit.
- Raw DTOs and backend entities with no presentation or layout behavior.
- A framework built-in used bare, with no project convention encapsulated (`<input>` is not a unit; the project's
  `TextField` with its validation and styling rules is).
- Generated component wrappers, vendored UI kit exports — they are dependencies, not units. Say the kit is used
  and skip the list.

## Grouping

Use the project's own names. A taxonomy that has worked when the project has none:

| Group | Holds |
|---|---|
| Base / primitive components | buttons, inputs, cards, badges, toggles, typography |
| Composite / block components | compound views, headers, form groups, dialogs, screen layouts |
| Adaptive / platform concepts | responsive and multi-device abstractions |
| Design system and primitives | tokens, themes, motion, effects, skeleton loaders |
| Builder functions and presentation utilities | layout constructors, renderers, factories, formatters |
| System and shell integrations | app shell, navigation, tray/menu bar, modal and notification hosts |

Groups are the `##` headings; each unit is still one `### U-###: Name` entry. Above the entries, a summary table
(`| Unit | Where | Status |`) is welcome for scanning — it is a view, not the record.

## Statuses in this profile

The vocabulary stays the same; only the reading is UI-specific:

| Status | Means here |
|---|---|
| `active` | implemented, wired, and used by real screens (the profile's former "Implemented") |
| `pending` | the interface or stub is declared, no real implementation yet (the former "Scaffold") — record in **Notes** what would make it `active` |
| `experimental` | built and used behind one surface, contract not settled |
| `deprecated` | replaced by another unit; name the replacement in **Reuse instead of** |
| `unknown` | listed by an earlier pass, not re-checked since |

If a project's existing `UNITS.md` used `Scaffold`/`Implemented` verbatim, keep the words in **Notes** and set the
linter-valid status — do not fork the vocabulary, because the whole point of the index is that it stays
machine-checkable.

## Fields worth filling in here

- **Where:** the directory pattern when the group lives in one place (`src/ui/blocks/`), or the file when the unit
  is a single component.
- **Depends on:** the units this one composes — a card built on a shell depends on that shell. This is what makes
  a design-system change answerable.
- **Reuse instead of:** the ad-hoc markup this unit replaced (the row that stops a fifth button variant).
- **Notes:** states, variants, accessibility contract, "do not use outside the shell", theme-key assumptions.

Run the same check as any units file:

```bash
python <units-md-skill-dir>/scripts/units_lint.py docs/UNITS.md --strict
```
