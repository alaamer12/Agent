# Arming the gate

> A gate that reads nothing reports exactly what a clean repo reports. This file is the difference
> between a wall and a comment that mentions a wall.

## 1. The seven arming checks

```
- [ ] 1 Every configured path/glob matches >= 1 real file      (scripts/glob-liveness.mjs)
- [ ] 2 Every exempt directory is proven to actually contain the banned thing
- [ ] 3 One planted violation per rule code, in a temp tree, asserted to fire
- [ ] 4 Controls: correctly-shaped files asserted NOT to be flagged
- [ ] 5 Every rule in the registry has a fixture and an explanation that names a doc
- [ ] 6 Every code named in the docs exists in the registry, and vice versa
                                                    (scripts/rule-code-parity.mjs)
- [ ] 7 Every ratcheted rule has a fixture that LOWERS the stored count and must exit 0
- [ ] 8 A file the auditor cannot parse exits non-zero — 0 means "clean", never "could not run"
```

**Check 1 is the highest-value line in the skill.** A rule scoped to a directory that was renamed
months ago stays quiet forever: the files it was meant to police go unpoliced while the gate prints
green. Liveness must run against the *same config the auditor reads*, otherwise it proves that a
copy of the list is alive. Point it at the real config and put it in the gate, not in a README.

**Check 2** is the same failure wearing a permission. An exemption for a directory that contains no
banned thing is a rule that gave up on nothing; an exemption whose contents were later cleaned is
still in the list, still widening the hole. Prove the exemption is load-bearing or delete it.

**Check 3** is the only test that a rule can fire at all. Build a throwaway tree, plant exactly one
offence per rule code, run the real auditor, assert its exit code and that the reported code is the
one you planted. Use the auditor's own exit status as the oracle — do not re-implement its logic in
the test, or the test passes when the auditor breaks.

**Check 4** matters more than it looks. A rule that flags correct code gets switched off by the
first person to hit it, and the switch-off is permanent and undocumented. Controls are
correctly-shaped files asserted to stay clean: the seam file itself, a file importing the project's
own name, a vendor tag inside the skin tier where it is legal. Include the near-miss controls a real
matcher gets wrong: a directory that shares the seam's prefix (`src/baseball/`), a decoy
(`src/features/base/`), and — for tag matchers — `<Button>` next to `<button>`, because a
case-insensitive match flags the project's own component and that is how the rule dies in week one.

**Check 6** closes the loop between the auditor and the docs. A code in the registry with no doc is
a rule no one can look up or argue with; a code named in prose with no registry entry is a rule that
cannot fire and will be cited in review as if it could. Both directions are defects. The script only
set-diffs two lists — which side is stale is your call.

**Check 7 is the one a ratchet never gets**, and it is the difference between a ratchet and a freeze
wearing a ratchet's clothes. A ratcheted rule refuses growth, so it must *accept* shrinkage — and the
only way to know it does is to store a count one above the fixture's offenders and assert the run
exits 0. Without that fixture, nothing in the suite distinguishes "only growth fails" from "any
non-zero fails", and under the second rule the batch that removes the last violation is reported as a
failure, so people stop removing violations. Sabotage it in both directions to prove the check itself
is alive: stored −1 must pass, stored +1 must fail, and a fixture that passes on both is a dead check.

**Check 8 separates "no violations" from "I did not look."** A parser crash, a timeout, a missing
binary and a syntax the auditor predates all end in a number; if that number is 0 the gate calls the
tree clean. Assert three outcomes rather than two — `0` clean, `1` violations found, `2` the audit
could not run — and make `2` fail the gate. The file the auditor cannot parse is exactly the file
where the rule matters.

## 2. Severity: hard-zero or ratcheted

One question decides it: **could a competent reviewer disagree that this is wrong?**

| Answer | Severity | Why | Examples |
| --- | --- | --- | --- |
| no — the fact is checkable | **hard-zero**, absent means clean, no baseline entry | a ratchet here stores a number for something with no judgment attached; it encodes the debt the wall exists to remove | a vendor import outside the seam; a vendor tag or utility class outside it; a raw platform control reaching around the seam; a layer skipping the seam |
| yes — it depends on intent | **ratcheted**, counts stored, only growth fails | the rule needs a human decision, so the tree legitimately carries some of them today | "a lower layer's appearance was overridden from above", where layout-on-the-parent is legal and colour-on-the-child is not |

A ratchet that shrinks is progress. A ratchet that is never re-blessed downward is **a lie being
maintained**: the stored number stops describing the tree and starts describing the day it was
written. Re-bless on every decrease, in the same change, so the number you commit is the number the
tree has.

### 2.1 The third shape: an allowance that expires

Some rules are judgment-free yet cannot ship at zero, because the debt already exists (a hard-zero
tag rule over a tree with thirty-four offenders). A numeric ratchet is the wrong instrument there —
it stores a number for something with no judgment attached, which is the debt the wall exists to
remove. Use a **named allowance** instead:

