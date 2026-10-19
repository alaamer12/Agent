# Detection: Radius outside DESIGN.md

## Catalog route

The official catalog classifies this as a **source** rule. Finding a numeric radius not in `DESIGN.md` creates a candidate; it does not establish that the rendered shape is inappropriate.

## Candidate signals

1. Read documented radius tokens and any component-specific radius settings.
2. Inspect CSS/SCSS, CSS-in-JS, component props, and theme files for authored radius values and token references.
3. Resolve custom properties and component variants where possible; preserve file/line and the affected component role.
4. Compare repeated roles for unexplained near-miss values, then inspect the computed radius and rendered shape at relevant sizes and states.

## Contextual confirmation

Check whether the system is stale, a new radius is an approved redesign, or a component-specific setting is intentional. Review clipping, content room, actual interactive target area, and visible keyboard focus; a static value cannot determine these outcomes.

## False-positive controls

- Do not presume one radius must apply to every component.
- Do not treat target size or accessibility as implied by a radius token match.
- Do not infer a visible UI from an unused CSS declaration or a value generated at runtime.
- Regex may locate explicit values but cannot resolve all computed styles or intent.

## Test disposition

Source-candidate evaluation is suitable. Positive fixtures should include an unexplained authored radius outside the scale; negative fixtures should cover a documented token, an approved component-specific radius, and a responsive or state-specific exception. Add rendered checks for clipping/focus where feasible. Detector accuracy is pending.