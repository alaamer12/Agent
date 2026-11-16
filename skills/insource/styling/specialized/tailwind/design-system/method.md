# design-system — Tailwind tokens, scales, and picking values

Every value a Tailwind utility emits comes from one place: the theme. Spacing, color, type,
breakpoints, radii, shadows, easing, animation. All of them are tokens, and the markup expresses
intent *within* that token system. Fluent Tailwind is picking tokens; the moment a call site
carries a raw value, the system has a hole in it that the next contributor will widen.

Four facts hold on both v3.4 and v4:

1. **The theme is the single source of truth.** A utility is a name for a theme entry. `p-4` is not
   "16px", it is `theme.spacing[4]` / `calc(var(--spacing) * 4)`.
2. **The defaults are the design system.** 22 color families, 11 shades each, a 32-step spacing
   scale, a 13-step type scale, 5 breakpoints. Most projects need zero custom tokens; the ones that
   need them need a handful, named.
3. **Custom tokens extend, they do not replace.** Add under `theme.extend` (v3) or add namespaced
   variables (v4). Redefining whole namespaces is a deliberate wipe, not an accident.
4. **A raw value at a call site is a defect** unless it is genuinely one-off (`p-[13px]`) or runtime
   (`bg-(--brand)`). Anything that repeats belongs in the theme.

v3 keeps the theme in a JavaScript config object; v4 moves it into CSS variables on the document
root. Same class names, different surfaces, and the surface decides how a token is declared, read,
and themed at runtime.

## Default scales at a glance

| Domain | Default scale | v4 namespace | v3 location |
|---|---|---|---|
| Spacing | `0`, `0.5`, `1` … `4`, `5`, `6` … `96` in 0.25rem steps, plus `px` | `--spacing` (single base unit, `0.25rem`) | `theme.spacing.*` (32 named entries) |
| Color | 22 families (5 neutral + 17 chromatic) x 11 shades (`50`…`950`) | `--color-{family}-{shade}` (`oklch`) | `theme.colors.*` (`rgb`/`hsl`/hex) |
| Type | `text-xs` … `text-9xl`, 13 steps, each with a paired line-height | `--text-*` + `--text-*--line-height` | `theme.fontSize.*` (tuple form) |
| Breakpoints | `sm` 640, `md` 768, `lg` 1024, `xl` 1280, `2xl` 1536 (px) | `--breakpoint-*` | `theme.screens.*` |
| Opacity | `0`, `5`, `10` … `100` in 5% steps, plus arbitrary | modifier `/N` or `/[N%]` | modifier `/N` or `/[N%]` |

Full tables (every spacing step with rem/px, every family and shade, the paired line-heights, the
complete v4 namespace list and its v3 `theme.*` equivalent) live in `references/namespaces.md`.

The three patterns that cover most token consumption, identical on both versions:

```html
<!-- spacing token -->
<div class="px-4 py-8 gap-6 mt-12">...</div>

<!-- color token + opacity modifier -->
<button class="bg-blue-600 text-white hover:bg-blue-700/90">...</button>

<!-- breakpoint + type token, mobile-first -->
<h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">...</h1>
```

## Configuration surface: v3 vs v4

| | v3.4 | v4.0+ |
|---|---|---|
| Where tokens are declared | `tailwind.config.js` (JavaScript) | `@theme { ... }` in the main CSS (CSS variables) |
| Load behavior | resolved automatically when present | not loaded automatically; loading a legacy JS config is a directive decision, see the `config` module ([../config/method.md](../config/method.md)) |
| Color format for tokens | `rgb()` / `hsl()` / hex | `oklch()` (P3 wide gamut) |
| Spacing definition | 32 named entries in `theme.spacing` | one `--spacing: 0.25rem`; utilities desugar to `calc(var(--spacing) * N)` |
| Integer spacing off the scale | arbitrary value only: `p-[68px]` | native dynamic: `p-17` |
| Reading a token from JS | `resolveConfig(tailwindConfig).theme.colors.red[500]` | `getComputedStyle(document.documentElement).getPropertyValue('--color-red-500')` |
| Reading a token from CSS | `theme(colors.red.500)` | `var(--color-red-500)` or `theme(--color-red-500)` |

The class names generated are identical. The mechanism, the file, and the value format are not.
Everything the upgrade itself involves (breaking changes, renamed scales, changed defaults, removed
config options) is the `migration` module's: [../migration/method.md](../migration/method.md).

## Decision trees

### Picking a spacing value

