# Verified free asset sources (hotlink / direct-download)

## Freshness & maintenance (read first)

- **Date format is ISO `YYYY-MM-DD`.** Every entry below carries the date it
  was last **proven** by actually fetching real bytes (magic-byte validated),
  not a date it merely "sounded plausible."
- **This file is living and append-mostly.** It is the single source of truth
  for the skill. Each time you hunt sources:
  1. verify candidates with `scripts/verify_sources.py <kind> URL...`;
  2. **add** newly-proven entries under the right category with today's date,
     and append a line to the **Growth log** at the bottom;
  3. **re-stamp** the `✅ <date>` on anything you just re-confirmed;
  4. **demote** entries that now fail (`✅` → `⚠️` if it only rate-limits,
     `⚠️`/`✅` → `❌` if dead/blocked) rather than deleting them silently —
     the ❌ graveyard is as valuable as the wins.
- **Free hosts churn on the order of weeks.** Treat anything older than ~30
  days as a hint, not a fact: re-verify before shipping it. Bulk refresh:
  ```bash
  grep -oE 'https://[^ )`]+' references/verified-urls.md | sort -u \
    | xargs python3 scripts/verify_sources.py any
  ```

**Last full re-verification: 2026-09-16.**

Legend: ✅ verified-good (dated) · ⚠️ works but transiently flaky · ❌ confirmed dead/blocked (do not propose)

## Images (30) — ✅ verified 2026-09-16

### Photos / stock / real imagery
- ✅ Lorem Picsum — `https://picsum.photos/800/1400` (also `/seed/x/…`, `?grayscale`, `/<id>/`)
- ✅ Unsplash CDN — `https://images.unsplash.com/photo-<id>?w=800&h=1400&fit=crop` (needs a real photo id)
- ✅ Pixabay CDN — `https://cdn.pixabay.com/photo/<path>/<name>_1280.jpg`
- ✅ Pexels CDN — `https://images.pexels.com/photos/<id>/pexels-photo-<id>.jpeg?auto=compress&cs=tinysrgb&w=800`
- ✅ Wikimedia Commons — `https://upload.wikimedia.org/wikipedia/commons/<h>/<hh>/<File>`
- ✅ Wikimedia by-name — `https://commons.wikimedia.org/wiki/Special:FilePath/<File>.jpg?width=800` (resolves by exact filename)
- ✅ NASA Image Library (public domain) — `https://images-assets.nasa.gov/image/<ID>/<ID>~small.jpg`
- ✅ Google sample gallery — `https://www.gstatic.com/webp/gallery/1.webp`
- ✅ wsrv.nl (image resizer/proxy) — `https://images.weserv.nl/?url=<src>&w=800&h=1400&fit=cover`
- ✅ random.imagecdn.app — `https://random.imagecdn.app/800/1400`
- ⚠️ LoremFlickr — `https://loremflickr.com/800/1400/<keyword>` (great for themed filler like `mosque`; frequent upstream 500s — verify before use)

### Random animal filler
- ✅ Cataas (cats) — `https://cataas.com/cat?width=800` (also `/cat/says/<text>`)
- ✅ PlaceBear — `https://placebear.com/800/1400`
- ✅ place.dog — `https://place.dog/800/600`
- ✅ PlaceDog.net — `https://placedog.net/800/600`

### Generated placeholders (you control size/color/text)
- ✅ dummyimage — `https://dummyimage.com/800x1400/272727/ffffff.png`
- ✅ placehold.co — `https://placehold.co/800x1400/272727/ffffff` (`/svg`,`/png`)
- ✅ placehold.jp — `https://placehold.jp/800x1400.png`

### Themed
- ✅ http.cat — `https://http.cat/200` (status-code cat images)
- ✅ http.dog — `https://http.dog/200.jpg`

### Screenshots of any URL
- ✅ thum.io — `https://image.thum.io/get/width/800/https://example.com`
- ✅ WordPress mShots — `https://s0.wp.com/mshots/v1/<urlencoded>?w=800`

