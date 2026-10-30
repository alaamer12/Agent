# Pattern: a scoped, dev-gated debug facility

The universal shape of "controlled instrumentation": one tiny module,
inert unless explicitly enabled, addressable per service/module. Adapt the
syntax to the project's language — the *pattern* is the point.

## Contract

```
- inert in production by construction (env check, not memory check)
- enable globally:   DEBUG=*
- enable by scope:   DEBUG=service-a,orders-module   (only these print)
- output carries:    scope, timestamp, correlation id if present
- no secrets:        values printed are chosen by the developer, and a
                     redact helper exists for the near-misses
```

## Pseudocode (any runtime)

```pseudocode
function makeDebugger(scope):
    enabledScopes = parseList(env["DEBUG"] or "")          # "a,b" or "*"
    isProd        = env["NODE_ENV" | "APP_ENV"] == production
    enabled       = not isProd and (isIn("*", enabledScopes) or isIn(scope, enabledScopes))

    return function debug(...args):
        if not enabled: return                # zero cost path when off
        print(format(timestamp, scope, args) with redaction applied)
```

## TypeScript example

```typescript
// src/debug.ts — the only debug primitive the codebase needs
const PROD_ENVS = new Set(["production", "prod", "staging"]);
const SCOPES = (process.env.DEBUG ?? "").split(",").map((s) => s.trim()).filter(Boolean);

export function createDebugger(scope: string) {
  const enabled =
    !PROD_ENVS.has(process.env.NODE_ENV ?? "") &&
    (SCOPES.includes("*") || SCOPES.includes(scope));

  return (...args: unknown[]) => {
    if (!enabled) return;
    console.log(`[${new Date().toISOString()}] [${scope}]`, ...args);
  };
}

export const redact = (v: unknown) => "<redacted>"; // use for tokens/PII fields
```

```typescript
// usage — scoped, so you can debug Service B without drowning in Service A
import { createDebugger } from "./debug";
const debug = createDebugger("orders-module");

debug("checkout started", { orderId, step: "validate" }); // quiet unless DEBUG=orders-module
```

```bash
DEBUG=orders-module npm run dev      # only orders-module prints
DEBUG=* npm run dev                  # everything prints (still dev-only)
npm start                            # prod: silent no matter what — inert by construction
```

## Rules of use during an investigation

- Place calls at the **pipeline midpoints** you picked to halve the search
  space — one per experiment, not one per line.
- Log the four things worth logging: input at the hop, output at the hop,
  state delta, identifiers for correlation. Everything else is noise.
- Temporary high-volume dumps for one question only? Fine in `tmp/`
  scripts (their prints can be raw); **never** in shared source files —
  shared source gets the gated call or nothing.
- At session end the calls may stay (they're cheap and useful next time)
  — this is the "instrumentation can remain" allowance; what must not
  remain are ungated prints.
