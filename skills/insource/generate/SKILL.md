---
name: generate
description: "Universal image AND video generation via RESTful providers (xAI, OpenAI, Gemini, KovAPI/NezhaGate) through registry data.csv: vendors and media types are data rows. Encapsulated per-media docs (media/image.md, media/video.md). Shared engine: concurrent --batch N with progress bar; --variations; --prompts-file; persistent context (--context new|<id>, seed with --context-seed); image inputs auto-encoded; video duration/fps; billing via usage.jsonl ledger; atomic download with results.jsonl for --salvage; keys masked. Triggers: generate, generate image, generate video, text-to-video, image-to-video, batch images, edit image, genimage, kovapi, nezha."
metadata:
  version: "3.0"
  valid-as-of: "2026-11-09"
  registry: data.csv
---

# Generate — universal, registry-driven image and video generation

One engine (`scripts/generate.py`, stdlib-only) + one registry (`data.csv`,
one row per provider **per media type**) = works with any RESTful image or
video vendor, aggregators included. The engine speaks a small set of request
*builders* (`openai_json`, `gemini_json`, `gemini_omni`); a vendor that matches
one is pure data — no code. New request shapes get a builder, never a redesign
(`references/provider-onboarding.md`).

**Token discipline:** this file is the router. Load only the media and
provider files the current job needs.

| Need | Read |
|---|---|
| Generate/edit an **image** | `media/image.md` |
| Generate/edit a **video** | `media/video.md` |
| One vendor's verified endpoints, models, quirks | `providers/<id>.md` |
| Add a provider / understand `data.csv` | `references/provider-onboarding.md` |
| Cost, billing, content-safety rules | `references/billing-and-safety.md` |
| Expiring links, `--salvage`, ledgers | `references/result-durability.md` |
| Prompt craft for UI icons, heroes, clips | `media/image.md`, `media/video.md` (sections) |
| Superseded v1 scripts | `legacy/` (read only if asked) |

