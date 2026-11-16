## Specialization: `specialized` frontmatter

Every independent skill in this registry declares, next to `name` and `version`, whether it is bound to one framework, library, language, or file format, or applies in general:

```yaml
---
name: scss
version: 1.0.0
specialized: scss
description: ...
---
```

```yaml
---
name: dtb
version: 1.0.0
specialized: none
description: ...
---
```

| Value | Meaning | Examples |
|---|---|---|
| `none` | A general skill: a method, posture, or workflow that works across technologies. Polyglot examples inside it do not make it specialized. | `dtb`, `iwts`, `planner`, `update`, `readme-md` |
| one technology | The skill's rules only make sense inside that technology. | `scss` → `scss`, `gh` → `github`, `pdf` → `pdf` |

Rules:

- **Name the umbrella technology, not its toolkit.** A Tailwind skill that recommends `cva` or `clsx` is `specialized: tailwind`; helper libraries used *inside* that technology are not listed.
- **One value.** A comma list such as `specialized: react-native, expo` is accepted, but lint warns on it: a skill should focus on one technology. Split the skill, or name the technology that actually owns the rules.
- **Format.** Lowercase, no spaces: letters, digits, and `-`, `.`, `+`, `#` (for example `react-native`, `next.js`, `c#`). Blank values, `general`, `n/a`, or YAML lists are invalid; general skills use exactly `none`.
- **Where it applies.** Required on every independent skill's `SKILL.md` in this registry: plain skills, Meta-Skill parents, and each Meta-Skill child. Battery-Skill modules (`method.md` or no file) carry no frontmatter and inherit the battery's value. Skills installed into agent folders from other sources are not checked.

`python manager.py lint` reports a missing, invalid, multi-value, or non-canonical `specialized` as a skill warning; `lint --strict` fails on it.

### Naming conventions for `specialized` values

One spelling per technology, chosen from how this inventory already writes it. Lint rejects known aliases and points at the canonical form.

**Dialect: American English.** The inventory overwhelmingly uses `color` (677 vs 298), `behavior` (676 vs 159), `organize`/`organization`, `optimize`, `catalog` (739 vs 19), `center`, `gray`, and `license`. New prose, values, and keys follow American spelling; the frontmatter key is `specialized`, not `specialised`.

**Canonical technology names** (lowercase; the official project name as its own docs write it, with spaces become hyphens and abbreviations expanded):

| Canonical | Rejected aliases |
|---|---|
| `tailwind` | `tailwindcss`, `tw` |
| `react-native` | `react native`, `rn` |
| `next.js` | `nextjs` |
| `vue` | `vuejs`, `vue.js` |
| `node.js` | `nodejs`, `node` |
| `typescript` | `ts` |
| `javascript` | `js` |
| `postgresql` | `postgres` |
| `scss` | `sass` is a *different* syntax; use `sass` only for a skill that targets the indented Sass syntax |
| `mermaid` | `mmd` |
| `github` | `gh` |
| `git` | — |
| `win32` | `windows`, `winapi` (the OS is not the API) |
| `dotnet` | `.net` (a leading dot is not a valid value) |
| `c#` | `csharp` |
| `svelte` | `sveltekit` is a separate framework; use it only for a SvelteKit-specific skill |
| `svg`, `pdf`, `hyperframes`, `navigo` | — |

Rules for picking a name not in the table:

1. Lowercase the official name (`PostgreSQL` → `postgresql`, `Next.js` → `next.js`).
2. Prefer the full name over an abbreviation (`typescript`, not `ts`; `github`, not `gh`).
3. Multi-word official names use hyphens (`react-native`); never spaces.
4. A framework and its meta-framework are different values (`vue` vs `nuxt`, `svelte` vs `sveltekit`, `react` vs `next.js`).
5. A file format or platform API counts as a technology when the skill's rules are specific to it (`pdf`, `svg`, `win32`); a broad platform like "web" or "mobile" does not — those skills are `none`.

### Adding a specialized skill to a battery

A specialized skill is an independent, technology-bound skill (`specialized: <tech>`) grouped under a
platform-neutral parent battery, inside the parent's `specialized/` folder. It keeps its own `SKILL.md`,
so it is a **Meta-Skill child, not a battery module**. The parent's own method stays platform-neutral, so
the parent keeps `specialized: none` — hosting specialized children does not bind the parent to a
technology. Live example: [`styling`](../styling/SKILL.md) (`none`) hosts
[`scss`](../styling/specialized/scss/SKILL.md) (`specialized: scss`).

1. **Create the child as a real skill.** `<battery>/specialized/<name>/SKILL.md` with full frontmatter:
   `name`, `version`, `specialized: <canonical value from the table above>`, `description`, plus
   `when_to_use`, and `argument-hint` whenever the child presents commands or modes (required by the
   argument-hint rule, see [argument-hint.md](argument-hint.md)). Do **not** rename it to `method.md` — that demotes it
   to an internal module. Give it its own references/examples/scripts as the technology needs.
2. **Split ownership, one owner per fact.** The parent owns the universal, platform-neutral laws; the child
   owns its technology's mechanics and applies those laws in its idiom. The child defers to the parent on
   architecture; the parent defers to the child on language specifics. Never restate the parent's laws
   inside the child.
3. **Wire the parent router.** In `<battery>/SKILL.md`: keep `specialized: none`; add a "Specialized skills"
   section with a table naming each child and when to reach for it; add `specialized/<name>` to the Layout
   tree. Reference the child **by name** (`/<name>`), not by a cross-skill file path — separately installed
   skills' junctions break path links between them.
4. **Install the child on its own.** Nesting does not install it. The child is an independent skill and needs
   its own junction so `/<name>` resolves (`python manager.py skill <name>`); the parent's junction only
   exposes the files. If the parent tree later moves inside the registry, `python manager.py skill --refresh`
   repoints nested children's junctions too — resolution falls through to a unique nested match.
5. **Catalog and version.** Add the child's Quick Index bullet and detail block at its real path
   `<battery>/specialized/<name>/SKILL.md`; keep the parent's row. The child carries its own `version`; bump
   the parent for the router change. Regenerate the README and run `lint`.
6. **Accept the hybrid finding.** A battery that keeps internal `method.md` modules *and* hosts an
   independent specialized child is a mixed-composition hybrid (part Battery-Skill, part Meta-Skill). Record
   the decision on the parent with `lint-accept: { mixed-composition: "<reason>" }` (see
   [Accepting lint findings](lint-accept.md#accepting-lint-findings-lint-accept)) rather than leaving a warning or deleting
   the child's `SKILL.md`. `styling` carries this acceptance.

**Moving an existing standalone skill in** is the same procedure with a `git mv` into
`<battery>/specialized/<name>` first: then retarget the child's junctions to the new path, update every
README path pointer, wire the parent router, and add the acceptance. Leave no stale copy of the old location.
