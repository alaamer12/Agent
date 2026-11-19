# Time-based media: video, audio, embed facades, motion

The user-visible symptom this pillar exists for, restated as engineering:
*"the YouTube embed's play icon arrives deferred, not at first render — and
the page responds faster."* That is the **facade** pattern, and it is
documented, quantified, and tool-enforced. Video/audio decisions around it:
preload posture, poster, autoplay reality, consent gating, motion obligations.

## 1. Why a defer is not decoration — the embed cost model

Verified numbers (web.dev / developer.chrome.com, fetched):

- Popular embeds ship **>100 KB of JavaScript, sometimes up to 2 MB**, executing
  on the main thread; a failing third party can block rendering until timeout
  — **10–80 seconds**.
- An `<iframe>` is a whole HTML document with its own subresource tree; it
  often shares a process → lazy iframes improve **INP during startup**, not
  just LCP.
- Lazy-loading the YouTube embed alone saves **≈500 KB** of initial load; a
  facade costs **≈2–3 KB vs the ≈540 KB player**; Facebook Like ≈200 KiB saved;
  Instagram "over 100 KB gzipped".
- Each new origin costs DNS+TCP+TLS before a byte; `preconnect` saves 100–500 ms
  **only for origins you will certainly use** (unused connections close in ~10 s).
- The payoff asymmetry, verbatim from the docs: if the user never plays the
  video, none of its delivery cost is ever paid. The user downloads what they
  *actually* want.

## 2. The facade ladder

Definition: a static element that looks like the embed but is not functional —
taxing almost nothing at page load. Canonical interaction ladder:

1. **On page load**: render the facade (poster + play button).
2. **On mouseover** (intent): `preconnect` to the provider origins.
3. **On click** (consent): replace the facade with the real iframe/API —
   *import on interaction*.

Do not write your own: `paulirish/lite-youtube-embed` ("≈224× faster",
nocookie by default, progressive-enhancement via light-DOM `<a>`) and
`justinribeiro/lite-youtube` (2.2 KB min+gzip, `posterquality` ladder,
IntersectionObserver `autoload`, `noscript` SEO injector, IFrame-API access
via `getYTPlayer()`). Named alternatives for Vimeo (`lite-vimeo-embed`), chat
(`react-live-chat-loader`), generic (`lazyframe`). Cost note from the authors
themselves: iOS/iPadOS Safari blocks audible playback when the iframe is
created after the tap, so the component pre-creates a hidden iframe on those
devices **trading away some loading/privacy benefit** — know what you are
paying where.

**Facade is required** when all three hold: the embed is not the page's
primary content, **and** it pulls >100 KB JS or its own subresource tree,
**and** the user must interact for it to matter (video, map, chat, social,
reviews). **Direct `<iframe loading="lazy" width height>`** instead when: the
video *is* the hero content, muted autoplay loops are required (facades break
autoplay), no-JS operability must be guaranteed, or the embed is small and
already consented. SEO fence from the docs: facade only offscreen/non-primary
content, so critical content stays indexable. Cheap rungs below a full facade,
in cost order: iframe `loading="lazy"` → defer/async third-party script after
first-party → static image of the map/tweet (node-screenshot → WebP) → dynamic
image facade (Maps Static API) → plain link `target="_blank"` → removal.

## 3. Privacy and consent are separate levers

`youtube-nocookie.com` (Privacy Enhanced Mode, verbatim from YouTube Help
171780): embed views **do not influence** the viewer's YouTube experience;
ads served in it are non-personalized; enable by swapping the domain (firewall
allowlist for network admins; websites only — apps use WebView). **It is not a
no-cookie solution and not a consent substitute** — practitioner analyses of
its wording agree. The honest architecture: consent-gate the facade's
click-replace swap itself, nocookie as baseline hygiene underneath.

Third-party **thumbnail hotlinking is technically fragile and legally
undocumented**: `maxresdefault.jpg` frequently does not exist, 404s still
return a valid JPEG body (so `onerror` never fires — probe `naturalWidth` on
`onload`), only `hqdefault` is near-universal; ladder
`maxresdefault.webp → sddefault.webp → hqdefault.jpg`, prefer a server-side
fetch into your own storage. Lab-measured twist: a `.webp` rung can answer
**404 with a JPEG body** — wrong-format-on-error is the same trap wearing a
different hat, which is why the ladder decodes bytes, never trusts the
extension or the status. Read the YouTube ToS/developer-policies clause
text before treating hotlink rules as law (open item, flagged).

## 4. Video/audio element doctrine

- `preload`: **UA default varies; the spec advises `metadata`** — make it
  explicit. `auto` may download the whole file "even if the user is not
  expected to use it": reserve it for the one video that *is* the content.
- `loading="lazy"` on `<video>` defers network, poster, and autoplay until near
  viewport — and **without width/height the unloaded box is 0×0**, the gallery-
  loads-everything reflow trap. Explicit dimensions are mandatory with lazy.
