# UI Units — Taxonomy & Format Reference

Detailed field reference for `UNITS.md`, the catalog produced by
**system-creator**'s Units mode. See `SKILL.md` for when and how to invoke
this mode. Everything below is framework-agnostic: apply it to whatever UI
stack the target application actually uses (React, Next.js, Vue, Svelte, React
Native, Flutter, Swift/SwiftUI, Kotlin/Compose, .NET MAUI/WPF, Angular, Web
Components, vanilla UI, or anything else).

---

## What Qualifies as a "Unit"?

A **unit** is any reusable, named UI building block: a base/primitive
component, a composite/block component, an adaptive/platform concept, a
design-system primitive (token, theme, effect), or a **builder function**.

### What Qualifies as a "Builder Function"?

A Builder Function does **NOT** need to follow the classical GoF "Builder
pattern" (`Builder.SetFoo().Build()`). Instead:

> **Definition:** Any function, factory method, layout composer, render
> helper, or markup-producing utility that is **reusable or designed to be
> reusable across multiple call sites**, rather than a private single-use
> helper tied to one screen or component.

### Universal Examples Across Frameworks & Languages

- **React / Next.js / Vue / Svelte:**
  - Layout factory functions or compound view builders (e.g.,
    `createModalShell(...)`, `renderFilterBar(...)`).
  - Reusable hook-based component builders or render props (e.g.,
    `useDialogBuilder()`, `createTableColumnBuilder()`).
  - Formatting & presentation builders used across features (e.g.,
    `formatCurrencyBadge()`, `buildAvatarCluster()`).
- **Flutter / Dart:**
  - Widget-building helper functions (e.g., `buildActionChip(...)`,
    `buildAdaptiveScaffold(...)`, `createStatusBadge(...)`).
- **Swift / SwiftUI:**
  - ViewBuilder functions and ViewModifiers (e.g.,
    `@ViewBuilder func makeCardHeader(...)`, `customToolbarBuilder(...)`).
- **Kotlin / Jetpack Compose:**
  - Reusable composable factory functions and slot API builders (e.g.,
    `AppScaffold(...)`, `renderProjectItem(...)`).
- **C# / .NET (MAUI, WPF, Avalonia):**
  - Layout factory functions (e.g., `NavigationControl.Build(rail, content)`,
    `CardFactory.Create(...)`).
  - Platform/capability selectors (e.g., `PlatformSelect.For<T>(...)`).
- **Web / Vanilla / Any:**
  - DOM/HTML builders, template tag functions, web component factories.

### Inclusion Criteria

- **UI Component Units:** Any reusable view, control, widget, or container.
- **Adaptive / Concept Mappers:** Resolvers that swap platform or viewport
  paradigms under one conventional name.
- **Composition / Builder Functions:**
  - Layout factory functions and view composers.
  - Reusable presentation builders and slot/template constructors.
  - Formatter & normalization builders producing formatted presentation
    artifacts across multiple features.
- **Design System Primitives:** Reusable behaviors, layout splitters,
  radar/canvas painters, debouncers, skeleton/shimmer loaders.

### Exclusion Criteria (do NOT add to `UNITS.md`)

- Private, single-usage helper methods inside a specific page, screen, or
  single component.
- Raw data transfer objects (DTOs) / backend entities with zero
  presentation, layout, or builder behavior.
- Bare standard framework built-ins used without custom encapsulation or
  project conventions.

---

## Standard `UNITS.md` Structure & Format

```markdown
# Units — {ApplicationName}

This document catalogs the application's **units** — the named, reusable building blocks and builder functions that make up the UI and presentation layer. Each unit has one conventional name used consistently across the codebase.

Units are grouped by architectural category:
- **Base Components** — primitive inputs, buttons, cards, toggles, badges, labels.
- **Composite / Block Components** — high-level composite widgets, cards, shells, and screen layouts.
- **Adaptive / Platform Concepts** — components or mappers that adapt behavior/layout across platforms, devices, or viewports.
- **Design System & Primitives** — tokens, themes, visual behaviors, skeletons, animations, and canvas/effect helpers.
- **Builder Functions & Presentation Utilities** — reusable layout builders, render utilities, and presentation formatters.
- **System & Shell Integrations** — application shell, navigation controllers, system tray/menu bar, dialog/modal hosts.

Status legend:
- `Scaffold` = stub/interface declared, no real implementation yet.
- `Implemented` = fully functioning, wired, tested unit.

---

## <Category / Mechanism Name>

Location: `<directory or path pattern>`

| Unit | Base Type / Implementation | Purpose & Mechanism | Status |
|---|---|---|---|
| `<UnitName>` | `<BaseType or Signature>` | `<Description of purpose, design rationale, and builder behavior>` | `Implemented` / `Scaffold` |
```

### Category Taxonomy (adapt to the detected architecture)

- **Base/Primitive Components:** Reusable buttons, inputs, cards, badges,
  toggles, typography.
- **Composite/Block Components:** Reusable compound views, headers, list
  cards, form groups, dialogs.
- **Platform/Device Adaptations:** Multi-platform/multi-device concept
  abstractions (e.g., responsive layouts, desktop vs. mobile navigation
  paradigms).
- **Design System & Primitives:** Shared tokens, themes, colors, typography
  scales, animation/motion utilities, effects.
- **Reusable Builder Functions & Utilities:** Layout constructors,
  renderers, factory helpers, formatting/presentation builders.
- **System & Shell Integrations:** Shell navigation, tray/menu bar,
  windowing, modals, notification presenters.
