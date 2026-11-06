---
name: seam
description: Place and enforce the one file that knows the third party - the framework, the vendor SDK, the platform driver - so every layer above it speaks the project's own vocabulary. Covers the import wall and the markup wall, hard-zero versus ratcheted severity, arming a gate (glob liveness, planted violations, controls, doc/registry code parity, one baseline per auditor, wall-time budget), where enforcement actually bites, disjoint migration batches and counts-file keying, codemod mechanics, and the per-component ownership that adopting a framework component transfers. Use when someone says "only X may be used in Y" and nothing enforces it, when a component swap is planned, or when a boundary rule has been green for a suspiciously long time.
argument-hint: "<the boundary to place, or the auditor to arm>"
---

# Seam

Who is allowed to know what. A **seam** is the one file that knows the third party, so every layer above it speaks the project's own vocabulary and the third party becomes replaceable by editing that file. A **wall** is the check that keeps the claim true when the next person forgets it exists.

_Use it when someone says "only X may be used in Y" — and nothing enforces it._

## Scope

**Includes**
- Placing the seam: which tier knows the framework, what it hands upward, and the naming law that keeps the vendor's name on exactly one line (`Button`, never `VendorButton`).
- Both walls: the **import wall** (who may `import` it) and the **markup wall** (who may *use* it while importing nothing).
- Severity: what is hard-zero, what is ratcheted against a blessed baseline, and why the split is a judgment test.
- Arming: proof each rule can fire, that each scope matches a real file, that docs and registry name the same codes, that each auditor owns its own baseline, and that the audit is affordable.
- The migration: disjoint per-file batches, counts-file keying, codemod mechanics; exemptions as data (a marker, a reason, a ledger row), never prose in a comment.
- What adoption costs: the component's internals become yours, per component — and deleting hand-written code in favour of a vendor component *is* an adoption, whatever the diff statistic says.

**Excludes**
- Role placement inside the UI — tiers are `pvc`. A seam governs *knowledge*, not responsibility; they overlap once (a component layer may not skip to the seam) and disagree usefully the rest of the time.
- What the library itself wants to be used like — that research is `treat`. The seam decides who may talk to it once that is known.
- Whether a swap is worth it, visually or behaviourally — that measurement is `spike`. A spike usually triggers this skill; it never writes one.
- Designing the token/palette system (the seam only says which layer may name vendor internals), and commit wording: `commit`.

## Workflow

Copy this checklist; each step names the file that owns its detail.
```
- [ ] 1 Place the seam and name it in our vocabulary ................. the-two-walls.md
- [ ] 2 Probe: can the build resolve a name nobody declared? ......... the-two-walls.md §3
- [ ] 3 Fill the rule table before writing the auditor ............... assets/rule-table.md
- [ ] 4 Split severity by the judgment test .......................... arming-the-gate.md §2
- [ ] 5 Arm the gate: liveness, plants, controls, parity, one baseline per auditor,
      and a ratchet fixture that must PASS on a decrease ... arming-the-gate.md §1, §3
- [ ] 6 Decide where it bites: full-tree authority, a tested refusal, and a re-run on
      the merged trunk .......................................... arming-the-gate.md §4
- [ ] 7 State the audit's wall-time budget ........................... arming-the-gate.md §5
- [ ] 8 Migrate: disjoint batches, keying strategy, codemod proof ..... migration-batches.md
- [ ] 9 Intake every adopted component, add its ledger row ........... ownership-transfer.md
```

## The two walls

| Wall | Catches | Misses |
| --- | --- | --- |
| **Import** | vendor imports outside the seam, deep package paths, subpath aliases, dynamic and type-only imports, layer skipping the seam | anything resolved without an import |
| **Markup** | vendor tags in a template, vendor utility classes on our elements, raw platform primitives reaching around the seam, vendor names in identifiers | code that never reaches markup |

The second is not optional. A framework that resolves components **at build time** (auto-import, global registration, a compiler transform) leaves no import to find: the file imports nothing, the tag works, the type-checker is satisfied, and the strictest import lint in the world reports a clean tree. If you don't know whether yours can, run the probe — build a file that uses the vendor tag with no import. If it compiles, your import rule is decorative.

## Severity

| Kind | Rule | Stored where | Examples |
| --- | --- | --- | --- |
| **Hard-zero** | absent means clean; no baseline entry | nowhere | vendor import, tag or utility class outside the seam; a raw platform control reaching around it; a layer skipping the seam |
| **Ratcheted** | counts stored, only growth fails; re-bless every decrease in the same change | its own file, one per auditor | "a lower layer's appearance was overridden from above" — layout-on-the-parent is legal, colour-on-the-child is not |

