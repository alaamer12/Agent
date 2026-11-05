# The layer chain and expressive naming

The chain idea generalized from a component doctrine (`<base> → <adaptive> → <component> →
<specialised>`) and a production SCSS system — applied to styling on any stack. **The number of
layers is not the doctrine; the direction is.** How many tiers exist, what they are called, and
what each may import is decided by the project and its author. [Bracketed] shapes are examples.

## The invariant: knowledge-ordered layers, downward-only imports

Every style artifact answers exactly one question, and may consume only the layer immediately
below it:

| Layer (role) | Question it answers | Example mechanisms |
|---|---|---|
| **Values** | what raw literals exist | [`$values` map / single SCSS file], [token JSON], one file where every hex/number lives |
| **Compiled tokens** | how the runtime sees them | [SCSS `@function space()`/`chrome()` + a `tokens-root` file emitting `:root { --x }`], [CSS theme file], [XAML `ResourceDictionary` generated from source], the **one-time** bridge to platform variables (`--ion-*`, system colors) |
| **Vocabulary** | what patterns exist | [token-alias `$ink: var(--mt-ink)`], [@mixin truncate-lines / @mixin card], [functions that compute from tokens], code-level helpers ([cn/clsx joiners], small variant mappers) |
| **Composed styles** | what this thing in this context means | expressive named classes/variants: `payment-card`, `stats-card`, keyed XAML styles with `BasedOn`, QML variant types using `inherit` |
| **Module scope** | what this one page needs privately | [Vue `<style scoped>`], [Blazor `.razor.css`], [page-local stylesheet], per-module QML |

Hard rules, any count of layers:

1. **Imports point downward only and never skip.** A composed style importing the values file, or
   a page reaching past the vocabulary layer for a raw literal, is a defect even when it "only
   needs one small thing."
2. **The compiled-token layer is imported exactly once**, at the document/app root; everything
   above it consumes the *names*, never re-emits values. (Real-world evidence: a `tokens-root.scss`
   with a header comment "Component styles must never @use this file", imported once by
   `global.scss`.)
3. **Literals exist in one place only.** Guard it mechanically ([stylelint no-color-literals],
   [analyzers], [a grep gate in CI]) — a rule without a failing check is a suggestion.
4. **Framework token bridges go one way:** own tokens → platform variables (`--ion-color-*`,
   system brushes), never the reverse, so a framework upgrade touches the bridge only.
5. **The count belongs to the project.** Two layers in a toy app, five in a documented design
   system: read the existing chain (folder order, `@use`/`using`/import graph) before adding a
   file, and slot new work into the layer whose question it answers. Where the project has
   *services* or modules with declared purposes, styling joins as another named layer, not as a
   side channel. The same law places the folders: ONE styling root whose NAME comes from the
   project's incumbent location first, the framework's idiom second ([styles], [css], [themes],
   [resources], co-located files - `styles` is an example, never a default this skill imposes),
   and layer names that speak their concern (values, tokens, skins, modules) —
   never a directory named after the styling language (`[sass]/` under any root): one project, one
   styling system, the extension speaks it.

## The topmost layer is style-free

The enterprise pattern that makes the whole chain readable from the top down: **screens/pages are
thin builder-wrapper layers with zero styling.** Not "minimal" — zero: no style block, no class
tweaks, no token references, sometimes no class attribute at all. A real production app's pages
all scored zero on style-blocks/`@use`/`var(--`/hex greps; the only exception was a boot gate, and
even there the styling belonged to a shell, not a page.

Why it matters more than it looks:

- The page becomes a **table of contents of intent**: `<VideoSlide :item> <ActionRail :actions>` —
  a reviewer sees what the screen *does*, and every *looks* decision is addressable at exactly one
  place below.
- Any styling need surfacing at a page is a **routing signal**, not a task: it means a component
  variant is missing (extend it) or a shared pattern was never named (lift it). Pages never fix
  looks locally.
- It is the cheapest possible guardrail: a grep for style syntax in the pages directory must
  return nothing, and CI can enforce that with one rule.

## Variants can do the work of layering

A project does not owe you a five-layer stylesheet chain. A legitimate compression, observed in
production: the adaptive/component skin exposes **a closed, documented variant set as its only
styling surface**, and the guardrails make that enough:

```text
variant?: "cta" | "link" | "icon" | "circle" | "row" | ...   // closed union
:class="`skin--${variant}`"                                  // inside the skin that DEFINES
                                                             // every member's rule
"A missing variant is a defect HERE — extend it, never bypass it."
```

