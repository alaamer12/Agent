# Snduk merge testbed — findings log

Lab: `git clone --no-hardlinks` of `F:\Projects\Languages\Python\WorkingOnIt\Snduk Inc\snduk`
into `/tmp/merge-lab/snduk` (2,154 commits, 18 remote refs).
Detection of real conflict/evil resolutions: merge commits whose `git show -c` combined diff is non-empty (resolution differs from BOTH parents).

## Population stats
- 53 merge commits total in history; only **9** carried manual resolutions.
- Dominant pattern: frequent `Merge branch 'main' into <feature>` sync-merges (small divergence, short-lived branches) — the repo's safety comes from merging main often, which the practitioner research should confirm.

## Scenario classes (with exact commits, for skill examples + merge_lab reconstruction)

### S1 — Both-ahead, different features (THE hard case)
- `24808d6f` (main × snduk-ai): merge-base = PR #18 two days earlier; side ahead: 1 vs 13 commits.
  Conflicted surfaces: `useAdminShell.ts`, `constants/permissions.ts`, `utils/ability.ts`, `router/index.ts`
  — both sides *added* different routes/permissions/capabilities near the same anchors.
- `8b0096c5` (snduk-ai merged into 2v): same file family — repeated across the repo's life.
- `2b6f0a01`, `9bfa6d40`, `de7ee144`: more S1 instances (Vue import forms, alerts page + jobs.service + app.json).
- Doctrine to derive: neither side is "correct"; union of intents + registration-order sanity + full test pass is the resolution; identity of who-is-ahead is answered by merge-base + rev-list counts, NOT by branch names.
- Reproduce commands: `git merge-base`, `git rev-list --count base..parentN`.

### S2 — Prettified vs uglified JSON (format-divergent content)
- `37dd0cdd`: `apps/admin/public/locales/ar/common.json` — parent side held the whole file as ONE minified line; resolution is pretty-printed 1118 lines (+1117/−1).
  Git saw a whole-file conflict for what is semantically a key-union.
- Doctrine: canonicalize (jq -S / json.dumps sort_keys) → semantic diff → if pure format delta, adopt formatted form + port value changes; if data delta, deep-merge with explicit array policy; never `--ours/--theirs` a structured file blindly.
- Evidence: locale files across ar/* — the repo's format flip happened in a merge, so the skill must handle "the conflict IS the formatter".

### S3 — Lockfile conflict
- `b5b6ca7d`: `bun.lock` manual resolution (+90/−60) alongside `apps/mobile/app.json`, `eas.json`.
- Doctrine: regenerate from manifests (`bun install` with both package.jsons merged), or documented merge drivers; hand-editing lockfiles is the anti-pattern with this repo as witness.

### S4 — Evil merge (behavior invented in the resolution)
- `e5ae29c2`: `apps/web/app/robots.ts` final adds `.replace(/\/+$/, '')` (trailing-slash strip) present in NEITHER parent.
- Detection command: `git show -c <merge>`; non-empty combined diff = resolution differs from both sides — legitimate ONLY as conflict glue, never as new behavior (Linus doctrine — pending wave-A citation).
- Use in skill as the "how to find sneaky merge changes" example AND the cautionary tale.

### S5 — Trivial-but-real
- `614d4e87` railway.json (small config), `e5ae29c2` also shows main-sync merges happening straight on main (fetch merge).

## For the skill's scripts/merge_lab
Reconstruct S1-S4 generically (no Snduk code): scratch repo with registration-file append conflicts; one minified vs pretty JSON; lockfile + regeneration; evil-merge detection demo. Each scenario must print the exact git output the doctrine claims.

## Open questions to settle with research waves
- What does `checkout --theirs` mean during rebase vs merge (side-swap)? [wave A]
- rerere for repeated sync-merges (this repo does the SAME registration conflicts monthly)? [wave A/B]
- Format-driver (.gitattributes merge=) viability for JSON vs regenerate policy; -X renormalize role in S2. [wave C]
- Sync-merge cadence doctrine ("merge main into feature often" vs "rebase feature onto main") — this repo chose merge; why is defensible for shared branches. [wave B]
