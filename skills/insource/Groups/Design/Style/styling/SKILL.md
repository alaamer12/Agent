---
name: styling
description: >-
  Platform-neutral rules for writing NEW styling on any stack (HTML/Web, Blazor, MAUI, Qt):
  per-module stylesheets, no monolith; role-named tokens as single source of truth; styling as a
  chain of layers, downward-only imports (values -> tokens -> mixins/utilities/functions ->
  composed styles -> module scope; layer count is the project's call, not this skill's);
  expressive names over ambiguous ones - the ambiguity trap: do not call everything 'card' and
  patch it per site; thin bases fine, expressive layers chosen not mandated; module classes are
  file-private; conditional/runtime discipline: states as class mappings or state attributes,
  runtime values as dynamic tokens, inline only for calculated numbers; composition helpers
  (joiner, merge-on-conflict, variant registry). Use when styling structure is yours, when it
  sprawls into inline dumps or built class strings, or asked how to organize CSS/XAML/QML. Not
  for retrofitting projects into tokens (styleup), redesign (denoise), or component galleries
  (components).
---

# Styling

Write styling that a stranger can read: every value named once, every file scoped to its module,
every dynamic decision made through a channel the platform can resolve — never assembled as a
string at the call site.

The same discipline holds on HTML/Web, Blazor, MAUI, Qt, and every other styling system. Names of
mechanisms differ; the layers do not. Options shown in [brackets] are illustrative, not a closed
menu; a hybrid or an unlisted mechanism is always acceptable when it fits the platform.

## Rules that hold everywhere

1. **No monolith.** Each page/module/component owns its style scope. Shared CSS is small: tokens,
   base, utilities. A 4,000-line stylesheet is a search failure waiting to happen.
2. **Tokens are the single source of truth.** Colors, spacing, type scale, radii, elevation,
   motion — role-named (`--surface`, `text-secondary`), never raw values at consumption sites.
   Theme flips (light/dark/brand) reassign roles; components never notice.
3. **Utilities are minimal and layered.** Only common, small patterns. Build `card` once, then
   `primary-card` / `secondary-card` as thin layers on top — by extension/composition, not by
   copy-pasting the base.
4. **Conditional styling is a lookup, not a build.** State maps to a named variant or a class
   from a mapping table. Interpolating class-name fragments (`bg-${x}-500`) is banned: it breaks
   build-time extraction and makes the rendered style unsearchable in source.
5. **Runtime values go through a dynamic channel.** A measured percentage, a user-chosen color, a
   computed offset: pass it as a runtime variable/token and reference it from the style layer.
   Inline styles are legitimate only for genuinely calculated values, never as a styling escape
   hatch.
6. **Styling is a chain of layers, imports point downward only.** The layer count is whatever the
   project's author established (discover it; do not re-invent it). Typical shape: raw values →
   compiled tokens/theme maps → token-consumed mixins/utilities/functions → expressive composed
   styles → module-private classes. Nothing skips a layer.
7. **Names must be expressive, not positionally convenient.** The trap that ruins the system:
   everything gets called `card`, then every consumer quietly overrides what `card` means —
   payment cards are not stats cards. A thin generic base (`card` = radius + surface) is fine;
   `payment-card` / `stats-card` layers are optional-by-choice, never by scatter. If a class
   lives in one module's file, it exists nowhere else in the app.
8. **The topmost layer wears no styling.** Pages/screens are thin builder-wrapper layers: they
   compose named components and pass data and intent — no style blocks, no class tweaks, no
   tokens. A page that needs a look means the look belongs *below* it: a component variant, or a
   gap to extend in the shared layer.
9. **Variants can do the work of layering.** A component whose styling surface is a closed,
   documented variant set — with a guardrail that consumers may only *pick names* and a missing
   variant is a defect to fix by extending that set, never by bypassing — can stand in for a
   deeper style-layer chain. Adopt the contract the project's author chose; the invariant is the
   guardrail, not the number of layers.

Ledger these four rules optimize: **maximum reusability, minimum overriding, maximum flexibility,
minimum inline styling.**

## The three layers

```text
Token layer      values + theme maps            -> "what things are"
System layer     utilities, named variants,     -> "what things look like"
                 component styles
Call-site layer  code choosing/composing the     -> "which one applies"
                   names (mappings, registries)
```

Style decisions belong in the system layer; the call-site layer only selects names. If the call
site contains hex values, arithmetic, or assembled class strings, the layers have leaked.

These three are the *conceptual* roles. The **physical** chain — how many files/tiers it is cut
into, and their names — belongs to the project: two tiers in a small app, five in a documented
design system ([a values file → a compiled-token file imported once → token-alias mixins +
functions → variants → scoped module styles] is one real shape). Read the project's existing
chain first and slot every new style into it; where a project has no chain yet, lay one down in
this order and say so in one line. **Folder placement follows the framework too, and the root's
name belongs to the framework and the project, not to this skill:** if the project already has a
styling location, that wins - reuse it, never open a rival. If none exists, take the name the
stack's idiom uses ([styles], [css], [assets], [themes], [ui], co-located per-component files
([Vue SFC], [Blazor `.razor.css`]), or barely a folder at all ([Tailwind]-style utility stacks) -
`styles` is an example, not a default). NEVER nest a subfolder named after the styling language -
`[sass]/` inside any root is a structure error: the project has exactly one styling system, the
file extension already speaks it, and a tool-named directory implies parallel systems that don't
exist. `references/04-layer-chain-and-naming.md`.

