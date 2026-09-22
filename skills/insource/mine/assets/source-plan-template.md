# Mining plan — <topic>

**Source type:** <"Codebase / GitHub" | "Visual / design references" | other — state what kind of source this task actually points at>

**Independence model:** <"True independents — every candidate a distinct, unrelated instance" | "Industry/products — sources are whole products/platforms; one product may contribute several candidates" — settled with the user before discovery started; if the user didn't specify, ask which they want first (workflow.md → "True-independents or industry/products — settle this before discovery")>

**Budget:** <"N sources" | "~X minutes/hours">
<!--
  For a count-based budget, N is fixed by the user (or by "top 20" style
  phrasing in the request) — list exactly N candidates below.

  For a time-based budget, estimate a source count by dividing the total
  budget by a rough per-source estimate (see references/workflow.md →
  "Estimating project count for a time budget"), then list that many
  candidates. State the estimate and its basis plainly so the user can
  correct it before mining starts — this number is a planning estimate,
  not a per-source time cap; some sources will legitimately take longer
  than others once mining is underway.
-->

**Discovery method:** <how these candidates were found — e.g. "searched
'best enterprise-scale open source projects github 2026', cross-referenced
with GitHub stars/activity" for a codebase task, or "searched Mobbin for
dashboard screens across SaaS analytics products" for a visual task —
state this plainly so the user can judge whether the selection method
matches what they actually wanted>

**Mining tool:** <state which tool this run will use, and its status —
e.g. "DeepWiki (connected) — used where it covers a candidate, manual
search as fallback" | "Mobbin (available, requires your paid plan) —
asking below whether to connect it" | "Manual search/fetch only — no
specialized tool found or available for this source type">

**Who performs the deep mining:** <"Solo — main agent mines every source
sequentially" | "Subagents — one per source/category in parallel; briefs
built with the /subagent skill if present (see workflow.md → 'Who
performs the deep mining')">

**Distinctness check:** <for a codebase task: "each candidate below is
judged distinct from the others at a glance (different language,
architectural approach, problem space, scale) — not verified by deep
mining; if candidates converge once mined, that's a finding to report,
not a flaw in this plan." For a visual/design task: "candidates are NOT
pre-filtered for distinctness at this stage — visual sources can look
different by name/source and still turn out to be near-duplicates once
actually viewed, so dedup happens after collection, before deep analysis
(see workflow.md → Phase 2). This plan may include sources that get
removed as duplicates once mining starts.">

## Candidates

| # | Source | URL | Why it's a plausible candidate | Link status |
|---|--------|-----|-------------------------------|-------------|
| 1 | <name> | <url> | <one clause — why it's distinct/relevant/"top"> | ✅ verified |
| 2 | <name> | <url> | <one clause> | ✅ verified |
| ... | | | | |

<!--
  Every URL must be checked before this plan is shown to the user — no
  4xx/5xx, and it must actually resolve to the claimed source (not a
  redirect to an unrelated page, a dead fork, an archived placeholder,
  etc.). For codebase sources, use scripts/fetch_repo.sh --verify (or
  fetch_repo.ps1 -Verify). For visual/design or other non-repo sources,
  fetch the URL directly and confirm it resolves to the claimed content.
  Mark status accordingly; don't include a candidate whose link doesn't
  verify — find a replacement instead.
-->

---

Reply to approve this plan as-is, or tell me what to change — swap a
specific candidate, adjust the count, change the discovery criteria, or
anything else.
<!--
  If Mining tool above is "available but not yet connected," fold the
  connect/decline choice into this same message (e.g. via
  suggest_connectors) rather than a separate follow-up — the user should
  be able to approve the plan and settle the mining approach together. If
  the tool requires payment (e.g. Mobbin), say so plainly here too.
-->
I'll only start mining once this list is approved.