**API validity:** registry rows carry `status` + `valid_as_of`. Re-verify a row
(or search the vendor's current docs) before trusting it past ~30 days —
endpoints and model IDs move.

## Permission gate (mandatory)

Before the first generation in a session: ask once — *"I can generate images
and video via the available providers (`--list-providers` shows which keys
exist). Batches and edits cost real credits. May I proceed when assets are
needed?"* Wait for an explicit yes; cache consent for the session. Never
generate without it. When pricing is known, state the expected spend for the
planned batch before running.

## Quick start

```bash
python scripts/generate.py --list-providers                      # registry, media, and which keys are present (masked)
python scripts/generate.py --prompt "flat icon for settings, minimal, indigo" --out assets/settings-icon.png
python scripts/generate.py --media video --prompt "slow orbit around a ceramic mug, studio light" --duration 5 --out assets/mug.mp4
python scripts/generate.py --media video --image first-frame.png --prompt "the camera pushes in" --out assets/scene.mp4
python scripts/generate.py --prompt "mug variants" --batch 30 --concurrency 10 --out assets/mugs/
python scripts/generate.py --media video --prompts-file shots.txt --duration 5 --out clips/
python scripts/generate.py --context new --system "Assets for brand X: flat, 2 colors" --prompt "logo mark"
python scripts/generate.py --context a1b2c3d4 --prompt "now make it monochrome"
python scripts/generate.py --prompt "match this style" --image ref.png --image https://…/logo.png
python scripts/generate.py --edit --image photo.png --prompt "remove the background" --provider openai
python scripts/generate.py --usage --provider kovapi
python scripts/generate.py --media video --prompt "check payload" --duration 5 --dry-run
```

## Media routing

| Media | Default output | Required flags | Extra params | Details |
|---|---|---|---|---|
| `image` | `.png` | `--prompt` | `--size`, `--resolution`, `--quality`, `--variations`, `--edit` | `media/image.md` |
| `video` | `.mp4` | `--prompt` | `--duration`, `--fps`, `--size` (aspect), `--resolution`, `--image` (first frame) | `media/video.md` |

`--media` defaults to `image`. `--video` is a shortcut for `--media video`.
A provider row declares which media it serves; the engine never sends an image
request to a video-only row (or vice versa).

## Shared flag contract

| Flag | Behavior |
|---|---|
| `--provider / --model` | Pin the row and model. Omitted: ranking below picks one that has a key and covers the media. |
| `--size / --resolution / --quality` | Universal params; the row's `param_map` + `value_maps` translate them (`size`→`aspect_ratio` on xAI, `1080P`→`1080p`). Unsupported params are dropped, never faked. |
| `--variations N` | N results per prompt: provider-side `n` when the row supports it, else client-side fan-out. |
| `--batch N --concurrency C` | N requests total (repeats of `--prompt`, or lines of `--prompts-file`), run concurrently, capped by the row's `max_concurrent`. Live bar; final table `# job media model status time cost output error`; exit 1 if any failed. |
| `--context new/<id>` `--system` `--label` | Persistent context in `.generate/contexts/<id>.json`; turns are `[system, user(+inputs), assistant(+outputs, params, result)]`. Continuing folds recent turns into the request and replays prior outputs as references (up to the row's `max_ref_images`). Multi-process safe: advisory lockfile (`O_EXCL`, stale-broken at 30 s, busy-fails after `GENERATE_LOCK_TIMEOUT`, default 15 s), merge-append against disk, atomic `os.replace`. |
| `--context-seed <id>` | Creates or seeds an explicit context ID with initial turns, system prompt, and repeatable `--image` inputs (local files or URLs, auto-encoded to Base64) without requiring a live generation call. Builds ready-to-use contexts immediately. |
| `--batch-context` | With `--batch`: every request forks from the **same snapshot**; one summary turn is appended when the batch lands. Without it each job gets its own fork (`<id>-j3.json`). |
| `--image` (repeatable) | URLs and/or local files → base64/files in the row's declared `image_format` (`data_url`, `b64`, `inline_b64`, `object_url`, `multipart`), trimmed to `max_ref_images`. For video this is usually the first frame / reference still. Rejected up front when the row declares no image input. |
| `--edit` | Routes to the row's edit endpoint. Hard error listing providers that support editing when the chosen row does not. |
| `--api-key` | Explicit key; needs `--provider`. Displayed **masked only**; env vars preferred; never echoed in stdout/table/ledger. `--dry-run` prints `<redacted>`. |
| `--usage` | GET the row's usage endpoint (feature-gated) — balance/credits/tokens. |
| `--out / --out-dir / --name-format` | `--out` = file (single job, when it carries a media extension) or directory; `--out-dir` forces directory mode. In dir mode names come from `--name-format` — `{slug} {index} {n} {provider} {model} {ext} {media} {date} {time} {ts}` (default `{slug}-{index}.{ext}`). URL results are downloaded atomically (temp file → `os.replace`); `--no-download` keeps URLs. |
| `--json / --plain / --dry-run` | Machine output / no animation (CI) / redacted request preview. |
| `--salvage` | Re-download any result whose file is missing or failed, **from `.generate/results.jsonl`**. Dead links are reported unrecoverable (rc 1) and the attempt is recorded. |

## Choosing a provider

Prefer: the user's explicit choice → a row for the requested media whose
`features` cover the job (`edit`, `i2i`/`i2v`, `n`, `duration`, big-batch
`max_concurrent` — see `--list-providers`) → registry `priority` among rows
with a key present. Gateways (KovAPI, formerly NezhaGate) put many models behind one key
and expose usage; direct vendors may offer models or quality a gateway lacks.
For video, prefer the vendor whose documented duration/resolution limits match
the requested clip. Check `status`/`valid_as_of` before trusting a row — an
unverified format is labeled unverified in `notes`.

## Billing & keys (summary)

- Every request appends `.generate/usage.jsonl`: provider, media, model, job,
  cost string, raw provider usage, outputs, error. Quote the ledger, not memory.
- Cost column: provider-reported credits × `credit_usd` when present, else the
  row's `rates` estimate (`~$0.1200`), else `n/a` — never invent a number.
  Video rows are usually `per_second` (rate × seconds) or `per_clip`.
- Keys live in env per row (`NEZHA_API_KEY`/`KOVAPI_API_KEY`, `XAI_API_KEY`,
  `OPENAI_API_KEY`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`). No key material in
  stdout, tables, ledger, dry-run, or errors.
- Never upload user media anywhere except the selected provider. Refusals are
  recorded as failed jobs; prompts are not laundered.

Full rules: `references/billing-and-safety.md`.

## Result durability (summary)

The instant a job returns, raw result URLs are appended to
`.generate/results.jsonl` (`kind: received`) **before** any download; the
completion record (`kind: done`) pairs each URL with its file. A crash
mid-download loses nothing; expiring links stay recoverable while alive
(`--salvage`); dead links are reported as unrecoverable rather than papered
over. The run is only "done and happy" when every recorded URL has a file or an
honest failure row. Full detail: `references/result-durability.md`.

## Verification (keyless)

`tests/mock_provider_test.py` runs local mocks of the image flow
(submit → poll → download) and the video flow and asserts the contract —
single, batch, mixed failure, context, batch-context vs forks, image inputs,
key masking/non-leak, ledger, registry parse — **with zero real API keys**.
`tests/registry_dryrun_eval.py` pushes every real `data.csv` row through
`--dry-run` for both media. Run both after touching the engine or registry:

```bash
python tests/mock_provider_test.py <skill-dir> <scratch-workdir>
python tests/registry_dryrun_eval.py
```

## Adding a provider

New aggregator = one `data.csv` row per media it serves (read its docs first —
search, don't remember). Same builder family → zero code. Different request
shape → add a builder and say so in the row. Schema, the vendor questions, and
honest `status` labels: `references/provider-onboarding.md`. Never mark a row
`user-verified` or `tested` unless its flow was actually run.

## References & legacy

- `media/image.md`, `media/video.md` — flags, parameters, selection, prompts.
- `providers/kovapi.md`, `providers/xai.md`, `providers/openai.md`,
  `providers/gemini.md` — verified per-vendor detail.
- `references/provider-onboarding.md`, `references/billing-and-safety.md`,
  `references/result-durability.md`.
- `legacy/` — pre-3.0 image-only scripts and notes; superseded, kept for
  reference.
