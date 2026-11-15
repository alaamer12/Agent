# Calibrate — Universal Verification Checklist

A language- and framework-agnostic checklist to ensure zero loss of subtle design layers during North Star propagation.

> **Standing Note**: All values in brackets `[example]` are illustrative references. Adapt tokens, scales, and component syntax to your project's target design system and tech stack.

---

## 1. Atmosphere & Canvas
- [ ] **Ambient background layer present**: Out-of-flow decorative layer `[e.g. z-index: -1 / pointer-events: none]` replicated across sibling views.
- [ ] **Glow & blur elements positioned**: Soft radial gradients or blur disks `[e.g. blur-3xl, 30–50% opacity]` positioned correctly relative to container bounds.
- [ ] **Pattern uniqueness**: Any patterned SVG fills, gradients, or clip-paths use distinct identifiers `[e.g. id="pattern_<view_name>"]` to eliminate browser SVG cache collisions.
- [ ] **Organic flow geometries**: Contour curves, wave shapes, or brand ribbons scaled and positioned without obstructing interactive elements.

## 2. Spatial & Surface Architecture
- [ ] **Enclosure geometry matches**: Border radius scale `[e.g. 16px / rounded-2xl]`, border stroke tokens, and background elevation match the North Star.
- [ ] **Interaction feedback verified**: Hover, focus, and press elevation changes match reference transitions.
- [ ] **Strict clipping containment**: Every card hosting embedded micro-charts, edge watermarks, or glowing ribbons strictly enforces `overflow: hidden` `[e.g. clipBehavior: Clip.antiAlias in Flutter, .clipped() in SwiftUI]`.
- [ ] **Generous breathing room**: Internal padding `[e.g. 20px–24px]` and component flow gaps `[e.g. space-y-6 / space-y-8]` prevent visual crowding.

## 3. Iconographic System & Framing
- [ ] **Anchored badge architecture**: Icons are enclosed within structured badge shapes `[e.g. circular 44x44px or squircle 48x48px]` anchored consistently `[e.g. top-left in LTR or top-right in RTL]`.
- [ ] **Palette semantics**: Badge background tint and vector foreground color reflect consistent semantic pairs `[e.g. Mint/Emerald, Sky/Blue, Amber/Orange, Lavender/Purple]`.
- [ ] **Verified vector paths**: Every icon renders a genuine vector path. No undefined keys producing empty fallback characters or placeholder dots `[•]`.

## 4. Micro-Visualizations & Rhythm
- [ ] **Embedded micro-charts present**: Mini trend lines, sparklines, or progress rings are integrated into summary cards as seen in the North Star.
- [ ] **Chart bounding verified**: Positioned with fixed dimensions in an isolated layer `[e.g. absolute bottom-left with fixed height 32–40px]`.
- [ ] **Rendering engine dependencies**: Parent template, build bundle, or layout shell includes all necessary visualization runtime libraries.

## 5. Typographic Hierarchy & Figures
- [ ] **Tabular/Monospace figures**: Key numerical metrics employ monospace or tabular font variants `[e.g. font-mono, tabular-nums]` to prevent layout shift.
- [ ] **Scale contrast**: Prominent size for primary metric figures `[e.g. 28px–36px, extra-bold]` paired with legible, muted secondary labels `[e.g. 13px–14px, medium weight]`.
- [ ] **Status indicator pills**: Badges and status pills follow unified corner radius, font weight, and contrast standards.

## 6. Lifecycle & Data Simulation Contract
- [ ] **Simulated state capability**: Realistic mock datasets populated deterministically when requested `[e.g. ?filled query param, debug mock store, or preview fixtures]`.
- [ ] **Honest baseline state**: When simulation is inactive, components gracefully render honest zero values, placeholders, and clean empty-state illustrations without runtime errors.
- [ ] **State persistence**: Filter parameters, tab selections, and simulation flags are preserved across internal links and modal triggers.
