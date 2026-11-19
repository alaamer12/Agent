# SVG engineering: geometry contract, optimization, sanitization

Doctrine for vectors and icons once you have the file. The two classic agent
incidents — the logo with cut-off edges and the hand-drawn brand mark — are
both geometry failures; the classic security hole is a load-mode misunderstanding.

*Claims follow documented MDN / SVGO / Lucide semantics (links at the end); the
repo-side brand-mark evidence is the `fahlwy` logo hunt. Verify wrapper
pipelines (SVGR, imagemin) on the project — they can differ from SVGO defaults.*

## 1. The geometry contract: `viewBox` → `preserveAspectRatio` → `overflow`

"Edges get cut off" is always decided by these three, in this order:

- **`viewBox` is the scaling contract.** It supplies the *intrinsic ratio*;
  without it `preserveAspectRatio` has **no effect** (except `<image>`) and the
  SVG behaves like a fixed-size raster — it will not fill its box and clips in
  smaller containers. An SVG with explicit width/height and *no* viewBox is the
  classic broken logo file (the `removeViewBox` output, §2).
- **`preserveAspectRatio` is the fit decision.** Default `xMidYMid meet`
  letterboxes — never crops. `slice` (or CSS `object-fit: cover` on the media
  element) is the *literal* "edges cut off" setting; `none` distorts to fill.
  Align values: the nine `xMin|Mid|Max YMin|Mid|Max` combos plus `none`.
- **`overflow` is hidden by default** for non-root `<svg>` per the UA
  stylesheet: anything drawn outside the viewBox rectangle — an edge-centered
  stroke, overshoot, badge — simply disappears. Escape hatch for inline SVG:
  `overflow: visible` on the root.

Diagnosis order when a logo renders cropped: ① missing `viewBox`; ② viewBox
tighter than the artwork (exported a layer, not the frame) + default hidden
overflow; ③ `slice`/`object-fit: cover` applied; ④ stroke riding the canvas
edge (half its width is outside — the frame needs padding; ≥1px edge clearance
is why Lucide mandates it); ⑤ non-integer scale factor → seams, not cuts (§3).

As CSS background or `<img>`: a fixed `background-size` wins; else intrinsic
ratio; else specified size; else background area. Undeclared SVG renders at
300×150 default. viewBox = ratio, width/height = size.

## 2. SVGO: pin the dangerous switches, don't trust defaults

- **`removeViewBox` must stay off.** v4's `preset-default` does not include it —
  but its own docs carry the warning *"This plugin prevents SVGs from scaling,
  so they will not fill their parent container, or may clip"*, and wrappers
  drift: SVGR pre-v6 merged its own config (and removed viewBox behaviors);
  `imagemin-svgo` presets have historically re-enabled it. Doctrine: pin
  `removeViewBox: false` explicitly in the repo config; pin it, don't trust it.
- **Default plugins that change pixels, not bytes:** `convertPathData` rounds at
  `floatPrecision: 3` and bakes transforms into path data; `cleanupNumericValues`
  rounds; `convertShapeToPath` costs editability. The rounding + transform-baking
  is the mechanism behind §3's seams. Keep the authored source in version
  control; the optimized output is a build artifact.
- **`removeDesc` is default-on, `removeTitle` is off:** an "optimized" icon can
  keep a `<title>` but lose its `<desc>` silently. Re-assert a11y naming in the
  component layer (§5), or treat the source file as the a11y-of-record.
- **Optimization is NOT sanitization.** `removeScripts` exists but is *not* in
  the default preset. Different step, different tool (§4).

## 3. The pixel grid and hairline seams

Fractional coordinates (precision collapse, baked transforms) on a non-integer
scale factor make adjacent shapes sample onto different device-pixel grids;
anti-aliasing leaves a lighter seam. The authoritative mitigation is a design
grammar, from Lucide's spec (must/should normative): 24×24 square canvas, 2px
strokes, round caps/joins, **≥2px visual separation** between distinct elements,
≥1px edge clearance, pixel-grid alignment "where possible" — but never at the
cost of visual quality. Corollary for icon-set hygiene: a 2px gap on the 24-unit
grid is 0.67px rendered at 8px — hairline gaps appear exactly when the design
rule thins below that. `shape-rendering: crispEdges` trades seams for jaggies:
last resort, axis-aligned static tiles only.

A stroke-based set is a *typographic system*: stroke width must scale with the
icon, which is the opposite of `vector-effect="non-scaling-stroke"` (real use:
maps/diagrams where 1px is the requirement — never let it ride along from a
design-tool export). Fill icons dodge stroke drift but lose the
"one-file-N-weights" property.

