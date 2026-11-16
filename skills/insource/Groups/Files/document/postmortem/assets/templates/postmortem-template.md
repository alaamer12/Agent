<!--
  POSTMORTEM TEMPLATE — postmortem skill
  Copy this file to index.md (folder mode) or <slug>.md (file mode), then replace every <placeholder>.
  Keep the numbered headings exactly. Do not drop a section: if the fact is unavailable, write
  "UNKNOWN — <what would establish it>" and move on. Delete the "_Guidance_" lines when done.

  Section -> source map (what each must end up containing):
   1  exec summary + exact symptom            10 investigation log, hypothesis by hypothesis
   2  full traceability matrix                11 fix type, mechanism, rollout, rollback
   3  exposure window                         12 fix/release commands (paths in fix/)
   4  timing interval + sampling              13 evidence level V0-V5 and why not higher
   5  reproducibility class + repro            14 verification evidence (before/after)
   6  layer depth + blast radius              15 rare-bug soak math, watch, re-open
   7  bug class/pattern + sweep               16 Prevent/Detect/Mitigate/Learn + action table
   8  causal chain + five whys                17 metadata, impact, timeline, lessons, sign-off
   9  cause category + confidence             18 (folder mode) artifacts index + investigation narrative
-->

# Postmortem: <Component> — <what broke> — <YYYY-MM-DD>

> **Status:** <draft | review | final> · **Severity:** <SEV-1…SEV-4> · **Incident ID:** <INC-…>
> **Authors:** <names> · **Reviewers:** <names> · **Sign-off:** <name, date>

---

## 1. What the problem was

> _Guidance: at most six sentences. A reader who stops here must still know what broke, who felt it, and whether
> it is fixed. Then paste the exact symptom — the error string, stack trace, or log excerpt, verbatim._

**Summary.** <Six sentences maximum.>

**Exact symptom.**
```text
<paste the literal error / stack trace / log excerpt — not a paraphrase>
```

**Impact in one line.** <N of M users / requests affected for D duration; what they could not do.>

## 2. When and where — traceability

> _Guidance: every cell is a fact with a source. "UNKNOWN" is acceptable; a guess is not. Full 40-char SHAs._

| Field | Value |
|---|---|
| First bad commit | `<sha>` — <subject> |
| Last good commit | `<sha>` — <subject> |
| Fix commit(s) | `<sha>` — <subject> · PR <link> |
| Versions affected | <e.g. 2.4.0 – 2.4.3> |
| Version fixed | <e.g. 2.4.4> |
| Release channel | <dev / nightly / beta / stable / LTS / internal> |
| Build ID | <id> |
| Artifact hash | `sha256:<hash of the shipped artifact>` |
| Built from | commit `<sha>` by CI run <URL> — proves the shipped bytes match the reviewed source |
| Build type | <debug / release / optimized / reproducible / cross-compiled> |
| Toolchain | <compiler/runtime/SDK version> |
| Dependencies | <lockfile hash + notable versions> |
| Feature flags / config that matter | <flag = value; config key = value> |
| OS / build | <version, patch level, distro/edition> |
| Hardware | <CPU/GPU/board/driver, or cloud instance type> |
| Container digest | `sha256:<digest>` (if applicable) |
| Cloud region / zone | <region> |
| Security policies in force | <AV/EDR/AppLocker/group policy/pinning — including anything that could influence behavior> |
| Network conditions | <latency, MTU, proxy, IPv6, TLS interception> |
| Reproduces where? | <matrix: env × version → yes/no/unknown> |

**Reproduce matrix**

| Environment | Version | Reproduces? | Notes |
|---|---|---|---|
| <env> | <version> | <yes/no/intermittent/untested> | <observation> |

## 3. When it started and how long it lasted

> _Guidance: UTC everywhere; compute the window, do not estimate it._

| Milestone | UTC timestamp | Evidence |
|---|---|---|
| First-ever occurrence | `<YYYY-MM-DDTHH:MM:SSZ>` | <log line / metric / user report> |
| First noticed | `<…Z>` | <alert / report> |
| Introduced (commit/merge) | `<…Z>` | `<sha>` |
| Detected by monitoring | `<…Z>` | <alert name> |
| Fix deployed | `<…Z>` | <deploy id> |
| **Total exposure window** | **<duration>** | <first occurrence → fix deployed> |

## 4. The interval in which the pattern occurs

> _Guidance: the distribution matters more than one example. Give sample size and say WHY the window exists._