## The ambiguity trap

A consistent-looking system still dies when names lie. `card` used for a payment card, a stats
card and a media card, each patched per-site with overrides and inline tweaks, is not one
abstraction — it is three forks that forgot to separate. The discipline:

- A generic name is honest **only when the meaning is genuinely shared** by every consumer.
- Same skin, different purposes → same-skin base plus expressive upper names is allowed and often
  better; it is *not* forced — a one-property delta applied once in the owning module can stay
  local as long as the base's meaning still holds.
- A need the shared layer cannot express is a **gap in that layer**: extend the layer with a
  named variant (every future consumer inherits it), or accept it as module-local — decided by
  whether the meaning is shared, never by whichever file is closest.
- Module-private rule: classes defined in one page/component's file appear in no other file's
  markup; wanting the same class elsewhere is a promotion signal, not a copy instruction.

## Decision table for dynamic styling

| Situation | Channel |
|---|---|
| Finite known states (primary/danger, open/closed) | Named variants via a class mapping or state-attribute selector |
| Boolean/discrete UI state | State attribute (`data-state`, `aria-*`), visual state, pseudo-class — styled in CSS/XAML/QML, not re-rendered logic |
| Value only known at runtime (progress %, user color, measured size) | Set a runtime variable on the element; style layer references it |
| Truly calculated value, used once | Inline style of that one property — the exception, not the layer |
| Complex effect utilities cannot express (mask, layered shadow art, clip-path) | One named, scoped rule block |

Generalized mechanism per platform: [CSS custom properties + attribute selectors], [Blazor CSS
isolation + bound single class string], [MAUI/WinUI DynamicResource + VisualStates + BasedOn
styles], [Qt QML property bindings + states/Control styles]. Details and anti-patterns:
`references/02-conditional-and-runtime.md`.

## Composition helpers, whichever framework

Three jobs, any stack — prefer a thin local helper or platform primitive over a dependency:

- **Joiner** — assemble a class list from truthy parts ([clsx]-style). Present in most component
  frameworks or trivially hand-rolled.
- **Merge-on-conflict** — later intent wins over earlier utility of the same property
  ([tailwind-merge]-style). Only needed when your system has overlapping utilities.
- **Variant registry** — one object declaring variants, defaults, and composition ([CVA] /
  [tailwind-variants]-style; platform analogs: [MAUI Style + BasedOn sets], [QML style aliases]).

`references/03-composition-and-variants.md`.

## Procedure

1. Identify the platform's native scoping and theming mechanism; adopt it, do not fight it.
2. Map the project's existing style chain — which files exist, who imports whom, what each layer's
   one job is. Fit new work into it. Only when none exists, lay one down (values → tokens →
   mixins/utilities/functions → composed styles → module scope) and keep imports downward-only.
3. Create the token file first; from then on, components consume roles — a raw value may exist in
   the token layer only.
4. Structure files per module; keep a small shared core (tokens, base, utilities).
5. Add utilities/mixins/functions only for patterns that actually repeat; layer variants on a
   base, never duplicate it; name them for what they *mean*, not what they look like.
6. For each conditional need, consult the decision table above and use one channel consistently.
7. Keep call sites readable: a component's style choice should scan as names, not values.

## Boundaries

`styling` and `styleup` both aim to enhance the styling experience — they are the same goal at
different layers: **styling constructs the project so a true design system can exist** (structure,
chain, naming, decisions made right the first time); **styleup takes action on the code that was
already written** (inventorying hardcoding, migrating it into tokens with parity evidence). New
work: this skill. Retrofit of existing mess: styleup.

| Situation | Skill |
|---|---|
| Existing project hardcoded/duplicated, migrate into tokens with parity evidence | `styleup` |
| Redesigning an existing UI for calm/readability | `denoise` |
| Reviewing component x state coverage | `components` |
| Deriving which states a screen must handle at all | `stateful` |
| Choosing a styling library/framework from scratch | `techstack` / `thebest` |

## Resources

- `references/01-structure-and-tokens.md` — file layout, token layer design, layered utilities
- `references/02-conditional-and-runtime.md` — build-time vs runtime, anti-patterns, decision table worked deep
- `references/03-composition-and-variants.md` — join/merge/variant-registry patterns beyond one framework
- `references/04-layer-chain-and-naming.md` — the downward-only layer chain (project-defined count), promotion/demotion rules, expressive naming
- `examples/styling-polyglot-walkthrough.md` — one scenario (button variants + runtime progress) in HTML/CSS, Blazor, MAUI, Qt, before vs after
