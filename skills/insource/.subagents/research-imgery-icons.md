# Research: imgery — brand marks, icons, and the "never hand-draw a logo" doctrine

Skill under research: **imgery** (media handling doctrine). This lane covers **icons, brand
marks/logos, and how an agent should obtain, vendor, and render them professionally**.
Companion files: `research-imgery-loading.md` (raster loading/performance lane) and
`research-imgery-vectors-media.md` (SVG mechanics, icon systems, fonts, video/audio).

Confidence marks:
- **[VERIFIED-fetched]** — read from the authoritative page (or measured from real bytes) in this session, URL given.
- **[SEARCH-asserted]** — surfaced in a search-result snippet/title only, not fully read.
- **[REASONED]** — engineering inference drawn from verified facts; no source states it directly.

Date of research: **2026-11-18 (UTC)**. All Google asset measurements were made in this session by
downloading the live bundle.

---

## 1. The Google case: the founding example, measured

### 1.1 "Sign in with Google" branding guidelines — the current spec

[VERIFIED-fetched] https://developers.google.com/identity/branding-guidelines
(fetched 2026-11-18; the whole page read, 157 lines of source).

The page opens with a compliance framing, not a style framing: *"This document provides
guidelines on how to display a Sign in with Google button on your website or app. Your website
or app **must follow these guidelines to complete the app verification process**."* — i.e. a
mis-drawn button is not a taste problem, it is a **gate failure** [REASONED].

Delivery ladder, in the order Google itself states (this is the doctrine's spine):
1. **Google Identity Services SDK** — "render a Sign in with Google button that **always
   adheres to the most recent Google branding guidelines**. They are the recommended way."
2. **HTML configurator** — "an HTML configurator that allows you to customize the appearance …
   You can then download an HTML and CSS snippet that will render the button."
3. **Pre-approved brand icons (download)** — *"you can download our pre-approved Sign in with
   Google buttons provided in PNG and SVG formats for all platforms"*, from
   **https://developers.google.com/static/identity/images/signin-assets.zip** (the `gstatic`/
   `developers.google.com/static` asset path the brief asked about — this is the real URL).
4. **Custom button** — explicitly last resort: *"If you, however, need to adapt the button to
   match your app design, adhere to the following guidelines."*

Current button spec (verbatim values from the Color/Padding/Font sections):

| Theme | Fill | Stroke | Font |
|---|---|---|---|
| Light | `#FFFFFF` | `#747775`, 1px, inside | `#1F1F1F`, **Google Sans Medium**, 14/20 |
| Dark | `#131314` | `#8E918F`, 1px, inside | `#E3E3E3`, Google Sans Medium, 14/20 |
| Neutral | `#F2F2F2` | no stroke | `#1F1F1F`, Google Sans Medium, 14/20 |

- Themes × shapes enumerated as **Light / Neutral / Dark** × **Rectangular / Pill**, and buttons
  "available in **standard and icon modes**".
- Padding (Android & Web): **12px** left of the logo, **10px** right of the logo, **12px** right
  of the text. iOS: **16 / 12 / 16**. [VERIFIED-fetched, same page]
- Size: *"You can scale the button as needed for different devices and screen sizes, but you
  must **preserve the aspect ratio** so that the Google logo is not stretched."* — note there is
  **no minimum px height in the current doc**; the widely-cited "min 40dp / 28dp" figure belongs
  to the older Google Identity Services spec. [VERIFIED-fetched for absence + REASONED attribution]
- Font: **"The button font is Google Sans Medium"**, installable from
  https://fonts.google.com/specimen/Google+Sans. **This supersedes the old "Roboto Medium 500,
  14px" spec that the brief (and most training data) still assumes** — see §1.4.
- The logo itself: *"Regardless of the text, **you can't change the size or color of the Google
  "G" logo**. It must be the standard color version (the standard color gradient super G logo)
  and appear on a **white background**. If you need to create your own custom size Google logo,
  **start with any of the logo sizes included in the download bundle**."* ← the "start from the
  file, never from scratch" clause, in Google's own words.

The do/don't table (the prohibition set the skill should quote):
- **Don't** *"Use the Google icon or logo by itself **without the button boundary and without
  text** to indicate the user action."* / **Do** *"Use the Google "G" **by itself for action
  button** if needed."* → the two are reconciled by the badge form: the G may stand alone **only
  inside the official boundary** (see §1.2). This is the real content of the brief's "badge-only
  rule". [VERIFIED-fetched wording + REASONED reconciliation]
- **Don't** *"Use **monochrome** versions of the Google "G" for the button."*
- **Don't** *"Put the standard color Google "G" icon on a colored background other than light,
  dark, or neutral."*
- **Don't** *"**Create your own icon for the button** or **use an outdated Google "G"** for the
  button."* ← both halves of imgery's founding failure, named as separate don'ts by Google.
- **Don't** *"Use the term "Google" by itself in the button."*
- Do *"Use the [Google Material](https://m3.material.io/) design guidelines for button boundary
  and color scheme"* — i.e. the corner-radius question is delegated to M3, not fixed here.
- Text: recommended CTAs *"Sign in with Google" / "Sign up with Google" / "Continue with
  Google"*, localization *"permitted and encouraged"*, and it "should be clear … they are
  signing into **your** app … not signing up for a Google Account".
- Prominence: *"The Sign in with Google button should be displayed **at least as prominently**
  as other third party sign-in options … approximately the same size and … similar visual
  weight."* → doctrine for social-login stacks [VERIFIED-fetched].
- Escalation clause: *"Use of Google brands in ways not expressly covered by this document is
  **not allowed without prior written consent from Google**"* → https://www.google.com/intl/en/permissions/
  (Guidelines for Third Party Use of Google Brand Features). [VERIFIED-fetched pointer; page not yet read — see §8]

### 1.2 Measured anatomy of the official artwork (the decisive evidence)

Downloaded live in this session: `https://developers.google.com/static/identity/images/signin-assets.zip`
→ HTTP 200, `application/zip`, 855,303 bytes, 24 SVGs + PNG tiers @1x/@2x/@3x/@4x for
`Android + Web` and `iOS`, folders keyed `Theme=Light|Dark|Neutral`, `Show text=Yes|No`,
`Shape=Square|Pill`. Timestamps inside the archive: 2026-04-15 (bundle), 2026-05-01 (dir).
[VERIFIED — measured bytes]

Geometry measured from the real files:
- **Badge-only ("Show text=No")**: `viewBox="0 0 40 40"`, `width="40" height="40"`; PNG IHDR =
  40×40 @1x. **Square** shape corner radius = **4** (path `M4 0.5H36C…` — inset 0.5 for a
  centered stroke), **Pill** shape = full round (`M20 0.5C30.77…` ⇒ r = 19.5).
- **With text ("Show text=Yes")**: `viewBox="0 0 180 40"`, PNG 180×40 @1x ⇒ **4.5:1 ratio, 40px
  tall reference height**.
- The Light badge is literally `<path … fill="white"/>` + `<path … stroke="#747775"/>`, matching
  the documented spec exactly. [VERIFIED — measured]

**The "G" is not drawable by hand. Composition of the badge SVG (tag skeleton, measured):**
1. `<mask id="mask0_1298_12516" …>` containing the G silhouette path (id format = **raw Figma
   node ids**, `paint0_angular_1298_12516_clip_path` etc.).
2. Inside `<g mask="url(#…)">`: a `<g filter="url(#filter0_f_…)">` → `<g clip-path=…
   data-figma-skip-parse>` → `<g transform="matrix(0.00804129 -0.00805186 …)">` →
   **`<foreignObject x="-2105.64" y="-2105.64" width="4211.29" height="4211.29">` holding an
   XHTML `<div style="background: conic-gradient(from 90deg, rgba(255,70,65,1) 0deg,
   rgba(255,70,65,1) 4.14555deg, rgba(49,134,25…">`** — the gradient is **HTML/CSS inside the
   SVG**, over four thousand units wide, scaled down by a matrix.
3. **Seven `feGaussianBlur` filters** (stdDeviation 1) applied to `<ellipse>` blobs filled
   `#3186FF`, `#FF4641`, `#FF5B8B`, `#E94FFF` — a soft color cloud masked into the G.
4. `<path … data-figma-gradient-fill="{&#34;type&#34;:&#34;GRADIENT_ANGULAR&#34;…}">` — the real
   angular-gradient stops serialized in a Figma-specific data attribute, not in `<defs>`.
5. Zero `<linearGradient>`/`<radialGradient>` elements. Zero `<text>` and zero `font-family`:
   **the label is outlined geometry** — which contradicts the page's own note that "The SVG
   files require the Google Sans font". [VERIFIED — measured vs. [VERIFIED-fetched] doc text]

