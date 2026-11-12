# Conditional and runtime styling

The generalization of the hard part: styling that changes. Everything here rests on one principle —
**decide at the earliest moment the answer is knowable, and pass it through the channel the
platform resolves, not one you assemble yourself.** [Bracketed] mechanisms are examples; hybrids
and platform-native equivalents are fine.

## The build-time vs runtime split

| Known when? | Correct channel | Wrong channel |
|---|---|---|
| While writing the code (a danger button is always danger) | Static name in the style layer | Computing it at runtime |
| At render time, from a finite set (error/success/pending) | Class mapping or state attribute resolved from data | Assembling class strings from fragments |
| At runtime, continuous or measured (progress %, drag position, user-picked color) | Runtime variable set on the element, referenced by the style layer | Adding a generated CSS rule per value |
| Never (the value is the point: `width: 42.7%`) | Inline style of that single property | Anything else — this is inline's one honest job |

## Anti-patterns, generalized

1. **Constructed class names.** `class="bg-${tone}-500 text-${tone}-contrast"` —
   - breaks any build step that extracts/optimizes used styles (purge/content scanning can never
     prove the class is used, so it is dropped or the build must be weakened);
   - makes the rendered style unsearchable: grepping the output name finds no source;
   - invents combinations that may not exist as tokens at all.
   The failure is identical with [Tailwind], with [BEM string concatenation], or with generated
   XAML/QML style keys. Never build names at a call site; **select** names. The legal form of
   interpolation is *selection inside the layer that owns the names*: `` :class="`mt-button--${variant}`" ``
   within the component whose closed union and per-member rules live in the same file is a
   mapping wearing shorter clothes — exhaustive and greppable. The banned form is interpolation
   *over token fragments at consumption sites*, where no layer guarantees the produced name
   exists. See `04-layer-chain-and-naming.md` §"Variants can do the work of layering".

2. **Hundreds of conditional utility classes at the call site.** A `class` attribute containing
   `dark:`, `hover:`, `md:` permutations for one button is the component's visual spec pasted into
   every usage site — changed once per usage, wrong in the other forty. Push the repetition down:
   the component or the style layer owns the spec; call sites pass intent (`primary-card`).

3. **Inline styles as a layer.** An inline dump escapes tokens (theme flips miss it), wins the
   specificity fight against every real rule, and turns every style change into a code change plus
   redeploy. Inline for one computed value, not for a stylesheet's worth of properties.

4. **Re-render logic to repaint style.** Toggling a boolean that rebuilds the view just to change
   a color, when the platform has hover/focus/[`:hover`, `:focus-visible`, `:checked`, MAUI
   `VisualStateManager`, `:hover`/`:pressed` pseudo-states and `State` blocks in QML]. Discrete
   interaction state belongs to the style layer's own selectors.

5. **A new CSS rule generated per runtime value** (inserting stylesheets for every user color).
   Variables exist for exactly this; generating rules leaks memory and defeats caching.

## Good practices, generalized

### Class mapping — finite states in, name out

One lookup object per component, keyed by state, containing only complete variant names:

```css
/* style layer */
.btn { /* base */ }
.btn--primary { background: var(--accent); color: var(--on-accent); }
.btn--danger  { background: var(--danger); color: var(--on-danger); }
```

```ts
const toneClass = { primary: "btn--primary", danger: "btn--danger" } as const;
<button class={cx("btn", toneClass[tone])}>
```

```csharp
// Blazor: same idea, dictionary of names; call site never builds a string fragment
private static readonly Dictionary<Tone, string> ToneClass = new()
{
    [Tone.Primary] = "btn--primary",
    [Tone.Danger]  = "btn--danger",
};
<button class="@($"btn {ToneClass[Tone]}")" ...>
```

The map is greppable, exhaustive (a missing state is a type error or a loud `undefined`), and
survives style extraction on any build pipeline.

### Runtime variables — continuous values through a named channel

```tsx
<div style={{"--fill": `${pct}%`} as CSSProperties} class="progress" />
/* .progress .bar { width: var(--fill); } */
```

```xml
<!-- MAUI: a dynamic resource / binding the style consumes -->
<ProgressBar Progress="{Binding Fraction}" />  <!-- fraction is data, not style -->
```

```qml
// Qt: property binding feeds the visual, tokens feed the constants
Rectangle { width: parent.width * control.fraction; color: Theme.accent }
```

Set the variable; let the style layer reference it. The element stays theme-reactive because the
*style* still comes from tokens — only the number is runtime.

### State attributes — discrete UI state keyed in the style layer

`data-state="open|closed"`, `aria-expanded`, `aria-invalid`, disabled/checked. Style selectors
react to them; behavior code only flips the attribute:

```css
.sheet[data-state="closed"] { transform: translateY(100%); }
.field[aria-invalid="true"] { border-color: var(--danger); }
```

Platform analogs: [XAML `VisualStateManager` / `Trigger` on state], [Blazor binding one class
that means the state], [QML `states`/`transitions`]. One mechanism per project for this; mixing
attribute-styling, class-styling and re-render-styling for the same concept is the actual bug.

### Custom CSS for genuinely complex effects

Masks, layered shadows, clip-path art, container-query choreography: give it one named, scoped
block in the module's file, consuming tokens like anything else. The existence of one bespoke rule
is not a failure of the system — inventing an eight-utility combination to fake it is.

## Consistency rule

Whichever channels you picked from the table, apply them the same way everywhere: one class-mapping
shape, one way to set runtime variables, one state-attribute convention. The decision table earns
its keep only when nobody re-decides it per component.
