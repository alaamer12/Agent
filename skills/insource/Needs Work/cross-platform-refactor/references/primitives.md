# Primitives: Inventory, Gaps, and the "Build It First" Phase

This refactor's Pillar 2 (`principles.md` §3) assumes a chain already exists:

```
Core Primitive → Base Unit → Domain Specialization
```

**That assumption is frequently false.** A codebase asked to "get a search field that debounces and matches our confirm-dialog pattern" often has none of the three tiers actually built — or has a Base Unit but no primitive underneath it, or has a primitive that's *almost* right but is missing one hook the refactor needs. Skipping the gap check and jumping straight to writing the specialization is the single most common way this kind of refactor makes things worse: whoever hits the gap first, under time pressure, hand-rolls something one-off — which is exactly the abstraction-break this whole exercise exists to prevent.

## Table of contents
1. The three tiers, defined precisely
2. Gap-inventory procedure (do this before planning any specialization work)
3. Deciding: use as-is / extend / create new
4. Scoping a "create or extend the primitive" phase correctly
5. Worked example

---

## 1. The three tiers, defined precisely

- **Core Primitive**: the lowest-level reusable UI/logic element — a themed text input, a themed button, a raw timer/scheduler, a raw modal-hosting mechanism. It knows nothing about the *domain* (it doesn't know what "search" or "exit confirmation" means) but it does know the platform-neutral theming/behavior contract everything above it builds on.
- **Base Unit**: composes one or more primitives to add one specific, reusable *behavior* — debouncing, confirmation semantics, asset resolution with caching. Still domain-agnostic.
- **Specialization**: configures a Base Unit for exactly one concrete use case in the app's actual domain — wording, icons, which fields it exposes, what happens on confirm/cancel.

The tiering matters because **a violation at the wrong tier gets fixed in the wrong place otherwise.** If "our search box on mobile doesn't debounce properly" turns out to be a missing capability in the *primitive* text input (it doesn't expose a stable enough change-event to debounce cleanly), patching it inside the `SearchInputField` specialization only hides the problem — the next specialization that needs debounced input hits the same wall.

## 2. Gap-inventory procedure (do this before planning any specialization work)

For every Base Unit or Specialization the refactor plan calls for:

1. **Check the existing unit catalog first** (`principles.md` §3's "catalog every unit" — if the project has no such catalog yet, creating one is itself a Step-1 task, not optional busywork; you cannot do an honest gap check against an undocumented set of components).
2. **If a name matches, verify it actually still does what's needed** — a Base Unit that exists but is a stub/scaffold (returns nothing, throws "not implemented", or was clearly built for a narrower case) counts as **missing**, not present. Don't let a matching name give false confidence.
3. **If no matching unit exists, check one tier down** — is there at least a Core Primitive this Base Unit could be built on, or is that missing too? Gaps often cascade; find the bottom of the gap before scoping the fix, not just the first missing tier you notice.
4. **Record each gap explicitly** in the same findings list as the cross-platformality/abstractionality violations (Step 2 of the main `SKILL.md` workflow) — a missing primitive is a finding with the same status as a leaky file, not a footnote.

## 3. Deciding: use as-is / extend / create new

For each gap found:

- **Use as-is** — the primitive/Base Unit exists and genuinely covers the need. Proceed straight to the specialization.
- **Extend** — the primitive/Base Unit exists and is *structurally* right, but is missing one hook, prop, or event the new specialization needs (e.g. a `DebouncedEntry` exists but has no `onDebouncedChange` the way a `SearchInputField` would need — only a raw `onChange`). Extending means adding the missing surface to the existing unit **without breaking any current consumer of it** — treat every existing call site of that unit as a regression check, not just the new one you're adding.
- **Create new** — nothing at the right tier exists. Build the missing tier(s) from the bottom up (primitive before Base Unit, if both are missing), following whatever this project's existing primitives already establish as its visual/behavioral conventions — a new primitive should look like it was always part of the same family, not like a one-off import from a different design system.

**A common trap**: treating "extend" as "add a special case just for me." If the new requirement is genuinely specific to one specialization, it doesn't belong on the shared Base Unit at all — it belongs entirely inside the specialization, composing the existing unit unchanged. Only extend the shared unit when the new capability is something *other* future specializations would plausibly also need.

## 4. Scoping a "create or extend the primitive" phase correctly

When the refactor plan needs to include primitive/Base Unit work, scope it as its own phase, sequenced **before** the specializations that depend on it — and keep it appropriately narrow:

**Include**:
- The minimum surface (props/hooks/events/theming tokens) the currently-known specializations actually need.
- Whatever the project's existing primitives already do for cross-platform correctness (if every other primitive resolves its own platform-specific styling via the project's select-helper, the new one should too — don't introduce a second convention).
- Accessibility basics consistent with the project's other primitives (focus handling, labels) if that's an established convention — don't skip it just because it's "just a primitive," but also don't invent a new accessibility standard for one primitive that the rest of the codebase doesn't follow.

**Explicitly exclude** (resist scope creep here — this is the second most common way this phase goes wrong):
- Speculative props/variants for specializations nobody has asked for yet ("while I'm in here, let me also support X in case we need it later"). Add them when a real specialization needs them, following the same "second call site graduates it" rule from Pillar 2.
- Visual redesign of unrelated existing primitives, even if you notice they're inconsistent with the new one, unless that inconsistency is itself blocking the current refactor. File it as a separate finding instead.
- Business/domain logic of any kind — if you find yourself writing domain-specific wording, validation rules, or API calls inside what's supposed to be a Core Primitive or Base Unit, that content belongs in the Specialization tier instead; move it there before finishing this phase, don't ship it misplaced and fix it later.

## 5. Worked example

**Requirement surfaced during audit**: "Notifications settings screen needs a search field for filtering notification types, matching the existing search pattern used elsewhere."

1. **Catalog check**: `UNITS.md` lists `DebouncedEntry` (Base Unit, status: implemented) and `SearchInputField` (Specialization, status: implemented, used on the Projects screen).
2. **Verify it still does what's needed**: `SearchInputField` takes a static placeholder string and a fixed icon — fine. Check `DebouncedEntry` underneath it: it hard-codes a 300ms debounce with no way to override it. The new screen needs 150ms because the filtered list is small and users expect near-instant feedback.
3. **Classify**: this is an **extend**, not a create-new — `DebouncedEntry` is structurally right, just missing one prop.
4. **Scope the extension phase**: add an optional `debounceMs` prop to `DebouncedEntry` defaulting to the existing 300ms (so the Projects screen's current call site is unaffected — verify this explicitly, don't just assume), thread it through `SearchInputField` as an optional pass-through prop. Nothing else. No redesign of `DebouncedEntry`'s styling, no new debounce *strategy* system, no speculative props for hypothetical future screens.
5. **Then**, and only then, build the actual notifications-search specialization call site, now that the unit underneath it genuinely supports what it needs.

This is the sequencing every "create or extend" phase should follow: catalog → verify → classify → scope narrowly → build the dependency → build the thing that depends on it. Doing the last step first is what produces a duplicated, one-off search field living outside the Base Unit system — the exact defect this refactor exists to eliminate.