- Window: <e.g. "between 5 s and 40 s after process start">
- min / median / max: <…> / <…> / <…> · sample size: <n>
- **Histogram (required — the distribution is the evidence, one example is an anecdote):**

| Bucket | Count | % of sample |
|---|---|---|
| <0–10 s> | <n> | <…> |
| <10–20 s> | <n> | <…> |

- Time-based pattern: <after N h uptime / at midnight / after N requests / none observed>
- Frequency: <every run / 1 in 20 / once per ~100 h>
- Recurrence once started: <escalates / steady / self-recovers after …>
- **Why it falls in this window:** <the mechanism that makes the timing non-random>

## 5. Reproducibility

> _Guidance: one primary class; list secondary factors if the behaviour depends on more than one._

**Class:** <deterministic | probabilistic | timing/concurrency-dependent | state-dependent | environment-dependent | long-latency | not reproducible>

**Exact steps**
1. <step>
2. <step>

**Minimal reproducer:** <smallest input/setup that still fails — path to it in `investigation/` (folder mode)>
**Reproduced on:** <N of M attempts / environments> · **Not reproduced on:** <…>

## 6. How deep — layer and blast radius

> _Guidance: name the deepest layer the defect actually lives in, not the layer where it was seen._

| Layer | Involved? | Where |
|---|---|---|
| UI / presentation | <yes/no> | <file/component> |
| Application logic | <yes/no> | <file/function> |
| Framework / library | <yes/no> | <dependency + version> |
| Runtime | <yes/no> | <runtime version> |
| OS / driver | <yes/no> | <component> |
| Hardware / firmware | <yes/no> | <component> |
| Network / infrastructure | <yes/no> | <component> |
| Data / storage | <yes/no> | <table/format> |
| Process / organization | <yes/no> | <process> |

**Depth rating:** <surface | moderate | deep | systemic>
**Blast radius:** <what was affected> · **Not yet failed but exposed:** <components that share the defect>

## 7. The pattern

- **Bug class:** <race | leak | overflow | config drift | certificate expiry | off-by-one | dependency | …>
- **Repeat of a known incident?** <no | yes → <INC-…> and what changed/ did not>
- **Same defect elsewhere?** <result of the sweep> — **sweep query:** `<exact search/query used>`
- **Pattern tag:** `<searchable-tag>` (one string future searches will find)

## 8. How it happened

> _Guidance: four different things — do not blend them. The causal chain cites file, function and line at a
> commit SHA; the five whys ends at a system property, never at a person._

| Element | Statement |
|---|---|
| Symptom | <what users saw> |
| Trigger | <the event that started it this time> |
| Root cause | <the defect that made the trigger consequential> |
| Latent conditions | <why it could sit unnoticed until now> |

**Causal chain**
1. <event> — [`path/file.ext#L10-L20`](<permalink at sha>) 
2. <event> — [`path/file.ext`](<permalink at sha>)
3. <event> → <observed symptom>

**Five whys**
1. Why did <symptom> happen? → <answer>
2. Why <answer 1>? → <answer>
3. Why <answer 2>? → <answer>
4. Why <answer 3>? → <answer>
5. Why <answer 4>? → <system property: the missing invariant, guard, test or review step>

**Contributing factors**
- <factor> — <how it made this worse or more likely>

**Second story — why each human step looked reasonable at the time** *(required; blameless is not nameless)*

| Human step in the chain | What they saw / knew then | Why the action was rational | What the system should have shown or prevented |
|---|---|---|---|
| <e.g. on-call rolled back DB migration at 03:20Z> | <alert only said "replication lag"> | <runbook step 4 says roll back the migration on lag> | <alert should name the writer; runbook step 4 is unsafe under load> |

No names in this table. If a step has no human actor, delete the row — but do not delete the section; "there was
no human decision here" is itself a finding worth one line.

## 9. Cause category, with evidence

**Primary category:** <code-side (developer) | tool-side (framework/library/compiler/runtime) | environment-side (OS update, policy, driver, hardware, config drift) | outside (attacker, malicious input, third-party outage) | process/organizational | data | unknown>

- **Evidence:** <links to files/lines/commands that establish this category>
- **Tool-side only:** upstream issue/discussion links: <…>
- **Outside only — security assessment:** vector <…> · indicators of compromise <…> · data exposure <…> · disclosure obligations <…>
- **Root-cause confidence:** <proven | strongly supported | plausible | speculative> — because <evidence>
- **Alternatives considered and why rejected:**
  - <alternative> — rejected because <evidence>