### Brand / asset / icon-style images
- ✅ jsDelivr (GitHub) — `https://cdn.jsdelivr.net/gh/<owner>/<repo>@<ref>/<path>.png`
- ✅ GitHub raw — `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>.png`
- ✅ GitHub OpenGraph preview — `https://opengraph.githubassets.com/1/<owner>/<repo>`
- ✅ flagcdn — `https://flagcdn.com/w320/<cc>.png`
- ✅ Google favicons — `https://www.google.com/s2/favicons?domain=<site>&sz=128`
- ✅ GIPHY static — `https://media.giphy.com/media/<id>/giphy.gif`
- ✅ emoji CDN — `https://em-content.zobj.net/source/apple/391/<name>_<codepoint>.png`
- ✅ OpenClipart — `https://openclipart.org/image/300px/<id>`
- ✅ TheCatAPI CDN — `https://cdn2.thecatapi.com/images/<id>.jpg`

## Video (10) — distinct providers · ✅ verified 2026-09-16
- ✅ test-videos.co.uk — `https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4`
- ✅ W3Schools — `https://www.w3schools.com/html/mov_bbb.mp4` (also `movie.mp4`)
- ✅ MDN shared-assets — `https://mdn.github.io/shared-assets/videos/flower.mp4`
- ✅ MDN interactive-examples — `https://interactive-examples.mdn.mozilla.net/media/cc0-videos/flower.mp4`
- ✅ Pexels Videos — `https://videos.pexels.com/video-files/<id>/<id>-sd_640_360_25fps.mp4`
- ✅ Video.js sample — `https://vjs.zencdn.net/v/oceans.mp4`
- ✅ W3C media — `https://media.w3.org/2010/05/sintel/trailer.mp4` (⚠️ throttles under parallel load; fine on a single request)
- ✅ Internet Archive — `https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4`
- ✅ Blender Foundation — `https://download.blender.org/peach/trailer/trailer_480p.mov`
- ✅ file-samples — `https://filesamples.com/samples/video/mp4/sample_640x360.mp4`

## Audio (10) — 9 distinct providers + 1 second track · ✅ verified 2026-09-16
- ✅ SoundHelix — `https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3` (`-2` … `-10` same host)
- ✅ SoundHelix #2 — `.../SoundHelix-Song-2.mp3`
- ✅ Internet Archive — `https://archive.org/download/testmp3testfile/mpthreetest.mp3`
- ✅ Pixabay audio — `https://cdn.pixabay.com/download/audio/<date>/audio_<hash>.mp3` (path expires; re-resolve)
- ✅ Wikimedia Commons — `https://upload.wikimedia.org/wikipedia/commons/c/c8/Example.ogg`
- ✅ MDN shared-assets — `https://mdn.github.io/shared-assets/audio/t-rex-roar.mp3`
- ✅ MDN interactive-examples — `https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3`
- ✅ Google Actions sounds — `https://actions.google.com/sounds/v1/alarms/beep_short.ogg` (categories: alarms, animals, cartoon, water, …)
- ✅ file-samples — `https://filesamples.com/samples/audio/mp3/sample3.mp3`
- ✅ W3Schools — `https://www.w3schools.com/html/horse.mp3` (also `horse.ogg`)