Consequences for the skill (all [REASONED] from the measured bytes unless flagged):
- **No model can reproduce this from parametric memory.** The mark is a mask + blurred blob
  cloud + CSS conic gradient + Figma export scaffolding. "Slightly-wrong G" is the *best* case;
  the realistic agent output is a flat four-arc approximation in the 2015 palette.
- The official SVG is **fragile in non-browser renderers**: anything that ignores
  `foreignObject`/CSS `conic-gradient` or `filter` (react-native-svg, librsvg/`sharp`, resvg /
  satori OG-image generators, many icon pipelines) will render the G as a black or empty shape.
  → **Use the PNG tier or the SDK when the renderer is not a browser**, and never "simplify" the
  official SVG with an optimizer that strips `filter`/`foreignObject`/`data-*`.
- The G's colors in the 2026 artwork (`#3186FF`, `#FF4641`, `#FF5B8B`, `#E94FFF`, plus the
  conic stops) are **not** the classic 2015 four-color set (`#4285F4 #EA4335 #FBBC05 #34A853`)
  that dominates training data. → "outdated Google G" is now *the default*, not an edge case:
  the model's memory is a frozen older brand. [VERIFIED-measured for the current values;
  REASONED for the training-data claim]
- **The zip is the API.** The right "professional path" is: fetch the zip → pick the exact
  theme/shape/text variant → commit the bytes → wrap in a component. Not: search "google logo
  svg png".

### 1.3 The brief's own artifact: "ONERING logo rules"

The task brief asked for "the **ONERING** logo rules" as a Google brand element. Searched:
no Google brand asset, guideline, or file by that name exists; results return a crypto token
"OneRing (RING)" and Lord-of-the-Rings fan art. [SEARCH-asserted, negative]
**Verdict: "ONERING" is a parametric-memory hallucination in the request itself** — the exact
class of error imgery exists to prevent. The nearest real things are the **"super G" gradient
G** named in §1.1 and Google's **"one Google" / Google Sans** brand language.
→ Doctrine rule: *a spec term the agent cannot resolve to a fetched URL or byte is to be
reported as unresolved, never invented into code.* This is also a direct generalization of the
fahlwy finding "a guessed slug produces a fake ceiling" (§5).

### 1.4 What changed vs. the remembered spec (drift table for the skill)

| Claim in common training-data lore | Current official page (2026-11-18) |
|---|---|
| Roboto Medium 500, 14px | **Google Sans Medium**, 14/20 line-height |
| Blue button `#4285F4` | **White / `#131314` / `#F2F2F2` fills**, `#747775`/`#8E918F` 1px inside stroke |
| 4px corner radius | delegated to **Material 3**; shipped art = r4 (square) or full pill |
| Flat four-color G (`#4285F4/#EA4335/#FBBC05/#34A853`) | **conic/angular gradient + blurred blobs**, `#3186FF/#FF4641/#FF5B8B/#E94FFF` |
| monochrome/black G allowed on dark | **"Don't use monochrome versions of the Google 'G'"** |
| min height 40dp | no minimum stated; only "preserve the aspect ratio" |

[VERIFIED-fetched for the right column; the left column is the model's default output — flagged
as [REASONED] characterization of typical parametric memory.]
**Doctrine:** brand specs are *moving documents with an effective date*. Any icon/brand rule the
agent "knows" must be re-fetched at implementation time, and the fetched URL + date recorded
next to the vendored file. [REASONED, from §1.1–1.4]

---

## 2. Apple: the strictest "do not redraw" clause on the web

[VERIFIED-fetched] https://www.apple.com/legal/intellectual-property/guidelinesfor3rdparties.html
("Guidelines for Using Apple Trademarks and Copyrights", formerly "Guidelines for Third Parties…").
Loaded 2026-11-18; note the page is a legal document, **not** an HIG page — Apple's brand rules for
third-party marks live in Intellectual Property law pages, while the HIG governs *your* app's UI.
Related pointer cited by the same page: Apple Trademark List
https://www.apple.com/legal/intellectual-property/trademark/appletmlist.html and
Apple Web Badges https://www.apple.com/about/webbadges/ (not fetched — see §8).

The clauses that decide implementation:
- **Blanket prohibition, no license = no use**: *"You may not use the Apple Logo or any other
  Apple-owned graphic symbol, logo, or icon on or in connection with web sites, products,
  packaging, manuals, promotional/advertising materials, or for any other purpose **except
  pursuant to an express written trademark license from Apple**, such as a reseller agreement."*
  → "Sign in with Apple" art is therefore **not** something you may obtain by scraping; it ships
  only inside Apple's own SDK/UI kits and the press resources under license. [VERIFIED-fetched]
- **Anti-parody / anti-"almost" clause**: *"You may not use **an image of a real apple or other
  variation** of the Apple logo for any purpose. Third parties cannot use a variation, phonetic
  equivalent, foreign language equivalent, **takeoff**, or abbreviation of an Apple trademark for
  any purpose."* → this is the legal naming of exactly the "slightly-wrong mark" failure mode:
  an approximation is not a lesser offence, it is the offence. [VERIFIED-fetched]
- **Anti-imitation of style**: *"You may not imitate the distinctive Apple packaging, web site
  design, logos, or typefaces."* + *"You may not use or imitate an Apple slogan or tagline."*
  [VERIFIED-fetched]
- **Rendering vs photograph** (the single most quotable line for the skill): under
  "Depictions of Apple Products → Compatibility", the permitted image must be *"**an actual
  photograph of the genuine Apple product and not an artist's rendering** (Note: You must obtain
  express written permission from Apple before using any photograph owned or licensed by Apple)."*
  → Apple explicitly distinguishes real assets from hand-made approximations and forbids the
  latter. [VERIFIED-fetched]
- **Word mark ≠ graphic mark**: developers may use `Apple`/`Macintosh` etc. in a *referential
  phrase* ("for", "compatible with"), "**but not the Apple Logo or other Apple-owned graphic
  symbol/logo**", with the word mark "less prominent than the product name". → Doctrine: the safe
  fallback for a third-party logo you cannot license is **plain text of the brand name**, not a
  drawn glyph. [VERIFIED-fetched]
- **Attribution mechanics** (a real deliverable, easy to skip): ®/TM on first use for
  US-only distribution, no symbols outside the US, plus a credit line
  "`____` and `____` are registered trademarks of Apple Inc." or internationally
  "`____` is a trademark of Apple Inc., registered in the U.S. and other countries and regions.";
  and *"By using an Apple trademark … you are acknowledging that Apple is the sole owner … and
  promising that you will not interfere with Apple's rights … no other rights of any kind are
  granted hereunder, by implication or otherwise."* [VERIFIED-fetched]

