# Tiered Walkthrough: raw → tiers 1–3

> **For the tiered system** (this skill). The general (non-tiered) walkthrough lives in `/type-up`.

Per-tier detail is in [`../references/tiers.md`](../references/tiers.md); conversion steps are in [`../references/migration.md`](../references/migration.md). This file runs complete examples end to end.

Identifiers are illustrative role names (the naming rules: `/type-up`).

## Where the files go

Tier 1 files go in `shared/types/primitives/`; tier 2 in `features/<owner>/types/brands/` (or `shared/types/brands/` if two or more features use them); tier 3 in the matching `shapes/` folder — example names, the project's convention wins ([structure](../references/tiers.md#2-structure--where-the-tier-folders-go)).

## Example 1: one field through every tier

The bug: module A lowercases an email, module B does not.

| Step | Action | Result |
|------|--------|--------|
| 1 | name the raw type by what it means | an email is not "any string": `PlainString` is only a temporary marker while migrating, and the end state is a brand |
| 2 | every module lowercases, a visible state | tier 1: `LowercaseString` + creation point (trimming stays a step in the brand's creation point) |
| 3 | it means "a user's email" | tier 2: `UserEmail`, policy `[normalize then reject]` |
| 4 | it travels with other user fields | tier 3: `UserSchema { iso, email, name, age? }` |
| 5 | it arrives from a request body | boundary check: raw request body → `UserSchema` |

End state of steps 2 to 4, in TypeScript (the other languages follow their own idioms in [tiers](../references/tiers.md)):

```ts
type UserEmail  = LowercaseString & Brand<"UserEmail">;
type UserSchema = { iso: UserIso; email: UserEmail; name: UserDisplayName; age?: UserAge };

function findUser(email: UserEmail) { /* … */ }     // an ordinary function: no conversion function is called here
findUser(typed);                  // error: 'string' is not assignable to 'UserEmail'
findUser(typed.toLowerCase());    // still an error: toLowerCase() returns a plain string

function isUserEmail(s: string): s is UserEmail {   // the one creation point, where a runtime string enters
  return s === s.toLowerCase() && /^[^@\s]+@[^@\s]+$/.test(s);
}
if (isUserEmail(typed)) findUser(typed);            // narrowed: ok
```

Module B can no longer forget the lowercase step: the compiler refuses a plain string wherever a `UserEmail` is required.

## Example 2: promoting an existing raw configuration

Start (shown in pseudo-neutral form, any language): `checksDir: text`, `workers: number`, `scanMode: text`.

| Field | Step 1 | Step 2: generic rule | Step 3: brand | Tier 3 |
|-------|--------|---------------------|---------------|--------|
| `checksDir` | `PlainString` | `NonEmptyString` | `PathValue` | `ResolvedConfig.checksDir` |
| `workers` | `PlainNumber` | `PositiveIntNumber` | `WorkerCount` (reject if above `[256]`) | `ResolvedConfig.workers` |
| `scanMode` | `PlainString` | closed set | `ScanMode` = `[full]`, `[changed]`, `[staged]` | `ResolvedConfig.scanMode` |

Variants: `RawConfig` (unvalidated file), `ConfigPatch` (CLI overrides), `ResolvedConfig` (after defaults). Step 5: the boundary check for the config; nothing inside the app sees an unparsed config. See [migration §4](../references/migration.md#4-the-boundary-and-variants).

## Example 3: state as a tagged union

Replace `{ isLoading, error?, results? }` with four cases (`idle`, `loading`, `success(results)`, `error(message)`). The language's exhaustive-match feature (TypeScript `switch` on `kind`, Python `match`, Go type switch over a sealed interface, Rust `match`) then flags any unhandled case at check time. Full per-language types: [tiers §7](../references/tiers.md).

## Example 4: adding a new field later

1. Does a tier 1 refinement already express its generic rule? Reuse it, or add it (with creation point) to the primitive-family file.
2. Define the tier 2 brand with one creation point and a stated policy.
3. Add the brand to the tier 3 shape.
4. Update the boundary check and `toWire`.
5. Add creation point property tests and the catalog row in the same commit.
