# Layout, indexes, areas, and agents

> This document describes how the steering tree is laid out and entered: the `index.md` convention, the shared-plus-area pattern, how agents start, and a sample layout. It does not define the folders themselves; see the [index](index.md) for the set.
> **Terminology reminder.** The steering folder whose directory name is `function` is always called the **steering function folder**, never just "function". Full rule: [function.md](function.md).

## index.md

Every folder, including the top level, has an `index.md`. It is a plain list of names with one line each. The name `README.md` is intentionally **not** used for navigation and stays free for another purpose later. Indexes are updated in the same change as the files they list.

## Shared content and areas

A project may have one or several areas, such as separate apps or other distinct parts. This taxonomy does not say how many there are or what they are called. When there are several, the steering folders follow a shared-plus-area pattern:

- A shared directory holds what is common to all areas. The name is each project's choice.
- Each area repeats only the folders it needs, and adds its own files.
- **Nothing is overridden.** Shared content must not be overloadable. An area adds files, it never replaces a shared file with a same-named one.
- Consequence: the shared directory may contain only what is true for **every** area. A fact that is true for only one area belongs in that area.

Example: the shared stack facts live in the shared directory, and one area adds a single extra stack file for the part that is specific to it.

## Agents

How agents navigate the wiki is not governed here. In general, an agent first reads the `AGENTS.md` file, which points it onward.

## A sample layout (illustrative)

Layout is not prescribed: how many areas there are, what they are called, and where the shared directory lives are left to each project. The exact placement is each project's choice. This shows the shape.

```
.steering/
  index.md
  shared/
    index.md
    doctrine/   index.md  test-quality.md  data-deletion.md
    stack/      index.md  frontend.md  backend.md
    structure/  index.md  styles.md
    product/    index.md
    function/   index.md  error-ux.md  client-lifecycle.md
    playbook/   index.md  run-in-containers.md  db-tables.md  seed-test-data.md  release-new-version.md
  <area>/                  (repeated for each area the project has, if any)
    index.md
    stack/      index.md  area-only-libraries.md
```

Feature documentation and other documentation folders, such as decision records, sit alongside and are outside this taxonomy (see [placement.md](placement.md)).
