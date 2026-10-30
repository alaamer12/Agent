# packages — audit toolkit

Scripts, recipes, and templates for both jobs. Language-agnostic recipes
first; the concrete scripts are worked examples from one ecosystem, labelled
with what was actually verified. Tool suggestions are illustrative — verify
current tooling by search before depending on any named project.

---

## The universal scan algorithm (any ecosystem)

Both the native detectors and any hand-rolled script answer the same three
questions per declared dependency:

1. **Extract the declared set** — dependency names from the manifest
   (+ dev/tool scopes separately, since scope moves are a category).
2. **Text-prove references** — search name *and subpaths* across source and
   config files; treat a manifest's own dependency declarations as noise
   (every dep literally "appears" there — only its scripts/tool sections
   count as a reference).
3. **Subtract the untextable** — the implicit kinds that no grep can see
   (entry-point/metadata-discovered plugins, native link stubs, peer deps,
   compiler-consumed type packages) by consulting package *metadata* and
   docs, not code. A zero-reference result is the start of the implicit
   checklist, never the verdict.

Bash/ripgrep form (portable across stacks — swap the file globs and manifest
reader):

```bash
# deps=$(extract names from manifest)  e.g. jq, python -c tomllib, cargo metadata, go list -m all
for d in $deps; do
  rg -q --hidden -g '!lockfile*' -e "\"$d" -e "'$d" -e "$d/" . \
    && echo "REFERENCED  $d" || echo "NO-TEXTREF   $d  <- run implicit checklist"
done
```

Python form (stdlib-only manifest read for a `pyproject`, to show the same
algorithm in a second ecosystem):

```python
import tomllib, pathlib, re

cfg = tomllib.loads(pathlib.Path("pyproject.toml").read_text())
raw = cfg.get("project", {}).get("dependencies", []) or list(
    cfg.get("tool", {}).get("poetry", {}).get("dependencies", {}))
# PEP 508 strings ("requests>=2.31") -> bare names; python itself isn't a dep to audit
declared = [n for n in (re.split(r"[<>=!~\[; ]", str(r))[0] for r in raw)
            if n.lower() != "python"]

files = [p for p in pathlib.Path(".").rglob("*")
         if p.is_file() and p.suffix in {".py", ".toml", ".cfg", ".ini", ".txt"}
         and "lock" not in p.name and p.name != "pyproject.toml"]  # declarations aren't usage

for name in declared:
    pat = re.compile(rf"\b{re.escape(name)}\b")
    hits = [f for f in files if pat.search(f.read_text(encoding="utf-8", errors="ignore"))]
    print(("REFERENCED " if hits else "NO-TEXTREF ") + name + "  <- metadata/entry-point check still required")
```

(The Python form was run against a fixture: specifier parsing (`requests>=2.31`
→ `requests`), the implicit `python` entry excluded, referenced vs
no-textref classified correctly. Its permanent caveat: entry-point plugins
read as unreferenced *forever* no matter the grep — the flagged tail is the
checklist, not noise.)

---

## Worked example: JS-family workspace audit script (verified)

For `package.json` workspaces this script exists and **was run against a
synthetic fixture** covering: explicit import, binary invoked only via a
`package.json` script, config subpath plugin (`'lib/babel-preset'`), and
genuine no-reference deps — each classified correctly. The
package-self-declaration false positive is specifically guarded by the
scripts-only rule. It has *not* been run against a real monorepo; expect to
tune `SKIP_DIRS`/`TEXT_EXT` on first real use. Save as `scratch/audit.js`,
run with `node scratch/audit.js`.

```javascript
import fs from 'fs';
import path from 'path';

// CONFIGURATION
const PACKAGE_PATH = path.resolve('packages/my-package');
const SKIP_DIRS = new Set(['node_modules', 'dist', '.turbo', '.expo', 'build']);
const TEXT_EXT = new Set(['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.json', '.yaml', '.yml', '.md', '.html', '.gradle', '.pbxproj']);

function getAllFiles(dirPath, arrayOfFiles) {
    if (!fs.existsSync(dirPath)) return arrayOfFiles || [];
    const files = fs.readdirSync(dirPath);
    arrayOfFiles = arrayOfFiles || [];

    files.forEach(function(file) {
        const full = path.join(dirPath, file);
        if (fs.statSync(full).isDirectory()) {
            if (!SKIP_DIRS.has(file)) {
                arrayOfFiles = getAllFiles(full, arrayOfFiles);
            }
        } else {
            arrayOfFiles.push(full);
        }
    });

    return arrayOfFiles;
}

function checkUsage(lib, files) {
    const bases = [lib];
    if (lib.startsWith('@types/')) bases.push(lib.slice('@types/'.length)); // @types/x backs explicit import of x
    const names = bases.map(b => b.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));

    for (const file of files) {
        const ext = path.extname(file);
        const isTarget = TEXT_EXT.has(ext) || ext === '' || path.basename(file).startsWith('.');
        if (!isTarget) continue; // text-ish: listed extensions, extensionless configs, dotfiles
        let content;
        try { content = fs.readFileSync(file, 'utf8'); } catch { continue; }
        // The package's own package.json mentions every dep by declaration —
        // only its scripts section counts as an implicit reference there.
        if (file === packageJsonPath) {
            content = JSON.stringify(packageJson.scripts || {});
        }

        for (const n of names) {
            const patterns = [
                new RegExp(`from\\s+['"]${n}(/.*)?['"]`),                    // explicit import
                new RegExp(`require\\(['"]${n}(/.*)?['"]\\)`),               // require
                new RegExp(`import\\s+['"]${n}(/.*)?['"]`),                  // side-effect import
                new RegExp(`['"]${n}(/.*)?['"]`),                             // config plugin lists, scripts, presets (incl. subpaths)
                new RegExp(`\\b${n.split('/').pop()}\\b.*(?:generate|build|run|exec)`), // binary invoked by a script (heuristic)
            ];
            if (patterns.some(re => re.test(content))) {
                return { used: true, where: file };
            }
        }
    }
    return { used: false };
}

