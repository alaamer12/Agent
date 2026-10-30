# <asset-name>

<!-- Copy this card into bequest/<asset-slug>/README.md and replace every placeholder.
     Keep the eight headings: the validator checks for them. Delete this comment when done. -->

## What it does

<One sentence: the behaviour, not the history. This line becomes the row in bequest/INDEX.md.>

## When to use it

<The situation that should make an agent open this asset. Include the words someone would actually type,
e.g. "flaky tests only under CI load", "migration blocked on a lock".>

## How to use it

```bash
<exact, copy-pasteable command(s) — the same ones a caller runs, not a paraphrase>
```

`--help` prints the same contract. Exit codes: `0` ok, `1` findings, `2` usage error.

## Inputs

| Name | Kind | Required | Default | Notes |
|---|---|---|---|---|
| `--input` | file path | yes | — | <format expected; see Assumptions> |
| `--threshold-ms` | integer | no | `800` | <what changing it means> |

Environment variables: <none / name — why>. Secrets are supplied by the caller, never stored here.

## Outputs

- stdout: <human-readable lines; one per finding, format>
- `--json`: <schema or example>
- files written: <none / path pattern, and whether overwriting is possible>
- side effects: <none by default / requires an explicit flag>

## Dependencies

<Runtime and version (e.g. Python 3.9+, standard library only). External tools (ffmpeg, psql, docker) with the
version you tested. Network/privileges required. Anything missing means the asset cannot run.>

## Assumptions and limitations

- <data shape>, <OS tested>, <scale tested>, <what was deliberately not implemented>
- <known failure mode and what the user sees>

## Verification

**Status:** <verified (automated) | verified (manual) | partially verified | unverified> — <date>

```text
<command>  -> <observed output>
<command>  -> <observed output>
<command with bad input> -> <error message>, exit 2
```

Not tested: <cases, environments, sizes>. <!-- If everything was tested, say "the full case matrix above". -->

## Origin

<Session/incident, date, and — if this asset was inherited and modified — what changed and why.>