## 4. Security: the boundary is the load mode

- Scripts run when SVG is: inline in HTML, standalone-opened, `<object>`,
  `<iframe>`, `<embed>`. Scripts never run — "secure, non-interactive mode" —
  when SVG is used as an image: `<img>`, `<image>`, CSS `background-image`.
  External resources and `:visited` styling are also disabled in image mode.
- **Serving untrusted SVG from your own origin in a non-image mode is the
  stored-XSS shape** (real advisories exist for exactly "does not sanitize
  uploaded SVG files"). Upload paths: store the bytes, serve via
  `<img>`/background, done.
- The browser-native answer: HTML Sanitizer API `setHTML()` / safe baseline
  removes `<script>`, event-handler attributes, `<iframe>/<object>/…` **and
  `<use>`** — the trap: XSS-safe baseline breaks sprite `<use>`. The deliberate
  path is `setHTMLUnsafe()` with an audited custom config, or DOMPurify
  (`USE_PROFILES: {svg: true}`) — with its documented foot-guns: sanitize-then-
  modify voids the sanitize, closed shadow roots cannot be sanitized, `sanitize()`
  is not re-entrant, server-side needs current jsdom.
- Multi-color caveat for components: one `currentColor` resolves to one color
  per subtree — two paths sharing it collapse to monochrome on hover/dark-mode.
  Real multi-color needs explicit fills or `--icon-primary`/`--icon-secondary`
  tokens (works because presentation attributes lose to any stylesheet rule:
  specificity zero).

## 5. Accessible naming lives on the consumer

| Placement | Naming mechanism |
|---|---|
| `<img src=*.svg>` | `alt` (or `alt=""` decorative) |
| Inline SVG that means something | `role="img"` + `<title>` as the **first child**, or `aria-labelledby` to title+desc ids (better AT support than `aria-describedby`; `aria-describedby` wins over `<desc>` when present) |
| Icon inside a button | **label on the button**, icon `aria-hidden="true"`; never `aria-label` on the glyph (double announcement); touch target ≥44px on the wrapper, not the icon |

Decorative-or-semantic is decided by what the pixel conveys (WCAG 1.1.1 /
WAI images tutorial); "avoid text inside images unless it's a logo" applies
verbatim to SVG banners.

## 6. Sprites (`<symbol>` + `<use>`): what the clone boundary really allows

- Cloned nodes are **not exposed to CSS**: only *inherited* properties
  (`color`/`currentColor`, `fill`, `stroke`, `stroke-width`, `visibility`) reach
  inside. `use .path-2 { fill: red }` is not a thing.
- Attributes on `<use>` are ignored where the referenced element already sets
  them (only `x/y/width/height/href` apply) → a sprite baking `fill="#0F0"` is
  **uncolorable**; author symbols with `currentColor`/no baked attributes.
- `<use width/height>` only take effect when the referenced element has a
  `viewBox` → symbols must carry their own.
- External files: same-origin only (cross-origin `<use>` has no defined policy;
  `data:` hrefs deprecated for security) → a CDN-hosted shared sprite is not a
  supported pattern.
- Scale tradeoff: sprite = one cache object, zero tree-shaking, inherited-styling
  only, `<title>` inside symbols unreliable → per-icon components give full CSS
  control + tree-shaking + a11y at markup cost. Component-by-default with
  sprite-as-option is where the serious ecosystems (Lucide et al.) landed.

## Sources

- MDN: [viewBox](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/viewBox),
  [preserveAspectRatio](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/preserveAspectRatio),
  [overflow](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/overflow),
  [vector-effect](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/vector-effect),
  [`<use>`](https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Element/use),
  [SVG as image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image),
  [Scripting](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/Scripting),
  [SVG in HTML](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_in_HTML),
  [Sanitizer API](https://developer.mozilla.org/en-US/docs/Web/API/HTML_Sanitizer_API)
- SVGO: [preset-default](https://svgo.dev/docs/preset-default/), [removeViewBox](https://svgo.dev/docs/plugins/removeViewBox/), [convertPathData](https://svgo.dev/docs/plugins/convertPathData/), [cleanupNumericValues](https://svgo.dev/docs/plugins/cleanupNumericValues/); [SVGR migration](https://react-svgr.com/docs/migrate/)
- Lucide: [icon specification](https://lucide.dev/contribute/icons/specification), [accessibility](https://lucide.dev/how-to/accessibility.md), [svg-sprite](https://lucide.dev/guide/static/svg-sprite.md)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [WAI images tutorial](https://www.w3.org/WAI/tutorials/images/), [DOMPurify](https://github.com/cure53/DOMPurify)