```text
need padding / margin / gap / size?
├── on the default scale (0..96 in 0.25rem steps)?
│   └── ALWAYS use the scale token : p-4, gap-6, mt-12
├── exactly 1px?
│   └── ALWAYS use the -px variant : p-px, mx-px, border-px
├── v4, integer off the scale (e.g. 17)?
│   └── ALWAYS use native dynamic : p-17 → calc(var(--spacing) * 17)
├── v3, integer off the scale?
│   └── EITHER extend theme.spacing OR use arbitrary p-[68px]
├── value not expressible as a rem multiple (13px, 2.5vh, calc(...))?
│   └── ALWAYS use arbitrary : p-[13px], p-[calc(100%-2rem)]
└── value held in a runtime CSS variable?
    ├── v4 : p-(--my-padding)  (parens)
    └── v3 : p-[var(--my-padding)]  (brackets)
```

The moment a spacing value repeats in more than one place, it is a token, not an arbitrary value.
Arbitrary values are for genuinely one-off geometry, not for a scale the project forgot to extend.

### Picking a color value

```text
need a color?
├── in the default palette (5 neutral + 17 chromatic families, 11 shades)?
│   └── ALWAYS use the named token : bg-blue-600, text-slate-900, border-red-500
├── brand color or custom name?
│   ├── v4 : define --color-brand-500: oklch(...) inside @theme
│   └── v3 : define theme.extend.colors.brand[500]
├── transparency on a token color?
│   ├── named step (5% increments) : ALWAYS use /N       → bg-blue-600/50
│   └── arbitrary                  : ALWAYS use /[N%]    → bg-blue-600/[37.5%]
├── one-off color outside every palette?
│   └── arbitrary : bg-[#1da1f2], text-[oklch(0.7_0.2_220)]
└── color held in a runtime CSS variable?
    ├── v4 : bg-(--brand-bg)  (parens)
    └── v3 : bg-[var(--brand-bg)]  (brackets)
```

Custom families follow the 50-950 shade convention. Named-by-tone steps (`-light`, `-dark`) break
every contributor's expectation and every tool that derives shades: see AP-7 in
`references/anti-patterns.md`.

### Picking a type token

```text
need a font size?
├── on the default scale (text-xs .. text-9xl)?
│   └── ALWAYS use the named token : text-base, text-2xl, text-7xl
├── custom size?
│   ├── v4 : define BOTH --text-display and --text-display--line-height in @theme
│   └── v3 : theme.extend.fontSize.display = ['4.5rem', { lineHeight: '1.05' }]
└── exact size on the fly?
    └── arbitrary : text-[15px], text-[14.5px]/[1.3] (size/leading)
```

Never ship a font-size token without its leading. The pair is the token.

### Picking a breakpoint

```text
need a responsive variant?
├── default scale fits (sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536)?
│   └── ALWAYS use the mobile-first prefix : sm:, md:, lg:, xl:, 2xl:
├── custom breakpoint?
│   ├── v4 : --breakpoint-3xl: 120rem in @theme (generates 3xl:* automatically)
│   └── v3 : theme.extend.screens['3xl'] = '120rem'
├── upper bound instead of lower bound?
│   └── max-{breakpoint}: → max-md:hidden (v3.4+)
├── arbitrary viewport width?
│   └── min-[1440px]:flex, max-[640px]:hidden
└── styling off the PARENT's width rather than the viewport?
    └── class="@container" on the parent, then @sm:*, @md:* on the children
```

`sm:` means "from 640px upward", never "only on small screens". Base styles are the mobile design;
each prefix overrides from there up.

## Patterns

### 1. Defining tokens

Highest-divergence area between the two versions. Never share one snippet.

v3.4 — `tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eff6ff', 500: '#3b82f6', 900: '#1e3a8a' },
      },
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      fontSize: {
        display: ['4.5rem', { lineHeight: '1.05', letterSpacing: '-0.02em' }],
      },
      screens: {
        '3xl': '120rem',
      },
    },
  },
}
```

v4.0+ — `@theme` in the main CSS:

```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.014 254);
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-900: oklch(0.34 0.146 264);

  --spacing: 0.25rem;
  /* p-128 is generated dynamically; the 128/144 entries are unnecessary */

  --text-display: 4.5rem;
  --text-display--line-height: 1.05;
  --text-display--letter-spacing: -0.02em;

  --breakpoint-3xl: 120rem;
}
```

Both produce the same class names: `bg-brand-500`, `p-128`, `text-display`, `3xl:flex`. In v4 the
namespace prefix is what makes a variable a token — a `--brand-500` with no recognized prefix
defines nothing usable.

### 2. The opacity modifier

`/N` works on **every** color-consuming utility, not just backgrounds.

