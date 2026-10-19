# Commit Discipline

> One concern: how to write atomic, well-sized, well-messaged commits.  
> Core principles that govern when and why to commit live in the parent SKILL.md.

## Atomic Commits

Each commit does one logical thing.

```
# Good
git log --oneline
a1b2c3d Add task creation endpoint with validation
d4e5f6g Add task creation form component
h7i8j9k Connect form to API and add loading state
m1n2o3p Add task creation tests (unit + integration)

# Bad
x1y2z3a Add task feature, fix sidebar, update deps, refactor utils
```

## Descriptive Messages

Explain the *why*, not just the *what*.

```
# Good
feat: add email validation to registration endpoint

Prevents invalid email formats from reaching the database.
Uses Zod schema validation at the route handler level,
consistent with existing validation patterns in auth.ts.

# Bad
update auth.ts
```

**Format**

```
<type>: <short description>

<optional body explaining why, not what>
```

**Types**

- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code change that neither fixes a bug nor adds a feature
- `test` — Adding or updating tests
- `docs` — Documentation only
- `chore` — Tooling, dependencies, config

## Keep Concerns Separate

Do not combine formatting changes with behavior changes. Do not combine refactors with features. Each type of change should be a separate commit — and ideally a separate PR.

```
# Good
git commit -m "refactor: extract validation logic to shared utility"
git commit -m "feat: add phone number validation to registration"

# Bad
git commit -m "refactor validation and add phone number field"
```

Small cleanups (renaming a variable) may be included in a feature commit at reviewer discretion. A pure refactoring change and a feature change are two different changes — submit them separately.

## Size Your Changes

```
~100 lines  → Easy to review, easy to revert
~300 lines  → Acceptable for a single logical change
~1000 lines → Split into smaller changes
```

Target ~100 lines per commit/PR. Changes over ~1000 lines should be split before submitting.
