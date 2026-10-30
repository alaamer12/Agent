---
name: postmortem
description: 'Blameless, self-contained incident documents: postmortem, incident report, RCA, bug write-up, "what went wrong". Modes: file (default) or folder. FILE: one Markdown doc, commands quoted inline, repo files cited by path + commit SHA. FOLDER: a package named "Postmortem - [Component] - [What broke] - [YYYY-MM-DD]" (sanitized) with index.md, the bundled reader index.html, and evidence/, investigation/, fix/, verification/ holding every artifact copied in, SHA256-indexed, secrets redacted, plus a Files and Artifacts Index and a "How we reached this conclusion" narrative with dead ends, so the folder alone re-runs the reasoning. Its 18-section template covers symptom, build and environment traceability, exposure window, timing interval, blast radius, causal chain, cause category, investigation log, fix, evidence level V0-V5, verification, rare-bug soak math, prevention with owner/due/ticket/DoD. Full SHAs, UTC timestamps, quantified claims, never "human error" as a root cause. Prose follows the /document skill.'
when_to_use: The user asks for a postmortem, incident report, RCA, root-cause analysis, bug write-up, "what went wrong", or a blameless review of an outage, crash or regression.
argument-hint: "[file|folder] [one-line incident hint]"
---

# Postmortem

A postmortem is read by someone with **no context, months later**: they must be able to tell what broke, when,
where, how, what was ruled out, and whether the fix is actually proven — from the document alone. Every rule
below serves that reader.

This is a **document-type skill**: it owns structure, evidence discipline and the artifact package;
[`document`](../document/SKILL.md) owns prose (its `references/guidelines.md`, `comprehensive.md`). Do not
restate style rules here — invoke `document` for the writing.

## Step 0 — pick the mode (ask once)

Ask if the user did not say. One question, then proceed: **file** or **folder**. No answer → **file**.

| | **file** (default) | **folder** (complete package) |
|---|---|---|
| Output | one Markdown file | one folder: `index.md` + `index.html` + evidence/investigation/fix/verification |
| Commands | quoted inline in the document | stored as runnable files **and** quoted in `index.md` |
| Repo files | cited by path + full commit SHA (permalink), not copied | copied **and** cited by path + SHA |
| Use when | the story is the deliverable; few artifacts | investigation, fix and verification must be reproducible later |

## Step 1 — facts before prose

Gather, per section: versions, SHAs, UTC timestamps, build IDs, config/flags, environment. Anything you cannot
establish: **ask the user, or write `UNKNOWN`**. Never invent a SHA, a time, a version, a count, or a cause.
`UNKNOWN` is an honest value; a plausible guess is a corrupted record.

Separate three registers and label them in the text: **fact** (observed, with a source), **inference**
(reasoned from facts — say what would falsify it), **opinion** (judgment — say it is judgment).

## Step 2 — build the document