```html
<!-- named steps: 0, 5, 10 ... 95, 100 -->
<div class="bg-blue-600/0">fully transparent</div>
<div class="bg-blue-600/50">the common case</div>
<div class="bg-blue-600/100">identical to no modifier</div>

<!-- arbitrary percentage or decimal -->
<div class="bg-pink-500/[71.37%] text-white/[0.85]"></div>

<!-- runtime variable alpha -->
<div class="bg-cyan-400/(--my-alpha)"></div>       <!-- v4 parens -->
<div class="bg-cyan-400/[var(--my-alpha)]"></div>  <!-- v3 brackets -->

<!-- every color-consuming utility takes it -->
<div class="text-slate-900/60 border-red-500/30 ring-blue-600/50 fill-emerald-500/80"></div>
```

Mechanism differs: v3 splits the token into color and alpha channels and composes them at build
time; v4 emits `color-mix(in oklch, var(--color-red-500) N%, transparent)`. That difference is why
mixing hex tokens into an oklch palette changes alpha-blended output (AP-2).

### 3. Inspecting a token at runtime

Non-style consumers (charts, canvas, native chrome, OG-image generators) must read the theme, not
retype it.

v3.4 — a JS object:

```js
import resolveConfig from 'tailwindcss/resolveConfig'
import tailwindConfig from './tailwind.config.js'

const fullConfig = resolveConfig(tailwindConfig)
fullConfig.theme.colors.red[500]   // 'rgb(239 68 68)'
fullConfig.theme.fontSize.xl        // ['1.25rem', { lineHeight: '1.75rem' }]
fullConfig.theme.screens.lg         // '1024px'
```

v4.0+ — CSS variables are the only runtime API:

```js
const styles = getComputedStyle(document.documentElement)
styles.getPropertyValue('--color-red-500').trim()        // 'oklch(0.637 0.237 25.331)'
styles.getPropertyValue('--text-xl').trim()              // '1.25rem'
styles.getPropertyValue('--text-xl--line-height').trim() // '1.75rem'
styles.getPropertyValue('--breakpoint-lg').trim()        // '64rem'
```

There is no JS-importable theme object in v4. For build-time or server-side lookup with no DOM,
parse the compiled CSS output for `--color-*` declarations.

### 4. oklch and P3 wide gamut (v4)

v4 declares every default color in `oklch()`, targeting the P3 wide-gamut profile. On sRGB displays
the value falls back to the nearest sRGB equivalent; on P3 displays (most phones, MacBooks since
2016, most external monitors since 2020) the same token renders more saturated, especially in the
orange, red, violet and cyan ranges.

oklch matters for authored palettes because lightness is perceptually uniform:

```css
@theme {
  /* GOOD: same hue, one perceptual step apart */
  --color-brand-500: oklch(0.65 0.196 254);
  --color-brand-600: oklch(0.55 0.196 254);

  /* TOLERATED: parses fine, loses P3 reach and perceptual stepping */
  --color-legacy: #3b82f6;
  --color-alt: hsl(217 91% 60%);
}
```

ALWAYS use `oklch()` for custom v4 tokens. The default palette is all oklch; a palette that mixes
formats has inconsistent perceived contrast between neighbors. Convert brand colors with a tool
(oklch.com, the `culori` library) rather than eyeballing hex.

### 5. Reset, override, or extend

| Goal | v3.4 | v4.0+ |
|---|---|---|
| Add to the defaults | `theme.extend.{namespace}` | `@theme { --{namespace}-newkey: ... }` |
| Replace one namespace | `theme.{namespace}` (no `.extend`) | `@theme { --{namespace}-*: initial; --{namespace}-key: ... }` |
| Wipe every default | replace every `theme.*` key by hand | `@theme { --*: initial; --spacing: 0.25rem; ... }` |
| Resolve a token against a runtime variable | compute in JS | `@theme inline { --color-brand: var(--my-brand); }` |

`initial` is the namespace wipe; forgetting it when you replace a palette leaves the old defaults
declared next to the new ones, still generating classes. `@theme inline` is the escape hatch for
tokens whose value is only known at runtime (a JS-set variable, a `[data-theme]` swap). Directive
mechanics — `@apply`, `@layer`, `@reference`, `@config` — belong to the `config` module
([../config/method.md](../config/method.md)).

### 6. Type scale with paired line-height

Every default text token carries its own leading: `text-base` applies `font-size: 1rem` with
`line-height: 1.5rem`; `text-2xl` applies `1.5rem / 2rem`. From `text-5xl` upward the pair is the
unitless `1`.

