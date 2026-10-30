# Worked examples

Both examples are invented to show the shape of the output. Names, axes, and languages are examples only.

## Example A: `/isolate this project layers` (audit and plan)

**Situation.** A cross-platform app with a confirmation dialog component. The scan shows `Dialog.Canary.Android.cs` (a grid name), eleven `#if` blocks on a canary flag, and the product name as a string literal in nine files.

**Step 1, evidence** (`scan_axes.py . --product Acme`, abbreviated):
```
GRID names (two axes in one filename): 1
    src/Dialog/Dialog.Canary.Android.cs
Family with 4 variants: src/Dialog/Dialog
channel-check: 11 hits in 4 files
Identity literals for 'Acme': found in 9 files
```

**Step 2, axis inventory** (confirmed by reading the files):

| Axis | Values | Total or sparse | Binds at | Feeds identity |
|---|---|---|---|---|
| `[platform]` | android, ios, windows, macos | total | build | no |
| `[release channel]` | stable, plus several canaries | sparse, open | build | yes |
| `[audience]` | eg, us, more later | sparse, open | runtime | no |

Set aside as not code: the `rc` ring (same bytes as stable, promoted by moving a feed pointer) and the regional currency and wording strings (data, so a configuration pack).

**Step 3, escalation shown to the user:**
1. *Platform alone* is Level 1. It already exists and works, and the family files (`_Dialog.Mobile`, `_Dialog.Desktop`) are kept as they are.
2. *Add channel.* `Dialog.Canary.Android.cs` is the constraint: a filename cannot hold two axes. Level 2 moves channel to `Overlays/<canary-id>/Dialog/`.
3. *Add audience.* Audience must switch at runtime and one audience policy collides with a canary policy, so Level 2 would form a grid. Level 3: layers, with channel included by the build and audience selected at runtime.

**Step 4, layout and decisions** (sketch, project idiom preserved):
```
src/
  Core/                          selectors, layer key, registry, resolver
  Dialog/                        base: Dialog.cs, Dialog.Windows.cs, _Dialog.Mobile.cs, DefaultPolicy.cs
  Layers/
    channel/canary-gpu/Dialog/   CanaryGpuRenderer.cs
    audience/eg/Dialog/          EgPolicy.cs
    channel+audience/canary-gpu.eg/Dialog/   CanaryGpuEgPolicy.cs   (only because the two collide)
  Registration/                  per-build list
```
Ambiguity policy: strict (collision fails until a tie-breaker exists). Trade-off stated to the user: more work than a fixed precedence, but every collision is reviewed. Identity: channel feeds a generated identity source, audience stays metadata, and the nine product-name literals move into it.

**Step 5, verification.** `check_layers.py src/Layers --base src --profile channel=canary-gpu,audience=eg` in CI for each shipping profile, plus the identity lint.

**Step 6, migration order.** Identity source first (lowest risk, removes the collision risk), then the dialog component, then the next component that shows a grid name.

## Example B: `/isolate feature: regional tax rules` (planning, no code yet)

**Situation.** A new feature: compute tax by region. Nothing is written yet, so the goal is to plan the feature so its variation is isolated from the start.

**Axis inventory:**

| Axis | Values | Total or sparse | Binds at | Note |
|---|---|---|---|---|
| `[region]` | eg, us, more later | sparse, open | runtime | one user may change region |
| `[tax provider]` | provider A, provider B | total for the contract | build or runtime | a capability, not a policy |

**Decisions, applying "do not over-isolate":**
- Tax **rates, labels, and rounding rules** differ only in values, so they are a data pack per region. No layer.
- The **provider integration** differs in code but is a capability. It becomes one seam (`TaxProvider`) with one implementation per provider, chosen by the region's data pack. This is Level 1 for the provider axis, expressed as a registry because the choice is by data.
- **Region** therefore needs no layer folders at all. A single axis with one seam stays at Level 1, and adding layers would be cost with no benefit.

**Plan output (short).** Seam `TaxProvider`: contract `calculate(order) -> tax lines`. Base implementation: provider A. Region data packs: `regions/eg`, `regions/us`. Verification: a test that loads every region pack and asserts its provider is registered. Open question for the user: will a region ever need behavior that is not a provider choice? If so, revisit and escalate to layers.

The plan is smaller than Example A on purpose. The skill's job is the least structure that keeps differences isolated, not the most.

## Example C: `/isolate src/dialog/Dialog.Canary.Android.cs` (small task, no plan)

**Situation.** One grid-named file. The component already uses platform files and a mobile family file, and there is one experimental variant that changes a single seam.

**Sizing.** One component, two axes, no identity or build changes, no shared contract affected. This is small, so there is no plan and no template.

**What the agent does.** It moves `Dialog.Canary.Android.cs` to `Overlays/canary-gpu/Dialog/_Dialog.Mobile.cs`, keeping only the code that differs from the base mobile family file. It then runs the project build for stable and for the canary property, and runs `check_layers.py` if a layers tree exists.

**Closing summary (the whole deliverable):**
> Isolated the canary GPU path. The canary difference now lives only in `Overlays/canary-gpu/Dialog/_Dialog.Mobile.cs`, and the grid-named file is gone. Stable and canary both build. Not changed: identity and the other components, which still hold three product-name literals, so say if you want those isolated next.

**Escalation trigger.** If the agent had found that the canary also needed a different audience policy, it would stop, say the task grew, and switch to the plan path.
