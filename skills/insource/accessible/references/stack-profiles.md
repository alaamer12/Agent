# Deriving a stack profile

`mode-audit.mjs` and `rollout/map.mjs` have no idea what framework you are on. They read a
**stack profile** — a small JSON file holding the patterns that differ between projects. Shipped
starting points live in `assets/stack-profiles/`: `base` (neutral), `vue-tailwind`,
`react-tailwind`, `plain-css`. None of them is yours; copy the closest and fix it.

```
node scripts/mode-audit.mjs --requested ultra --profile vue-tailwind --against <rev>
node scripts/mode-audit.mjs --requested ultra --profile ./my-stack.json --before ... --after ...
```

## Why this exists rather than a hardcoded default

The first version of the grader shipped with a Tailwind colour regex baked in. Run against a
Sass project with no utility classes, that regex matches **nothing**, so the tool reported "0 raw
colours — the pass is clean" on a codebase full of hex literals. It did not crash. It produced a
confident, wrong, *passing* answer.

A rule that cannot match anything is indistinguishable from a rule that found nothing. So the
patterns are data, the data is per-project, and every measure the profile cannot take is printed
as **NOT MEASURED** instead of 0. When you fill one in, the failure to avoid is a null you
mistook for a clean result.

## Deriving it: the five greps

Run these at the project root. Each answers one knob.

**1. Which files hold the UI?** → `exts`
```
git ls-files | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -15
```
Include the file that declares routes. A grader that scans only view files will not see the
router at all — that exact omission made a 16-route re-architecture measure as zero renames.

**2. Is there a utility-class colour layer, and what are its hue names?** → `colour.utilityClasses`
```
grep -rhoE 'class="[^"]*"' src | grep -oE '\b(text|bg)-[a-z]+-[0-9]{2,3}' | sort -u | head -30
```
If that returns rows, copy `vue-tailwind.json`'s pattern and edit the hue list to the ones you
actually see (Tailwind v4 ships `stone/mauve/olive/mist` variants that the default list omits). If
it returns nothing, set it to `null` — honestly, because the tool will then say so.

**3. How are design tokens declared?** → `colour.tokenDefinitions`
```
grep -rhoE '^\s*(--[a-z-]+:|\$[a-z-]+:|@[a-z-]+:)' src --include=*.css --include=*.scss | head
grep -rn "@theme\|createTheme\|extendTheme" src | head
```
A CSS-in-JS theme object needs a pattern that matches *its* shape, or the "was the palette
rebuilt" criterion measures nothing.

**4. Where are routes declared, and how are redirects written?** → `routes.*`
```
grep -rlE "(createRouter|BrowserRouter|defineRoute|Route path)" . --include=*.{ts,tsx,js,jsx} | head
```
Open the top result. Copy one real declaration and one redirect verbatim into
`declarationPattern` / `redirectStubPattern`. The redirect stub must be stripped before counting,
or every retired path still looks declared and renames never register.

**5. What prefixes mark your own shared components?** → `components.localPrefixes`
```
grep -rhoE "import [A-Z][A-Za-z]+ from '\.[^']*(components|ui)/" src | awk '{print $2}' | sort -u | head
```
These drive the "used in markup but never imported" check, which catches the failure a compiler
cannot see: an unknown element renders as a blank hole and errors nowhere. Leave empty to disable
the check — never guess a prefix, because a wrong one silently skips the component it should flag.

## Sanity-check the profile before trusting it

Two tests, both cheap, both designed to make the profile prove it can fail.

**It must find what you know is there.** Pick a file you can see has raw hex colours or utility
classes in markup. Run the map over it. If that file reports "0 raw colours", the pattern is
wrong and every green row in the report is meaningless.

**It must go blind when the rules are removed.** Copy the profile, set `colour.utilityClasses`
and `colour.inlineLiterals` both to `null`, re-run. The output should flip to "colour rule not
configured" and report **zero** pages as converted. If it still says converted, the tool is
reading a zero as a pass and no profile will save you.

## What the thresholds are, and how to set them

`rampMinTokens` / `rampGrowthFactor` decide when "the palette was rebuilt" stops being a
re-skin. They are relative to what the project started with, so:

- A project with 5 ad-hoc hex values becoming 40 tokens is a genuine rebuild — set the factor
  high (1.5–2) and the floor low.
- A project that already had 400 tokens is *not* rebuilding the palette by adding 30 more. Raise
  the floor until the criterion means something for your starting point, or accept that this
  criterion cannot be met and say so in the report rather than quietly tuning it to green.

That second clause matters: the temptation when a gate reads "failed" is to loosen the number
until it passes. If you adjust a threshold, write the reason in the profile's `$comment` so the
next reader can tell calibration from capitulation.

## Reuse across a monorepo

Different apps in one repo can need different profiles — an admin Vue app and a marketing Astro
site share almost nothing. Keep one profile per app next to it (`.stack-profile.json`) and pass
that path. Do not average them into one file; a merged pattern list silently widens what each
measure considers "found".
