# Principles: Vocabulary & the Three Pillars

## Table of contents
1. Diagnostic vocabulary
1a. Platform Type — closed, checkable representation of "platform"
2. Pillar 1 — Cross-Platformality (file/module separation)
3. Pillar 2 — Abstractionality (Base Unit → Specialization)
4. Pillar 3 — View/Layout Barrel for composite components
5. Full parity checklist (audit every dimension, not just API calls)

---

## 1. Diagnostic vocabulary

| Term | Definition |
|---|---|
| **Platform** | A concrete target the app ships to (e.g. "iOS", "Android", "Windows", "Web", "a game console"). Fixed for the life of a running process — read it once, treat it as a constant, don't re-detect it repeatedly. See §1a for how to represent this as a closed, checkable type rather than raw strings. |
| **Platform Family** | A group of platforms that plausibly share the same answer for a *given concern* (e.g. "touch-based mobile platforms" as a family for input handling). Families are a per-concern judgment call, not a fixed taxonomy — two platforms can be the same family for touch handling and different families for secure storage. |
| **Capability** | Something the app can *optionally* do, which some platforms don't support at all (system tray icon, background execution, biometric prompt, haptics, "reveal in file explorer"). Defining trait: on unsupported platforms the correct answer is **nothing** (null/no-op) — not a worse version of the same thing. |
| **Variant** | Something every platform must do, but differently (send a notification, persist a secret, resolve an image, lay out a screen). Defining trait: every platform has a *real* implementation; only the mechanism differs. Never resolve a Variant to null — that's a Capability mistake. |
| **Base Unit** | A named, documented, reusable building block encoding one micro-behavior (a debounced text field, a confirmation dialog, a currency formatter). |
| **Specialization** | A named unit that composes/configures a Base Unit for one concrete use case without re-implementing its logic. |
| **Barrel** | A thin, platform-neutral entry point (file/module/class) with **zero** platform-conditional logic of its own — it only routes to the correct per-platform implementation. The barrel is where "which platform am I" gets asked; nowhere else should ask it. |

### 1a. Platform Type — give "platform" a closed, checkable shape

Every rule above assumes "platform" is a small, closed set of values — but that's only *enforced* automatically in a statically typed language. Before writing any barrel, selector, or capability map:

- **Statically typed language** (TypeScript, C#, Kotlin, Swift, Java, Rust, …): define an actual closed type — a union type, an enum, or a sealed class — for the platform identity (e.g. `type PlatformName = 'ios' | 'android' | 'web'`). The compiler then makes it impossible to compare against a typo'd string or to forget a case in a switch.
- **Untyped or dynamically typed language** (plain JavaScript, Python without type hints, Ruby, …): there is no compiler to catch `'Android'` vs `'android'` scattered across the codebase, so define one canonical, frozen constant object/module (e.g. a frozen object of named values) that every other file imports its platform values from — never a raw string literal at a call site. Treat this the same as the "one canonical file" rule in §2.1: exactly one file defines the set of valid values, and exactly one function in that file is allowed to ask the runtime/OS what the actual current platform is.
- Either way, this Platform Type is a *prerequisite* for the rest of Pillar 1 — a selector, capability map, or barrel built on top of raw ad hoc string/number comparisons will regress the moment someone fat-fingers a value, silently falling through to a default case instead of failing loudly.

## 2. Pillar 1 — Cross-Platformality: file/module-separation

**The one legal way to express platform variance is at the file/module boundary — never as a branch inside a shared file's body.** For any unit `Thing` that varies by platform:

```
Thing/
├── Thing.core           # shared, platform-neutral shell — public API + shared logic, NO platform conditionals
├── Thing.platformA       # Platform A's real implementation
├── Thing.platformB       # Platform B's real implementation
├── _Thing.familyX        # logic shared by an entire family — not platform-neutral, but reused verbatim
├── Thing.platformC       # exports/re-uses _Thing.familyX (platform C belongs to family X)
└── Thing.platformD       # exports/re-uses _Thing.familyX (platform D also belongs to family X)
```

Rules:
- The shared shell contains **zero** platform-conditional branches. Wanting one there is the signal to split a new per-platform file instead.
- A per-platform file whose logic is identical to another's doesn't get rewritten — it exports the shared family file. It still gets its own file, though, so the build only compiles what that target actually needs.
- Verify your build/compile configuration genuinely excludes non-matching platform files from non-matching targets. This is not automatic in most toolchains.
- **Only one canonical location in the entire codebase may contain the real "which platform is this" check.** Everything else — every capability map, every barrel, every audit — reads from that single accessor. If you search the whole codebase for your language's platform-conditional syntax, the only hits should be that one file, plus the compile-time selector helper (§below) if its own internals need one.

**Two shapes beyond "single value" that come up constantly** (see `examples-refactors.md` for full code):
- **Multi-member shared module**: a module/class with several operations, only some of which vary — split into a shared shell + per-platform files supplying just the varying operations, using a "try" shape (`try_get_result() -> (found, value)`) if a platform has no answer yet.
- **Composition-root/startup code**: several small platform-only side effects scattered as inline conditionals in app bootstrap code — extract each into a named method on a small platform-only "hooks" object, called with one line from the composition root.

**Standing self-check**: codify and run, repeatably, a search for your stack's platform-conditional syntax across all source files. Run it once at the start of any audit (don't trust a stale count), after every single file split during a refactor (not batched), and as a standing lint/CI check afterward.

