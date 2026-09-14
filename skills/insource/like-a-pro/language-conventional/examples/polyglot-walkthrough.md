# Polyglot Walkthrough: Applying language-conventional

This guide shows how an AI agent applies `language-conventional` to different target ecosystems without assuming any single language.

---

## Scenario A: A TypeScript / Node.js Web Application

### 1. Toolchain & Config Check
The agent opens `tsconfig.json` and ensures strict mode is activated:
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### 2. Public API Collection Boundaries
- **Before (Leaking mutable array):**
  ```typescript
  export interface ProjectService {
    getProjects(): Promise<Project[]>;
  }
  ```
- **After (Encapsulated immutable view):**
  ```typescript
  export interface ProjectService {
    getProjects(signal?: AbortSignal): Promise<readonly Project[]>;
  }
  ```

---

## Scenario B: A Go Backend Service

### 1. Toolchain & Linter Check
The agent checks `.golangci.yml` or `go.mod` to ensure static analysis and error checking are active (`errcheck`, `staticcheck`).

### 2. Concurrency & Context Discipline
- **Before (Uncancellable I/O):**
  ```go
  func (r *Repository) FetchProjects() ([]*Project, error)
  ```
- **After (Context-aware and bounded):**
  ```go
  func (r *Repository) FetchProjects(ctx context.Context) ([]Project, error)
  ```

---

## Scenario C: A Python Backend Service

### 1. Toolchain & Tooling Check
The agent checks `pyproject.toml` and mandates:
- Type Checker: `mypy --strict`
- Linter: `ruff check`
- Formatter: `ruff format`
- Docstyle: `pydocstyle` (Google convention)

### 2. Typing Rigor (Lossy vs Branded / Abstract Collections)
- **Before (Lossy & Primitive):**
  ```python
  def get_user_projects(user_id: int) -> list[dict]:
      ...
  ```
- **After (Branded Types & Abstract Collections):**
  ```python
  from collections.abc import Sequence
  from typing import NewType

  UserId = NewType('UserId', int)

  def get_user_projects(user_id: UserId) -> Sequence[ProjectDto]:
      """Fetches user projects without leaking mutable lists.
      
      Args:
          user_id: Strictly validated domain user identifier.
      Returns:
          Immutable sequence of project records.
      """
      ...
  ```

---

## Scenario D: A C# / .NET Application

### 1. Toolchain Check
The agent checks `.csproj` for:
```xml
<Nullable>enable</Nullable>
<TreatWarningsAsErrors>true</TreatWarningsAsErrors>
```

### 2. Public API Collection & Cancellation
- **Before:**
  ```csharp
  public Task<List<Project>> GetProjectsAsync();
  ```
- **After:**
  ```csharp
  public Task<IReadOnlyList<Project>> GetProjectsAsync(CancellationToken ct = default);
  ```
