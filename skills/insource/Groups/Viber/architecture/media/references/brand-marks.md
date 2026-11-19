# Brand marks & icons: source the bytes, never draw the glyph

The founding failure this pillar exists to stop: asked for a "Sign up with
Google" button, the model hand-draws the "G" as an inline `<path>`. It is
wrong twice — it reads amateur at exactly the sizes people judge, and it is a
trademark problem, not a taste problem. Every claim below is quoted from the
brand owner's own guidance or measured from the owner's own file (2026-11-18;
per-claim confidence in the workshop dossier).

## 1. The law, in each owner's own words

- **Google** (branding-guidelines, fetched): the page is a **gate**, not
  advice — *"your website or app **must follow these guidelines to complete
  the app verification process**."* Its Don'ts name imgery's exact failure as
  two separate Don'ts: *"**Create your own icon for the button**"* and *"use
  an **outdated** Google "G""*. Also: *"you can't change the size or color of
  the Google "G" logo… it must be the standard color version… on a **white
  background**"*; *"If you need to create your own custom size Google logo,
  **start with any of the logo sizes included in the download bundle**."*
  "Start from the file, never from scratch."
- **Meta/Facebook** (brand center, "Updated December 2024", fetched): *"use
  the link below and **don't download a logo from a Google search which may be
  out of date or incorrect**"*; *"Any logos or images found elsewhere on the
  web are **not approved for use**."* An icon aggregator is, by their words,
  "somewhere else." And it forbids the whole hand-drawn idiom for Facebook:
  *"**DON'T outline the logo**"* and *"**DON'T design your own logo word
  mark**"* and *"use just the 'f'… the logo must be **complete and
  unaltered**."*
- **Apple** (IP guidelines, fetched — the strictest): *"except pursuant to an
  express written trademark license"*; *"You may not use **an image of a real
  apple or other variation**"* — the approximation *is* the offence; and the
  most quotable line for the skill: a permitted product image must be *"an
  **actual photograph of the genuine Apple product and not an artist's
  rendering**."* Apple explicitly separates real assets from hand-made
  approximations and bans the latter.
- **GitHub** (brand.github.com, fetched — note `github.com/logos` now 301s
  there, the memorised path is stale): *"**No adaptation or use of any kind**
  … without the express written permission"* — the ban is on *adapting*,
  i.e. drawing your own, not just republishing theirs; and *"Do not modify…
  including changing the color, dimensions, or combining with other… design
  elements."*

Doctrine line: **for a third-party mark there are exactly two sanctioned
artifacts — the owner's SDK-rendered control, or the owner's downloaded file.
Everything else (hand-drawn, redrawn, recolored, "found on the web") is a
defect with legal weight.**

## 2. The "outlined vs colored?" question, answered per brand

The brief's question — outlined Google "G" or colored? — has a per-brand, not
universal, answer; this is the table to internalize:

| Brand | Color rule | Outline/mono allowed? | Standalone badge? |
|---|---|---|---|
| Google "G" | standard-color gradient **on white**; button G size/color fixed | **No** — "Don't use monochrome versions of the G for the button" | only inside the official button boundary |
| Facebook "f" | Facebook Blue + white "f" (primary); white + transparent-f on blue | **No** — "Don't outline the logo" | complete & unaltered only |
| GitHub Invertocat | white, black, or in few cases grey/green; "when in doubt highest contrast" | **Yes** — explicitly monochrome-friendly | only "where the brand is already clearly established" |
| Apple logo | (license-gated) | n/a — no self-serve download; SDK/press asset only | per license |

So "outline vs color" is decided **by the brand's own policy**, and the two
ends of the axis both occur (Google/Meta forbid mono; GitHub invites it).
Guessing "outlined looks more minimal/professional" is precisely the amateur
move: for Google it is a named Don't.

## 3. How to obtain the vector — the delivery ladder (Google's spine)

Prefer higher rungs; the whole point is that the top rung is self-updating:

1. **The provider SDK** — Google Identity Services *"renders a button that
   always adheres to the most recent branding guidelines. They are the
   recommended way."* Apple's `ASAuthorizationAppleIDButton` likewise. Highest
   rung because the vendor owns currency.
2. **Vendor configurator** → Google's HTML configurator downloads an
   HTML/CSS snippet.
