# Detection: Hairline border with wide shadow

## Catalog route

The official catalog classifies this as a **source** rule. Source inspection can find border and shadow declarations; rendered/contextual evidence is needed to judge whether they redundantly define one surface.

## Candidate signals

1. Locate components with both a border and box-shadow/elevation style; capture the component, values/tokens, and source location.
2. Compare the rendered border and shadow against the actual background and neighboring/nested surfaces.
3. Determine whether each cue has a separate role (edge, elevation, focus, selection, separation) or simply repeats the same perimeter.
4. Check whether the actual boundary remains visible if one cue is softened, and assess required non-text contrast on the boundary itself.

## False-positive controls

- Do not flag the coexistence of CSS properties alone.
- Do not assume exterior shadow provides required boundary contrast.
- Preserve state/focus cues and intentional separation on dense or layered surfaces.
- A computed or source value does not establish perceived visual weight across themes.

## Test disposition

Source-candidate positive fixtures can include border+shadow on the same component. Negative fixtures should cover one cue being imperceptible, separate boundary/elevation roles, and a distinct focus/selection border. Visual calibration is needed to assert redundancy; regex cannot confirm it.