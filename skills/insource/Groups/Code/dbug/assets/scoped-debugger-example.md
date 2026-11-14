# Pattern: a scoped, dev-gated debug facility

The universal shape of "controlled instrumentation": one tiny module,
inert unless explicitly enabled, addressable per service/module. Adapt
the syntax to the project's language — the *pattern* is the point.

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
    isProd        = env[PRODUCTION_ENV_VAR] == production  # NODE_ENV / APP_ENV / …
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

## Python example

```python
# debug_util.py
import os, sys
from datetime import datetime, timezone

PROD_ENVS = {"production", "prod", "staging"}
_SCOPES = {s.strip() for s in os.environ.get("DEBUG", "").split(",") if s.strip()}

def make_debugger(scope: str):
    enabled = (
        os.environ.get("APP_ENV", "") not in PROD_ENVS
        and ("*" in _SCOPES or scope in _SCOPES)
    )
    def debug(*args):
        if not enabled:
            return
        ts = datetime.now(timezone.utc).isoformat()
        print(f"[{ts}] [{scope}]", *args, file=sys.stderr)
    return debug
```

```python
from debug_util import make_debugger
debug = make_debugger("orders-module")
debug("checkout started", {"orderId": order_id, "step": "validate"})
```

## Go example

```go
// package debug — env-gated scoped logger
package debug

import (
    "log"
    "os"
    "strings"
)

var scopes = map[string]bool{}
var prod bool

func init() {
    env := os.Getenv("APP_ENV")
    prod = env == "production" || env == "prod" || env == "staging"
    for _, s := range strings.Split(os.Getenv("DEBUG"), ",") {
        if s = strings.TrimSpace(s); s != "" {
            scopes[s] = true
        }
    }
}

func New(scope string) func(format string, v ...any) {
    on := !prod && (scopes["*"] || scopes[scope])
    return func(format string, v ...any) {
        if !on {
            return
        }
        log.Printf("["+scope+"] "+format, v...)
    }
}
```

```go
debug := dbg.New("orders-module") // quiet unless DEBUG=orders-module
debug("checkout started step=%s", "validate")
```

## Running it

```bash
DEBUG=orders-module <project's dev command>   # only orders-module prints
DEBUG=* <project's dev command>               # everything prints (still dev-only)
<project's prod start>                        # prod: silent no matter what — inert by construction
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
