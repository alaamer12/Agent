# Library Decision — the skill's only judgment

The workflow has exactly one open decision: when a project has **no styling system at all**, build
the layer on framework-native tokens, adopt a library, or pilot a hybrid. Everything else in
`SKILL.md` is fixed procedure.

Standing note: the options below are illustrative, not exhaustive or mandatory. A hybrid or an
unlisted library is always acceptable if the evidence supports it; a stack-specific answer is only an
example, never a mandate.

## Step 0 — Is there an incumbent? (before the five tests)

| What the project already uses | What styleup does |
|---|---|
| A professional styling library (e.g. Emotion, styled-components, Tamagui, Tailwind/UnoCSS theme config, a component/design-system suite) | **No library question.** Extend that library's token/theme model, replace arbitrary values with its tokens, enforce its usage. Replacing the stack is a separate project. |
| A framework-native token mechanism (CSS custom properties, MAUI/WinUI resources, Compose theme, RN theme context, SwiftUI environment) | **No library question.** Centralize the remaining values into that mechanism. |
| Plain styling only (raw CSS/SCSS/StyleSheet/inline styles/loose constants) | Run the five tests below. |
| An incumbent that is unmaintained or incompatible | Record an upgrade candidate/follow-up; do not migrate the stack during this run. |

Asking “should we adopt a library?” when the project already uses one is a category error: the
existing library *is* the styling system, and the work is to use it properly. A library that is
present but unused is plain styling with dead weight — test the actual usage, not the dependency list.

## Five tests

| # | Test | Evidence to collect | Fails ⇒ |
|---|---|---|---|
| 1 | **Necessity** | What reactive-token capability does the platform lack today? Name the gap, not a preference | Native |
| 2 | **Fit** | Packaging model, runtime loading, crash-safety rules, RTL, offline, build-time checks, pinned framework version | Native, or hybrid for one isolated area |
| 3 | **Health** | Release cadence, contributor count / bus factor, adoption, open-issue responsiveness, license, framework-version support | Native unless the surface is small and vendorable |
| 4 | **Interop** | Coexistence with existing components/styles, incremental adoption, escape hatch for unstyled cases | Native or hybrid |
| 5 | **Exit** | Removal path, vendoring option, migration cost back to native | Do not adopt without a rollback path |

All five pass ⇒ adopt, but **pilot one isolated area first** and keep the rollback. Necessity failing
is decisive: do not add a second source of truth to solve a problem the platform already solves.

## Where to get the evidence

- Package registry: installed version, release dates, download counts, license, supported runtimes.
- Source repository: contributors, last push, open issues, dependent projects.
- Documentation **for the installed major**: the tool's model and constraints, not the version in a blog.
- A spike in the real build: packaging quirks, asset/resource loading, RTL, and the platform where the
  project actually ships. Documentation that does not cover your deployment model is not evidence.

## Markup-only vs token-centralizing libraries

Two different things often get conflated:

- **Authoring-only** libraries change *where* styles are written — fluent builders, JSX helpers, thin
  wrappers. Consumers still carry values unless a token layer already exists. They are an ergonomics
  choice, not a styling-system cure.
- **Token-centralizing** libraries own a token/theme model (typed theme providers, SSR-aware CSS-in-JS
  themes, design-system packages). They can pass Necessity — but only when the platform truly lacks a
  reactive-token mechanism, and only if Fit/Interop/Exit also pass.

Evaluate the category before the brand name.

## Case notes (illustrative)

**markup builder, mobile UI (e.g. FmgLib.MauiMarkup, 2026).** v10.3.0, active releases, MIT, roughly
one contributor and ~20K downloads, no popular dependents. Model: fluent `Style<T>`, theme/platform/
idiom builders, dynamic-resource builders, XAML coexistence. Verdict on a hardcoded-style problem:
**not the cure** — the platform already offers reactive resources; value is authoring ergonomics;
bus factor and the desktop packaging path were unproven. Eligible only for an isolated ergonomics
pilot.

**CSS-in-JS theme provider, web (e.g. styled-components, Emotion, Tamagui — illustrative).** When one
is **already adopted**, Step 0 closes the question: styleup works inside its theme model. When the
project is on plain CSS, these do centralize tokens (typed theme, SSR support), so Necessity can pass
where custom properties are insufficient (typed contracts, runtime interpolation, SSR theming); on a
plain custom-property-capable stack they usually lose on Necessity/Fit (runtime cost, build coupling),
and that is a finding, not a defect.

## Native mechanisms (illustrative)

- [CSS custom properties + `prefers-color-scheme` / `data-theme` attributes; Tailwind/CSS Modules consuming vars]
- [.NET MAUI / WinUI resource dictionaries + dynamic resources]
- [Jetpack Compose theme + composition locals]
- [React Native tokens module + theme context; `StyleSheet` imports tokens]
- [SwiftUI environment values / asset catalogs]
- [Canvas/SVG/chart drawing: read the same tokens via typed accessors or computed styles]

## Decision record template

```text
STYLEUP DECISION
Scope:              <entire project | path>
Verdict:            native | library:<name>@<version> | hybrid
Necessity:          <the capability gap, or "none — platform covers it">
Fit:                <constraints checked + spike result>
Health:             <version, date, contributors, adoption, license>
Interop:            <coexistence, incremental adoption, escape hatch>
Exit:               <rollback/vendor path>
Trade-offs accepted:<what is given up>
Revisit trigger:    <what future change would reopen the decision>
```

## When to stop

A genuinely unresolvable blocker — license, unsupported target, unsafe runtime behavior — is an Open
Question. Surface it with the evidence and stop that branch; do not guess and do not ask the user to
choose between unverified options.