## 10. Scripts, tools and commands used to FIND the bug

> _Guidance: this is the record of the search, including the wrong turns. Folder mode: every row's path lives in
> `investigation/`. File mode: inline commands + repo path + SHA._

**Hypothesis log**

| # | Hypothesis | How it was tested (exact command) | Result | Verdict |
|---|---|---|---|---|
| 1 | <hypothesis> | `<command>` | <output summary> | confirmed / rejected / inconclusive |
| 2 | <hypothesis — a dead end> | `<command>` | <output> | rejected because <…> |

**Tools used**

| Purpose | Tool | Exact copy-paste command | Output (summary or file) |
|---|---|---|---|
| <e.g. find the introducing commit> | `git bisect` | `<command>` | <result> |
| <e.g. detect the race> | <sanitizer/race detector> | `<command>` | <result> |

Cover, where relevant: git bisect · log/metric analysis · debuggers and dump analysis · sanitizers · race
detectors · profilers · syscall/OS tracing · network capture · metrics/tracing · fault or timing injection ·
fuzzing · security forensics · custom scripts.

## 11. How it was solved

- **Fix type:** <root-cause fix | mitigation | workaround | rollback | config change | dependency pin | heuristic>
- **How it addresses the mechanism:** <the sentence that connects the fix to section 8's root cause>
- **Removes the cause, or only the symptom?** <answer — if symptom only, say what remains>
- **Commits / PRs:** `<sha>` <link>, …
- **Rollout:** <flag / staged / canary / full> — **Rollback plan:** <exact command and trigger>
- **Side effects:** <behavior, performance, compatibility, operational cost>

## 12. Scripts, tools and commands used to FIX and release

> _Guidance: branch → build → test → deploy → rollback, plus one-off remediation. Folder mode: paths inside
> `fix/`; make each re-runnable._

| Stage | Command | File (folder mode) | What it did |
|---|---|---|---|
| Branch / patch | `<git command>` | `fix/<file>` | <…> |
| Build | `<command>` | `fix/<file>` | <…> |
| Test | `<command>` | `fix/<file>` | <…> |
| Deploy | `<command>` | `fix/<file>` | <…> |
| Rollback | `<command>` | `fix/<file>` | <…> |
| One-off remediation | `<command>` | `fix/<file>` | <what it changed, blast radius, reversibility> |

## 13. Heuristic or verified?

**Achieved level: V<n> — <name>.**
<One paragraph: the evidence that supports this level **with its N** (runs, iterations, instance-hours, sample
size), and exactly why not the next one up. A level without N is a slogan. See references/00-evidence-levels.md.>

## 14. How it was verified

> _Guidance: each line needs a result, not an intention. A regression test that never failed on the old code
> proves nothing._

| Check | Before the fix | After the fix | Evidence |
|---|---|---|---|
| Reproduction | <fails / n/a> | <no longer reproduces, N attempts> | `<file>` / `<command>` |
| Regression test | <fails, with output> | <passes> | `<test name / file>` |
| Sanitizer / race detector | <report> | <clean> | `<log>` |
| Multi-environment retest | <matrix> | <matrix> | `<log>` |
| Performance check | <baseline> | <after> | `<benchmark>` |
| Production monitoring | <alert/metric> | <quiet for D> | `<dashboard/link>` |
| Independent reviewer | — | <name, what they re-ran> | `<note>` |

## 15. Rare or untestable bugs

> _Guidance: fill this whenever the failure was not reproducible on demand. "Cannot be fully verified" is an
> honest conclusion; leaving this section vague is not._

- **MTBF estimate:** <…> (from <basis: production hours, field reports, …>)
- **Soak duration needed:** <3 × MTBF ≈ 95% confidence; P(no failure) = e^(−T/MTBF)> → <needed T>
- **Arithmetic, shown (required):** `T = MTBF × ln(1 / (1 − confidence))` → <e.g. 41 h × 3.0 = 123 h> ;
  `confidence = 1 − e^(−T_instance_hours / MTBF)` → <e.g. 1 − e^(−133/41) ≈ 96%>
- **Instance-hours actually run:** <N instances × T> — **achieved confidence:** <…>
- **Acceleration used:** <fault injection / clock skew / shortened timers / stress / none>
- **Not covered:** <what the soak could not exercise>
- **Rule of three:** <0 failures in N instance-hours → upper bound on failure rate ≈ 3/N>
- **Production watch:** <duration> with alert `<exact alert name/query>`
- **Re-open criteria:** <observable condition that means "not fixed after all">
- **Residual risk:** <what remains, accepted by whom>

