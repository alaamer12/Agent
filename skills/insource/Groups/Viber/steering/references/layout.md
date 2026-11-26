# Layout, Indexes, Areas, and Tiers

> This document describes how the steering tree is laid out, indexed, and split into areas across the Two-Tier Steering Taxonomy. See [`index.md`](index.md) for the master map.

## 1. Top-Level Two-Tier Structure

The `.steering/` directory is split into two primary branches:

```text
.steering/
  index.md
  perception/            Business understanding, stable across technical rewrites
    index.md
    shared/              Minimal canonical facts needed by every area
    <area>/              Local delta only; links shared facts without repeating them
  tech/                  Technical architecture, engineering standards, and execution
    index.md             (Optionally versioned as tech/v1/, tech/v2/ for major architectural rewrites)
    shared/
    <area>/
```

---

## 2. Folders per Tier

No folder is mirrored across both tiers. Each tier has its own dedicated concerns:

### Perception Tier (4 Folders)
- **`product/`**: Why the product exists, for whom, and high-level objectives.
- **`domain/`**: Nouns, entities, roles, lifecycle states, and structural relationships.
- **`capabilities/`**: What the platform provides or does across features.
- **`policy/`**: What is allowed, forbidden, and who holds decision authority.

### Tech Tier (5 Folders)
- **`stack/`**: What tools the project is built with ("We use X").
- **`structure/`**: Static repository organization, package boundaries, and pattern-first placement rules with illustrative or observed tree snapshots.
- **`function/`** (**steering function folder**): System-wide technical runtime mechanisms across features.
- **`doctrine/`**: Engineering guidelines and non-negotiable technical mandates for a specific part.
- **`playbook/`**: Step-by-step operational recipes to run or configure tasks.

---

## 3. Mandatory Tech Directory Interview Matrix

Before proposing or writing the tree, enumerate the actual areas and create one Tech Directory Decision Ledger row for each existing or planned tech concern folder:

```text
<area>/
  stack/
  structure/
  function/          (steering function folder)
  doctrine/
  playbook/
```

Apply the same matrix to `shared/` and every confirmed area. Do not mirror all five folders mechanically: mark an absent folder **Not applicable** only after the user confirms no content is planned. Interview in-scope folders separately using their reference questionnaires, record evidence and decisions, and obtain a user-confirmed recap for each one. The complete gate is in [`documentation-conventions.md`](documentation-conventions.md#mandatory-tech-directory-interview-and-authoring-gate).

A topology is not an interview. No directory may contribute examination, design, mapping, or steering-file content until its ledger row is **Settled**.

---

## 4. index.md Convention

Every directory in `.steering/` (including the root, tier roots, shared directories, area directories, and individual concern folders) must contain an `index.md`.
- It is a clean list of files with a one-line description per entry.
- The name `README.md` is **never** used inside `.steering/`.
- Indexes are updated in the same change as the files they list.
- In the `tech/` tier, every index file covering `function/` includes the mandatory **steering function folder** terminology reminder.
- An index is a current-file snapshot, not a closed set. The owning `structure/` document defines how new files join; example paths do not become mandatory homes.

---

## 5. Shared Content and Areas

When a project encompasses multiple applications or surfaces (e.g., `web`, `mobile`, `admin`, `api`), steering files follow the **shared-plus-area** pattern within each tier. `shared/` is the **minimal canonical common core**: not a default destination, a catch-all for common-looking material, or a union of every area's content.

### Universal Scope Test

Before placing any passage in `shared/`:

1. **Enumerate the confirmed areas.** Never invent an area split just to populate `shared/`. If the project has only one area, keep content in that area unless the user explicitly chooses a canonical shared root.
2. **Require every area.** Admit a fact only when it is applicable and needed by **every** confirmed area without area-specific qualification. "Cross-feature," "used by several areas," and "true for most areas" do not pass.
3. **Reject subset or uncertain scope.** If only one area needs it, place it there. If only a subset needs it or no owner is clear, keep it with the owning area and let other areas link, or ask the user; never park it in `shared/` to avoid deciding.
4. **Recheck after topology changes.** Adding or removing an area can invalidate a shared fact. Move or retire content that is no longer universal.

### Minimalist Shared Contract

- State each common fact once, clearly enough to stand alone. Minimalist means **no local delta**, not vague or incomplete.
- Keep area-specific sections, examples, exceptions, appendices, and summaries out of shared files. Never merge area documents into a shared superset.
- Keep dependency direction one-way: **area files link to shared files; shared files do not link to or depend on area files**. This prevents cycles and preserves the common core.
- Keep each `shared/` index limited to shared files; do not copy area entries into it.

### Area Delta Contract

- When an area inherits a shared fact, link to the canonical shared file and write **only the area's additional facts, constraints, or approved variations**.
- Do not copy or paraphrase the shared normative content, clone the shared file, or create a same-named shadow that overrides it.
- Record an approved exception with its authority and exact scope. If the exception contradicts the shared universal claim, flag the conflict and reopen the scope decision instead of overriding shared content.

**Example.**

`tech/shared/doctrine/test-invariants.md` holds only the invariants required by every area. `tech/web/doctrine/web-test-invariants.md` links to it and adds only the web-specific testing requirement; it does not restate the shared invariants.

---

## 6. Sample Two-Tier Layout (Illustrative)

This tree illustrates the steering taxonomy; its folder roster is closed. The filenames are examples, not required content or a complete inventory. Files inside `structure/` follow the [pattern-first authoring rule](structure.md#pattern-first-authoring-rule), so their own trees may grow without turning example paths into mandates. Area files contain only local deltas; omit any file that would merely repeat a linked shared fact.

```text
.steering/
  index.md
  perception/
    index.md
    shared/              # minimal core: only facts every area needs
      index.md
      product/        index.md  overview.md
      domain/         index.md  user-tiers.md
      capabilities/   index.md  periodic-sync.md
      policy/         index.md  non-negative-balance.md
    web/
      index.md
      capabilities/   index.md  responsive-experience.md  # local delta; link shared when inherited
    admin/
      index.md
      capabilities/   index.md  cms-controls.md           # local delta; link shared when inherited
  tech/
    index.md
    shared/              # minimal core: only facts every area needs
      index.md
      stack/          index.md  platform.md
      structure/      index.md  repo-layout.md
      function/       index.md  external-feed-sync.md
      doctrine/       index.md  test-invariants.md
      playbook/       index.md  seed-demo-data.md
    web/
      index.md
      stack/          index.md  client-framework.md     # local delta; link shared when inherited
      structure/      index.md  client-tree.md          # local delta; link shared when inherited
    admin/
      index.md
      stack/          index.md  admin-framework.md      # local delta; link shared when inherited
      structure/      index.md  admin-tree.md           # local delta; link shared when inherited
```
