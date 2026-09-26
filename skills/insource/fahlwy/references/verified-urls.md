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

### Kyoto / Japan travel photo set — ✅ verified 2026-09-20 (12/12, HTTP 200 + `image/jpeg`)

Real photographs, keyless, hotlinkable, resolved through the Commons search API
(`action=query&list=search&srnamespace=6` → `prop=imageinfo`) so no filename is a
guess. All at `?width=1280`. Note the width ladder: 640≈800 (176 KB) and
1000≈1280 (291 KB) return identical bytes, so **request 1280 — the extra width is
free**. Measured 291–751 KB, mean 431 KB, 5.1 MB if a single page loads all twelve.

```
https://commons.wikimedia.org/wiki/Special:FilePath/Kyoto01.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/20181110%20Fushimi%20Inari%20Torii%2012.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Momiji%20in%20Ginkaku-ji.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/2021%20Sagano%20Bamboo%20forest%20in%20Arashiyama%2C%20Kyoto%2C%20Japan.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Gion%20Streets%2C%20Kyoto%2C%202024.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Kaiseki%20-%20Kyoto.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Interior%20of%20a%20ryokan%20room%20%282999708441%29.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/020%20N700%20Series%20Shinkansen%20%E6%96%B0%E5%B9%B9%E7%B7%9A%20arriving%20at%20Kyoto%20Station%2C%20Japan.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Yasaka-dori%20early%20morning%20with%20street%20lanterns%20and%20the%20Tower%20of%20Yasaka%20%28Hokan-ji%20Temple%29%2C%20Kyoto%2C%20Japan.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Shariden%2C%20Kinkaku-ji%2C%20Kyoto%2C%20East%20View%2020130811%201.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Cherry%20blossoms%20and%20Five-storied%20Pagoda%2C%20Daigo-ji%20temple%2C%20Kyoto%20-%20Mar%2027%2C%202009.jpg?width=1280
https://commons.wikimedia.org/wiki/Special:FilePath/Kyoto%20Ryoanji.jpg?width=1280
```

Slots: temple · torii · autumn(maple) · bamboo · street · food · ryokan · train · lantern · pavilion · pagoda · garden.

**Two traps this hunt exposed, both invisible to a status code:**
1. **A 200 + valid JPEG is not the right picture.** Searching "paper lantern"
   returned *Lantern festival in Odaiba* (Tokyo) and "Yasaka pagoda" returned
   *Hōkan-ji, Higashiosaka* — wrong city, still a passing asset. Read the returned
   **filename** for the place name, or the subject is silently wrong.
2. **Default `curl` UA is refused by Wikimedia's UA policy** — it answers a ~2 KB
   HTML body, which looks like a broken/tiny image. The same URL returns the real
   300–750 KB JPEG with a browser `User-Agent`. Always re-probe with `-A` before
   calling a Wikimedia URL broken.

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
- ✅ Simple Icons (brand logos) — `https://cdn.jsdelivr.net/npm/simple-icons/icons/github.svg` (the **brand-logo category below** is the authority for this provider; `cdn.simpleicons.org` plain form is still ❌ 403 — use the jsDelivr path)
- ✅ Iconify API (aggregator: 200k+ icons, 150+ sets incl. all of the above) — `https://api.iconify.design/<set>/<name>.svg` (e.g. `mdi/heart`)

## Documents / PDF books (16 open-license full texts) — ✅ verified 2026-09-21

**Only documents the rights holder itself released.** Every URL below is a
full-text book whose author/publisher publishes it free (CC BY / CC BY-NC-SA /
GFDL / BSD / public domain, or an official MIT Press / Stanford / UPenn release).
Commercial titles (Clean Code, Code Complete, Refactoring, CLRS, K&R, DDIA, …)
have **no** legal free full-text PDF — a "working" copy of those is by
definition an infringing upload, so it never belongs in this catalog. See the
license gate in the Growth log.

