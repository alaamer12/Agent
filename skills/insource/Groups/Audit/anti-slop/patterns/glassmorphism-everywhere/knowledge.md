# Glassmorphism everywhere

**ID:** `glassmorphism-everywhere`  
**Catalog section:** Visual Details  
**Official modality:** Design review

## Definition and empirical evidence

The catalog describes glass panels, blur, and glow borders used broadly as decoration rather than to solve a real layering problem. Glassmorphism uses translucent surfaces to suggest depth and show some context beneath them. Translucency is a material/hierarchy cue, not a defect by itself.

## Underlying principle and potential harm

Use a translucent material when the relationship to underlying content helps users understand a distinct layer. Repeated glass surfaces can make elevation and boundaries difficult to parse, compete with content, or reduce text legibility as the background changes. Layered blur may also increase rendering/power costs on some platforms/devices. These are risks to assess, not automatic consequences of a blur declaration.

Text contrast must be evaluated over actual backgrounds and states. Windows Acrylic guidance warns against stacking Acrylic layers and notes GPU/power costs and solid fallbacks in high-contrast, battery-saver, reduced-transparency, and low-end conditions. Apple materials are also platform-specific conventions rather than a blanket instruction for every page.

## Recognition signals

- Translucent fills, backdrop blur, glowing edges, and visible background content repeat across unrelated surfaces.
- Several blurred surfaces overlap without helping users understand layer or context.
- Body text sits on backgrounds whose colors/images change through transparency.
- Decorative highlights dominate over content or obscure boundaries.
- The effect has no clear role in navigation, temporary overlays, system material, or intentional hierarchy.

## Causes to investigate

Possible causes include adopting a visual trend as a global component style; copying platform materials outside their intended use; replacing clear hierarchy/boundaries with translucency; or layering effects without reviewing the composition or device cost.

## Exceptions and false positives

- Platform-native materials can intentionally use blur/vibrancy and may preserve foreground legibility through system behavior.
- Menus, popovers, flyouts, and transient panes may preserve underlying context; some persistent surfaces are better opaque.
- A limited translucent layer can distinguish navigation/control surfaces from underlying content.
- Solid elevated cards and dimming scrims are other depth cues; do not label every layered surface as glassmorphism.
- Reduced-transparency media preferences are not broadly supported in every browser, so maintain a legible fallback.

## Correction guidance

Identify each surface’s role and retain translucency only where it clarifies layering or context. Replace gratuitous use with a solid/opaque fill or another clear boundary; avoid stacking blurred panels. Test text contrast across the possible underlay colors and UI states, adjust tint/opacity or provide a stable text backing, and honor reduced-transparency preferences where supported with a robust fallback. Validate platform-native components against platform guidance and test on representative devices.

## Independent research references

- [Nielsen Norman Group — Glassmorphism](https://www.nngroup.com/articles/glassmorphism) — definition, possible hierarchy benefits, and risks when overused.
- [Apple Human Interface Guidelines — Materials](https://developer.apple.com/design/human-interface-guidelines/materials) — platform material and legibility conventions.
- [Microsoft Learn — Acrylic material](https://learn.microsoft.com/en-us/windows/apps/design/style/acrylic) — suitable contexts, layering, contrast, performance, and fallback guidance.
- [W3C WAI WCAG 2.2 contrast minimum](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) — evaluated text/background contrast requirements.
- [MDN `prefers-reduced-transparency`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/%40media/prefers-reduced-transparency) and [`backdrop-filter`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/backdrop-filter) — user preference, CSS effect, and support caveats.