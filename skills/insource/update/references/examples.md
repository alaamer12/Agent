# Worked examples

Read this when you are unsure how to classify a hit, how much to ask, or how to phrase the report. Each example shows the trap, what the agent should do, and why.

> **Illustrative, not exhaustive.** The languages, scenarios, and scope choices below are examples to reason from. The failure they show is the same in every stack, so if the project uses something not shown here, map the pattern onto it. A hybrid or unlisted scope is always an acceptable answer.

## Contents

- [Example 1: The trap, across four language families](#example-1-the-trap-across-four-language-families)
- [Example 2: The report that resolves it](#example-2-the-report-that-resolves-it)
- [Example 3: A value change, not a name](#example-3-a-value-change-not-a-name)
- [Example 4: A behavior change, not a rename](#example-4-a-behavior-change-not-a-rename)
- [Example 5: Contracts you must not assume](#example-5-contracts-you-must-not-assume)
- [Example 6: The look-alike](#example-6-the-look-alike)
- [Example 7: A dependency or library migration](#example-7-a-dependency-or-library-migration)
- [Example 8: When NOT to ask](#example-8-when-not-to-ask)
- [Anti-patterns](#anti-patterns)

---

## Example 1: The trap, across four language families

**Request:** "We call them *topics* now, not *catalogs*." The user points at one spot. The agent fixes that spot and reports done. In every language below, the same concept is still alive a few lines away, under a different spelling.

Each block shows the **naive edit** (only the spot the user pointed at) and the **footprint** the sweep would have found.

### Go (compiled, static, tags carry a second spelling)

```go
// Naive edit: the user-visible label was changed...
const pageTitle = "Explore topics"

// ...but the same concept survives in other spellings, in the same package:
type CatalogItem struct {
    ID        int    `json:"catalog_id"`   // wire format: a contract
    CatalogID int    `db:"catalog_id"`     // storage column
}
func (s *Service) ListCatalogItems(ctx context.Context) ([]CatalogItem, error) { /* ... */ }
```

### Python (dynamic, snake_case, framework derives names)

```python
# Naive edit: the display string was changed...
PAGE_TITLE = "Explore topics"

# ...but these still say "catalog" in the same module tree:
class CatalogPolicy(BasePolicy): ...
def get_catalog_items(user_id: int) -> list["CatalogItem"]: ...
CATALOG_CACHE_KEY = "catalog:items:v2"          # cache key: outside consumers may read it
```

### Java (enterprise OOP, accessors add prefixes)

```java
// Naive edit: the label constant was changed...
private static final String PAGE_TITLE = "Explore topics";

// ...but the concept persists through generated and derived names:
public class CatalogItem { private long catalogId; public long getCatalogId() { return catalogId; } }
@GetMapping("/catalog/items")                   // route: a contract
public List<CatalogItem> listCatalogItems() { /* ... */ }
```

### Rust (systems, snake_case functions, PascalCase types)

```rust
// Naive edit: the display string was changed...
const PAGE_TITLE: &str = "Explore topics";

// ...but the module tree and types still carry the old word:
pub mod catalog;                                // file: src/catalog/mod.rs
pub struct CatalogItem { pub catalog_id: u64 }
pub fn list_catalog_items(db: &Pool) -> Result<Vec<CatalogItem>, Error> { /* ... */ }
```

**Why this matters.** The four snippets use different idioms, yet the pattern is identical: the visible string is one spelling among many. Note also that some leftovers are **contracts** (a JSON tag, a route, a cache key), where changing them can break outside consumers. The skill's job is to find all of them, then let the user decide the boundary.

---

## Example 2: The report that resolves it

**After the sweep, do not edit yet. Ask.** The report below applies to any of the four stacks above. It is shown here in its filled-in form.

> **Change:** rename "catalog" to "topic".
> **You pointed at:** the page title constant.
>
> I searched the whole workspace, not just that spot. I found **34 places across 13 files**:
>
> | Bucket | Count | Examples |
> |---|---|---|
> | User-facing | 6 | page title, nav label, empty-state text |
> | Internal | 19 | `CatalogItem` type, `listCatalogItems`, `catalog/` module |
> | Contracts | 3 | JSON tag `catalog_id`, route `/catalog/items`, cache key `catalog:items:v2` |
> | Verification and docs | 5 | 3 tests, 2 doc pages |
> | Possible look-alike | 1 | `catalog` in a vendored third-party library |
>
> **Needs your call:** the three contracts. Renaming them breaks any client that still sends `catalog_id` or calls `/catalog/items`.
> **Cannot verify from here:** analytics dashboards and other repos that consume the API.
>
> **My recommendation** (only a suggestion): rename user-facing and internal names now, and keep the three contracts as deprecated aliases for one release.
>
> How far should I take this? I could do `[display text only]`, `[everything except contracts]`, `[everything, with the old public names kept as aliases]`, or `[everything, including a breaking rename]`. Those are only starting points. Tell me a different split if that fits better.

**Why this shape.** It counts by bucket, names the risky items and what breaks, says what it cannot see, recommends something the user can simply accept, and offers choices as examples rather than a closed menu.

---

## Example 3: A value change, not a name

**Request:** "The primary brand color is now `#0b57d0`."

The trap appears in every stack that stores a color. A constant is changed in one file; the same value lives on in other notations and other layers.

```typescript
// TypeScript / web: naive edit changed only this token
export const brandPrimary = "#0b57d0";
// still old, elsewhere:  rgb(26, 115, 232)   #1A73E8   theme.palette.primary
```

```kotlin
// Kotlin / Android: naive edit changed only the Compose color
val BrandPrimary = Color(0xFF0B57D0)
// still old, in resources:  <color name="brand_primary">#1A73E8</color>
```

```swift
// Swift / iOS: naive edit changed only the asset catalog color
extension Color { static let brandPrimary = Color(red: 11/255, green: 87/255, blue: 208/255) }
// still old, in a separate file:  UIColor(hex: 0x1A73E8)
```

```python
# Python / data visualization: naive edit changed the default palette
BRAND_PRIMARY = "#0b57d0"
# still old, in a plotting config and an email template:  "#1a73e8"
```

**Correct behaviour.** Sweep for the old value in every notation it can take (hex in either case, `rgb(...)`, a packed integer like `0xFF1A73E8`, a per-channel float triple). Report by bucket, and note that some places (an email template, a third-party embed, a logo) may deliberately *not* follow the theme, so ask rather than assume.

**Why.** The skill is not about names. Any change to a term, value, path, or rule has a footprint.

---

## Example 4: A behavior change, not a rename

**Request:** "Limit free-tier accounts to 3 projects." Nothing is renamed, so there is no "old term" to grep for, and it is easy to feel finished after editing one number.

```csharp
// C#: the constant is changed...
public const int MaxFreeProjects = 3;
// ...but the rule is restated elsewhere:
//   ValidationMessages.resx:  "Free accounts can have up to 5 projects."
//   [SwaggerSchema("Max 5 projects on the free tier")]
//   Assert.False(_limits.CanCreate(freeUser, currentCount: 5));   // test encodes the old rule
```

```go
// Go: the constant is changed...
const MaxFreeProjects = 3
// ...but the rule is restated elsewhere:
//   errors.New("free accounts can have up to 5 projects")
//   docs/pricing.md:  "Free: up to 5 projects"
//   if count >= 5 { ... }   // an unrelated retry limit: a LOOK-ALIKE, do not touch
```

```elixir
# Elixir: the module attribute is changed...
@max_free_projects 3
# ...but the rule is restated elsewhere:
#   gettext("Free accounts can have up to 5 projects")
#   test "free user blocked at 5 projects" do ... end
```

**Correct behaviour.** Take the search handles from the change itself: the constant, its literal value near the word "project", the function that enforces it, and every place that states or assumes the rule. Follow callers outward. Then ask, and raise the question the user may not have considered: what happens to existing free accounts that already have 4 or 5 projects? That is a product decision, not a code one, and it is invisible to any text search.

**Why.** The footprint here includes user-facing copy, documentation, tests, and an existing-data question, none of which contains a renamed word.

---

## Example 5: Contracts you must not assume

**Request:** "Rename `user_id` to `account_id`." Internal variables are easy. But the same name appears at boundaries where other people's code depends on it.

```ruby
# Ruby / Rails: an internal rename is safe...
def belongs_to?(account_id) = self.account_id == account_id

# ...but these boundaries are contracts, so they are NOT yours to assume:
#   db/migrate/..._create_orders.rb      t.integer :user_id        (applied migration: history)
#   app/serializers/order_serializer.rb  attribute :user_id        (public API field)
#   config/webhooks.yml                  payload: { user_id: ... } (third-party subscribers)
```

```sql
-- SQL: a column rename needs a migration and a backfill plan, not a find-and-replace.
ALTER TABLE orders RENAME COLUMN user_id TO account_id;
-- and every reader and writer of that column must change in the SAME release.
```

**Correct behaviour.** Do not touch contract items on assumption. Name the consequence of each and offer paths the user may not have thought of, such as keeping the old field as a deprecated alias for one release, then let them choose:

> - DB column `orders.user_id`: needs a migration and a backfill plan
> - API field `user_id`: renaming breaks existing API clients
> - Webhook payload `user_id`: breaks subscribers
>
> I could do `[internal names only]`, `[internal + a DB migration]`, or `[all of it, with the API field kept as a deprecated alias for one release]`. Those are starting points; tell me if you want a different split.

**Why.** These decisions have blast radius outside the repository. The agent should surface options, but must not choose for the user.

---

## Example 6: The look-alike

**Request:** "Rename 'class' to 'course' (the scheduling feature)." A raw search returns hundreds of hits, because `class` is also a language keyword, a style hook, and a substring of longer words.

```python
class ClassSchedule:                       # the feature: in scope
    def add_class(self, title): ...        # the feature: in scope

class Repository(Model):                   # the `class` KEYWORD: unrelated, leave alone
    pass
```

```java
public class ClassSchedule { }                    // the feature: in scope
public class Repository extends Model { }         // the `class` KEYWORD: unrelated
Class<?> type = obj.getClass();                   // reflection API: unrelated look-alike
```

```ruby
class ClassSchedule < ApplicationRecord   # the feature: in scope
end
klass = Object.const_get(name)            # `klass` is idiomatic for "class": unrelated
```

**Correct behaviour.** Do not run a blind replace, and do not paste 400 lines of grep output. Filter to the hits that plausibly mean the feature, then show the user a short sample of *both* groups so they can confirm where the boundary sits.

**Why.** Reporting everything buries the decision. The skill's job is to make the decision easy: group, count, sample, recommend.

---

## Example 7: A dependency or library migration

**Request:** "Replace library A with library B for date handling."

```typescript
// TypeScript: naive edit swapped the import in the ONE file the user opened
import { format } from "date-fns";
// ...23 other files still import the old library, and the manifest still lists it.
```

```python
# Python: naive edit changed one call site
from datetime import datetime
# ...the project still imports `arrow` in 14 modules, and requirements.txt still pins it.
```

```rust
// Rust: naive edit changed one function
use chrono::Utc;
// ...Cargo.toml still depends on `time`, and 9 modules still call it.
```

**Correct behaviour.** Sweep for every import, `use`, `require`, or `include` of the old library, plus manifests, lockfiles, config, and type references. Report the count by file. Importantly, note that two libraries usually have **different APIs**, so this is a rewrite per call site, not a find-and-replace. Offer scopes such as `[just this file]`, `[all imports in one change]`, or `[migrate module by module]`, and say which you recommend and why.

**Why.** For a migration the footprint is the whole point. A partial swap leaves two libraries in the build, which is worse than either alone.

---

## Example 8: When NOT to ask

This skill triggers on every change, so the sweep always runs. What varies is whether the *question* is needed. Two cases where it is not.

### 8a. The user already set the scope

**Request:** "In the pricing table only, rename the column 'Plan' to 'Tier'. Leave everything else, I'm doing the rest in another change."

Run the sweep anyway; it shows "Plan" appears in 9 other places. The user has already decided scope, so do not ask and do not expand. Make the one change, then mention what you saw:

> Done, pricing table only. FYI "Plan" also appears in 9 other places (the settings screen, a badge component, 3 tests) that I left alone as requested.

**Why.** The skill exists to stop the agent from *silently deciding* scope. When the user has decided it, there is nothing to unlock. Re-asking would be the mirror-image failure: ignoring an explicit instruction. The heads-up is informational, and it is only possible because the sweep ran.

### 8b. The sweep finds nothing else

**Request:** "Change the submit button label on the contact form to 'Send message'."

Sweep for the old label. Suppose the only reference is the one the user pointed at. Say so in a line and make the change:

> Changed. I checked for other uses of that label and this was the only one, so nothing else needed updating.

**Why.** A skill that fires on every change must not turn every change into a questionnaire. The question exists to resolve real ambiguity. When the sweep shows none, asking is noise.

---

## Anti-patterns

**The silent minimal edit.** Fixing the one visible spot and saying "done". This is the failure the skill exists to prevent, in any language.

**The silent maximal edit.** Replacing every hit without asking. It can break public APIs, rewrite changelogs, and mangle look-alikes. Wide search does not license wide editing.

**The assumption dressed as a statement.** "I left the route alone since you probably wouldn't want it changed." That is a question. Ask it.

**The wall of hits.** Pasting 200 grep lines and asking "what do you want?". The user cannot decide from a wall. Group, count, sample, recommend.

**The closed menu.** Offering "pick 1, 2, or 3" as if those were the only possible scopes. Present choices as examples and welcome a hybrid.

**The questionnaire.** Asking even when the sweep found nothing else, or when the user already set the scope.

**The endless questions.** Asking about every category one by one. Ask **one** scope question with well-shaped choices.

**The skipped verification.** Editing, then reporting done without re-sweeping. Memory of what you changed is not evidence of what remains.

**Re-arguing a decision.** After the user picks a narrow scope, repeating the case for a wider one. Record the skipped items in the summary and move on.
