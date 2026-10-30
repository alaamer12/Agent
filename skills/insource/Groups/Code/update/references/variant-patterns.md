# Variant patterns: how one concept hides in a codebase

Read this when `scripts/sweep.py` (or the dependency-free fallbacks `scripts/sweep.sh` / `scripts/sweep.ps1`) finds less than you expect, or when the project mixes several ecosystems. A single concept is rarely spelled one way. Every language, framework, and layer has its own naming rules, so the same idea shows up in several spellings at once.

> **Illustrative, not exhaustive.** The languages, tables, and examples here are starting points. If the project uses a stack not listed, work out its naming conventions the same way: ask "how would this ecosystem spell a two-word concept in a type, a field, a constant, a file, a URL, and a config key?" A hybrid or unlisted convention is always in scope.

## Contents

- [The principle](#the-principle)
- [How ecosystems differ](#how-ecosystems-differ)
- [Where a concept lives, by layer](#where-a-concept-lives-by-layer)
- [Things text search cannot see](#things-text-search-cannot-see)
- [Grammar traps](#grammar-traps)
- [Look-alikes](#look-alikes)

## The principle

Every search for a concept is really a search for **a set of spellings**. Build the set from the words, not from one string. Take the two-word concept *order status*:

| Convention | Spelling |
|---|---|
| lower / spaced (prose) | `order status` |
| kebab-case | `order-status` |
| snake_case | `order_status` |
| camelCase | `orderStatus` |
| PascalCase | `OrderStatus` |
| SCREAMING_SNAKE | `ORDER_STATUS` |
| Train-Case (headers) | `Order-Status` |
| concatenated | `orderstatus` |
| dotted (keys, namespaces) | `order.status` |

A one-word concept looks identical across most of these, which hides the problem. The miss then shows up as a **prefix or suffix** (`OrderService`, `order_id`, `ORDER_URL`), so always search for a term as a substring, not as a whole word.

## How ecosystems differ

The same concept, named the way each ecosystem's idioms would name it. Pick the rows that match the project; ignore the rest.

| Ecosystem | Type / class | Field / variable | Constant | File or module | Notes |
|---|---|---|---|---|---|
| Go | `OrderStatus` | `orderStatus`, struct tag `json:"order_status"` | `OrderStatusPending` | `order_status.go` | exported = capitalized; tags carry a *second* spelling |
| Rust | `OrderStatus` | `order_status` | `ORDER_STATUS_DEFAULT` | `order_status.rs` | `snake_case` fns, `PascalCase` types |
| C# / .NET | `OrderStatus` | `OrderStatus` (property), `_orderStatus` (field) | `OrderStatusDefault` | `OrderStatus.cs` | properties are PascalCase; private fields often `_camel` |
| Java / Kotlin | `OrderStatus` | `orderStatus`, `getOrderStatus()` | `ORDER_STATUS` | `OrderStatus.java` | accessors add `get`/`set`/`is` prefixes |
| Python | `OrderStatus` | `order_status` | `ORDER_STATUS` | `order_status.py` | `snake_case` everywhere except classes |
| Ruby / Rails | `OrderStatus` | `order_status` | `ORDER_STATUS` | `order_status.rb` | Rails derives table and route names: `order_statuses`, `/order_statuses` |
| Elixir | `OrderStatus` (module) | `order_status` | `@order_status_default` | `order_status.ex` | module attributes use `@` |
| JS / TS | `OrderStatus` | `orderStatus` | `ORDER_STATUS` | `order-status.ts` or `OrderStatus.tsx` | file naming varies by project |
| SQL | table `order_statuses` | column `order_status` | | `V1__create_order_status.sql` | index and constraint names embed the column name |
| Config / infra | | key `order_status` or `order-status` | env `ORDER_STATUS` | `order-status.yaml` | env vars are almost always SCREAMING_SNAKE |

Key thing to notice: a rename in one layer is rarely visible from another. A struct tag, a SQL column, an env var, and a URL slug are four spellings of one concept, in four files, in four different conventions.

## Where a concept lives, by layer

Use this as a checklist of places to look. Skip layers the project does not have.

**Code**
- Type, class, module, package, and namespace names
- Function, method, and accessor names (`getX`, `set_x`, `X()`)
- Variables, fields, properties, struct tags, and annotations
- Constants, enum members, and feature flags

**Interfaces and contracts**
- Route paths, RPC method and message names, GraphQL fields
- Serialized field names (JSON, protobuf, XML, form keys)
- Event, queue, topic, and webhook names
- Public function signatures and exported symbols
- Permission, role, and scope strings

**Data**
- Table, column, index, constraint, and view names
- Migrations, seed data, fixtures, and snapshots
- Cache keys and search-index field names

**Presentation and content**
- UI strings, error messages, emails, notifications
- Translation keys (not only their values)
- Style hooks, theme tokens, template names, markup attributes
- Accessibility text, alt text, and metadata (titles, descriptions)

**Project meta**
- README, docs, ADRs, diagrams, and API specs
- Test names, mocks, and test data
- Build, CI, deploy, and packaging config
- File and directory names, including generated code inputs

## Things text search cannot see

`sweep.py` and its shell fallbacks read text. None of them will find:

- **Constructed strings.** A name built at runtime from parts (`prefix + "_status"`, string templates, reflection, dynamic dispatch). Search for where the parts are defined.
- **Generated or compiled output** in build directories. These are excluded on purpose. Confirm they are regenerated, not hand-edited.
- **Code generated from a schema.** Renaming the schema field changes generated types elsewhere. Find the generator input and the regeneration step.
- **Data in a running database, CMS, or feature-flag service.** Rows and flags will not appear in the repo. Flag it as an out-of-repo follow-up.
- **External systems.** Dashboards, third-party configs, other repositories that consume your API, saved links, documentation sites. Name them as risks; do not pretend they are covered.
- **Binary content.** Text inside images, PDFs, or design files.
- **Git history.** Commit messages and old branches keep the old term. This is normal and fine.

When any of these are likely, put them in the report as "cannot verify from here" so the user knows where the edges of your sweep are.

## Grammar traps

Renaming a word is not always find-and-replace.

- **Plurals and irregular forms.** `catalog` becomes `catalogs`, but `category` becomes `categories`, `index` becomes `indices`, `person` becomes `people`, `status` becomes `statuses`. Ecosystems also pluralize differently: Rails derives `order_statuses` for you, Go usually writes `[]OrderStatus`. Do not assume one.
- **Articles.** "a topic" versus "an item": an article can change when the new word starts with a different sound.
- **Capitalization.** A word at the start of a sentence, in a heading, or inside an identifier follows different rules.
- **Compound phrases.** "catalog page" might become "topic page" or just "topics". Ask when a phrase does not translate word for word.
- **Short-token collisions.** Replacing `cat` would hit `catalog`, `category`, and `concatenate`. Prefer whole-token matches for short terms.
- **Non-English or localized text.** The same concept may appear in translation files under other languages. Check the locale directory.

## Look-alikes

The same string can name unrelated concepts. Before treating a hit as in scope, read a few lines around it.

| Term | Concept being changed | Unrelated look-alike |
|---|---|---|
| `catalog` | a product feature | a database system catalog, a vendored audio library, a package registry |
| `order` | a purchase | sort order in a query, evaluation order |
| `class` | a course offering | the language keyword, a style class, a `classifier` |
| `type` | a product category | the language keyword or a type annotation |
| `status` | a business state | an HTTP status code, a process exit status |
| `state` | a workflow stage | UI component state, a geographic state |
| `service` | a business capability | a DI-container service, an OS service, a k8s Service |

If a hit is ambiguous, do not guess. Put it in the report under its own **Possible look-alike** heading and ask.
