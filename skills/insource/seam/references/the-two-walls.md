# The two walls

> The seam is one file that knows the third party. Two independent checks keep that true, and one
> of them is the one most repos never build. Read this before writing any rule.

## 0. What the seam actually is

The seam is the **only** place the framework, the vendor SDK, or the platform driver is named. Above
it, code speaks the project's own vocabulary; below it, nothing does. Placement is a knowledge
question, not a responsibility question — the tier roles are owned elsewhere (`pvc`), and this file
never re-names them.

A seam file may be one line long. It is **complete, not thin**: its job is that a name exists in
exactly one place. Do not invent props, behaviour or caching to justify a bigger file — that is how
a seam becomes a second framework.

Naming law: our vocabulary carries no vendor name. `Button`, never `VendorButton`. The vendor's name
appears on one line, and if it appears in a message that line is the config, not the source.

**The seam is a set of files, not always a directory.** The framework's bootstrap and its build config
name the vendor too — the plugin registration, the auto-import resolver, the theme hookup. Decide
whether each of those is *part of the seam* (audited, and permitted by path like the wrappers) or a
named exemption with a reason; what you must not do is leave them unmentioned, because the first time
your own rule flags `vite.config.ts` is the day someone turns the rule off. This matters most with
auto-import: the config that makes the vendor available to every template is the reason the import
wall cannot see usage, and it sits outside the directory you thought was the seam.

**The boundary has two directions.** A rule that forbids the vendor above the seam says nothing about
the seam importing *upward* — a base component importing a feature, a page, a store. Left unruled,
"put it in the seam" becomes the way around every other boundary and the seam turns into a dump, which
is the same leak wearing the opposite coat. One rule per direction, and a fixture for the reverse: a
seam file that imports from above must fail.

## 1. Wall one — the import wall

Who may `import` the third party. It catches:

- a direct import of the vendor package, from any file except the seam;
- a **deep package path** (`vendor/src/internal/thing`) — the classic escape when the rule only
  matches the package's root name;
- a subpath or re-export chain (`vendor/features`, `vendor/compat`) that resolves to the same
  internals through a different string;
- a dynamic or deferred import (`await import(...)`) and a type-only import of a vendor type —
  type imports leak the vendor's shape upward exactly as loudly as value imports;
- a **layer skipping the seam**: a consumer reaching past the tier that is supposed to skin the
  vendor and importing the raw thing directly. This is the most common violation in a real tree and
  it looks completely reasonable in review.

It misses: anything resolved **without an import**. That is not a corner case; it is the default for
any framework that resolves components at build time.

## 2. Wall two — the markup wall

Who may *use* the third party without importing anything. It catches:

- a vendor tag written directly in a template or in markup-producing code;
- a vendor **utility class** on our element (`class="…vendor spacing token…"`) — the vendor's
  stylesheet then owns our layout, and no import ever happened;
- a raw platform control reaching around the seam (a native input, a native dialog element);
- a vendor name inside an identifier, a CSS class we author, or a data attribute the skin keys off.

A framework with auto-import, global registration, or a compiler transform leaves **nothing for the
import rule to find**: the file imports nothing, the tag works, the type-checker is satisfied, and
the strictest import lint in the world reports a clean tree. If your framework can do that, the
markup wall is the only wall.

## 3. The probe that decides which wall you need

Do not reason about this; run it. It costs one file and one build.

```
1. Write a file that uses the vendor's component in markup, with no import and no registration.
2. Build it with the real toolchain (not the editor, not the type checker alone).
3. Read the result.
```

**In a drifted tree, look for the probe already present before writing one.** Any `.vue` (or JSX) file
that uses a vendor tag with no import in the same file, and ships, has already answered the question: the
build resolved a name nobody declared. That is better evidence than a probe you write, because it is the
real configuration doing the real thing on a real route.

| Result | What it means | What you must build |
| --- | --- | --- |
| it compiles and renders | the import wall is decorative | the markup wall is mandatory; add it before the sweep |
| it fails to compile | imports are the only route | the import wall is sufficient — arm it anyway (§4) |
| the type-checker complains but the build succeeds | you have two authorities and the build is the one users get | gate on the build, not on the checker |
| it renders only after something else pulled the vendor in | the leak is order-dependent | markup wall, plus a check that runs on the whole tree, not per file |

The same question in the other paradigm: in a JSX/hyperscript tree with an auto-import plugin, a
bare `<VendorCard/>` or an `h(VendorCard, …)` call with no import is the identical leak. In a
class-utility system, the scanner that generates CSS for classes it has never seen is the identical
leak. The shape to recognise is "**the toolchain resolves a name I never declared**" — if it can do
that for anything, it does it for the vendor.

## 4. Two walls, one rule registry

Two auditors, one registry of rule codes, and each auditor's message names the doc section that
explains it. Never let a rule's own message be the only place its reason exists, and never let the
second auditor share the first auditor's baseline file — see
[arming-the-gate.md](./arming-the-gate.md) §5.

Keep an exemption list in one audited place. An allowlist plus an exemption marker that nobody reads
is two exemptions, and they will disagree within a month.

## 5. What this file does not own

- Which tier a component belongs to, and the Page/View/Component roles: `pvc`. The seam only says
  which layer may *name* the vendor's internals (that bill is
  [ownership-transfer.md](./ownership-transfer.md)).
- What the library itself wants to be used like: `treat`.
- Whether the swap is worth it visually: `spike`.
- The commit message on the sweep: `commit`.
