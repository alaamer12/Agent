# Case 06 — feature flags: the seam you can't grep shut

*Names and numbers are illustrative. The hardest backend case for the doctrine, because the vendor
lives in two places at once: the evaluation SDK in the code, and the control plane (the dashboard
where flags are actually flipped) outside every file the audit can see.*

## The setup

`LaunchDarkly` (any flags vendor) imported in 23 files across three services. Evaluation calls sat
directly in domain logic:

```ts
if (ld.variation("billing-v2-splitting", user, false)) { ... }
```

Three facts made this worse than the payment case, not better:

| Property | Why it strains the doctrine |
| --- | --- |
| The vendor SDK is *ergonomic* | one call, defaults, streaming — every consumer becomes a seam by convenience, 23 at a time |
| Flag names are **shared vocabulary** with the vendor dashboard | `billing-v2-splitting` exists in the code AND in the vendor's UI; renaming it in code means migrating the control plane, not the file |
| Swapping vendors is a *runtime* event | the dashboard, segmentation, audit history — no code edit moves those; the seam seals knowledge, not data gravity |

## The seam

```ts
// flags/index.ts — the contract seam; vendor ends here.
export interface Flags {
  enabled(feature: FeatureName, ctx: EvalContext): boolean;   // our names, our context type
  variant<T>(feature: FeatureName, ctx: EvalContext): T;
}
// flags/registry.ts: FeatureName is OUR enum — a typed union / const set in the project's vocabulary.
// flags/provider.ts: the SDK + a mapping table FeatureName -> providerFlagKey, one file, audited.
```

```go
// flags/flags.go
type Flags interface { Enabled(f FeatureName, ctx EvalContext) bool }
// flags/provider_launchdarkly.go + flags/mapping.go: our keys -> provider keys, the seam's data half.
```

The ladder for flags is shallow on purpose — `Flags` (skin) → per-domain selectors (`BillingFlags`)
(semantics). Rate/quota behavior attaches *below* the interface, not above it: flag evaluation must
stay cheap and synchronous, so the cache lives inside the provider seam's body, invisible upward.

## What the walls enforce — and what they structurally cannot

Hard-zero, mechanical: SDK imports outside `flags/provider*`, **bare vendor flag keys** in any source
file (the registry enum is the only spelling), `evaluation detail` types leaking past the seam.
Ratcheted with a baseline: none needed after the registry landed — the flag-key rule is fact-checkable
once the enum owns the vocabulary, so the ratchet was refused.

And the honest boundary: the dashboard is not in the tree. The doctrine's answer is the **named
exemption row in the register** — `flags/mapping.go` documents the provider-side namespace, and the
seams document's §7 records that flag *definitions* live on the vendor's control plane with the
migration story (export → map keys → replay) as the swap proof. The seam's contract makes the mapping
one file; it does not pretend the vendor's UI is inside the codebase. **This is the doctrine at its
own limit: a seam seals knowledge behind an interface; runtime surfaces outside the tree get an
exemption row and a rehearsed migration, never silence.**

## The swap test, backend-extended

For vendors with external state, "swap touches: 1 file" is measured as **1 file + the declared data
path**: replace `provider_launchdarkly.go`, edit `mapping.go`'s right column, run the exported-flag
replay. Anything that edits more than the provider file and the mapping — that is the finding; the
audit code `FLAG_KEY_OUTSIDE_REGISTRY` catches it in CI, and the replay fixture (23 evaluation call
sites → recorded expected values) proves behavior survived without the vendor.

## The general form

Anything where the vendor is both a library *and* a place: [auth0/cognito (tenant data lives on their
side)], [segment/analytics (the pipeline is configured externally)], [a hosted Postgres (the driver
is the seam; the console is the exemption)]. The rule generalizes: seal the code-side knowledge
absolutely, name the runtime-side surface explicitly, and rehearse the migration path so the swap
test stays a fact, not a feeling.
