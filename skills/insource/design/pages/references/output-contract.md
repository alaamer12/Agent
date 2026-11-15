# The output contract — one story for every page of every kind

**A page is one row, one canon, one build.** Whatever kind it is and whichever mode produced
it, the full output story is fixed here and nothing else restates it:

```
decide (mode method) → register (PAGES.md row, kind = its section) →
canon location (one place the content lives) → build (the linked engineering owner)
```

| step | owner | rule |
|---|---|---|
| **Register** | `pages-md-format.md` | every page gets exactly one row: §4 main / §5 secondary / §6 complementary. No page exists that PAGES.md does not list; no row exists without the decision trail (status, evidence, reason-on-exclusion). |
| **Canon** | this contract | one canonical location per page or document — the row names it. Other surfaces link/redirect/embed it; a bundled or mirrored copy is a DECLARED synced duplicate, never a second original. |
| **Build** | the mode's linked engineering owner | `main` → the project's own stack conventions (the map decides routes; the implementation skill builds); `secondary` → `../secondary/references/engineering.md` (identity from config, templates as files, static rendering, SEO on web canons); `complementary` → `../complementary/references/anatomy.md` (the six-field contract) plus the project's build. |

## What the contract forbids

- **Type/family references never own output.** A doc like `status.md` or `http-errors.md` owns
  *content requirements and copy laws*; the moment it starts prescribing its own file layout,
  rendering pipeline, or registration process, that is this contract's material duplicated —
  replace it with a link. Domain-specific engineering that genuinely has no home elsewhere
  lives as a short "extra over the engineering contract" line, not a parallel build story.
- **No second registry.** PAGES.md is the only inventory; the index/catalog files inside each
  mode are candidate lists and method material, never competing outputs of what exists.
- **Same-change duty.** The row and the page move together — creation, update, removal. A
  page changed in code but not in PAGES.md is, per the format doc, a map defect; the reverse
  is a phantom row.
- **One owner per cross-cutting fact** (secondary set): the ownership table in
  `../secondary/references/catalog.md` decides which document canonically states retention,
  violations, refund windows, jurisdiction, contact routes. Everyone else links.