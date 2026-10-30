---
name: watch-video
argument-hint: <video-url-or-local-path> [section or question]
description: Watch a video by reconstructing it from frames plus a timestamped transcript, measure how objects move through it, and write structured markdown notes. Downloads with yt-dlp, extracts auto-scaled JPEG frames with ffmpeg, gets captions (Whisper API fallback), then reads frames and speech together. scripts/motion.py compares two frames or a whole frame dump and reports which way the dominant object went as one of eight compass directions, in-place (including rotation about itself), or cannot-determine. Use when the user asks to watch, analyze, summarize, transcribe, take notes on, or explain a video, asks what is shown on screen at a given moment, asks where an object went, whether the camera pans, or about motion or editing style, wants a presentation or editing style replicated, hands over a YouTube/Vimeo/TikTok/X/Twitch/Loom/Instagram URL or a local mp4/mov/mkv/webm and asks about its content, or types /watch-video.
---

# Watch Video

## Overview

Video models cannot stream video, so this skill fakes it: `scripts/watch.py` downloads the source, cuts a duration-scaled set of still frames, fetches a timestamped transcript, and prints a report. Then read the frames with the `Read` tool, align each frame to the words spoken at its timestamp, and write one markdown notes file. Where movement matters, `scripts/motion.py` measures which way the subject actually went instead of guessing from two stills.

