# Utilities: The Select Helper & Capability Wrapper, Across Ecosystems

The point of this file is **not** to tell you which of these to copy. It's to show that "compile-time/build-time value selection" and "explicit optional-capability wrapping" are the same two concepts everywhere, wearing different clothes. Recognize which shape a project already has (even a built-in language/framework feature counts!) before inventing a new one, and if none exists, pick the idiom that fits the ecosystem — don't port a C#-flavored helper into a Dart or Kotlin codebase verbatim.

## Table of contents
1. The "select" concept, per ecosystem
2. The "capability" concept, per ecosystem
3. The file-suffix / conditional-import concept, per ecosystem (this is Pillar 1's file-separation, expressed natively)
4. Choosing what to build when nothing exists yet

---

## 1. The "select" concept, per ecosystem

The shape is always: **given one value/factory per platform (or family), resolve exactly one, as early as possible, with zero runtime branching cost at the call site.**

**React Native / TypeScript** — the framework ships this natively; use it before inventing your own:
```ts
// theme.ts
import { Platform } from 'react-native';

// Platform.select IS the select-helper concept, built into the framework.
export const cardElevation = Platform.select({
  ios: 0,              // iOS uses shadow, not elevation
  android: 4,           // Android's native elevation unit
  default: 0,
});
```

**.NET / C# (e.g. MAUI)** — no built-in equivalent, so the project defines its own generic helper:
```csharp
// PlatformSelect.cs — the ONE file allowed to contain the real platform check
public static class PlatformSelect
{
    public static T For<T>(T? windows = default, T? android = default,
                            T? ios = default, T? @default = default)
    {
#if WINDOWS
        return windows ?? @default!;
#elif ANDROID
        return android ?? @default!;
#elif IOS
        return ios ?? @default!;
#else
        return @default!;
#endif
    }
}

// call site, anywhere else in the codebase — no conditional in sight:
double cardElevation = PlatformSelect.For(windows: 2.0, android: 4.0, ios: 0.0, @default: 0.0);
```

**Kotlin Multiplatform** — the *language itself* provides the select mechanism via `expect`/`actual`; you don't write an if/else at all:
```kotlin
// commonMain/CardStyle.kt — the shared shell declares the shape, no implementation
expect fun cardElevation(): Float

// androidMain/CardStyle.android.kt
actual fun cardElevation(): Float = 4f

// iosMain/CardStyle.ios.kt
actual fun cardElevation(): Float = 0f
```
This *is* the select concept — resolved by the compiler picking whichever `actual` matches the current source set, not by a runtime branch.

**Flutter / Dart** — no single built-in helper, but the common project convention is a small top-level function:
```dart
// platform_select.dart
T platformSelect<T>({T? ios, T? android, required T fallback}) {
  if (Platform.isIOS && ios != null) return ios;
  if (Platform.isAndroid && android != null) return android;
  return fallback;
}

// call site:
final cardElevation = platformSelect<double>(ios: 0, android: 4, fallback: 0);
```

**Swift (SwiftUI cross-platform: iOS + macOS + visionOS, etc.)**:
```swift
// PlatformSelect.swift
enum PlatformSelect {
    static func value<T>(ios: T? = nil, macOS: T? = nil, `default`: T) -> T {
        #if os(iOS)
        return ios ?? `default`
        #elseif os(macOS)
        return macOS ?? `default`
        #else
        return `default`
        #endif
    }
}

// call site:
let cardElevation = PlatformSelect.value(ios: 0.0, macOS: 2.0, default: 0.0)
```

**Takeaway**: whatever this is called in your project — `Platform.select`, `PlatformSelect.For`, `expect`/`actual`, `platformSelect()`, `PlatformSelect.value` — the moment you see a call site doing `if (platform == X) { a } else { b }` to pick a plain value, that's a violation to route through whichever of these your ecosystem uses (or a new one, following the ecosystem's own idioms, if genuinely none exists).

---

## 2. The "capability" concept, per ecosystem

The shape is always: **wrap an optional, platform-limited feature so "not supported here" is a typed, explicit outcome — never an unconditional call that crashes or silently no-ops.**

**.NET / C#**:
```csharp
public sealed class PlatformCapability<T> where T : class
{
    public T? Value { get; }
    public bool IsSupported => Value != null;
    public PlatformCapability(T? value) => Value = value;

    public static PlatformCapability<T> WindowsOnly(Func<T> factory) =>
#if WINDOWS
        new(factory());
#else
        new(null);
#endif
}

// declaring the capability, once:
public static readonly PlatformCapability<TrayIcon> SystemTray =
    PlatformCapability<TrayIcon>.WindowsOnly(() => new TrayIcon());

// every call site:
if (SystemTray.IsSupported) { SystemTray.Value!.Show(); }
// on mobile, IsSupported is false — nobody has to remember to guard against a crash
```

**TypeScript / web**:
```ts
// capability.ts
interface Capability<T> {
  isSupported: boolean;
  value: T | null;
}

function trayIconCapability(): Capability<TrayIcon> {
  if (typeof window !== 'undefined' && 'systemTray' in window) {
    return { isSupported: true, value: new TrayIcon() };
  }
  return { isSupported: false, value: null }; // explicit, not an accident
}
```

**Swift** — Swift's own `Optional` type already *is* most of this concept; the wrapper mainly adds a same-shaped API across capabilities so call sites are consistent:
```swift
struct Capability<T> {
    let value: T?
    var isSupported: Bool { value != nil }
}

let systemTray: Capability<TrayIcon> = {
    #if os(macOS)
    return Capability(value: TrayIcon())
    #else
    return Capability(value: nil)
    #endif
}()
```