## Avatars (15) — 10 distinct providers + 5 style endpoints · ✅ verified 2026-09-16
Distinct providers (each its own service):
- ✅ DiceBear — `https://api.dicebear.com/9.x/<style>/png?seed=<x>` (styles: adventurer, bottts, fun-emoji, icons, initials, micah, notionists, personas, pixel-art, shapes, thumbs, dylan, miniavs, lorelei, glass, big-smile, avataaars, …)
- ✅ RoboHash — `https://robohash.org/<seed>.png?size=200x200&set=set1|set2|set3|set4`
- ✅ ui-avatars — `https://ui-avatars.com/api/?name=A+B&background=3ea6ff&color=0f0f0f`
- ✅ pravatar.cc — `https://i.pravatar.cc/150?img=12`
- ✅ Gravatar — `https://www.gravatar.com/avatar/<md5>?d=<retro|identicon|monsterid|wavatar|mm>&s=150`
- ✅ randomuser.me — `https://randomuser.me/api/portraits/<men|women>/<0-99>.jpg`
- ✅ GitHub avatars — `https://avatars.githubusercontent.com/u/<userid>?v=4&s=200`
- ✅ Libravatar — `https://seccdn.libravatar.org/avatar/<md5>?s=150&d=retro`
- ✅ Avataaars — `https://avataaars.io/?avatarStyle=Circle&topType=ShortHairTheCaesar`
- ✅ Discord default avatars — `https://cdn.discordapp.com/embed/avatars/<0-4>.png`

## YouTube thumbnails (canonical shape) · ✅ verified 2026-09-16
- ✅ `https://i.ytimg.com/vi/<11-char-videoId>/hqdefault.jpg` → 200 `image/jpeg` real JPEG bytes (verified 5–35 KB). Also `mqdefault`/`sddefault`/`maxresdefault` (maxres may 404 for shorts).
- Existence + embeddability proof (no API key): `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=<id>&format=json` → 200 JSON (public+embeddable); 401 = embed disabled; 404 = missing/private. Pair every thumbnail id with an oembed 200 before shipping.

Labeled style-variants used to reach 15 assets (same underlying providers):
- ✅ DiceBear `bottts` · ✅ DiceBear `fun-emoji` · ✅ RoboHash `set3` · ✅ Gravatar `d=identicon` · ✅ Gravatar `d=monsterid`

## Illustrations (8 direct endpoints) — ✅ verified 2026-09-17
Friendly UI/UX / onboarding-style illustrations (SVG or PNG). "Direct" = hotlinkable file bytes proven by the verifier.

- ✅ Doodle Ipsum (by Blush) — `https://doodleipsum.com/700x525/flat?bg=ceebff` (PNG; styles `flat|outline|hand-drawn`; params `bg, shape, sat, blur, i=<seed>`). NOTE: `.svg` extension returns 500 — PNG only.
- ✅ Open Doodles — `https://opendoodles.s3-us-west-1.amazonaws.com/<name>.svg` (also `.png`; e.g. `jumping`, `loving`)
- ✅ Sketchvalley — `https://sketchvalley.com/uploads/svg/<slug>.svg` (site pages are `/illustration/<slug>/`; the file lives under `/uploads/svg/`)
- ✅ DiceBear illustrated-avatar styles — `https://api.dicebear.com/9.x/<style>/svg?seed=<x>` (open-peeps, lorelei, big-smile, notionists proven; also avataaars, personas, micah, dylan, miniavs)
- ✅ OpenMoji — `https://cdn.jsdelivr.net/npm/openmoji/color/svg/<HEXCODE>.svg` (e.g. `1F600`)
- ✅ Twemoji — `https://cdn.jsdelivr.net/gh/twitter/twemoji@14.0.2/assets/svg/<code>.svg` (e.g. `1f600`)
- ✅ Iconify emoji/illustration sets — `https://api.iconify.design/<set>/<name>.svg` (sets: `noto`, `fluent-emoji`, `twemoji`, `openmoji`, `avataaars` …; same API host as the icon aggregator)
- ✅ Notion Avatar Maker parts — `https://raw.githubusercontent.com/Mayandev/notion-avatar/main/public/avatar/part/<category>/<name>.svg` (categories: accessories, beard, eyebrows, eyes, face, glasses, hair, mouth, nose …)

