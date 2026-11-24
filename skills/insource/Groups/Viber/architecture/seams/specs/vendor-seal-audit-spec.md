# Vendor-Seal Audit Specification

> Specification for an autonomous agent or developer to author an on-demand audit script (Python or
> Bash) tailored to the local repository, detecting third-party knowledge escaping its seam: vendor
> imports, vendor markup, vendor names in identifiers, vendor types crossing the boundary — and the
> platform-specific instance of the same leak. Pairs with
> [references/the-two-walls.md](../references/the-two-walls.md); the severity split for each code is
> decided by [references/arming-the-gate.md](../references/arming-the-gate.md) §2.

---

## 1. Audit Objective

A fast, deterministic scan over **shared** source directories (`shared/`, `commonMain/`, `core/`,
`features/`, `src/`) proving the seam claim mechanically: the third party's name exists in one place
only, and nothing above the seam resolves it — with or without an import.

The audit reports three outcomes, never two: `0` clean, `1` violations found, `2` the audit could not
run. `2` must fail the gate — a parser crash, a missing binary or an unparsable file is exactly the
case where the rule matters.

---

## 2. Detection Rules & Regex Patterns

Vendor-generic family (arm per [assets/rule-table.md](../assets/rule-table.md)):

| Error Code | Violation Description | Target Regex Patterns | Severity |
| :--- | :--- | :--- | :--- |
| **`VENDOR_IMPORT_OUTSIDE_SEAM`** | Any import of a pinned vendor package outside its seam files | `from ['"](<vendor-pkg>|<vendor-pkg>/.*|@<scope>/<pkg>.*)['"]`, `require\(['"]<vendor>` | **ERROR** |
| **`VENDOR_TAG_IN_MARKUP`** | Vendor tags or utility classes used with no import (auto-import, compiler transform) | `<vendor-[a-z-]+`, `class="[^"]*<vendor-prefix>-` | **ERROR** |
| **`VENDOR_NAME_IN_IDENTIFIER`** | Vendor vocabulary inside authored names, CSS classes, or data attributes | `\b<vendorCamel>\w*`, `\b<vendor-kebab>\b` in identifiers/attributes | **ERROR** |
| **`VENDOR_TYPE_LEAK`** | Generated/vendor types crossing the boundary (contract seam breach) | `import type .*<generated-namespace>\.`, `: <VendorSdk>\.` in exported signatures | **ERROR** |
| **`LAYER_SKIP_TO_VENDOR`** | A consumer reaching past the tier that skins the vendor | same import patterns, scoped to layers above the skin tier | **ERROR** |

Platform instance of the same leak (kept from the cross-platform heritage; exclusions per axis
naming live in `cross-platform/references/06`):

| Error Code | Violation Description | Target Regex Patterns | Severity |
| :--- | :--- | :--- | :--- |
| **`LEAK_PREPROCESSOR`** | Conditional compilation preprocessors inside shared code | `^\s*#(if\|elif\|ifdef\|ifndef)\s+(ANDROID\|IOS\|WINDOWS\|MACCATALYST\|TARGET_OS)` | **ERROR** |
| **`LEAK_OS_INSPECTION`** | Direct runtime OS checks in shared logic or views | `Platform\.OS\s*===`, `Platform\.isAndroid`, `Platform\.isIOS`, `OperatingSystem\.Is(Windows\|Android\|IOS)`, `defaultTargetPlatform\s*==` | **ERROR** |
| **`LEAK_IDIOM_BRANCH`** | Direct hardware idiom checks in shared views | `DeviceInfo\.Idiom\s*==`, `DeviceInfo\.Current\.Idiom`, `DeviceIdiom\.(Desktop\|Phone\|Tablet)` | **ERROR** |
| **`LEAK_NATIVE_IMPORT`** | Importing raw platform hardware or vendor libraries into shared modules | `import.*from\s+['"](react-native-keychain\|expo-camera\|@react-native-community\/netinfo)['"]`, `import\s+android\.hardware\.`, `import\s+UIKit` | **ERROR** |