### Mode "file"
Produce `<slug>.md` (or the user's filename). All 18 template sections present, in order, or explicitly
`UNKNOWN — <what would fill it>`. `INDEX`-style sections 18 are replaced by inline commands and permalinks:
the document must stay self-contained even though the artifacts are not beside it.

### Mode "folder"
Folder name — exact pattern, sanitized for the filesystem:

```text
Postmortem: [Component] — [What broke] — [YYYY-MM-DD]
  → ":" → " -"      remove / \ * ? " < > |
  → Postmortem - Sync service — startup crash — 2026-10-12
```

Keep the **unsanitized** title (colons, em dashes) as the H1 of `index.md`. Use
`python scripts/pm_check.py --sanitize "<title>"` to get the folder name; never hand-sanitize.

```text
<folder>/
├── index.md        the postmortem (all 18 sections)
├── index.html      the bundled reader, opening index.md
├── evidence/       logs, dumps, traces, pcaps, screenshots, graph snapshots, crash reports
├── investigation/  every script, query, config or wrapper used to FIND the problem
├── fix/            the patch/diff + every script to build, apply, release, roll back, remediate
└── verification/   regression, soak, stress, fault-injection, benchmark scripts + raw results
```

Create a subfolder **only if it has content**; nest further inside if a category grows large.

The six folder rules:

1. **Everything the document uses lives in the folder.** Copy files in (never link out); scripts that live in
   a repository are copied **and** cited with repo path + commit SHA.
2. **Redact secrets and personal data** (tokens, keys, passwords, emails, sensitive IPs) in the copies. Record
   what was redacted and where; keep the **original** file's SHA256 in the notes so the copy is traceable.
3. **Files and Artifacts Index** — one table, every file in the folder: `Path | Role (find/fix/verify/evidence)
   | What it is | How to run it (exact command) | What it showed | Supports (section or hypothesis) | SHA256`.
   Every folder file appears; every file mentioned in `index.md` exists. Relative links so they open from the
   reader.
4. **How we reached this conclusion** — chronological narrative citing files by path. Per step: suspicion →
   file/command → what it returned → what it proved, ruled out or suggested. **Include dead ends.** A reader
   must be able to re-derive the diagnosis from the folder alone.
5. **Fix and verification sections reference the exact files** in `fix/` and `verification/`, with how to
   re-run them.
6. **Nothing outside the folder is load-bearing.** If the document depends on it, copy it in.

### The reader (`index.html`)
`assets/index.html` is the bundled Markdown reader. In folder mode copy it to `<folder>/index.html` and change
**exactly two things**: the default `SOURCE` from `'example.md'` to `'index.md'` (and the comment above it), and
the `<title>` to the postmortem title. Keep theme, font picker, TOC, drag-drop, `?file=` behavior untouched.

Browsers block `file://` pages from fetching sibling files, so tell the user how to open it:

```bash
cd <folder>
python -m http.server 8000        # POSIX: python3 -m http.server 8000
# then open http://localhost:8000/   (the reader loads index.md)
```

The asset's own error text says `python3`; on Windows that is a Store stub — give the user the `python` form.
Verify relative links to `evidence/`, `investigation/`, `fix/`, `verification/` resolve **when served**.

## Step 3 — the 18 mandatory sections

Fill [`assets/templates/postmortem-template.md`](assets/templates/postmortem-template.md) section by section.
Numbered headings 1–18; none may be dropped. Summary of what each owns lives in the template's header comment;
the evidence-level mapping (V0–V5) is [`references/00-evidence-levels.md`](references/00-evidence-levels.md).

Non-negotiables inside the sections:

- **Blameless.** The system is the subject of every sentence. `The retry loop had no backoff`, not
  `X forgot to add backoff`. "Human error" is never a root cause — ask why the system allowed that action. No
  names except as authors/reviewers/sign-off. **Blameless is not nameless and not accountability-free:** when a
  human decision is in the chain, state what made it look reasonable at the time (the *second story* — the alert
  they saw, the runbook they followed, the load they were under), and keep the owner of each action item named.
  Blameless describes the analysis, not the follow-up.
- **One mechanism, several factors.** A single "root cause" is a simplification that survives only when it is
  true. If two independent conditions had to coincide, say so — that is a causal chain with contributing factors,
  and it implies two different prevention actions. Prefer the causal chain over the comfort of one sentence.
- **Traceability is exact.** UTC ISO-8601 timestamps (`2026-10-12T03:14:07Z`), full 40-char SHAs, concrete
  versions and build IDs, absolute dates. Never "yesterday", "latest build", "recently".
- **Quantify.** "1,842 of 12,000 requests (15.4%) over 38 min", never "many users for a while".
- **Ask whether it was known.** If an accepted risk was disclosed earlier — the `caution` skill's card in the
  conversation, a decision record, a ticket comment — put it in §17 as *Known risks accepted*: what was disclosed,
  when, and the answer. An incident that was an accepted risk is not a surprise: the second story is the
  disclosure, and §16's prevention is "the guard that was declined", which makes it a process finding rather than
  a coding one.
- **Confidence is stated, not implied.** Root cause: proven / strongly supported / plausible / speculative —
  with the evidence that justifies that word.
- **Verification level is claimed only as high as the evidence.** V0–V5, and say why not higher.
- **Every action item**: one owner, due date, ticket, and a verifiable definition of done. Quality beats
  volume: **cap at 8**, keep at least one `mitigate` and one `prevent`, prefer actions doable within a month,
  and close an item only with evidence that its DoD was met — a status change is not evidence
  ([`references/05-learning-and-action-quality.md`](references/05-learning-and-action-quality.md)).

## Step 4 — investigate like a record, not a story

The investigation log is where the value is: hypotheses, the command that tested each, the result, and the
verdict — including the ones that were wrong. Tools per domain (bisect, logs, debuggers/dumps, sanitizers, race
detectors, profilers, syscall/OS tracing, packet capture, metrics/tracing, fault injection, fuzzing, forensics)
are in [`references/02-tools-and-commands.md`](references/02-tools-and-commands.md) with exact commands.

Rare/timing-dependent bugs: [`references/01-rare-bug-verification.md`](references/01-rare-bug-verification.md)
— MTBF, `3 × MTBF ≈ 95%` confidence (`P(no failure) = e^(-T/MTBF)`), instance-hours, acceleration techniques,
rule of three, watch period, re-open criteria. **"This fix cannot be fully verified" is an allowed sentence;
hiding that it is unverified is not.**

## Step 5 — checklist, then hand back to `document`

Run, in order:

```bash
python scripts/pm_check.py --file <pm.md>            # file mode: 18 sections, dates, SHAs, people-as-cause, vague quantities
python scripts/pm_check.py --folder "<folder>"       # folder mode: all of the above + index coverage, dead links, SHA256 drift,
                                                     #   index.html SOURCE/title, artifacts index completeness
```

Fix every finding it can justify, or record why it does not apply. Then final read-through checklist:

- [ ] 18 sections present (or explicit `UNKNOWN — <what would fill it>`), no orphan heading
- [ ] Every claim has a source: a link, a pasted excerpt, a file, a command output
- [ ] Facts, inferences and opinions are distinguishable; inferences say what would falsify them
- [ ] Timeline is UTC and monotonic; durations (TTD/TTA/TTI/TTM/TTR) computed, not estimated
- [ ] Exposure window and impact quantified against a stated denominator
- [ ] Fix section states whether it removes the cause or hides the symptom, and the rollback plan
- [ ] Verification level matches what was actually run; rare-bug coverage honest
- [ ] Action items have owner + due + ticket + DoD; prevention covers Prevent/Detect/Mitigate/Learn
- [ ] A person never appears as the cause; "human error" appears nowhere as a root cause
- [ ] Every human decision in the chain has its second story (why it looked right at the time)
- [ ] At most 8 actions, including one mitigate and one prevent; every closed item has evidence, not a status
- [ ] Reviewer re-ran at least one command and the result is recorded; publication date and location stated
- [ ] Folder mode only: every file indexed and present, links resolve when served, secrets redacted with the
      original checksum recorded, `index.html` opens `index.md`
- [ ] Prose reviewed against `document` (`references/guidelines.md`, `comprehensive.md`)

## Review, then publish

- **Timing.** Draft within 48 h while memory is fresh; publish within **5 business days**. The normal window
  is 3–7 days — beyond a week the incident has become archaeology and the timeline is reconstructed from chat.
  If evidence is still arriving, publish as `Status: draft` with a dated commitment to the next revision rather
  than going silent.
- **Review meeting.** 30–45 minutes. The author walks the causal chain and the action table; the reviewer
  checks four things: every claim has a source, the V-level matches the evidence, no sentence blames a person,
  and the actions are few and verifiable.
- **The reviewer re-runs at least one command** from the investigation or verification tables and records the
  result (folder mode: the output goes in the package). A review that only reads is proofreading.
- **Publish where the team already looks** — the incident tool, `docs/`, or the folder — and link it from the
  action tickets. A postmortem nobody can find teaches nobody.
- **Measure the postmortem itself**, not just the incident: time to publish, action completion on time (aim
  > 90%), recurrence rate of the same pattern (aim < 10%), and whether closed actions were verified rather than
  marked. Numbers go in §17 ([`references/05-learning-and-action-quality.md`](references/05-learning-and-action-quality.md)).

**Security incidents** (cause category "outside"): preserve before touching — hash, copy, record custody
(hash → copy → never edit the original), and defer disclosure/legal timing to the organisation's IR policy
(NIST SP 800-61r3 is the common reference). The postmortem records what happened and what was preserved; it does
not decide notification obligations.

## Rules to enforce

- **Blameless, always** — rewrite any sentence whose subject is a person's mistake.
- **No invented facts** — `UNKNOWN` beats a confident guess; a missing SHA is a blocker to cite, not a blur.
- **No unverified claims of verification** — V-level and "done" are claims that need evidence.
- **No outside dependencies** in folder mode; no absolute machine paths inside the document.
- **Redaction is recorded, not silent** — what was removed, from which file, with the original checksum kept.

## Assets, references, scripts

| Path | Owns |
|---|---|
| [`assets/templates/postmortem-template.md`](assets/templates/postmortem-template.md) | the 18-section skeleton with placeholders and per-section guidance |
| [`assets/index.html`](assets/index.html) | the bundled Markdown reader (copy verbatim; two edits in folder mode) |
| [`references/00-evidence-levels.md`](references/00-evidence-levels.md) | V0–V5, what each claim requires, how to phrase "cannot fully verify" |
| [`references/01-rare-bug-verification.md`](references/01-rare-bug-verification.md) | MTBF/soak math, acceleration, rule of three, watch period, residual risk |
| [`references/02-tools-and-commands.md`](references/02-tools-and-commands.md) | the exact commands for each investigation, fix and verification domain |
| [`references/03-worked-example-file-mode.md`](references/03-worked-example-file-mode.md) | a condensed single-file postmortem |
| [`references/04-worked-example-folder-mode.md`](references/04-worked-example-folder-mode.md) | a condensed folder package: tree, index table, narrative |
| [`references/05-learning-and-action-quality.md`](references/05-learning-and-action-quality.md) | the second story, action-item quality and metrics, review meeting, "postmortems that change nothing" |
| `scripts/pm_check.py` | folder-name sanitizer + document/folder validator (run it; exit 1 on findings) |
