---
name: genimage
description: "Universal image generation through any RESTful provider — xAI, OpenAI, Gemini, or OpenAI-compatible gateways (NezhaGate, Apidot, newer) — via a growing provider registry (data.csv): a new vendor is a row, not a redesign. Concurrent --batch N with progress bar + state table; --variations, --prompts-file; persistent context (--context new|<id> saves system+user+assistant turns, replays prior images as references; --batch-context shares one base; locked merge-append is multi-process safe); image inputs from URL or file, base64 per provider format; --edit only on providers whose row declares support; billing via provider usage, credit/token estimates, --usage, usage.jsonl ledger; result URLs recorded at receipt in results.jsonl before download, --salvage restores lost files; keys from env or --api-key, masked, never logged. Use to generate, batch-generate, edit, or iterate images/assets in any stack. Triggers: genimage, generate image, batch images, edit image, nezha apidot."
metadata:
  version: "2.0"
  valid-as-of: "2026-10-21"
  registry: data.csv
---

# GenImage — universal, registry-driven image generation

One engine (`scripts/genimage.py`, stdlib-only) + one growing registry
(`data.csv`, one row per provider) = works with **any RESTful image vendor**,
aggregator gateways included. The engine speaks a small set of request
*builders* (`openai_json`, `gemini_json`); a vendor that matches one is pure
data — no code. New vendor shapes get a builder, never a redesign
(`references/provider-onboarding.md`).

