# Format divergence: when the same data wears different clothes

The class: one side reformatted (pretty↔minified, key order, EOL,
indentation), the other changed values. Line-based merge sees the *whole
file* as changed on both sides. The semantic delta may be four added keys.
This file is the ordered ladder from diagnosis to durable fix. **The order
is the point** — most bad merges happen because an agent jumped to step 5
with a text tool.

Meta-rule from the ASE 2024 measurement (`IncorrectCost ≫ UnhandledCost ≫
CorrectCost ≈ 0`): every rung that risks being wrong must *fail loudly*
instead. And the empirical asymmetry: **simple format-specific rules beat
general clever algorithms** (a trivial imports-augmentation outperformed
AST merge tools in the same paper; a 60-line 3-way JSON driver beat
`jq -s '*'` here).

## Step 0 — Classify the file before touching it

| Class | Examples | Route |
|---|---|---|
| hand-written structured data | config JSON/YAML/TOML, i18n catalogues, manifests | steps 3–5 |
| derived/generated artifact | lockfiles, `dist/*.min.js`, generated clients, snapshots | step 1 |
| opaque asset | images, fonts, PDFs, binaries, model weights | step 2 |
| record table | CSV/TSV, SQLite | step 6 |

Evidence for the taxonomy: gitattributes defines a driver per class, and
describes `binary` as *"suitable for binary files that do not have a
well-defined merge semantics"*. npm and yarn both route lockfiles out of
the text merge entirely. If the repo hasn't declared classes, **add
`.gitattributes` now** — that is the durable fix, not a merge hack.

## Step 1 — Generated artifact: do not merge it

Take one side of the **source** (`package.json`, `.proto`, templates),
resolve the artifact by `git checkout --theirs <artifact>` (or delete it),
run the installer/builder, commit the regenerated output.

Evidence: npm's own "merge driver" re-runs the resolver and rewrites the
lockfile format (R6 replay); yarn's maintainer answer is
`yarn.lock merge=binary` + reinstall; practitioner consensus: don't commit
`dist/` at all. Guard rail: **regeneration is version-sensitive** — npm 11
turned a v1 lockfile into v3, so the merge silently depended on the tool on
PATH. Pin the generator (`lockfileVersion`, corepack) or the artifact is
not reproducible. **Never hand-splice a lockfile.**

## Step 2 — Opaque asset: declare a side, never line-merge

`merge=binary` keeps ours verbatim, marks the path conflicted, and
preserves the stages for inspection (`git ls-files -u`). Resolution is a
decision (`--ours`/`--theirs`/re-export from the design source), plus LFS
for size. Never "take both" bytes. Lab: S10 (text merge of binary content
conflicts with a NUL-bytes warning and no usable markers).

## Step 3 — Canonicalize before deciding anything

Compare semantics, not bytes:

```bash
jq -S -c . FILE                    # sorted keys, one line — reorder-invisible
python -c "import json;print(json.dumps(json.load(open(F,encoding='utf-8')),sort_keys=True,separators=(',',':')))"
jd A B                             # no output == no semantic change; exit 1 == real change
jd -set / -mset -setkeys '[…]'     # when order is semantically meaningless
```

Normalize EOL as part of this (jq emits CRLF on Windows — measured). Then
read the **stages**, not the marked-up worktree: `git show :1/:2/:3:FILE`.
The base turns "both rewrote this file" into "main changed X, feature added
Y".

## Step 4 — Semantic diff empty on one side ⇒ pure-format conflict

Adopt the **other side's bytes**; port nothing. Do *not* reflow into your
own preferred formatting as the resolution — that is how the next merge
breaks the same way. Root-cause fixes instead: format at commit (`prettier`
+ `lint-staged`, or `git-format-staged` which formats objects in git's
database without touching unstaged work), plus `* text=auto` +
`git add --renormalize .` for EOL.

Cheap tries before any tooling:
- `git merge -X ignore-all-space` (also `ignore-space-change`,
  `ignore-cr-at-eol`) — roughly one in eight conflicts is whitespace-only,
  and space-aware `ort` measurably beats default `ort` (48% vs 46% correct in
  the ASE benchmark). Limitation from the docs: *"Whitespace changes mixed
  with other changes to a line are not ignored."*
