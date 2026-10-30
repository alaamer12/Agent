# Examples Index: Before/After Refactor Directories

Real before/after project trees live under `examples/`, one subfolder per refactor **shape**. `view` the `before/` and `after/` directories directly — don't just read about them here. These examples deliberately span different domains, languages, and frameworks (a storage service, an app bootstrap, a share action, a list card) — the point is the *shape* of each refactor, not the specific feature. When applying this to a real codebase, match the shape to your violation and translate the domain — don't assume the project you're refactoring has anything to do with storage, sharing, or cards.

## Table of contents
1. `examples/secure-storage/` — file → files (+ Platform type for an untyped language)
2. `examples/app-bootstrap/` — inside the file (composition root)
3. `examples/share-sheet/` — multi-member module split (Kotlin `expect`/`actual`)
4. `examples/list-item-card/` — view/layout barrel

---

## 1. `examples/secure-storage/` — file → files

**Shape**: a module doing real, structural, multi-operation work for more than one platform. **Language**: plain JavaScript (untyped) — chosen deliberately to also demonstrate the Platform Type point from `principles.md` §1a.

- `before/src/services/secureStorage.js` — one file, real branching logic inside a shared location, other platforms silently unsupported by omission.
- `after/src/platform/Platform.js` — new file: a frozen, closed set of platform values (`PlatformName`) plus the one function allowed to ask the runtime directly. This is the untyped-language substitute for a compiler-checked enum — see `principles.md` §1a.
- `after/src/services/secureStorage.js` — shared shell/barrel, switches only on `PlatformName`, never a raw string.
- `after/src/services/secureStorage.ios.js` / `.android.js` — real per-platform implementations.
- `after/src/services/secureStorage.unsupported.js` — explicit honest no-op (a Variant not yet implemented, not a Capability).

Read this pair first — it's the canonical shape most violations reduce to, and the one most likely to need a Platform Type if your codebase isn't statically typed.

## 2. `examples/app-bootstrap/` — inside the file (composition root)

**Shape**: several small platform-only side effects scattered as inline conditionals in one file. **Language**: C# (.NET), where the file-suffix convention requires **manual build configuration** — see `utilities.md` §3 for why this matters before you copy the pattern.

- `before/Program.cs` — one file, three unrelated inline `#if` blocks.
- `after/Program.cs` — composition root with zero inline conditionals, three one-line hook calls.
- `after/PlatformStartupHooks.cs` — new file, shared shell declaring the hooks (no platform logic itself).
- `after/PlatformStartupHooks.Windows.cs` / `.Android.cs` — new files, per-platform hook implementations.

Compare this to `examples/secure-storage/` — same underlying rule (file-separation, one canonical platform check), applied to side effects instead of a return value, in a different ecosystem with a different (manual, not automatic) file-resolution mechanism.

## 3. `examples/share-sheet/` — multi-member module split

**Shape**: a module with several operations, only some of which vary by platform — split only the varying one. **Language**: Kotlin Multiplatform, where `expect`/`actual` + source sets (`commonMain/`, `androidMain/`, `iosMain/`) **is** the language's own file-separation mechanism — no custom helper needed at all.

- `before/ShareSheet.kt` — one object, one function branches internally, a second unrelated function has no variance at all.
- `after/commonMain/ShareSheet.kt` — the varying function becomes an `expect fun` declaration only; the non-varying function is untouched, in the same file/source set.
- `after/androidMain/ShareSheet.android.kt` / `after/iosMain/ShareSheet.ios.kt` — `actual fun` implementations, one per source set.

Notice what did **not** move: `formatShareMessage` never needed a platform check, so it stays in `commonMain` untouched — don't over-split a file just because *some* of it varies.

## 4. `examples/list-item-card/` — view/layout barrel

**Shape**: a composite/block-level component whose layout tree itself (not just styling) needs to differ per platform. **Language**: React (TypeScript).

- `before/src/components/ListItemCard.tsx` — one component, one layout tree, `isMobile &&` scattered through it to hide/show fields.
- `after/src/components/ListItemCard/ListItemCard.tsx` — thin host shell, zero real layout content.
- `after/.../ListItemCardDesktopLayout.tsx` — full-detail layout with hover affordances.
- `after/.../ListItemCardMobileLayout.tsx` — designed for what a small screen actually needs (two fields, swipe actions) — not a shrunk copy of the desktop tree.

Apply this pattern to every composite component and page in the app being refactored, not just cards — a dashboard panel, a settings screen, a detail page are all candidates.

---

## How to use these when refactoring a real codebase

1. Identify which shape (§1–§4 above) the violation you're looking at matches — ignore the specific domain (storage/bootstrap/sharing/cards), it's incidental.
2. Open the matching `before/` tree and compare it structurally to the violation in front of you — same anti-pattern, different feature.
3. Open the matching `after/` tree and mirror its file layout and naming convention, substituting this project's actual platforms, actual select mechanism (see `utilities.md`), and actual domain logic.
4. Before assuming a file-suffix convention "just works," check how the actual framework in this project resolves platform files — see `utilities.md` §3. Some frameworks auto-detect suffixes at bundle time (Expo/React Native's Metro bundler), some require you to configure the build yourself (.NET's `.csproj` globs), and some use an entirely different mechanism that isn't filename-based at all (Kotlin source sets, Dart conditional imports).
5. If the project's language has no static type system, check whether it already has a canonical Platform type/constant set (`principles.md` §1a) before adding a new one — and never compare raw platform strings ad hoc at a call site.