Ratcheting a judgment-free rule encodes the debt the wall exists to remove. A ratchet never re-blessed downward is a lie being maintained. **Two auditors never share one counts file**: one careless regenerate would launder both rules, silently, in one commit.

## Adopting a component transfers its internals

When a framework component enters through the seam, **ownership of its internals transfers to the seam — per component, not once**: which node actually receives focus and where the visible ring lands, the extra child nodes it renders around what you authored, the style flags that silently override each other, and where your `class`/`style`/`data-*`/aria attributes fall through to. Every adopted component owes its own intake review and its own ledger row, and the twelfth owes as much as the first.

**The tell: a clean visual diff plus a broken keyboard or focus path.** If the only evidence that an adoption went well is that it looks right, you measured pixels and called it a component.

**The trigger is the vendor's name entering the tree, not the line count.** Deleting hand-written code in favour of a vendored component shrinks the file and *grows* the vendor surface; it owes the same intake and the same ledger row as an adoption that added lines. `-240 / +31` reads as a cleanup, which is how a new adoption gets waved through.

## Rules that prevent the usual failures

- One seam, one direction: everything above imports the project's name, never the vendor's.
- A seam file may be one line long. It is complete, not thin — the tier is about who knows whom.
- An exemption without a reason and a ledger row is a violation with better formatting.
- Green is not evidence: a rule whose scope matches zero files prints exactly what a clean tree prints — assert every configured glob matches ≥1 real file (`scripts/glob-liveness.mjs`).
- Docs and registry must name the same codes, in both directions (`scripts/rule-code-parity.mjs`).
- A wall added over existing violations states its starting count in the same commit; a hard-zero rule ships with the planted offence that proves it can fire.
- The counts file is generated, never hand-edited: key it **per file** while batches run in parallel, then do **one whole-tree bless** when the last lands, because per-file keys cannot see a violation moving between files. Never two people editing one total.
- A codemod must be idempotent, tag-only in its diff, and proven by fixture plus snapshot — **a diff that changes more than it claims is a rejected diff**, and you reject the run, not the offending lines.
- A local hook is bypassable and a staged-files-only check is bypassable by committing one bad file with good ones; the rule is only provable in the full tree, and you must test that a deliberate violating commit is refused.
- A ratchet that has never been shown to *permit* a decrease is a freeze wearing a ratchet's clothes: store the count one higher than the fixture's offenders and assert exit 0. Sabotage both directions — the check that passes on +1 and −1 is dead.
- Per-branch checks prove the branch, never the combination. Two branches that are each clean can merge to a tree that is not (an override newly possible, a moved violation, an N+1 that only the union produces), so the full-tree audit runs again on the merged trunk.
- State a wall-time budget. An auditor that takes minutes gets skipped, disabled, or `--no-verify`'d; a too-slow rule is a design bug in the rule, not a failure of the person running it.
- Never let a rule's own message be the only place its reason exists.

## Resources

| File | Read when |
| --- | --- |
| [references/the-two-walls.md](references/the-two-walls.md) | placing the seam; the build probe that shows whether an import wall is decorative |
| [references/arming-the-gate.md](references/arming-the-gate.md) | the seven arming checks, ratchet vs expiring allowance, per-auditor baselines, where enforcement bites, cost budget |
| [references/migration-batches.md](references/migration-batches.md) | sweeping an existing tree: batch order, counts-file keying, codemod proof |
| [references/ownership-transfer.md](references/ownership-transfer.md) | before adopting a component; when a focus path breaks on a clean visual diff |
| [references/eval-protocol.md](references/eval-protocol.md) | testing whether this skill earns its keep against a no-skill baseline |
| [examples/case-01-dead-glob.md](examples/case-01-dead-glob.md) · [case-02-importless-leak.md](examples/case-02-importless-leak.md) · [case-03-ownership-transfer.md](examples/case-03-ownership-transfer.md) | worked shapes: a wall whose directory was renamed; a vendor tag no import lint could see; a clean visual diff over a broken keyboard |
| [assets/rule-table.md](assets/rule-table.md) | copy-first: layer → may know → refused by → severity, plus exemption, ledger and arming columns |
| `assets/auditor-config.example.json`, `assets/counts.example.json` | the config the auditor and the liveness check share; the generated baseline shape |
| `scripts/glob-liveness.mjs`, `scripts/rule-code-parity.mjs` | in the gate: prove each glob matches a file; set-diff registry codes against codes named in docs (`--help`) |

Scripts measure and diff. They never decide which side of a disagreement is stale.
