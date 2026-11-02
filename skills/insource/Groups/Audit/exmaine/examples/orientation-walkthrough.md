# Worked orientation pass (small fictional project)

Compressed to show the shape of a run, not its size.

## What was found, in order

**Entry.** `AGENTS.md` exists: declares workflow doc, units catalog, a Commitments section, and a
Skills line ("whenever you use the `plan` skill, read `docs/planning-rules.md` first").

**Doc chain.** Read: `docs/WORKFLOW.md` ✅, `docs/UNITS.md` ✅, `docs/planning-rules.md` ❌ broken
pointer, `GLOSSARY.md` ✅ (defines "lead" as a sales contact, not the HTML tag — mattered later).
Second hop: WORKFLOW references `docs/deploy.md` ✅. Ledger built from the claims in §01.

**Sweep.** Manifest declares `dev`/`build`/`test` scripts (quoted only, never run). Bootstrap
registers 6 of the 8 modules UNITS.md lists; `src/reporting/` is imported nowhere; one route
handler file is missing while the router references it (a certain static break).

**Cross-check, three representative lines:**

| Claim (source) | Verdict | Evidence |
|---|---|---|
| "Only `LeadStore` writes leads table" (UNITS.md) | CONTRADICTED | `src/crm/QuickAdd.ts:41` inserts directly |
| "Reporting module is live" (UNITS.md) | PARTIAL | E1 only — files exist, nothing imports them |
| "Deploy runs on tag v*" (docs/deploy.md) | CONFIRMED-static | `.github/workflows/deploy.yml:4` on: tag, E4, never executed |

**Gap ledger (excerpt):** broken pointer `planning-rules.md`; orphan `src/reporting/`; router →
missing handler (`routes.ts:12`); double truth: retry constant `3` in `api.ts:8` and `5` in
`sync.ts:20`; gitignored `.env` is tracked in git.

**Runtime unknowns (handed to the user, quoted from the project):** `npm test` (does the suite
pass), `npm run dev` (does it boot), deploy workflow outcome. None run by exmaine.

## The one-screen takeaway, as written

> Inventory-lite CRM, Vue+Express. Docs mostly honest: 14 of 17 claims CONFIRMED-static, 1
> contradicted (direct table write), 2 unimplemented/stale. Newcomer must know: leads vocabulary
> from GLOSSARY, the single-writer rule (currently broken), and that reporting is dead code.
> Biggest risks: tracked .env, router pointing at a missing handler, retry constant forked.
> Docs trust level: usable, with the two citations above corrected before reuse.

No recommendations were written; the user asked for fixes after seeing the ledger.
