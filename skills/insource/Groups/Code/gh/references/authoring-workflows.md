# Authoring workflow files — surviving both parsers

A `.github/workflows/*.yml` is parsed twice: first as **YAML**, then the
`${{ }}` values are parsed by the **Actions expression grammar**. A file
can pass the first and die at the second, and GitHub reports it as a
run with **zero jobs**: *"This run likely failed because of a workflow
file issue"*. `yaml.safe_load`, yamllint, and a careful human read all
miss the classic case below — only actionlint catches it before push.

## The #1 trap: space-then-`#` inside an unquoted expression

In YAML, space + `#` starts a comment. An unquoted scalar containing an
expression with `#` (issue numbers! `#{0}` formatting!) is silently
truncated — and the truncated `${{` never closes:

```yaml
# BAD — value ends at " #"; Actions sees an unterminated expression
run-name: ${{ format('Evaluate PR #{0}', inputs.pr_number) }}

# GOOD — double quotes keep everything inside the scalar
run-name: "${{ format('Evaluate PR #{0}', inputs.pr_number) }}"
```

`yaml.safe_load` accepts the BAD form (it just sees a short string).
actionlint reports it as
`got unexpected EOF while lexing end of string literal, expecting '''`.

## When a scalar must be quoted

| Value contains | Why it breaks | Fix |
|---|---|---|
| space then `#` | comment truncation (above) | double-quote the whole value |
| `:` then space | parsed as nested mapping key | quote |
| leading `* & ! ? \| > @ \`` | anchor/tag/block syntax | quote |
| `true/false/yes/no/on/off` or numbers that must stay strings | YAML type coercion | quote |
| expression with inner single quotes | outer single quotes would collide | use double quotes outside (and vice-versa) |

Rule of thumb: **any `name`, `run-name`, `if`, `env`, `with` value that
embeds `${{ }}` and holds `#`, `: `, or a leading special character gets
wrapped in double quotes.** Do not escape the braces — quoting the
scalar is enough; escaping `${{` breaks the expression. The structural
`on:` key itself stays unquoted (Actions expects it; some generic YAML
parsers read it as boolean `true`, which is a parser artifact, not a
workflow bug).

## Expressions in short

- `${{ }}` is allowed in values (`name`, `if`, `with`, `env`, `run`,
  `uses`) — never in keys.
- Contexts that matter: `github` (event metadata), `inputs` (dispatch /
  reusable), `matrix`, `needs.<job>.outputs`, `steps.<id>.outputs`,
  `secrets`, `vars`, `env`. Availability differs by position — if a
  context is empty somewhere, that is the documented boundary, not a
  bug to work around twice.
- Inside `run:`, `${{ }}` is template-substituted **before the shell
  sees it**; prefer referring to context values via the environment
  (`${GITHUB_REF}`) or an `env:` mapping — same conclusion as
  `logic-in-scripts.md`'s injection rule.

## Skeleton worth starting from

```yaml
name: ci
on:
  pull_request:
    paths-ignore: ["docs/**"]          # granular triggers: don't run what can't fail
permissions:
  contents: read                       # baseline; grant more per job — see hardening.md
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true             # PR branches: newer push supersedes
jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@<full-sha> # vN.N.N
      - run: bash scripts/ci/test.sh     # behavior lives in the file — law 1
```

Structure rules while filling it in: one job per phase (build/test/lint/
deploy); pass data with `needs:` + `outputs:` and artifacts, not by
re-running work; `matrix` with `fail-fast: false` when you want every
combination reported; every job gets `timeout-minutes`; steps that need
repo files must come **after** `actions/checkout`; on Windows runners set
the shell explicitly (`shell: pwsh` / `bash`) — defaults differ.

## Validate before committing — actionlint

actionlint understands the Actions schema **and** the expression grammar;
it is the only pre-push proof. Pinned download (verify checksum; adapt
the asset name per platform — `windows_amd64.zip` + `Expand-Archive` on
PowerShell, `darwin_amd64.tar.gz` on macOS):

```bash
ACTIONLINT_VERSION=<current release>   # pin the version and its sha256 you verified today
curl -fsSLo actionlint.tar.gz \
  "https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz"
echo "${ACTIONLINT_SHA256}  actionlint.tar.gz" | sha256sum -c -
tar -xzf actionlint.tar.gz actionlint
./actionlint -shellcheck= -pyflakes= .github/workflows/*.yml   # workflow/expression errors only
```

Exit 0 = structurally valid. Enable shellcheck/pyflakes later once
pre-existing noise is dealt with — they lint the *contents* of `run:`
blocks, which law 1 keeps short anyway.

If the project gates workflow edits with a CI check for this, use that
gate too — but run actionlint locally first; the gate is the proof, not
the experiment. Final proof beyond actionlint is the run starting jobs at
all: "it parses" is never evidence enough.