Every union member has its modifier defined in the same file, each variant justified by a named
spec or mockup, and runtime numbers still enter as local custom properties (`--hit-box: 40px` set
inline, consumed by the rule). With those pieces in place the project may skip strict
values→tokens→mixins→variants file separation — the **variant contract carries the discipline**.

Recognize it as valid because of the guardrails, not the shape:

1. The variant set is **closed** (a type union, a keyed-style list, a registry object) — an
   arbitrary class/string prop is not a variant system.
2. **Consumers may only pick names**; there is a stated or linted ban on re-skining in place.
3. **Extension happens in the owning layer** — a new need becomes a new variant (justified by the
   system spec or a real design), never a call-site override.
4. Interpolation is legal **only inside the layer that defines the names** — `skin--${variant}`
   where every member's rule lives beside the union is *selection*; at a call site over token
   fragments (`bg-${x}-500`) it is the banned construction from `02-conditional-and-runtime.md`.

So when entering a project: read what carries the single-source-of-truth promise — a file chain,
a variant contract, or both — and adopt that. Do not bolt a second mechanism onto a project whose
guardrails already hold, and do not accept a "variants" prop that is secretly a free-form class
escape hatch; that is the chain with the wall removed.

## Gap handling: extend the layer, never bypass it (OCP for styles)

When a screen needs a look the vocabulary/composed layer cannot express, three temptations are
wrong (local override stacks, copied-and-tweaked files, direct framework/base imports) and one is
right:

```text
Need differs from what the shared layers offer…
├─ meaning is shared with existing consumers?  → extend the layer: new named variant,
│                                                 everyone inherits it for free
├─ one-property delta, one module, meaning intact? → module-local rule is honest, keep it private
└─ delta changes the MEANING of the base name?  → it is not a variant of that base;
                                                  give it its own expressive name
```

The gate against bloating the shared layer: a new shared name is justified when its meaning (not
just its pixels) will be reused. Same skin twice is acceptable; same *knowledge* twice is not.

## The ambiguity trap — expressive names over convenient ones

The failure this whole reference exists to warn about, because the structure alone does not
prevent it:

> A generic name gets reused for things that mean different things. `card` is applied to a
> payment card, a stats card, a media card; each consumer then patches it with overrides or
> inline tweaks. `card` now means five things; changing "the card" changes all of them or none;
> the design system is a suggestion again.

Rules:

- **A base utility may be thin and generic** — `card` = radius + surface + border is a fine
  shared floor. Expressiveness is required where *meaning* diverges, not at every layer.
- **Name test:** does the class name read honestly in the requirement sentence? "The payment
  card shows the last four digits" → `payment-card` exists or the meaning is already carried.
  If two consumers would describe the same class with different nouns, the name is ambiguous.
- **`payment-card` / `stats-card` layers are chosen, not mandated.** Create them when their
  deltas accumulate or their meanings matter to the design contract; when the only difference is
  one property, the honest options are a small module-local rule (meaning intact) or a parameter
  that names the intent — **not** call-site override scatter.
- **Never resolve ambiguity by piling overrides** on a generic name; that is the fork wearing
  the system's clothes.
- Same-skin-different-purpose pairs (two cards that merely look alike) stay separate names; do
  not merge them "to be DRY". Duplication of appearance is cheap; duplication of *decisions*
  (a hex, a radius, a meaning) is the disease.

## Module-private classes: promotion and demotion

- **Private by default:** a class defined in one module's file (`filter.vue` styles) appears in
  no other file's markup. Platform scoping ([Vue `scoped`], [Blazor isolation]) enforces it
  structurally; naming prefixes ([`.search-view__bar`-style BEM]) make violations greppable.
- **Promotion signal:** a second file "wants" the same class → stop, and run the gap test above:
  shared meaning → lift it into the vocabulary/composed layer with an expressive name; visual
  coincidence → leave both, private.
- **Demotion signal:** a shared class used exactly once → move it down into its module; shared
  surface area is maintenance cost.

## What the chain buys (the ledger)

| Goal | Which rule delivers it |
|---|---|
| Maximum reusability | vocabulary layer exists; variants extend it; promotion lifts real repeats |
| Minimum overriding | OCP gap handling; no override stacks on generic names |
| Maximum flexibility | layer count per project; runtime variables; thin bases + optional expressive layers; a variant contract may replace the file chain |
| Readable top layer | pages grep-clean of style syntax; styling needs route downward as variant gaps |
| Minimum inline styling | literals live in one file; inline only for genuinely calculated values |