### Author/publisher-hosted full texts (direct file, no login)
- ✅ Think Python 2e — `https://greenteapress.com/thinkpython2/thinkpython2.pdf` (0.9 MB, 244 pp)
- ✅ Think Bayes — `https://greenteapress.com/thinkbayes/thinkbayes.pdf` (2.5 MB, 210 pp)
- ✅ Think OS — `https://greenteapress.com/thinkos/thinkos.pdf` (0.4 MB)
- ✅ The Little Book of Semaphores 2e — `https://greenteapress.com/semaphores/LittleBookOfSemaphores.pdf` (1.2 MB, 291 pp)
- ✅ SICP — `https://web.mit.edu/6.001/6.037/sicp.pdf` (7.4 MB, 883 pp; MIT Press free full text)
- ✅ Eloquent JavaScript 3e — `https://eloquentjavascript.net/Eloquent_JavaScript.pdf` (2.0 MB, 463 pp; also `…_small.pdf` print-optimised)
- ✅ Open Data Structures (Java/C++/Python) — `http://opendatastructures.org/ods-java.pdf` (1.5 MB, 334 pp; CC BY; swap `-java`/`-cpp`/`-python`)
- ✅ Mining of Massive Datasets — `http://infolab.stanford.edu/~ullman/mmds/book.pdf` (3.0 MB, 513 pp; Stanford-hosted)
- ✅ Gaussian Processes for Machine Learning — `https://gaussianprocess.org/gpml/chapters/RW.pdf` (4.1 MB, 266 pp; MIT Press free)
- ✅ Introduction to Probability (Grinstead & Snell) — `https://math.dartmouth.edu/~prob/prob/prob.pdf` (3.0 MB, 518 pp)
- ✅ Reinforcement Learning: An Introduction 2e — `http://incompleteideas.net/book/RLbook2020.pdf` (73.1 MB, 548 pp; MIT Press free — HEAD-check the size first)
- ✅ Dive into Deep Learning — `https://d2l.ai/d2l-en.pdf` (44.7 MB, 1151 pp, CC BY-NC-SA)
- ✅ Advanced Bash-Scripting Guide — `https://www.tldp.org/LDP/abs/abs-guide.pdf` (2.7 MB, 916 pp, GFDL)
- ✅ GNU Emacs Manual — `https://www.gnu.org/software/emacs/manual/pdf/emacs.pdf` (3.1 MB, GFDL; pattern `/software/<pkg>/manual/pdf/<pkg>.pdf`)
- ✅ PostgreSQL 17 docs — `https://www.postgresql.org/files/documentation/pdf/17/postgresql-17-A4.pdf` (15.5 MB; pattern `/files/documentation/pdf/<major>/postgresql-<major>-A4.pdf`)
- ✅ Common Lisp: A Gentle Introduction — `https://www.cs.cmu.edu/~dst/LispBook/book.pdf` (1.1 MB, 587 pp; author-released)

### GitHub-hosted (walk the tree, check the license — see Growth log)
- ✅ Pro Git 2e (CC BY-NC-SA 4.0) — `https://github.com/progit/progit2/releases/download/<tag>/progit.pdf` → latest tag from `/repos/progit/progit2/releases`; `2.1.450` = 18.8 MB, 501 pp. Release assets 302 to a signed bucket that **rejects suffix `Range: bytes=-N`** (501) — use explicit `bytes=<lo>-<hi>`.
- ✅ radare2 Book — `https://github.com/radareorg/radare2-book/releases/download/6.0.0/r2book.pdf` (7.8 MB, 297 pp)
- ✅ Learn Python (open book) — `https://raw.githubusercontent.com/animator/learn-python/main/pdf/learn-python-v2022.10.pdf` (2.8 MB, 149 pp)
- ✅ The Holy Book of x86 vol.2 — `https://raw.githubusercontent.com/Captainarash/The_Holy_Book_of_X86/master/book-vol-2.pdf` (3.3 MB, 56 pp)
- ✅ Programming Language Foundations in Agda (CC BY) — `https://archive.org/download/plfa_epub_announced_2021_0824/plfa.pdf` (9.9 MB, 516 pp) or the repo's `dev/papers/scp/PLFA.pdf`
- ✅ Functional Programming in Lean (CC BY) — `https://archive.org/download/functional-programming-in-lean-may-2023/Functional_Programming_in_Lean.pdf` (2.2 MB, 462 pp)

### Chapter-family sources (many PDFs from one pattern)
- ✅ OSTEP chapter set — `https://pages.cs.wisc.edu/~remzi/OSTEP/<topic>-<chapter>.pdf` (e.g. `cpu-sched.pdf`, 13 pp). ⚠️ There is **no** single full-book PDF here — the free release is per-chapter; `ostep-3rd-edition-v0.9.pdf` is 404.
- ✅ Security Engineering vol. bundle check — `https://www.cl.cam.ac.uk/~rja14/Papers/SE-0<n>.pdf` are 12–21 pp **papers/reviews, not the book**; grep the page before claiming a volume.

## Brand logos (official marks) — 13 of 21 sources clear 10/12 · ✅ verified 2026-09-21

Reproduce every number below with `python3 scripts/brand_logos_matrix.py`
(`--json` for the full matrix, `--min`, `-p`/`-b` to slice). It resolves each
provider's own slug index and pins versions before fetching, so its counts are
stricter — and more honest — than hand-probing.

Every entry below was proven by fetching bytes (magic class + size, and for PNG
the IHDR dimensions), across a fixed 12-brand matrix: github, youtube, google,
microsoft, figma, slack, docker, spotify, netflix, vercel, **windsurf**, openai.
`PASS n/12` = how many of those twelve the source really serves. Rights note for
the whole category: **brand logos are trademarks** — hotlinkability grants
nothing; usage is governed by each brand's own brand/press guidelines.

⚠️ **A sub-10/12 score is not "bad source"** — Simple Icons (9/12) is the only
reliable home for young brands, and LobeHub (7/12) is the only real PNG tier.
The matrix is consumer-heavy on purpose; re-run with `-b cursor,codeium,ollama,
huggingface,notion,anthropic,stripe,supabase,react,twitch,whatsapp,instagram`
to see the AI-era ranking flip.

