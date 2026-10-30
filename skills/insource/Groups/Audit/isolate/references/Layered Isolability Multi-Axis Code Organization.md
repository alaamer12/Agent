# Layered Isolability: Organizing Code That Varies Along Several Axes

*Language-agnostic design standard. Status: proposed.*

## 1. Summary

**Isolability** is the property of code that can be isolated: built, tested, replaced, shipped, or removed without editing code that belongs to a different axis of variation. A system has good isolability when every difference has exactly one home and no single file has to name two dimensions to exist.

The approach is escalating. Start with the simplest mechanism that works, and move up only when a named constraint forces you to. Each level solves the constraint of the one before it.

| Level | Trigger | Constraint it runs into | Mechanism |
| --- | --- | --- | --- |
| 1 | One axis varies | A second axis appears and names start to multiply | Per-variant files selected by a name suffix |
| 2 | Two axes vary | A third axis appears and directories start to multiply | Overlay directories selected by a build property |
| 3 | Three or more axes, or any axis that must switch at runtime | None structural: a new axis adds one selector, not a new grid | Layers: selectors, layer keys, a registry, and a resolver |

Level 3 is not limited to three axes. It is the first level whose structure does not change when another axis arrives, so it works for any number of axes from two upward. It becomes worth its cost at the point where Level 2 would start to form a grid, which is usually the third axis.

## 2. How to Read This Document

**Standing note on examples.** Every concrete choice in this document is illustrative, not exhaustive or mandatory. Names in `[brackets]` are examples of what could fill a slot, and a hybrid or an unlisted answer is always acceptable. Where a choice has real trade-offs, the document states them so the team can decide.

- **Axes are not fixed.** \[target platform\], \[release channel\], \[audience or region\], \[customer tenant\], \[hardware tier\], \[experiment cohort\], and \[accessibility profile\] are all examples of axes. Your system may have different ones, and in a different order.
- **The running component is only an example.** To keep things concrete, the document follows one illustrative component: a confirmation dialog (called `ConfirmationBox` in the sketches). Any component with behavior that varies would do.
- **Code is descriptive, not prescriptive.** Snippets show the shape of an idea in several languages. The requirement is the behavior described in the prose, not any one syntax or library.

## 3. Level 1: One Axis Varies

**Scenario.** The example component must behave differently depending on one axis, say \[target platform\]: how it finds the native window, how it draws, how it plays a sound.

**Solution: seams fulfilled by per-variant files.**

1. The component has **one public surface**. Callers use a single name and a single import and never see a variant.
2. The shared file declares **seams**: members that are named but not implemented. Each variant file fulfils the seams for its own variant.
3. Selection happens **at build time**. A variant that fails to fulfil a seam is a build error, not a production bug.
4. Variants that share a family (for example two \[mobile\] platforms) put the shared logic in one **family file**, marked by a convention such as a leading underscore. Each platform file then re-exports it through a thin forwarding member, which keeps an explicit, searchable place where that platform can diverge later.

Here is point 4 as a concrete file layout, using the example component. Each family (here \[mobile\] and \[desktop\], though yours may differ) writes its shared logic once in an underscore file, and every platform in the family keeps its own small file:

```
ConfirmationBox.cs            shared logic; declares the seams
_ConfirmationBox.Mobile.cs    logic shared by the mobile family (Android, iOS)
ConfirmationBox.Android.cs    one-line forward to the mobile family file
ConfirmationBox.iOS.cs        one-line forward to the mobile family file
_ConfirmationBox.Desktop.cs   logic shared by the desktop family (Windows, macOS, Linux)
ConfirmationBox.Windows.cs    one-line forward to the desktop family file
ConfirmationBox.macOS.cs      one-line forward to the desktop family file
ConfirmationBox.Linux.cs      one-line forward to the desktop family file
```

The platform file is only a forward. Both the Android and iOS files contain the same single line:

