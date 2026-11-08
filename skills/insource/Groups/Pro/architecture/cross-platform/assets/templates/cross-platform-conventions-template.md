# Cross-Platform Architecture Steering Conventions

> Master steering conventions for `<docs>/cross-platform-architecture.md` (or `<docs>/cross-platform/`). Defines the project's immutable rules for UI mechanics, decoupling, and isolation.

---

## 1. Core Architectural Laws

1. **Zero Conditional Compilations in Shared Modules:**
   - `#if ANDROID`, `#if IOS`, `#if WINDOWS`, and runtime `Platform.OS ===` checks are **forbidden** inside `shared/`, `commonMain/`, or `features/`.
   - All platform-divergent code lives inside toolchain-resolved extension files (`.android.ts`, `.ios.ts`) or dedicated platform folders (`Platforms/`, `androidMain/`).

2. **Zero Form-Factor Idiom Branching in Views:**
   - Direct inspection of `DeviceInfo.Idiom == Desktop` or device categories inside UI templates is prohibited.
   - Form-factor divergence is handled exclusively through **View Barrels** and container **Breakpoint Layout Dispatching**.

3. **Neutral Architectural Naming (PlatformConcepts):**
   - Universal UI roles must be named for their abstract function, never after the visual widget of a single operating system.
   - Example: Name the top-level container `NavigationShell`, not `BottomTabBar` or `DesktopSidebar`.

4. **The Single-Axis Filename Law:**
   - A filename may express at most ONE axis of variation. Compounding multiple dimensions into a single filename (e.g. `Payment.android.playstore.eu.ts`) is strictly banned.

5. **Capability vs. Policy Separation:**
   - Hardware and OS capabilities (`PlatformCapability<T>`) never know about or inspect business subscriptions, regions, or distribution channels.
   - Business policies consume abstract capability tokens; capabilities never consume policies.

6. **UNITS.md Reusability Mandate:**
   - Before authoring any new visual control or component, the catalog in `UNITS.md` must be inspected. Parallel reinvention is a defect.

---

## 2. Directory & Namespace Structure

```
src/
├── app/                  # Application bootstrap, routing, and NavigationShell
├── features/             # Business domains composed via View Barrels
│   └── [feature]/
│       ├── state/        # Agnostic state machines, presenters, view models
│       └── views/        # View Barrels delegating to renditions
├── shared/
│   ├── capabilities/     # PlatformCapability contracts & native implementations
│   ├── contracts/        # Abstract service interfaces
│   └── ui/
│       ├── primitives/   # Tier 1 Core Primitives
│       ├── containers/   # Tier 2 Base Units
│       └── responsive/   # BreakpointContainer & layout dispatchers
└── platforms/            # Native toolchain bindings & OS entry points
```
