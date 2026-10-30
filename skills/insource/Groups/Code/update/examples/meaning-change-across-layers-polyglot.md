# A Meaning Change Across Layers: Upload Limit 10 MB -> 25 MB - Polyglot Walkthrough

**Principle (Update skill):** when a *fact* changes, everything that states, enforces, quotes, or derives from it is affected - often under different names, in different units, and in different languages. This is the case where an exact-string search finds the least.

**Scenario.** The maximum file upload size goes from 10 MB to 25 MB. This is not a bug fix; the old value was correct, it simply changed.

## 0. Claim and vocabulary

> Old: uploads are limited to 10 MB -> New: 25 MB. Meaning change.

Search vocabulary for the *value*: `10`, `10 MB`, `10MB`, `10 Mo`, `١٠ ميغابايت`, `10485760` (bytes), `10 * 1024 * 1024`, `ten megabytes`.
Search vocabulary for the *concept*: `MAX_UPLOAD_MB`, `maxFileSize`, `upload_limit`, `sizeCap`, `MaxRequestBodySize`, `client_max_body_size`, `file too large`, `413`.

## 1. The same concept under different names

```typescript
// web/src/config/limits.ts
export const MAX_UPLOAD_MB = 10;
```
```python
# api/settings.py
UPLOAD_LIMIT_BYTES = 10 * 1024 * 1024
```
```go
// internal/upload/limits.go
const MaxFileSize = 10 << 20
```
```rust
// crates/upload/src/limits.rs
pub const MAX_BODY_BYTES: usize = 10_485_760;
```
```csharp
// Program.cs
options.Limits.MaxRequestBodySize = 10 * 1024 * 1024;
```

Five layers, five names, three notations of the same number (`10`, `10 * 1024 * 1024`, `10_485_760`). A search for `10 MB` finds none of them. Search by concept and by each numeric form, then decide per occurrence whether it is the same limit or a coincidence (a 10-second timeout is not an upload limit).

After updating, check whether one layer should *derive* from another (client reads the server's limit) and **propose** that; do not restructure as part of the content change.

## 2. Infrastructure and config (easy to forget, fail late)

```nginx
# nginx.conf
client_max_body_size 10m;
```
```yaml
# deploy/ingress.yaml
nginx.ingress.kubernetes.io/proxy-body-size: "10m"
# .env.example
UPLOAD_MAX_MB=10
```

If the application accepts 25 MB but the proxy still rejects at 10 MB, the change "works in tests and fails in production". These are part of the claim.

## 3. User-facing text in every language

```jsonc
// locales/en/upload.json
{ "hint": "Maximum file size: 25 MB", "error": "File is too large (max 25 MB)." }
// locales/fr/upload.json - French writes the unit "Mo"
{ "hint": "Taille maximale : 25 Mo", "error": "Le fichier est trop volumineux (25 Mo max)." }
// locales/ar/upload.json - follow the file's numeral convention (Western or Arabic-Indic digits)
{ "hint": "الحد الأقصى لحجم الملف: 25 ميغابايت", "error": "الملف كبير جدًا (الحد الأقصى 25 ميغابايت)." }
```

Better still, if the project's strings already take a placeholder (`{{max}}`), the number should come from the constant and the locale files need no edit at all. When they hard-code the number, update each locale and **mention** the placeholder option to the owner.

## 4. Documentation, API description, comments

```yaml
# openapi.yaml
description: "Upload a document. Files larger than 10 MB are rejected with 413."
```
```text
README.md        "Files up to 10 MB"
docs/faq.md      "Why can't I upload a 12 MB video?" (the answer and the example both change)
// comment         // 10 MB hard cap, see nginx.conf
```

Paraphrases count: `ten megabytes`, `about 10 megs`, `anything under the 10-meg limit`. Search the word forms, not only digits.

## 5. Tests and fixtures

```typescript
// before: rejects an 11 MB file
expect(validate(fileOfSize(11 * MB))).toBe("too_large");
// after: boundary moves; add/adjust both sides of the new boundary
expect(validate(fileOfSize(25 * MB))).toBe("ok");
expect(validate(fileOfSize(26 * MB))).toBe("too_large");
```

This test exists to protect a business rule, so confirm the new boundary is intended before rewriting it (see `classify-and-verify.md`); never loosen a test just to make it green.

## 6. Classification of what the sweep returned

| Hit | Decision |
|-----|----------|
| Constants/limits in each service, proxy config, ingress, `.env.example` | Update |
| Locale strings (all languages), error messages | Update |
| OpenAPI, README, FAQ, comments | Update |
| Unit/integration tests on the boundary | Update after confirming the rule |
| `CHANGELOG.md` "0.9: limit uploads to 10 MB" | **Leave**; add a new entry for 25 MB |
| Terms of Service: "files up to 10 MB" | **Flag**, legal text; propose wording |
| Pricing page table "Upload size: 10 MB (Free)" | **Ask** if this is a plan limit that should change for Free only |
| Support macro, help-center article in a third-party tool | **Needs a human** |
| `timeoutSeconds = 10` in the same files | Out of scope (coincidence) |
| Existing rows/records with stored limits (per-tenant overrides) | **Ask**, production data |

## 7. Verify

```bash
rg -n -i -e "\b10\s?(MB|Mo)\b" -e "10485760|10 << 20|10 \* 1024 \* 1024|10m\b|ten megabytes" -e "MAX_UPLOAD_MB|maxFileSize|upload_limit"
python scripts/sweep.py --term "10 MB" --term "10485760" --term "MAX_UPLOAD_MB"
python scripts/locale_parity.py --root web/src/locales --grep "10"
```

Every remaining hit is history, flagged, or a coincidence you can name. Then run the boundary tests and an end-to-end upload at 24 MB and 26 MB against the real proxy configuration if the environment allows.

## Key points

- Meaning changes spread through *units, notations, names, and languages*; search the concept, not just the literal.
- Enforcement points (client, server, proxy) must agree or the change is half-applied.
- Legal text, pricing tables, production data, and third-party tools are decisions or hand-offs, not silent edits.
- Coincidental matches (`10` as a timeout) are excluded by relationship to the claim, not by pattern.
