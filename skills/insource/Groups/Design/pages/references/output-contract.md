# The output contract — one story for every page of every kind

**A page is one file, one canon, one build.** Whatever kind it is and whichever mode produced
it, the full output story is fixed here and nothing else restates it:

```
decide (mode method) → register (a page file + its index entry, kind on the map) →
canon location (one place the content lives) → build (the linked engineering owner)
```

| step | owner | rule |
|---|---|---|
| **Register** | `pages-tree-format.md` | every page gets exactly one file under `<docs>/pages/` and one entry in its shard index; the root index map carries its kind (main / secondary / complementary) and status. No page exists that the tree does not hold; no file exists without its decision trail (status, evidence, reason-on-exclusion) on the map. |
| **Canon** | this contract | one canonical location per page or document — the page file's `url` names it. Other surfaces link/redirect/embed it; a bundled or mirrored copy is a DECLARED synced duplicate, never a second original. |
| **Build** | the mode's linked engineering owner | `main` → the project's own stack conventions (the tree decides routes; the implementation skill builds); `secondary` → `../secondary/references/engineering.md` (identity from config, templates as files, static rendering, SEO on web canons); `complementary` → `../complementary/references/anatomy.md` (the six-field contract) plus the project's build. |

## What the contract forbids

- **Type/family references never own output.** A doc like `status.md` or `http-errors.md` owns
  *content requirements and copy laws*; the moment it starts prescribing its own file layout,
  rendering pipeline, or registration process, that is this contract's material duplicated —
  replace it with a link. Domain-specific engineering that genuinely has no home elsewhere
  lives as a short "extra over the engineering contract" line, not a parallel build story.
- **No second registry.** The tree is the only inventory — one file per page. The shard indexes
  are maps that link and describe; the index/catalog files inside each mode are candidate lists
  and method material, never competing outputs of what exists.
- **Same-change duty.** The file, its index entry, and the page move together — creation,
  update, removal. A page changed in code but not in the tree is, per the format doc, a map
  defect; the reverse is a phantom file.
- **One owner per cross-cutting fact** (secondary set): the ownership table in
  `../secondary/references/catalog.md` decides which document canonically states retention,
  violations, refund windows, jurisdiction, contact routes. Everyone else links.