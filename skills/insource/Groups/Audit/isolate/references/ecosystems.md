# Mapping the design onto an ecosystem

Contents: seams per ecosystem, per-language sketches, build selection per ecosystem, how to choose.

Standing note: every ecosystem named here is an example. If the project uses one that is not listed, find its native way to say "declared here, fulfilled per variant" and "include these files for this build", and use that. Never convert a project to another language's idiom.

## Level 1: declaring and fulfilling a seam

| Ecosystem (examples) | How a seam is declared and fulfilled |
|---|---|
| `[C#]` | `partial` members, files chosen by multi-targeting |
| `[Kotlin Multiplatform]` | `expect` declarations with `actual` implementations per source set |
| `[Go]` | one function name defined in several files, each guarded by a build constraint |
| `[Rust]` | one function name defined under mutually exclusive `cfg` attributes |
| `[Swift, C, C++]` | per-variant source files plus conditional compilation or per-target build rules |
| `[TypeScript, JavaScript]` | conditional package exports or per-variant module resolution |
| `[Python]` | per-variant modules chosen by a single import shim, or an abstract base plus one registered implementation |

All of these give the property that matters: a variant that fails to fulfil a seam is a build or import error, not a runtime surprise. If an ecosystem cannot give that, add a startup check that fails when a seam has no implementation.

Sketches of one seam (find the native window) in four paradigms:

```csharp
// shared file
public static partial class ConfirmationBox { static partial object? NativeWindow(); }
// one platform file
public static partial class ConfirmationBox { static partial object? NativeWindow() => null; /* OS call */ }
```

```kotlin
// common source set
expect fun nativeWindow(): Any?
// android source set
actual fun nativeWindow(): Any? = null // OS call here
```

```go
// confirmation_windows.go
//go:build windows
func nativeWindow() any { return nil } // OS call here
// confirmation_android.go holds the same signature under //go:build android
```

```rust
#[cfg(target_os = "windows")]
fn native_window() -> Option<Handle> { None } // OS call here
#[cfg(target_os = "android")]
fn native_window() -> Option<Handle> { None }
```

Family file forward, shown for one language (the same shape works in every other: the family file is a shared module and each platform file re-exports it):

```csharp
// Component.Android.cs (Component.iOS.cs is identical)
public static partial class Component
{
    static partial object? NativeWindow() => MobileNativeWindow(); // body lives once, in _Component.Mobile.cs
}
```

## Level 2 and 3: choosing what is included in a build

| Ecosystem (examples) | How the overlay or layer folders are chosen at build time |
|---|---|
| `[MSBuild]` | item globs that remove base files and include overlay files, driven by a property |
| `[Gradle]` | source sets or product flavors |
| `[Bazel, Buck]` | `select()` on a build setting |
| `[CMake]` | conditional `target_sources` |
| `[Cargo]` | features combined with `cfg` |
| `[Bundlers]` | resolve conditions or aliases |

Whatever the mechanism, three behaviors are required:
1. Exactly one variant's overlay or layer folders are compiled for a given build property.
2. Platform filtering applies to the resolved file list once, not per layer, so a platform-specific file in a layer never compiles into another platform.
3. Layer folders for other build-time axis values are excluded, so they never ship in this binary.

Give each variant its own intermediate and output directories so parallel builds do not overwrite each other.

## Choosing, with trade-offs

- **Generate the registration list** `[from the included layer folders]`: no hand edits to drift, but needs a build step. **Write it by hand**: simplest, but a layer can be forgotten; the folder-matches-key check in `verification.md` covers that.
- **Resolver in code** `[plain function]` versus `[dependency-injection container]`: use the container only if the project already has one, and keep the rule (most specific match wins, ties fail) unchanged.
- **Dynamic languages** with no compile step: make the "missing seam" check a startup assertion and run it in CI.
