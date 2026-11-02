# Worked audit — "full working app" that was never built or run

## The ask and the claim

> User: "Build me a full working inventory app - items, add/edit, saved locally."
>
> Delivery: "Done! Implemented the inventory app: items list, add/edit screens, local persistence,
> validation. The code is in `app/`."

Three paragraphs of claim, zero artifacts. This is the audit.

## Step 0 — the bar written before anything was run

```text
Done = all of:
  1. App builds on a clean checkout       [L1]
  2. App launches, home screen renders    [L3-L4]
  3. Add an item -> appears in list       [L4]
  4. Restart -> the item is still there   [L4]
  5. Edit an item -> change persists      [L4]
  6. Empty state renders before any data  [L4]
  7. README's run steps reproduce 1-2     [L1-L3]
Not part of this verification: styling quality, multi-device, cloud sync (not asked).
```

## The sweep (abridged)

| Check | What it found |
|---|---|
| Requirements coverage | Add/edit exist as screens; persistence code exists; validation branch exists. Artifacts present. |
| Implementation completeness | 3 `TODO`s: "wire save button", "handle storage error", "remove sample rows". The list screen renders a hardcoded sample array. |
| Build | `[build]` -> exit 1: missing dependency in the manifest. |
| Tests | none in the repo; the claim said "validated" with no test output anywhere. |
| Integration | not run: app never launched. |
| Consistency | README's run command names a script that does not exist. |
| Proof of work | every claim maps to L0 only - files exist. The "validation" claim has no artifact. |

## The report

```markdown
# Verification report — inventory app

**Verdict:** INCOMPLETE
**Verified against:** the user's ask ("full working app: items, add/edit, saved locally")
**Scope:** build, launch, core flows, persistence · **Not reached:** none (small scope)
**Environment:** Windows, project toolchain from its manifest

## The bar
1. Builds on clean checkout [L1]
2. Launches, home renders [L3-L4]
3. Add item -> list [L4]
4. Restart -> item persists [L4]
5. Edit persists [L4]
6. Empty state [L4]
7. README reproduces build/launch [L1-L3]

## Evidence table
| # | Requirement | Artifact | Evidence | Level | Status |
|---|---|---|---|---|---|
| 1 | Builds | repo root | `[build]` -> exit 1: missing dependency | L0 | FAIL |
| 2 | Launches | - | not run; blocked by 1 | - | UNVERIFIED |
| 3 | Add item | `app/AddItem` | button has `TODO: wire save`; list uses sample rows | L0 | INCOMPLETE |
| 4 | Restart persists | `app/storage` | code exists; never executed | L0 | UNVERIFIED |
| 5 | Edit persists | `app/EditItem` | exists; never executed | L0 | UNVERIFIED |
| 6 | Empty state | `app/List` | hardcoded sample data; empty path absent | L0 | INCOMPLETE |
| 7 | README reproduces | README | names a script that does not exist | L0 | FAIL |

## Blockers
- The project does not build (missing manifest dependency).
- The save button is unwired; the list is sample data - "add/edit" cannot work yet.

## Missing proofs
- Launch + add + restart, at L3-L4, once the build is fixed.
- "Validation" from the delivery claim: no artifact exists.

## Next actions
1. Fix the manifest dependency; get the build to exit 0.
2. Wire the save button; replace sample rows with the real store.
3. Launch the app, add an item, restart, confirm it persists.
```

## The lesson in one line

Every claim in the delivery was **L0 - it exists**. The verdict could not exceed that level, and the
honest label for "never launched" is UNVERIFIED, not "probably fine". The sweep took one build attempt to
turn the entire claim into a concrete, fixable list.

## Second shape — the false PASS

Same app, but this time a test suite exists and passes:

- `[test]` -> 14 passed, L2.
- `[run]` -> the app crashes on boot: unhandled storage permission error (the `TODO` from before).
- Verdict: **BROKEN** - green tests over an app that never starts is the canonical false PASS; L2 does not
  buy L3.
