# 09 — Pattern matching and switching (the ladder the compiler checks)

Language-level matching reads like a ladder and, in most languages, does something hand-written chains
cannot: prove you covered the domain, or tell you that a branch is unreachable.

## The same ladder, seven stacks

**Rust** - exhaustive `match`, guards with `if`, unreachable-arm warnings.

```rust
match fetch {
    Fetch::Ok(n) if n > 1000 => "loaded-heavy",
    Fetch::Ok(_)             => "loaded",
    Fetch::Stale(0)          => "fault",     // ordering still matters: earlier arm wins
    Fetch::Stale(_)          => "stale",
    Fetch::Empty | Fetch::Cancelled => "nothing-to-show",
    _                        => "unknown",   // a wildcard here gives back the exhaustiveness you paid for
}
```

**TypeScript** - `switch` is not exhaustive; `ts-pattern` or a `never` default gets you there.

```ts
import { match, P } from "ts-pattern";

const kind = match(f)
  .with({ blocked: true }, () => "blocked")
  .with({ fault: true, rows: 0 }, () => "fault")
  .with({ fault: true, rows: P.number.gt(0) }, () => "stale")
  .otherwise(() => "ready");          // otherwise() is mandatory - that is the whole benefit
```

**Python 3.10+** - `match/case` with class patterns and guards. No exhaustiveness check: the missing
`case _` fails open exactly like an `if` chain.

```python
match point:
    case Point(x=0, y=0):                 return "origin"
    case Point(x=0) | Point(y=0):         return "axis"
    case Point(x=x, y=y) if x == y:       return "diagonal"
    case Point(x=x, y=y):                 return "quadrant"
    # no wildcard here -> non-matching shapes return None
```

**C#** - switch expressions with relational patterns and a discard arm.

```csharp
string Grade(int n) => n switch
{
    < 0 => "invalid",
    0 or < 50 => "fail",
    >= 90 => "pass-with-distinction",
    _ => "pass",
};
```

**Java 21** - pattern labels in `switch`, `when` guards, exhaustiveness enforced for sealed types.

```java
String describe(Fetch f) {
    return switch (f) {
        case Fetch.Ok ok when ok.n() > 1000 -> "loaded-heavy";
        case Fetch.Ok ok -> "loaded";
        case Fetch.Empty e -> "empty";
        case Fetch.Fault x -> "fault";
    };
}
```

**Go** - `switch` with no fallthrough by default, an optional `default`, and no exhaustiveness. A
missing `default` on an enum-like type is the same silent zero-value bug as a missing `else`.

```go
switch state {
case StateLoading: return view.Pending()
case StateError:   return view.Failure(err)
default:          return view.Unknown(state)   // write it, do not inherit it
}
```

**Elixir** - `cond` is the ladder; `case` with `when` guards matches a shape and orders clauses.

```elixir
cond do
  f.blocked -> :blocked
  f.fault and f.rows == 0 -> :fault
  f.fault -> :stale
  true -> :ready      # `true ->` is mandatory in practice: without it cond raises CaseClauseError
end
```

## What each one gives you, and what it never gives you

| Guarantee | Rust | TS+ts-pattern | Python | C# | Java (sealed) | Go | Elixir |
|---|---|---|---|---|---|---|---|
| Exhaustiveness checked | yes | with `otherwise` | no | with `_` only if written | yes for sealed | no | no |
| Unreachable arm warned | yes | - | - | - | - | - | - |
| Guards | `if` | `.when`/predicates | `if` | `when` | `when` | case expr | `when` |
| Fallthrough hazard | no | yes (`switch`) | no | no (expression) | yes unless `->` | no | no |

Matching never decides **semantics**. Two overlapping arms still need "first wins" - which the
compiler will happily honor while giving you the wrong answer. Specificity ordering is your job
(`00`, `14`).

## Pick it when

- The discriminator is a closed type the compiler knows.
- You want new variants to break the build instead of surfacing as a bug report.
- The ladder is short and local; extraction into a table (`02`) would be ceremony.

Do not pick it when the set is open (strings from users, ranges), when rules come from config, or when
several call sites must share the same ordering - then the compiler is on no one's side.

## Failure modes

- **Wildcard added to silence the error.** Exhaustiveness becomes decoration; the next new variant
  matches it and nobody notices. Give the wildcard arm its own test that asserts it is reached only by
  genuinely unknown input.
- **Guards that reorder meaning.** `Ok(n) if n > 1000` above `Ok(_)` is intentional; the reverse is a
  bug that reads identically in review. Comment the dependency between adjacent arms.
- **Or-patterns losing data**: `Fetch::Empty | Fetch::Cancelled => ...` cannot tell the caller which
  one fired - the audit trail is gone. Return a tuple with the arm name if you need to log it.
- **Fallthrough in C-family `switch`**: an omitted `break` runs the next arm. Java's arrow form and
  Go's default behavior exist precisely because this was a decade of bugs.
- **Matching on a stringly type** ("pending" | "loading" as raw strings): you keep the ladder, lose the
  check. Bind to an enum or a union first.

## Seen in

Everywhere, including inside ladders you write by hand: state renderers, verdict mapping, parser
dispatch, protocol handling, CLI exit-code mapping, and the "if-else ladder" that code review keeps
asking you to replace.
