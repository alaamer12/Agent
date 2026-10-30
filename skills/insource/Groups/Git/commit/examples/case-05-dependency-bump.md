# Case 5 - dependency bumps: when one line is enough and when it is not

A lockfile-only change with no behavior effect needs no body. Almost everything else about a dependency
change does.

## Fine as a bare subject

```text
chore(deps): bump lodash 4.17.20 -> 4.17.21
```

```text
chore(deps-dev): bump vitest 1.6 -> 2.1
```

Both are mechanical, no code changed to accommodate them, no behavior delta claimed. Do not pad these with a
body - "upgraded to the latest version" is noise, and a run of those makes the log unreadable.

## Needs a body: a bump with a reason, a range, or a side effect

```text
chore(deps): upgrade http client 2.4.1 -> 2.7.0

2.7 adds per-request timeouts, which the export path needs to stop hanging on
slow proxies (the 2.4 default is unlimited). It also drops the transitively
pinned tls library that had the advisory we keep getting flagged for.

Behavior note: connection reuse is capped at 10 per host in 2.7; our load
profile peaks at 4, so nothing changes in practice. Test suite and the export
integration test against staging both pass locally.

Refs #5102
```

The three things a reviewer cannot infer from a version number: **why now**, **what behavioral default
moved**, and **what you actually verified**.

## Needs a separate commit: bump plus code change

Never land `upgrade X and adapt our code to it` as one commit when the adaptation is more than a rename:

```bash
git add package.json package-lock.json && git commit -F msg1   # the bump, mechanically reviewable
git add src/…                                                  # read the new API's effect
git commit -F msg2                                             # the adaptation, with its own reasoning
```

```text
chore(deps): upgrade form validator 3 -> 4

Major bump, no code adapted yet. The 3.x config API is removed in 4, so the
package currently fails to build - the next commit fixes that. This split exists
so the diff of the adaptation is not buried in 4,000 lines of dependency churn.
```

```text
refactor(forms): move validation config to the 4.x schema API

3.x took a rules object at construction; 4.x takes a schema and validates
imperatively. Wrapped our rule set in the provided compatibility builder rather
than rewriting it as a schema, because three of our rules are dynamic and the
schema form would have needed a code path per form type.
```

The intermediate commit knowingly breaks the build - which contradicts "every commit leaves the tree working".
That is the trade-off: either the dependency commit is transiently broken, or 4,000 lines of vendor churn ride
along with your reasoning. Say which you chose and why, in the body, so the next reader does not think the
broken intermediate commit is a mistake. Where a project treats bisectability as sacred, do it the other way:
squash into one commit and put the migration reasoning in the body.

## Security bumps

```text
fix(deps): upgrade image decoder 1.8.2 -> 1.8.5 for CVE-2026-31415

The advisory covers a heap overflow on malformed ICC profiles, which our upload
path accepts. 1.8.5 is the first patched release in the 1.8 line; the 2.x
upgrade is a separate change because it drops the synchronous decode API.

Closes #5233
```

Name the CVE, name the code path that makes it reachable, and do not include exploit detail
([`06`](../references/06-scenario-recipes.md#security-fixes--two-different-obligations)).