```csharp
// ConfirmationBox.Android.cs (ConfirmationBox.iOS.cs is identical)
public static partial class ConfirmationBox
{
    static partial object? NativeWindow() => MobileNativeWindow(); // body lives once, in _ConfirmationBox.Mobile.cs
}
```

Callers still see one `ConfirmationBox`. If Android later needs different behavior, you edit its one-line file only, and iOS is untouched. The same shape works in other languages: the family file is a shared module, and each platform file re-exports it.

A platform that shares nothing with others needs no family file and fulfils the seams in its own file. A new platform joins an existing family by adding one forwarding file, and a new family is one new underscore file.

Most ecosystems already have a native way to say "declared here, fulfilled per variant":

| Ecosystem (examples) | How a seam is declared and fulfilled |
| --- | --- |
| \[C#\] | `partial` members, files chosen by multi-targeting |
| \[Kotlin Multiplatform\] | `expect` declarations with `actual` implementations per source set |
| \[Go\] | One function name defined in several files, each guarded by a build constraint |
| \[Rust\] | One function name defined under mutually exclusive `cfg` attributes |
| \[Swift, C, C++\] | Per-variant source files plus conditional compilation or per-target build rules |
| \[TypeScript, JavaScript\] | Conditional package exports or per-variant module resolution |

Illustrative sketches of the same idea:

```csharp
// shared file
public static partial class ConfirmationBox { static partial object? NativeWindow(); }
// windows file
public static partial class ConfirmationBox { static partial object? NativeWindow() => null; /* OS call here */ }
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

Why this level is right for one axis: the axis is **total**. Every variant must answer every seam, and the compiler can check that. A name suffix is a coordinate, and one coordinate fits in a filename.

**Constraint.** A second axis arrives. A file that must vary by platform and by \[release channel\] wants a name like `ConfirmationBox.Canary.Android.cs`, and nothing says whether the other order is correct. Multiply that by every component and every new value and you get a grid of near-identical files that drift apart. A filename can hold one dimension. It cannot hold two.

## 4. Level 2: A Second Axis Appears

**Scenario.** The product now ships on a second axis, for example a \[release channel\] with an experimental variant next to the stable one. The experimental variant changes the code (say, a different rendering path), not just a few strings.

**Solution: move the second axis from the filename to the path.** The first axis stays in the name. The second axis becomes a directory that overlays the base:

```
ConfirmationBox/                    base: every file the component has
  ConfirmationBox.cs
  ConfirmationBox.Windows.cs
  _ConfirmationBox.Mobile.cs
Overlays/
  <variant-id>/
    ConfirmationBox/
      _ConfirmationBox.Mobile.cs    only the files that differ
```

The build takes one property (for example the variant id), and a file in the overlay **shadows** the base file at the same relative path. The filename never carries more than the first axis.

**Rules that keep this level healthy:**

- **Overlay, do not fork.** The overlay holds only files that differ. Copying a whole component into the overlay recreates the grid inside a folder.
- **Key overlays by id, not by a fixed name.** The axis is an open set. There may be many experimental variants, each with different content, so a single folder called `Experimental/` is not enough.
- **Shadowing replaces a file.** It is not inheritance, so the overlay cannot call the original. Keep seam files small and single-purpose so that replacing one is cheap.
- **Platform filtering still applies to overlay files**, so a file for one platform in an overlay is not compiled into another platform's build.
- **Seam signatures belong to the base.** A mismatch is a compile error, which is the behavior you want.

The build property is selected differently in each ecosystem. These are examples:

| Ecosystem (examples) | How the overlay is chosen at build time |
| --- | --- |
| \[MSBuild\] | Item globs that remove base files and include overlay files, driven by a property |
| \[Cargo\] | Features combined with `cfg` |
| \[Bundlers\] | Resolve conditions or aliases |

**Constraint.** Two things break as this level grows:

1. **A third axis arrives** (for example \[audience or region\]). Nesting it as `Overlays/<variant>/<audience>/` is a grid again, one level up.
2. **File shadowing is blunt.** It is fixed at build time, so it cannot switch at runtime, and it replaces rather than wraps, so an overlay cannot extend base behavior.

## 5. Level 3: A Third Axis, and Any That Follow

**Scenario.** Besides platform and \[release channel\], the product now varies by a third axis such as \[audience or region\]. Tags like `[experimental]-[candidate]-[region]` show up in release names.

**Solution: layers.** The key idea is to separate two jobs that Level 2 mixed together.

- **Inclusion** decides which code exists in this binary. Directories and the build handle it.
- **Selection** decides which of the included implementations is used right now. Code handles it, in one visible place.

### 5.1 The parts

1. **Axis selector.** One small unit per axis that reports one fact: the current platform, the current channel, the current audience. A selector knows nothing about components.
2. **Layer key.** The explicit coordinates a layer applies to: a set of (axis, value) pairs. An empty set is the base. A key with one pair is a single-axis layer. A key with two pairs is a **tie-breaker layer** that exists only where two single-axis layers collide.
3. **Registry.** For each seam, the base declares a contract (an interface, protocol, trait, or function type) and a registry. Layers register an implementation under their key.
4. **Resolver.** A single function takes the registry and the current values from the selectors and returns one implementation.

### 5.2 The resolution rule

A layer matches when every coordinate in its key equals the current value of that axis. Among matching layers, **the one with the most coordinates wins**. If two matching layers have the same number of coordinates, the result is ambiguous and must fail loudly until someone registers a tie-breaker layer that names both. This generalizes to any number of axes without a table of special cases.

Illustrative sketches of the resolver:

```typescript
type Ctx = Record<string, string>;        // e.g. { channel: "x", audience: "y" }
type Layer<T> = { when: Ctx; impl: T };   // when = {} is the base

function resolve<T>(layers: Layer<T>[], ctx: Ctx): T {
  const hits = layers.filter(l => Object.entries(l.when).every(([k, v]) => ctx[k] === v));
  const best = Math.max(...hits.map(l => Object.keys(l.when).length));
  const top = hits.filter(l => Object.keys(l.when).length === best);
  if (top.length !== 1) throw new Error(top.length ? "ambiguous layers" : "no base layer");
  return top[0].impl;
}
```

```python
def resolve(layers, ctx):
    hits = [l for l in layers if all(ctx.get(k) == v for k, v in l.when.items())]
    best = max((len(l.when) for l in hits), default=-1)
    top = [l for l in hits if len(l.when) == best]
    if len(top) != 1:
        raise LookupError("ambiguous layers" if top else "no base layer")
    return top[0].impl
```

```kotlin
data class Layer<T>(val whenAll: Map<String, String>, val impl: T)

fun <T> resolve(layers: List<Layer<T>>, ctx: Map<String, String>): T {
    val hits = layers.filter { l -> l.whenAll.all { (k, v) -> ctx[k] == v } }
    val top = hits.groupBy { it.whenAll.size }.maxByOrNull { it.key }?.value
        ?: error("no base layer")
    return top.singleOrNull()?.impl ?: error("ambiguous layers")
}
```

The strict ambiguity rule is a choice. Example alternatives: \[declare a fixed axis precedence, such as audience beats channel\], \[require an explicit tie-breaker layer\], \[allow runtime ordering by priority number\]. A fixed precedence is shorter to write but hides collisions. Requiring a tie-breaker is more work but makes every collision a reviewed decision. This document recommends the strict rule, and a team may choose otherwise.

### 5.3 Folder layout

The folder structure mirrors the keys. Axis names and values below are examples.

```
<Component>/                         base layer: contract, shared logic, platform files
Layers/
  <axisA>/<valueA>/<Component>/      layer keyed by one coordinate
  <axisB>/<valueB>/<Component>/
  <axisA>+<axisB>/<valueA>.<valueB>/<Component>/
                                     tie-breaker, exists only if the two above collide
```

The filename still carries exactly one dimension (the total axis, often platform). The folder chain carries every sparse axis. A name such as `Component.ValueA.ValueB.Platform.ext` never exists.

**A concrete tree.** Using the example component and two example axes, \[release channel\] (value: canary) and \[audience\] (value: eg), the folders sit like this:

```
src/
  Core/                              shared machinery, knows no component
    axis selectors                   report the current channel, audience, platform
    layer key, registry, resolver    the Level 3 mechanism, written once
  ConfirmationBox/                   the component and its BASE layer
    ConfirmationBox.cs               public surface, seams, registry; asks the resolver
    ConfirmationBox.Windows.cs       Level 1 platform files
    _ConfirmationBox.Mobile.cs
    ConfirmationBox.Android.cs
    DefaultPolicy.cs                 base implementation of the seam contract
  Layers/                            sibling of the components, never inside them
    channel/canary/ConfirmationBox/
      CanaryPolicy.cs                applies when channel = canary
    audience/eg/ConfirmationBox/
      EgPolicy.cs                    applies when audience = eg
    channel+audience/canary.eg/ConfirmationBox/
      CanaryEgPolicy.cs              applies when both match; exists only if the two above collide
  Registration/
    registration list                per-build list of registration calls, generated or hand-written
```

**Where layer folders exist.** They live under one `Layers/` root, grouped by axis, and each contains one subfolder per component that the layer changes. Someone asking what canary changes finds the answer in one folder. A layer folder holds only files that differ from the base.

**What each build includes.** The build includes the base, the layer folders for its own build-time axes (this build's channel), and, for runtime axes, the folders of every value that may be selected (all audiences). A folder for another channel is excluded, so it never ships in this binary.

### 5.4 Who depends on whom

```
callers        -> component (the one public surface)
component      -> resolver (the only thing it knows about layers)
resolver       -> axis selectors
layer files    -> the base contract only; the registration list imports them
base           -> never references any layer
```

The base owns the contract and layers fulfil it. This is dependency inversion, the same relationship the base already had with its per-platform files at Level 1. Two consequences follow:

**The same thing in file terms: who imports whom.**

- **Callers** import the component and nothing else.
- **The component's main file** imports the core machinery (the registry type and the resolver). It never imports a layer.
- **The base implementation** imports the seam contract, which lives in the component's main file.
- **A layer file** imports the seam contract from the component and the layer key type from core. It never imports another layer, and it never imports the component's implementation files.
- **The registration list** is the only place that imports layers. It imports the component's registry, the base implementation, and every layer included in this build, and adds each one under its key.
- **App startup** calls the registration list once, before the first use of any component.

There is no cycle. The component does not import the registration list, so the registration list can import both the component and the layers. The choice of which layers are present lives in the build, and the knowledge that they exist lives in one file.

- **Layers never reference each other.** Any layer may be absent from a given build. Only a tie-breaker layer may know both of its parents, because it exists only when both are present.
- **Wrapping becomes possible.** The resolver may return an ordered chain instead of one winner, so a layer can decorate another layer's behavior, which file shadowing could not do.

### 5.5 Inclusion versus selection by axis

Not every axis binds at the same moment. Classify each one:

| Axis (examples) | Candidates present in the binary | Choice made |
| --- | --- | --- |
| \[target platform\] | Only that platform's files | Build |
| \[release channel\] | Only that channel's layer folders | Build |
| \[audience or region\] | All audiences, if it can change at runtime | Runtime |
| \[customer tenant\] | All tenants | Runtime |

If an axis is fixed per install and does not need to switch at runtime, it may also bind at build time, and the registry for it shrinks to a single static choice.

### 5.6 Registering layers

Two rules matter more than the mechanism:

- **Name the full coordinates in every registration**, even when the build already decided one of them. The registration then documents which cell it fulfils, and a layer that leaks into the wrong build stays inert because it can never match.
- **Register explicitly.** Prefer a generated or hand-written registration list, or a module initializer, over reflection or classpath scanning. Scanning breaks under trimming, ahead-of-time compilation, and strict-sandbox platforms.

Use typed identifiers for axis values (an enum, a branded type, a constants class) rather than free strings, so a typo is a compile error.

### 5.7 When a fourth axis arrives

This is the payoff of Level 3. Adding an axis such as \[hardware tier\] touches no existing component:

1. Add a selector that reports the new axis.
2. Add its typed identifier values.
3. Add layer folders only for components that actually vary on it.
4. Extend the ambiguity check so it includes the new axis.

No existing layer is renamed, copied, or moved.

## 6. Isolating Variants That Run Together

If variants must be installed and run on one machine at the same time (for example so testers can compare them), isolation extends beyond code. Every identifier that two variants share is a collision, so identity must derive from one source rather than being typed by hand in many places.

**Collision checklist** (examples, adapt to your platform):

- Install location and executable name
- Single-instance locks and watchdog locks
- OS registrations: \[shortcut identity\], \[URL scheme handlers\], \[file associations\], \[autostart entry\], \[notification ids\]
- Databases, settings, logs, and caches
- Local IPC endpoints: \[named pipes\], \[sockets\], \[local ports\], \[shared memory\]
- Embedded web view data folders
- Update feed and update target
- Mobile identifiers: \[application id\], \[bundle id\]
- Telemetry and crash reports, tagged by variant so test noise does not pollute production numbers
- Database schema: migrations must be additive, or each variant keeps a separate store

**Which axes feed identity.** Only axes that must coexist should. The others are metadata stamped into build info and telemetry.

| Axis (examples) | Feeds identity? | Reason |
| --- | --- | --- |
| \[release channel\] | Yes | Variants must run side by side |
| \[audience or region\] | No, metadata by default | A real user installs the plain product, not a regional copy |
| \[promotion ring\] | No, metadata | See section 7 |

If testers need audiences side by side, they opt in with an explicit identity suffix, which is not the default.

**Enforce it.** Add a lint rule, static analyzer, or test that fails the build when the product name appears as a literal anywhere outside the single identity source. Isolation then becomes a build error instead of a discovery during testing.

## 7. Things That Look Like Axes but Are Not Code

Run two checks before adding anything to the source tree.

1. **Would the bytes differ?** If the binary is the same, it is not a code axis. A \[promotion ring\] such as a release candidate is a state, not a variant. The candidate must be the exact artifact that later becomes the stable release, so promotion means moving a pointer in the update feed, never rebuilding.
2. **Would the code differ, or only values?** If only values differ (names, endpoints, locale, limits, wording), the difference is data. Put it in a configuration pack, not in a layer.

A composite tag such as `[channel]-[ring]-[audience]` should be parsed into segments, and each segment should contribute only its own part: the channel to build inputs, the ring to distribution, the audience to layer selection. Do not hand-write one profile per combination. A segment with no matching definition should fail the build, so a typo is caught immediately.

## 8. Rules

1. **One axis per filename.** If a filename needs two dimension suffixes, policy has leaked into capability. Find the missing primitive in the capability layer and add it there.
2. **Capability versus policy.** The environment supplies capabilities (what the platform can do). Channel, audience, and similar axes supply policy (what we choose to do with them). Policy is written once on top of capabilities and never asks which environment it runs on.
3. **Total axes use names. Sparse axes use priority.** A coordinate scheme suits an axis every variant must answer. A priority chain suits an axis that overrides a few things.
4. **Layers contain only differences.** A layer that copies a whole component is a fork.
5. **Seams are small and named for what varies**, not for the component.
6. **The base owns signatures.** Layers cannot change a seam's contract.
7. **Layers never reference each other.** Shared code moves down into the base or a common library, never sideways.
8. **Layers may add helper files**, reachable only through the seam they serve.
9. **Platform filtering applies to the resolved file list**, once, not per layer.
10. **Explicit registration and typed identifiers.** No scanning, no free strings.
11. **If two builds can run at once, every identifier they share is a bug.**

## 9. Verification

| Check | What it catches |
| --- | --- |
| Folder matches key | A layer's folder path and its registered key disagree |
| Ambiguity test | Two layers of equal specificity match the same context and no tie-breaker exists, tested over every combination of axis values |
| Duplicate key | Two registrations in one cell, failing at startup |
| Missing base | A seam with no base implementation |
| Resolved-map report | CI prints which layer wins each seam per profile, and warns when a base file changed after the layer that shadows it |
| Identity lint | A hardcoded product name outside the identity source |
| Coexistence smoke test | Launch every variant at once and assert nothing collides |

The tie-breaker rule is the important one. A cell where two axes meet is allowed to exist, but only where two layers truly disagree, and a person writes the resolution once.

## 10. Decision Guide

| Situation | Use |
| --- | --- |
| Only one axis varies, and every variant must answer | Level 1: per-variant files with a name suffix |
| A second sparse axis appears | Level 2: overlay directories |
| A third axis appears, or any axis must switch at runtime or wrap behavior | Level 3: layers |
| Only strings or values differ | Data: a configuration pack |
| The binary would be identical | Distribution: a feed pointer or rollout setting |
| An axis needs a different implementation per environment | Add a capability seam to the platform layer, then let policy choose |

Before adding a file, ask three questions in order. Would the bytes differ? Would the code differ, or only values? Is the difference a capability or a policy?

## 11. Trade-offs and Risks

- **Runtime selection ships every candidate.** Inclusion must exclude layers that do not belong in the binary, or experimental code ships inside the stable build.
- **Shadowing replaces.** Where wrapping is needed, resolve a chain and decorate, rather than shadow a file.
- **Two features claiming one seam** is a real conflict. Validate and fail the build instead of letting registration order decide.
- **Base drift.** A base file can change while an overlay silently keeps the old behavior. The resolved-map report exists to expose this.
- **Frequent tie-breaker layers** signal that a seam is too coarse. Split it into smaller seams.
- **Cost of Level 3.** It adds selectors, a registry, and CI checks. Do not adopt it while directories are enough.

## 12. Adoption Checklist

1. List every axis that varies today, and classify each as total or sparse, build-time or runtime, identity or metadata.
2. Keep the total axis in filenames. Do not change what already works.
3. Extract small replaceable seams from components that will need to change.
4. Introduce the selectors, layer key, registry, and resolver once, in shared core code, in your language's idiom.
5. Move variant identity into a single generated source and add the lint rule.
6. Add build inclusion rules so each build contains only its own layers.
7. Add the checks in section 9 to CI.
8. Migrate one component first, then repeat.

## 13. Glossary

- **Isolability:** every difference has one home, and any layer can be added, replaced, tested, or removed without editing another.
- **Axis:** an independent dimension of variation.
- **Seam:** a small, named, replaceable unit of behavior that the base declares and layers fulfil.
- **Base:** the default implementation, which owns the contract and knows nothing about layers.
- **Layer:** a set of implementations that apply to one cell of the axes.
- **Layer key:** the explicit coordinates a layer applies to.
- **Tie-breaker layer:** a layer keyed by two or more axes, written only where single-axis layers collide.
- **Selector:** a unit that reports the current value of one axis.
- **Resolver:** the single function that chooses one implementation for the current context.
- **Inclusion versus selection:** the build decides what exists, the resolver decides what is used.
- **Capability versus policy:** the environment supplies capabilities, and the other axes supply policy on top.
- **Promote, do not rebuild:** a release ring moves the same bytes forward.