```html
<!-- rely on the pair -->
<p class="text-base">Body copy gets correct leading without extra work.</p>

<!-- override the pair deliberately -->
<h2 class="text-2xl leading-tight">Headline tightened.</h2>
<h2 class="text-5xl leading-[1.05] tracking-tight">Compact display.</h2>

<!-- both at once, arbitrary -->
<p class="text-[14.5px]/[1.3]">Exact size with exact leading.</p>
```

In v4 the pair is the companion variable `--text-{name}--line-height`; in v3 it is the second
element of the `theme.fontSize` tuple. A custom size with no pair keeps whatever leading it inherits,
which is wrong for display text almost every time.

### 7. Token-driven dark mode

Dark mode is a change of variable values, not a rewrite of utilities. Theme flips reassign roles;
components never notice.

```css
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));

@theme {
  --color-background: oklch(1 0 0);
  --color-foreground: oklch(0.15 0.02 270);
  --color-muted: oklch(0.96 0.005 250);
  --color-muted-foreground: oklch(0.55 0.02 270);
  --color-primary: oklch(0.65 0.196 254);
  --color-primary-foreground: oklch(0.98 0.005 254);
}

@layer base {
  .dark {
    --color-background: oklch(0.18 0.02 270);
    --color-foreground: oklch(0.95 0.01 270);
    --color-muted: oklch(0.25 0.015 270);
    --color-muted-foreground: oklch(0.7 0.02 270);
    --color-primary: oklch(0.75 0.18 254);
    --color-primary-foreground: oklch(0.15 0.04 254);
  }
}
```

```html
<body class="bg-background text-foreground">
  <main class="bg-muted text-muted-foreground p-6 rounded-xl">
    <button class="bg-primary text-primary-foreground px-4 py-2 rounded-md">Action</button>
  </main>
</body>
```

`bg-background` and `text-foreground` now work in both modes with no `dark:` variant on any element.
Role-named tokens (`background`, `foreground`, `muted`, `primary-foreground`) beat shade-named ones
(`slate-900`, `blue-600`) for anything that participates in a theme swap. Reserve shade names for
values that never change role.

## Ownership boundaries

| Question | Where it goes |
|---|---|
| "What does this token resolve to, and should I use it?" | this module |
| "How do I declare tokens for this project?" | this module for the token model; the `config` module for directive mechanics |
| "My classes changed appearance / broke after upgrading to v4" | the `migration` module ([../migration/method.md](../migration/method.md)) |
| "My class renders but has no CSS behind it" | the `dynamic-classes` module ([../dynamic-classes/method.md](../dynamic-classes/method.md)) |

Interpolated class names (`bg-${color}-500` built at a call site) are the classic way a token system
leaks: the literal never appears in source, so no CSS is generated. Keep token choices as complete
literal strings in a map. The full fix ladder and the safelist-expansion grammar are the
`dynamic-classes` module's.

## Resources

- `references/namespaces.md` — complete token reference: every default scale with values, the full
  v4 `--*-*` namespace list, the v3 `theme.*` → v4 namespace map, color-consuming utilities,
  opacity-modifier syntax forms.
- `references/examples.md` — worked examples: component on default tokens, full brand palette in
  both versions, layered opacity, responsive type, runtime token reads, token-driven dark mode,
  off-scale spacing.
- `references/anti-patterns.md` — failure modes with cause and deterministic fix: token names
  assembled at call sites, mixed oklch/hex palettes, legacy dotted `theme()` paths, the split-channel
  opacity form, importing the JS config for a token read, two arbitrary-variable syntaxes, tone-named
  shades, `sm:` read as "small screens only", raw values at call sites.

## Sources

- https://tailwindcss.com/docs/colors (v4 palette, oklch format, opacity modifier)
- https://tailwindcss.com/docs/theme (v4 theme variable namespaces, `@theme` syntax)
- https://tailwindcss.com/docs/padding (v4 spacing scale, dynamic integer utilities)
- https://tailwindcss.com/docs/responsive-design (mobile-first semantics, `min-*`/`max-*`)
- https://v3.tailwindcss.com/docs/customizing-colors (v3 palette, `theme.colors` format)
- https://v3.tailwindcss.com/docs/configuration (v3 `theme` object structure)
- https://tailwindcss.com/blog/tailwindcss-v4 (oklch, P3 wide gamut)
- https://tailwindcss.com/docs/upgrade-guide (theme function and runtime token lookup changes; the
  breaking-change catalogue itself is the `migration` module's)
- https://ui.shadcn.com/docs/theming (role-named token convention)

Last verified: 2026-05-19 (Tailwind CSS v4.x current).