Site-based illustration libraries (manual download; page reachable but no direct hotlink byte-verified — unDraw/Storyset/Blush/Ouch are JS apps): unDraw (undraw.co) · Storyset (storyset.com) · Humaaans (humaaans.com) · Open Peeps (openpeeps.com, CC0 — also available via the DiceBear `open-peeps` style above) · DrawKit (drawkit.com) · Blush (blush.design) · ManyPixels gallery (manypixels.co/gallery) · Icons8 Ouch! (icons8.com/ouch) · Absurd Design (absurd.design, free tier) · Fresh Folk (fresh-folk.com) · handz.design · Unblast (unblast.com) · getillustrations.com (mega-list)

## Icon sets (15 providers) — ✅ verified 2026-09-17
All via jsDelivr npm (versionless = latest) or the Iconify API; every URL returned 200 `image/svg+xml` with real SVG bytes.

- ✅ Font Awesome — `https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.7.2/svgs/solid/heart.svg` (pattern: `svgs/<solid|regular|brands>/<name>.svg`)
- ✅ Heroicons — `https://cdn.jsdelivr.net/npm/heroicons@2.2.0/24/outline/heart.svg` (`24/outline|24/solid|20/solid`)
- ✅ Lucide — `https://cdn.jsdelivr.net/npm/lucide-static/icons/heart.svg`
- ✅ Feather — `https://cdn.jsdelivr.net/npm/feather-icons/dist/icons/heart.svg`
- ✅ Tabler — `https://cdn.jsdelivr.net/npm/@tabler/icons/icons/outline/heart.svg` (also `icons/filled/`)
- ✅ Bootstrap Icons — `https://cdn.jsdelivr.net/npm/bootstrap-icons/icons/heart.svg`
- ✅ Material Design Icons — `https://cdn.jsdelivr.net/npm/@mdi/svg/svg/heart.svg`
- ✅ Ionicons — `https://cdn.jsdelivr.net/npm/ionicons/dist/svg/heart.svg`
- ✅ Phosphor — `https://cdn.jsdelivr.net/npm/@phosphor-icons/core/assets/regular/heart.svg` (`assets/<thin|light|regular|bold|fill|duotone>/`)
- ✅ Remix Icon — `https://cdn.jsdelivr.net/npm/remixicon/icons/Health%20&%20Medical/heart-line.svg` (category folders, URL-encode spaces; filenames carry `-line`/`-fill` suffixes)
- ✅ Octicons — `https://cdn.jsdelivr.net/npm/@primer/octicons/build/svg/heart-16.svg` (sized: `-16`, `-24`)
- ✅ Boxicons — `https://cdn.jsdelivr.net/npm/boxicons/svg/regular/bx-heart.svg` (`svg/regular|solid|logos/`)
- ✅ Fluent UI System Icons — `https://cdn.jsdelivr.net/npm/@fluentui/svg-icons/icons/heart_24_regular.svg` (pattern `<name>_<size>_<style>.svg`)
- ✅ Simple Icons (brand logos) — `https://cdn.jsdelivr.net/npm/simple-icons/icons/github.svg` (NOTE: cdn.simpleicons.org is ❌ 403 from sandbox — use the jsDelivr path)
- ✅ Iconify API (aggregator: 200k+ icons, 150+ sets incl. all of the above) — `https://api.iconify.design/<set>/<name>.svg` (e.g. `mdi/heart`)

