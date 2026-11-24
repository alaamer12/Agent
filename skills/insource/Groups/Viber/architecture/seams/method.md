# Seams Pillar — Method

> Route here when the question is **who is allowed to know the third party**. The pillar places one
> seam per external capability, keeps vendor knowledge sealed behind it, and hands enforcement to
> armed walls. Doctrine spine: [references/seam-doctrine.md](references/seam-doctrine.md) — read it
> first; every step below instantiates it.

## 1. Scope

**Owns**
- The seam inventory: every external capability, classified by taxonomy, mapped to exactly one seam.
- Placement: where the contract lives per stack (module export, interface + registration, barrel,
  build-config exemption row) and which files count as *part of* each seam.
- Naming law: project vocabulary upward, vendor name on one line only.
- Composition ladders: which rung applies which utility, and what inner rings may never know.
- The two walls: import wall, markup wall, and the probe that decides which one you need.
- Severity: hard-zero vs ratcheted vs expiring allowance — the seam-rule judgment.
- Migration: disjoint batches, counts keying, codemod proof.
- Adoption cost: per-component intake and the internals ledger.

**Does NOT own**
- Where a gate runs, at which tier, at what cost, and what failing means: the `gates/` pillar. This
  pillar designs the rules and arms them; gates registers and places them.
- Role placement inside the UI (Page/View/Component tiers): skill `pvc`. Seams govern *knowledge*,
  not responsibility.
- Whether a swap looks right or performs better: skill `spike`. A spike usually triggers a seam
  audit; it never writes one.
- How the library itself wants to be used: skill `treat`. The seam decides who may talk to it once
  that is known.
- Fixture and fake design behind the seam: the `testing/` pillar (it consumes this pillar's seams as
  determinism points).

## 2. Workflow

```
- [ ] 1 Live research for each confirmed vendor/framework and its ecosystem's
      boundary idioms (queries below).                                    invariant of the skill
- [ ] 2 Inventory external capabilities: dependencies, generated clients,
      platform APIs, service SDKs, framework primitives.                  §3 below
- [ ] 3 Classify each capability by taxonomy; one seam per capability.    seam-doctrine.md §4-5
- [ ] 4 Place each seam and name it in the project's vocabulary; decide
      which files are *part of* the seam (build config, registration).    seam-doctrine.md §1, two-walls.md §0
- [ ] 5 For capability-on-function joins, draw the ladder: ring order,
      one responsibility per rung, upward-blindness checked.              seam-doctrine.md §3
- [ ] 6 Run the build probe; decide import wall, markup wall, or both.    two-walls.md §3
- [ ] 7 Fill the rule table before writing any auditor.                   assets/rule-table.md
- [ ] 8 Split severity by the judgment test; arm the gate with the eight
      checks; hand tier/budget/register rows to the gates pillar.         arming-the-gate.md, → gates/method.md
- [ ] 9 Existing debt? Migrate: disjoint batches, counts keying, codemod
      proof, starting count stated in the same commit.                    migration-batches.md
- [ ] 10 Adopted components: run the intake checklist, open a ledger row
      per component.                                                      ownership-transfer.md §4-5
- [ ] 11 Author <docs>/architecture/seams-architecture.md from
      assets/templates/seams-architecture-template.md; every pending
      decision is a numbered open item, never a silent default.
```

Worked shapes by world — read the one closest to your capability before placing: **[UI/markup]**
cases 01–03 (dead glob, importless leak, ownership transfer); **[backend vendors]** case 04 (payment
gateway — the three leak faces: import, type, string); **[backend ladders]** case 05 (API client,
caching rung); **[vendors with a control plane]** case 06 (feature flags — where the doctrine meets
its own limit and the exemption row carries the runtime half).

**Research queries (step 1), per confirmed stack:**
`"<framework> auto-import component resolution"`, `"anti-corruption layer <ecosystem>"`,
`"vendor lock-in adapter module <language> best practices"`,
`"<build tool> tree-shaking barrel sideEffects"`, `"<platform> native module wrapper pattern"`.
Cross-check against current docs before recommending any idiom — obsolete paradigms are exactly what
live research exists to prevent.

## 3. The seam inventory (step 2 output)

One row per external capability, the document's spine:

| Capability | Kind (utility/usability/framework/vendor/contract) | Seam file/registration | Public name | Wall(s) | Rule code(s) | Swap touches |
| --- | --- | --- | --- | --- | --- | --- |

A capability with no row is unsealed: it is the finding the walls would report. A row whose
"Swap touches" column names more than its own seam file has not passed
[the swap test](references/seam-doctrine.md#6-why-it-pays-and-the-test-that-proves-it).

## 4. Cross-pillar reconciliation

- **`gates/`** — every hard-zero/ratcheted rule registered in §2 step 8 must appear in the gates
  register (rule → gate → tier → owner → evidence → exception). A wall with no register row is
  advice, not architecture.
- **`cross-platform/`** — View Barrels are framework seams; the barrel is the seam file for platform
  widgets, and the vendor-seal audit's platform-idiom codes ([specs/vendor-seal-audit-spec.md](specs/vendor-seal-audit-spec.md))
  are its per-axis instance. Axis *naming and dispatch* stays in `cross-platform/`; who may *know*
  the platform SDK is decided here.
- **`plugin/`** — the Open/Closed gate's "if shared code appears, the seam is wrong" is this
  pillar's swap test applied to extension points.
- **`testing/`** — seams are the legal faking points; the generator registry consumes the seam
  inventory, never the vendor directly.
- **`language/`** — contract seams are where the typing tier's "no vendor types in public APIs"
  boundary check lands.

## 5. Evidence standard

The pillar's claims are mechanical, so the evidence is too: probe outputs, planted violations that
fired, liveness counts printed per rule, ledger rows, and one-file swaps proven on branches. A seams
document quoting "the boundary is held" without a fired fixture or a match count is reporting the
absence of a look. When the tree and the rule disagree, the rule's scope is suspect first — the
auditor is pointed at the same config as liveness
(`scripts/glob-liveness.mjs`), and the parity script keeps docs and registry naming the same codes
(`scripts/rule-code-parity.mjs`, `--help` for usage).
