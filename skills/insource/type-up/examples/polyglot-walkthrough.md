# type-up — Polyglot Walkthroughs

## Example 1: Configuration Shape

### Before (lossy primitives)

**TypeScript**
```ts
interface Config {
  checksDir?: string;
  gitignore?: string | null;
  steps?: { id: string; concurrency?: number }[];
}
```

**Python**
```python
from typing import TypedDict, NotRequired

class Config(TypedDict):
    checksDir: NotRequired[str]
    gitignore: NotRequired[str | None]
    steps: NotRequired[list[dict]]
```

**Go**
```go
type Config struct {
    ChecksDir *string `json:"checksDir,omitempty"`
    Gitignore *string `json:"gitignore,omitempty"`
    Steps     []Step  `json:"steps,omitempty"`
}
type Step struct {
    ID          string `json:"id"`
    Concurrency *int   `json:"concurrency,omitempty"`
}
```

### After (semantic + layered)

**TypeScript**
```ts
/** Non-empty file-system path. */
type PathLike = string;
/** Optional ignore-file path. */
type GitignorePath = PathLike | null;
/** Domain check identifier: check_<snake_case> */
type CheckId = `check_${string}`;
/** Integer ≥ 1 */
type PositiveInt = number;
type ScanMode = "full" | "changed" | "staged";

interface StepConfig {
  id: CheckId;
  concurrency?: PositiveInt;
  gitignore?: GitignorePath;
}

/**
 * Loaded from chekr.config.js (or equivalent) at project root.
 * @example
 * ```js
 * /** @type {import('pkg').Config} */
 * export default { checksDir: "./checks", scanMode: "changed" };
 * ```
 */
interface Config {
  checksDir?: PathLike;
  gitignore?: GitignorePath;
  scanMode?: ScanMode;
  steps?: StepConfig[];
}
```

**Python**
```python
from typing import NewType, TypedDict, NotRequired, Literal

PathLike = NewType("PathLike", str)
GitignorePath = PathLike | None
CheckId = NewType("CheckId", str)          # validated as check_<snake_case>
PositiveInt = NewType("PositiveInt", int)  # ≥ 1
ScanMode = Literal["full", "changed", "staged"]

class StepConfig(TypedDict):
    id: CheckId
    concurrency: NotRequired[PositiveInt]
    gitignore: NotRequired[GitignorePath]

class Config(TypedDict):
    checksDir: NotRequired[PathLike]
    gitignore: NotRequired[GitignorePath]
    scanMode: NotRequired[ScanMode]
    steps: NotRequired[list[StepConfig]]
```

**Go**
```go
// PathLike is a non-empty file-system path.
type PathLike string

// CheckId is a domain identifier matching check_<snake_case>.
type CheckId string

// PositiveInt is an integer ≥ 1.
type PositiveInt int

type ScanMode string
const (
    ScanFull    ScanMode = "full"
    ScanChanged ScanMode = "changed"
    ScanStaged  ScanMode = "staged"
)

type StepConfig struct {
    ID          CheckId     `json:"id"`
    Concurrency PositiveInt `json:"concurrency,omitempty"`
    Gitignore   *PathLike   `json:"gitignore,omitempty"`
}

// Config is the user-facing configuration shape.
type Config struct {
    ChecksDir *PathLike    `json:"checksDir,omitempty"`
    Gitignore *PathLike    `json:"gitignore,omitempty"`
    ScanMode  *ScanMode    `json:"scanMode,omitempty"`
    Steps     []StepConfig `json:"steps,omitempty"`
}
```

**Rust (newtype style)**
```rust
/// Non-empty file-system path.
pub struct PathLike(String);

/// Domain check identifier: check_<snake_case>
pub struct CheckId(String);

/// Integer ≥ 1
pub struct PositiveInt(u32);

#[derive(Debug, Clone, Copy)]
pub enum ScanMode {
    Full,
    Changed,
    Staged,
}

pub struct StepConfig {
    pub id: CheckId,
    pub concurrency: Option<PositiveInt>,
    pub gitignore: Option<PathLike>,
}

/// User-facing configuration.
pub struct Config {
    pub checks_dir: Option<PathLike>,
    pub gitignore: Option<PathLike>,
    pub scan_mode: Option<ScanMode>,
    pub steps: Option<Vec<StepConfig>>,
}
```

---

## Example 2: Runtime Validation (lightweight, production-safe)

Keep validators free of heavy schema libraries in the core package.

**TypeScript / JavaScript**
```js
const CHECK_ID_RE = /^check_[a-z][a-z0-9_]*$/;

function assertCheckId(value, path) {
  if (typeof value !== "string" || !CHECK_ID_RE.test(value)) {
    throw new ConfigError(`${path} must match check_<snake_case>`, path);
  }
}

function assertPositiveInt(value, path) {
  if (typeof value !== "number" || !Number.isInteger(value) || value < 1) {
    throw new ConfigError(`${path} must be an integer ≥ 1`, path);
  }
}
```

**Python**
```python
import re

CHECK_ID_RE = re.compile(r"^check_[a-z][a-z0-9_]*$")

def assert_check_id(value: object, path: str) -> str:
    if not isinstance(value, str) or not CHECK_ID_RE.match(value):
        raise ConfigError(f"{path} must match check_<snake_case>")
    return value

def assert_positive_int(value: object, path: str) -> int:
    if not isinstance(value, int) or value < 1:
        raise ConfigError(f"{path} must be an integer ≥ 1")
    return value
```

**Go**
```go
var checkIDRe = regexp.MustCompile(`^check_[a-z][a-z0-9_]*$`)

func assertCheckID(v string, path string) error {
    if !checkIDRe.MatchString(v) {
        return fmt.Errorf("%s must match check_<snake_case>", path)
    }
    return nil
}

func assertPositiveInt(v int, path string) error {
    if v < 1 {
        return fmt.Errorf("%s must be an integer ≥ 1", path)
    }
    return nil
}
```

---

## Example 3: Schema Layer (dev / CI)

Use the ecosystem’s preferred schema library only in the types/contracts package or test suite.

- TypeScript: Zod, Valibot, ArkType
- Python: Pydantic, msgspec
- Go: go-playground/validator, or custom + property tests
- Rust: serde + custom validation or validator crate

The schema should mirror the same constraints enforced by the lightweight runtime validator.

---

## Example 4: Adding a New Field (process)

1. Add the semantic type (or reuse an existing one).
2. Add the field to the public config / API shape with documentation.
3. Extend the lightweight runtime validator.
4. Extend the schema / property tests.
5. Update the sync table and any user-facing docs.
6. Prefer a single PR/commit that keeps all layers consistent.
