# SVG Logo Animation

**Method of the [`animation`](../SKILL.md) battery** — reached as `/animation svg <style> <file.svg>`.
This is the 100-style SVG/logo treatment path (v3); general UI motion (micro, component, transition) is
[`../life/method.md`](../life/method.md).

Turns a static SVG (flat `<path>` elements with solid fills) into an animated version using one of
**one hundred animation styles**. This file is the router: it identifies styles and nothing else. Shared
build rules, scaling, validation and delivery live in
[`references/foundations.md`](references/foundations.md); each style's template and geometry live in its
own recipe — **the recipe is the sole home of its numbers.**

## Read order

| The job is | Read |
|---|---|
| animate a target with a named style | [`references/foundations.md`](references/foundations.md) (once, fully) + `references/<style>.md` only |
| replicate an existing animated file onto a new one | foundations + the recipe matching that file's style; copy structure and ordering, re-derive every number for the new SVG's size — never literal seconds or pixels |
| color-only light/dark variant of an already-animated logo | foundations §8 alone — no recipe re-read |
| an effect outside the 100, or a new mechanic | [`references/rejected-mechanics.md`](references/rejected-mechanics.md) first — four measured failures are already recorded there |

No command or an unknown command: ask ONE question offering the one hundred (grouped by family: geometric, kinetic, optical, signal/filter, or ambient loop); if
asking is impossible, default to `liquid`.

## The 100 styles

