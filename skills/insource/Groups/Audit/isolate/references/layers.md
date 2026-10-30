# The layer mechanism (Level 3)

Contents: parts, resolution rule, ambiguity policy, folder layout, who imports whom, inclusion versus selection, registration, resolver sketches.

Axes, values, and the component name are examples. The mechanism, not the syntax, is the requirement: use the project's own idiom for contracts and registries.

## Parts

1. **Axis selector.** One small unit per axis that reports one fact: the current platform, channel, or audience. It knows nothing about components.
2. **Layer key.** The explicit coordinates a layer applies to: a set of (axis, value) pairs. An empty set is the base. One pair is a single-axis layer. Two or more pairs form a **tie-breaker layer**, which exists only where lower layers collide.
3. **Registry.** For each seam the base declares a contract (an `[interface]`, `[protocol]`, `[trait]`, or `[function type]`) and a registry. Layers register an implementation under their key.
4. **Resolver.** One function takes the registry and the selectors' current values and returns one implementation, or an ordered chain when layers may wrap each other.

## Resolution rule

A layer matches when all its coordinates equal the current values. Among matches, the one with the most coordinates wins. If two matches tie on coordinate count, the result is ambiguous and must fail loudly until someone registers a tie-breaker layer that names both. No table of special cases is needed for any number of axes.

## Ambiguity policy (a team decision)

State the trade-off and let the user choose. Examples:
- `[strict: ambiguity fails until a tie-breaker exists]` is more work but makes every collision a reviewed decision. This is the recommended default.
- `[fixed axis precedence, such as audience beats channel]` is shorter to write but hides collisions.
- `[priority numbers on registrations]` is flexible but makes behavior depend on numbers nobody reviews.

## Folder layout

The folders mirror the keys. The filename still carries only the total axis (often platform). The folder chain carries every sparse axis. A name such as `Component.ValueA.ValueB.Platform.ext` never exists.

```
src/
  Core/                              shared machinery, knows no component
    axis selectors
    layer key, registry, resolver
  <Component>/                       the component and its BASE layer
    <Component>.ext                  public surface, seam contracts, registry; asks the resolver
    <Component>.<Platform>.ext       Level 1 platform files
    _<Component>.<Family>.ext        family files
    DefaultPolicy.ext                base implementation of a seam contract
  Layers/                            sibling of components, never inside them
    <axisA>/<valueA>/<Component>/             layer keyed by one coordinate
    <axisB>/<valueB>/<Component>/
    <axisA>+<axisB>/<valueA>.<valueB>/<Component>/
                                              tie-breaker, only if the two above collide
  Registration/
    registration list                per-build list of registration calls, generated or hand-written
```

`Layers/` is grouped by axis, so "what does `[canary]` change" is answered by one folder. Each layer folder holds only files that differ from the base. Axis and value names must not contain `.` or `+`, because those separate keys in folder names; `scripts/check_layers.py` relies on this.

## Who imports whom

```
callers        -> component (the one public surface)
component      -> resolver (the only thing it knows about layers)
resolver       -> axis selectors
layer files    -> the base contract only
registration   -> component registry, base implementation, every layer included in this build
app startup    -> registration, once, before the first use of any component
base           -> never references any layer
```

- Callers import the component and nothing else.
- The component's main file imports core (registry type, resolver) and never a layer.
- A layer file imports the seam contract from the component and the key type from core. It never imports another layer or the component's implementation files.
- The registration list is the only place that imports layers. There is no cycle because the component never imports it.
- Only a tie-breaker layer may know both parents, because it exists only when both are present.
- Because a resolver can return an ordered chain, a layer can decorate another layer's behavior, which file shadowing cannot do.

## Inclusion versus selection

Classify each axis by when it binds:

| Axis (examples) | Candidates present in the binary | Choice made |
|---|---|---|
| `[target platform]` | only that platform's files | build |
| `[release channel]` | only that channel's layer folders | build |
| `[audience or region]` | all audiences, if it can change at runtime | runtime |
| `[customer tenant]` | all tenants | runtime |

An axis fixed per install may bind at build time, and its registry shrinks to one static choice. Runtime selection ships every candidate, so inclusion must exclude layers that do not belong in the binary, or experimental code ships inside the stable build.

## Registration

- Name the full coordinates in every registration, even when the build already decided one. It documents which cell the registration fulfils, and a leaked layer stays inert because it can never match.
- Register explicitly, with a generated or hand-written list or a module initializer. Reflection or classpath scanning breaks under trimming, ahead-of-time compilation, and strict sandboxes.
- Use typed identifiers for axis values (`[enum]`, `[branded type]`, `[constants class]`), not free strings, so a typo is a compile error.
- A duplicate key is an error at startup.

## Resolver sketches

Illustrative, idiomatic shapes of the same rule. Translate to the project's language.

```typescript
type Ctx = Record<string, string>;
type Layer<T> = { when: Ctx; impl: T };          // when = {} is the base

function resolve<T>(layers: Layer<T>[], ctx: Ctx): T {
  const hits = layers.filter(l => Object.entries(l.when).every(([k, v]) => ctx[k] === v));
  const best = Math.max(...hits.map(l => Object.keys(l.when).length));
  const top = hits.filter(l => Object.keys(l.when).length === best);
  if (top.length !== 1) throw new Error(top.length ? "ambiguous layers" : "no base layer");
  return top[0].impl;
}
```

```python
def resolve(layers, ctx):
    hits = [l for l in layers if all(ctx.get(k) == v for k, v in l.when.items())]
    best = max((len(l.when) for l in hits), default=-1)
    top = [l for l in hits if len(l.when) == best]
    if len(top) != 1:
        raise LookupError("ambiguous layers" if top else "no base layer")
    return top[0].impl
```

```kotlin
data class Layer<T>(val whenAll: Map<String, String>, val impl: T)

fun <T> resolve(layers: List<Layer<T>>, ctx: Map<String, String>): T {
    val hits = layers.filter { l -> l.whenAll.all { (k, v) -> ctx[k] == v } }
    val top = hits.groupBy { it.whenAll.size }.maxByOrNull { it.key }?.value
        ?: error("no base layer")
    return top.singleOrNull()?.impl ?: error("ambiguous layers")
}
```

```go
// Go 1.18+: the same rule with generics
type Layer[T any] struct { When map[string]string; Impl T }

func Resolve[T any](layers []Layer[T], ctx map[string]string) (T, error) {
	var zero T
	best, n := []Layer[T]{}, -1
	for _, l := range layers {
		ok := true
		for k, v := range l.When { if ctx[k] != v { ok = false; break } }
		if !ok { continue }
		switch c := len(l.When); {
		case c > n: best, n = []Layer[T]{l}, c
		case c == n: best = append(best, l)
		}
	}
	if len(best) != 1 { return zero, fmt.Errorf("layers: %d candidates", len(best)) }
	return best[0].Impl, nil
}
```
