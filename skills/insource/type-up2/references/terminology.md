# Terminology

The single source of truth for the words this skill uses. Every other file uses these terms and no synonyms. When a file and this one disagree, this one wins; fix the file.

*These are **role names**, not identifiers. Names in code examples (`PlainString`, `UserEmail`, `UserSchema`, `toX`) are illustrative; the project's and the ecosystem's own names win ([naming](./tier-principles.md#naming-describe-the-role-follow-the-ecosystem)).*

## 1. Structure

| Term | Definition | Example |
|------|-----------|---------|
| **tiered system** | The opt-in three-tier type system (Mode B). | tiers 1 to 3 |
| **tier** | One of three ordered groups of types, each built only from the tier below. Used for nothing else: not for architecture, UI roles or deployment. | tier 1 primitives, tier 2 brands, tier 3 shapes |
| **raw type** | A type the language provides. In the tiered system it is named in tier 1 only. | `string`, `number`, `int` |
| **plain type** | A raw type under an explicit name, as a deliberate "any value is acceptable" choice. The first member of a primitive family. Use it only for that; if the code needs an integer, a float, a sign or a range, use the refinement. | `PlainString`, `PlainNumber` (`PlainX` is shorthand for the plain type of raw type X) |
| **refinement** | A tier 1 type that narrows a plain type to a **visible state** of the value. It must pass the distinguishability test (see the [tier 1](../tiers/tier-1-primitives.md#what-qualifies-as-a-refinement-the-distinguishability-test) file). | `UppercaseString`, `IntNumber`, `PositiveIntNumber`, `NonEmptyString` |
| **primitive** | Any tier 1 type: a plain type or a refinement. (Not the language's own type; that is a raw type.) | `PlainNumber`, `IntNumber` |
| **primitive family** | The tier 1 types derived from one raw type, kept in one file. | the string family, the number family |
| **brand** | A named type that says what a value means. Tier 2 in the tiered system, built from tier 1. In Mode A a brand may be as light as a documented alias or as strong as a nominal type. | `UserEmail`, `Port`, `UserIso` |
| **shape** | A tier 3 type that assembles brands and other shapes into a record, configuration, contract or tagged union. Folder name `shapes/`. | `UserSchema` (an illustrative type name), `SearchState` |
| **tagged union** | A shape with cases, each carrying only its own data. | idle, loading, success(results), error(message) |
| **variant** | One named version of a shape: **raw** (unvalidated input), **patch** (optional overrides), **resolved** (after defaults and validation). | `RawConfig`, `ConfigPatch`, `ResolvedConfig` |
| **schema** | Reserved for a validation-library schema (Zod, Pydantic…) or a database schema. Never the name of a tier 3 type. | a Zod schema, a database schema |
| **existing type** | A type provided by the language, its standard library, or a dependency already in the project. The tiers' roles are filled with existing types first; in Mode B an existing type enters through tier 1 only. | Pydantic `PositiveInt`, Rust `NonZeroU32`, `Uppercase<string>` |
| **nominal type** | A type distinguished by name, not by structure. Representations: newtype, opaque type, `NewType`, value class, intersection marker. | Rust newtype, Scala `opaque type` |

## 2. Creating and checking values

| Term | Definition | Notes |
|------|-----------|-------|
| **creation point** | The one place a runtime value becomes a refinement or brand: it normalizes and/or rejects, and is the only place a cast or wrapper is made. No function per type is required: a type guard, a library's `parse` call or `TryFrom` all qualify. | Ecosystem names: smart constructor, `TryFrom`, `from`, `New…`, a library's `parse`. Not a language constructor. |
| **value source** | Where a refined value comes from: a literal the compiler verifies, a more refined value (up is free), or a creation point. Only the third needs code. | |
| **policy** | How a creation point treats input: **normalize**, **reject**, or **normalize then reject**. Decided once per primitive family (tier 1) and per group of sibling brands (tier 2). | |
| **operation** | Something done to a value (trim, truncate, collapse, escape, decode) that leaves no trace in the result. Lives inside creation points; never a type. | |
| **boundary** | Where untrusted data enters: network, files, environment, forms, command line, storage, untyped callers. | |
| **boundary check** | The code at a boundary that turns untrusted data into shapes, using creation points. One per source of data. | Forms: a library's parse call, `TryFrom`, a decoder, a type guard. |
| **failure carrier** | How invalid input is reported. Always the ecosystem's own. | `Either`, `Result`, `(T, error)`, an exception |
| **micro-decision** | A small choice about a value (case, range, unit, sign, trimming…) that must be made once, in one place. | |
| **visible state** | A property you can see in the value itself (case, integer-ness, sign, finiteness, emptiness). Refinements name visible states. | |

## 3. Enforcement

| Term | Definition |
|------|-----------|
| **check** | One of three kinds of enforcement. **Static**: the compiler and lint. **Runtime**: creation points, boundary checks and database constraints. **Tests**: negative tests, property tests, shared vectors. |
| **compiler-first ladder** | The order in which to express a rule, highest first: a built-in or ecosystem type, a closed set, a nominal type, a literal check, a runtime check. |
| **literal route** | An optional compile-time-verified way for a literal written in source to become a refinement or brand, beside the creation point. |
| **database constraint** | A rule enforced by the database (SQL `CHECK`, a domain). In prose this is never called "a check". |
| **negative test** | A test that fails if a wrong value compiles or is accepted. |
| **shared vectors** | One list of accepted and rejected values, run through the creation points and the database. |
| **catalog** | The table that records each type: tier, built from, creation point, policy, users. |
| **up is free, down is checked** | A value of a more refined type is usable where its parent is expected; the reverse goes through a creation point or a verified literal. |

## 4. Modes and process

| Term | Definition |
|------|-----------|
| **Mode A** | General enhancement of the project's type system (default). Brands are used; the tiers are not required. |
| **Mode B** | The tiered system (opt-in). |
| **rigor options** | `[plain types]` (readable names, no safety), `[brands with creation points]` (rules enforced; Mode A), `[tiered system]` (Mode B). |
| **golden rule** | Do not reinvent the wheel: use an existing type, and add only the part it lacks (see [reuse-before-create](./reuse-before-create.md)). |
| **promotion** | Moving a value up: raw type, then the type the code means (a plain type only for "any value", otherwise a refinement), then brand, then shape. |

## 5. Words not to use

| Do not write | Write |
|--------------|-------|
| semantic type, semantic alias, semantic primitive | brand |
| constructor (for the place a value becomes a brand) | creation point |
| entry check, outside-data check, entry point, parse step, parser | boundary check (or boundary) |
| construction, composite, schema (for a tier 3 type) | shape |
| raw primitive, bare primitive | raw type |
| unconstrained alias, plain alias | plain type |
| stage, layered variant | variant |
| database check | database constraint |
| validator (as a generic noun) | creation point (library or crate names such as `validator` are unaffected) |
| layer, level (of the type system) | tier (structure) or check (protection) |
| constructed types | brands with creation points |
| tiered branded system | tiered system |
