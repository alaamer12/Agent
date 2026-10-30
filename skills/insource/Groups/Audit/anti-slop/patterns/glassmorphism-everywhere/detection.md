# Detection: Glassmorphism everywhere

## Catalog route

This is one of the six **design-review** patterns. It requires visual and contextual judgment; source code or `backdrop-filter` presence cannot confirm it.

## Visual/contextual checks

1. Identify translucent, blurred, and glowing surfaces in the rendered page and record their roles and locations.
2. Check whether the treatment preserves relevant background context or clarifies a distinct layer.
3. Assess repetition, overlapping blur, surface boundaries, visual hierarchy, and text contrast over changing underlays/states.
4. Check platform/system materials, reduced-transparency preferences, fallbacks, and device behavior where applicable.

## Structural clues (candidate only)

CSS `backdrop-filter`, translucent alpha colors, blend modes, and repeated glow styles can locate surfaces for visual inspection. They are not a deterministic violation signature.

## False-positive controls

- Do not flag platform-native materials, temporary overlays, or a purposeful single context-preserving layer solely for transparency.
- Distinguish glass from opaque elevated surfaces, scrims, and ordinary shadows.
- Do not infer contrast failure from blur; evaluate rendered text/background pairs.

## Test disposition

Not a regex-confirmable pattern. Visual calibration should include repeated gratuitous glass, subtle purposeful translucency, platform-native materials, and a low-contrast failure over variable underlays. Structural hits remain candidates for the independent visual scout.