# genimage — provider onboarding (adding any vendor as a registry row)

The engine is generic; a provider is **data**. This file is the contract for
growing `data.csv` with a new aggregator or direct vendor — no engine changes
unless its request shape matches no existing builder.

Standing rule inherited from the skill's ethos: when you onboard, **read the
vendor's current docs by searching** (their docs page, an OpenAPI spec,
context7 if installed) — never fill the row from remembered API shapes. A
row is a claim with an expiration date.

## The six questions to answer from any vendor's docs

1. **Auth** — header name(s), scheme, env var convention(s) → `auth` column.
2. **Shape** — is submit synchronous (image in the response) or a job you
   poll (or webhook)? Job id / status / result locations in the JSON →
   `request.mode` + `response` paths.
3. **Parameters** — what do they call aspect ratio, resolution, quality,
   count? What values are legal? → `request.param_map` + `value_maps`
   (universal name → provider name / value; omit or `null` = unsupported).
4. **Features** — text→image? image inputs (how many)? dedicated edit route?
   native `n`? concurrent-job cap? usage/balance endpoint? result URL
   expiry? → `features` booleans/numbers (the engine gates on these instead
   of letting jobs fail at the API).
5. **Money** — per-image rate? credits math? are failures refunded? what
   does the usage object contain? → `pricing`.
6. **Image encoding** — do they want `data:image/png;base64,…` URLs, raw
   b64 strings, `multipart` file uploads, or an inline-parts object? →
   `request.image_format` (`data_url` | `b64` | `multipart` | `inline_b64`).

## Column reference (`data.csv`)

| Column | Type | Notes |
|---|---|---|
| `provider_id` | str | kebab-case; used with `--provider` |
| `priority` | int | auto-selection order among rows with env keys present (lower = first) |
| `base_url` | URL | no trailing slash required (engine strips it) |
| `auth` | JSON | `{"header","format":"Bearer {key}" or "{key}","env":[names]}` |
| `endpoints` | JSON | keys: `generate` (required), `edit`, `poll` (must contain `{id}`), `usage`, `models`. Path templates may contain `{model}` (gemini style). |
| `request` | JSON | `builder` (`openai_json`/`gemini_json`), `mode` (`sync`/`submit-poll`), `param_map`, `value_maps`, `image_field`/`edit_image_field`, `image_format`, `extra_defaults` |
| `response` | JSON | path extraction: `job_id_path`, `status_path`, `succeeded`/`failed` (lists of status values), `error_path`, `urls`/`b64` (lists of dotted paths), `parts_path` (gemini-style image parts), `usage_path` |
| `features` | JSON | `t2i, i2i, edit, n, usage_endpoint, max_ref_images, max_concurrent, result_expiry_days` — engine enforces these |
| `models` | JSON | `default` + `known` list |
| `pricing` | JSON | `unit`, `rates` (`model` or `model|resolution` → USD), `credit_usd` if credits-based, `notes` |
| `docs` | URL | vendor API docs |
| `status` | label | **honesty ladder**: `documented` (transcribed from docs, not run) → `user-verified (<what, when>)` (a human ran the core flow) → `tested` (full row incl. i2i/edit formats exercised). Mark what was and wasn't verified inside the string. |
| `valid_as_of` | date | re-verify after ~30 days |
| `notes` | str | quirks the engine can't express |

Dotted-path syntax: `data[0].url`, `candidates[0].content.parts` — resolved
tolerantly (missing → None, never a crash).

## When no builder fits

`openai_json` covers any REST/JSON vendor whose create-request is a flat
`{prompt, model, ...}` dict (the OpenAI-compatible family most aggregators
imitate). `gemini_json` covers nested-`contents` styles. A vendor outside both
(e.g., XML, form-encoded creates, webhook-only completion): add a builder
function in `scripts/genimage.py` (`BUILDERS` dict) — ~20 lines, keeping the
same signature `(row, prompt, model, params, images_enc, n, edit) -> body`.
That is the extension point; nothing else in the engine changes.

## Onboarding procedure

1. Search + read the vendor's current API docs (their words, not yours).
2. Answer the six questions above; write the row.
3. `python scripts/genimage.py --registry <path> --provider <new> --prompt "smoke" --dry-run`
   — inspect the mapped payload; fix `param_map` until it's right.
4. One **real** generation (smallest/cheapest tier) → confirm download,
   status handling, usage capture. Upgrade `status` accordingly, quoting
   what was verified.
5. If the vendor has an async flow, exercise a failing prompt once (bad
   model name) — confirm the error row lands in the table and ledger, exit 1.
6. Add the human-readable details to `references/providers.md` if useful.

## Growing the registry safely

- Rows never overwrite each other's lessons: keep per-row `notes`/`status`.
- If a vendor changes shape (breaking docs update): **update the row, bump
  `valid_as_of`, downgrade `status`** to `documented` until re-run.
- A provider that needs auth the env convention can't express: extend the
  `auth` JSON schema (e.g. `api_key_param` for query-string vendors) — the
  engine should read it generically; hardcoding a vendor name in engine code
  is the design smell this registry exists to prevent.