3. **Pre-approved download** → Google's exact asset URL
   `developers.google.com/static/identity/images/signin-assets.zip` (measured
   this session: 200, 855,303 B, 24 SVGs + PNG @1×–@4×, folders keyed
   Theme/Show-text/Shape). GitHub `brand.github.com/GitHub_Logos.zip`
   (499,228 B, **128 entries but only 60 real assets**: 20 SVG + 20 PNG +
   20 PDF plus 64 `__MACOSX/._*` resource-fork twins and `.DS_Store` —
   the dossier's first tally of "40 per format" was itself inflated by
   exactly this junk, caught by the lab; see §6). Meta ships
   `Facebook-Brand-Asset-Pack.zip` but behind a **signed, expiring**
   clickwrap URL — you cannot hotlink or re-fetch it deterministically →
   **download once, commit the bytes** next to the guideline URL + date +
   terms note.
4. **Custom adaptation — explicit last resort**, and even then "start from
   the bundle."

**Vendor links expire; the bytes must outlive them.** Google branding assets
were measured serving a 24 h `Expires` window (the hub's download links
reportedly carry `X-Goog-Expires=86400`); Meta's pack is a signed clickwrapped
`scontent` URL. So the download-once pattern is not laziness, it is the
spec — and each vendored asset gets a **sidecar row**: final URL, fetch date,
the authorizing clause (quote or §link), variant used (theme/shape/badge),
rights split (mark ≠ file), `modification: none`, and a refresh cadence
(re-check when the brand re-skins; GitHub's dated deprecated-logos list shows
the cadence exists in the wild).

**Never hotlink a brand asset from a directory path.** Content-hashed vendor
paths are stable per file (Google `static/…`, Meta's `rsrc.php/y9/r/<hash>.svg`);
directory/versionless paths silently swap contents — see §5.

## 4. The decisive proof the "G" is not hand-drawable (measured)

Opening Google's official badge SVG in this session: the "G" is a `<mask>`
containing the silhouette, over **seven `feGaussianBlur` filters** on colored
`<ellipse>` blobs (`#3186FF`/`#FF4641`/`#FF5B8B`/`#E94FFF`), with the angular
gradient expressed as an **XHTML `foreignObject` carrying a CSS
`conic-gradient(…)`** (offset x=−2105.64, four thousand units wide) scaled by
a `matrix()`, with raw Figma node-ids and `data-figma-gradient-fill`
attributes rather than `<defs>`. A model drawing "the Google G" from memory
produces a flat four-arc pinwheel — it is not the same object. Engineering
consequence measured from the same fact: **the `foreignObject` renders empty
in non-browser rasterizers** — SVG-in-SVG pipelines (icon build steps,
OpenGraph image generators) should use the bundle's PNG tier or the SDK.
Geometry (measured): badge `viewBox 0 0 40 40`, square corner radius 4, pill
r=19.5; text button `viewBox 0 0 180 40`. Spec colors verbatim: light fill
`#FFFFFF`/stroke `#747775`, text `#1F1F1F`; padding 12/10/12 (iOS
16/12/16); font is **Google Sans Medium** (the old Roboto Medium 500 spec is
superseded — training-data trap: agents still emit it; re-fetch specs, date
the fetch).

Related trap from the same evidence: **"Sign in with X" buttons ship as
fixed-size images with the TEXT OUTLINED** (Google 180×40; Microsoft's
`ms-symbollockup_signin_dark.svg` 215×41, 19 paths, zero `<text>` elements —
measured). Localizing that text is impossible by construction; the correct
i18n pattern is **badge-only official mark + your own accessible text**, not
the lockup file. Google's prominence rule also generalizes beyond buttons:
*"Don't use Google's palette or fonts in your own UI"* — an agent restyling a
whole auth page in brand chrome violates the very page it fetched the asset
from.

## 5. Two icon pipelines, one channel ranking

General UI icons and third-party brand marks are different pipelines —
confusing them is a common agent error (reaching for the icon package for a
"Sign in with GitHub" button):

- **`ui` pipeline:** Lucide/Heroicons/Phosphor/Primer ship **zero
  third-party marks**; only a vendor's own package may carry its own logo
  (`@primer/octicons` → `mark-github-16/24.svg`, MIT).
- **`brand` pipeline:** official sources only, §3's ladder, §6's sidecar.

Channel ranking, best to worst (never fall past "official zip" without a
written waiver): **SDK → vendor's own package → official download zip →
community redraw with source recorded → hotlink (last-resort, unstable) →
hand-drawn (prohibited).**

## 6. Provenance, versions, and the grading trap (fold with fahlwy)

The repo-side hunt `Groups/Crawl/fahlwy/references/brand-logos.md` established
the sourcing mechanics; three findings cross-reference this doctrine:

- **A brand icon set has dated versions.** GitHub publishes its own *deprecated
  logos* (2008–2012, 2012–2015, 2015–2025) and states "beginning in 2025 Copilot
  no longer has a standalone logo." A still-common old glyph (the pre-2023
  Twitter bird) is a defect, not a style choice — the "use an outdated G" Don't
  generalized. **Pin the revision** you vendored and date the row.
