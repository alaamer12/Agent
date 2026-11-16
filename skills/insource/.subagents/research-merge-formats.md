# Research — `merge` skill, wave 2: non-plain-text & format-divergent content

Domain covered here: **JSON / minified-vs-pretty / generated artifacts / semantic (AST-aware) merging.**
Git internals and general practitioner practice are other agents' lanes; git mechanisms are used here as *tools*, cited only where a claim depends on them.

Method: WebSearch + WebFetch against primary docs (git-scm.com, mergiraf.org, Codeberg/GitHub/PyPI/npm metadata APIs, project READMEs), then **every load-bearing claim reproduced locally** in scratch repos under
`C:\Users\amrmu\AppData\Local\Temp\mergefmt\` (`d1`, `d3`, `d4a`, `d4b`, `d5`, `d6`, `d7`, `d8`, `d9`; scripts `d1.sh … d9.sh`, custom driver `json3way.py`).

Confidence labels used: **VERIFIED** = reproduced on this machine with the transcript below; **SOURCED** = quoted from a primary doc, not reproduced; **UNVERIFIED** = could not confirm.

---

## 0. Machine baseline (measured, not assumed)

```
git version 2.46.2.windows.1
Python 3.11.9            pip 24.0
node v24.16.0  npm 11.13.0  npx 11.13.0   bun 1.4.4
jq  -> NOT installed; obtained as a single static binary (see §1)
PyYAML 6.0.3 present; ruamel.yaml NOT installed; git-lfs hooks present in global config
global git config: core.autocrlf = true  (a live cause of the whole-file churn this skill is about)
```

---

## 1. Tool inventory — what actually exists, who maintains it, did it run here

| Tool | Where it comes from | Maintenance state (queried live 2026-11-16) | Ran on this machine? |
|---|---|---|---|
| **jq 1.8.2** | github.com/jqlang/jq releases, `jq-win64.exe` | latest release `jq-1.8.2` | **YES** `./jq.exe --version → jq-1.8.2` |
| **Mergiraf 0.20.0** | codeberg.org/mergiraf/mergiraf releases, `mergiraf_x86_64-pc-windows-gnu.zip` | v0.20.0 published **2026-09-26**; steady ~monthly cadence (0.17→0.20 across 2026) | **YES** `mergiraf --version → mergiraf 0.20.0` |
| **jd 2.5.0** (JSON diff & patch, Go) | github.com/josephburnett/jd, `jd-amd64-windows.exe`; docs jd-tool.io | v2.5.0 published **2026-02-23** | **YES** `jd --version → jd version 2.5.0` |
| **Difftastic 0.72.0** | github.com/wilfred/difftastic, `difft-0.72.0-x86_64-pc-windows-msvc.zip` | 0.72.0 published **2026-10-29** | **YES** `difft --version → Difftastic 0.72.0` |
| **npm-merge-driver 2.3.6** | npm `npm-merge-driver` (github.com/npm/npm-merge-driver) | latest published **2020-03-26** (6 yrs stale) but still npm's official answer | **YES**, run through `bun x npm-merge-driver@2.3.6` |
| **jsonmerge 1.9.2** (PyPI) | pypi.org/project/jsonmerge — Tomaz Solc | latest upload **2023-07-19** | **YES** (`pip install --target`, merge + schema `append` strategy) |
| **merge3 1.0.0** (PyPI) | pypi.org/project/merge3 — github.com/breezy-team/merge3 (Breezy/bzr) | v1.0.0 uploaded **2026-10-25** — alive; it is a **line**-based 3-way text merge, not JSON | installed, not exercised |
| **json-merge-patch 0.3.0** (PyPI) | open-contracting/json-merge-patch, RFC 7396 | uploaded **2025-03-25** | not run |
| **deepmerge 4.0.0** (PyPI) | toumorokoshi/deepmerge | uploaded **2026-10-25** — alive | not run |
| **jsondiff 2.2.1** (PyPI) | xlwings/jsondiff | uploaded **2024-08-29** | not run |
| **weave** (entity-level git merge driver) | github.com/Ataraxy-Labs/weave | **1,361 stars, release v0.7.1 2026-11-02, last push 2026-11-14**, Apache-2.0/MIT, Rust, 38 languages | **NO** — Homebrew + `cargo install --path crates/weave-cli` / `crates/weave-driver`; no Windows artifact usable here |
| **git-hires-merge** | github.com/paulaltin/git-hires-merge | 71 stars, last push **2026-10-31**, GPL-3.0, Python | **NO** — `pip install git-hires-merge` → *"Could not find a version that satisfies the requirement"*; **not on PyPI**, must be installed from git |
| **Spork** (AST 3-way merge for Java) | github.com/ASSERT-KTH/spork | 72 stars, last push **2025-02-25** (~21 months dormant), academic | **NO** (Java build) |
| **IntelliMerge** | academic, graph-based, Java-only | see ASE 2024 evaluation below | **NO** |
| **plume-lib/merging** (Imports / Version-Numbers / IVn merge drivers) | github.com/plume-lib/merging | 16 stars, last push **2026-11-16** (today) — the ASE 2024 paper's own tools, documented as git merge drivers | **NO** (not fetched/built here) |
| **`dq`** (structural editor for JSON/YAML, massoverlaod/dq) | github.com/massoverlaod/dq | `releases/latest` returned **no release tag** → no install-free artifact | **NO** — blocked |
| **jqjs / git-merge-json / json-merge-driver / merge-driver-insensible / yarn-merge-driver** | npm | registry returned **404 Not Found** for all five | do not exist under those names |
| **`git-json-merge`** | npm | registry **200** — the only other real npm JSON-driver name found | not exercised |
| **`jsonmerge3`, `jsoneq`, `@semantify/merge-json`, `git-merge-yarn`, `yarn-merge-driver`** | PyPI / npm | **404 — these names do not exist** | n/a |

Corrections to the research brief, stated plainly:
- **"jsonmerge3" does not exist on PyPI** (`https://pypi.org/pypi/jsonmerge3/json` → `{"message": "Not Found"}`, `/simple/jsonmerge3/` → HTTP 404). The real adjacent package is **`merge3`** (Breezy's *line*-based 3-way merge). UNVERIFIED-as-named; the concept it was meant to point at is covered by `jsonmerge` + a custom driver.
- **"pixieMerge" is not findable as a tool.** GitHub repository search `q=pixieMerge` → `total_count: 0`. The related *research line* is real (Fei He's group: *"Mastery: Shifted-Code-Aware Structured Merging"*, SETTA 2022; *"On the methodology of three-way structured merge in structured-persistent languages"*, JSS 2023) — but no installable tool named pixieMerge was located. UNVERIFIED.
- **"CalMerge" as a Calit2 semantic git merge tool: not confirmed.** GitHub search `q=calmerge` returns 24 repos, all **calendar** merging (`cfenollosa/calmerge`, `torchbox/calmerge`, `shamanskyh/CalMerge` = "ICS merging … between iCloud and Google"). No semantic-merge CalMerge surfaced. UNVERIFIED; recorded as a dead route rather than filled in with a guess.
- The living, currently-maintained descendants of that research tradition are **Mergiraf**, **weave**, **git-hires-merge**, and **Spork** — and of those, only Mergiraf ran cleanly here with zero build.

---

## 2. Q1 — Normalize-then-merge doctrine

**The empirical anchor.** The ASE 2024 evaluation (Schesch, Featherman, Yang, Roberts, Ernst — https://arxiv.org/abs/2410.09934, DOI 10.1145/3691620.3695075) measured this directly:

> "A diff algorithm's readability does not materially affect its success for merging. **Handling whitespace is important, however: about 1/8 of conflicts are due to whitespace alone**."

and, on the shape of the problem:

> "Another example of an undesirable conflict is when Parent 1 changes the indentation of a line, while Parent 2 makes a code change to that line."

So one-eighth of real conflicts are pure formatting. That is the number the skill should quote, not vibes.

**Prettier's own position** (https://prettier.io/docs/precommit — SOURCED): normalisation belongs at *commit* time, not merge time. Six documented options, all of which run the formatter before the blob is written:
- Option 1 `lint-staged` — `npx mrm@2 lint-staged`; explicitly the option "if you need support for partially staged files (`git add --patch`)".
- Option 2 `pretty-quick` + `simple-git-hooks` — `.simple-git-hooks.json` = `{"pre-commit":"npx pretty-quick --staged"}`; bun variant `bun pretty-quick --staged`.
- Option 4 **`git-format-staged`** — the most interesting to this skill: *"it applies the formatter directly to objects in the git object database, and merges changes back to the working tree"*, guaranteeing *"Changes in commits are always formatted"* and *"Unstaged changes are never, under any circumstances staged during the formatting process"*. Wired up as `git-format-staged -f 'prettier --ignore-unknown --stdin --stdin-filepath "{}"' .`
- Option 5 Lefthook — `stage_fixed: true` so the formatted version is what gets committed.
- Option 6 raw shell hook, with the `git diff --cached --quiet` guard for "formatting removed all staged changes".
- Footnote worth keeping: *"If git is reporting that your prettified files are still modified after committing, you may need to add a post-commit script to update git's index"* → `git update-index -g`. That symptom is the EOL/filter round-trip problem, not a formatter bug.

**Mergiraf's own doctrine on this** (https://mergiraf.org/conflicts.html, section *Conflicting formatting and content changes* — SOURCED, verbatim):

> "When one side reformats the file and the other makes changes to its contents, Mergiraf attempts to retain both the new formatting and the new contents. … Merging formatting and content changes is done on a best-effort basis and is **bound to produce imperfect formatting in certain cases. Those types of conflicts are best avoided by enforcing a particular style via a linter.**"

That is the honest ceiling: the best available syntax-aware tool tells you the real fix is normalisation *before* the merge, not cleverness *during* it.

**`merge=union` — why Git itself forbids it for structured text** (https://git-scm.com/docs/gitattributes, *Built-in merge drivers* — SOURCED, verbatim):

> "**union** — Run 3-way file level merge for text files, but take lines from both versions, instead of leaving conflict markers. **This tends to leave the added lines in the resulting file in random order and the user should verify the result. Do not use this if you do not understand the implications.**"

Reproduced breaking JSON and CSV in R3 and R8e below.

**`-X renormalize` — the text-format equivalent of canonicalize-then-merge.** git-merge(1) (SOURCES: https://git-scm.com/docs/git-merge, *MERGE STRATEGIES → ort → renormalize*):

> "This runs a virtual check-out and check-in of all three stages of any file which needs a three-way merge. This option is meant to be used when merging branches with different clean filters or end-of-line normalization rules."

gitattributes(5) (*Merging branches with differing checkin/checkout attributes*):

> "To prevent these unnecessary merge conflicts, Git can be told to run a virtual check-out and check-in of all three stages of each file that needs a three-way content merge, by setting the `merge.renormalize` configuration variable."
> "As long as a 'smudge→clean' results in the same output as a 'clean' even on files that are already smudged, this strategy will automatically resolve all filter-related conflicts. Filters that do not act in this way may cause additional merge conflicts that must be resolved manually."

Also SOURCED from git-merge(1), the whitespace strategy options, because they are the cheap first try before any driver:

> "**ignore-space-change / ignore-all-space / ignore-space-at-eol / ignore-cr-at-eol** — Treats lines with the indicated type of whitespace change as unchanged for the sake of a three-way merge. **Whitespace changes mixed with other changes to a line are not ignored.**"

That last sentence is the limitation: a reformatter that re-wraps a line *while* changing content on it is not rescued by `-X ignore-all-space`.

EOL mechanics from gitattributes(5) `text` / `eol`: `text` set ⇒ normalise to LF in index; `eol` only matters when `text`/`text=auto` is set; *"If `text` is set but neither of those variables is, the default is `eol=crlf` on Windows and `eol=lf` on all other platforms"*; and the normalisation procedure is `echo "* text=auto" >.gitattributes; git add --renormalize .; git status; git commit -m "Introduce end-of-line normalization"`.

---

## 3. Q2 — JSON-aware merging

### 3.1 What `jq`'s operators actually do (VERIFIED, R2)

```
$ jq -cn '{"a":{"b":1}} * {"a":{"c":2}}'   ->  {"a":{"b":1,"c":2}}     # recurses into objects
$ jq -cn '{"a":[1,2]} * {"a":[3]}'         ->  {"a":[3]}               # arrays REPLACED, never concatenated
$ jq -cn '{"a":1,"b":2} * {"a":null}'      ->  {"a":null,"b":2}        # null is a VALUE, not a delete
$ jq -cn '{"v":"1.0.0"} + {"v":"1.0.1"}'   ->  {"v":"1.0.1"}           # '+' = shallow, RHS wins
```

Two doctrine-critical consequences:
1. **`*` is an overlay, not a merge.** It has no ancestor, so "which side is the change and which side is the default" is unanswerable — whoever is on the right wins every scalar collision. Proven destructively in R2 §4: `jq -s '.[0] * .[1]' ours theirs` silently **reverted** main's `version` bump from `1.0.1` back to feature's `1.0.0`, exit code still 0, no conflict, no warning.
2. **`*` cannot express deletion.** R2 §5: base `{a,b,gone:3}`, ours `{a,b,gone:4}`, theirs `{a,b}` → `.[0] * .[1]` = `{"a":1,"b":2,"gone":4}`. The deleted key comes back. Same reason `null` is a value: a two-way deep merge has no place to put "absence".
   (Contrast RFC 7396 JSON Merge Patch, where `null` *does* mean delete — `json-merge-patch` on PyPI/npm implement that; they are different semantics and the difference is the whole bug.)

### 3.2 The correct mechanical rule (VERIFIED, driver in R4)

A JSON merge is **leaf-wise three-way**, and the only sound table is:

```
ours == base          -> take theirs          (incl. theirs' deletion)
theirs == base        -> take ours            (incl. ours' deletion)
ours == theirs        -> take ours            (both made the same change)
both dicts, differ    -> recurse per key
both leaf/array, differ -> CONFLICT at that path   (arrays atomic unless you declare identity)
```
Equality on the leaves is tested on the **canonical form** (parsed + sorted keys), never on bytes — that is what makes a reformat a no-op.

I implemented exactly this as `json3way.py` and registered it as a real git merge driver. All four cases behaved as designed (R4).

### 3.3 git custom merge drivers — the authoritative contract (SOURCED)

gitattributes(5) *Defining a custom merge driver*, verbatim:

```
[merge "filfre"]
        name = feel-free merge driver
        driver = filfre %O %A %B %L %P
        recursive = binary
```
> "The `merge.*.driver` variable's value is used to construct a command to run to common ancestor's version (`%O`), current version (`%A`) and the other branches' version (`%B`). These three tokens are replaced with the names of temporary files that hold the contents of these versions when the command line is built. Additionally, `%L` will be replaced with the conflict marker size."
> "The merge driver is expected to **leave the result of the merge in the file named with `%A` by overwriting it, and exit with zero status if it managed to merge them cleanly, or non-zero if there were conflicts.** When the driver crashes (e.g. killed by SEGV), it is expected to exit with non-zero status that are higher than 128, and in such a case, the merge results in a failure (which is different from producing a conflict)."

That crash-vs-conflict exit-code rule (129+ = failure, 1..128 = conflict) is the thing most hand-rolled drivers get wrong and is worth a line in the skill.
`merge.*.recursive` = "what other merge driver to use … for an internal merge between common ancestors, when there are more than one" — the criss-cross case; "When left unspecified, the driver itself is used for both internal merge and the final merge."
Selection: `*.json merge=<driver>` in `.gitattributes`; per-repo untracked control in `$GIT_DIR/info/attributes` (highest precedence); per-user global in `core.attributesFile` (default `$XDG_CONFIG_HOME/git/attributes`).

### 3.4 jsonmerge (PyPI) — schema-declared merge strategy (VERIFIED it runs)

```
$ pip install --target /tmp/mergefmt/pylibs jsonmerge
$ PYTHONPATH=/tmp/mergefmt/pylibs python - <<'PY'
import jsonmerge
jsonmerge.merge({'a':1,'nested':{'x':1,'y':2}}, {'a':2,'nested':{'y':99,'z':50}})
#   -> {'a': 2, 'nested': {'x': 1, 'y': 99, 'z': 50}}      (recursive object merge)
jsonmerge.merge({'tags':['a']}, {'tags':['b']},
                {'properties':{'tags':{'mergeStrategy':'append'}}})
#   -> {'tags': ['a', 'b']}                                 (array policy declared in the schema)
PY
```
The lesson jsonmerge encodes, and the skill should encode: **array behaviour is not a tool question, it is a schema question.** `replace` / `append` / `unique` / `numericAddition` per key, declared where the data's meaning is declared.

### 3.5 Lockfile drivers are living evidence (VERIFIED end-to-end, R6)

`npm-merge-driver` exists, runs, and is documented as *"git merge driver for automatically merging lockfiles"* (npm description). `install` wrote:
```
merge.npm-merge-driver.name automatically merge npm lockfiles
merge.npm-merge-driver.driver npx npm-merge-driver merge %A %O %B %P
```
plus attribute lines in **`.git\info\attributes`** (not `.gitattributes`), and printed `npm-merge-driver: npm-merge-driver installed to \`git config --local\` and .git\info\attributes`.
`git check-attr merge -- package-lock.json` → `package-lock.json: merge: npm-merge-driver`.

**What the official driver actually does is NOT merge.** During the real merge it re-ran the resolver — its own output was `npm-merge-driver: merging package-lock.json` → `up to date, audited 2 packages in 2s` → `npm-merge-driver: package-lock.json successfully merged.` — and the result was rewritten from `lockfileVersion: 1` to `lockfileVersion: 3`, dropping the two entries that existed only in the lockfile and keeping the one derivable from `package.json`. Its README documents exactly this shape:
```
$ git merge my-conflicting-branch
npm WARN conflict A git conflict was detected in package-lock.json. Attempting to auto-resolve.
added 1 package in 0.077s
```
so npm's own "merge driver" is a **regeneration driver** (`-c, --command` lets you choose the command). Doctrine: a lockfile is a *derived* artifact; the merge is performed by the resolver against `package.json`, not on text.
Caveat worth stating: it invokes **`npx`**, so under a bun-only toolchain the driver is a hidden npm dependency, and the regenerated format depends on whatever npm version is on PATH — here npm 11 silently produced a v3 lockfile from a v1 one.

Yarn's community answer is the same conclusion reached from the other direction: yarnpkg/yarn issue **#2155 "Deal with lockfile merge conflicts in some way"** proposes `.gitattributes` with `yarn.lock binary` — *"This will make git ignore conflicts and line endings, like if file was binary"* — and the widely-repeated practice (stackoverflow 42939113; dev.to "Let Yarn Resolve Your Conflicts"; medium/@drdmason) is *delete the conflicted lockfile and re-run the installer*.

---

## 4. Q3 — AST-aware / semantic merge tools that exist today

### 4.1 Mergiraf — the one that runs (VERIFIED, R5)
- Docs https://mergiraf.org/ ; repo https://codeberg.org/mergiraf/mergiraf ; book chapters *Conflicts solved, limitations*, *Supported languages*, *Usage*.
- Mechanism (docs, SOURCED): tree-sitter-based syntactic merge with per-language **"commutative parents"** (contexts whose child order is irrelevant) and **"signatures"** (keys that must be unique among children of a commutative parent). Its own Java example: both sides add a different field to a class ⇒ auto-resolved, *because field order does not matter*; but both sides add a different statement inside a `while` body ⇒ **conflict**, "given that the order in which they are inserted matters". That is a *principled* answer to "array policy" that most tools leave implicit.
- Docs also flag the honesty case: *"Strictly speaking, the order of declaration of class attributes or methods in Java can have an influence on program execution (for instance via the use of reflection). Explicit reliance on this order is broadly discouraged so this tool assumes that such conflicts can be resolved without human intervention."*
- Registration (usage.html, SOURCED verbatim):
  ```
  git config --global merge.conflictStyle diff3
  git config --global merge.mergiraf.name   mergiraf
  git config --global merge.mergiraf.driver 'mergiraf merge --git %O %A %B -s %S -x %X -y %Y -p %P -l %L'
  # ~/.config/git/attributes:  * merge=mergiraf      (or *.json merge=mergiraf etc.)
  mergiraf languages --gitattributes        # generates the full include list
  ```
  **Why diff3 is mandatory, in their words:** *"Mergiraf will try to resolve conflicts by reconstructing the base, left, and right revisions. The default style, `merge`, doesn't provide the information about the base revision at all. And `zdiff3` … pulls the changes common to the left and right revision out of the conflict … if both sides end with a brace, zdiff3 will pull it outside, so the reconstructed base revision will have unbalanced braces and thus fail to parse."* — a brace-level detail that decides whether a JSON driver works at all.
- Other documented switches: `--fast` (solve textual conflicts only, no full structured rebuild), `-t/--timeout` (ms, falls back on git's algorithm), `--allow-parse-errors` (default-enabled for C/C++/HTML), `-c/--compact` (sub-line conflict markers), `--language`/`-L`, `mergiraf.language` and `linguist-language` gitattributes, `mergiraf=0 <git cmd>` to disable once, `mergiraf review <merge-id>` and `mergiraf report <file>`, and *"For best results, use Git v2.44.0 or newer."*
- Formats confirmed on this machine: `mergiraf languages` lists **JSON (\*.json)**, YAML, TOML, XML, INI, plus Java/Kotlin/Rust/Go/go.mod/go.sum etc.; `mergiraf languages --gitattributes` emitted `*.json merge=mergiraf`, `*.yaml merge=mergiraf`, `*.toml merge=mergiraf`, `pyproject.toml merge=mergiraf`.
- **Verified result on the owner's exact scenario (R5 A/C):** plain `git merge-file` ⇒ CONFLICT; `mergiraf merge` ⇒ `INFO Mergiraf: Solved 1 conflict.`, exit 0, output carried **both** main's `version: "1.0.1"` and feature's `telemetry: true`, in feature's pretty formatting. Same result through a real `git merge` with the driver registered.
- **Verified duplicate-key guard (R5 B):** with left and right each adding `"new"` at a different position, `git merge-file` exits **0** and emits one object containing `"new"` **twice**; `mergiraf` exits 1 and emits a narrow three-way conflict around only that entry. And the loss is silent downstream: `jq '.new'` → `"right value"`, `python -c json.load(...)['new']` → `right value`. The left value simply ceases to exist.
- Limitation it states about itself (SOURCED): *"if the files merge cleanly using Git's usual line-based merging algorithm, so will they with Mergiraf"*, *except* the duplicate-signature case above. So Mergiraf does not un-minify; it does not "fix" a whole-file-reformat conflict by itself either — it wins because it merges trees, not because it is magic.

### 4.2 weave — the most current multi-agent-oriented tool (SOURCED, not runnable here)
github.com/Ataraxy-Labs/weave. *"Entity-level semantic merge for Git. Resolves merge conflicts that Git can't by parsing code into functions, classes, and keys with tree-sitter, then merging those entities instead of lines."* 1,361 stars; **v0.7.1 released 2026-11-02; last push 2026-11-14**. Apache-2.0 OR MIT, Rust, 38 languages.
Its framing is exactly the current agent-workflow problem: *"This happens constantly when multiple AI agents work on the same codebase. Agent A adds a function, Agent B adds a different function to the same file, and Git halts everything for a human to intervene."*
Setup: `brew install weave`, or two crates — `cargo install --path crates/weave-cli` and `cargo install --path crates/weave-driver` (*"weave setup fails without it on PATH"*); then `weave setup` (`--local` → `.git/info/attributes`, `--global` → `~/.config/git/attributes`, `--off`), and `git merge` is unchanged. Conflict markers carry a reason line: `// refused_by: statement_fold · collision: ...`. Commands: `weave explain <file>`, `weave check` (exit 1 findings, 2 couldn't verify), `weave land --resolver <cmd>` labelling each file PROVEN/VERIFIED/REFUSED, `weave stats --bench`.
Two doctrinal nuggets worth stealing:
- *"This merge algorithm is deterministic and stateless: it reads three file revisions and writes one result, the same way `git merge-file` does. It is not a CRDT."*
- Its benchmark table refuses to look better than it is: 31 scenarios / 7 languages, **two of which it deliberately will not merge** — *"When both sides add different decorators to the same Python or TypeScript function, decorator application is function composition, so the stack order is a semantic decision neither side made — `@cache` outside `@auth` serves cached responses without ever running the auth check. Weave refuses rather than fabricate an order, **and a tool that merges those cleanly is wrong, not better.**"* Real-repo replay (first 500 merge commits per repo, comparing to the human-authored merge): git/git 1,701 file-merges, 183 wins / 23 regressions / 72% human-match; CPython 256, 11/10/45%; Go 1,667, 120/37/33%; TypeScript 1,280, 15/… It also states *"Vue, Svelte, ERB, Haskell parse, but their per-file entity model is too coarse to merge well, so they take Git's line merge, always."*
- The "human match" caveat matters for the skill: a clean auto-merge is **not** the goal; matching what the developer intended, or refusing, is.

### 4.3 The research verdict on all of this (SOURCED — arxiv 2410.09934, ASE 2024)
Evaluated tools: **Git Merge** (ort / ort-ignorespace / recursive-{histogram,minimal,myers,patience} / resolve), **Hires Merge** (character-level, whitespace-ignoring, registered via `.gitattributes`), **IntelliMerge** (graph-based, Java-only, refactoring-aware, PEGs), **Spork** (AST 3DM-Merge + GumTree, Java-only, *"the most starred AST-based merge tool on GitHub"*), plus their own **Imports**, **Version-Numbers**, **IVn**.
Dataset: 42,092 Java repos → 294,714 merges → 6,045 merges where *both parents pass tests* (median 3 files touched by both parents). Method: run the project's own test suite as the correctness oracle; each test run 5× for flakiness.
Headline numbers, Git default `ort` (of the 5,983 merges measured for that configuration): **2,748 correct (46%), 3,078 unhandled (51%), 157 incorrect (3%)**. `ort-ignorespace`: **2,889 (48%) / 2,905 (49%) / 189 (3%)** — the whitespace flag buys ~2 points and is one of the largest single levers in the whole table.
Conclusions that bear directly on this skill:
- *"A merge algorithm that merely augments Git's handling of import statements **usually outperforms Spork, IntelliMerge, and other tools**. This suggests that finding simple solutions to common problems is a more effective approach to building a merge tool than complex algorithms that handle relatively uncommon cases."*
- *"IntelliMerge is rarely applicable. When it is applicable, it produces more incorrect merges than Git Merge does."*
- *"Spork is the best merge tool if incorrect merges cost no more than unhandled merges (k=1). But by k≈2, Spork is the worst tool other than IntelliMerge."*
- `IncorrectCost ≫ UnhandledCost ≫ CorrectCost ≈ 0`; *"Unhandled merges are easier because they come with location and diff information"* — the formal justification for **"prefer a loud conflict over a quiet wrong answer"**.
- *"Current merge tools work conflict-by-conflict … Accounting for the context of a conflict (e.g., other code in the same file) leads to better merges."* Their Imports tool: *"simply unioning the import lines in each git conflict performed much worse."* — i.e. **naive union loses even in the tool's own ablation.**
- *"Non-main branches have more challenging merges than main branches do."*
- Version-Numbers rule: when base/ours/theirs all differ and both edits are larger than base, take the largest. Directly reusable for `"version"` keys.
- Install path for the paper's tools: https://github.com/plume-lib/merging — *"which gives instructions for using them as git merge drivers, git mergetools, or to clean up conflicts at an arbitrary time."*

### 4.4 IDE 3-way merge as the industry norm (SOURCED, low depth — not this wave's lane)
VS Code: https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts — *"For more complex conflicts or when you want a side-by-side view of all changes, use the 3-way merge editor."* Visual Studio: https://learn.microsoft.com/en-us/visualstudio/version-control/git-resolve-conflicts. JetBrains ships its own three-way tool and (via Spork's authors' institution) is the origin of much AST-merge research. What the editors add over `<<<<<<<` reading is **the base pane**; none of them changes the merge algorithm. Historical C#/Java grammar-driven tool **git-unity**/"SemanticMerge" is described by DaedTech (Erik Dietrich, 2014, https://daedtech.com/merging-done-right-semantic-merge/) under the honest heading *"Standard Diff Tools are Bad at Telling You What Happened"*; Endjin's 2014 write-up is the integration recipe. I did **not** verify either is installable in 2026 — UNVERIFIED.

---

## 5. Q4 — Generated / minified artifacts: policy, not patching

**Git's own vocabulary for "don't merge this"** (gitattributes(5) *merge*, SOURCED verbatim):
> "**binary** — Take the version from the current branch as the tentative merge result, and declare that the merge has conflicts. **This is suitable for binary files that do not have a well-defined merge semantics.**"
> built-in driver **binary**: *"Keep the version from your branch in the work tree, but leave the path in the conflicted state for the user to sort out."*
> built-in driver **text**: *"Usual 3-way file level merge … Conflicted regions are marked with conflict markers."*
> `merge` Unset: same "take current branch + declare conflict" behaviour. `merge.default` config can name a driver for unspecified paths.
Also *Marking files as binary*: *"the content, while technically composed of text characters, **is opaque to a human reader**. For example, many postscript files contain only ASCII characters, but produce noisy and meaningless diffs."* → that is the minified-bundle case in Git's own words. Simplest marker: `*.ps -diff`. Escape hatch for *review* (not merge): `[diff "jpg"] textconv = exif` + `cachetextconv = true`, and `binary = true` when you want textconv for viewing but binary for merging.

**Minified/single-line artifacts are unmergeable by construction.** R8a: two branches each changed a *different function* inside one-line bundle; both edits were valid and independent; git reported a whole-line conflict, because the line is the atom:
```
<<<<<<< HEAD
function a(){return 1}function b(){return 2}function c(){return 30}
=======
function a(){return 1}function b(){return 20}function c(){return 3}
>>>>>>> feat
```
**Binary artifacts, exactly as the attribute promises** (R8b):
```
warning: Cannot merge binary files: bundle.js (HEAD vs. feat)
CONFLICT (content): Merge conflict in bundle.js
```
worktree keeps **ours verbatim, zero markers**; the three stages remain addressable (`git ls-files -u` → stages 1/2/3), so a tool/agent can decide; resolution is `git checkout --theirs <path> && git add <path> && git commit`.

**"Don't merge generated output, regenerate it"** — SOURCED positions: VibeReference *Should You Commit the dist/ Folder to Git?* → *"No. Add dist/ to your .gitignore and let your build pipeline generate it fresh every time."*; r/git *Compiled files and git* → *"In general, I counsel people to avoid committing build artifacts to the repo, for exactly this reason."*; and the strongest evidence is behavioural, from npm's own driver (§3.5) and yarn issue #2155: **the merge is performed by the resolver, not by a text tool.** If a generated file must be in VCS (release branches, docs sites, checked-in `Cargo.lock`-style determinism), declare it `merge=binary` and rebuild the losing side; if it must not, `.gitignore` it — but then the merge is *not your problem, and never a line merge*.
Distinguish **diff-on-source** from **merge-on-output**: you may want `textconv`/`jd`/`difft` to *review* the artifact, while the *merge* always happens on the source and the artifact is regenerated. That is exactly the `textconv` + `binary = true` combination gitattributes describes.

---

## 6. Q5 — "Which side is actually ahead?" Semantic diff tooling (VERIFIED, R7 & R9)

The question the agent must answer before touching a conflict: *did B really add a key, or only move it?* Three install-free-or-trivial answers, all run here:

**(a) jq canonical sort + byte compare — zero install beyond jq itself.**
```
$ jq -S -c . base.min.json    > c1
$ jq -S -c . reorder.min.json > c2
$ cmp -s c1 c2 && echo IDENTICAL canonical bytes
IDENTICAL canonical bytes
```
**Pure key reordering is invisible.** `jq --help` documents the flag as `-S, --sort-keys  sort keys of each object on output`.

**(b) python stdlib, no third-party at all (VERIFIED):**
```
python -c "import json;print(json.dumps(json.load(open('x.json')),sort_keys=True,separators=(',',':')))"
```
→ `IDENTICAL canonical form` for the reorder pair. This is the right answer on a locked-down machine.

**(c) `jd` — the real diff/patch tool, and a git diff driver.** (github.com/josephburnett/jd, jd-tool.io; *"jd is a commandline utility and Go library for diffing and patching JSON and YAML values. It supports a native jd format (similar to unified format)*"; v2.5.0.)
```
$ jd base.min.json reorder.min.json   -> (no output)   exit 0   # reorder = NOT a change
$ jd base.min.json pretty.json        -> (no output)   exit 0   # reformat = NOT a change
$ jd base.min.json pretty.newkey.json -> ^ {"file":"base.min.json"}
                                         @ ["telemetry"]
                                         + true                                   exit 1
$ jd base.min.json value.json         -> @ ["version"]
                                         - "1.0.0"
                                         + "1.0.1"                                exit 1
```
That is a complete, machine-readable answer to the owner's core question: **the only real change on the reformatted side is `+telemetry`.** Note jd's exit code is a *change* signal, exactly like `diff` — usable as a guard in scripts.

**jd as a semantic git diff driver (VERIFIED, R9)** — this is the highest-leverage one-liner in the whole report, because it changes what `git diff`/`git log -p` show forever:
```
$ printf '*.json diff=jd\n' > .gitattributes
$ git config diff.jd.name  "jd semantic JSON diff"
$ git config diff.jd.command "jd -git-diff-driver"
$ git check-attr diff -- data.json
data.json: diff: jd
$ git diff main~1 main -- data.json
^ {"file":"data.json"}
@ ["tags",0]
[
+ "b"
  "a"
@ ["tags",2]
  "a"
- "b"
]
```
(Mechanics note: gitattributes(5) says an external **diff** driver is *"called … with 7 parameters, just like `GIT_EXTERNAL_DIFF` program is called"* — **not** `%O %A %B`; those belong to **merge** drivers. My first attempt used `%O %A` and died with `fatal: external diff died`. Also relevant: `diff.<name>.trustExitCode = true` for tools that "return exit code 1 if it finds significant changes and 0 if it doesn't" — which is precisely jd's contract.)

**Array policy is a flag, not a guess** (VERIFIED): the pair `base` vs `feat` differed only by reordering `users` (two objects).
```
jd -          exit 1  (arrays ARE ordered per RFC 8259 — it reported the move as a change)
jd -set       exit 0  (arrays as sets: order irrelevant)
jd -mset -setkeys '["users=id"]'   exit 0  (match objects by identity key "id")
```
jd's help also exposes `-precision` (numeric tolerance) and a header echo (`^ {"setkeys":["id"]}`) *"to show how the diff was produced … and enables reproducible results"*. **A merge skill must state its array policy explicitly, per array, or its answers are not reproducible.**

**(d) difftastic 0.72.0** — structural diff, `difft FILE1 FILE2`, works and integrates with git (`GIT_EXTERNAL_DIFF` / a diff driver). Honest result on our case: on minified-vs-pretty+newkey it printed a side-by-side structural diff dominated by the reflow (exit 0). It is a *diff* tool; it is Mergiraf's recommended companion (*"Pssst! Why don't you install Difftastic too? … a fantastic structural diff tool which works great in combination with Mergiraf"*), but it does not answer "is this change real" for JSON the way `jd` does.

**`jiq`** (npm, 0.0.10, published 2020-12-13, bin `jiq`) — exists but 6 years stale and JS-REPL-shaped, not a batch differ. **`dq`** — blocked, no release artifact (§1). **`json-diff`** (npm, andreyvit, 1.0.6, 2023-05-15, bin `json-diff`) and **`deep-diff`** (1.0.2, 2018) exist as library/CLI diff helpers; not exercised here — UNVERIFIED behaviour.

---

## 7. Q6 — Ordering, canonicalization, and the non-JSON text formats

**JSON.** Objects are unordered by spec; git diffs lines; that gap *is* the bug class. Canonicalization is therefore the whole first move, and it has to be applied *asymmetrically*: canonicalise to **decide**, then emit in **one side's** format to commit. Emitting canonical form for both files as a mass rewrite is a repo-wide noise commit — the doctrine is one project style, enforced at commit (see §2 prettier/git-format-staged), not per-merge reflow.
Reorder-only changes are a **no-op** (VERIFIED with jq `-S`, python `sort_keys`, and `jd`), and Mergiraf's duplicate-signature conflict (§4.1/R5B) is the only tool behaviour I found that catches the *other* order bug: git merging cleanly into one object with the same key twice.

**YAML — the reformat trap is worse than JSON's, because the format has content git can't see.** VERIFIED with stdlib PyYAML 6.0.3 (R8c):
```
original:                              after yaml.safe_load + yaml.safe_dump(sort_keys=True):
# deployment config                    env:
replicas: 3   # keep this note           - NAME: a
env:                                     - VALUE: b
  - NAME: a                              replicas: 3
  - VALUE: b
SEMANTICALLY EQUAL: True
git diff --numstat:  4  5  cfg.yaml => cfg.roundtrip.yaml
```
Both comments destroyed, key order changed, inline-comment lost — and the merge machinery now sees a **whole-file rewrite** (4 deletions / 5 insertions) for a semantically null change. YAML's anchors/aliases, block-vs-flow style and quoting are further round-trip surfaces. Consequence for the skill: **for YAML, "round-trip" is not a nicety, it is a correctness requirement** — which is exactly the documented reason `ruamel.yaml` exists (yaml.dev/doc/ruamel.yaml; default mode is round-trip `YAML(typ='rt')` and preserves comments; *"If you are using ruamel.yaml in its default (round-trip, YAML(typ='rt')) mode, there is currently no advantage of installing"*; and the `safe` type explicitly loses comments — lyz-code blue-book: *"If invoked with YAML(typ='safe') … the comments of the yaml will be lost"*). Community pain is visible in the wild (homeassistant "HA erasing comments from YAML files is a crime"; strawgate/kb-yaml-to-lens#585 *"Recommendation: Migrate from PyYAML to ruamel.yaml for round-trip YAML editing with comment preservation"*). ruamel was **not installed here**, so this is SOURCED, not reproduced. Mergiraf does handle `*.yaml`/`*.yml` natively (verified in its language list) and merges on the tree, which sidesteps the reflow problem without needing any library.

**CSV/TSV — no identity, so no safe merge exists.** VERIFIED twice:
- 8d: default merge. Both sides changed row `id=2`; conflict emitted **per line**, with no notion of "same logical record": `<<<<<<< HEAD / 2,pear,7 / ======= / 2,pear,99 / 3,kiwi,2 / >>>>>>> feat`. Header and row are the same kind of line to git.
- 8e with `*.csv merge=union`: **`git merge` exit 0, "Merge made by the 'ort' strategy"**, and the file is:
  ```
  id,name,qty
  1,apple,10
  2,pear,7
  2,pear,99
  3,kiwi,2
  ```
  Read back with `csv.DictReader`: `rows: 4`, `ids: Counter({'2': 2, '1': 1, '3': 1})` — the same primary key now resolves to **two records with different quantities**, and nothing failed. This is the cleanest single refutation of `merge=union` for any format with identity semantics, and it is Git's own warning made concrete.
No CSV-semantic merge driver turned up on npm/PyPI under obvious names (§1). Practical stance for the skill: CSV is a **data** file, not a text file — merge it through its loader with an explicit key, or treat it as `merge=binary` and have one side re-produce it.

**Encodings.** gitattributes `working-tree-encoding` (UTF-16 `*.ps1` etc.) carries an explicit warning block: not supported by JGit/libgit2 or older git; *"Reencoding content to non-UTF encodings can cause errors as the conversion might not be UTF-8 round trip safe"*; `core.checkRoundtripEncoding`; *"may slow down certain Git operations"*. Read it as: **an encoding filter is a merge hazard, and `merge.renormalize` only saves you if smudge→clean == clean.**

---

## 8. Reproduction transcripts (the four items the brief demanded)

### R1 — the naive conflict, minified vs pretty + one new key (VERIFIED, `d1.sh`)
Repo `C:\Users\amrmu\AppData\Local\Temp\mergefmt\d1`, `core.autocrlf=false`.
base(main): `{"name":"app","version":"1.0.0","features":{"auth":true,"dark":false}}`
feature: `jq -S --indent 2 '. + {"telemetry":true}'`; main: version→1.0.1.
```
### line-level diff base->feature:
@@ -1 +1,9 @@
-{"name":"app","version":"1.0.0","features":{"auth":true,"dark":false}}
+{
+  "features": { … "telemetry": true, "version": "1.0.0" }
 ### MERGE ATTEMPT:
Auto-merging data.json
CONFLICT (content): Merge conflict in data.json
Automatic merge failed; fix conflicts and then commit the result.
(merge exit 1)
### conflicted working file:
<<<<<<< HEAD
{"name":"app","version":"1.0.1","features":{"auth":true,"dark":false}}
=======
{^M
  "features": {^M
…
>>>>>>> feature
```
**Bonus finding, real and Windows-specific:** `^M` — **`jq` on Windows writes CRLF**. `git cat-file -p feature:data.json | od -c` → `{ \r \n …`. A developer who pretty-prints a JSON config with jq on Windows has now created a *second* divergence (EOL) on top of the first (indent), and it is baked into the blob, not just the worktree. Any "canonicalise then merge" recipe run on Windows must strip/normalise EOL as part of canonicalisation (here: `sed 's/\r$//'`, and `--indent`/`-j` output through a normalising filter).

### R2 — semantic diff proves the only real change is the new key; then the naive fix fails (VERIFIED)
Three stages are directly addressable: `git show :1:data.json` (base), `:2:` (ours), `:3:` (theirs).
```
--- base vs OURS (canonical): -… "version":"1.0.0"}  +… "version":"1.0.1"}
--- base vs THEIRS (canonical): -… "name":"app","version":"1.0.0"}
                                +… "name":"app","telemetry":true,"version":"1.0.0"}
```
i.e. main touched exactly `version`, feature touched exactly `telemetry`; every other line of the "conflict" is formatting.
Then the tempting one-liner:
```
$ jq -s --indent 2 -S '.[0] * .[1]' ours.json theirs.json
{ … "telemetry": true, "version": "1.0.0" }        # <-- main's 1.0.1 GONE
$ jq -e '.version=="1.0.1" and .telemetry==true' resolved.json    # test FAILS, exit 1
```
and the deletion trap:
```
base {"a":1,"b":2,"gone":3}  ours {"a":1,"b":2,"gone":4}  theirs {"a":1,"b":2}
$ jq -s -c '.[0] * .[1]' o.json t.json  ->  {"a":1,"b":2,"gone":4}
```
**Both are silent.** The skill must say: *two-way `*`/`+` is an overlay, and an overlay with no base is not a merge.*

### R3 — custom JSON merge driver, registered in .gitattributes, end-to-end (VERIFIED, `d3.sh` + `json3way.py`)
```
$ printf '*.json merge=json3\n' > .gitattributes
$ git config merge.json3.name  'JSON 3-way semantic merge driver'
$ git config merge.json3.driver "python \"$T/json3way.py\" %O %A %B %P"
$ git check-attr merge -- cfg.json
cfg.json: merge: json3
```
| case | ours | theirs | driver output | exit |
|---|---|---|---|---|
| fmtonly | pretty, no semantic change | minified + `telemetry` | `ours semantically unchanged -> kept theirs` → `{"name":"app","version":"1.0.1","telemetry":true}` | 0, clean |
| orthogonal | `{"a":9,"b":2}` | `{"a":1,"b":8,"c":3}` | `auto-merged` → `{"a":9,"b":8,"c":3}` | 0, clean |
| clash | `{"a":1,"b":"ours"}` | `{"a":2,"b":"theirs"}` | `CONFLICT value at /b` → git leaves the conflict | 1 |
| deletion | `{"a":1,"gone":3,"keep":false}` | `{"a":1,"keep":true}` (deleted `gone`) | `auto-merged` → `{"a":1,"keep":false}` — **honoured the deletion**, kept our other change | 0 |
Note the fmtonly case is the doctrine made executable: **when one side's change is format-only, adopt the *other* side's bytes verbatim**, so nobody's formatting choice gets silently standardised.

### R4 — `-X renormalize`, end-to-end, exact commands (VERIFIED, `d4b.sh`)
```
printf 'line1\r\nline2\r\nline3\r\n' > notes.md      # legacy CRLF blobs
git checkout -qb feature
printf '*.md text\n' > .gitattributes
git add .gitattributes notes.md && git add --renormalize .
git commit -qm "feature: eol=LF renormalization only"
# feature blob: l i n e 1 \n l i n e 2 \n l i n e 3 \n     (base was \r\n)
# git diff --stat main feature:  3 insertions(+), 3 deletions(-)   <- nothing changed
git checkout -q main; printf 'line1\r\nline2 EDITED ON MAIN\r\nline3\r\n' > notes.md; git commit -qam "main: real edit"

A) git merge --no-edit -m x feature
   CONFLICT (content): Merge conflict in notes.md            (exit 1)
B) git merge --no-edit -X renormalize -m x feature
   Auto-merging notes.md
   Merge made by the 'ort' strategy.                          (exit 0)
$ git cat-file -p HEAD:notes.md | od -c
   l i n e 1 \n l i n e 2   E D I T E D   O N   M A I N \n l i n e 3 \n
$ git check-attr -a notes.md -> notes.md: text: set
$ git add --renormalize . && git status --porcelain -> (clean; repo is consistent)
```
So `-X renormalize` is exactly the EOL analogue of "canonicalise first": it does the virtual check-out/check-in on all three stages and merges on the normalised forms. **Permanent fix is the renormalisation commit** (`* text=auto` + `git add --renormalize .`); `-X renormalize` is the rescue for the merges still in flight.

### R5 — Mergiraf on the owner's exact problem (VERIFIED, `d5.sh`) — the headline result
```
A) git merge-file -p --diff3 left.json base.json right.json      -> exit 1, whole-object conflict
   mergiraf merge base.json left.json right.json -o mrg.out      -> exit 0
   INFO Mergiraf: Solved 1 conflict. Review with: mergiraf review base.json_pw6yImM7
   result: { "features":{"auth":true,"dark":false}, "name":"app",
             "telemetry": true, "version": "1.0.1" }
   jq -e '."version"=="1.0.1" and .telemetry==true' -> YES: 1.0.1 + telemetry, no markers

B) git merge-file (base/ours/theirs adding "new" at different positions)
   -> exit 0 with "new" appearing TWICE (grep -c '"new"' -> 2)
   mergiraf merge -> exit 1:
   {
   <<<<<<< l2.json
     "new": "left value",
   ||||||| b2.json
   =======
     "new": "right value",
   >>>>>>> r2.json
     "alpha": "A",
     "beta": "B"
   }
   downstream: jq '.new' -> "right value";  python json.load -> right value   # silent loss

C) real git merge through the registered driver (repo d5/repo):
   git config merge.conflictStyle diff3
   git config merge.mergiraf.driver "\"…/mergiraf\" merge --git %O %A %B -s %S -x %X -y %Y -p %P -l %L"
   .gitattributes:  *.json merge=mergiraf
   $ git merge --no-edit -m "merge feature" feature
   INFO Mergiraf: Solved 1 conflict. Review with: mergiraf review app.json_VBCB71wk
   Auto-merging cfg/app.json
   Merge made by the 'ort' strategy.      (exit 0)
   -> cfg/app.json has both version 1.0.1 and telemetry:true
```

### R6 — npm-merge-driver end-to-end (VERIFIED, `d6.sh`)
```
CONTROL (no driver): CONFLICT (content) inside package-lock.json; python json.load ->
  json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 11 column 1
INSTALL: bun x npm-merge-driver@2.3.6 install
  npm-merge-driver: npm-merge-driver installed to `git config --local` and .git\info\attributes
MERGE:   npm warn exec The following package was not found and will be installed: npm-merge-driver@2.3.6
  npm-merge-driver: merging package-lock.json
  up to date, audited 2 packages in 2s
  found 0 vulnerabilities
  npm-merge-driver: package-lock.json successfully merged.
  Auto-merging package-lock.json / Merge made by the 'ort' strategy.  (exit 0)
RESULT:  lockfileVersion rewritten 1 -> 3, deps = {left-pad} only (the two lockfile-only
         entries were dropped, correctly, because package.json never declared them)
```
Also observed: with the repo's own `core.autocrlf` unset and the global `=true`, git warned `in the working copy of 'package-lock.json', LF will be replaced by CRLF the next time Git touches it` — i.e. the toolchain itself was generating EOL divergence during the reproduction. Note the driver hard-codes **`npx`**.

### R7 — semantic diff suite (VERIFIED, `d7.sh`) — see §6.

### R8 — binary / generated / YAML / CSV (VERIFIED, `d8.sh`) — see §5 and §7.

### R9 — jd as a git diff driver + array-set policy (VERIFIED, `d9.sh`) — see §6.

---

## 9. DOCTRINE — the decision ladder for "formatted vs unformatted content"

The order is the point. Steps 0–2 are *diagnosis* and cost seconds; most bad merges happen because an agent jumped to step 4 with a text tool.

**Step 0 — Classify the file before touching it.** Which is it?
*(i) hand-written structured data* (config JSON/YAML/TOML, i18n catalogues, manifests),
*(ii) derived/generated artifact* (lockfiles, `dist/*.min.js`, generated clients, snapshots),
*(iii) opaque asset* (images, fonts, PDFs, compiled binaries, model weights),
*(iv) record table* (CSV/TSV/SQLite).
Evidence: gitattributes defines a driver per class (`text` / `binary` / custom), and Git describes binary as *"suitable for binary files that do not have a well-defined merge semantics"*; npm and yarn both route their lockfiles out of the text merge entirely (§3.5, §5). **Classification, not cleverness, is what makes most of the remaining steps unnecessary.** If the repo hasn't declared it, this is the moment to add `.gitattributes` — that's a durable fix, not a merge hack.

**Step 1 — Is it a generated artifact?** → **Do not merge it. Take one side of the *source*, then regenerate.** This is the top of the ladder for a reason: it converts an unresolvable text collision into a deterministic build.
Command shape: resolve source-of-truth files (`package.json`, `.proto`, templates, `src/`), `git checkout --theirs <artifact>` or simply delete it, run the build/installer, commit the regenerated output.
Evidence: npm's own "merge driver" re-ran the resolver and rewrote the lockfile format (R6); yarn's maintainer-thread answer is `yarn.lock merge=binary` + re-install; practitioner consensus is not to commit `dist/` at all.
Guard rail: **regeneration is version-sensitive.** Here, npm 11 turned a v1 lockfile into v3 — the merge result silently depended on the tool on PATH. Pin the generator, or don't pretend the artifact is reproducible.

**Step 2 — Is it an opaque asset?** → **Declare a side, never line-merge.** `merge=binary` (or leaving `merge` unset) makes git keep ours verbatim, mark the path conflicted, and preserve all three stages for inspection: `git ls-files -u`. Resolution is a *decision* (`--ours` / `--theirs` / re-export from the design source), possibly plus Git LFS for size. Never splice; never "take both".
Evidence: R8b's exact transcript; gitattributes' own wording. For review-without-merge, `textconv` + `[diff …] binary = true`.

**Step 3 — Canonicalise before you decide anything about a structured-text conflict.** Compare semantics, not bytes:
```
jq -S -c . FILE            # sorted keys, one line — VERIFIED reorder-invisible
python -c "import json;print(json.dumps(json.load(open(F)),sort_keys=True,separators=(',',':')))"   # zero-dependency
jd A B                     # VERIFIED: no output == no semantic change; exit 1 == real change
jd -set / -mset -setkeys '[…]'   # when order is semantically meaningless
```
…and normalise EOL as part of canonicalisation on Windows (jq emits CRLF — R1).
Then read the actual conflict stages instead of the marked-up worktree:
`git show :1:FILE` (base), `git show :2:FILE` (ours), `git show :3:FILE` (theirs) — the base is what turns "both sides rewrote this file" into "main changed `version`, feature added `telemetry`" (R2).

**Step 4 — If the semantic diff is empty on one side ⇒ PURE-FORMAT conflict.** Adopt the *other* side's bytes and port nothing. `merge=ours`-style "take theirs", or a driver that short-circuits on `canon(x)==canon(base)` (R3 fmtonly case, R4 `-X renormalize`).
Do **not** reflow the file into your own preferred formatting as the "resolution" — that's how the next merge breaks the same way. Fix the root cause instead: normalise at commit (`prettier` + `lint-staged` / `pretty-quick` / **`git-format-staged`**, which formats objects in git's database without touching unstaged work), plus `* text=auto` + `git add --renormalize .` for EOL.
Cheap first try, before any of that: `git merge -X ignore-all-space` (or `ignore-space-change`, `ignore-cr-at-eol`) — 1/8 of all conflicts are whitespace-only and `ort-ignorespace` measurably beats default `ort` (48% vs 46% correct). Limitation: *"Whitespace changes mixed with other changes to a line are not ignored."*

**Step 5 — If both sides changed real data ⇒ merge leaf-wise against the base, never two-way.**
```
leaf: ours==base -> theirs | theirs==base -> ours | ours==theirs -> ours | else CONFLICT(path)
dict: union of keys, each recursed; add/delete handled per key with base consulted
array: POLICY MUST BE EXPLICIT — replace | append | set | identity-keyed merge
```
Use a real tool for this rather than hand-editing markers: **`jd`** to see the change set, **`jsonmerge`** (schema-declared per-key strategies, incl. `append`) or a **`*.json merge=<driver>`** for automation, **`mergiraf`** (JSON/YAML/TOML/XML + commutative-parents/signatures) where you want syntactic merging across a polyglot tree.
Hard prohibitions, all reproduced: **never `jq -s '.[0] * .[1]'` as a merge** (R2: silently reverted ours and resurrected a deletion); **never `merge=union` on structured text** (R3/R8e: produced two concatenated JSON objects that `jq` happily read as a *stream* while strict parsers failed, and a CSV with duplicate primary keys accepted with exit 0); **never hand-splice a lockfile**.
Prefer **registering the driver** over ad-hoc resolution: it fixes rebase, cherry-pick and revert too, and it fails loudly. Set `merge.conflictStyle=diff3` (or `zdiff3`) so the base is visible for the residual conflicts — and note Mergiraf's warning that `zdiff3` can break a driver's tree reconstruction.

**Step 6 — If the format has identity that lines can't express (CSV/TSV, tables, calendars, multi-line records in minified code) ⇒ stop.** Line-based merge gives you a per-line conflict with no record semantics (R8d), and union gives you duplicate records accepted silently (R8e). Merge through the loader with an explicit key, or declare `merge=binary` and let one side re-produce the table. If the file is minified code, the atom is the whole file (R8a): regenerate from source.

**Step 7 — Verify like the merge was a release, because it is.**
```
jq -e . FILE                                  # parses at all?  (exit 0 is not enough — see below)
jq 'keys' / jq -s 'length'                    # duplicate keys? multiple top-level docs?
python -c "import json,csv; …"                # a STRICT parser, not a lenient stream reader
jd base.json merged.json                      # what changed vs base — should equal ours+theirs minus none
git diff --no-index ours.json merged.json     # nothing accidentally reverted
git diff --no-index theirs.json merged.json
```
The `jq`-accepts-union-garbage result is the cautionary tale of this whole wave: **`jq` exit 0 does not mean "valid single JSON document"**, because jq parses a *stream* of JSON values. Verification must use a strict parser (`python json.load`) or check top-level document count. Also verify the build/regeneration actually ran for step-1 files, and that a lockfile's format version did not move under you.

**Step 8 — Encode the decision so this conflict never recurs.** `.gitattributes` is the persistent form of the doctrine: `<pattern> merge=<driver>` for structured data, `merge=binary` for artifacts and assets, `* text=auto` for EOL, `diff=jd` for reviewable JSON. Use `.gitattributes` when the policy is the team's, `$GIT_DIR/info/attributes` when it's only yours (highest precedence, untracked), `core.attributesFile` for per-user global. Mergiraf can generate its own list (`mergiraf languages --gitattributes`).

**The meta-rule, from the ASE 2024 measurement:** `IncorrectCost ≫ UnhandledCost ≫ CorrectCost ≈ 0`. **A loud conflict is cheap; a quiet wrong merge is the most expensive outcome available.** Every rule above — no union, no two-way overlay, no silent lockfile splice, refuse-order on decorators, declare-a-side on assets — is a refusal to trade a visible conflict for an invisible error. And: *simple, format-specific rules beat general clever algorithms* — the paper's trivial Imports-augmentation outperformed the AST merge tools, and the same asymmetry showed up here when `jq -s '*'` lost to a 60-line three-way driver.

---

## 10. Blocked / could-not-verify (reported, not papered over)

| Item | Status |
|---|---|
| `jsonmerge3` on PyPI | **Does not exist** (JSON API 404, `/simple/` 404). Real adjacent package: `merge3` (Breezy, line-based). |
| **pixieMerge** | **No such repository** (GitHub search `total_count: 0`). Research lineage real (SETTA 2022 *Mastery*, JSS 2023) but not an obtainable tool. |
| **CalMerge (Calit2 semantic merge)** | **Not confirmed.** All 24 GitHub hits are calendar-ICS mergers. Sweep list: GitHub repo search, general web search (engine error once, retried), arxiv/ASE-related-work references. |
| `weave` locally | Not run: Homebrew/cargo only; needs two Rust binaries (`weave` + `weave-driver`) on PATH. Sources & docs verified, behaviour NOT reproduced. |
| `git-hires-merge` locally | `pip install git-hires-merge` fails — **not on PyPI**; must install from the git repo. Not attempted (build/clone out of scope). |
| `dq` (massoverlaod) | GitHub `releases/latest` → no tag, no artifact. No install-free path. |
| `Spork`, `IntelliMerge` | Java/academic builds; not installed. Claims taken from the ASE 2024 paper. |
| `ruamel.yaml` | Not installed here; YAML round-trip claims are SOURCED (docs + issue reports), only the *destructive* PyYAML side is reproduced. |
| `json-merge-patch`, `deepmerge`, `jsondiff`, `json-diff`, `deep-diff`, `jiq`, `git-json-merge` | Existence + version + dates verified via registry APIs; **behaviour not exercised.** |
| SemanticMerge / git-unity current installability | Historical sources only (2014-era). UNVERIFIED. |
| Mergiraf on Windows *as a git driver* | **Reproduced and working** — but only because the driver string was quoted with backslashes around the binary path; the docs' bare `mergiraf merge --git …` form assumes a global `merge.mergiraf.driver` on PATH. |

---

## 11. Sources

Primary / official
- Git — gitattributes(5) https://git-scm.com/docs/gitattributes (text/eol/`-X renormalize` note, `merge` attribute, built-in `text`/`binary`/`union` drivers, custom driver `%O %A %B %L %P` + exit-code contract, external diff 7-parameter convention + `trustExitCode`, `working-tree-encoding`, "Marking files as binary")
- Git — git-merge(1) https://git-scm.com/docs/git-merge (`ort` options `ours`/`theirs`/`ignore-*space*`/`renormalize`, conflict presentation `diff3`/`zdiff3`, `git show :1:/2:/3:`)
- Mergiraf https://mergiraf.org/ · /installation.html · /usage.html · /conflicts.html · repo https://codeberg.org/mergiraf/mergiraf (releases API: v0.20.0 2026-09-26)
- jq https://github.com/jqlang/jq/releases (jq-1.8.2) · https://jqlang.org/
- jd https://github.com/josephburnett/jd · https://jd-tool.io/ (v2.5.0, 2026-02-23)
- Difftastic https://github.com/wilfred/difftastic/releases (0.72.0, 2026-10-29)
- Prettier — Pre-commit Hook https://prettier.io/docs/precommit (lint-staged, pretty-quick, Husky.Net, **git-format-staged**, Lefthook, shell hook, `git update-index -g`)
- npm-merge-driver https://www.npmjs.com/package/npm-merge-driver · https://github.com/npm/npm-merge-driver (README quoted in §3.5)
- jsonmerge https://pypi.org/project/jsonmerge/ (1.9.2, 2023-07-19) · merge3 https://pypi.org/project/merge3/ (1.0.0, 2026-10-25, https://github.com/breezy-team/merge3) · deepmerge https://pypi.org/project/deepmerge/ · json-merge-patch https://pypi.org/project/json-merge-patch/ (RFC 7396) · jsondiff https://pypi.org/project/jsondiff/
- ruamel.yaml https://yaml.dev/doc/ruamel.yaml/ · https://lyz-code.github.io/blue-book/coding/python/ruamel_yaml/
- weave https://github.com/Ataraxy-Labs/weave (v0.7.1 2026-11-02; push 2026-11-14) · benchmarks https://ataraxy-labs.github.io/weave/benchmarks.html
- git-hires-merge https://github.com/paulaltin/git-hires-merge · Spork https://github.com/ASSERT-KTH/spork · plume-lib/merging https://github.com/plume-lib/merging

Research
- **B. Schesch, R. Featherman, K. J. Yang, B. R. Roberts, M. D. Ernst, "Evaluation of Version Control Merge Tools", ASE 2024** — https://arxiv.org/abs/2410.09934 , HTML https://arxiv.org/html/2410.09934v1 , DOI 10.1145/3691620.3695075 , PDF https://homes.cs.washington.edu/~mernst/pubs/merge-evaluation-ase2024.pdf (whitespace = 1/8 of conflicts; 46/51/3% vs 48/49/3%; tool roster; cost model; Imports-beats-Spork)
- F. Zhu et al., "Mastery: Shifted-Code-Aware Structured Merging", SETTA 2022 — https://feihe.github.io/materials/setta22a.pdf , slides https://namasikanam.github.io/papers/setta2022-slides.pdf
- F. Zhu et al., "On the methodology of three-way structured merge…", JSS 2023 — https://www.sciencedirect.com/science/article/abs/pii/S138376212300190X
- "Detecting Semantic Conflicts with Unit Tests" (SAM) — https://spgroup.github.io/papers/sam-semantic-merge-tool.html
- Structured Merge org — https://github.com/structuredmerge

Practitioner / community
- Git's Magic Files (merge drivers, `binary`, `merge=ours`) — https://nesbitt.io/2026-02-05/git-magic-files.html *(URL 404'd on fetch; snippet seen via search — treated as secondary, UNVERIFIED text)*
- Stackoverflow: "Normalize Git Curly Brace Formatting … on merge" https://stackoverflow.com/questions/66711627 · "How do you resolve Git conflicts in yarn.lock" https://stackoverflow.com/questions/42939113
- yarnpkg/yarn#2155 "Deal with lockfile merge conflicts in some way" https://github.com/yarnpkg/yarn/issues/2155
- "Should You Commit the dist/ Folder to Git?" https://www.vibereference.com/devops-and-tools/should-you-commit-dist-folder · r/git "Compiled files and git" https://www.reddit.com/r/git/comments/qsiijt/
- joepkockelkorn.com "Combining gitattributes, EditorConfig and Prettier" https://joepkockelkorn.com/blog/combining-gitattributes-editorconfig-and-prettier · markoskon.com line endings + ESLint https://markoskon.com/line-endings-in-vscode-with-git-and-eslint/
- h4l/jsonmerge (CLI deep-merge) https://github.com/h4l/jsonmerge · DaedTech "Merging Done Right: Semantic Merge" https://daedtech.com/merging-done-right-semantic-merge/ · Endjin SemanticMerge+SmartGit https://endjin.com/blog/using-semanticmerge-to-fix-git-merge-conflicts
- git-format-staged https://github.com/hallettj/git-format-staged · its rationale https://www.olioapps.com/blog/automatic-code-formatting/
- IDE: https://code.visualstudio.com/docs/sourcecontrol/merge-conflicts · https://learn.microsoft.com/en-us/visualstudio/version-control/git-resolve-conflicts
- https://blog.git-init.com/the-magic-of-3-way-merge/ (three-way merge explanation)