The pipeline is vendored from [bradautomates/claude-video](https://github.com/bradautomates/claude-video) (MIT — see `THIRD_PARTY_NOTICES.md`); `motion.py` is original to this skill.

## Pick the cheapest tier that answers the question

| The ask | Do this |
|---|---|
| "What does this video say?" / "summarize the argument" on a talking-head video | `watch.py "<url>" --transcript-only` — captions only, no video download, no frames. |
| Anything about how it **looks**, or a claim that on-screen text, slides, code, or B-roll carries the content | Full pipeline below. |
| Anything about **movement** — where something went, a camera pan, an editing rhythm | Full pipeline, then step 4's `motion.py`. |
| One moment of a long video | Full pipeline with `--start`/`--end` — always prefer this over a full scan past 10 minutes. |

## 1. Preflight

```bash
python3 .qoder/skills/watch-video/scripts/setup.py --check
```

Exit 0 = ready. 2 = a binary is missing. 3 = binaries fine but no Whisper key (captioned videos still work; uncaptioned come back frames-only). 4 = unhandled.

Install what is missing: `ffmpeg`/`ffprobe` via `sudo apt install ffmpeg`, `brew install ffmpeg`, or `winget install Gyan.FFmpeg`; `yt-dlp` via `pipx install yt-dlp` or `brew install yt-dlp`. `python3` alone (no module dependencies) is enough.

A Whisper key is only needed for videos without English-ish captions. Put `GROQ_API_KEY` (preferred: cheaper, faster, runs `whisper-large-v3`) or `OPENAI_API_KEY` in `~/.config/watch/.env` — run `setup.py` to scaffold it. Never put either key in a project's `.env` or in source.

## 2. Run the pipeline

```bash
python3 .qoder/skills/watch-video/scripts/watch.py "<url-or-local-path>" [flags]
```

Progress goes to stderr; the markdown report goes to stdout. Capture stdout — it is the frame manifest, the transcript, and the work dir path.

| Flag | Effect |
|---|---|
| `--start T` / `--end T` | Focus a section (`SS`, `MM:SS`, `HH:MM:SS`). Packs frames denser inside the window. |
| `--max-frames N` | Frame cap. Default 80, hard max 100. |
| `--resolution W` | Frame width in px. Default 512; raise to 1024 only when on-screen text is unreadable. |
| `--fps F` | Override auto-fps. Hard-capped at 2 fps. |
| `--whisper groq\|openai` | Force one backend. Default prefers Groq when its key exists; there is **no** mid-run fallback between backends. |
| `--no-whisper` | Skip transcription; frames-only when captions are absent. |
| `--transcript-only` | Captions only: never downloads the video, never extracts frames, never calls Whisper. URLs only. |
| `--cookies FILE` | Netscape `cookies.txt` for yt-dlp — the remedy for a bot-blocked source (see Gotchas). |
| `--cookies-from-browser BROWSER` | Pull cookies from an installed browser (`chrome`, `firefox`, `chrome:Profile 1`, …). |
| `--out-dir DIR` | Work somewhere specific instead of the system temp dir. Only on explicit request. |
| `--slug NAME` | Name the temp work directory, instead of one derived from the source. |

Full-video budgets: ≤30s ≈ 1 frame/sec (never below 12) · 30–60s → 40 · 1–3min → 60 · 3–10min → 80 · >10min → the cap, sparse, and the report says so.

Focused budgets (`--start`/`--end`): the target density rises to 6 fps for a ≤5s window and 4 fps for ≤15s, but **2 fps is the hard ceiling**, so short windows land at ~2 frames/sec (a 5s window → 10 frames) · 15–30s → 60 · 30–60s → 80 · >60s → the cap.

### Where the files go

Every run splits its working directory in two, and the report prints both paths:

```
<work>/input/     download, frames/, audio.mp3   — what the video gave us
<work>/output/    notes.md, motion.md            — what we make of it
```

Runs land in the **system temp dir** by default — never in the repo. The path is
`<tempdir>/watch-video/<name>/`, where `<name>` comes from the source or
`--slug`, so a re-run of the same video gets a predictable location instead of a
fresh random directory (a second run on an occupied name takes `-2`, never a
shared folder). Anything written into `output/` is deleted by step 6 unless you
move it out first — so write the notes file to its permanent home, not into the
work dir.

Only pass `--out-dir` when the user explicitly asks for the work to live inside
the project. Then say that the path is untracked and will show up in
`git status`, and clean it up in the same session.

## 3. Read the frames

Issue the `Read` calls for every frame path in one message — they render as images and parallel batching keeps the round-trips at one. When the count exceeds ~40, read every other frame first and go back for the in-between frames of any beat that needs visual confirmation.

Each report line is `- \`<abs path>\` (t=MM:SS)`. Pair that timestamp with the `[MM:SS]` transcript lines around it: the frame says what was on screen while that line was spoken. That pairing is where the value is — never write the summary from the transcript alone.

## 4. Measure motion (only when movement carries meaning)

When the ask is about movement — action, animation, camera work, an editing style, a play, "did the ball go left?" — do not eyeball direction off a few frames. Measure it.

```bash
python3 .qoder/skills/watch-video/scripts/motion.py <frameA> <frameB>
python3 .qoder/skills/watch-video/scripts/motion.py --seq <work>/input/frames --step 2
```

- **Pair mode** prints the direction, the bearing (0° = up, clockwise), the shift as a fraction of the frame, the changed area, a confidence, a plain-language reason, and an ASCII map — `o` where it was, `#` where it went, arrow glyphs along the path.
- **`--seq`** walks every consecutive pair in a frame dump and tallies the result, so a clip reads as *right ×8, in-place ×2, top ×9*. Use `--step 2` for brisk action and `--step 4+` for slow scenes, where adjacent frames barely differ.
- **`--json`** works on either mode.

The verdict is one of `top`, `top-right`, `right`, `bottom-right`, `bottom`, `bottom-left`, `left`, `top-left`, or:

- **`in-place`** — either nothing moved, or the picture changed a lot while the centre of mass held still, which is what an object **rotating or deforming about itself** looks like. The `Why:` line says which of the two it was.
- **`cannot-determine`** — a one-sided change (something entering or leaving frame, a fade), a scene cut, or a frame too flat to track. Never promote this to a guess.

How it decides, so you know what to trust: the frame difference is split into the pixels that brightened and the pixels that darkened. A moving object leaves a darkened trail where it was and a brightened arrival where it went, so the vector between the two centroids *is* its displacement. That also means it reports the **net** motion of everything that changed — a camera pan reads as the pan, and two objects moving opposite ways can cancel out, surfacing as low confidence or `in-place`. Quote the confidence alongside the direction, and look at the frames yourself below about 0.5.

`python3 .qoder/skills/watch-video/scripts/selftest.py` builds eight frames with known motion and asserts the verdicts — run it after changing any threshold in `motion.py`.

## 5. Write the notes file

Write **outside** the work dir, which step 6 deletes. Default to `notes/videos/<video-slug>.md` under the project root; ask the user first when they implied somewhere else.

```markdown
# <Title>

**Source:** <URL or local path>
**Duration:** <mm:ss>
**Uploader:** <if from a site>
**Transcript source:** <captions / whisper (groq) / whisper (openai) / none>

## One-line summary
<≤20 words — the video's core claim or hook>

## TL;DR
<3–5 bullets: the main arguments, moments, or beats>

## Timeline
- **[00:00]** <what is on screen + the key line being said>
<one row per meaningful beat, not per frame>

## Key quotes
> "<verbatim quote>" — [mm:ss]

## Visual notes
<what only frames reveal: setting, B-roll, on-screen text, slides, graphics, transitions, the speaker's emotion>

## Motion
<only when step 4 ran: the direction per beat with its confidence, the camera's own movement, and anything that rotated or deformed in place>

## Takeaways
<only when the content bears on the user's domain or goals; otherwise drop this section>
```

## 6. Clean up

Delete the work dir named in the report footer (`_Delete <work> when done…_`). It holds the downloaded video plus every frame. Move the notes file out of `output/` first, and ask before deleting an `--out-dir` the user chose.

## Gotchas

- **Captions are fetched for `en,en-US,en-GB,en-orig` only** (manual first, then auto-generated, as VTT). A foreign-language video with no such captions silently falls through to Whisper, and Whisper output is not translated. Report the transcript source so the user knows what was actually read.
- **`Sign in to confirm you're not a bot`** — YouTube (and Vimeo's web client) commonly refuses anonymous extraction from cloud, CI, and devcontainer IPs. This is IP-level: a JS runtime does not clear it, and `watch.py` already passes `--js-runtimes deno|node` automatically when either is installed. Remedies, in order: pass `--cookies-from-browser chrome` on a machine with a logged-in browser; export a `cookies.txt` and pass `--cookies`; or hand the user a local file. If none is available, say the source is blocked and offer the transcript route — do not invent content.
- **Shorts, age-gated, members-only, region-locked** sources can make yt-dlp fail for their own reasons. Surface its stderr verbatim; do not retry silently.
- **A local file with no audio track** makes Whisper extraction fail cleanly — pass `--no-whisper`. `--transcript-only` never works on a local file (nothing to caption it).
- **Groq 403** comes from Cloudflare rejecting the default Python user agent; `whisper.py` already sets one, so a persistent 403 means a bad key.
- **Groq rate limits** retry twice and then error out. Re-run with `--whisper openai`.
- **Comparing the wrong two frames** gives a confident wrong answer: `motion.py` on frames from different shots reports a cut, but on frames of the same subject in a new position reports a wild direction. Compare adjacent frames from one shot, and use `--seq` when you are unsure where the shot boundaries are.
- **Slow motion needs a wider step.** Two frames 0.5s apart of a person turning barely differ, and you get `in-place`. Raise `--step` until the pairs show movement, then report the step you used.
- **Two subjects moving opposite ways** cancel into a low-confidence or `in-place` verdict — the measure is of net change, not of each object. Isolate one subject with `--start`/`--end` on a tighter window, or read the frames.
- **Videos over ~30 min** are worth confirming with the user before running: the budget is bounded, but a sparse scan of an hour of footage is rarely useful — running on the specific section almost always beats it.

## Do not

- Invent video content from a title or thumbnail. If the pipeline fails, say so.
- Summarize before reading frames.
- Guess a direction that `motion.py` returned as `cannot-determine`, or quote a low-confidence bearing as fact.
- Skip cleanup.
- Reach for this pipeline when a transcript answers the question — see tier 1.

## Resources

- `scripts/watch.py` — the pipeline entry point and report printer.
- `scripts/download.py` — yt-dlp download + caption fetch.
- `scripts/frames.py` — ffprobe metadata, auto-fps budgets, frame extraction.
- `scripts/transcribe.py` — VTT parsing and range filtering.
- `scripts/whisper.py` — Groq/OpenAI transcription, API key and env loading.
- `scripts/motion.py` — frame-to-frame direction measurement: pair mode, `--seq` over a frame dump, `--json`.
- `scripts/selftest.py` — regenerates eight known-motion frames and asserts `motion.py`'s verdicts.
- `scripts/setup.py` — `--check` preflight, `--json` status, dependency install and `~/.config/watch/.env` scaffolding.
- `THIRD_PARTY_NOTICES.md`, `LICENSE` — vendored MIT attribution. Keep them with the scripts.