const packageJsonPath = path.join(PACKAGE_PATH, 'package.json');
const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
const files = getAllFiles(PACKAGE_PATH);

const report = { deps: {}, devDeps: {}, noReferenceFound: [] };

for (const [field, bucket] of [['dependencies', report.deps], ['devDependencies', report.devDeps]]) {
    for (const dep of Object.keys(packageJson[field] || {})) {
        const r = checkUsage(dep, files);
        bucket[dep] = r.used ? 'referenced' : 'NO-REFERENCE — check implicit kinds before removing';
        if (!r.used) report.noReferenceFound.push({ dep, wasIn: field });
    }
}

console.log(JSON.stringify(report, null, 2));
```

**Reading the output:** `referenced` includes config-file mentions — a Metro
plugin named only in `metro.config.js` is referenced. `NO-REFERENCE` is not a
death sentence: it's the list to run the implicit table against (native
runtime stubs, entry-point-discovered packages, and peer deps can have zero
textual references anywhere and still be load-bearing). Only packages that
survive both checks go in the removal report — and native-stub-class
packages need runtime verification, because their absence compiles fine and
crashes on launch.

---

## Maintained redundancy table (per-repo artifact — example)

The monorepo check from job 1 ("this dep is already provided by the shared
kit") compounds over time: every confirmed kit-redundancy deserves a row so
the next audit starts from verified ground. Example of what that table looks
like in this repo:

| Library | Redundant if… |
|---------|-----------------|
| `react-i18next` | Package uses `@kit/i18n` |
| `expo-haptics` | Package uses `@kit/shared` (check `utils/haptics.ts`) |
| `expo-router` | Package uses `@kit/features-shared` |
| `use-count-up` | Package uses `CountUpNumber` from `@snduk/primitives` |
| `nanoid` | Package can use `crypto.randomUUID()` or shared utils |

Every row still needs the confirmation step (the kit really re-exports it) —
a maintained table is a head start, not a verdict.

---

## Job 2 helpers — checking and reporting versions

Native checkers first (they know the stack; report drift without touching
anything). Per-ecosystem commands are in `ecosystem-playbook.md`; the JS
family, since it's the verified one here:

```powershell
bun update --latest            # bun: resolve latest across the tree (run on a branch!)
npx expo install --check       # Expo: versions the installed SDK expects
npx expo fix                   # Expo: repair config drift
npx npm-check-updates          # npm-family: current vs latest, no writes (-u to write)
npx npm-check-updates --target minor   # bounded: no majors
pnpm outdated                  # pnpm
```

Registry-direct when no tool covers the package — the query *is* the search
(one call each; equivalents exist per ecosystem in the playbook):

```powershell
npm view <pkg> version         # latest on npm
npm view <pkg> versions --json | tail   # full history when you need a specific one
pip index versions <pkg>       # PyPI
cargo search <pkg>             # crates.io
go list -m <module>@latest     # Go module proxy
```

With context7 installed, query it per package instead — version-matched docs
arrive with the number, which is what the major-version breaking-change check
needs. For that check: `<pkg> <oldMajor> to <newMajor> migration guide /
breaking changes` (context7, then the project's own CHANGELOG/releases — the
maintainers' migration doc beats any summary).

### Before/after report template

```markdown
## Dependency update report — <project/subtree> (<date>)
Ecosystem: <detected stack> · Method: <native updater | context7 | registry queries>

| Package | Current | Latest | Bump | Breaking in *this* project? | Source |
|---------|---------|--------|------|------------------------------|--------|
| zod | 3.24.1 | 4.1.12 | **major** | checked: yes — `.strict()` removed, 6 call sites in `packages/features/*` | changelog link |
| expo | 52.0.47 | 54.0.9 | **major** | SDK 54 ⇒ RN 0.81, react-native-reanimated ≥ 3.17 | migration guide |
| lodash-es | 4.17.20 | 4.17.21 | patch | no | registry |

**Proposed now (safe):** all patch/minor rows.
**Needs your call:** majors with breaking changes found (zod, expo);
"unknown breakage" rows (none).
Verify after apply: lock sync → static gate → build → tests → runtime smoke.
```

Rows from a different ecosystem look identical (the column set is the
contract); fill "Breaking in *this* project?" from the actual migration
guide checked against *this* codebase's usage — "it's a major" is not a
finding, "major X removes API Y which we call at these 6 places" is.
