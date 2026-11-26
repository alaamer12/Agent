# 09 — Governance: the ADR, the docs sweep, the commit

A brand-asset pipeline is a **durable architectural decision**, not a task. Six months later someone will
want to change the accent colour, add a family, or "just use sharp". The decision record is what stops them
from re-litigating it in the dark.

## 1. The ADR

One file, `<docs>/decisions/00X-<slug>.md` (or your project's equivalent), with a header that anchors it:

```markdown
# 00X — Brand assets, OG renderer, and palette

- **Date:** <YYYY-MM-DD>
- **Commit:** <sha>
- **App-Version:** <x.y.z>
- **Status:** Accepted
```

Sections, in this order:

| Section | Content |
|---|---|
| Question | the decision being made, in one paragraph |
| Context | what exists, what is broken, what the constraints are (one raster master, no vector, RTL product, no browser at request time) |
| Options | the real candidates with their rejection reason — **including the ones you rejected with evidence** |
| Choice | the decision, stated plainly |
| Consequences | what becomes true, what becomes harder, what is now a rule |
| Reversal | what would have to change to undo it |

Include the **measurements**, with the method:

- Phase 0 selection gate: resvg vs Chromium ink boxes, identical within 1 px on pure Arabic, differing on
  mixed script → the one-script-per-line law.
- `Bun.Image` capability probe: what exists, what does not, and the fact that it does not exist under Node.
- `pngjs`: `dePalette` is read-only, so it cannot write an indexed PNG.
- Byte results: 124–136 KB per card, colour type 3, on the first rung of the ladder.
- Render cost: 550–1100 ms cold, cached after.
- Splash flattening: 978 KB → 586 KB each.

An ADR without numbers is an opinion. An ADR with numbers someone can re-run is a decision.

## 2. The docs sweep — where a fact lives, once

This work touches more documents than any other feature of its size, because it changes the *brand* layer.
The rule is one owner per fact, everyone else points.

| Fact | Owner | Everyone else |
|---|---|---|
| what each asset is, its size, its alpha posture | the media/asset **pillar** | links to it |
| the social card contract (tags, `og:locale`, alt text) | the SEO **doctrine** section | links to it |
| route, cache, invalidation, degradation ladder | the backend **function** doc | links to it |
| the palette values and their two roles | the **palette module** + a sync block | never restates hex codes |
| how to verify on real platforms | the **playbook** | links to it |
| the decision and its alternatives | the **ADR** | links to it |
| the commands and ports | `USAGE.md` | — |

**Sync blocks.** If your project keeps a table of meanings with more than one home, the brand palette is one
of them: the module, the stylesheet, the icons, and the OG cards all carry the same colours. Adding or
changing a colour means every row of that block changes in the same commit.

**The rulebook row.** Add one line to the mid-task router: "brand colour, logo, favicons, app icons, native
icons, splash, or an OG card → read the pillar §, regenerate with the script, never hand-edit a generated
asset". That single row is what makes the next agent find the pipeline instead of hand-making a favicon.

**Facts ledger.** Two facts are worth recording because they contradict what an agent would assume:

1. `pngjs` cannot write a palette PNG and `Bun.Image` is unavailable under Node — so the encoder is
   hand-written. (Prior belief: a library handles it.)
2. The SEO rubric scores zero Open Graph checks — so a 100/100 page can share as a bare URL. (Prior belief:
   SEO score covers the social card.)

Format: subject / the truth / prior belief / how it was proven, with a date.

## 3. `USAGE.md` and the changelog

- **USAGE**: the two commands (`assets:brand`, `assets:brand:check`), where the masters live, what the
  generated set contains, and the fact that `--check` runs in `prebuild`. If a command changes, this file
  changes in the same commit — it is the only operational truth.
- **CHANGELOG**: one dated entry naming the revision, what shipped (the asset count, the card matrix, the
  encoder), and the tests added. Not a file list.

## 4. The commit

One commit, because the assets, the generator, the palette, the tests, and the docs are one decision. Shape:

```
feat(seo): serve OG cards from a shared indexed-PNG encoder and gate the brand asset set
```

Body: what changed at the level of contracts (palette roles, encoder home, degradation ladder, gates), the
measured numbers, and the docs updated. Expect a few dozen files and roughly a thousand lines — that size is
normal for this class of work and is a reason to do it in one pass, not five.

Conventional Commits, imperative, English. No trailer. Generated assets are in the commit; that is the
point of committing them.

## 5. Order of operations that worked

1. **Phase 0 gate** — prove the renderer on the hardest text. Write the numbers down. Do not proceed on a
   guess.
2. **Contracts first** — palette module, copy keys, geometry, byte ceiling. No pixels yet.
3. **Cards + meta** — the user-visible failure (blank share) before the invisible one (favicon).
4. **Asset set** — the full file set, the static handler.
5. **Dynamic cards** — route, resolvers, cache, degradation.
6. **Native sets** — iOS, Android, splash.
7. **Gates** — the six suites, the drift gate in `prebuild`.
8. **Governance** — ADR, pillar, doctrine, function, sync block, router row, facts, changelog, usage.
9. **Commit** — once, with the numbers in the body.

Steps 7 and 8 are not cleanup. They are the difference between "we made some icons" and "the project has a
brand-asset contract".

## 6. Anti-patterns this governance prevents

| Anti-pattern | What it looks like | The rule that stops it |
|---|---|---|
| Hand-edited generated asset | someone nudges `icon-192.png` in an image editor | `--check` in `prebuild` |
| Second palette | a component hardcodes `#5ef06b` because "it's the same green" | one module, one conformance test |
| Copy in code | a tagline typed into the composer | keyed copy + the project's no-hardcode check |
| Doc drift | the pillar says 48 px, the generator writes 32 | the pillar points at the generator's constants |
| Phantom platform claim | "we support Facebook cards" with no observation | the human sign-off table |
| Encoder creep | a second encode path added "for speed" | one encoder, two callers, stated in the ADR |
| Silent degradation | cards are always generic and nobody knows why | `X-Og-Card` header + one log line per fallback |
