# Evaluating whether a skill earns its keep

> A skill is a claim that an agent does worse without it. This is how to test the claim cheaply,
> honestly, and without letting the skill's author grade it.

## 1. The method

Give **one identical scenario** to two fresh agents, differing only in access to the skill:

| Arm | Setup |
| --- | --- |
| **Skill** | told to apply the skill; handed its text as **one concatenated blob** and told to read exactly that one file |
| **Baseline** | told to answer from its own judgment; **forbidden from reading anything** |

Hard conditions, each of which breaks the comparison if dropped:

- **Same prompt text.** One scenario, pasted identically. Re-wording per arm measures the wording.
- **The skill arrives as one read, not a tree walk.** Concatenate `SKILL.md` and its references
  (`cat SKILL.md references/*.md > scratch/evals/<skill>-blob.md`) and point the arm at that single
  file. An arm browsing the directory measures how the files are arranged and how fast it can walk
  them, not whether the rules change the answer — twelve round-trips of latency for a signal the
  blob already carries. If you *also* want to know whether the SKILL.md surface alone triggers the
  rules, that is a separate, stricter variant (blob = `SKILL.md` only); run it as its own comparison,
  never mixed into the same wave.
- **No code.** Neither arm writes or edits files. Code hides judgment in details neither arm was
  asked about, and it costs five times the tokens for the same signal.
- **Plan-only output.** Each arm returns what it would do and why it would catch what it claims to
  catch. A plan is where "we should also prove the glob is alive" costs one line instead of one file.
- **Fresh context per run.** No shared session, no memory of the other arm, no leftovers.
- **Same model, same tool access** (read one file at most: the blob), run back to back so the
  environment does not drift between arms.
- Keep the raw outputs in a scratch directory. A summary of both arms written after the fact is a
  document you can steer; the transcripts are not.

## 2. The rubric

Fix the properties **before** the runs, from the skill's own rules. Each property is one line: the
behaviour expected, and the section that owes it. Score present / absent per run; do not let a
property be invented after seeing an answer, or the rubric becomes a description of the winner.

Illustrative shape for a boundary-and-enforcement skill:

| # | Property the plan must show | Owed by |
| --- | --- | --- |
| 1 | names both walls, and knows a build-time resolver defeats the import wall | the-two-walls |
| 2 | asserts every configured glob matches a real file | arming §1 |
| 3 | one baseline file per auditor | arming §3 |
| 4 | doc↔registry code parity | arming §1 |
| 5 | hard-zero vs ratcheted, with the *reason* for the split | arming §2 |
| 6 | a wall over existing debt states its starting count in the same commit | migration §5 |
| 7 | codemod idempotence, tag-only diff, fixture+snapshot | migration §4 |
| 8 | names the two counts-keying strategies and picks one with a reason | migration §3 |
| 9 | says where enforcement bites, and that a violating commit must be tested | arming §4 |
| 10 | states a wall-time budget for the auditor | arming §5 |
| 11 | adoption transfers per-component internal ownership | ownership-transfer |

The properties are not weighted. A skill that wins eleven and loses one is not "mostly right"; it is
a document with a hole, and the hole is the reason the other arm will ship the bug.

## 3. Runs and direction

**Three runs per arm minimum before trusting direction.** A single run of a single agent on a single
scenario is one sample from a noisy distribution: one arm can produce a better plan because it
happened to recall a similar problem last week.

- A property counts as **held** by an arm when it appears in at least two of three runs. One-out-of-three
  is the arm thinking about it sometimes; report it as flaky, not as a win.
- Record the disagreement rate explicitly: how many properties differed across runs *within* the same
  arm. If an arm is 50/50 on a property, that arm's plan does not depend on the skill for it, and the
  comparison is underpowered — run more, or stop claiming the rule.
- Report the delta as a set difference in both directions. **The baseline's wins are the finding.**
  A skill that loses a property to no-skill is a rule that was missing, and it is the only honest way
  to find out which of your rules are decoration.

What to do with the result: add what the baseline beat you on, keep what the skill uniquely
contributed, and **delete a rule that earns nothing in three rounds of runs** — it is bulk that slows
the reader for no advantage.

## 4. The two confounds — state both when you report

1. **The baseline may already know the domain.** A tie on the obvious rules is not evidence the skill
   is worthless; it is evidence it is redundant *for a strong model on a familiar problem*. Say which
   of the two explanations you cannot rule out. The corollary is that a skill's value concentrates in
   the non-obvious rules, which is why the rubric above is per-rule and not per-answer.
2. **Scenario design can hide a rule you want to test.** If the scenario does not need migration
   mechanics, the skill cannot show its migration mechanics, and the arm will look silent on a rule
   that is in fact load-bearing. After every run, list which rules were even *reachable* given the
   scenario, and say plainly which ones the scenario could not exercise. That is today's failure
   exactly: several of the rules now in this skill were invisible to the evaluation that tested it,
   because the scenario never had a sweep in it.

   Mitigation, not cure: derive the scenario from a real decision the repo recently made, so the shape
   that needed the rule is present; and re-run with a second scenario that exercises the unreachable
   half.

3. **Giving both arms the repo collapses the gap — and that is a finding, not a failure.** With read
   access, a capable model investigates the tree and reconstructs most of what the skill would have told
   it; the round becomes a ceiling tie. A plan-only arm with no file access measures the model's priors
   instead, which is where a checklist earns its keep. Choose the format deliberately and say which one
   you ran: *text-only* tests whether the rules get applied when the facts are given; *read-access* tests
   whether the model investigates. A skill that wins the first and ties the second is a discipline aid,
   not a discovery aid — a distinction worth stating rather than hiding.

   If an arm reads outside its permitted root, discard the run and say so. A contaminated arm has the
   skill's content via the back door and its score is not a baseline.

## 5. Reporting shape

```
Scenario: one paragraph, identical text to both arms, no skill vocabulary in it
Arms: skill (n runs) / baseline (n runs), forbidden-access statement for the baseline
Rubric: the fixed table, filled before the runs
Delta: properties only the skill won | only the baseline won | flaky within an arm
Confound statement: which half of the rubric the scenario could not reach, and whether the
  baseline plausibly already knew the domain
Change: rules added, rules kept because they won, rules deleted because they earned nothing
```

Fill the "Change" section honestly. A skill that only ever gains rules is not being evaluated; it is
being accumulated.
