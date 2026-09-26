# Delivery

One master, N derivatives. `hyperframes render` produces the file; everything
here is what makes it usable where it is going. Platform numbers move — treat the
table as the shape of the decision, and confirm the current spec for the actual
destination before shipping.

## The master

Render the master at the spec's canvas and fps with `-q delivery`, from a
composition that already passed `check` and `qa.py`. Every derivative comes from
that file or from re-rendering the same composition — never from transcoding a
derivative.

```bash
npx hyperframes render . -o renders/master.mp4 -f <spec fps> -q delivery
```

## Derivative matrix

| Destination | Aspect | Notes |
|---|---|---|
| YouTube / embed / desktop hero | 16:9 | the master; chapters and description carry the CTA |
| Reels / Shorts / TikTok | 9:16 | re-render, do not pillarbox; safe zones tighten — the bottom 15% is under UI chrome |
| Feed video (IG, X, LinkedIn) | 1:1 or 4:5 | most feed players start muted |
| Deck or landing hero | 16:9 or 21:9 | 21:9 is already letterboxed — do not add bars |
| PR diff / docs | gif or webm at 15 fps | small, loopable, no audio |
| Broadcast / alpha overlay | mov (ProRes 4444) | keeps the alpha channel |

**A vertical cut is not a resize.** Reframing 16:9 to 9:16 changes what fits in
title-safe, kills two-column layouts, and moves the hook forward. Re-author the
scene list for the vertical version — shorter shots, one subject per frame,
burned-in captions — and let the composition carry it. `spec.py` treats aspect as
a structural input for exactly this reason.

## Muted-first rule

Any feed placement plays without sound by default. So:

- the story must survive silence — captions or on-screen text carries every beat
- a `voiceover`-dependent beat needs a caption twin
- sound is enhancement there, not the message

## Sound finishing

Target −14 LUFS integrated with true peak ≤ −1 dBTP for streaming, and check the
destination's current number before shipping. `qa.py` measures both. Loudness
*mechanics* — gain automation, ducking, carving a bed under a voice, effect
chains — belong to `/hyperframes-audio`; a duck alone is not a finished mix, and
its carve step runs before verify.

## Captions

Burned-in for muted feeds; a sidecar `.srt`/`.vtt` everywhere else so platforms
can restyle them and so the text is searchable. Word timing comes from
`/media-use` transcription; the caption track itself is `/hyperframes`' single
captions track, inside title-safe.

## Naming and handoff

```
<slug>_<aspect>_<duration>s_<destination>.mp4     myapp_9x16_24s_reels.mp4
renders/master.mp4                                 the source of every derivative
```

Deliver with: the axes and runtime actually shipped, the `qa.py` result (passes,
warnings, and any deliberate exception), the motion promises measured against
their expectations, and the file paths. Offer `npx hyperframes publish` for a
stable link — private by default — but never publish without being asked.

## The pre-handoff pass

```bash
npx hyperframes check . --json --at-transitions    # valid
python3 scripts/qa.py . --spec video-spec.json --video renders/master.mp4   # good
```

`qa.py` exits non-zero on a failure. A warning is a decision: fix it, or name it
in the handoff. An unmentioned warning is a defect you shipped on purpose.
