# Layout, Indexes, Areas, and Tiers

> This document describes how the steering tree is laid out, indexed, and split into areas across the Two-Tier Steering Taxonomy. See [`index.md`](index.md) for the master map.

## 1. Top-Level Two-Tier Structure

The `.steering/` directory is split into two primary branches:

```text
.steering/
  index.md
  perception/            Business understanding, stable across technical rewrites
    index.md
    shared/              What is true across every area
    <area>/              What is true for one specific area
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
- **`structure/`**: Static repository organization, package boundaries, directory trees, file naming.
- **`function/`** (**steering function folder**): System-wide technical runtime mechanisms across features.
- **`doctrine/`**: Engineering guidelines and non-negotiable technical mandates for a specific part.
- **`playbook/`**: Step-by-step operational recipes to run or configure tasks.

---

## 3. index.md Convention

Every directory in `.steering/` (including the root, tier roots, shared directories, area directories, and individual concern folders) must contain an `index.md`.
- It is a clean list of files with a one-line description per entry.
- The name `README.md` is **never** used inside `.steering/`.
- Indexes are updated in the same change as the files they list.
- In the `tech/` tier, every index file covering `function/` includes the mandatory **steering function folder** terminology reminder.

---

## 4. Shared Content and Areas

When a project encompasses multiple applications or surfaces (e.g., `web`, `mobile`, `admin`, `api`), steering files follow the **shared-plus-area** pattern within each tier:

- **`shared/`**: Contains only what is universally true for **every** area.
- **`<area>/`**: Adds files specific to that area.
- **Nothing is overridden**: An area directory adds files; it never replaces or overrides a same-named file in `shared/`.

---

## 5. Sample Two-Tier Layout (Illustrative)

```text
.steering/
  index.md
  perception/
    index.md
    shared/
      index.md
      product/        index.md  overview.md
      domain/         index.md  user-tiers.md  group-competitions.md
      capabilities/   index.md  virtual-trading.md  periodic-sync.md
      policy/         index.md  non-negative-balance.md  org-creation-policy.md
    web/
      index.md
      capabilities/   index.md  responsive-experience.md
    admin/
      index.md
      capabilities/   index.md  cms-controls.md
  tech/
    index.md
    shared/
      index.md
      stack/          index.md  platform.md
      structure/      index.md  repo-layout.md
      function/       index.md  external-feed-sync.md
      doctrine/       index.md  concurrency-invariants.md  test-invariants.md
      playbook/       index.md  seed-demo-data.md  rotate-api-keys.md
    web/
      index.md
      stack/          index.md  client-framework.md
      structure/      index.md  client-tree.md
    admin/
      index.md
      stack/          index.md  admin-framework.md
      structure/      index.md  admin-tree.md
```