**API validity:** registry rows carry `status` + `valid_as_of` columns.
Re-verify a row (or search for the vendor's current API) before trusting it
past ~30 days — endpoints and models move.

## Permission gate (mandatory)

Before the first generation in a session: ask once — *"I can generate images
via available providers (check `--list-providers`); batches and edits cost
real credits. May I proceed when images are needed?"* Wait for explicit yes;
cache consent for the session. Never generate without it. State the expected
cost for the planned batch size when known (pricing column + `--usage`).

## Quick start

```bash
python scripts/genimage.py --list-providers                 # registry + which keys are present (masked)
python scripts/genimage.py --prompt "flat icon for settings, minimal, indigo" --out assets/settings-icon.png
python scripts/genimage.py --prompt "hero banner" --size 16:9 --resolution 4K --provider nezha-gate --model gpt-image-2.5-sunburst
python scripts/genimage.py --prompt "mug variants" --batch 30 --concurrency 10 --out assets/mugs/   # parallel, progress bar + state table
python scripts/genimage.py --prompts-file ideas.txt --out assets/set/                              # one request per line
python scripts/genimage.py --context new --system "You design assets for brand X: flat, 2 colors" --prompt "logo mark"
python scripts/genimage.py --context a1b2c3d4 --prompt "now make it monochrome"                     # iterates with saved history
python scripts/genimage.py --context a1b2c3d4 --batch-context --prompt "poster" --batch 3 --out posters/
python scripts/genimage.py --prompt "match this style" --image ref.png --image https://…/logo.png    # URL or file → base64 per format
python scripts/genimage.py --edit --image photo.png --prompt "remove the background" --provider nezha-gate
python scripts/genimage.py --usage --provider nezha-gate                                             # balance/credits
python scripts/genimage.py --prompt "check payload" --dry-run                                        # redacted preview, mapped params
```

## The flag contract

| Flag | Behavior |
|---|---|
| `--provider / --model / --size / --resolution / --quality` | Universal params; the row's `param_map` + `value_maps` translate them (e.g. `size`→`aspect_ratio` on xAI). Unsupported universal params are dropped, not faked. |
| `--variations N` | N images per prompt: provider-side `n` when the row supports it, else client-side fan-out. |
| `--batch N` `--concurrency C` | N requests total (repeats of `--prompt`, or lines of `--prompts-file`), run concurrently — capped by the row's `max_concurrent` (NezhaGate: 50). Live bar while running; final markdown table: `# job model status time cost output error`; exit 1 if any failed. |
| `--context new\|<id>` `--system` `--label` | Persistent context in `.genimage/contexts/<id>.json` — turns are `[system, user(+input images), assistant(+output images, params, result)]`. Continuing a context folds recent turns into the request AND replays prior generated images as style references (up to the row's `max_ref_images`). **Multi-process safe:** writes take an advisory lockfile (`O_EXCL`, stale-broken at 30s, busy-fails after `GENIMAGE_LOCK_TIMEOUT`, default 15s), merge-append the current disk history rather than overwrite it, and save via atomic `os.replace` — two terminals on one context keep both sessions' turns; concurrent writers never see torn files. `--context new` ids are collision-checked under the same lock. |
| `--batch-context` | With `--batch`: every request reads the **same snapshot** of the context as its base; one summary turn is appended when the batch lands. Without it, each job gets its own fork (`<id>-j3.json`) so branches can diverge. |
| `--image` (repeatable) | **Multiple** URLs and/or local files → base64 in the provider's declared `image_format` (`data_url`, `b64`, `inline_b64`, `multipart`), trimmed to the row's `max_ref_images`. Rejected up front if the row declares no image support. |
| `--edit` | Routes to the row's `edit` endpoint; hard error listing providers that do support it when one doesn't. |
| `--api-key` | Explicit key; needs `--provider`. Displayed **masked only** (`SK…999`), warned against in favor of env vars, never echoed in stdout/table/ledger. `--dry-run` shows `<redacted>` in place of auth. |
| `--usage` | GET the row's usage endpoint (feature-gated) — balance/credits/tokens. |
| `--out` `--out-dir` `--name-format` | `--out` = file (single job, when it has an image extension) or directory; `--out-dir` forces directory mode explicitly. In dir mode filenames come from `--name-format` — placeholders `{slug} {index} {n} {provider} {model} {ext} {date} {time} {ts}` (default `{slug}-{index}.png`). URL results are **downloaded atomically** — bytes land in a temp file, then `os.replace()` renames into the final name, so partial/corrupt files never appear at the destination (NezhaGate-class links expire anyway — download is the default; `--no-download` keeps URLs). |
| `--json / --plain / --dry-run` | machine output / no animation (CI) / preview. |
| `--salvage` | Re-download any result whose file is missing or failed, **from `.genimage/results.jsonl`** — never from memory. Dead/expired links are reported as unrecoverable (rc 1) and the attempt is recorded. |

## Choosing a provider

Prefer, in order: the user's explicit choice → a row whose `features` cover
the job (`edit`, `i2i`, `n`, `max_concurrent` for big batches — see
`--list-providers`) → registry priority among rows with a key in env
(`--api-key` overrides, still per-provider). Gateways (nezha-gate) route many
models through one key and expose usage; direct vendors may offer
provider-only quality or features. Check `status`/`valid_as_of` before
trusting a row — unverified formats are labeled as such in the notes column.

## Billing & usage discipline

- Every request appends a `.genimage/usage.jsonl` line: provider, model, job,
  cost string, **raw provider usage object**, outputs, error. The ledger is
  the audit trail — quote from it, not memory.
- Cost column: provider-reported credits × the row's `credit_usd` when
  present (NezhaGate: 1 credit = $0.005, failed jobs refunded); else the row's
  `rates` estimate (`~$0.0400`); else `n/a` — never invent a number.
- Before batches, state the expected spend if rates are known; for
  `--batch 30` on unknown-rate providers say "cost unmeasured — run 1 first".

## Adding a provider (the extensibility contract)

New aggregator = one `data.csv` row (read its docs first — search, don't
remember). Same builder family → zero code. Different request shape → add a
builder function and say so in the row. Full schema, the six questions to
answer from any vendor's docs, and honesty labels for `status`:
`references/provider-onboarding.md`. Never mark a row `user-verified` or
`tested` unless its flow was actually run.

## Result durability — URLs outlive the terminal

The moment a provider job returns, its raw result URLs are appended to
`.genimage/results.jsonl` (`kind: received`) **before any download starts**,
and the completion record (`kind: done`) pairs each URL with its saved file.
Consequences the agent must honor: a crash mid-download loses nothing (the
URLs are on disk); aggregator links that expire in 15 days are recoverable
while alive (`--salvage`); a `--salvage` on a dead link says "unrecoverable"
rather than pretending. The final summary always prints the manifest path —
the run is only "done and happy" when every recorded URL has a file (or an
honest failure row).

## Key & safety rules

- Keys live in env (`NEZHA_API_KEY`, `XAI_API_KEY`, `OPENAI_API_KEY`,
  `GEMINI_API_KEY`/`GOOGLE_API_KEY`, per row); `--api-key` exists for
  one-offs with masked display and a warning.
- No key material in stdout, tables, ledger, dry-run, or errors — enforced.
- Never upload user images to hosts other than the chosen provider.
- Generated images are the user's assets; respect each provider's content
  policy (a refusal is recorded as a failed job, prompt not laundered).

## Verification & evals (keyless)

`tests/mock_provider_test.py` runs a local mock of the NezhaGate-style flow
(submit → poll → download → usage) and asserts the full contract — single,
batch, mixed failure, context continuation, batch-context vs forks, image
base64 inputs, `--api-key` masking + non-leak, ledger, registry parse —
**with zero real API keys**. Run it after touching the engine or registry:

```bash
python tests/mock_provider_test.py <skill-dir> <scratch-workdir>
```

All pass as of 2026-10-21.

## References & legacy

- `references/provider-onboarding.md` — registry schema + how to add vendors.
- `references/providers.md` — human-readable provider detail (pre-2.0; the
  `data.csv` row is the source of truth when they disagree).
- `references/prompt-patterns.md`, `references/examples.md` — prompt craft.
- `scripts/gen_xai.py|gen_openai.py|gen_gemini.py|detect_keys.py` — legacy v1
  per-provider scripts; still work, superseded by the engine for
  batching/context/usage features.