| Style (command) | Signature — what it looks like | Trigger words · aliases | Duration |
|---|---|---|---|
| [`chrome-liquid`](references/chrome-liquid.md) (`liquid`) | Chrome outline draws itself → true colors rise like liquid bottom-to-top → diagonal sheen sweeps | liquid fill, liquid metal, chrome reveal · `chrome` | ~8s, then sheen loops |
| [`draw-fill`](references/draw-fill.md) (`draw`) | Each outline draws itself, then its fill fades in | draw itself, self-drawing, draw on, line by line, sign itself, one-shot intro | ~3.5s one-shot |
| [`loading-loop`](references/loading-loop.md) (`load`) | Outlines draw and reverse endlessly, never filling | loading, progress, loop forever, draws over and over · `loading` | infinite |
| [`elastic-entrance`](references/elastic-entrance.md) (`elastic`) | Logo elastically scales/rotates in, wobbles, glows, fades out | playful, bounce in, elastic, pop in, wobble, animated intro loop | ~8s loop |
| [`rise`](references/rise.md) (`rise`) | Shapes rise from below and fade in, one after another | rise up, staggered, fade in one by one, cascade | ~2.5s one-shot |
| [`iris`](references/iris.md) (`iris`) | Circular clip grows from the center, revealing like a camera iris | iris, circle reveal, cinematic reveal, spotlight (round) | ~1.5s one-shot |
| [`neon`](references/neon.md) (`neon`) | Dark stage, outlines flicker on like a neon sign, then fill glows steady | neon, glow sign, flicker on, dark stage | ~2s, holds |
| [`pulse`](references/pulse.md) (`pulse`) | Logo breathes — calm scale + glow inhale/exhale | breathing, ambient, idle, calm loop | infinite |
| [`flip`](references/flip.md) (`flip`) | Logo flips in like a card around its vertical axis | flip, card flip, 3D reveal | ~0.9s one-shot |
| [`comet`](references/comet.md) (`comet`) | Bright dash traces each outline endlessly like a comet; fills stay lit dimly | comet, energy line, trace, light traces the outline | infinite |
| [`focus`](references/focus.md) (`focus`) | Camera rack-focus — the artwork itself is soft and sharpens, with one deliberate re-blur | rack focus, defocus, blur resolves, soft to sharp, camera focus · `rack-focus`, `defocus` | ~1.4s one-shot |
| [`crt`](references/crt.md) (`crt`) | Hot line on the centreline, logo opens vertically out of it through scanlines that then fade | tv power on, crt, scanlines, band opens from the middle, retro screen · `tv`, `power-on`, `scanline` | ~1.2s one-shot |
| [`chroma`](references/chroma.md) (`chroma`) | Artwork splits into RGB channel ghosts, slides apart, converges back to the exact brand color | chromatic aberration, rgb split, channel separation, anaglyph · `rgb-split`, `chromatic-aberration` | ~1.8s one-shot, dark stage |
| [`mosaic`](references/mosaic.md) (`mosaic`) | Grid of mask tiles each opening on its own jittered beat, so a wave crosses the logo | mosaic, tiles, dissolve in, pixelated reveal, wave of squares · `dissolve`, `tiles` | ~1.4s one-shot |
| [`ripple`](references/ripple.md) (`ripple`) | Fractal noise displaces the actual geometry and the warp relaxes to crisp | ripple, water, liquid warp, refraction, heat haze · `water`, `liquid-warp` | ~1.6s one-shot |
| [`spark`](references/spark.md) (`spark`) | A bright spark travels the logo and the artwork stays lit in its wake | spark, weld, torch, travelling light draws it in · `weld`, `torch` | ~1.6s one-shot |
| [`engrave`](references/engrave.md) (`engrave`) | Blind embossed relief under a raking light that sweeps around, then real colors land | emboss, deboss, engraved, letterpress, blind seal, raking light · `emboss`, `deboss`, `letterpress` | ~1.8s one-shot |
| [`grain`](references/grain.md) (`grain`) | Resolves out of film grain as a noise threshold is raised until nothing is masked | film grain, noise dissolve, static resolves, analog reveal · `noise`, `film-grain`, `analog-grain` | ~1.5s one-shot |
| [`tide`](references/tide.md) (`tide`) | A wavy waterline rises and flattens, filling the logo from below | water fills up, wavy line rises, tide, liquid with a meniscus · `fill-up`, `wave-fill` | ~1.6s one-shot |
| [`polarity`](references/polarity.md) (`polarity`) | A band sweeps across and inverts whatever it touches | invert, negative, x-ray, polarity flip, band of inversion · `invert`, `negative`, `neg-band` | ~1.3s one-shot |
| [`blinds`](references/blinds.md) (`blinds`) | Horizontal slats open one after another, each growing its own height | blinds, shutters, horizontal slats open · `shutters` | ~0.9s one-shot |
| [`assemble`](references/assemble.md) (`assemble`) | Rectangular fragments fly in from scattered offsets and lock into the whole logo | shatter, pieces fly in, assemble, explode-in · `shatter`, `explode-in`, `pieces` | ~1.6s one-shot |
| [`lantern`](references/lantern.md) (`lantern`) | A soft round light wanders across and blooms, revealing the logo in its path | lantern, spotlight sweep, soft light wanders across · `sweep`, `lamp` | ~1.5s one-shot |
| [`pinwheel`](references/pinwheel.md) (`pinwheel`) | Wedges each scale up from the center on their own beat, sweeping like a turbine | pinwheel, turbine, wedges open, segmented iris · `iris-blades`, `turbine` | ~1.4s one-shot |
| [`unroll`](references/unroll.md) (`unroll`) | The logo falls into place around a fixed top hinge, like paper unrolling | unroll, paper falls into place, hinged at the top · `paper`, `fall-in` | ~1.1s one-shot |
| [`curtain`](references/curtain.md) (`curtain`) | Two opposing vertical halves part outward from the centreline behind a brief vertical seam glint | curtain, split reveal, center out, theater doors · `split`, `doors` | ~1.1s one-shot |
| [`diamond`](references/diamond.md) (`diamond`) | Rotated 45° diamond aperture expands from the center with crisp chamfered diagonal edges | diamond, rhombus, chamfer reveal, angled iris · `rhombus`, `lozenge` | ~1.2s one-shot |
| [`chevron`](references/chevron.md) (`chevron`) | Bold arrowhead wedge sweeps across left-to-right, slicing the artwork open in its wake | chevron, arrow wipe, wedge sweep, spearhead · `arrow-wipe`, `wedge` | ~1.1s one-shot |
| [`louver`](references/louver.md) (`louver`) | Vertical architectural slats across X each widen on a staggered wave | vertical blinds, louvers, columns open, vertical slats · `columns`, `slats` | ~1.0s one-shot |
| [`slash`](references/slash.md) (`slash`) | Two opposing diagonal half-planes slide in from opposite corners and lock along the diagonal | diagonal wipe, slash, scissor wipe, dual diagonal · `diagonal`, `scissor` | ~1.0s one-shot |
| [`zipper`](references/zipper.md) (`zipper`) | Alternating horizontal strips slide in from opposite left/right edges and interlock cleanly | zipper, interlock, alternating strips, horizontal weave · `weave`, `interlock` | ~1.2s one-shot |
| [`rings`](references/rings.md) (`rings`) | Concentric stroked rings radiate outward from the center and thicken until they fuse solid | concentric rings, ripple rings, sonar, radar rings · `sonar`, `concentric` | ~1.4s one-shot |
| [`pendulum`](references/pendulum.md) (`pendulum`) | Logo hangs from a top-center pivot and settles through a damped harmonic swing | pendulum, swing in, hanging sign, damped sway · `swing`, `sway` | ~1.5s one-shot |
| [`typewriter`](references/typewriter.md) (`typewriter`) | Stepped discrete reveal marches across in mechanical ticks behind a blinking vertical caret | typewriter, terminal, cursor reveal, stepped wipe · `typing`, `caret` | ~1.4s one-shot |
| [`drop`](references/drop.md) (`drop`) | Drops gently from above and lands with a tight, clearance-safe squash-and-stretch settle | squash drop, gravity drop, land, thud settle · `squash`, `gravity` | ~1.1s one-shot |
| [`sprint`](references/sprint.md) (`sprint`) | Artwork dashes in leaning forward in italic skew, brakes past center, and snaps upright | skew sprint, speed brake, kinetic dash, italic slide · `dash`, `skew` | ~1.0s one-shot |
| [`accordion`](references/accordion.md) (`accordion`) | Vertical clipped strips unfold along Y from individual left hinges like pleated paper | accordion, fold out, pleats, brochure open · `pleat`, `fold-out` | ~1.3s one-shot |
| [`orbit`](references/orbit.md) (`orbit`) | Original path layers arc in along opposing curved trajectories and lock into print registration | orbit, print registration, layers converge, dual arc · `converge`, `register` | ~1.2s one-shot |
| [`blueprint`](references/blueprint.md) (`blueprint`) | Faint architectural grid and hairline wireframe draw in first, then true colors crossfade solid | blueprint, wireframe, cad, technical draft, schematic · `wireframe`, `cad` | ~2.0s one-shot |
| [`prism`](references/prism.md) (`prism`) | Spectral rainbow band sweeps across with rotating hue shift, leaving exact brand colors behind | prism, rainbow sweep, spectrum, iridescent wipe · `spectrum`, `rainbow` | ~1.5s one-shot |
| [`colorize`](references/colorize.md) (`colorize`) | Enters crisp in architectural grayscale, then true brand colors wipe cleanly left-to-right | colorize, grayscale to color, mono wipe, desaturate reveal · `mono`, `grayscale` | ~1.5s one-shot |
| [`exposure`](references/exposure.md) (`exposure`) | Overexposed darkroom flash develops downward in brightness and contrast to crisp tonal lock | exposure, flash develop, darkroom, overexposed settle · `flash`, `develop` | ~1.3s one-shot |
| [`scanner`](references/scanner.md) (`scanner`) | Glowing vertical laser sweeps right to trace wireframe, then returns left locking solid fills | scanner, laser scan, barcode beam, optical sweep · `laser`, `xray-scan` | ~1.8s one-shot |
| [`glitch`](references/glitch.md) (`glitch`) | Horizontal micro-slices jitter in stepped digital bursts, then snap sharply into exact lock | glitch, signal lock, slice jitter, digital snap · `signal`, `jitter` | ~1.1s one-shot |
| [`posterize`](references/posterize.md) (`posterize`) | Quantized screenprint color bands step from 2-tone through multi-tone into continuous exact color | posterize, screenprint, risograph, tonal steps · `risograph`, `screenprint` | ~1.4s one-shot |
| [`shimmer`](references/shimmer.md) (`shimmer`) | Finished logo stays crisp while a soft diagonal white specular glint glides across periodically | shimmer, sheen loop, gloss sweep, subtle glint · `sheen`, `glint` | infinite (~3.2s) |
| [`heartbeat`](references/heartbeat.md) (`heartbeat`) | Rhythmic double-beat lub-dub scale cadence (clamped to edge clearance) with a calm rest | heartbeat, lub-dub, cardiac pulse, double beat · `cardiac`, `thump` | infinite (~1.8s) |
| [`float`](references/float.md) (`float`) | Weightless micro-levitation drifting gently up and down with a subtle tilt | float, levitate, hover loop, zero gravity, drift · `levitate`, `drift` | infinite (~3.6s) |
| [`radar`](references/radar.md) (`radar`) | Translucent rotating beacon wedge sweeps 360° inside the logo silhouette endlessly | radar, beacon sweep, sonar loop, rotating glint · `beacon`, `sweep-loop` | infinite (~2.8s) |
| [`stamp`](references/stamp.md) (`stamp`) | Heavy ink-press impact with tight micro-recoil and an expanding shockwave ring that fades out | stamp, ink press, impact, seal strike · `press`, `impact` | ~0.95s one-shot |
| [`hexagon`](references/hexagon.md) (`hexagon`) | Six-sided honeycomb polygon aperture expands from the center with a crisp 30° twist lock | hexagon, honeycomb, hex iris, six-sided reveal · `hex`, `honeycomb` | ~1.25s one-shot |
| [`starburst`](references/starburst.md) (`starburst`) | Twelve-point faceted star aperture bursts outward from the center with a slight rotational snap | starburst, star reveal, burst, spiky iris · `star`, `burst` | ~1.15s one-shot |
| [`checker`](references/checker.md) (`checker`) | Chessboard parity mask pops even squares in first, then fills the odd complement on beat two | checkerboard, chess reveal, two-beat grid, parity tiles · `chess`, `parity` | ~0.85s one-shot |
| [`crosshair`](references/crosshair.md) (`crosshair`) | Sighting bars form a plus-shaped crosshair at center, then widen both axes outward to reveal all quadrants | crosshair, plus reveal, reticle, target lock, quad open · `reticle`, `plus` | ~1.15s one-shot |
| [`frame`](references/frame.md) (`frame`) | Four border curtains creep inward simultaneously from all four edges and seal cleanly at the center | frame in, border inward, perimeter close, reverse iris · `border-in`, `perimeter` | ~1.05s one-shot |
| [`horizon`](references/horizon.md) (`horizon`) | Top and bottom mask doors close inward toward the center equator and seal with a horizontal glint | horizon, top-bottom close, equator seal, vertical clamp · `equator`, `clamp` | ~1.25s one-shot |
| [`staircase`](references/staircase.md) (`staircase`) | Vertical columns rise sequentially from the bottom edge like ascending bar-chart risers | staircase, equalizer, rising columns, bar chart reveal · `bars`, `equalizer` | ~1.15s one-shot |
| [`fan`](references/fan.md) (`fan`) | Radial wedges hinged at the bottom-left corner unfold clockwise like a Japanese hand fan | hand fan, corner fan, folding fan, corner sweep · `hand-fan`, `corner-fan` | ~1.25s one-shot |
| [`spotlight`](references/spotlight.md) (`spotlight`) | Three soft radial spotlights drift inward from separate corners and bloom together into full light | triple spotlight, stage lights, converging lamps, floodlights · `stage-lights`, `floodlight` | ~1.45s one-shot |
| [`tunnel`](references/tunnel.md) (`tunnel`) | Concentric rounded-rectangle frames radiate outward from a center pill and fuse solid | tunnel, rounded frames, corridor, concentric boxes · `corridor`, `frames` | ~1.25s one-shot |
| [`book`](references/book.md) (`book`) | Logo swings open around a fixed left-edge spine like turning a hardcover book page | book open, page turn, left hinge, door swing · `page-turn`, `hinge-left` | ~1.15s one-shot |
| [`trapdoor`](references/trapdoor.md) (`trapdoor`) | Logo rises up from a fixed bottom-edge floor hinge like a pop-up card standing upright | trapdoor, pop-up card, floor hinge, bottom unroll · `popup-card`, `hinge-bottom` | ~1.1s one-shot |
| [`slingshot`](references/slingshot.md) (`slingshot`) | Logo pulls back slightly in anticipation, snaps horizontally across, and settles with elastic recoil | slingshot, anticipation, snap back, rubber band · `recoil`, `snap-back` | ~1.15s one-shot |
| [`domino`](references/domino.md) (`domino`) | Vertical clipped strips tilt upright in a cascading 2-D falling-domino wave across the logo | domino, domino cascade, tilting strips, falling blocks · `cascade-tilt`, `dominoes` | ~1.25s one-shot |
| [`venetian`](references/venetian.md) (`venetian`) | Horizontal clipped slats each twist open in 3-D around their own centerline like venetian blinds | 3d blinds, venetian slats, twist open, horizontal flip · `3d-blinds`, `twist-slats` | ~1.2s one-shot |
| [`carousel`](references/carousel.md) (`carousel`) | Vertical clipped columns slide in vertically from alternating top and bottom edges like slot drums | slot machine, vertical weave, drum roll, alternating columns · `slots`, `drums` | ~1.2s one-shot |
| [`tumble`](references/tumble.md) (`tumble`) | Logo rolls in along a shallow micro-arc with a damped counter-tilt like a coin settling flat | tumble, roll in, coin settle, tilt roll · `roll-in`, `coin` | ~1.25s one-shot |
| [`spring`](references/spring.md) (`spring`) | Compressed horizontally at the center, the logo snaps outward along X like a coiled spring | coiled spring, horizontal bounce, stretch out, elastic widen · `coil`, `widen` | ~1.1s one-shot |
| [`anvil`](references/anvil.md) (`anvil`) | Logo snaps upright vertically from the baseline as twin horizontal impact sparks shoot outward | anvil, stomp, floor slam, baseline pop, heavy land · `slam`, `stomp` | ~0.95s one-shot |
| [`parallax`](references/parallax.md) (`parallax`) | Separate path layers glide in horizontally at staggered camera speeds, locking into 2.5-D depth | parallax, depth pan, camera slide, layered pan · `depth-pan`, `layered-slide` | ~1.25s one-shot |
| [`sepia`](references/sepia.md) (`sepia`) | Enters bathed in warm archival sepia film tones that gradually cool into exact brand colors | sepia, vintage film, archival warm, antique tone · `vintage`, `archival` | ~1.45s one-shot |
| [`thermal`](references/thermal.md) (`thermal`) | Infrared false-color heat map glows violet-to-amber across the logo before cooling to true colors | thermal, infrared, heat map, predator vision, flir · `infrared`, `heatmap` | ~1.55s one-shot |
| [`duotone`](references/duotone.md) (`duotone`) | High-contrast two-ink editorial print wash enters crisp and crossfades to the full brand palette | duotone, two-ink, editorial print, monochrome tint · `two-ink`, `tint-reveal` | ~1.45s one-shot |
| [`solarize`](references/solarize.md) (`solarize`) | Sabattier darkroom tone-inversion curve morphs dynamically from metallic negative to true color | solarize, sabattier, tonal fold, darkroom negative · `sabattier`, `tone-fold` | ~1.45s one-shot |
| [`cyanotype`](references/cyanotype.md) (`cyanotype`) | Sun-exposed Prussian-blue blueprint proof develops from pale wash to rich blue, then lands true color | cyanotype, sunprint, prussian blue, photo blueprint · `sunprint`, `prussian` | ~1.65s one-shot |
| [`vignette`](references/vignette.md) (`vignette`) | Soft elliptical center glow blooms outward from a dim moody halo until the entire logo sits fully lit | vignette, center bloom, soft iris, feathered spotlight · `soft-iris`, `center-bloom` | ~1.4s one-shot |
| [`xray`](references/xray.md) (`xray`) | Clinical cyan-tinted negative radiograph flashes into view, then wipes cleanly into exact solid fills | x-ray radiograph, medical scan, negative wipe, bone scan · `radiograph`, `neg-wipe` | ~1.55s one-shot |
| [`chroma-v`](references/chroma-v.md) (`chroma-v`) | Artwork splits vertically into additive RGB channel ghosts on a dark stage and converges crisp | vertical chromatic aberration, vertical rgb split, v-anaglyph · `v-chroma`, `rgb-vertical` | ~1.7s one-shot, dark stage |
| [`flashbulb`](references/flashbulb.md) (`flashbulb`) | Crisp camera strobe white-out drops briefly into a dark afterimage dip before snapping to exact tone | flashbulb, camera strobe, paparazzi flash, shutter pop · `strobe`, `shutter-flash` | ~1.2s one-shot |
| [`inkbleed`](references/inkbleed.md) (`inkbleed`) | Organic low-frequency cloud blooms through an alpha threshold like watercolor ink soaking wet paper | ink bleed, watercolor bloom, cloud dissolve, organic soak · `watercolor`, `soak` | ~1.65s one-shot |
| [`morse`](references/morse.md) (`morse`) | Rhythmic short-long Morse code dashed contours race along the outlines before solid fills lock in | morse code, telegraph, dashed signal, dot-dash draw · `telegraph`, `dot-dash` | ~1.65s one-shot |
| [`etch`](references/etch.md) (`etch`) | Copperplate 45° diagonal crosshatch proof wipes across inside the silhouette, then inks solid | etching, crosshatch, copperplate, engraving proof, sketch hatch · `crosshatch`, `copperplate` | ~1.6s one-shot |
| [`holo`](references/holo.md) (`holo`) | Holographic transmission drops in across two jittered projection bursts through shimmering cyan bars | hologram, sci-fi transmission, holo projection, beam in · `hologram`, `projection` | ~1.45s one-shot |
| [`wave-h`](references/wave-h.md) (`wave-h`) | Anisotropic horizontal heat-shimmer bands ripple across the logo geometry and relax to crisp | horizontal wave, heat haze, mirage, shimmer warp · `mirage`, `heat-haze` | ~1.5s one-shot |
| [`wave-v`](references/wave-v.md) (`wave-v`) | Vertical fluted-glass refraction bands warp the artwork vertically before settling crystal clear | fluted glass, vertical wave, reed glass, curtain refraction · `fluted`, `reed-glass` | ~1.5s one-shot |
| [`chisel`](references/chisel.md) (`chisel`) | Raking light climbs from low 12° sunrise to 78° overhead across carved stone relief, then true color lands | chisel, stone carve, elevation light, sunrise relief · `carve`, `bevel-rise` | ~1.65s one-shot |
| [`static`](references/static.md) (`static`) | Broadcast RF snow and rapid stepped horizontal tracking lock settle cleanly into sharp reception | tv static, rf snow, signal tracking, tuning lock · `rf-snow`, `tuning` | ~1.15s one-shot |
| [`stencil`](references/stencil.md) (`stencil`) | Three staggered soft-edged airbrush strokes spray across top, middle, and bottom bands to fill the mark | stencil, spray paint, airbrush, graffiti pass, three passes · `spray`, `airbrush` | ~1.2s one-shot |
| [`laser-h`](references/laser-h.md) (`laser-h`) | Twin glowing horizontal laser beams sweep outward from center Y, burning wireframe before solid fill lock | twin laser, horizontal laser, dual beam, burn reveal · `dual-laser`, `twin-beam` | ~1.25s one-shot |
| [`pixel-step`](references/pixel-step.md) (`pixel-step`) | Coarse 8×3 macro blocks snap on crisply in center-out spiral order with zero fade smoothing | pixel pop, spiral blocks, hard snap grid, retro load · `spiral-grid`, `block-pop` | ~1.15s one-shot |
| [`glimmer`](references/glimmer.md) (`glimmer`) | Crisp resting logo stays sharp while four asynchronous 4-point starlight sparkles twinkle inside the mark | glimmer, sparkles, twinkle, starlight, jewelry glint · `sparkles`, `twinkle` | infinite (~3–4s async) |
| [`pendulum-loop`](references/pendulum-loop.md) (`pendulum-loop`) | Calm infinite metronome sway gently rocks the logo around a top-center hinge within tight clearance | metronome, gentle sway, hanging loop, rock loop · `metronome`, `sway-loop` | infinite (~4.2s) |
| [`neon-loop`](references/neon-loop.md) (`neon-loop`) | Dark-stage glowing neon logo stays steady with periodic realistic electrical hum and subtle tube blinks | neon idle, buzzing sign, neon hum, ambient neon · `neon-idle`, `sign-hum` | infinite (~4.8s) |
| [`wave-loop`](references/wave-loop.md) (`wave-loop`) | Seamless horizontal highlight band glides smoothly up and down inside the logo like calm water light | water reflection, vertical sheen loop, bobbing light, caustic band · `reflection`, `caustic` | infinite (~3.4s) |
| [`chrome-loop`](references/chrome-loop.md) (`chrome-loop`) | Dual opposing metallic sheen bands cross asynchronously over the solid logo like living brushed steel | brushed metal, dual sheen, chrome ambient, steel glint · `brushed-metal`, `dual-sheen` | infinite (~3.8s / 4.7s) |
| [`sonar-loop`](references/sonar-loop.md) (`sonar-loop`) | Two staggered concentric ellipse pings expand softly behind the razor-sharp logo and fade out endlessly | sonar pulse, beacon ping, radar rings loop, broadcast wave · `ping`, `broadcast` | infinite (~3.0s) |
| [`prism-loop`](references/prism-loop.md) (`prism-loop`) | Subtle iridescent rainbow sheen drifts gently across the solid logo silhouette on a calm ambient cycle | iridescent loop, holographic sheen, rainbow glint, foil loop · `iridescent`, `foil` | infinite (~4.4s) |
| [`orbit-loop`](references/orbit-loop.md) (`orbit-loop`) | A luminous brand-colored satellite dot continuously traces an elliptical orbit around the logo | satellite, orbiting dot, electron loop, planet track · `satellite`, `electron` | infinite (~3.6s) |
| [`breathe-opacity`](references/breathe-opacity.md) (`breathe-opacity`) | Ultra-calm stationary luminance and opacity breathing loop with zero spatial movement or blur | calm fade loop, gentle breathe, minimal idle, status glow · `minimal-idle`, `soft-breathe` | infinite (~4.0s) |
| [`marquee`](references/marquee.md) (`marquee`) | Continuous marching-ants dashed highlight glides cleanly along every logo contour over solid resting fills | marching ants, dashed perimeter, outline loop, ticker border · `marching-ants`, `perimeter-loop` | infinite (~1.2s) |

`/animation svg <command> <file.svg>` must reproduce the matching recipe's treatment (structure and
ordering; numbers re-derived per the foundations scaling table). The four `liquid` / `draw` / `load` /
`elastic` treatments were originally tuned against an external `variations/` reference set that is **not
in this repository** — the recipes in `references/` are the authoritative description, and the ninety
`examples/*.svg` files (15 from v1 + 25 from v2 + 50 new v3 styles) are committed alongside an
`examples/index.html` review harness.

## Layout

```text
svg/
├── method.md                         this router — style identification only
├── references/
│   ├── foundations.md                shared build rules: extraction, scaling, hard rules, validation, variants, delivery
│   ├── rejected-mechanics.md         four measured failures — read before inventing a 101st mechanic
│   └── <style>.md × 100               one recipe per style: template + geometry + unique notes
├── scripts/                          extract_paths.py, validate.py (run, never read)
└── examples/
    ├── index.html                    dependency-free <img> review gallery with replay, stage & zoom controls
    └── *.svg × 90                    worked outputs (15 v1 + 25 v2 + 50 new v3 styles)
```