**Don't over-correct**: a file whose *history* involved a platform bug doesn't need a split if the final code has no actual branch left. Splitting adds churn without reducing risk — inspect first, document why it's safe, move on.

**Assets are code too**: images, icons, fonts, sounds need the same treatment — one small reusable resolver that accepts a candidate set (per-platform, per-family fallback, default), caches the resolution, and never has a call site invent a fictitious "different" asset for a platform before real art actually exists for it (point the slot at the existing asset until it does).

## 3. Pillar 2 — Abstractionality: Base Unit → Specialization

**Rule**: never repeat a micro-interaction, confirmation wording, debouncing rule, or formatting/validation logic across more than one call site. The moment a *second* call site needs the same behavior as an existing one, that behavior graduates into a named unit:

```
Core Primitive → Base Unit → Domain Specialization A
                            → Domain Specialization B
```

**Concrete archetypes** (generalize the shape, not the names):
- Debounced input: raw text primitive → base unit adding debounced-event-triggering → specialization adding a clear button / direction-awareness / query formatting for search.
- Confirmations: platform-neutral modal-hosting shell → base "confirmation box" unit (title/message/primary/secondary/"remember my choice") → specializations with pre-baked wording for specific flows ("confirm exit", "confirm delete").
- Assets: base unit resolving+caching a platform-appropriate asset → specialization binding one specific asset to one specific use.
- Formatters/validators: one centralized implementation per concept, reused everywhere that concept is displayed — never five slightly different ad hoc versions.

**Catalog every unit** in one canonical document (mechanism, base type, purpose, status). This is the thing an audit or a new contributor reads *first* to avoid reinventing what already exists — see `primitives.md`.

**Scaffolds are debt with a name**: an empty/stub Base Unit is not neutral. Every call site currently bypassing it is an abstraction-break waiting to be found, because nobody can build on a stub, so they hand-roll instead. Finishing an unfinished Base Unit often has to happen *before* the duplication around it can even be fixed — see `primitives.md` for how to sequence this.

## 4. Pillar 3 — View/Layout Barrel for composite components

Primitive-level components (a button, an input) can often share one layout tree and just swap styling underneath. **Composite, block-level components and full screens cannot.** A dense desktop card and a compact mobile card are not the same layout tree with different styling — they need genuinely different structure and sometimes different interaction affordances (swipe-to-reveal vs. hover menu). Treating them as "one layout, some responsive tweaks" produces mediocre results everywhere at once.

**This applies to every composite/block-level component and page — not just primitives.** An audit that checked buttons and inputs but never checked cards/panels/pages hasn't finished; block-level components are exactly where the layout tree itself (not just styling) needs to differ.

Pattern:
```
Component/
├── Component.host        # thin container, no real layout of its own — resolves and renders...
└── layouts/
    ├── ComponentLayoutDesktop   # full-detail: dense grids, hover affordances
    └── ComponentLayoutMobile    # streamlined: only essential fields, touch affordances
```

Key discipline: the constrained-form-factor layout is allowed to show meaningfully *less* than the full layout. If a desktop card shows eight metadata fields and mobile only makes sense with two, the mobile layout should actually only implement those two — not a shrunk visual copy of everything.

Audit checklist per composite component/page:
- [ ] It's a thin host shell with zero real layout content of its own.
- [ ] A genuinely distinct layout exists (or is explicitly planned) per platform family that needs one.
- [ ] The constrained layout was designed for what that form factor needs, not derived by hiding/shrinking the full layout's elements.
- [ ] Data bindings, event routing, and test identifiers still function through the new indirection.

## 5. Full parity checklist — audit every dimension, not just API calls

A component can pass an "isolate the platform-only API calls" audit and still be quietly non-portable. Re-check every dimension per component:

- **Interaction model** — hover has no touch equivalent; design the touch-first equivalent for real (press/scale + haptics, long-press, tap-to-inspect), don't leave it blank.
- **Animation & motion** — does the animation mechanism exist and behave identically on every target? Does a reduced-motion preference resolve correctly per platform?
- **Styling/theming** — do visual tokens (color, radius, elevation, spacing) render identically across rendering engines?
- **Fonts, assets, density** — do custom fonts load the same way everywhere? Are assets provided at the densities each target needs?
- **Layout structure** — see Pillar 3; not just styling of the same tree.
- **Business logic/state** — byte-identical results regardless of platform, or does it secretly depend on a platform's locale/timezone/threading assumption?
- **Storage & security** — secure-storage mechanisms differ fundamentally per platform family; this is a Variant, never a Capability.
- **Background execution** — OS constraints on background work differ hugely; a "runs freely" assumption from one platform won't survive porting to a stricter one.
- **Navigation & lifecycle** — "suspended," "resumed," "back pressed" don't map 1:1 everywhere; audit lifecycle handling explicitly, not just visible UI.
