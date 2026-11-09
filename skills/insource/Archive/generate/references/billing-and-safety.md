# Billing & Safety Rules

## 1. Credit & Token Ledger
Every generation or editing job appends a record to `.generate/usage.jsonl`:
```json
{
  "timestamp": 1731150000,
  "job": "img-abc123",
  "provider": "kovapi",
  "media": "image",
  "model": "gpt-image-2.5-flare",
  "cost": "$0.0050",
  "provider_usage": {"credits": 1},
  "outputs": ["generate-out/icon-01.png"],
  "error": null
}
```
Always report costs and tokens from this ledger rather than guessing.

## 2. Cost Estimation
- When provider returns credits and the row defines `credit_usd`: `credits * credit_usd` (e.g. KovAPI $0.005 per credit).
- For per-second video generation: `rate_per_second * duration_in_seconds` (e.g. xAI Grok Imagine Video 1.5 is $0.08/s; a 10s video is ~$0.80).
- When a rate is configured in `pricing.rates`: reported as an estimated cost (e.g. `~$0.0400`).
- If no rate or credit data is available: reported honestly as `n/a`.

## 3. Key Hygiene & Zero Leakage
- API keys reside in environment variables (`KOVAPI_API_KEY`, `NEZHA_API_KEY`, `XAI_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, `GOOGLE_API_KEY`).
- When `--api-key` is supplied on the CLI, it is masked in all console output (`SK...999`) and dry-run previews display `<redacted>`.
- API keys are NEVER written to logs, tables, ledger files, or error tracebacks.

## 4. Safety & Content Policies
- Respect vendor moderation policies. If a request is rejected by safety filters, record the error honestly in `.generate/usage.jsonl` as a failed job.
- Never launder or alter user prompts to bypass moderation filters.
- Never upload user input media to third-party hosts other than the user-selected provider.
