# Real bugs this workflow found (check for each class)

Security / production leaks
- Debug/dev check written as `process?.env?.NODE_ENV !== "production"`: in browsers and Workers `process` is undefined, so it behaves as dev in production.
- Fixture-feed endpoint reachable in production with no guard.
- `?devMode=true` query flag calls dev-login with no environment check on the client.
- Test-only global (`window.__X_TEST_GOOGLE_ID_TOKEN__`) honored in production builds.
- Internal cache-purge endpoint with no secret check.
- Auth rate limiting disabled outside literal "production" so staging ran unprotected.
- Production allowed to boot with a fixture/mock upstream or a loopback upstream.

Origin / cookie / CORS
- `localhost` vs `127.0.0.1` split between surfaces: cookies not shared, CORS fails, handoff between sites lands on the wrong host. Fix with one alignLoopback used by every surface (it previously existed only in one app).
- Native WebView origins (`https://localhost`, `capacitor://localhost`) missing from production CORS.
- Native API client rewriting loopback requests because `isLoopback("localhost")` is true inside the WebView.
- Hardcoded cookie domain compare (`host.endsWith("example.com")`).
- Secure-cookie flag tied only to mode so local HTTP staging rehearsal drops cookies; tie to protocol.

Naming / drift
- `.env.example` documents `*_SITE_URL` while code reads `*_MARKETING_URL`.
- `*_CLIENT_ID` vs `*_WEB_CLIENT_ID` in mobile config.
- Orchestrator lists dead vars, misses ~20 live ones; build vars in pass-through instead of hashed list.
- Four separate `.env` parsers with different precedence; test runner hydrating the developer's real `.env`.

Bundler traps
- `Reflect.get(import.meta, "env")` / `import.meta.env?.[key]` break static replacement in production Vite builds, also inside shared packages.
- Static `index.html` with hardcoded OG/canonical URLs.

Business-literal drift
- Domains, support emails, copyright year inside translation JSON.
- Share/QR links built on the app origin instead of the public marketing origin.
- Contact-form mail sent to the no-reply address instead of support.

Incidental
- Route response wrapped twice by a helper; hostname extraction mishandling IPv6 `::1`; three duplicate test config mocks (merge into one env factory); default locale decided by browser language when product wants a fixed default (ask).
