# Case 02 — the vendor tag no import lint could see

*Names, paths and numbers here are illustrative. The shape is what transfers.*

## The setup

A boundary rule with a good import wall: the vendor package was named in exactly one file, verified by
a lint that failed the build, and the tree had a handful of imports to check. The plan was to widen
that wall to the markup layer "later", since the import rule already covered everything.

It did not cover anything.

## The leak

A file that used a vendor component in its template with **no import at all**:

```
<vendor-card>        ← no import, no registration, no declaration in this file
  <vendor-button />
</vendor-card>
```

The build resolved it. The framework auto-imports components by scanning the vendor package's exports
at compile time, so a name in markup is a complete program: the file imports nothing, the tag renders,
the type-checker is satisfied, and the import lint — the strictest in the tree — reports a clean file.

Worse, the second leak in the same file was invisible to any linter that understood imports but not
CSS: `class="vendor-card--elevated vendor-space-4"`. Our element, the vendor's stylesheet. The vendor
now owned that element's spacing, and changing it meant a search that had nothing to do with imports.

## The probe that found it

One file and one build, taken seriously as a question rather than as a bug report:

```
1. Write a file that uses the vendor tag with no import and no registration.
2. Build it with the real toolchain — not the editor, not the type checker alone.
3. If it compiles, the import rule is decorative for markup, and the markup wall is mandatory.
```

It compiled. That single fact re-ranked the plan: the wall people intended to defer was the only wall
that worked, and the wall they had built was the one that could be deferred.

## What was added

- A **markup wall** in the same registry as the import wall, refusing: vendor tags outside the seam
  and skin tiers, vendor utility classes on our elements, raw platform controls reaching around the
  seam, vendor names inside authored identifiers or class names.
- The probe itself kept as a fixture: a temp-tree file that must **fail** the build. A framework
  upgrade that changes resolution semantics now shows up as a fixture that stops failing.
- Both walls armed the same way (planted violation, controls, glob liveness, doc↔registry parity).
  Sharing a baseline file between them was refused: one careless re-bless must not launder two
  auditors.

## The general form

"The toolchain resolves a name I never declared." Any of: a component auto-importer, a global
registration pass, a compiler transform that rewrites unknown tags, a class-utility scanner that
emits CSS for classes it has never seen, a dependency-injected runtime lookup. If it can resolve
anything it has not been told about, it can resolve the vendor, and an import rule will never know.

The failure is not that the wall was weak. It is that the wall was chosen by reasoning about what
imports look like instead of by probing what the build accepts.