---

## 3. Exclusion Matrix (Ignored Paths)

The script skips files where naming the third party is legitimate — and each exemption is proven
load-bearing or deleted (arming check 2):

- The seam files themselves, and the skin tiers declared part of the seam in the rule table
  (`seamFiles` entries in the auditor config).
- Build/bootstrap config that registers the vendor: the plugin entry, the auto-import resolver, the
  DI composition root — named rows in the registry, never silent ignores.
- Platform-permitted directories: `platforms/`, `Platforms/`, `androidMain/`, `iosMain/`,
  `desktopMain/`, `windows/`; files following axis conventions `*.android.*`, `*.ios.*`,
  `*.windows.*`, `*.web.*`.
- Test fixture directories: `tests/fixtures/dirty/`.

---

## 4. Agent Script Recipe (Python Template)

The agent synthesizes and runs this against the local repository, substituting the family's real
package names from the seam inventory:

```python
#!/usr/bin/env python3
import os
import re
import sys

PROHIBITED_PATTERNS = [
    # platform instance of the vendor leak (fill real names from the seam inventory)
    ("LEAK_PREPROCESSOR", re.compile(r'^\s*#(if|elif)\s+(ANDROID|IOS|WINDOWS|MACCATALYST)')),
    ("LEAK_OS_INSPECTION", re.compile(r'Platform\.OS\s*===|Platform\.isAndroid|Platform\.isIOS|OperatingSystem\.Is(Windows|Android|IOS)')),
    ("LEAK_IDIOM_BRANCH", re.compile(r'DeviceInfo(\.Current)?\.Idiom\s*==|DeviceIdiom\.(Desktop|Phone|Tablet)')),
    ("LEAK_NATIVE_IMPORT", re.compile(r'import\s+.*from\s+["\'](react-native-keychain|expo-camera)["\']|import\s+android\.hardware\.|import\s+UIKit')),
]

EXCLUDED_DIRS = {"platforms", "androidmain", "iosmain", "desktopmain", "windows", "fixtures", "node_modules", "bin", "obj"}
EXCLUDED_FILE_SUFFIXES = (".android.", ".ios.", ".windows.", ".web.", ".desktop.")

def is_excluded(path):
    parts = path.lower().replace("\\", "/").split("/")
    if any(p in EXCLUDED_DIRS for p in parts):
        return True
    return any(s in os.path.basename(path).lower() for s in EXCLUDED_FILE_SUFFIXES)

def scan(root_dir):
    findings, scanned = [], 0
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            full_path = os.path.join(root, f)
            if is_excluded(full_path):
                continue
            if not f.endswith(('.ts', '.tsx', '.cs', '.kt', '.dart', '.xaml')):
                continue
            try:
                scanned += 1
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    for line_no, line in enumerate(fp, start=1):
                        for code, pattern in PROHIBITED_PATTERNS:
                            if pattern.search(line):
                                findings.append((code, full_path, line_no, line.strip()))
            except OSError as e:
                print(f"[CANNOT-RUN] {full_path}: {e}", file=sys.stderr)
                return None  # unreadable file => outcome 2, never a silent 0
    return (findings, scanned)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    result = scan(target)
    if result is None:
        print("AUDIT COULD NOT RUN", file=sys.stderr)
        sys.exit(2)
    errors, scanned = result
    if scanned == 0:
        print(f"DEAD SCOPE — nothing matched under {target}", file=sys.stderr)
        sys.exit(2)
    if not errors:
        print(f"OK — zero vendor leaks across {scanned} files in {target}")
        sys.exit(0)
    for code, path, line, text in errors:
        print(f"[ERROR] {code} at {path}:{line} -> {text}")
    print(f"\nTotal violations: {len(errors)}")
    sys.exit(1)
```

The recipe adds two guards the inherited platform-only script lacked: `scanned == 0` exits `2`
(a dead scope prints the same green as a clean tree — [examples/case-01-dead-glob.md](../examples/case-01-dead-glob.md)),
and an unreadable file exits `2` rather than being swallowed.
