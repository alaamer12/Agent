# Composition and variants

When a component's final style = its own variants + whatever the caller adds + sometimes a parent
theme, three small jobs appear on every platform. Name them, and the framework-specific tools
become obvious instances rather than requirements. [Bracketed] tools are examples — a ten-line
local helper is frequently the right call over a dependency.

## Job 1 — Join: assemble a list from truthy parts

Call sites want `class={cx("btn", active && "btn--active", className)}` — conditional parts, no
stray spaces, caller's classes appended last. This is [clsx] / [cn]; in C# a
`string.Join(' ', parts.Where(p => !string.IsNullOrWhiteSpace(p)))` helper; in QML a small
function or just string concatenation with named pieces. Trivial, universal, worth having once
per project rather than inline-ternary spaghetti.

## Job 2 — Merge on conflict: later intent wins

Joins alone cannot express "everything from the component, except the caller wants `rounded-none`".
When utilities can conflict (two paddings, two colors), someone must decide the winner — normally
the caller. This is [tailwind-merge]-style: parse each class's property family, keep the last per
family.

Platform-neutral alternatives when you do not have a merge library:

- **Don't let utilities conflict:** your own system layer controls its utility set; a hand-rolled
  map of `prefix -> family` is enough for a curated vocabulary.
- **Tokens with local override:** caller sets a runtime variable (`--card-radius`), style layer
  consumes `var(--card-radius, default)` — conflict resolution by cascade, zero parsing. [CSS
  custom property fallbacks], [XAML dynamic resource shadowing at element scope].
- **Props into the variant system:** the component exposes the knob explicitly (`radius="none"`)
  mapped to a known class.

Merge-on-conflict is only needed **if** the system has overlapping arbitrary utilities. A token +
variant system can make this job vanish entirely — that is a design win, not a missing feature.

## Job 3 — Variant registry: one declaration of the style API

The component's visual contract — base, variants, sizes, defaults, composition — declared once:

```ts
// [CVA]-shaped: framework-free object, any joiner can consume it
const card = defineVariant({
  base: "card",
  variants: {
    tone:   { primary: "primary-card", secondary: "secondary-card" },
    padded: { true: "card-padded", false: "" },
  },
  defaultVariants: { tone: "primary", padded: true },
});
// usage: class={card({ tone })}
```

[tailwind-variants] adds composing several registries into one component; the concept generalizes
regardless of utility framework. What matters is the shape: **the style API is data, declared in
one place, typed exhaustively, and call sites pass intent.**

Non-web instances of the same contract:

- **Blazor:** parameters enum-typed, mapped to classes through Job 1 + the dictionary from
  reference 02; or an existing component library's `Class`/`Theme` parameters.
- **MAUI/WinUI:** the registry already exists in XAML — keyed `Style`s with `BasedOn` chains and
  `ControlTemplate`s per variant; `SetBinding`/implicit styles select by type. The skill's rule:
  variants are keyed styles in the module dictionary, not inline property dumps.
- **Qt/QML:** [Qt Quick Controls style/subtype mechanisms], a `Theme` singleton with role
  properties, or base component + variant wrappers using `inherit`. Property bindings select the
  variant name; visuals live in the style module.

## When composition becomes debt

- A component taking `class`, `style`, `sx`, *and* three style-override props: pick one override
  channel (usually: variant props for known choices, one pass-through for the escape hatch).
- Thirty variants for two real visual families: that is two components pretending to be one.
- Every call site overriding the same "default": the default is wrong — change it once in the
  registry, delete forty overrides.

## Checklist per component

- [ ] Its visual choices are declared once (registry / keyed styles / variant map), not re-spelled
      at call sites
- [ ] Call sites pass intent (names), never values or fragments
- [ ] A caller override has exactly one sanctioned channel
- [ ] Conflict resolution is by cascade/variables or a merge helper — whichever the system needs,
      chosen once per project
