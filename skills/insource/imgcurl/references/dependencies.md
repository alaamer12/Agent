# Dependencies & Environment

## Required packages

```
playwright
curl_cffi
Pillow
```

Install:

```bash
pip install -r scripts/requirements.txt
python -m playwright install chromium
```

On headless CI or restricted containers you may also need the system dependencies that Playwright’s `--with-deps` flag installs (libnss3, libatk, etc.). Prefer the official Playwright install command over manual package lists.

## Why curl_cffi?

Many modern CDNs and publishing platforms (Medium in particular) fingerprint TLS handshakes. Plain `requests` or `httpx` often receive 403s on the original high-resolution asset URLs. `curl_cffi` with `impersonate="chrome120"` supplies a matching JA3 fingerprint and succeeds where ordinary clients fail. The script therefore uses it both for the GraphQL route handler and for the final “upgrade to original” fetch.

## Why Playwright?

- Reliable scroll + network-idle semantics.
- Access to the live DOM for text-position search.
- Ability to intercept and re-route GraphQL through curl_cffi without an external proxy.

## Runtime notes

- Default viewport is 1280×800.
- User-Agent is a recent Chrome string.
- `--disable-blink-features=AutomationControlled` is set to reduce simple bot detection.
- The overall `--timeout` is a hard wall-clock deadline checked at every major stage; the process raises `TimeoutError` when it is exceeded.
