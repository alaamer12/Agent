# Signatures with relations: overloads, overrides, dispatch

The compiler-first ladder says *what* rejects; this file owns the next question: what happens to a
signature when **the result depends on which input arrived**, or when one signature must honor
another's contract. Agents systematically flatten those relations — a union where a pairing
belonged, a subclass rewrite where the base contract was law, a decorator that erases everything
it wrapped.

*Names and `[bracketed]` options are illustrative, not exhaustive. The behavioral notes follow
documented checker semantics; verify on the project's language/tool versions before enforcing.*

## 1. Bias warning: relation-flattening

The default agent output for a two-input API is `A | B -> C | D`: legal, and it destroys the fact
that `A` produces `C` and `B` produces `D`. Every consumer then re-narrows or casts — the wall you
just built has a door in it. Same family: an overriding method treated as a fresh signature instead
of a promise inherited from the base. The relations are first-class; say them with a mechanism.

## 2. The five failure modes

**(1) Correlated return flattened.** `parse(str) -> Doc`, `parse(bytes) -> BinaryDoc` written as
one union-in-union-out. Express the relation instead, by ecosystem:
- TypeScript: [function overloads] or — usually better — [one generic signature with a conditional
  return] (`<S extends string>(s: S) => S extends Uppercase<S> ? A : B`). Note that with classic
  overloads the implementation signature is invisible to callers; the arms are the public face.
- Python: `@overload` arms from `typing` / `typing_extensions`; the real implementation under them
  is legitimately wide (`Any`-ish) — the arms, not the body, are the contract.
- Rust: no overload syntax by design — traits are the overloading mechanism (`impl From<...>`,
  marker generic parameters); separate functions when the meanings differ.
- Go: no overloads — [distinct method names] or [generics with a type set]; two behaviors under
  one name is usually the wrong API anyway.
- Java / C# / Kotlin / Swift: native overloads; keep arms symmetric.

**(2) The ignored override contract (Liskov).** A subclass that narrows a parameter, widens the
return, adds a required argument, or changes the failure mode does not "override" — it breaks every
caller typed against the base. The law: **parameters at least as general, return at most as
promised, same or narrower errors.** When the checker rejects the rewrite, the hierarchy is wrong,
not the checker: split the base (drop the method from the common contract, make the divergent
capability its own type / sealed variant) rather than appeasing it with `Any`. Make the intent
declared, not implied: TypeScript's `override` keyword, Java's `@Override`, C#/Kotlin's `override`
modifier, Python's `typing_extensions.override` (3.12+) — the marker exists so the checker verifies
the relation instead of you trusting a name match.

**(3) Dispatch that hides everything.** `singledispatch` / multipledispatch / handler registries
route at runtime; typed sloppily, the base signature becomes `Any` and the whole API goes dark to
the checker. Rule: the **base signature is the contract** — typed parameters (a union or protocol)
and a typed return; every registered arm is a concretely typed implementation of it. Choosing
between the neighbors:
| The pairing is… | Use |
|---|---|
| static, closed, decided by input type at write time | overloads (mode 1) |
| open — arms register from other modules/plugins | dispatch with a typed base |
| decided by runtime data only | one signature + a boundary check (rung 5) |
| actually different meanings wearing one name | separate functions — and say so in names |

**(4) Overload theater.** N arms that all share the same input→output relation are a union wearing
a trench coat: extra surface, arms that drift apart, tests duplicated per arm. One arms-worth of
information = one signature. Likewise, a "convenience" arm that merely normalizes into another arm
belongs in the body (or at a creation point with a normalize policy), not in the public face.

**(5) Wrapper erasure.** Decorators, higher-order functions, proxies — the most reused code, and
the agent's most destructive annotation: `(fn: (...args: any[]) => any) => any`, Python
`def decorator(f: Callable) -> Callable`, Go interface{} combinators. Every signature passing
through becomes weak-typed downstream. Preserve it: Python [`ParamSpec` + `Concatenate` (PEP 612)];
TypeScript [generic rest tuples / `Args extends unknown[]` propagation, `ThisParameterType`];
Rust/Go — the wrapper is typed by construction once the wrapped signature is named (generics /
explicit func types). Test: a wrapper whose declared types cannot answer "what did this call
return?" is untyped infrastructure — fix before adding another call site.

## 3. Suppression is not a fix (this family's escape hatch)

`# type: ignore`, `@ts-ignore`, `@type: ignore` variants, `as any`, a cast inserted because the
checker refused the override or the overload: each converts a found bug into a deferred one. The
deck's cast law (casts exist only at the creation point —
[wrong-type-errors §4](./wrong-type-errors.md)) extends here: a suppression may live **only** at
interop boundaries or creation points, must name its reason in a comment, and when the reason reads
"the checker disagrees with my design" — the design is the bug. Fix the signature or the hierarchy;
never the error list.
