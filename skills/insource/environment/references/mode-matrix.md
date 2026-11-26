# Mode and capability matrix (default; edit per user's confirmed decisions)

Four modes. Name the mode variable `<APP>_ENV`. `NODE_ENV` maps: dev -> development, test -> test, staging -> production, production -> production.

| Capability | dev | test | staging | production |
|---|:-:|:-:|:-:|:-:|
| isProdBehavior (strict auth, secure cookies, no debug) | no | no | **yes** | **yes** |
| allowDevShortcuts (dev-login, `?devMode=`, preview flags, debug overlay, A/B override flags) | **yes** | no | no | no |
| allowTestMocks (test outbox, fake ID tokens, test hooks) | no* | **yes** | no | no |
| allowLocalSeededData (local DB, fixture feeds/endpoints) | yes | yes | local only | **no** |
| enforceAuthRateLimit | no | no | **yes** | **yes** |
| exposeErrorDebug (`_debug` in error bodies) | yes | yes | no | no |
| allowLoopbackWildcardCors | yes | yes | no (declared origins + aligned loopback) | no |
| useSecureCookies | by protocol | by protocol | by protocol | always |
| loopback origins permitted | yes | yes | local rehearsal only on web; **never in mobile builds** | **never** |

\* Confirm with the user; some teams enable test mocks in dev too. Record the answer in the ADR.

## Forbidden-combination checks at boot (fail fast, forbidden-in-mode error)
- Fixture/mock upstream provider in production.
- Production upstream missing token or pointing at loopback.
- Loopback URLs in staging/production mobile builds.
- Missing required client ids (OAuth) in production.
- Secrets or weak secrets in client-exposed prefixes.

## Ergonomic helpers to export (names can follow repo style)
Mode: `isDev isTest isStaging isProd isProdBehavior isLocalRuntime`
Capability: `canUseDevShortcuts canUseTestMocks canUseLocalSeedData shouldRateLimitAuth shouldExposeErrorDebug`
URLs: `apiUrl marketingUrl appUrl adminUrl dbUrl publicProfileUrl appAuthUrl allowedCorsOrigins`
Loopback/cookies: `alignLoopback isLoopback cookieDomain shouldUseSecureCookies`
Business: `productName operatorName rootDomain canonicalOrigin supportEmail supportMailto partnershipsEmail noreplyEmail supportPhone mobileAppId deepLinkScheme legalIdentity`
Plus a namespace/object export (`Environment`) for places that need the whole thing, and `initEnvironment` / `getEnvironment` / `createEnvironment` for seams and tests.