**Kotlin** — same idea, but note that in Kotlin Multiplatform this can *also* be expressed as `expect`/`actual` returning a nullable type, so you may not need a separate `Capability<T>` wrapper class at all:
```kotlin
expect fun systemTrayCapability(): TrayIcon?   // null on platforms without a tray

// androidMain: actual fun systemTrayCapability(): TrayIcon? = null
// desktopMain (JVM): actual fun systemTrayCapability(): TrayIcon? = TrayIcon()
```

**Takeaway**: the *name* varies (`Capability<T>`, a plain nullable, a `{ isSupported, value }` object), but the non-negotiable part is that unsupported is an explicit, typed, checked value — never a bare call to a native API that happens to only work on some platforms.

---

## 3. The file-suffix / conditional-import concept, per ecosystem — and who actually resolves it

Pillar 1 (`principles.md` §2) says platform variance belongs at the file/module boundary. **This does not mean every framework understands a `.ios.`/`.android.` filename automatically.** Whether a suffixed file "just works" depends entirely on the toolchain, and assuming the wrong mechanism is a common way this refactor silently fails (the split file exists, but the build never picks it up, or picks up the wrong one). Before applying any file-suffix convention, classify the actual framework in play into one of these three categories:

### (a) Auto-detected by the bundler/compiler — filename alone is enough
The tool scans for a recognized suffix and resolves it itself; no extra configuration needed.
- **React Native / Expo** (Metro bundler): `Thing.ios.tsx`, `Thing.android.tsx`, `Thing.native.tsx`, `Thing.web.tsx`, with `Thing.tsx` as the shared fallback. Metro resolves these automatically at bundle time — this is the convention used in `examples/secure-storage/`.
- **Kotlin Multiplatform**: not filename-suffix based at all, but still auto-resolved — see (c) below.

### (b) Requires explicit build configuration — filename alone does nothing by itself
The suffix is a human convention; the build tool must be told to honor it, or every suffixed file compiles into every target regardless of name.
- **.NET / MAUI**: `Thing.Windows.cs`, `Thing.Android.cs` only get excluded from the wrong target because the `.csproj` contains explicit `<Compile Remove="**\*.Windows.cs" />`-style globs per `TargetFramework` (see `examples/app-bootstrap/` and the original playbook's §3.1 multi-targeting rule). Delete that project-file configuration and the suffix becomes purely cosmetic — every file still compiles everywhere.
- **Most generic web bundlers (Vite, Webpack, esbuild) without a mobile-specific plugin**: no built-in platform-suffix resolution at all; achieving this requires either a plugin, custom `resolve.alias` config, or falling back to (c)'s conditional-import approach.

### (c) A completely different mechanism — not filename-based
The ecosystem solves file-separation a different way; forcing a filename-suffix convention on top of it is redundant or simply won't be picked up.
- **Kotlin Multiplatform**: source sets (`commonMain/`, `androidMain/`, `iosMain/`) plus `expect`/`actual` declarations — the *directory* a file lives in matters, not its filename. This is the mechanism used in `examples/share-sheet/`.
- **Flutter/Dart**: conditional imports resolved at build time — `import 'thing_stub.dart' if (dart.library.io) 'thing_io.dart' if (dart.library.html) 'thing_web.dart';` — the platform choice is made at the *import statement*, not by a recognized filename.
- **Swift, multi-target Xcode project**: per-target file *membership* is configured in the project/workspace itself (a file is or isn't included in a given target's build phase); `#if os(...)` is reserved for the one canonical platform-check location, not for swapping whole files.

### The check to run before trusting any suffix convention
1. Identify which of (a)/(b)/(c) the actual framework in this codebase falls into — don't assume based on what a *different* project used.
2. For (a): confirm the exact suffix vocabulary the bundler recognizes (e.g. React Native's Metro also accepts `.native.` as a mobile-family fallback distinct from `.ios.`/`.android.` — check the current docs, this list changes across versions).
3. For (b): confirm the build-configuration glob/exclude rules actually exist and actually match the new file's name — a typo'd glob pattern silently compiles the wrong-platform file into every target.
4. For (c): don't invent a filename suffix at all; use the ecosystem's real mechanism (source sets, conditional imports, target membership) exactly as documented.

**Rule of thumb**: use the framework's native mechanism, whichever category it falls into — don't build a parallel custom system on top of a category-(a) or category-(c) framework. Reserve custom `select`/`Capability` helpers (§1–§2 above) for the *values and optional-features* problem, not the *which file gets compiled* problem, since a category-(a)/(c) framework already solves the latter for you.

---

## 4. Choosing what to build when nothing exists yet

If a project's ecosystem has no native select mechanism and no existing helper:
1. Check whether the framework already solves this a level up (e.g. many UI frameworks have *some* theming/resource-resolution system that already does density/locale swapping — don't duplicate it for a problem it already covers).
2. If genuinely nothing exists, write the smallest possible generic helper in the ecosystem's own idiom (a plain function for JS/Dart, a generic static class for C#/Java, an `expect`/`actual` pair for Kotlin Multiplatform) — not a heavyweight abstraction layer.
3. Name it clearly and put it in exactly one place. Whatever you call it, that name becomes this project's vocabulary for "the select helper" and "the capability wrapper" for the rest of the refactor — use it consistently rather than reinventing it per file.