**Resolving slugs — the one rule that decided every result:** never guess a
filename. Each source's real names come from its own index:
`https://data.jsdelivr.com/v1/packages/npm/<pkg>@<ver>?structure=flat` (npm;
resolve `tags.latest` from the unversioned URL first — the unversioned form
returns metadata, not files), `.../packages/gh/<owner>/<repo>@<ref>?structure=flat`
(GitHub without the rate-limited API), `https://api.iconify.design/<set>.json`
and `cdn.jsdelivr.net/gh/iconify/icon-sets/json/<set>.json` (Iconify sets),
`commons.wikimedia.org/w/api.php?list=allimages&aiprefix=<Brand>%20logo`
(Commons), and LobeHub's nested (not flat) package tree.

### Curated vector datasets (SVG)
- ✅ **Simple Icons** (CC0, mono `currentColor`) — **pin the release**: `https://cdn.jsdelivr.net/npm/simple-icons@<ver>/icons/<slug>.svg` (latest 16.32.0) — **9/12** on the fixed matrix: `microsoft` was removed at v13.0.0 and `slack` + `openai` at v16.0.0, so 3 of the twelve can never come from a current release. ⚠️ **The versionless URL lies**: `.../npm/simple-icons/icons/openai.svg` answers **200 with 1570 B** (bytes from ≤v15) while `@16.32.0` 404s the same path — jsDelivr's versionless path serves a stale cached release and will happily return files the current one deleted. Hand-probing it produced a false 12/12; always pin. Still the strongest young-brand coverage (windsurf 813 B, cursor, codeium, ollama), and 3461 marks overall. Second host `https://simpleicons.org/icons/<slug>.svg` is a **partial/older build** (windsurf ✅, openai ❌, microsoft ❌).
- ✅ **SVG Logos / gilbarbara** (official artwork, COLOUR) — `https://raw.githubusercontent.com/gilbarbara/logos/main/logos/<slug>.svg` (mirror `https://cdn.jsdelivr.net/gh/gilbarbara/logos@main/logos/<slug>.svg`) — **11/12** (only windsurf absent), 1839 files, multi-path/multi-fill (google 6 paths/4 fills). Highest coverage of legacy+AI brands in one repo. `github.svg` is the 512×139 wide lockup — use `github-octocat.svg` for the mark; 424 `-icon.svg` variants exist.
- ✅ **VectorLogo.zone** (press-kit-derived official vectors) — `https://www.vectorlogo.zone/logos/<slug>/<slug>-icon.svg` (also `-ar21`, `-tile`, `-wordmark`, `-horizontal`; availability varies) — **10/12**; richest path counts (github 14 paths, docker 12, slack 8). ⚠️ Library **froze ~2021**: no windsurf/openai/notion (submissions sit in `upload.vectorlogo.zone/logos/<slug>/pending.json`); most files have **no `viewBox`** (width/height + transform only); `cdn.vectorlogo.zone` is NXDOMAIN from sandbox — use `www`.
- ✅ **WorldVectorLogo** — `https://cdn.worldvectorlogo.com/logos/<slug>.svg` — **11/12** *with correct slugs* (bare-slug probing scores only 7/12: microsoft**-1**, figma**-2**, spotify**-2**, netflix**-1**; both bare and suffixed forms occur). Needs a **non-empty UA** (blank = 403; curl/8.5.0 accepted). The slug index (`/sitemap.xml`) is Cloudflare-challenge-gated with no Wayback copy ⇒ slugs must be suffix-enumerated against the CDN.
- ✅ **logotypes.dev — via its GitHub repo only** — `https://raw.githubusercontent.com/yceballost/logotypes/main/static/logos/<brand>-<glyph|wordmark>-<color|black|white>.svg` — **10/12**, 648 files, colour + black/white tiers. ⚠️ Community redraws (20-star repo), and the hosted API is dead: every `logotypes.dev` path returns **402 `DEPLOYMENT_DISABLED`** ⇒ never cite the domain.
- ✅ **Iconify → `thesvg-color`** (unique upstream, COLOUR official-style) — `https://api.iconify.design/thesvg-color/<name>.svg` — **12/12**, but the bare brand name 404s for a third of the matrix: this set is **theme-suffixed**, use `<brand>-dark` / `<brand>-light` (github-dark 985 B, windsurf-light 928 B, openai-dark 1634 B, vercel-dark 141 B). Multi-path with real fills (google 10 paths, figma 6).
- ✅ **LobeHub Icons** (best young-brand coverage, and a **real PNG tier**) — SVG `https://cdn.jsdelivr.net/npm/@lobehub/icons-static-svg@<ver>/icons/<slug>.svg` (+ `<slug>-color.svg` where published) — **7/12** on the consumer matrix but **14/14** on a dev/AI-weighted one (windsurf, cursor, huggingface, ollama, aws, apple all present); PNG `https://cdn.jsdelivr.net/npm/@lobehub/icons-static-png@<ver>/{light,dark}/<slug>.png` → proven **640×640 `image/png`** 6822 B. ⚠️ Its 950-icon set is AI/dev-scoped: youtube/slack/docker/spotify/netflix/whatsapp/instagram/stripe/react are **not in the index at all**. Read the **nested** package tree — `?structure=flat` returns 0 files for this package.
- ✅ **Wikimedia Commons** (2-call recipe, no hand-copied filename) — resolve `https://commons.wikimedia.org/w/api.php?action=query&format=json&list=allimages&aiprefix=<Brand>%20logo&ailimit=30` → then serve `https://upload.wikimedia.org/wikipedia/commons/<h>/<hh>/<File>` or `https://commons.wikimedia.org/wiki/Special:FilePath/<File>` — **11/12** core (17/18 incl. backfills), SVG for 16/17. ⚠️ Three traps: files are often **historical revisions** (google 2010-13, github 2013, stripe 2014); Slack's "SVG" is a wrapper around a **20×20 raster**; and a word-boundary title test is mandatory — searching "windsurf" returns *windsurfing-sport* map icons that are 100 % valid bytes and 100 % the wrong brand.
- ⚠️ **Devicon** (dev-tool brands only, COLOUR official) — `https://cdn.jsdelivr.net/npm/devicon/icons/<slug>/<slug>-original.svg` (fallback `-plain.svg`) — **6/12** of the consumer matrix (576 folders, none social/streaming) but the best fidelity when the brand IS a dev tool (docker 16 paths/9 fills). Counts for a dev-logo need, not a general brand wall. Filter `.eps` siblings.
- ⚠️ **Font Awesome Brands** — `https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free/svgs/brands/<slug>.svg` — **9/12**; no netflix/vercel/windsurf/supabase (Pro-only). ⚠️ **CC BY 4.0 = attribution required**, and versionless resolves to v7 (viewBox now 512², some icons renamed `*-square` → `square-*`) — pin `@6.7.2` if names must hold.
- ⚠️ **Boxicons Logos** — `https://cdn.jsdelivr.net/npm/boxicons/svg/logos/bxl-<slug>.svg` — **8/12**; 2.1.4 is the last release ever, so coverage is 2020-era (no windsurf/openai/vercel/notion/supabase).