- **Versionless ≠ current.** jsDelivr's versionless path served a file Simple
  Icons had **deleted** (openai/slack removed at v16.0.0): the stale-CDN 200 is
  the "outdated logo" Meta warns about, produced by infrastructure. Resolve
  `tags.latest` and pin it into the URL before you count or commit anything.
- **Path-count does NOT prove provenance.** fahlwy's heuristic (multi-path/
  multi-fill ≈ official) is a *complexity* signal only. GitHub's official
  Invertocat is **exactly one** `<path>` on 98×96; a community mono redraw is
  structurally identical. For marks that are simple by design (GitHub, X,
  Apple, Microsoft's squares) the **only** trustworthy discriminator is *where
  the bytes came from* — the ledger row's Source column, not the SVG. Use path
  count to flag "probably a redraw of a *complex* mark," never to certify.
- **Vendoring hygiene, measured:** Meta/Google/GitHub zips carry `__MACOSX/._*`
  resource-fork junk and `.DS_Store`; a naive `**/*.svg` glob commits non-SVG
  garbage named `.svg`. The count lies first: the GitHub pack's "40 SVGs"
  that a first-pass tally produced were 20 real files + 20 AppleDouble twins
  (lab-measured 2026-11-18; the lesson caught the dossier itself). Unzip to
  staging, magic-sniff bytes, drop the junk, count only survivors, then
  commit. Rights ≠ availability (CC0 on a file licenses the file, not the
  trademark; Font Awesome Brands is CC-BY-attribution; Commons `{{PD-textlogo}}`
  still carries `{{Trademarked}}`) — set the ledger `rights` column from the
  owner's terms, and never present a scraped paid library (IconScout/LogoDB/
  Brandfetch) as free.

## 7. Social-login / third-party-button stacks

Google's prominence rule (fetched): the button *"should be displayed **at
least as prominently** as other third-party sign-in options… same size and
similar visual weight."* So a provider stack is an accessibility + fairness
constraint, not a layout whim, and the CTAs are constrained: "Sign in with
Google" / "Sign up with Google" / "Continue with Google" — never "Google"
alone, and the action must read as signing into *your* app.

## 8. Non-brand icons (the other 90%)

General icon-set craft — one grammar (canvas/stroke/caps/gap/corner),
`currentColor` single-token color, sprite-vs-component delivery limits, sizing
(`em`/`lh`/px/props), baseline-in-button traps, and **icon fonts are legacy** —
is owned by [svg-engineering](./svg-engineering.md) and
[fonts-delivery](./fonts-delivery.md). Brand marks differ from general icons in
exactly one way that matters: **for general icons quality is the goal; for
brand marks provenance is the goal** — a technically perfect redraw of a real
logo is worse than an ugly-but-official file.

## Sources (all fetched 2026-11-18 unless noted)

- Google: [Sign in branding-guidelines](https://developers.google.com/identity/branding-guidelines); [Google brand features / permissions](https://www.google.com/intl/en/permissions/); asset zip `developers.google.com/static/identity/images/signin-assets.zip` (measured)
- Apple: [Guidelines for Using Apple Trademarks](https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html)
- GitHub: [brand.github.com/foundations/logo](https://brand.github.com/foundations/logo); `GitHub_Logos.zip` (measured); `github.com/logos`→301 behavior
- Meta: [brand/resources/facebook/logo](https://www.facebook.com/brand/resources/facebook/logo) ("Updated December 2024"); signed expiring asset-pack URL (measured behavior)
- Repo-side: [fahlwy brand-logos.md](../../../../Crawl/fahlwy/references/brand-logos.md) (slug/version/trademark grading, verified)
Per-claim confidence marks: `.subagents/research-imgery-icons.md` (workshop evidence, not doctrine).