| Shape | Stored | Fails when | Why it is better here |
| --- | --- | --- | --- |
| count | one number per rule | the count grows | blind to *which* files; a violation moving A→B keeps the count |
| named list | `path -> rule` rows, each with an owner and a removal batch | a violation appears on an unlisted path, **or a listed path no longer offends** (stale row) | the list can only shrink, and the shrink is attributable to a batch |

The stale-row failure is the point: a count can sit at 34 forever while the tree changes underneath
it, but an allowance row that no longer describes a real violation is a bug the gate reports the day
it happens. Either way the rule still needs an **exit criterion written at birth** — which batch
empties it, or the date it is deleted — because "temporary freeze" is how the original debt got six
years old. When the last row goes, flip the rule to plain hard-zero and delete the file.

## 3. Two auditors, two baseline files

Never share one counts file between two auditors. A shared file makes a single careless re-bless
launder both rules: someone "regenerates the baseline" to unblock a build and the other auditor's
real growth disappears with it, silently, in the same commit.

Each auditor gets its own file, its own regenerate command, and its own diff in review. The ratchet
rule still lives in the same place for both — only growth fails — but the *authority to raise a
number* must not be a shared resource.

## 4. Where enforcement actually bites

Three loci, and each is bypassable in a different way:

| Locus | Bypassed by | Verdict |
| --- | --- | --- |
| editor / local optional run | not running it | awareness only, never enforcement |
| commit hook on **staged files** | committing one bad file alongside good ones, `--no-verify`, a partial checkout, a merge that brings the offence in from elsewhere | good for speed, worthless as authority |
| full-tree check in CI (or the gate that lands the merge) | a job that is skipped, flaky, or disabled for being slow | the only place the rule is provable |

So: the rule must be **provable in the full tree**, and a fast per-change run is a convenience on
top of it. Two consequences that people skip:

1. **Test the refusal.** Make a deliberate violating commit on a throwaway branch and confirm it is
   refused. A wall nobody has watched bite has not been shown to have teeth — the config it reads may
   be the stale one from §1.
2. **Same registry both places.** If the staged check and the full-tree check carry different rule
   codes, the two authorities disagree and the developer learns to trust whichever one they run.
3. **Re-run on the trunk after the merge, not only on the branch.** Every check above proves the state
   of *the tree it was handed*, and a feature branch is not the tree anyone lands on. Two branches
   that are each clean can merge into a tree that is not: the offence was in the file the other branch
   deleted, a ratchet's per-file keys were edited by both and the total was never compared, or the
   merged result resolves a vendor tag that neither branch used alone. So the authority is the run on
   the merged trunk, and it has to happen **before** that trunk becomes the base for the next batch —
   otherwise the next branch inherits an unpoliced state and will test clean against it. A pull-request
   check on the *merge commit* is the usual way to get this; a check on the head commit is the branch
   claim again, wearing a different hat.

This is the same fact the counts-file keying in
[migration-batches.md](./migration-batches.md) §3 already warns about from the other side: per-file
keys cannot see a violation moving between files, and neither can per-branch enforcement. The two
defences are one argument — the whole-tree bless and the whole-tree run are both places where
someone finally looks at the combined state instead of the contributed state.

**Three mechanics decide whether the hook is even measuring the commit.**

1. **Lint the staged blob, not the working tree.** Under `git add -p` the working tree holds hunks
   that are not in the commit, so a hook reading the file on disk reports on something nobody is
   committing — in both directions, missing the staged offence and inventing an unstaged one.
2. **A suppression comment is an exemption path.** If `eslint-disable-next-line` (or `@ts-ignore`, or
   a waiver marker) can silence the rule, the policy has an unaudited bypass that routes around the
   whole registry. Either suppressions fail, or they must appear in the one audited list — and a
   guard that greps for the rule id in disable comments is cheap.
3. **A hook that invokes a tool by bare name fails where the shell differs.** GUI clients and IDEs do
   not inherit your PATH; the first "command not found" commit is the commit that teaches the team to
   disable the hook. Absolute tool path, hook installed from a tracked setup step, never `|| true`.

## 5. Cost budget

An auditor that takes minutes gets skipped, disabled, or `--no-verify`'d. That is not a user failure;
**a too-slow rule is a design bug in the rule.** State the budget out loud and measure it.

Illustrative targets (numbers are examples, calibrate on your tree):

| Check | Budget |
| --- | --- |
| glob liveness, whole config | < 5 s |
| full-tree audit, warm | < 60 s |
| planted-violation self-test suite | < 15 s |
| the whole gate's rule set | under the time a developer will sit through before a commit |

Measure with the shell's own timer in CI and record the number next to the budget, so drift is
visible. When a rule cannot meet its budget: narrow its scope, cache its parse, batch the file
stat, or move it to a scheduled full-tree job — in that order. Never solve it by asking people to be
disciplined.

## 6. Run the self-test inside the gate

Fixtures are cheap; a rule with no fixture is the expensive one. The arming suite belongs in the
same gate as the audit, so a rule can be added only in a change that also arms it. If your gate can
report "all rules pass" while three of them have never fired on anything, the gate is measuring its
own config, not the tree.
