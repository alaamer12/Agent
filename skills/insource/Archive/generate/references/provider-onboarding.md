# Provider Onboarding Guide

The `generate` engine is generic; providers are **data**. This guide explains how to add new image or video vendors to `data.csv` without engine modifications unless a brand-new payload builder is required.

## Registry Schema (`data.csv`)

| Column | Type | Purpose |
|---|---|---|
| `provider_id` | string | Short vendor identifier (e.g. `kovapi`, `xai`, `gemini`). May appear twice if providing both `image` and `video`. |
| `media` | `image` or `video` | Disambiguates rows and routes jobs to the correct API. |
| `priority` | integer | Provider fallback ranking (lower numbers tried first when keys are available). |
| `base_url` | url string | Provider base REST API endpoint. |
| `auth` | JSON | Header name, format string, and recognized environment variables. |
| `endpoints` | JSON | Paths for generation, editing, polling, usage, and models. |
| `request` | JSON | Builder name (`openai_json`, `gemini_json`, `gemini_omni`), mode (`sync`, `submit-poll`), param mappings, value maps, and default payloads. |
| `response` | JSON | JSON path pointers to extract job IDs, status strings, success/failure markers, URLs, and base64 payloads. |
| `features` | JSON | Declared capabilities: `t2i`, `i2i`, `t2v`, `i2v`, `edit`, `duration`, `n`, `max_ref_images`, `max_concurrent`, `result_expiry_days`. |
| `models` | JSON | Default model name, list of known models, allowed resolutions, aspect ratios, and durations. |
| `pricing` | JSON | Billing unit (`per_image`, `per_second`, `per_clip`), credit conversion rates, model rate card, and notes. |
| `docs` | url string | Primary vendor documentation link. |
| `status` | string | Honest verification badge (e.g. `documented (2026-11-09)`, `user-verified (2026-10-21)`). |
| `valid_as_of` | date string | `YYYY-MM-DD` timestamp of when the row was last checked. |
| `notes` | string | Quirks, retention policies, and API nuances. |

## The Seven Questions for Onboarding a Vendor

1. **Media Type**: Does this row serve `image` or `video`?
2. **Auth Scheme**: Header name (`Authorization`, `x-goog-api-key`) and environment variables.
3. **Execution Mode**: Synchronous (response contains final bytes/URL) or asynchronous (`submit-poll` with job ID)?
4. **Parameter Names**: Does the vendor expect `size`, `aspect_ratio`, `resolution`, `duration`, `quality`, or `n`?
5. **Input Formats**: How are reference images accepted? Data URL, raw base64 string, URL object (`{"url": "..."}`), or multipart?
6. **Result Durability**: How long do result URLs remain valid? (Immediately downloaded by the engine).
7. **Billing Model**: Per-image, per-output-second, per-clip, or token-based?
