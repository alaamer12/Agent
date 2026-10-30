# Verification

Contents: checks, using the scripts, CI wiring, trade-offs and risks.

## Checks

| Check | What it catches |
|---|---|
| Folder matches key | A layer's folder path and its registered key disagree |
| Ambiguity test | Two layers of equal specificity match the same context and no tie-breaker exists, tested over every combination of axis values |
| Duplicate key | Two registrations in one cell, failing at startup |
| Missing base | A seam with no base implementation |
| Resolved-map report | Prints which layer wins each file or seam per profile, and warns when a base file changed after the layer that shadows it |
| Identity lint | A hardcoded product name outside the identity source |
| Coexistence smoke test | Launch every variant at once and assert nothing collides |

The tie-breaker rule matters most. A cell where two axes meet is allowed to exist, but only where two layers truly disagree, and a person writes the resolution once.

## Scripts

Both scripts use only the Python standard library and work on any language's files.

`python scripts/scan_axes.py <path> [--product NAME] [--tokens axis=a,b] [--json]`
Evidence for the axis inventory: filename variants (grids with two axes in one name are flagged, families with three or more variants are family-file candidates), conditional-logic hotspots (conditional compilation, platform checks, channel checks, region or tenant checks), identity literals, and existing layer-like folders. It is heuristic, so confirm findings by reading code.

`python scripts/check_layers.py <layers-root> [--base <base-dir>] [--profile axis=value,axis=value] [--json]`
Validates the folder convention `Layers/<axisA>+<axisB>/<valueA>.<valueB>/<component>/...`, reports ambiguities that need a tie-breaker, warns about forks (a layer file identical to the base file), notes layer-only files, and with `--profile` prints the resolved map. It exits 1 when errors exist, so it can gate CI. It checks files and folders only, so the registration list and the resolver are verified by the project's own tests.

## CI wiring (examples, adapt to the project)

- Run `check_layers.py` once per supported profile (every channel and audience combination that ships), with `--base`.
- Fail on errors. Treat forks as warnings that must be answered in review.
- Print the resolved map as a build artifact so reviewers can see what each profile actually uses.
- Run the project's own test that enumerates every combination of axis values through the resolver.

## Trade-offs and risks to state in the plan

- **Shadowing replaces.** Where wrapping is needed, resolve a chain and decorate instead of shadowing a file.
- **Two features claiming one seam** is a real conflict. Validate and fail the build instead of letting registration order decide.
- **Base drift.** A base file can change while an overlay silently keeps old behavior. The resolved-map report and a "base changed after layer" warning expose it.
- **Frequent tie-breaker layers** signal a seam that is too coarse. Split it into smaller seams.
- **Cost of Level 3.** It adds selectors, a registry, and CI checks. Do not adopt it while directories are enough.
