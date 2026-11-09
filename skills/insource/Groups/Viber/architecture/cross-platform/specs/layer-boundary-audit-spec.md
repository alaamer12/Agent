# Layer Boundary & Multi-Axis Audit Specification

> Specification for authoring an audit script to verify compliance with the Single-Axis Filename Law, directory overlay structures, and downward dependency rules across layers.

---

## 1. Audit Objective

The purpose of the generated script is to validate structural file organization in multi-axis projects:
1. Guarantee that no file compounds multiple axes into its name.
2. Ensure that policy layers do not leak into capability layers.
3. Validate that upward dependency reaches are flagged as structural violations.

---

## 2. Detection Rules & Checks

### 1. The Single-Axis Filename Rule
Scan filenames against known orthogonal axis lists:
- **Platform Axis:** `android`, `ios`, `windows`, `macos`, `web`, `linux`, `desktop`, `mobile`
- **Channel Axis:** `playstore`, `fdroid`, `appstore`, `sideload`, `enterprise`
- **Region Axis:** `eu`, `us`, `ksa`, `china`, `global`

```python
# Rule violation condition:
# If a filename contains more than one token from two different axes before its extension:
# e.g., "auth.android.playstore.ts" -> Violation: MULTI_AXIS_COMPOUND_FILENAME
```

### 2. Downward Dependency Direction Rule
Inspect module import statements:
```
Tier 3 (Domain Specialization)
   ↓ imports
Tier 2 (Base Unit / Contract)
   ↓ imports
Tier 1 (Core Primitive)
```
- If a file in `shared/ui/primitives` (Tier 1) imports from `features/` (Tier 3) -> Violation: `REVERSED_PRIMITIVE_DEPENDENCY`.
- If a file in `capabilities/` imports from `policies/` -> Violation: `CAPABILITY_DEPENDS_ON_POLICY`.

---

## 3. Agent Script Recipe (Python Template)

```python
#!/usr/bin/env python3
import os
import re
import sys

AXES = {
    "platform": {"android", "ios", "windows", "macos", "web", "linux", "desktop", "mobile"},
    "channel": {"playstore", "fdroid", "appstore", "sideload", "enterprise"},
    "region": {"eu", "us", "ksa", "china", "global"}
}

def check_filename_axes(filename):
    # Strip extension
    base = os.path.splitext(filename)[0]
    tokens = set(re.split(r'[._-]', base.lower()))
    
    matched_axes = []
    for axis_name, axis_values in AXES.items():
        if tokens.intersection(axis_values):
            matched_axes.append(axis_name)
            
    if len(matched_axes) > 1:
        return f"File compounds multiple axes: {', '.join(matched_axes)}"
    return None

def scan_boundaries(root_dir):
    violations = []
    for root, _, files in os.walk(root_dir):
        for f in files:
            compound_err = check_filename_axes(f)
            if compound_err:
                violations.append((f, os.path.join(root, f), compound_err))
    return violations

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    issues = scan_boundaries(target)
    if not issues:
        print("OK — All files comply with Single-Axis laws and layer boundaries.")
        sys.exit(0)
    for f, path, msg in issues:
        print(f"[VIOLATION] {f} at {path}: {msg}")
    sys.exit(1)
```
