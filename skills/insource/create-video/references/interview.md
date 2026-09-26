# The Interview Protocol

The whole point of this skill: **no composition gets built from an adjective.**
But an interview that fires fourteen questions at the user is its own failure —
it reads as a form, not as a collaborator. So the protocol is derive first, ask
small, and never ask something the brief already answered.

## The three laws

1. **Derive before you ask.** Read the brief, fill every slot you can with an
   explicit inferred value, and mark it `inferred`. Only unfilled or
   expensive-to-get-wrong slots become questions.
2. **Ask in consequences, not adjectives.** An option that says `Fast` is worth
   nothing. `Fast — 24–45 cuts/min, shots 1.3–2.5s` is a decision the user can
   actually make.
3. **Lock before building.** The user sees the full spec and the derived build
   sheet, then says go. No silent defaults reach the render.

## What must never be inferred

These four are expensive to get wrong and cheap to ask. If the brief does not
state one, it is a question, whatever else you skip:

- **purpose** — the one sentence the video exists to serve
- **aspect** — decided by where it plays, not by taste
- **duration** — a 20s and a 90s brief are different jobs
- **audio** — music, voiceover, both, or none; it changes the structure

Everything else — the other five axes, the scene list — may be inferred and
presented for correction instead of being asked outright.

## Question mechanics

`AskUserQuestion` takes **at most 4 questions per call**, **2–4 options each**,
and always offers a free-text "Other". Plan around that:

- **Round 1 — the load-bearing four.** purpose (if unclear), aspect/platform,
  duration, audio. These gate everything else.
- **Round 2 — the shape of the thing.** pacing, camera_style, tone, and whichever
  of genre / visual_style / editing_style the brief left most open.
- **Scenes are proposed, never interrogated.** Free-text scene content does not
  fit an option list. Draft the structure from genre + duration + purpose, show
  it, and ask one approve-or-change question about it in prose.

Two rounds is the budget. A third round means Round 1 was asked badly — the
options were too vague or the brief was not read.

## Writing the options

Each option: the value, its number, and its feel. Three or four per question.

```
Q: What is the video's momentum?
   Moderate — 12–24 cuts/min, one idea per shot. Conversational explainer rhythm.
   Fast     — 24–45 cuts/min, shots 1.3–2.5s. Energetic; nothing is held long.
   Slow     — 6–12 cuts/min, shots 5–10s. Calm; reveals unfold, long holds.
```

```
Q: How does the frame behave?
   Static   — camera locked; all motion lives inside the frame. Cheapest to build.
   Tracking — viewport follows the focal point across the scene.
   Drone    — 3D flight through depth; heaviest build, most spectacle.
   Mixed    — one camera language per beat.
```

Never offer two options that differ only in adjectives ("cinematic", "epic").
If the user's own words were adjectives, translate them through
`dimensions.md`'s word→axis table first and ask about the axis.

## Presenting the draft

Show what you inferred, not just what they answered — that is where wrong
assumptions get caught:

```
Locked from your brief:
  genre        product_showcase   (from "show the app working")
  pacing       moderate           ← asking
  visual       minimal            (from "clean, like the site")
  camera       tracking           ← asking
  editing      standard_cuts      inferred from pacing
  tone         inspirational      ← asking
  aspect       9:16               (you said Reels)
  duration     24s                ← asking
  audio        music, no VO       (Reels usually plays muted — captions either way)
```

Flag every inferred value as inferred. If the user corrects one, re-run
`spec.py` — the derived numbers change with it.

## The lock

1. Write `video-spec.json` (see `spec-template.md`).
2. `python3 scripts/spec.py video-spec.json` → the build sheet.
3. Show the build sheet. Ask once: build it, or change something.

If `spec.py` exits non-zero, the spec is not ready — resolve the errors with the
user before touching the composition. Warnings are judgment calls: read them out
and say which way you resolved each.

## When the user refuses to decide

"Make it look good, you decide" is a legitimate answer. Then:

- pick the defaults for the genre from `dimensions.md`
- state each choice and its number out loud in the lock message
- keep the four never-infer slots if the user *did* say them — refusing the style
  interview is not permission to ignore "it's for Reels, 30 seconds"

Deciding on the user's behalf is fine. Deciding silently is not.

## What not to ask

- Anything the brief already answers, in other words ("is it for YouTube?" after
  they said "for my channel's homepage hero")
- Brand assets, colours, fonts, copy — request them as files, not as a question
- Frame-level art direction; that is `hyperframes-animation`'s and the build's job
- Whether they want it "professional" — every deliverable is professional by
  default; never imply the alternative
