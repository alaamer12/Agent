# Review, then publish — the review contract and the enforce-list

Read before publishing a postmortem. The entrypoint (`../SKILL.md`) points here for everything that happens
after the document is written.

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
  marked. Numbers go in §17 ([`05-learning-and-action-quality.md`](05-learning-and-action-quality.md)).

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