What this means for an implementer building "Sign in with Apple" [REASONED from the above]:
use `ASAuthorizationAppleIDButton` / `AuthenticationServices` (or the platform equivalent), which
renders Apple's own approved button; there is no self-serve vector download for the Apple logo
in these guidelines, so the only compliant path is **the SDK's artwork or a licensed press
asset**. A hand-written `<path>` apple is a clause-2 and clause-3 violation on its face.
[REASONED — the SDK mechanism itself is not stated on this page; verify against
https://developer.apple.com/documentation/authenticationservices/asauthorizationappleidbutton]

For contrast, Apple's *design* guidance (Human Interface Guidelines) is about not confusing users
with fake system UI rather than about the logo — searched, not fetched in detail:
https://developer.apple.com/design/human-interface-guidelines/ [SEARCH-asserted]. The operative
constraint for marks is the IP page above, and App Review rejects copycat/imitative iconography
(including "imitates Apple's own apps") under its own rules — worth a follow-up fetch
(§8). [REASONED]

---

## 3. GitHub and Meta: the two most quotable "use our file, not yours" policies

### 3.1 GitHub (brand.github.com — github.com/logos is gone)

**Route fact:** `https://github.com/logos` (the URL every model has memorised as a *git repo*)
now returns **301 → https://brand.github.com/foundations/logo**. [VERIFIED-fetched behavior]
→ Doctrine: the memorised URL may still resolve but to a *different artifact* than you expect;
follow redirects and re-read, and never assume "the repo I remember" is the current source.

[VERIFIED-fetched] https://brand.github.com/foundations/logo ("Logo | GitHub Brand Toolkit")
- **Download:** `https://brand.github.com/GitHub_Logos.zip` (measured live: HTTP 200,
  `application/x-zip-compressed`, 499,228 B, 128 files).
- **Naming:** the pictogram is the **Invertocat** ("We call our logo pictogram the Invertocat —
  it represents our mascot, the Octocat. It's our primary logo"), and
  *"**The standalone invertocat may be used in GitHub-owned environments or where the brand is
  already clearly established.**"* → a badge-only rule with a *context* condition, not a size one.
- **Color policy:** *"The Invertocat and our wordmark should **only appear in white, black, or in
  few cases grey or green**. Like text, the logo should be legible and pass accessibility
  requirements in all settings. When in doubt, use the highest contrast option."* → GitHub is
  explicitly **monochrome-friendly**, the opposite of Google (see the matrix in §4).
- **Prohibitions (verbatim, "Usage"):** *"**Don't** rearrange the elements of the logo."* ·
  *"**Don't** use our illustration, mascots or Mona as a substitute for the logo."* ·
  *"**Don't** add graphic effects like shadows or gradients."* ·
  *"**Don't** place the logo over busy backgrounds."* ·
  *"**Don't** mix the color of the logo or use backgrounds that provide insufficient contrast."* ·
  *"**Don't** compress distort, skew, stretch, or alter the logo in any way."*
- **Legal (the hardest clause found in this research):** *"GITHUB®, the GITHUB® logo design, the
  INVERTOCAT logo design, OCTOCAT®, and the OCTOCAT® logo design are trademarks of GitHub, Inc.,
  registered in the United States and other countries. The OCTOCAT design is the exclusive
  property of GitHub, Inc and has been federally registered with the United States Copyright
  Office. **No adaptation or use of any kind of any of our registered trademarks or copyrights,
  or any other contents of this website, is allowed without the express written permission of
  GitHub, Inc.**"* → note the object of the ban is "**adaptation**", i.e. drawing your own
  version, not just republishing theirs.
- **"Don't do these things" list** [VERIFIED-fetched]: *Imply affiliation* ·
  *Use as your logo* — *"Do not use any GitHub logo as the icon or logo for your
  business/organization, offering, project, **domain name**, social media account, or website."* ·
  ***Modify the logo*** — *"Do not modify the permitted GitHub logos, **including changing the
  color, dimensions, or combining with other words or design elements**."* ·
  *Use without permission*.
- **Permitted uses that matter to an implementer:** *"**Link to GitHub** — Use a permitted GitHub
  logo to link to GitHub."* and *"**Social button** — Use the Invertocat logo as a social button
  to link to your GitHub profile or project."* → the "Follow me on GitHub" button is explicitly
  sanctioned, **provided the art is the permitted file**. [VERIFIED-fetched]
- **Deprecated logos section (rare and valuable):** GitHub publishes its own obsolete marks —
  *"Deprecated logo versions from 2012-2015 and 2015-2025"*, *"Deprecated logotype versions from
  2008-2012 and 2012-2025"*, and *"**Beginning in 2025, GitHub Copilot no longer has a standalone
  logo** that heros the Copilot icon."* → official proof that a brand's icon set has **versions
  with dates**, and that a still-common old glyph is a defect, not a style choice.
- Page also links: `GitHub-BrandGuidelines-2026.pdf`, `https://asset-generator.github.com` (an
  official asset generator!), Primer/Octicons (`https://primer.style/octicons`), and
  `https://github.com/github/brand.github.com/blob/main/content/foundations/logo.mdx` — i.e. the
  brand site's **source is a public repo**, so guideline text is diffable. [VERIFIED-fetched]

**Measured bytes of `GitHub_Logos.zip`** [VERIFIED — measured this session]:
- Format tiers: **40 SVG + 40 PNG + 40 PDF**, named `GitHub_Invertocat_Black.svg`,
  `GitHub_Lockup_White_Clearspace.png`, `Copilot_Lockup_Black.pdf`, …
  → grammar = `{Brand|Product}_{Mark}_{Color}[_Clearspace].{svg|png|pdf}`, with **separate
  "Clearspace" files** that bake the exclusion zone into the artwork. That is the vendor-ready
  naming convention to copy in a repo (`assets/brand/github/invertocat--black.svg`).
- `GitHub_Invertocat_Black.svg`: `width="98" height="96" viewBox="0 0 98 96"`,
  **exactly one `<path>`**, fills `black`/`white`/`none`, with `<clipPath id="clip0_730_27126">`
  (again Figma-export node ids). `GitHub_Lockup_Black.svg`: 2 paths, `viewBox="0 0 416 95"`,
  **no `<text>`** (the wordmark is outlined geometry).
- **The grading heuristic breaks here, and that is the lesson.** fahlwy's rule "multi-path /
  multi-fill ≈ official artwork; one 24×24 path = community redraw" (§5) would score GitHub's
  *official* Invertocat as a community mono glyph: 1 path, single color, 98×96 not 24×24.
  **Path count grades *complexity*, never *provenance*.** For marks that are simple by design
  (GitHub, X, Apple, Microsoft's four squares) the official file and a redraw are structurally
  identical — so the only trustworthy discriminator is **where the bytes came from**.
  [VERIFIED-measured + REASONED doctrine]
- Vendoring gotcha, measured: the zip contains `__MACOSX/._GitHub_Invertocat_Black.svg` (219 B
  AppleDouble resource-fork junk) plus 4 `.DS_Store` entries. A naive `**/*.svg` glob commits
  **non-SVG garbage with an .svg extension**. → Unzip to a staging dir, magic-sniff, drop
  `__MACOSX`/`._*`/`.DS_Store`, then copy. [VERIFIED-measured]

### 3.2 Facebook / Meta — the most explicit anti-search-engine clause in existence

[VERIFIED-fetched] https://www.meta.com/brand/resources/facebook/logo/
("Facebook brand resources and guidelines", page states **"Updated December 2024"**).
Note `about.meta.com/brand/resources/facebookapp/logo/` **404s** after redirect; the live path is
`/brand/resources/facebook/logo/`. Sibling pages: Messenger icon, and brand centers for
Meta / Instagram / WhatsApp / Threads on the same host. [VERIFIED-fetched]

- **The founding sentence of imgery, in Meta's own words:** *"You can download our logo from the
  link below. It's important you use the current version of the logo. **Please use the link below
  and don't download a logo from a Google search which may be out of date or incorrect.**"*
- **FAQ hammer:** *"Can I use Facebook logos and images I found somewhere else on the web? —
  **Any logos or images found elsewhere on the web are not approved for use.** … only using
  approved brand assets from this site."* → an icon CDN (Iconify, LogoDB, Brandfetch, "300+ free
  Facebook icons" aggregators) is *by definition* "somewhere else on the web". For brand marks
  the licensing path is the brand center, full stop. [VERIFIED-fetched]
- **"Don't make your own" clause, literally:** *"**DON'T design your own logo word mark** — Do
  not combine the logo with 'acebook'."* · *"**DON'T use just the 'f' from our logo** — The logo
  must be **complete and unaltered**."* · *"DON'T use our word mark instead of our logo."* ·
  *"DON'T use our thumbs up 'like' symbol."* · *"DON'T write the word 'Facebook' next to the logo
  — Do not connect any other words to the logo."* · *"DON'T add emojis to the logo."*
- **Color / effect policy:** *"DON'T change the color of the logo — Do not **recolor our logo to
  your own brand colors**."* · *"DON'T **outline** the logo — Do not use an **outline** or any
  other version of the logo."* ← this kills the entire "stroke-based hand-drawn brand icon" idiom
  for Facebook · *"DON'T make the logo 3D."* · *"DON'T put a drop shadow on the logo — Do not use
  drop shadows or effects."*
- **Approved expressions:** primary = *"Facebook Blue with a white 'f'"*; on white is the primary
  use; over imagery the *"'f' is always white in this case, **never transparent**"*;
  secondary = *"white with a transparent 'f'"* on Facebook Blue.
- **Metrics:** clear space = *"the width of our logo **divided by four** … (1/4 X). This space
  applies to all applications."*; **minimum size "16px wide" digital / "6mm" print**; logo should
  be "at least half a logo distance away from any other content".
- **Enforcement framing:** *"Meta dedicates substantial resources to the development and
  protection of its intellectual property … **Meta enforces its rights against people who misuse
  its trademarks.**"* · *"**We may revoke permission** to use Meta's trademarks at any time.
  Meta reserves the right to withhold approval…"* · no merchandise licensing at all.
- **Where the vector actually is (architecture-relevant):** the pack is
  `Facebook-Brand-Asset-Pack.zip`, served from a **signed, expiring `scontent.*.fbcdn.net` URL**
  behind a clickwrap ("I have read and accept the applicable guidelines and other terms for
  use."). → **You cannot hotlink Meta's asset and you cannot re-fetch it deterministically**: the
  URL dies, so the only workable engineering pattern is *download once, commit the bytes with the
  guideline URL + date + terms note next to it*. Meta's own logo for schema.org markup is a
  versionless static CDN path `https://static.xx.fbcdn.net/rsrc.php/y9/r/tL_v571NdZ0.svg` —
  the `rsrc.php/y9/r/<hash>.svg` shape is content-hashed, so it is stable *per file*, which is
  why gstatic/fbcdn-style hashed paths are safe to pin while *directory* paths are not.
  [VERIFIED-fetched URL, REASONED caching interpretation]

---

## 4. Google's own brand center, Microsoft, and the recolor policy matrix

### 4.1 Google Partner Marketing Hub — "how to show Google's brand"

**Route fact:** `https://about.google/brand-resource-center/brand-elements/` (the URL models
memorise, and the URL Simple Icons still records as Google's `guidelines`) **301-redirects to**
**https://partnermarketinghub.withgoogle.com/brands/google/branding-guidelines/how-to-show-googles-brand/**
[VERIFIED-fetched: curl `-L` final URL + full read of the destination page]. The hub is
partly gated ("Please complete your application to access brand resources", `/signup/`), and its
download button carries a **confidentiality + approval clickwrap**: *"I understand that these
assets are subject to **strict confidentiality restrictions** … Google reserves the right to
review and request changes to my final creative."*

[VERIFIED-fetched] destination page content:
- Nomenclature, settled: *"**We have two logos: the Google logo (also called a wordmark) and the
  Google G.**"* … *"The Google G (**sometimes called the "Super G"**) is our second logo."* → this
  is the "super G" that the Sign-in page's phrase "standard color gradient super G logo" refers
  to; §1.1's odd wording is explained.
- **The outdated-glyph rule, official:** *"**We recently redesigned our Google G with an updated
  style. Be sure to always use the latest, correct version of the Google G.**"* ·
  DO *"Only use the newest version of the Google G (**the one with blended gradient colors**)."* ·
  **DON'T** *"**Don't use older versions of the Google G.**"* · for product icons: *"We're in the
  process of redesigning our product icons, so be sure to use the most up-to-date versions."*
- **No-redraw / no-recolor clauses:** DON'T *"Don't combine your logo with Google's or **modify
  the Google logo in any way**."* · DON'T *"Don't combine your logo with the Google G or **modify
  the Google G in any way, including changing the color**."* · *"Always use the full-color Google
  G. **Stick to white or black backgrounds** so the Google colors look correct."* ·
  *"Don't place the Google G on backgrounds that inhibit legibility."*
- **Clear-space rule of thumb (scale-relative, like Meta's):** *"Keep enough clear space around
  the Google G. **Use the width of the Google G to determine the minimum amount of clear space on
  all sides.**"* (same for the wordmark, keyed to the width of the G).
- **The counterintuitive one — and arguably the most useful rule in this document:**
  *"**Never use Google's brand colors or brand fonts in your work.** Make it clear that the work
  is coming from you, not from Google."* · DON'T *"Don't use Google's brand colors in your work.
  **This includes websites and apps**, as well as merchandise…"* ·
  DON'T *"Don't use **or mimic** Google's brand font in your work."*
  → a compliant "Sign in with Google" button must ship **Google's mark** while the *surrounding*
  UI must not borrow Google's palette or type. This kills the common agent move of restyling a
  whole auth page in `#4285F4` + Roboto. [VERIFIED-fetched]
- **Anti-screenshot-forgery:** *"Don't **recreate or modify** Google's product UI."* (product
  visuals are allowed for educational/informational use but must be accurate — the same "real
  asset, not a rendering" principle Apple states in §2.) Also *"Don't use Google Doodles in any
  way."*
- **Where the files actually are, measured from the page's own links:** assets are served from
  **`https://storage.googleapis.com/pe-portal-consumer-prod-wagtail-static/…`** with **signed
  `X-Goog-…` parameters and `X-Goog-Expires=86400`** (observed: `X-Goog-Date=20261118T173143Z`,
  i.e. the link dies in 24 h). Formats offered: `GoogleLogo_RGB_Color.png` (96 KB),
  `GoogleLogo_CMYK_Color.eps` (5.1 MB), `GoogleLogo_CMYK_Color_Med.jpg` (3.7 MB),
  `GoogleG_FullColor_RGB.eps` (3.4 MB), `GoogleG_FullColor_RGB.png` (134.5 KB),
  `GoogleG_FullColor_CMYK_Coated_Small.tif/.jpg`.
  → **Two architectural consequences.** (1) These links **expire daily**, so they cannot be a
  build-time dependency; they must be vendored once (same conclusion as Meta, §3.2). (2) The brand
  hub ships **no SVG at all** — its vector tier is **EPS**; the web-vector tier is
  `signin-assets.zip` (§1) or a conversion of the EPS, which re-introduces fidelity risk.
  [VERIFIED-fetched URLs + REASONED consequences]

### 4.2 Microsoft — the strictest wording of all, plus a *downloadable* button SVG

[VERIFIED-fetched] https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks
("Microsoft Trademark and Brand Guidelines"; note the path has **no hyphen**
(`intellectualproperty`) — the hyphenated `/legal/intellectual-property/…` variants 404, as do
`microsoft.design/brands/microsoft/geist`, and `brand.microsoft.com` fails to connect
[VERIFIED by curl status]).
- Definition: *"Microsoft's brand assets—including the Microsoft Trademarks (PDF), logos, icons,
  designs, trade dress, **fonts**, names of Microsoft software, products, services, sounds,
  **emojis**, and any other brand features and elements, whether registered or unregistered
  ('Brand Assets')—are **proprietary assets owned exclusively by Microsoft** and its group of
  companies."* … *"**Many uses, including our logos, app and product icons, and other designs,
  will require a license first.**"*
- **The split that decides everything:** *"In general, **wordmarks** can be used to truthfully
  convey information about your product or service … However, **our logos, app and product icons,
  illustrations, photographs, videos, and designs can never be used without an express license**."*
  → the brand *name* is free to refer to; the brand *drawing* is not (same structure as Apple §2).
- Don'ts, verbatim: *"**Don't use Microsoft's logos, icons, or designs, in any manner.**"* ·
  *"Don't **alter, animate, distort, or misappropriate** Microsoft's Brand Assets, for example, by
  combining Microsoft's Brand Assets with other terms, misspellings, or incorporating them into a
  tagline or slogan."* · *"Don't use Microsoft's Brand Assets in the name of your business,
  product, service, app, **domain name**, social media account, other offering, or business
  indicator."* · *"Don't use Microsoft's Brand Assets **as nouns or verbs**."* · *"Don't use
  Microsoft's Brand Assets on any **tangible goods or packaging**."* · *"Don't file any
  application or recordation to register terms or logos identical or similar to Microsoft's Brand
  Assets…"*
- App icons: *"Microsoft's logos, designs, and icons **can never be used as your app icon** and can
  only be used in your app advertisements with a license agreement in place."* Plus: *"Without a
  license arrangement with Microsoft, **everything about your app** (including developer name, app
  name, logo, description, screenshots, and other app collateral) **must be unique to you and free
  of Microsoft's Brand Assets**. The only exception is that you may truthfully state whether your
  app is compatible or interoperable…"*
- Reservation + attribution: *"Microsoft expressly reserves the right **in its sole discretion to
  terminate, revoke, modify, or otherwise change permission** to use its Brand Assets at any
  time"*; and the required footnote *"Include a trademark footnote … '**Microsoft, (list
  additional trademarks in alphabetical order) are trademarks of the Microsoft group of
  companies**.'"*
- Per-brand guideline PDFs are separate specs: `Microsoft_logo_third_party_usage_guidance_.pdf`
  (snippet: *"As a general rule, **a formal license is required to use the Microsoft logo**, and
  its use must be pursuant to the specifications on this page"* [SEARCH-asserted]), plus Windows /
  Microsoft 365 / Edge / Bing / Surface `*_trademark_guidelines_2026.pdf` and
  `FY27_Microsft_365_Trademark_Guidelines.pdf` (the typo `Microsft` is in Microsoft's own URL —
  [VERIFIED-fetched link text]). Minimum size from the Edge doc: *"On screen, the Microsoft logo
  should **never be smaller than 72 pixels wide**. In print, it must appear at least 1 in.
  (25.4 mm) wide."* [SEARCH-asserted — WebFetch returned raw undecoded PDF bytes, so the number is
  not yet verified; parse the PDF before publishing it]

[VERIFIED-fetched] https://learn.microsoft.com/en-us/entra/identity-platform/howto-add-branding-in-apps
— **"Sign in with Microsoft branding guidelines"** (`ms.date: 2023-12-15`,
`updated_at: 2026-06-15`, authored in a public GitHub docs repo → diffable):
- *"**DON'T alter the Microsoft logo.**"* — one line, no qualification.
- Terminology is part of the brand spec: use *"work or school account"*; **don't** use "enterprise
  account", "business account", "corporate account", "Microsoft 365 ID", "Azure ID"; and *"don't
  expose end users to the Azure or Active Directory brands."*
- Documented **spec drift**: *"In an earlier version of these guidelines, we recommended using a
  '**blue badge**' pictogram. Based on user and developer feedback, **we now recommend the use of
  the Microsoft logo instead**."* → an obsolete-but-official glyph, admitted by the vendor, with a
  date attached.
- Copy rule: *"If you don't have enough space for 'Sign in with Microsoft,' **it's ok to shorten it
  to 'Sign in'**"*; light or dark scheme allowed; *"It's the association of the Microsoft logo and
  the 'Sign in with Microsoft' terms that uniquely represent Microsoft Entra ID."*
- **The real download paths (measured live, `content-type: image/svg+xml`)**, under
  `https://learn.microsoft.com/en-us/entra/identity-platform/media/howto-add-branding-in-apps/`:

| file | measured | anatomy |
|---|---|---|
| `ms-symbollockup_mssymbol_19.svg` | 200, **343 B** | `viewBox="0 0 21 21"`, **0 `<path>`** — four rects filled `#F25022 #7FBA00 #00A4EF #FFB900` |
| `ms-symbollockup_signin_dark.svg` | 200, 7,414 B | `viewBox="0 0 215 41"`, **19 paths**, fills incl. `#2f2f2f`/`#fff` + the 4 brand colors, **no `<text>`, no `font-family`** → label outlined |
| `ms-symbollockup_signin_light_short.svg` | 200, 3,083 B | same family, short "Sign in" variant |

[VERIFIED — measured bytes]

- Doctrine read [REASONED, from the two tables + §1.2]:
  1. The four-square is *trivially* hand-drawable (four rects, 343 bytes) — and that is exactly the
     trap. **Ease of redrawing is not permission to redraw**: the geometry (gap widths, optical
     alignment) and the license position are the deliverable, not the byte count.
  2. **Official button art is a fixed-size image with the string burned in** (215×41, 19 outlined
     paths). It cannot be localized, themed, or driven by `currentColor`, and it costs ~7 KB per
     locale. Google is identical in kind (180×40, text outlined). → For an i18n product the sane
     pattern is **badge-only official SVG + your own text, typography and tokens**, which is
     precisely what Google's "icon mode" and Microsoft's shortened "Sign in" allow. Vendoring the
     full button SVG for every locale is the anti-pattern.

### 4.3 X, and the "brand toolkit behind a bot wall" case

- `https://brand.x.com` → redirects to `https://about.x.com/en/who-we-are/brand-toolkit`, which
  answers **403** to a non-browser agent; `about.x.com/en/press` → **403**;
  `about.twitter.com/press` → 403 → `about.x.com/press`; `https://x.com/brand` → 200 (JS app).
  [VERIFIED-fetched: status codes only, content unreadable]
- Simple Icons records X as `hex 000000`, `source https://x.com`,
  `guidelines https://about.x.com/en/who-we-are/brand-toolkit`
  [VERIFIED-fetched from `simple-icons@16.38.0/data/simple-icons.json`] — i.e. the community index
  points at the page that agents cannot read.
- **Doctrine consequence [REASONED]:** when the policy is unfetchable, the safe default is not
  "draw something". It is (a) use the brand's own embed/SDK, (b) use **text-only**
  ("Follow us on X"), or (c) hand the download to a human with a browser and record the file, URL,
  date and terms in the repo. The retired **Twitter bird** is still served by icon CDNs (§5.2), so
  "unreachable policy + still-live stale asset" is the worst combination — and the core argument
  for *vendored, dated, provenance-tagged* files over *hotlinked* ones.
- Instagram: Meta's page states *"Anyone using Instagram's assets should **only use the logos and
  screenshots found on our Brand Resource Center site** and follow these guidelines"*, gates the
  pack (`IG_brand_asset_pack_2023.zip` — a signed expiring `scontent` URL, clickwrapped; note the
  2023 filename still current in 2026), and adds word rules: *"Don't modify, abbreviate or
  translate the word Instagram … **or use any of our logos to replace it**"*, *"Don't combine
  'Insta' or 'gram' with your own brand."*
  [VERIFIED-fetched https://www.meta.com/brand/resources/instagram/instagram-brand/]
  Its detailed gradient/icon specs sit on the linked Brand Elements page, **not fetched this
  session**, so the famous gradient stops remain unverified here (§8). The mismatch that does
  matter and is measured: Simple Icons records Instagram as a **solid** `#FF0069`
  [VERIFIED-fetched] while Meta's artwork is the multicolor gradient → the package's `hex` field is
  a single-color fallback, **not** a brand authority. [VERIFIED both sides + REASONED inference]

### 4.4 Recolor / monochrome policy matrix (the practical table)

| Brand | Monochrome or recolor the mark? | Source |
|---|---|---|
| Google — G inside the Sign-in button | **Never**: "Don't Use monochrome versions of the Google 'G' for the button"; "you can't change the size or color of the Google 'G' logo"; must be standard color on white | [VERIFIED-fetched] developers.google.com/identity/branding-guidelines |
| Google — brand hub | **Never**: "Don't combine your logo with the Google G or modify the Google G in any way, including changing the color"; full-color only, on white/black | [VERIFIED-fetched] partnermarketinghub…/how-to-show-googles-brand |
| Microsoft | **Never** — and the whole graphic tier needs a license: "can never be used without an express license"; "DON'T alter the Microsoft logo" | [VERIFIED-fetched] learn.microsoft.com + microsoft.com/…/trademarks |
| Apple | Not permitted at all without a written license; no "variation"/"takeoff"; artist's renderings forbidden | [VERIFIED-fetched] apple.com/legal/…/guidelinesfor3rdparties.html |
| Facebook | **Never**: "DON'T change the color of the logo — Do not recolor our logo to your own brand colors"; "DON'T outline the logo"; only FB-blue+white-f or white+transparent-f | [VERIFIED-fetched] meta.com/brand/resources/facebook/logo |
| GitHub | **Yes, and only within** white/black/(grey/green): "should only appear in white, black, or in few cases grey or green"; "Don't mix the color of the logo" | [VERIFIED-fetched] brand.github.com/foundations/logo |
| X | `#000000` flat mark per the redraw ecosystem; official toolkit unfetchable by agents | [VERIFIED-fetched status only] / [SEARCH-asserted] |
| Instagram | gradient primary; the icon ecosystem's `#FF0069` is a simplification, official gradient spec unread this session | [VERIFIED-fetched ecosystem data] / [gap] |

→ **Skill rule:** "monochrome icon" is a *legally different act* per brand. A design system that
paints every brand glyph with `fill="currentColor"` is compliant for GitHub and **infringing for
Google, Microsoft, Apple and Facebook**. The brand-mark component must carry a **per-brand color
policy**, not a global one. [REASONED from the table]

---

## 5. The icon-supply ecosystem, measured (2026-11-18)

### 5.1 Licenses and terms of the packages an agent actually reaches for

Measured from the npm registry (`/<pkg>/latest` metadata) and package files:

| package | version | license (machine-read) | what that does *not* cover |
|---|---|---|---|
| `lucide`, `lucide-react` | 1.75.0 | **ISC** | the *artwork*; Lucide ships **no brand marks** at all (§5.3) |
| `@heroicons/react` | 2.2.0 | **MIT** | n/a — deliberately no brand icons |
| `@phosphor-icons/web` | 2.1.2 | **MIT** | n/a |
| `@primer/octicons-react` | 19.42.0 | **MIT** | **Octicons ships GitHub's own mark**: `mark-github-16/24.svg`, `logo-github-16/24.svg`, `lockup-github-16/24.svg` (§5.3) |
| `simple-icons` | 16.38.0 | **CC0-1.0** (package.json) | CC0 covers the *file*, not the *mark* |
| Font Awesome Free | 6.x | **icons (SVG/JS): CC BY 4.0** · **fonts: SIL OFL 1.1** | attribution is owed; brand glyphs remain third-party trademarks |
| Material Symbols / Icons | – | Apache-2.0 (Google's own UI glyph system, not brand marks) | [SEARCH-asserted this session; verified in the companion vectors file] |

[VERIFIED-fetched: `https://registry.npmjs.org/<pkg>/latest`, and
`https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/LICENSE.txt` — verbatim:
*"The Font Awesome Free download is licensed under a Creative Commons Attribution 4.0
International License and applies to all icons packaged as SVG and JS file types."*]

Simple Icons' own **DISCLAIMER.md** is the clearest statement in the ecosystem of the
trademark/file split and should be quoted in the skill:
[VERIFIED-fetched https://raw.githubusercontent.com/simple-icons/simple-icons/develop/DISCLAIMER.md]
- *"Simple Icons is released under CC0 — **though that doesn't mean to imply that all icons
  within the project are also CC0.** Please see individual licenses where available."*
- *"**Simple Icons cannot be held responsible for any legal activity raised by a brand**, or users
  of the package. **We ask that our users seek the correct permissions** to use the icons relevant
  to their project."*
- *"The lack of a `guidelines` entry for a particular brand **does not imply that the brand has no
  guidelines**."* and *"users of Simple Icons are instead encouraged to **check the `source` URL**
  as, in some cases, the icon will have been sourced from official guidelines."*
- *"As licenses are subject to change we also ask our users to **regularly check** if the license
  of the icons they use have been changed."* (same wording for guidelines)
- The mechanism behind the missing slugs: *"Should a brand wish for their icon to be removed from
  the package, contact `removals at simpleicons dot org` … We generally remove icons that no
  longer meet our criteria **twice a year in our major releases**"*, and the removal PR *"must be
  submitted by the Simple Icons maintainer."*

**Coverage measured on the shipped data file** (`simple-icons@16.38.0/data/simple-icons.json`,
457,901 B, **3,472 icons**): only **843 (24%) carry a `guidelines` URL** and only **225 (6.5%)
carry `license` data**. → The ecosystem's provenance metadata is the minority case; a build that
assumes it exists will silently ship thousands of unattributed marks. [VERIFIED — measured]

**Provenance fields worth copying into a vendoring manifest** (present per icon):
`title, slug, hex, source, svg, path, guidelines, license{type,url}`. Sampled values [VERIFIED]:
`google` hex **`4285F4`** (the *retired* 2015 blue, §1.4) · `facebook` `0866FF` ·
`instagram` `FF0069` · `x` `000000` · `github` `181717` · `apple` `000000` with
`guidelines: undefined` · `google`'s and `github`'s guidelines URLs still point at
`about.google/brand-resource-center/brand-elements/` and **`https://github.com/logos`** — the URL
that now 301s (§3.1). → **Doctrine: read `source`/`guidelines`/`hex` as hints with a decay rate,
never as authority; resolve them live before relying on them.**

### 5.2 Deleted brands are still served: the versionless-CDN trap, re-measured today

Independent reproduction of the fahlwy finding (§8), with fresh numbers on 2026-11-18:

| URL | HTTP | bytes | meaning |
|---|---|---|---|
| `cdn.jsdelivr.net/npm/simple-icons/icons/openai.svg` (versionless) | **200** | 1570 | the file **does not exist** in any current release |
| `cdn.jsdelivr.net/npm/simple-icons@latest/icons/openai.svg` | **200** | 1570 | the `@latest` alias is itself stale |
| `cdn.jsdelivr.net/npm/simple-icons@16.38.0/icons/openai.svg` | **404** | 67 | the real current release |
| `…@16.38.0/icons/slack.svg` · `…/microsoft.svg` | **404 / 404** | – | same removal class (v16.0.0, v13.0.0) |
| `…@16.38.0/icons/github.svg` | 200 | 822 | present; 1 path, `viewBox 0 0 24 24` |
| versionless `…/icons/twitter.svg` | **200** | 565 | **the retired bird is still downloadable** |
| versionless `…/icons/x.svg` | 200 | 299 | the replacement mark is available too |
| Iconify snapshot `icon-sets/json/simple-icons.json` | 200 | 4.78 MB | 3,757 names, incl. `twitter`, `openai`, `microsoft`, `slack` |

[VERIFIED — measured with curl this session; the versionless body begins
`<svg role="img" viewBox="0 0 24 24" …><title>OpenAI</title><path d="M22.2819 9.8211a5.9847…`]

The same trap in a *general* icon set, which is the more surprising case [VERIFIED — measured]:

| URL | HTTP |
|---|---|
| `cdn.jsdelivr.net/npm/lucide@latest/dist/esm/icons/github.js` | **200** (588 B) |
| `cdn.jsdelivr.net/npm/lucide@1.75.0/dist/esm/icons/github.js` — and `tags.latest` **is** 1.75.0 | **404** |
| `unpkg.com/lucide@1.75.0/dist/esm/icons/github.js` | **404** |
| `raw.githubusercontent.com/lucide-icons/lucide/main/icons/github.svg` | **404** (`icons/menu.svg` = 200) |
| `cdn.jsdelivr.net/npm/lucide@0.475.0/…/github.js` | 200 · `@0.469.5` → **404** |

The current Lucide release contains **zero** files matching brand names (4,210 files, 0 hits for
`github|twitter|facebook`), yet the versionless alias hands out a deleted brand glyph, and
availability across versions is **non-monotonic** (0.469.5 → 404, 0.475.0 → 200, 1.0.1 → 404).
→ **Always pin the version resolved from `tags.latest`; never trust `@latest` or a versionless
path for an existence claim; never infer availability from a neighbouring version.**

### 5.3 "Brand mark" and "UI icon" are two different asset classes

[REASONED, grounded in §5.1–5.2 + §1–4]
- General UI sets **do not carry other companies' brand logos**. Lucide (ISC), Heroicons (MIT) and
  Phosphor (MIT) ship none: measured, `lucide@1.75.0` has 4,210 files and **0** matching
  `github|twitter|facebook`. The one interesting exception is the **vendor's own** set:
  `@primer/octicons@19.42.0/build/svg/` contains `mark-github-16.svg` (single path,
  `viewBox="0 0 16 16"`), `mark-github-24.svg`, `logo-github-16/24.svg` and
  `lockup-github-16/24.svg`, all under MIT. [VERIFIED-measured]
  → **Ranking of channels, best to worst:** (1) the brand's SDK/embed, (2) **the brand's own
  published package** — the only case where a package-managed brand glyph is legitimate, because
  the licensor and the artwork author are the same party, (3) the brand's official zip/press page,
  (4) a community redraw with recorded `source`, (5) an icon-CDN hotlink, (6) a hand-drawn path.
  An agent expecting `lucide.github` reaches for a deleted module and then *invents* one — the
  founding bug of this skill. [REASONED from measurements]
- The only aggregated brand-mark sources are Simple Icons (+ its Iconify mirror) and Font Awesome
  Brands: **community redraws under a permissive file license, sitting on third-party trademarks**
  — the two layers must be recorded separately (fahlwy's split, §8).
- Architecture consequence: a project needs **two icon pipelines, not one**. A `ui` pipeline
  (package-managed, tree-shakeable, `currentColor`, one grid grammar, license = package license)
  and a `brand` pipeline (vendored official files, per-brand color/size/clear-space policy,
  provenance = fetched URL + date + terms excerpt, **never** satisfied by a community redraw unless
  that fallback is explicitly accepted and documented).

---

## 6. Where agents go wrong with icons — failure taxonomy, each with evidence

1. **Hand-drawing the mark.** Google: *"Don't **create your own icon** for the button or use an
   outdated Google 'G'"*; Meta: *"DON'T design your own logo word mark"*, *"The logo must be
   complete and unaltered"*; Apple: no *"variation … takeoff"*, and depictions must be *"an actual
   photograph … not an artist's rendering"*; GitHub: *"No **adaptation** or use of any kind …
   without the express written permission of GitHub, Inc."*; Google brand hub: *"Don't recreate or
   modify Google's product UI."* [VERIFIED-fetched ×5]
2. **Wrong *version*, not merely wrong shape.** Google's hub: the G was *"recently redesigned"* and
   *"Don't use older versions of the Google G"*; GitHub publishes a **Deprecated logos** page with
   dated ranges; Microsoft retired its own "blue badge" pictogram; Simple Icons' `google.hex` is
   still the retired `4285F4`; the retired Twitter bird is still 200-OK on two CDNs (§5.2).
   [VERIFIED] → *"it renders and looks familiar"* is **not** a pass condition.
3. **Trusting a hotlinked or aggregated asset.** Meta, verbatim: *"Please use the link below and
   **don't download a logo from a Google search** which may be out of date or incorrect"*;
   *"**Any logos or images found elsewhere on the web are not approved for use**."*
   [VERIFIED-fetched]
4. **Borrowing the wrong brand layer.** Agents restyle a whole auth page in `#4285F4` +
   Roboto/Google Sans, which Google forbids for *your* work (*"Don't use Google's brand colors in
   your work. This includes websites and apps"*), and which also breaks the prominence rule
   (Microsoft: *"Use less prominently than your own brand or company name"*; GitHub: *"Use the
   permitted GitHub logos less prominently than your own company or product name or logo"*).
   [VERIFIED]
5. **Applying a uniform monochrome idiom to third-party marks.** `fill="currentColor"` is right for
   Lucide and infringing for Google/Microsoft/Apple/Facebook (§4.4); Meta adds *"DON'T outline the
   logo"*, which forbids the popular stroke-icon brand idiom outright. [VERIFIED]
6. **Mixing sets/styles.** Doctrine verified in the companion vectors file (Lucide's single grid /
   stroke / cap-join / minimum-gap musts). Measured here: a Microsoft official button (19 outlined
   paths, 215×41) sitting in the same row as a 24-grid stroke icon is a style collision *on top of*
   a brand-terms collision. [VERIFIED + companion]
7. **Optimizing official artwork to death.** The Google badge is mask + `foreignObject` CSS
   conic-gradient + 7 `feGaussianBlur` + Figma node ids; the Microsoft/GitHub files carry
   `clip0_730_27126`-style ids and outlined text. SVGO's default preset runs
   `removeUnknownsAndDefaults`, `cleanupIds`, `mergePaths`, `convertShapeToPath`, `convertPathData`
   (floatPrecision 3) — precisely the plugins that would flatten or break this artwork.
   → **Never run a general icon-optimization preset over brand artwork**; the Microsoft four-square
   is the only case where a lossless rewrite is technically safe, and it remains a license
   question, not a technical one. [VERIFIED-measured + companion §1.2 + REASONED]
8. **Renderer mismatch.** The Google G's color comes *only* from `foreignObject` + CSS gradient +
   filtered blobs, so any rasterizer without HTML-in-SVG support (resvg/satori OG generators,
   librsvg/`sharp`, react-native-svg) renders it empty or black. [VERIFIED-measured structure,
   REASONED consequence] → ship the PNG tier or the vendor SDK for non-browser targets.
9. **Unzip/vendor junk.** `GitHub_Logos.zip` ships `__MACOSX/._*.svg` (219 B AppleDouble) and four
   `.DS_Store` — files with an `.svg` extension that are not SVG. [VERIFIED-measured]
   → magic-byte sniff + junk-path filter before commit (fahlwy's rule, §8).
10. **Accessibility of the glyph, not just the picture.** Chrome's icons guide:
    *"Mark decorative SVGs with `aria-hidden="true"` and give the containing control its own
    accessible name"*; *"Icon-only buttons … Give the button an accessible name with `aria-label`,
    or let the icon supply one through `--icon-style-alt`; **without either, the CSS-generated icon
    is decorative**"*; standalone informative icons → `role="img"` + `aria-label`; *"all icons have
    a contrast of at least **3:1** against their backgrounds in light and dark color schemes"*;
    `<use>` content is cloned into a shadow tree so *"page CSS cannot select its elements"* — which
    is why a `<title>` inside a sprite symbol is not a reliable accessible name.
    [VERIFIED-fetched https://developer.chrome.com/docs/modern-web-guidance/guides/ui-atoms/icons]
    Brand-specific trap: for *"Sign in with Google"* the accessible name is the **sentence**, not
    the mark — `aria-label="Google logo"` or an image alt on a control is the usual agent error.
    [REASONED]

---

## 7. Delivery practice: how a vendored file should reach the screen

Distilled from [VERIFIED-fetched] Chrome **Modern Web Guidance — "Using and managing icons"**
(https://developer.chrome.com/docs/modern-web-guidance/guides/ui-atoms/icons, fetched
2026-11-18; the guide states *"These guides are authored for AI coding agents"*, and its source is
public at `GoogleChrome/modern-web-guidance-src/blob/main/guides/ui-atoms/icons/guide.md`),
plus the measured brand-asset behavior above.
**Cited-but-absent check:** `web.dev/articles/icon-fonts` and `web.dev/articles/svg-sprites` both
**404** today [VERIFIED-fetched negative], and no live web.dev page states a "pin SVG revisions in
the lockfile" rule. The brief's attribution of that guidance to web.dev is therefore
**unsupported**; the *substance* is nevertheless true and here is evidenced by §5.2's measurements
and by standard lockfile semantics. [REASONED]

- **"Icon storage and rendering are separate choices."** Pick storage (package, sprite file, inline
  symbol, data-URI token, vendored file) independently of the render path.
- **Technique table** [VERIFIED-fetched]:

| technique | use when | caveat |
|---|---|---|
| CSS icon system (`mask` + `currentColor`; `background-image` for full-color) | CSS must choose or swap the icon (component defaults, `[aria-expanded="true"]`, theming) | generated content is decorative unless given alt text |
| SVG `<use>` | reusing a symbol whose built-in styling suffices | *"Third-party icon sets rarely expose custom properties, so `<use>` against them gives you color and little else"*; **same-origin only — "cross-origin sprites fail silently"**; namespace the ids; `viewBox` must live on the `<symbol>` |
| Inline SVG | arbitrary styling/animation of the contents, **or you do not control the source** | *"If you do not control the icon, inline it"*; *"Inline the SVG the first time an icon appears on a page and reference it with `<use href="#id">` for every repeat"* |
| `<img>` + CSS filters | **avoid** | *"Filters can't reliably apply an arbitrary CSS color value to the image"* |

- **Embedded vs remote** [VERIFIED-fetched]: embedding *"avoids a request and renders with the
  first paint, but bloats CSS or HTML and cannot be cached separately"* → a handful of core icons;
  *"A sprite is one cacheable request for the whole set, but downloads every icon whether used or
  not, and `<use>` can only reference a sprite from the same origin"* → larger sets / cross-page
  reuse. → For **brand marks** the right analogue is *one committed file per mark, content-hashed
  by the build, served from your own origin*: a sprite is wrong (it drags unrelated brand artwork
  into every page cache and hides per-brand terms), and a CSS data-URI is wrong (it hides the
  artwork from diff and review). [REASONED]
- **Craft defaults worth encoding** [VERIFIED-fetched]: size from `em`-linked custom props
  (`--icon-style-size: 1em`); optical centring via
  `vertical-align: calc(0.5cap - var(--icon-style-size)/2 + var(--icon-style-voffset, -0.02em))`
  rather than `middle` (*"`middle` aligns to half the x-height, which sits visibly low for most
  icon sets"*); `flex: none` (*"Icon size is a design decision, not something layout pressure
  should negotiate"*); `pointer-events: none`; `forced-color-adjust: none` (otherwise
  forced-colors mode erases masked icons); spacing only when real text is present; ≥3:1 contrast
  in both schemes. Safari carries three live icon bugs with documented workarounds
  (webkit#301609, #320220, #325900).
- **Tree-shaking has a measured price** [VERIFIED-measured]: `lucide@1.75.0` ships 4,210 files and
  its UMD tiers sum to **10.6 MB** raw, so per-icon ESM modules or component-level imports are the
  point; a vendored `assets/brand/*` folder must be imported explicitly per component and never
  barrel-exported by glob. [VERIFIED numbers + REASONED guidance]

### 7.1 The vendoring contract (the artifact imgery should require)

For every committed brand file, keep a sidecar or manifest row recording [REASONED, assembled from
§1.1, §3.2, §4.1, §5.1, §5.2]:
1. `source_url` — the exact page fetched, **after** redirects; 2. `fetched_at` — date;
3. `guideline_excerpt` — the clause(s) that authorize *this* use (e.g. "Use the Invertocat logo as
a social button to link to your GitHub profile or project"); 4. `variant` — theme/shape/text mode
plus the reference box (Google 180×40 and 40×40, Microsoft 215×41, GitHub 98×96);
5. `rights` — `trademarked` always, plus the file license where one exists, plus attribution
obligation (Font Awesome Brands CC-BY) and any clickwrap accepted; 6. `modification: none` —
byte-identical to the vendor's, with SVGO **disabled** for that path; 7. `policy` — color or
monochrome permitted?, minimum size, clear space, may it appear alone; 8. `no_hotlink` — signed or
expiring vendor links (`X-Goog-Expires=86400`, Meta's `scontent` signatures) are never runtime
dependencies; 9. `refresh` — a scheduled re-check (annually or on brand news), because Simple Icons
asks users to "regularly check", Meta says permission *"may [be] revoke[d] … at any time"*, and
Microsoft reserves the same right.
Plus a mechanical gate: a lint rule that fails CI on any inline `<path>` whose `d` is presented as
a brand mark without a registered vendored file — "don't draw the logo" as a build error rather
than a style preference. [REASONED]

---

## 8. The fahlwy precedent, generalized into architecture doctrine

Source read this session:
`F:\Projects\Agent\skills\insource\Groups\Crawl\fahlwy\references\brand-logos.md`
(the file is fahlwy's *brand-logo cataloging* method note; the skill's `data.csv`/`log.csv` and
`scripts/brand_logos_matrix.py` are its machinery).

fahlwy's five method steps → what each becomes as doctrine for **building** UI, not just hunting
sources:

| fahlwy finding (its words) | generalizes to |
|---|---|
| *"Every provider here 404s politely, so guessing a slug produces a fake ceiling … 7/12 on bare slugs and 11/12 once you use its real `microsoft-1` / `figma-2` forms"* | **Resolve, never guess** applies to asset *paths* in code too: `assets/brand/github-invertocat.svg` must come from a fetched manifest, not a plausible name. The measurable form of this rule: *a 404 you never checked is a fake success later.* |
| *"Pull each provider's own file index, then derive slugs from it"* + `data.jsdelivr.com/v1/packages/npm/simple-icons` → `?structure=flat` | **Read the index, not the map.** In a project the index is the vendor zip/manifest, and in a repo it is `UNITS.md`/the asset folder listing. Derive names from what exists. |
| *"Rights gate, like documents. Logos are trademarks — availability proves nothing about permission. **CC0 on Simple Icons covers the file, not the mark**; Font Awesome Brands is CC BY"* | Verified verbatim this session (§5.1): Simple Icons' own disclaimer says exactly this, and the coverage numbers (24% guidelines / 6.5% license) quantify how thin the metadata is. Doctrine: **two rights fields per asset — file license and mark permission — never one.** |
| *"Grade what the bytes actually are … count `<path>` and distinct `fill=` … Multi-path/multi-fill ≈ official artwork; one 24×24 path with no fill = a community mono redraw"* | True and still useful, **but it is not a provenance test**: the official `GitHub_Invertocat_Black.svg` is a single path with one fill, structurally indistinguishable from a community redraw (§3.1). Upgraded rule: **byte-grading tells you the tier; only the fetch provenance tells you the rights.** Also added this session: count *`foreignObject`/`filter`/`mask`* too — that's what marks "official Figma-export artwork" (§1.2), which no hand redraw will ever contain. |
| Three failure modes *"a status code cannot see"*: neighbouring slug; host ≠ provider; **release ≠ release** (jsDelivr versionless 200s a file the current release deleted) | Reproduced live today with new numbers (§5.2), and extended: the same ghosting happens in **Lucide** (`@latest` serves `github.js`, 1.75.0 does not), the availability curve is **non-monotonic** across versions, and Iconify's snapshot of `simple-icons` still carries `twitter`/`openai`/`microsoft`/`slack`. Doctrine: **"200" is not evidence; a version-pinned 200 is.** |
| *"a '200' logo API that returns the same 70 B 1×1 PNG … for all 12 domains is a stub, not a catalog — hash-compare across brands"* | Generalizes to the build: **if every brand icon in your set comes from one component with a hard-coded `d`, the set is a stub.** Real brand assets differ per brand in viewBox, fill count and structure — which is why `BrandIcon` should be a folder of files, not a switch of hand-written paths. |
| *"Pin the resolved `tags.latest` into the URL before counting coverage"* + *"exits non-zero unless every source clears `--min`"* | The same discipline as a CI gate for assets: resolve → pin → verify magic bytes → fail the build on unprovenanced brand paths. §7.1 is the artifact; the *verifier*, not the *rule text*, is what makes it stick. |

And the meta-lesson that ties fahlwy to imgery's founding observation: fahlwy refuses to report a
guessed URL as a working source; imgery must refuse to render a guessed path as a logo.
**The professional act is fetching, verifying the bytes, and committing them — for assets of any
kind, documents or logos.** [REASONED, from the file + this session's confirmations]

---

## 9. Doctrine rules this research supports (the seeds for the skill)

1. **A brand mark is never drawn; it is obtained.** If the answer to "where did this glyph come
   from?" is "from the model", it is wrong by default: every brand studied forbids it in its own
   words (Google "Don't create your own icon for the button", Meta "DON'T design your own logo
   word mark", Apple "not an artist's rendering", GitHub "No adaptation … without express written
   permission", Microsoft "can never be used without an express license"). [VERIFIED ×5]
2. **Vendor ladder: SDK → official snippet → official file → text-only.** Google's own ordering is
   SDK first, HTML configurator, pre-approved assets zip, and custom button *last*; Microsoft's and
   Meta's are the same shape. "Text-only brand name" is the licensed fallback that Apple explicitly
   permits for word marks. [VERIFIED]
3. **The brand artwork carries the geometry contract.** Reference boxes measured here:
   Google 180×40 / 40×40 (r4 or pill), Microsoft 215×41, GitHub Invertocat 98×96, Meta min 16 px.
   Scale proportionally, never stretch, and let the *artwork* set the aspect ratio — the button
   around it does not get to renegotiate it. [VERIFIED-measured]
4. **`currentColor` is a per-brand decision, not a design-system default** (§4.4). A brand icon
   component that accepts `color`/`className`-driven fill for Google/Facebook/Apple/Microsoft is a
   compliance bug wearing a nice API. [VERIFIED + REASONED]
5. **A brand file is frozen bytes.** Never run SVGO/formatting/normalization over it; keep the
   vendor's filename mapping in the repo path; store the zip-derived staging separately. The Google
   badge breaks if you strip `foreignObject`/`filter`; the Microsoft/GitHub files break character if
   you round path data. [VERIFIED-measured + REASONED]
6. **Two pipelines: `ui` icons (package, tree-shakeable, one grid grammar) and `brand` marks
   (vendored, provenance-tagged, per-brand policy).** General sets provably lack brand marks
   (Lucide 1.75.0: zero brand files), so conflating them guarantees the agent invents one.
   [VERIFIED-measured]
7. **Provenance is part of the asset**: URL-after-redirect, fetch date, the authorizing clause,
   variant, rights (mark vs file), modification=none, refresh cadence (§7.1). Without it the file is
   indistinguishable from a scrape in the eyes of the next reader — the fahlwy habit applied to code.
8. **Existence claims need a pinned version.** `@latest`/versionless CDNs serve deleted files
   (openai, slack, microsoft, twitter in Simple Icons; github in Lucide) while the resolved latest
   404s; snapshot indexes lag releases. [VERIFIED-measured, reproducible]
9. **"Familiar" is not "current".** Both halves of Google's don't pair — *create your own icon* and
   *use an outdated Google "G"* — are separate defects, and the second is the one an agent will hit
   first because the 2015 palette is what its memory holds (`#4285F4`, Roboto, flat four-color G).
   Re-fetch before implementing; date the fetch. [VERIFIED]
10. **Accessibility is decided at the consumer**: decorative mark → `aria-hidden="true"` + the
    control owns the name; standalone informative → `role="img"` + `aria-label`; the *sentence*
    ("Sign in with Google") is the accessible name of the control, never "Google logo"; ≥3:1
    contrast for icons in both color schemes. [VERIFIED-fetched, Chrome Modern Web Guidance]
11. **Verify terms before assuming an aggregator is "the source"** — Meta: *"Any logos or images
    found elsewhere on the web are not approved for use."* Icon CDN availability ≠ license; a 24%-6.5%
    metadata coverage proves the ecosystem cannot vouch for you. [VERIFIED]
12. **When the vendor page is unreachable** (X's 403 bot wall, Meta's JS-only pages, gated Google
    hub, expiring signed links) the agent escalates rather than approximates: text-only or SDK now,
    a recorded human fetch, and an explicit "unresolved" note in the code/issue. Never a guess.
    [VERIFIED-fetched failures + REASONED rule]

## 10. Gaps and follow-ups

- **Instagram gradient spec** (exact stops/angle, minimum size, when single-color is allowed): the
  Meta Brand Elements pages (`/brand/resources/instagram/icons/`) are client-rendered; the fetch
  returned page framework with **no extractable guideline text**, and `/instagram-glyph/`,
  `/instagram-gradient/`, `/icons/` (en-US) all 404. → **Unverified**; obtain via browser download.
  Also unresolved: the ecosystem's solid `#FF0069` vs the official gradient (§4.3). [gap]
- **Microsoft PDF specs not parsed**: `Microsoft_logo_third_party_usage_guidance_.pdf`,
  `Microsoft_Edge_trademark_guidelines_2026.pdf` (the "72 px minimum" figure) came back as raw PDF
  bytes; needs a real PDF text extractor (the `pdf` skill / `pdfminer`) before quoting numbers. [gap]
- **Apple**: the HIG and App Review wording on imitative icons was not fetched; only the IP
  guidelines page is verified (§2). `apple.com/about/press/` / newsroom asset paths not mapped. [gap]
- **Google third-party permissions page** `google.com/intl/en/permissions/` referenced by the
  Sign-in doc, not fetched. [gap]
- **Badge-only nuance**: Google's two adjacent don'ts ("icon by itself without the button boundary
  and without text" vs "use the Google 'G' by itself for action button if needed") are reconciled
  here by inference (§1.1) — worth confirming against `signin-assets.zip`'s icon-mode variants and
  the Google Material button spec. [REASONED → verify]
- **The brief's own hallucinations**: "ONERING logo rules" (§1.3) and "lockfile-pinning SVG
  revisions per web.dev guidance" (§7, both candidate web.dev URLs 404). Useful: they are live
  specimens of the failure the skill documents — an authoritative-sounding term with no resolvable
  source. The skill's rule is to *say so* rather than code it. [VERIFIED-negative]