- `git merge -X renormalize` — runs the clean filter on all three sides
  first; R4b transcript: a pure CRLF/LF flip disappears entirely.

## Step 5 — Both sides changed real data: leaf-wise 3-way, never 2-way

```
leaf:   ours==base -> theirs | theirs==base -> ours | ours==theirs -> ours
        | else CONFLICT(path)
dict:   union of keys, each recursed; add/delete per key against base
array:  POLICY MUST BE EXPLICIT — replace | append | set | identity-keyed
```

Real tools, not hand-editing markers: `jd` to see the change set;
`jsonmerge` (PyPI; per-key strategies declared in a schema, incl. `append`)
or a registered custom driver (`*.json merge=<driver>` in
`.gitattributes`) for automation; **Mergiraf** (JSON/YAML/TOML/XML;
`mergiraf merge --git`, commutative parents/signatures) for syntactic
merging across a polyglot tree. Windows note (reproduced): the driver
string needs **backslash-quoted binary paths** — the docs' bare form
assumes PATH availability.

Prohibitions, all reproduced in lab/replays:
- **never `jq -s '.[0] * .[1]'` as a merge** — two-way overlay silently
  reverted ours and resurrected a deletion (it has no base to notice
  deletions against);
- **never `merge=union` on structured text** — produced two concatenated
  JSON objects (which `jq` reads as a *stream* — see step 7) and a CSV with
  duplicate primary keys, both accepted with **exit 0** (S11);
- **never two-way anything**: every rule above consults the base.

Prefer registering the driver over ad-hoc resolution: it covers rebase,
cherry-pick and revert too (same machinery), and it **fails loudly** when
the shape surprises it. Keep `merge.conflictStyle=diff3`/`zdiff3` for
residual conflicts — but note Mergiraf warns `zdiff3` can break a driver's
tree reconstruction.

## Step 6 — No line-level record identity ⇒ stop using lines

CSV/TSV, tables, multi-line records inside minified code: line-merge gives
per-line conflicts without record semantics; union gives duplicate records.
Merge through the loader with an explicit key, or declare `merge=binary`
and let one side re-produce the table. Minified code: the atom is the whole
file — regenerate from source (step 1).

## Step 7 — Verify like it was a release, because it is

```bash
jq -e . FILE                        # parses?
python -c "import json;json.load(open(F,encoding='utf-8'))"   # STRICT parser
jq 'keys' FILE                      # duplicate keys?
jd base.json merged.json            # delta vs base == ours+theirs intents, nothing else
git diff --no-index ours.json merged.json    # nothing accidentally reverted
git diff --no-index theirs.json merged.json  # nothing accidentally dropped
```

The cautionary tale: **`jq` exit 0 does not mean "valid single JSON
document"** — jq parses a *stream*, so its own union garbage passes.
Verification must use a strict parser or count top-level documents. Also
confirm regeneration actually ran (step 1 files) and that a lockfile's
format version did not move under you.

## Step 8 — Encode the decision so this conflict never recurs

`.gitattributes` is the persistent form of this ladder:

```gitattributes
* text=auto
package-lock.json merge=binary          # + regenerate policy in AGENTS.md
src/locales/**.json merge=mergiraf      # or merge=<custom-driver>
dist/** merge=binary -diff
**.json diff=jd                         # reviewable JSON diffs
```

Team policy → `.gitattributes`; only-your policy →
`$GIT_DIR/info/attributes` (highest precedence, untracked); per-user global
→ `core.attributesFile`. `mergiraf languages --gitattributes` generates its
own list.

## Worked replay (real project, R7)

The locale case from `conflict-method.md`, run through the ladder
mechanically: classify (hand-written structured JSON) → canonicalize
(stages: base and feature minified 1 line, main pretty ~1117) → leaf-wise
union against base → **added=4, removed=0, changed=0** → strict-parser
verify → compare against the human historical resolution: **semantically
equal** (mergiraf wasn't on PATH in that environment; the python union
fallback rung produced the same result — the ladder degrades by rung, not
by verdict).
