# 08 — Gates: what a machine proves and what a human must

The repo can prove the tags, the bytes, the sizes, the alpha posture, and the pixels. It cannot prove that
Facebook shows the card. Ship both halves, and never blur them.

## 1. The conformance suites

Six suites, each asserting one contract. Names below are from the reference run; keep the shape, adapt the
names.

| Suite | Asserts | Fails when |
|---|---|---|
| `goldenOgContract` | every indexable route × locale emits the full OG + Twitter block, absolute URLs, `og:image` ends in `.png`, `og:locale` is `ll_TT`, alternates present | a route forgets a tag, or emits a relative/localhost image |
| `ogDynamicCards` | the dynamic route renders a real entity; ETag → 304; unknown/private/throwing all return 200 + static card + the right `X-Og-Card` | a fallback returns 404/500, or the cache ignores the entity version |
| `ogRenderFallback` | the static card is served when the renderer is made to throw | the fallback path re-enters the renderer |
| `ogRenderFidelity` | five ±2 px ink-box baselines; `fontFiles: []` yields a **0 × 0** box | the layout drifts, or the font is not what renders |
| `goldenBrandAssets` | all 70 files exist at exact sizes; alpha posture per file; maskable safe zone by luminance; `--check` reports no drift | a size is wrong, an icon gained alpha, the generator drifted |
| `goldenBrandPalette` | `BRAND_MARK` equals the measured values; `BRAND_ACCENT` equals the stylesheet token | someone re-tones the mark or changes the accent without the module |

Two of these are the ones that earn their keep immediately:

- **The `fontFiles: []` contrast.** Without it, a fidelity test can pass on a machine that happens to have
  the font installed. With it, "the file is embedded" is a fact.
- **The maskable luminance check.** The naive version ("no bright pixels outside the centre") passes on a
  broken icon because the background *is* bright at the edges. Threshold on luminance and it becomes a real
  test.

## 2. The drift gate

Generated assets are committed, so the risk is silent divergence: someone edits the palette, the icons stay
old, and the shipped favicon disagrees with the card.

```
bun run assets:brand:check     # regenerate into a temp dir, compare bytes
bun run assets:brand           # write the files
```

- `--check` must run in `prebuild` (and therefore in `check`), not in a script someone remembers.
- It must not need Bun-specific APIs, or the gate becomes runtime-dependent and gets skipped.
- Reference cost: ~14.8 s for 70 files. Acceptable in `prebuild`; too slow for a pre-commit hook.
- On Windows, a passing run can still print to stderr and make the shell report a non-zero exit; read the
  actual output, not only the exit code.

## 3. What else must stay green

| Gate | Why it touches this work |
|---|---|
| `seoFirstPacket100` | the meta block is injected by the same SSR path; a card change must not cost a point |
| no-hardcode / translation check | card copy is keyed; a literal string is caught here |
| architecture boundaries | the encoder must not be imported through a barrel that reaches the browser |
| doc orphan / broken-link sentinel | every new doctrine, playbook, and ADR must be linked from an index |

**Know your rubric's blind spot.** The common on-page SEO rubric (the 100-point kind shipped with most SEO
checklists and skills) scores title/headings/meta/media/code/url and has **zero** Open Graph checks. A page
can be 100/100 and share as a bare URL. That is the reason the Social Card Contract is a separate doctrine
with its own tests — not a section inside the SEO rubric. Verify the claim on your own tool before repeating
it; the point is the blind spot, not the tool.

## 4. Pre-flight with curl (do this before the eyeball round)

```bash
# 1. The page really emits the tags in the raw packet
curl -s https://example.com/ar/listings/some-entity | grep -E 'og:|twitter:'

# 2. The image URL in og:image is reachable, PNG, and the right size
curl -sI https://example.com/og/listings/ar/some-entity.png
#   expect: 200, content-type: image/png, cache-control, etag

# 3. The image really is what you think
curl -s https://example.com/og/listings/ar/some-entity.png -o card.png
#   open it: 1200x630, opaque, Arabic on one line, mark not on the ribbon

# 4. Caching works
curl -sI -H 'If-None-Match: "<etag>"' https://example.com/og/listings/ar/some-entity.png
#   expect: 304

# 5. A crawler sees the tags, not the SPA shell
curl -s -A 'facebookexternalhit/1.1' https://example.com/ar/listings/some-entity | grep og:image
```

Step 5 is the one people skip. A CDN or proxy that serves the client-rendered shell to unknown user agents
kills the card while every browser test passes.

## 5. The human round

Nine surfaces, one pass each. Use each platform's own inspector where it exists; otherwise paste the URL
into a real post draft.

| Surface | How | What to look at |
|---|---|---|
| Facebook | Sharing Debugger → paste URL → "Scrape Again" | title, description, image, no warnings |
| LinkedIn | Post Inspector | image renders; title not truncated |
| X / Twitter | compose a post, paste the URL, wait for the card | `summary_large_image`, image not cropped |
| Telegram | send the link to yourself | image, title, description |
| WhatsApp | send the link to yourself | image present (WhatsApp is the strictest about size) |
| Slack | paste in a channel | unfurl block, image not letterboxed |
| Discord | paste in a channel | embed colour, image |
| iMessage | send the link | preview card |
| Google / Bing | Search Console URL inspection | the crawler sees the same first packet |

Record, per surface: **pass / generic card / no card**, plus the date. Each platform caches for days; a
"fix" that has not been re-scraped is not a fix.

## 6. Sign-off table

| Check | Owner | Evidence |
|---|---|---|
| tags in raw packet | machine | `goldenOgContract` |
| image exists and is 1200 × 630 opaque PNG | machine | `goldenBrandAssets` |
| entity card renders | machine | `ogDynamicCards` |
| fallback never errors | machine | `ogRenderFallback` |
| layout stable | machine | `ogRenderFidelity` baselines |
| palette not re-toned | machine | `goldenBrandPalette` |
| no drift | machine | `assets:brand:check` in `prebuild` |
| platform A … platform I | **human** | the table above, dated |

Pass criteria for the whole task: every machine row green **and** every platform row observed. A green build
with an untested platform is "implemented", not "working".

## 7. Test-writing rules for this domain

- **Bytes, not "looks similar".** The generator is deterministic; compare files.
- **Baselines are ink boxes**, not full-image hashes: a 1 px antialiasing difference across renderer versions
  should not fail the build, but a moved line should.
- **Assert the negative branch explicitly** — force the renderer to throw, force an unknown slug. Untested
  degradation is unverified degradation.
- **Never assert on the platform's behaviour.** No test can prove Facebook's cache. Keep that in the human
  table so the boundary stays honest.
- **Record measurements with their method** in the test or the ADR ("±2 px", "at 300 px display width"), or
  the next person cannot tell a tolerance from a guess.