### Icon-set brands via npm (mono glyphs — recognisable, NOT official artwork)
- ✅ **Remix Icon Logos** — `https://cdn.jsdelivr.net/npm/remixicon/icons/Logos/<slug>-fill.svg` (also `-line`) — **10/12**; the `-fill`/`-line` suffix is mandatory (bare slug 404s); folder is capital-L `Logos`.
- ✅ **Tabler Brand** — `https://cdn.jsdelivr.net/npm/@tabler/icons/icons/outline/brand-<slug>.svg` — **10/12**; real folder is `icons/outline/` and every filename is prefixed `brand-`; stroke art, lowest logo fidelity of the counting set; microsoft exists only as `brand-windows` (different mark).
- ✅ **Iconify → `cib` (CoreUI brands)** — `https://api.iconify.design/cib/<slug>.svg` — **9/12**, viewBox 0 0 32 32 mono.
- ✅ **Iconify → `simple-icons`, `logos`, `bxl`, `fa7-brands`, `ri`, `tabler`, `ion`, `bi`, `devicon`, `arcticons`, `streamline-logos`, `hugeicons`, `lineicons`, `proicons`, `ant-design`, `meteor-icons`, `skill-icons`, `pixel`, `fontisto`** — `https://api.iconify.design/<set>/<name>.svg` — same 12-brand matrix as the npm/own-site rows above; **`simple-icons` scores 12/12 here vs 9/12 on the pinned npm release, because Iconify serves a frozen snapshot (3734 icon names vs the package's 3461) that still carries the microsoft/slack/openai marks upstream Simple Icons deleted** — useful if you want those marks as mono glyphs, but it is a stale copy, not a live provider; `logos` 15/18-hard, `bxl` 15/18, `arcticons` 12/18, `ri` 12/18, fa/cib/tabler ~9-11/12. **These are copies of upstreams already listed — count the UPSTREAM once.** Genuinely Iconify-only upstreams worth a slot: `thesvg-color` (above), `arcticons`, `streamline-logos`, `cib`, `ant-design`, `hugeicons`, `lineicons`, `meteor-icons`, `proicons`, `pixel`, `skill-icons`.

### Raster brand marks by domain (keyless runtime lookup, PNG/ICO)
- ✅ **Google Favicons** — `https://www.google.com/s2/favicons?domain=<domain>&sz=256` — **12/12**, PNG, up to 256×256 (figma 1906 B 256×256, windsurf.com 1868 B 256×256). ⚠️ The `sz=` ladder is **non-monotonic**: `sz=144/192/384/512` regress to a 16×16 stub — ask **256**. 301s to `t0–t3.gstatic.com` (the `faviconV2` form is directly hotlinkable; the shard rotates). No SVG.
- ✅ **Icon Horse** — `https://icon.horse/icon/<domain>` — **12/12**, best keyless raster (github 26199 B 256×256; ICOs passed through for docker/openai). ⚠️ **403 with no User-Agent**; `?size=256` is a no-op.
- ✅ **DuckDuckGo Icons** — `https://icons.duckduckgo.com/ip3/<domain>.ico` — **12/12**, stable same-host (no redirect). The `.png` extension 404s on all 12; the ICO packs several sizes (microsoft up to 128×128) — parse the directory, `Content-Length` understates it.
- ⚠️ **unavatar.io** — `https://unavatar.io/<domain>?fallback=false` — **12/12** but only with **~6 s spacing** (429s at 1 req/1.5 s; 2/12 failed even on a spaced pass). The **only keyless provider here that serves vector** (figma SVG 5 paths, openai/vercel/spotify SVG). ⚠️ `?fallback=false` is **mandatory** — the default route 200s a generic stub SVG for a miss (proven: identical hash for a live and a dead domain).
- ⚠️ **Yandex Favicon** — `https://favicon.yandex.net/favicon/<domain>` — 12/12 bytes but **16×16 only**; `?size=64/256` → 400; unknown domains 200 a **1×1 PNG** ⇒ reject by dimension, not status. Fallback tier only.
- ⚠️ **wsrv.nl as a favicon upscaler** — `https://wsrv.nl/?url=https%3A%2F%2F<domain>%2Ffavicon.ico&output=png&w=512&h=512` — 11/12, any size asked (1024 proven, 585 KB) but it **resamples** the source icon, so a 16×16 mark becomes a blurry 512. Format/size control, not resolution.

### Per-brand official hosts (no cross-brand template ⇒ never a "source")
Harvest the URL out of the brand's own HTML/`og:image`; do not invent a path.
Proven 18/19 files: `github.githubassets.com/favicons/favicon.svg`,
`windsurf.com/favicon.svg` (1344 B, 1024×1024 viewBox — the **only** current
Windsurf vector anywhere outside `thesvg-color`/LobeHub),
`static.figma.com/app/icon/2/favicon.svg`,
`www.gstatic.com/images/branding/product/<1x|2x>/<product>_<n>dp.png`
(18 Google products, one template, 96×96 — Google-family only),
`assets.nflxext.com/.../nficon2016.png`, `a.slack-edge.com` media kit,
`assets.vercel.com/image/upload/.../apple-touch-icon-180x180.png`.
Dead ends: openai.com + help.openai.com 403 (Cloudflare), microsoft.com exposes
no stable logo file, `www.youtube.com/s/desktop/<buildhash>/img/…` churns.

### Windsurf (and AI-era brands) coverage — the answer that decides the pick
`windsurf` exists in **only four** of the 15 sources: **Simple Icons** (mono),
**Iconify `thesvg-color`** (`windsurf-dark`/`windsurf-light`, colour),
**LobeHub Icons** (mono SVG + 640² PNG), and its own **`windsurf.com/favicon.svg`**
— plus the domain-keyed raster APIs (Google s2 at 256², Icon Horse, DDG, unavatar).
Absent from gilbarbara, VectorLogo.zone, WorldVectorLogo, logotypes, Devicon,
Font Awesome, Boxicons, Tabler, Remix, CoreUI, and Commons. General rule:
**legacy icon fonts (FA, CoreUI, Tabler, Remix, Boxicons) fail every AI-era tool**
— for cursor/codeium/ollama/huggingface/windsurf use Simple Icons + `thesvg-color`
+ LobeHub. Also note `windsurf.art` is not a live host; `codeium.com` 301s to
`windsurf.com`, which now 308s to `devin.ai/desktop` — all three share one icon
set, so they are ONE brand slot.

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

### Documents/PDF failures — ❌ checked 2026-09-21
- ❌ `www.catb.org` (ESR writings: TAoUP, Art of the Command Line) — TLS chain/altname fails strict verification, and plain HTTP 404s the `.pdf`. Unusable server-side.
- ❌ `paulgraham.com/<book>.pdf` (oisp/acns/hap) — answers **200 with `<html>`**, a fake success; magic-byte check rejects it.
- ❌ `en.wikibooks.org/wiki/Special:DownloadAsPdf?page=X` — returns HTML, not a PDF.
- ❌ `hal.inria.fr/hal-<id>/document` — HTML landing page; the file itself needs the record API's `/file/…pdf`.
- ❌ DNS does not resolve from this sandbox (re-check elsewhere before trusting): `learnyouahaskell.com`, `icce.rug.nl` (C++ Annotations), `c2rw.net` (compiler book), `network-theory.co.uk` (GCC/GNU Make intros), `diveinto.org`.
- ❌ `www.gnu.org/software/*/manual/*.pdf` guessed paths — "Network is unreachable" (v6 route); the real form is `/manual/pdf/<pkg>.pdf`, proven for emacs only.
- ❌ Single-PDF guesses that simply do not exist: `mitp-content-server…/book.pdf`, `…/OSTEP/ostep-3rd-edition-v0.9.pdf`, `debian-handbook.info/download/stable/…`, `docs.python.org/3/python3.pdf`, `hastie.su.domains/ISLR2/…`, `softwarefoundations…/LogicalFoundations.pdf`, `automatetheboringstuff.com/2e/…pdf`, `inventwithpython.com/…pdf`, `cs.yale.edu/…/concrete-*.pdf`. **Fix that beat all the guessing: harvest the landing page's own `href`s** — most of these publishers release HTML or per-chapter PDFs only, so a guessed filename is the wrong tool.
- 🚫 Not catalog material at all: Archive **lending-library** items (`access-restricted-item:true`), `/Encrypt`-ed PDFs, and repos that are dumps of in-copyright commercial books. A CC `LICENSE` file in a repo does **not** prove it holds the rights — `Vonng/ddia` and `doocs/technical-books` are CC-licensed repos carrying a translation/aggregation of copyrighted works. Read the copyright page inside the PDF, not just the repo license.

### Brand-logo failures — ❌ checked 2026-09-21
- ❌ `logo.clearbit.com` — **DNS-dead**: the name exists but returns no A/AAAA/CNAME (DoH NOERROR + empty answer) while clearbit.com itself resolves. HubSpot retired it. 0/12. Same class: `favicons.bitwarden.net` (no A record).
- ❌ `img.logo.dev/<domain>` — token-gated: keyless **401 `application/json`** on 12/12, including `?format=svg`. No keyless tier.
- ❌ `cdn.brandfetch.io/<domain>` (+ `/w/512/h/512`, `/format/svg`) — keyless 302→308 to `docs.brandfetch.com`, then **200 text/html 434 668 B byte-identical for all 12** ⇒ needs `?c=CLIENT_ID`. A classic 200-HTML fake.
- ❌ `api.faviconkit.com/<domain>/256` — **alive but lying**: 200 `image/png`, 70 B, **1×1**, same hash for 12/12, redirects to raw.githubusercontent. No logo data.
- ❌ `favicons.githubusercontent.com/<domain>` — 500 on 12/12 (internal-only service, no keyless path).
- ❌ `logotypes.dev` hosted API — 402 `DEPLOYMENT_DISABLED` on every path/UA combo; only the GitHub repo is alive.
- ❌ `cdn.vectorlogo.zone` — NXDOMAIN from sandbox; `www.vectorlogo.zone` works.
- ❌ besticon (`besticon-demo.herokuapp.com` 503 on 12/12; `besticon.dev` NXDOMAIN) · favicon.io (no domain route: 404 HTML on `/<d>` and `/favicon-provider/w/128/<d>`) · IconScout `api.iconscout.com` 500 JSON (token) · `logodb.io` + `api.logodb.io` NXDOMAIN · `logo.ly` unresolvable · `cravatar.com/favicon/api` (only ~7 real: 3 brands share one 32×32 stub hash, 504s on others).
- ❌ Not brand-logo libraries at all: **Pro Icons / Superdev** (`proicons.dev` NXDOMAIN, `proicons.superdev.sh` TLS handshake fail, npm `pro-icons` / `@superdevpro/icons` / `@superdev-pro/icons` all 404) · **Circumicons** (SPA HTML; `/api/icons/github` and `/github.svg` 404; npm 404) · **arconia** (a web-components docs site) · npm `brandicons@2.0.0` (36 stale 2017-era Material glyphs — and not the "BrandIcons" people mean today) · `world-vector-logos` / `logotypes` / `brand-icons-default` npm packages (404 — do not assume an npm twin exists).
- ❌ `iconify-design/modern-icon-pack` — repo does not exist (GitHub 404; `cdn.jsdelivr.net/gh/iconify-design/modern-icon-pack@latest/svg/...` 404). Iconify serves per-icon SVG **only** through `api.iconify.design` — there is no file tree, and `cdn.jsdelivr.net/npm/@iconify/json@latest/json/logos.json` 403s (package too large).
- ⚠️ Iconify API throttling + traps: **icon names are set-prefix-stripped** — `cib/github.svg` and `bxl/github.svg` are 200, `cib/cib-github.svg` and `bxl/bxl-github.svg` are **404** (the font-family's own `bxl-`/`cib-` prefix is not repeated inside the set; resolve names from `icon-sets/json/<set>.json`, never by prefixing); `/collections.json` answers **200 with the body `404`**; `<set>.json?icons=<missing>` answers **200 with `"notFound"`** (200 ≠ exists); `?color=ff0000` without `%23` emits invalid `fill="ff0000"`; `?format=png` silently returns SVG (there is **no** server-side PNG route); concurrency 3 × 0.12 s tripped 429 on ~80 % of requests with a penalty outlasting 45 s — **~2.5 s/request completed 452 URLs with zero 429**.

## Growth log (append-only, newest first)

Record every hunt here so the next agent inherits the knowledge. One line per
dated change: `YYYY-MM-DD | ADD/UPGRADE/DOWNGRADE | category | provider — what/why`.

- 2026-09-21 | ADD | brand-logos | new category — **15 sources** of official brand marks byte-proven against a fixed 12-brand matrix (incl. windsurf): 8 curated vector datasets (Simple Icons 12/12, gilbarbara 11/12, VectorLogo.zone 10/12, WorldVectorLogo 11/12, logotypes-repo 10/12, Iconify `thesvg-color` 12/12, LobeHub 14/14 + only real PNG tier 640², Wikimedia Commons 11/12 via a 2-call API recipe), 4 mono-glyph sets (Remix 10/12, Tabler 10/12, FA Brands 9/12 *attribution-required*, Boxicons 8/12 *frozen 2020*), 6 domain-keyed raster APIs (Google s2 12/12@256², Icon Horse 12/12, DDG 12/12, unavatar 12/12 *with 6 s spacing*, Yandex 16×16-only, wsrv.nl upscale). Plus 19 Iconify sets mapped to their real upstreams. Highest-value method: **resolve every slug from the provider's own index** (jsDelivr `?structure=flat`, `icon-sets/json/<set>.json`, Commons `list=allimages`) — guessing filenames cost a full run. Key finding: **Windsurf exists in only 4 of 15 sources** (Simple Icons, `thesvg-color`, LobeHub, its own favicon.svg) and legacy icon fonts fail every AI-era brand.
- 2026-09-21 | NOTE | scripts | `verify_sources.py image` has a **flat >256 B floor that false-fails valid brand SVGs** — it rejected Simple Icons `vercel` (132 B), Remix `microsoft` (230 B), `logotypes` `vercel-glyph-color` (155 B), MDI `netflix` (221 B) and VLZ `vercel-icon` (138 B), all of which are real `image/svg+xml` 200 marks. Use the `any` kind (or cite the larger `-ar21`/wordmark form) for icon-scale vectors; the floor makes sense for rasters only. Also: magic-sniffing must tolerate a **UTF-8 BOM + CRLF** (an Instagram mark on Commons starts with a BOM, so a naive `<?xml` offset-0 check fails it).
- 2026-09-21 | ADD | scripts | `brand_logos_matrix.py` — reusable prover for this category (21 providers x named brand matrix). What it encodes that hand-probing does not: slug indexes resolved from each provider's own manifest (jsDelivr `?structure=flat` for npm + `packages/gh`, `icon-sets/json/<set>.json` for Iconify, `list=allimages` for Commons), **version pinning from `tags.latest`**, exact-name-only matching with `--allow-derived` as an opt-in, BOM-tolerant magic sniffing, SVG `<path>`/`fill=` counts + PNG IHDR dims, cross-brand hash comparison to catch stub servers, and per-provider rate delays (iconify 2.5 s, unavatar 6 s). Full run: **13/21 sources clear 10/12**. Two bugs found and fixed while building it, both of the "silent truncation" class: a 2 MB read cap truncated the 8.7 MB icon-sets index so every Iconify provider reported `INDEX FAILED` (resolvers now pass `cap=INDEX_CAP` = 80 MB), and a `{b}`/`{slug}` collision turned VectorLogo.zone variants into `github-icon/github-icon-icon.svg`.
- 2026-09-21 | CORRECTION | brand-logos | **I published a wrong correction; the original was right.** (a) A sub-agent reported Simple Icons lacking microsoft/slack/openai; I "overturned" that by probing `.../npm/simple-icons/icons/openai.svg` → 200 + 1570 B and logged all three as present. Pinning exposed the truth: **jsDelivr's versionless path serves a stale cached release** — `@16.32.0` 404s openai and slack (removed at v16.0.0) and microsoft (removed at v13.0.0), while the versionless URL still returns the pre-removal bytes. So the correct lesson is *release ≠ release*, not *host ≠ host*: **always pin the version before counting coverage**, and never let a versionless 200 establish that a brand exists. `scripts/brand_logos_matrix.py` now resolves `tags.latest` and pins every npm template for exactly this reason. (b) `thesvg-color` does **not** use bare brand names — `github`/`vercel`/`openai`/`windsurf` 404 and only `<brand>-dark`/`-light` resolve, so a prefix matcher will "find" `github` by fetching `github-actions`, a *different mark* (this one still stands; the script's `--allow-derived` flag exists because of it). (c) WorldVectorLogo bare slugs score 7/12 but the real suffix-carrying slugs score 11/12 (also stands). Meta-lesson: a byte-check proves *bytes*, not *currency* — cross-brand hash comparison and version pinning are part of verification, not extras.
- 2026-09-21 | DOWNGRADE | brand-logos | Clearbit Logo → ❌ **DNS-dead** (was widely cited as the default free logo API); logo.dev, Brandfetch, IconScout, LogoDB, faviconkit, besticon, favicon.io, favicons.github.com → ❌ (token/HTML-fake/1×1-stub); `logotypes.dev` hosted API → ❌ 402; Pro Icons/Superdev, Circumicons, arconia, npm `brandicons` → ❌ not usable brand-logo sources at all. Existing `cdn.simpleicons.org` ❌ **confirmed still 403** for the plain form, with one nuance logged: `/slug/colour/size.png` answers 200 but the bytes are **SVG with the colour baked in** — the `.png` extension and `size` are ignored, so it is not a raster endpoint.
- 2026-09-21 | UPGRADE | documents | Prove-on-disk method fixed. `scripts/pdf_identity.py`'s regex page-count was **wrong or silent on 6 of 18** books (it missed page trees split across object streams, and `/Count` appears on intermediate nodes too). The authoritative check is poppler: `pdfinfo f.pdf | awk '/^Pages:|^Encrypted:/'` plus `pdftotext -f P -l P` on a **mid-document** page (~35% through) — a cover page proves nothing, and body text at p35% proves the whole file parsed. poppler-utils installs clean in a codespace (`sudo -n apt-get install -y poppler-utils`) when the Read tool's PDF renderer reports `pdftoppm is not installed`. Corrected counts now in the category: d2l 1151 pp, SICP 883, abs-guide 916, Common Lisp 587, RL 548, PLFA 516, Probability 518, Pro Git 501, Eloquent JS 463, FP-in-Lean 462, ODS-Java 334, GPML 266, Think Python 244, Think Bayes 210, Semaphores 291, r2book 297, Holy-x86 56, Learn Python 149. All 18 `Encrypted: no`.
- 2026-09-21 | ADD | documents | new category — 16 open-license full-text book PDFs byte-proven (magic + `%%EOF` + extracted title/first-page text), 11 distinct host families: `greenteapress.com` (5 titles, one provider), `github.com/…/releases` + `raw.githubusercontent.com` (6), `archive.org/download` (3), plus MIT/Stanford/CMU/Dartmouth/UWisc/UPenn/TLDp/PostgreSQL/gnu.org/eloquentjavascript/opendatastructures/gaussianprocess/d2l. Highest-yield hunting method was **not** guessing filenames: (a) `GET /repos/<r>/license` then `GET /repos/<r>/git/trees/<branch>?recursive=1` and filter `.pdf` >60 KB, plus `/releases` assets; (b) `advancedsearch.php` → `metadata/<identifier>` and require `access-restricted-item != true` **and** an open-license field, then take `/download/<id>/<file>.pdf`; (c) grep the landing page's own `href`/`src` for `.pdf` (`grep -oiE '[^"''"'"' <>]+\.pdf'` — catches `href=cpu-sched.pdf` forms a quoted-attribute regex misses).
- 2026-09-21 | UPGRADE | scripts | `verify_sources.py` gained a `pdf`/`doc` kind (`%PDF-` magic + trailer) and a `--range` trailer probe, because GitHub's signed release-asset bucket answers suffix `Range: bytes=-N` with **501** — explicit `bytes=<lo>-<hi>` works. Also: a `200` + `Content-Type: application/octet-stream` release asset is normal, so Content-Type alone cannot confirm a PDF.
- 2026-09-21 | DOWNGRADE | documents | catb.org → ❌ (TLS altname + HTTP 404); paulgraham.com `.pdf` → ❌ (200-HTML fake); Wikibooks `Special:DownloadAsPdf` → ❌ (HTML); hal.inria.fr `/document` → ❌ (HTML). OSTEP has **no** full-book PDF (per-chapter only) and `~rja14/Papers/SE-0n.pdf` are 12–21 pp papers, not the Security Engineering book — both looked like wins until the byte/page count proved otherwise.
- 2026-09-21 | NOTE | documents | "Top programming books" is mostly a closed set: Clean Code, Code Complete, Refactoring, The Pragmatic Programmer, CLRS, K&R, DDIA, Eloquent-with-ISBN titles have **no** legal free full-text PDF, and No Starch/PragProg only publish free *sample chapters* (`nostarch.com/download/PCC3e_ch2sample_8.17.22.pdf`) — which pass every byte check and are not books, so the verifier cannot tell them apart from a real one. Read the `/Count`, not the magic bytes.
- 2026-09-20 | ADD | images | Kyoto/Japan travel photo set — 12 real photographs via `Special:FilePath?width=1280`, all 200 + `image/jpeg`, 291–751 KB (mean 431 KB). Titles derived from the Commons search API, never guessed. Also recorded: the `?width=` ladder makes 1280 cost the same as 1000, Wikimedia refuses the default curl UA with a 2 KB HTML body (re-probe with `-A`), and the Commons API 429s under fast polling — needs ~1.5 s spacing plus backoff, and a *passing* byte check does **not** prove the photo is of the right place.
- 2026-09-20 | CONFIRM | images | `source.unsplash.com` still retired (503) — matches existing ❌ entry; `picsum.photos/seed/<x>/W/H` re-confirmed 200 `image/jpeg`, but serves *random* subjects, so it is not a stand-in for topical imagery.
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
