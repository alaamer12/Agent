# Polyglot Briefs — the three gates run end-to-end in three ecosystems

Same protocol, three paradigm families (TypeScript/managed-web, Rust/static-compiled, Python/dynamic-scripted). Each: situation -> Gate 1/2/3 -> the naive-memory code and the grounded code.

---

## 1. TypeScript + Ionic (mobile client)

*Situation:* "Add a debounced search field to the feed screen."

**Gate 1**
```
CODING BRIEF
scope      : mob client, feed search
stack      : TypeScript + Vue + Ionic
touches    : interfaces (Input component), input (keyboard), styling (look of filled variant)
docs need  : Ionic input API + keyboard guide + theming surfaces
```

**Gate 2** — root shows `bun.lock`; AGENTS.md mandates bun/bunx. Commands will be `bunx ionic g ...`, never `npm`.

**Gate 3** — cache exists (`scratch/docs-ionic/`):
```bash
grep -rln "debounce" scratch/docs-ionic/          # -> no input/component hit
grep -c 'css-properties\|CSS Properties' scratch/docs-ionic/api-input.md
```
Grounding result: **`ion-input` has no debounce option/property** — the docs silence IS the finding.

```typescript
// ❌ Anti-pattern: inventing an API from another framework's muscle memory (React MUI / Vuetify)
<IonInput v-model="q" :debounce="300" />

// ✅ Grounded: debounce is our layer's job; IonInput stays a base re-export,
//    composition happens in the component that owns the purpose.
const { debouncedQuery } = useDebounced(q, 300)   // our composable, our file
<IonInput v-model="q" fill="strong" />            // fill="strong" exists: api-input.md (Properties table)
```

---

## 2. Rust (backend worker)

*Situation:* "Preallocate the decode buffer, but fail gracefully instead of aborting when huge."

**Gate 1**
```
CODING BRIEF
scope      : OW worker, frame decoder buffer
stack      : Rust (edition 2024), cargo
touches    : interfaces (Vec allocation API), errors (capacity failure path)
docs need  : std::vec::Vec methods, alloc strategy docs
```

**Gate 2** — root shows `Cargo.lock` -> single toolchain: `cargo add`/`cargo run`. Nothing to guess.

**Gate 3** — std grounding (BFS-proven: `scrape --auto https://doc.rust-lang.org/std` capped-cache, or the single page):
```bash
grep -n "pub fn try_reserve" scratch/docs-std/stable/std/vec/struct.Vec.md   # hit: exists
grep -n "pub fn reserve_checked" scratch/docs-std/...                        # miss: invented - blocked
```

```rust
// ❌ Anti-pattern: a plausible-sounding API that does not exist
buf.reserve_checked(cap);   // compiles never; memory said so

// ✅ Grounded: try_reserve returns Result on capacity failure (struct.Vec.md, Methods table)
buf.try_reserve(cap).map_err(|e| DecodeError::OutOfMemory(e.with_capacity(cap)))?;
```
The `Errors` concern in the brief also fired: the grounding surfaced `try_reserve` (per-capacity) **vs** `try_reserve_exact` — a viable-choice trade-off -> per Gate 3 rule 3, ask the user which semantic they want, don't pick silently.

---

## 3. Python + FastAPI (admin tooling)

*Situation:* "Warm up the DB pool when the app starts, close it on shutdown."

**Gate 1**
```
CODING BRIEF
scope      : ops tool, FastAPI app lifespan
stack      : Python 3.12 / FastAPI
touches    : interfaces (app startup/shutdown API), concurrency (event loop lifecycle)
docs need  : FastAPI lifespan docs (tutorial subtree)
```

**Gate 2** — root shows `uv.lock` -> `uv add fastapi` / `uv run`, not pip.

**Gate 3** — the tutorial cache (proven: 51/51 pages) says the training-era pattern is **officially deprecated**:
```bash
grep -rln "lifespan" scratch/docs-fastapi/ | head -3
grep -n "on_event" scratch/docs-fastapi/tutorial/lifespan.md   # deprecation notice, [WARNING] block
```

```python
# ❌ Anti-pattern: the pre-2021 idiom every old snippet still shows
app = FastAPI()

@app.on_event("startup")          # deprecated; docs tutorial/lifespan.md
async def startup(): ...

# ✅ Grounded: lifespan context manager (tutorial/docs/lifespan.md)
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await open_pool()
    yield
    await app.state.pool.close()

app = FastAPI(lifespan=lifespan)
```

---

## What all three share

- The brief decided the doc target — never "the whole site" (debounce->input/keyboard, buffer->Vec methods, startup->lifespan page).
- Absence in the docs is an outcome: no `debounce` prop meant *our layer owns it*; a hit with a deprecation banner meant *replace the idiom*.
- Grounding is grep-verifiable evidence in a citation (`file.md:line`), not a vibe.
