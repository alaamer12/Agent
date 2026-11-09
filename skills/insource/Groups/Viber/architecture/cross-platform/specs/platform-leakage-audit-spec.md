# Platform Leakage Audit Specification

> Specification for an autonomous agent or developer to author an on-demand audit script (e.g. Python or Bash) tailored to the local repository, identifying platform leakage, preprocessors, and idiom branching in shared code.

---

## 1. Audit Objective

The purpose of the generated script is to perform a fast, deterministic scan across shared source directories (`shared/`, `commonMain/`, `core/`, `features/`) to detect prohibited platform contamination.

---

## 2. Detection Rules & Regex Patterns

| Error Code | Violation Description | Target Regex Patterns | Severity |
| :--- | :--- | :--- | :--- |
| **`LEAK_PREPROCESSOR`** | Conditional compilation preprocessors inside shared code | `^\s*#(if|elif|ifdef|ifndef)\s+(ANDROID\|IOS\|WINDOWS\|MACCATALYST\|TARGET_OS)` | **ERROR** |
| **`LEAK_OS_INSPECTION`** | Direct runtime OS checks in shared logic or views | `Platform\.OS\s*===`, `Platform\.isAndroid`, `Platform\.isIOS`, `OperatingSystem\.Is(Windows\|Android\|IOS)`, `defaultTargetPlatform\s*==` | **ERROR** |
| **`LEAK_IDIOM_BRANCH`** | Direct hardware idiom checks in shared views | `DeviceInfo\.Idiom\s*==`, `DeviceInfo\.Current\.Idiom`, `DeviceIdiom\.(Desktop\|Phone\|Tablet)` | **ERROR** |
| **`LEAK_NATIVE_IMPORT`** | Importing raw platform hardware or vendor libraries into shared modules | `import.*from\s+['"](react-native-keychain\|expo-camera|@react-native-community\/netinfo)['"]`, `import\s+android\.hardware\.`, `import\s+UIKit` | **ERROR** |

---

## 3. Exclusion Matrix (Ignored Paths)

The script must explicitly skip files where platform code is legitimately permitted:
- Directories named: `platforms/`, `Platforms/`, `androidMain/`, `iosMain/`, `desktopMain/`, `windows/`.
- Files following platform extension conventions: `*.android.*`, `*.ios.*`, `*.windows.*`, `*.web.*`.
- Test fixture directories: `tests/fixtures/dirty/`.

---

## 4. Agent Script Recipe (Python Template)

When asked to audit a project, the agent can synthesize and execute this lightweight Python script:

```python
#!/usr/bin/env python3
import os
import re
import sys

PROHIBITED_PATTERNS = [
    ("LEAK_PREPROCESSOR", re.compile(r'^\s*#(if|elif)\s+(ANDROID|IOS|WINDOWS|MACCATALYST)')),
    ("LEAK_OS_INSPECTION", re.compile(r'Platform\.OS\s*===|Platform\.isAndroid|Platform\.isIOS|OperatingSystem\.Is(Windows|Android|IOS)')),
    ("LEAK_IDIOM_BRANCH", re.compile(r'DeviceInfo(\.Current)?\.Idiom\s*==|DeviceIdiom\.(Desktop|Phone|Tablet)')),
    ("LEAK_NATIVE_IMPORT", re.compile(r'import\s+.*from\s+["\'](react-native-keychain|expo-camera)["\']|import\s+android\.hardware\.|import\s+UIKit'))
]

EXCLUDED_DIRS = {"platforms", "androidmain", "iosmain", "desktopmain", "windows", "fixtures", "node_modules", "bin", "obj"}
EXCLUDED_FILE_SUFFIXES = (".android.", ".ios.", ".windows.", ".web.", ".desktop.")

def is_excluded(path):
    parts = path.lower().replace("\\", "/").split("/")
    if any(p in EXCLUDED_DIRS for p in parts):
        return True
    return any(s in os.path.basename(path).lower() for s in EXCLUDED_FILE_SUFFIXES)

def scan(root_dir):
    findings = []
    for root, dirs, files in os.walk(root_dir):
        for f in files:
            full_path = os.path.join(root, f)
            if is_excluded(full_path):
                continue
            if not f.endswith(('.ts', '.tsx', '.cs', '.kt', '.dart', '.xaml')):
                continue
            try:
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    for line_no, line in enumerate(fp, start=1):
                        for code, pattern in PROHIBITED_PATTERNS:
                            if pattern.search(line):
                                findings.append((code, full_path, line_no, line.strip()))
            except Exception as e:
                pass
    return findings

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    errors = scan(target)
    if not errors:
        print(f"OK — Zero platform leakages found in {target}")
        sys.exit(0)
    for code, path, line, text in errors:
        print(f"[ERROR] {code} at {path}:{line} -> {text}")
    print(f"\nTotal violations: {len(errors)}")
    sys.exit(1)
```