## Confirmed dead / blocked from a normal sandbox — DO NOT propose · ❌ checked 2026-09-16
- ❌ PlaceKitten (`placekitten.com`) — 521 origin down
- ❌ Via Placeholder (`via.placeholder.com`) — SSL/defunct
- ❌ CSS Avatars / cssavatar.dev — DNS gone
- ❌ PlaceCage, FillMurray, Lorempixel, PlaceIMG — 404 / dead / rate-limited
- ❌ Lorem.space / cdn.lorem.space — 404 / timeout
- ❌ source.unsplash.com — retired (503)
- ❌ file-examples.com — 403 (use `filesamples.com`, a different site)
- ❌ mixkit / bensound / freesound previews — 403 or token-gated / path-specific 404
- ❌ sample-videos.com — returns an HTML page, not an mp4 (magic-byte check rejects it)
- ❌ commondatastorage.googleapis.com gtv-videos-bucket — 403 from sandbox (works in a real browser)
- ❌ download.samplelib.com, opengameart.org — network timeout from many cloud regions
- ❌ Boring Avatars (`source.boringavatars.com`) — incomplete TLS chain fails strict verification
- ❌ thispersondoesnotexist.com — returns HTML when a UA is set (no reliable direct image)
- ❌ Simple Icons CDN (`cdn.simpleicons.org`) — 403; thiscatdoesnotexist.com — TLS chain fails
- ❌ illustrations.popsy.co — TLS `CERT_ALTNAME_INVALID` from sandbox (browser may work; unusable server-side)
- ❌ error404.fun — connection timeout from sandbox (never verified)
- ⚠️ doodleipsum `.svg` endpoint — 500 server error; the PNG form works fine (see Illustrations)

## Growth log (append-only, newest first)

Record every hunt here so the next agent inherits the knowledge. One line per
dated change: `YYYY-MM-DD | ADD/UPGRADE/DOWNGRADE | category | provider — what/why`.

- 2026-09-17 | ADD | illustrations | new category — 8 direct endpoints byte-verified (Doodle Ipsum PNG-only, Open Doodles S3, Sketchvalley `/uploads/svg/`, DiceBear illustrated styles, OpenMoji, Twemoji, Iconify emoji sets, Notion Avatar parts) + 13 site-based libraries labeled (unDraw, Storyset, Humaaans, Open Peeps, DrawKit, Blush, ManyPixels, Ouch!, Absurd, Fresh Folk, handz, Unblast, getillustrations).
- 2026-09-17 | ADD | icons | new category — 15 providers verified via jsDelivr npm / Iconify API (Font Awesome, Heroicons, Lucide, Feather, Tabler, Bootstrap, MDI, Ionicons, Phosphor, Remix, Octicons, Boxicons, Fluent UI, Simple Icons, Iconify). Remix needs category folders + `-line/-fill` suffix; Simple Icons must use jsDelivr, not cdn.simpleicons.org.
- 2026-09-17 | DOWNGRADE | illustrations | illustrations.popsy.co → ❌ (TLS cert-altname invalid from sandbox); error404.fun → ❌ (timeout); doodleipsum `.svg` → ⚠️ (500; PNG form is the working endpoint).

- 2026-09-16 | ADD | images/video/audio/avatars | initial catalog compiled — 30 images, 10 videos, 10 audio, 15 avatars, all magic-byte verified in a Python sandbox.
- 2026-09-16 | DOWNGRADE | images | LoremFlickr ✅→⚠️ (persistent upstream HTTP 500); replaced its slot with Wikimedia-by-name (`Special:FilePath`).
- 2026-09-16 | NOTE | avatars | only 10 distinct avatar *providers* pass strict TLS + image bytes here; reached 15 with 5 labeled style endpoints (DiceBear/RoboHash/Gravatar variants). Boring Avatars, Multiavatar, Identicon.net, Adorable, CSS-Avatars all ❌ (broken TLS chain / 403 / dead DNS).
- 2026-09-16 | NOTE | audio | 10th distinct provider unreachable from this region (samplelib / opengameart time out; mixkit/bensound/freesound 403 or token-gated). SoundHelix #2 fills the slot but is the same host — not a new provider.
- (newest entries go above this line)
- 2026-09-16 | ADD | images (ytimg) | YouTube-thumbnail canonical shape proven for 17 real public+embeddable Islamic shorts via oembed=200 AND i.ytimg hqdefault.jpg=200 image/jpeg real JPEG; recorded oembed proof method.
- 2026-09-16 | ADD | avatars | re-confirmed 6 avatar providers for dev-seed channel avatars (ui-avatars, dicebear, pravatar, robohash, randomuser, gravatar-identicon), all 200 + real image bytes.
