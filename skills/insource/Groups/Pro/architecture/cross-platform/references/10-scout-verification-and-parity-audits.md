# 10 — Scout Verification & Parity Audits

> The Dual-Scout verification methodology for cross-platform applications: combining empirical surface scanning (AST/Regex) with structural abstraction auditing (Platform Parity & Completeness).

---

## 1. The Dual-Scout Doctrine

To certify that a cross-platform codebase is free of platform contamination and feature gaps, verification must execute through two orthogonal scouts:

```
                            VERIFICATION RUN
                                   │
         ┌─────────────────────────┴─────────────────────────┐
         ▼                                                   ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────┐
│     SCOUT 1: EMPIRICAL SCAN     │ │   SCOUT 2: STRUCTURAL AUDIT     │
│  Detects platform leakage, raw  │ │  Ensures feature parity across  │
│  conditionals, and idiom checks │ │  all targets; verifies no       │
│  in shared code (Regex / AST).  │ │  platform is left dangling.     │
└─────────────────────────────────┘ └─────────────────────────────────┘
```

---

## 2. Scout 1: Empirical Surface Scan (Leakage Detection)

Scout 1 sweeps shared directories to ensure that platform-specific APIs and conditional logic have not leaked into shared modules.

### Targeted Prohibited Tokens
1. **Preprocessor Directives:** `#if ANDROID`, `#if IOS`, `#if WINDOWS`, `#ifdef` inside shared code.
2. **Runtime OS Introspection in JSX/Views:** `Platform.OS === 'android'`, `Platform.isIOS`, `kIsWeb`, `OperatingSystem.IsWindows()`.
3. **Idiom Bifurcation in Views:** `DeviceInfo.Idiom == Desktop`, `DeviceInfo.Idiom == Phone`.
4. **Hardware Module Inlining:** Direct imports of `react-native-keychain`, `android.hardware.*`, `Windows.Devices.*` in shared view models.

---

## 3. Scout 2: Structural Abstraction Audit (Parity & Completeness)

Scout 2 audits the architecture to guarantee that declared platform abstractions are completely satisfied across every supported target.

### The Platform Parity Matrix Test
If a feature declares a contract `IPlatformShareSheet`, Scout 2 inspects the build matrix to verify that every active platform target has an implementation registered:

```
┌───────────────────────────┬───────────┬───────┬─────────┬─────────┐
│ Abstraction Contract      │ Android   │ iOS   │ Windows │ macOS   │
├───────────────────────────┼───────────┼───────┼─────────┼─────────┤
│ IPlatformShareSheet       │ ✅ Impl   │ ✅Impl│ ✅ Impl │ ✅ Impl │
│ IBiometricAuthenticator   │ ✅ Impl   │ ✅Impl│ ⚠️ Token│ ⚠️ Token│  <-- Handled via PlatformCapability<T>
│ IFilePickerGateway        │ ✅ Impl   │ ✅Impl│ ✅ Impl │ ❌ MISS │  <-- CRITICAL AUDIT FAILURE!
└───────────────────────────┴───────────┴───────┴─────────┴─────────┘
```

### Audit Failure Triggers:
1. **Dangling Implementation:** Contract declared, but one platform target throws an unhandled `NotImplementedException` or leaves an empty stub without a declared `PlatformCapability<T>` fallback.
2. **Missing Build Exclusions:** A platform-specific file compiles into an incompatible platform bundle.
3. **Single-Axis Law Violation:** A file name compounds two orthogonal axes (e.g. `Payment.android.playstore.ts`).