## 16. Prevention

> _Guidance: four layers, and an action table where every row is assignable. Prevention is not "be careful"._

**Prevent** — <what makes this defect impossible or caught at build time>
**Detect** — <what would have shortened detection; the alert/test that now exists>
**Mitigate** — <what limits the blast radius next time>
**Learn** — <what changed in review, docs, onboarding, or the checklist>

**Same class of bug elsewhere** — sweep: `<query>` → <results; link actions below>

**Rules for this table:** at most **8 rows** (more usually means unclear actions, not thoroughness); at least
one `mitigate` and one `prevent`; prefer actions finishable within 30 days; a row closes only when someone has
**verified its definition of done** — the "Verified by" cell is empty until then, whatever the status says.

| ID | Action | Type | Priority | Owner | Due | Ticket | Definition of done | Status | Verified by / date |
|---|---|---|---|---|---|---|---|---|---|
| A1 | <action> | prevent / detect / mitigate / learn | P1 | <name> | <YYYY-MM-DD> | <link> | <verifiable condition> | open | — |

## 17. Supporting sections

**Metadata**

| Field | Value |
|---|---|
| Incident ID | <INC-…> |
| Status | <draft / review / final> |
| Severity | <SEV-…> — justification: <…> |
| Authors / reviewers | <names> |
| Detection | <alert / user report / internal> |

**Impact**

| Dimension | Value |
|---|---|
| Users / requests affected | <n of N (x%), source: <…>> |
| Duration of user-visible impact | <…> |
| Data integrity / loss | <none | affected rows, recovery> |
| Security impact | <none | details + cross-ref section 9> |
| SLA / SLO breach | <…> |
| Cost | <…> |

**UTC timeline, with sources**

| UTC | Event | Source |
|---|---|---|
| `<…Z>` | <event> | <log/alert/commit/chat link> |

**Key durations:** TTD <…> · TTA <…> · TTI <…> · TTM <…> · TTR <…>

**Postmortem quality** *(the review's own numbers, filled at publication and again at the 30-day check)*

| Measure | Value |
|---|---|
| Time from incident end to published postmortem | <…> (target: ≤ 5 business days) |
| Actions completed on time at 30 days | <n of m, %> (target: > 90%) |
| Actions closed with evidence of DoD | <n of m> |
| Same pattern recurred since? | <no / yes → linked incident> (target: < 10%) |
| Reviewer re-ran | `<command>` → <result> |

**Detection analysis** — why was it not caught earlier? <…>

**Lessons learned** — went well: <…> · went poorly: <…> · where we got lucky: <…> · surprises: <…>

**Related incidents:** <links>
**Open questions:** <question — who will answer it, by when>

**Sign-off**

| Role | Name | Date |
|---|---|---|
| Author | <name> | <YYYY-MM-DD> |
| Reviewer | <name> | <YYYY-MM-DD> |

**Revision history**

| Version | Date | Change | Author |
|---|---|---|---|
| 1.0 | <YYYY-MM-DD> | initial | <name> |

## 18. Files and artifacts — folder mode only

> _Guidance: in file mode, delete this section; its jobs are done by inline commands and permalinks above.
> In folder mode, both subsections are mandatory._

### Files and Artifacts Index

| Path | Role | What it is | How to run it | What it showed | Supports | SHA256 |
|---|---|---|---|---|---|---|
| `investigation/<file>` | find | <description> | `<exact command>` | <result> | §10, hypothesis 2 | `<hash>` |
| `fix/<file>` | fix | <description> | `<exact command>` | <result> | §11 | `<hash>` |
| `verification/<file>` | verify | <description> | `<exact command>` | <result> | §14 | `<hash>` |
| `evidence/<file>` | evidence | <description> | — | <what it proves> | §2, §8 | `<hash>` |

Every file in the folder must appear here; every path here must exist. Relative links, sorted by role.

### How we reached this conclusion

> _Guidance: chronological, cites paths, keeps the dead ends. A reader with no context must be able to re-run
> this reasoning from the folder alone._

1. **Suspected** <hypothesis>. **Ran** `investigation/<file>` (`<command>`). **Returned** <summary>.
   **Proved / ruled out / suggested** <…>.
2. **Dead end —** <hypothesis that failed>, tested with `investigation/<file>`; result <…>; rejected because <…>.
3. … continue until the diagnosis is established, then point to `fix/` and `verification/`.
