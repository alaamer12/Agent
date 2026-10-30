# Universal Guideline: Cross-Platformality & Abstractionality for Any Multi-Platform Codebase

> **How to use this document**: This is a language- and framework-agnostic engineering standard. It uses pseudo-syntax, not any specific language's syntax — apply the *concepts* using whatever your stack's real mechanisms are (file suffixes, build-target conditionals, dependency injection, module systems, etc.). It is meant to be handed to an agent working on *any* codebase — web, mobile, desktop, embedded, game engine — as long as that codebase targets more than one runtime/OS/form-factor from one shared source.

---

## 0. The Two Diseases This Guideline Cures

Every long-lived multi-platform codebase rots in exactly two ways. Name them, and an agent can find and fix them without further explanation:

1. **Cross-Platformality Breaks** — code that lives in a "shared" location (used by every platform) but secretly only works correctly on the platform it was first written for. It doesn't crash loudly; it just silently assumes a capability, API, or behavior that isn't universal. The danger sign is not "this file is wrong" — it's "this file *lied about being shared*."
2. **Abstractionality Breaks** — behavior or UI logic that is duplicated, hand-rolled, or reinvented per call-site instead of being promoted to a single, named, reusable unit. The danger sign is not "this code is ugly" — it's "two places in the app now disagree about how the same concept should behave, and nobody decided that on purpose."

A "perfect" multi-platform codebase eliminates both diseases *and* keeps them from coming back. Elimination without prevention is not done — it regresses the moment someone adds a feature under time pressure.

---

## 1. Diagnostic Vocabulary (define these before auditing anything)

| Term | Definition |
|---|---|
| **Platform** | A concrete target the app ships to (e.g. "Desktop-OS-A", "Mobile-OS-B", "Mobile-OS-C", "Web", "Console"). Fixed for the lifetime of a running process — an instance never "becomes" another platform mid-run, so platform identity should be read once and treated as a constant, not re-detected repeatedly. |
| **Platform Family** | A group of platforms that plausibly share the *same* answer for a given concern (e.g. "the two touch-based mobile platforms" as a family distinct from "the mouse-and-keyboard desktop platforms"). Families are a judgment call per-concern, not a fixed taxonomy — "touch-capable" is a family for input handling but may be irrelevant for storage encryption. |
| **Capability** | Something the app can *optionally* do, which some platforms support and others don't at all (system tray icon, background execution mode, biometric prompt, haptic feedback, file-system-level reveal-in-explorer). A capability's defining trait: on unsupported platforms, the correct answer is "nothing" (null/no-op), not "a worse implementation of the same thing." |
| **Variant** | Something every platform *must* do, but differently (send a notification, persist a secret, resolve an image, lay out a screen). A variant's defining trait: every platform has a real implementation; only the mechanism differs. |
| **Base Unit** | A named, documented, reusable building block encoding one micro-behavior (a debounced text field, a confirmation dialog, a formatted timestamp). |
| **Specialization** | A named, documented unit that composes/configures a Base Unit for one concrete use case, without re-implementing the Base Unit's logic (e.g. Base Unit = generic confirmation dialog; Specialization = the specific "confirm exit" dialog with its own wording and result-mapping). |
| **Barrel** | A thin, platform-neutral entry point (a file, module, or class) that contains *zero* platform-conditional logic itself and simply routes to the correct per-platform implementation. The barrel is where "which platform am I" gets asked; nowhere else should ask it. |

---

## 2. Pillar 1 — Cross-Platformality: The File/Module-Separation Principle

### 2.1 The one legal way to express platform variance

Platform variance must be resolved at the **file/module boundary**, never by a conditional branch *inside* a shared file's body. Concretely, for any unit `Thing` that varies by platform:

```
Thing/
├── Thing.core                 # Shared, platform-neutral shell: public API, shared logic, NO platform conditionals
├── Thing.platformA            # Platform A's real implementation
├── Thing.platformB            # Platform B's real implementation
├── _Thing.familyX             # Logic shared by an entire family (e.g. "touch platforms"), NOT platform-neutral —
│                               #   exported/re-used by two or more per-platform files below
├── Thing.platformC            # exports/re-uses _Thing.familyX verbatim (platform C belongs to family X)
└── Thing.platformD            # exports/re-uses _Thing.familyX verbatim (platform D also belongs to family X)
```

Rules that make this work:
- **The shared shell (`Thing.core`) contains zero platform-conditional branches.** If you find yourself wanting an `if platform == X` inside the shared file, that's the signal to split a new per-platform file instead.
- **A per-platform file whose logic is identical to another platform's does not get re-written — it exports the shared family file.** Two mobile platforms with the same touch-gesture behavior both point at one `_Thing.mobile` file; they don't duplicate the logic twice, and they don't get force-merged into one file either (each platform still needs its own file so the build only compiles what that target needs).
- **The build/compile configuration must actually exclude non-matching platform files from non-matching targets.** This is not automatic in most toolchains — verify explicitly, because a leaked platform-only file compiling into the wrong target is a silent, deferred failure (it may just be unreachable dead code — or it may crash at runtime the first time it's touched, or fail to compile on a target that lacks the referenced platform API entirely).
- **Only ONE canonical location in the whole codebase is allowed to contain the actual "which platform is this" conditional/switch.** Everything else — every capability map, every barrel, every audit — reads from that single canonical accessor. It should be treated as immutable law: if you `grep`/search the entire codebase for the platform-conditional syntax your language uses, the *only* hits should be that one canonical file (plus, if your compile-time-selection helper described in §2.2 is itself implemented with a native conditional, that helper file too — nothing else).

### 2.2 Compile-time/build-time value selection helper

For resolving a *single value, constant, or factory* per platform without runtime branching cost, provide one small, reusable, generic helper. Pseudocode:

```
function PlatformSelect<T>(valueForPlatformA, valueForPlatformB, valueForFamilyX, valueForDefault) -> T:
    # Resolved at compile-time/build-time for the actual target, not evaluated at runtime as an if/else chain.
    # Family-level values are a fallback beneath platform-specific ones:
    #   platform-specific value, if given, wins;
    #   otherwise the family-level value, if given;
    #   otherwise the default.
```

This is the tool every capability map, every barrel, and every "which layout do I load" decision should route through — never a hand-rolled conditional at the call site.

### 2.3 Capability mapping helper (the "this doesn't exist on that platform" case)

Capabilities (§1) need an explicit, typed way to say "unsupported here" instead of every call site null-checking, catching an exception, or silently no-op-ing by accident. Pseudocode:

```
type Capability<T>:
    value: T or null
    is_supported: bool  # true iff value != null

    static function ForPlatforms(platformA_factory?, platformB_factory?, ..., default_factory?) -> Capability<T>:
        # Resolves the current platform's factory (if any), constructs it, wraps as Capability<T>.
        # Platforms with no factory given resolve to Capability<T>(null) — "not supported" is a first-class
        # outcome of this call, not an omission a caller has to remember to defend against.
```

Every call site then reads `capability.is_supported` / uses `capability.value` — never `if platform == X then call native API`.

**Anti-pattern to actively hunt for**: a capability being called *unconditionally*, as if every platform supported it, with the unsupported-platform behavior being an accidental crash, a silent no-op nobody decided on purpose, or (worse) a stub implementation on the wrong platform that half-works. If you find a capability like this, it needs a `Capability<T>` map, even if today only one platform actually exists.

### 2.4 Two shapes that a single-value selector does NOT cover — watch for these

Real codebases eventually need platform variance in shapes beyond "one value/factory." Two extremely common ones, and their fix:

**(a) A shared module/class with several interdependent operations, only some of which vary per platform.**
Wrong: a single `Thing` module where each method internally branches on platform.
Right: convert `Thing` into a shared shell with per-platform files that each supply the platform-specific operations, following §2.1's split — i.e. generalize the base file-splitting convention to modules with multiple members, not just single functions. If your language's per-platform files need to supply a *return value* (not just a side-effecting void), give the shared shell a "try" shape (e.g. `try_get_platform_result(...) -> (found: bool, result: T)`) so a platform with no answer yet can return "not found" safely rather than being forced to fabricate a value.

**(b) Startup/bootstrap/dependency-wiring code with several small platform-only side effects.**
Wrong: the app's composition root (wherever services get registered, wherever the app window/lifecycle gets configured) sprinkled with several separate inline platform-conditional blocks, each doing one small Windows/mobile/desktop-only thing (adjusting a window chrome height, suppressing a native scrollbar, wiring a tray icon, registering a platform-only service).
Right: extract each platform-only side effect into a named method on a small platform-only "startup hooks" object, resolved once via the capability map from §2.3, and have the composition root call `hooks?.DoTheThing()` — one line, no inline conditional, no platform knowledge in the composition root itself.

### 2.5 The standing self-check (make regressions loud, not silent)

Codify a rule your team/agent can mechanically verify at any time:
> "No file's body may contain a native platform-conditional/branch, except the one canonical platform-identity file (§2.1) and the compile-time selector helper itself (§2.2), if that helper's own internals require one."

Provide the exact search command for your language/toolchain (e.g. a grep for the platform-conditional syntax across all source files) as a one-line, repeatable check. Run it:
- once, at the start of any audit, to get a ground-truth violation count — don't trust a stale count from a previous session;
- after every single file split during a refactor (not batched at the end) — a broken build should be traceable to the one most recent change;
- as a standing CI/lint check going forward, so this class of regression can't reappear silently.

**Caution against over-correction**: not every file that *originated* from a platform-specific bug workaround needs a file split. Inspect first. If the resulting implementation has no actual platform-conditional branch left in it (e.g. a workaround that turned out to use a fully cross-platform mechanism once written), leave it in the shared file and document *why* it's safe, so a future audit doesn't re-flag it. Splitting files that don't need splitting adds churn without reducing risk.

### 2.6 Asset/resource variance (images, icons, fonts, sounds — not just code)

The same discipline applies to non-code assets. Provide one small reusable unit (mirroring §2.2/§2.3's shape) that:
- lets a call site declare a *set* of candidate assets (one per platform, plus family-level fallbacks, plus a default),
- resolves once and **caches/memoizes** the resolved choice per instance so re-layout, re-render, or repeated access never re-resolves needlessly,
- follows the same family-sharing convention as code (§2.1) — one shared "mobile" asset property instead of duplicating the same asset reference twice.

**Do not invent fictitious per-platform assets that don't exist yet.** If platform B has no distinct art yet, point its slot at the same asset platform A uses, and revisit only once real platform-specific art exists. Guessing at a "different" version prematurely creates false confidence and wasted work.

### 2.7 Full parity checklist — audit *every* dimension, not just API calls

A component can pass an "isolate the platform-only API calls" audit and still be quietly non-portable. Explicitly re-check every one of these dimensions per component, not just once at the project level:

- **Interaction model**: hover/pointer-based interactions have no equivalent on touch — a touch-first equivalent (press/scale feedback, haptics, long-press instead of hover, tap-to-inspect instead of hover-tooltip) needs its own real design, not a blank/no-op.
- **Animation & motion**: does the animation driver/mechanism used actually exist and behave the same on every target? A reduced-motion/accessibility preference should also resolve per-platform correctly, not just per one platform's OS setting.
- **Styling & theming**: do visual tokens (colors, radii, elevation/shadow, spacing) render identically, or does one platform's rendering engine interpret them differently?
- **Fonts, assets, and density**: do custom fonts load the same way on every target? Are image/icon assets provided at the resolutions/densities each target actually needs?
- **Layout structure itself** (see Pillar 3 below) — not just styling of the same layout, but whether the same layout tree is even appropriate for every form factor.
- **Business logic and state**: does a service, formatter, or validator produce byte-identical results regardless of platform, or does it accidentally depend on a platform-specific locale/timezone/threading assumption?
- **Storage & security**: secure-storage mechanisms differ fundamentally per platform family (OS-level credential vaults are not interchangeable) — this is a Variant (§1), not a Capability; every platform needs a *real* answer, never a null.
- **Background execution**: platform OSes impose very different constraints on background work; a "runs a background loop freely" assumption from one platform will not survive porting to a more restrictive one.
- **Navigation & app lifecycle**: hooks like "app suspended," "app resumed," "back button pressed" don't have 1:1 equivalents everywhere — audit lifecycle event handling explicitly, not just visible UI.

---

## 3. Pillar 2 — Abstractionality: The Base Unit → Specialization Hierarchy

### 3.1 The rule

Never repeat a micro-interaction, confirmation wording, input-debouncing rule, or formatting/validation logic across more than one call site. The very first time a second call site needs the *same* behavior as an existing one, that behavior graduates into a named unit:

```
Core Primitive → Base Unit → Domain Specialization A
                            → Domain Specialization B
```

### 3.2 Concrete archetypes (generalize the shape, not the names)

- **Debounced input**: a raw text-input primitive → a base unit that adds debounced-event-triggering → a domain specialization that adds a clear button, direction-awareness, and query formatting for one specific use (e.g. search).
- **Modal/dialog confirmations**: a platform-neutral modal-hosting shell (routes to whatever the native "modal/sheet/dialog" mechanism is per platform) → a base "confirmation box" unit (title, message, primary/secondary action, optional "remember my choice") → domain specializations with pre-baked wording/behavior for specific flows (e.g. "confirm exit," "confirm delete").
- **Asset resolution**: a base unit resolving a platform-appropriate asset with caching (§2.6) → a domain specialization binding a specific asset per specific use (e.g. one particular onboarding step's illustration).
- **Formatters/utilities**: a single, centralized formatter/parser for one concept (currency, relative time, tag/skill formatting) reused everywhere that concept is displayed, instead of five slightly-different ad hoc implementations scattered across screens.

### 3.3 Catalog every unit

Maintain one canonical document listing every Base Unit and Specialization: its mechanism, its base type/parent, its purpose, and its current status (implemented / scaffold / planned). This document is not optional documentation-for-documentation's-sake — it's the thing an audit or a new contributor reads *first* to avoid reinventing something that already exists. Update it the moment any unit's file layout, status, or shape changes — not in a later cleanup pass.

### 3.4 Scaffolds are technical debt with a name

If a "concept" unit exists only as an empty stub (e.g. returns an empty/no-op view, or throws "not implemented"), it is not neutral — every call site currently bypassing it is a *guaranteed* abstraction-break waiting to be found, because nobody can build on a stub, so they hand-roll instead. Treat unfinished Base Units as a leading indicator of where duplication is hiding, and prioritize finishing them before auditing for duplication elsewhere.

---

## 4. Pillar 3 — View/Layout Barrel Swapping for Composite Components

### 4.1 The problem this solves

Small, primitive-level components (a button, an input field, a toggle) can often share one layout tree across platforms and just swap styling/behavior underneath. **Composite, block-level components and full screens cannot.** A information-dense desktop card and a compact mobile card are not the same layout tree with different CSS — they need genuinely different structure, different information density, and sometimes entirely different interaction affordances (e.g. swipe-to-reveal on mobile vs. a hover menu on desktop). Treating them as "one layout, some responsive tweaks" produces a UI that's mediocre on every platform simultaneously.

**This applies to every composite/block-level component in the app, not just primitives.** An audit that verified primitives (buttons, inputs) got proper per-platform treatment but never checked block-level components (cards, dashboard panels, full pages) has not actually finished — block components are exactly where the *layout tree itself*, not just styling, needs to differ.

### 4.2 The pattern

Decouple every composite component into a thin **host shell** that resolves which concrete layout to render, plus one implementation file per distinct layout need:

```
Component/
├── Component.host              # Thin container: no real layout of its own, just resolves and renders...
└── layouts/
    ├── ComponentLayoutDesktop   # Full-detail layout: dense grids, multi-column, hover affordances
    └── ComponentLayoutMobile    # Streamlined layout: single-column, only the essential fields, touch affordances
```

Pseudocode for the host shell:

```
class Component.host:
    on_construct():
        self.content = PlatformSelect(
            platform_desktop_family: () => new ComponentLayoutDesktop(),
            platform_mobile_family:  () => new ComponentLayoutMobile(),
        )()
```

The key discipline: **the mobile layout is allowed to show meaningfully less than the desktop layout.** If a desktop card shows eight pieces of metadata and the mobile equivalent only makes sense with two (say, title and one status line), the mobile layout should *actually* only implement those two — it should not try to cram everything in, and it should not be a scaled-down visual copy of the desktop tree. The host-shell + swap-by-platform-family mechanism should be "plug and play" enough that adding a genuinely different mobile layout is a matter of writing one new layout file and wiring it into the existing selector — not a rearchitecture.

### 4.3 Audit checklist for this pillar specifically

For every composite/block-level component and every full screen/page in the app, confirm:
- [ ] It is a thin host shell with zero real layout content of its own.
- [ ] A genuinely distinct layout exists (or is explicitly planned) per platform family that needs one — not a shared layout wearing different stylesheets.
- [ ] The mobile (or other constrained-form-factor) layout was designed for what that form factor actually needs, not derived by hiding/shrinking the desktop layout's elements.
- [ ] Data bindings, event routing, and any automation/test identifiers still function correctly through the new indirection layer.

---

## 5. Full Cross-Platform Parity Reference Matrix (template — fill in per project)

When porting or auditing, walk every subsystem through this table. It forces the question "what is the OTHER platform's real answer here?" instead of leaving it implicit.

| Subsystem | Platform-A-first assumption (example) | Other-platform native equivalent (example) | Architectural resolution |
|---|---|---|---|
| Interactivity | Pointer hover, cursor change | Touch press/scale feedback + haptics | Per-platform file pair, §2.1 |
| Diagnostics/inspection overlays | Hover tooltip | Tap-to-inspect gesture + popup | Platform-specific gesture recognizer |
| Secure storage | OS-level desktop credential vault | OS-level mobile keystore/keychain | Variant (§1) — real impl per platform, never null |
| Navigation | Persistent sidebar rail | Bottom tab bar / drawer + safe-area insets | Barrel-resolved navigation concept |
| Search/query | Full-text search engine on desktop filesystem | Same engine, mobile app-sandboxed storage path | Shared engine, platform-specific storage path only |
| Background work | Unrestricted background thread | OS-managed background task/work-scheduler API | Platform-specific worker registration behind a shared interface |
| Notifications | Native desktop toast API | Native mobile local/push notification API | Variant — shared sender interface, real impl per platform |
| Capability-only feature | System tray icon | *(no equivalent — intentionally null)* | Capability map (§2.3) |
| Authentication | Native browser / manual cookie entry | In-app web-view session capture | Platform-appropriate secure flow, shared session contract |

Build your own matrix; the point is the exercise, not this specific table.

---

## 6. Execution Framework for an Agent (or team) Running This Refactor

### 6.1 Audit before you touch anything

- Run a full, live scan for the standing self-check pattern (§2.5) — don't rely on a stale count from a previous pass.
- Classify every hit into: **real violation** (mixed-concern file/module) / **already clean** (superficially suspicious but no actual branch — document why, don't touch) / **canonical-exempt** (the one legal platform-identity file, plus the selector helper if applicable).
- Write findings incrementally, as discovered — each with a concrete file reference, a one-line description, and a suggested fix — not batched at the end of the scan. This lets triage start before the scan finishes, and lets independent scans of overlapping areas cross-check each other.
- If splitting audit work across multiple parallel scans (e.g. one scan for cross-platformality breaks, one for abstractionality breaks), keep each scan's ownership area distinct enough to avoid wasted duplicate effort, while allowing deliberate overlap at the boundaries for cross-checking.
- Once the violation surface is small enough to be reasonably enumerable in one pass, a single thorough audit is more efficient than many parallel agents — match audit scale to actual surface size, not a fixed process.

### 6.2 Consolidate and prioritize

- Merge all findings into one deduplicated backlog.
- Prioritize whatever the requester explicitly called out first, then anything else surfaced that shares the same root cause (e.g. if "notifications" was called out as an example, treat every other capability/variant with the same shape as equally in-scope, not as a separate lower-priority request).

### 6.3 Execute stage by stage, verify constantly

- Fix one violation group at a time; **build/verify after every single change**, not batched at the end — a broken build should always be traceable to the one most recent, smallest change.
- Every refactor in this class should be a pure code-motion/restructuring change, not a behavior rewrite. Zero behavior change on the platform(s) that already work is the hard constraint; new platforms are allowed to keep existing safe-default/no-op/placeholder behavior — this refactor makes the codebase *ready* to receive real new-platform implementations, it does not have to build them.
- Where delegating stages to a subagent, give it the full relevant context (the exact violation, the target file layout convention, the relevant standing documentation) and treat its output as something to *review*, not something to trust on self-report — verify the build and re-check that no disallowed pattern remains before accepting a stage as done.

### 6.4 Close the loop — update the standing documentation

- Update the unit catalog (§3.3) for every unit whose status or file layout changed.
- Update the architectural conventions document itself with any new pattern this refactor introduced (a new toolkit shape from §2.4, a new capability, a new base unit) — including concrete before/after examples from the actual refactor, so the convention isn't just an abstract rule.
- Re-verify that any *existing* documentation describing project structure/layout still matches reality after the refactor — stale structure docs are exactly what lets violations regress silently, because a new contributor trusts the doc over the live tree.
- Do a final full-repo self-check (§2.5) and confirm the exemption list is exactly what it should be — no more, no less.

### 6.5 When in doubt, verify against current best practice

Before finalizing any new cross-platform pattern, check current official guidance for your actual framework/toolchain (multi-targeting conventions, resource/asset pipelines, background-execution APIs) — don't assume last year's approach is still the recommended one, and don't reinvent something the framework's own tooling already solves natively (e.g. don't build a custom density-scaling system if the framework's asset pipeline already handles simple DPI variance — reserve custom systems for *compositionally* different assets, not just resolution variance).

---

## 7. Anti-Pattern Quick Reference

| Anti-pattern | Why it's a violation | Fix |
|---|---|---|
| A file outside the one canonical platform-identity location contains a native platform-conditional branch | Mixed concern — can't be A/B toggled per platform without editing shared source; unclear compile scope | Split into shell + per-platform files (§2.1) |
| A capability is called unconditionally, crashing/no-op-ing by accident on unsupported platforms | No decision was made about "not supported" — it's an accident | Wrap in a Capability map (§2.3) |
| Two call sites hand-roll the same confirmation/debounce/formatting logic slightly differently | Behavior drift nobody decided on purpose | Promote to a Base Unit / Specialization (§3) |
| A block-level component only has platform-specific *styling*, not a platform-specific *layout structure* | Desktop information density forced onto a small screen (or vice versa) | View Barrel split (§4) |
| A "fixed" unit still has an internal `if platform==X / else` even though it's file-suffix-named for one platform | The suffix is decorative, not structural — regression waiting to be missed | Actually move the logic out; re-run the self-check |
| New per-platform assets invented speculatively before real design exists for them | False confidence, wasted work, guesswork baked into the codebase | Point unresolved platform slots at the existing asset until real art exists (§2.6) |
| A file gets split into `.PlatformX` purely because its *history* involved a platform-specific bug, even though the final code has no actual branch | Unnecessary churn, no risk reduction | Inspect first; only split where a real branch exists (§2.5) |
| Composite component audited for primitives (button/input) but never for block-level components (cards/pages) | The layout-tree problem (§4) is exactly where it hides | Explicitly re-audit every block-level component and page, not just primitives |