- **Poster is required**: without it, nothing renders until the first frame —
  an empty box on slow networks and a blank facade surface.
- Autoplay reality: allowed only when **muted** (or silent track), after prior
  user interaction, on an allowlist (engagement-based), or via Permissions
  Policy. The markup that actually autoplays on mobile:
  `<video … autoplay playsinline muted>` — `playsinline` is *required for
  Safari*. Trap: `autoplay="false"` still enables autoplay (boolean attribute
  presence, not value) — remove the attribute itself. Feature-detect with
  `navigator.getAutoplayPolicy("mediaelement")` → `allowed / allowed-muted /
  disallowed`; on `NotAllowedError` show a real play control.
- Audio needs a gesture the same way (`pointerup → play()`, then Media Session);
  Web Audio `start()` outside an input event is autoplay-gated too (Firefox
  blocks until the tab is foregrounded). WCAG **1.4.2 (A)** is stricter than
  policy: auto audio >3 s requires a pause/stop or independent volume — and
  non-interference makes it page-wide.
- Media Session API = the native-feeling layer: metadata + artwork,
  `playbackState`, action handlers (`play/pause/seek*/nexttrack/skipad/…`),
  feature-detected with `try/catch`; lock-screen and headset keys route through
  it. Captions/transcripts (WCAG 1.2.2 A) with auto-captions **reviewed**;
  captions must not cover the subject.
- Codec control when self-hosting: multiple `<source>` children — browser takes
  the first it understands; `error` fires on the `<video>` only after all fail;
  server MIME correctness is part of the contract. Adaptive streaming is a
  separate project, budgeted as one.

The self-host / embed / embed-behind-facade tradeoff, on cost, control,
privacy, captions, monetization, and egress, is a table in the dossier — the
doctrine sentence: **self-host buys control and privacy at your bandwidth;
platform embeds buy reach and tooling at the visitor's; the facade defers the
platform's cost to the moment of intent.**

## 5. Animated vector graphics (Lottie/Rive) carry a runtime bill

Files compress (gzip the JSON; dotLottie zips json+assets), but the player is
the elephant: lottie-web ≈60–75 KB gzip, WASM engines much more (measure your
own bundle — blog numbers are folklore). Cost cliffs per the maintainers:
node count, huge shapes behind masks (inverted masks worst), `setQuality()` as
the dial. `rendererSettings: { title, description }` for a11y; export an
**SVG first-frame snapshot as poster**; `prefers-reduced-motion →
autoplay:false + pause()/freeze()` + the snapshot. Rive's "10–15× smaller than
Lottie JSON" is a vendor claim — plausible, measure on your assets. Doctrine:
choose either when animation must recolor with theme, stay crisp at any DPR,
and react (state machines); otherwise a `<video>` (or CSS) wins on cost.

## 6. Motion is a user preference, not a decoration

`prefers-reduced-motion: reduce` means the UI must **remove, reduce, or
replace** motion (scaling/panning large objects are vestibular triggers —
replace, don't only delete; WCAG 2.2.2 (A) demands pause/stop/hide for
auto-motion >5 s in parallel with other content; 2.3.3 (AAA) is interaction
motion — the practical defensible bar: *controls on autoplay, reduced-motion
handled as quality obligation, static fallback always available*: poster for
video, first frame for Lottie, none for parallax).

## 7. Native players are lazy by construction

- **AVPlayer (iOS)**: "preparing" and "loading" are separate *observable*
  async states — `status`, `timeControlStatus`, `reasonForWaitingToPlay`,
  `automaticallyWaitsToMinimizeStalling`; `preroll(atRate:)` to prime what is
  about to appear; policy knobs `networkResourcePriority`,
  `audiovisualBackgroundPlaybackPolicy`. A lazy grid observes status and
  prerolls the near-visible, never prepares all.
- **Media3/ExoPlayer (Android)**: the default is **zero network until
  `prepare()`**; preloading is an explicit, bandwidth-yielding opt-in
  (`PreloadConfiguration` for playlists, `DefaultPreloadManager` +
  `TargetPreloadStatusControl` stages for feeds) — it "does not compete with
  the ongoing playback". The mirror image of web `preload="auto"`; port the
  web numbers backwards accordingly.

## Sources

web.dev `embed-best-practices` (+ its learn module on iframes/INP),
developer.chrome.com autoplay + MEI, MDN `<video>` / Autoplay guide / Media
Session / `aspect-ratio`, YouTube Help 171780, lite-youtube-embed +
lite-youtube READMEs (incl. `youtube-thumbnail-urls.md`), bumptech Glide /
developer.android Media3 preloading blog, Apple AVPlayer docs, Lottie-web
README, WCAG 2.2 (1.4.2, 2.2.2, 2.3.3), MDN `prefers-reduced-motion`,
rive.app Lottie-alternative (vendor). Full confidence-marked dossier: workshop
research files for the imgery lane.
