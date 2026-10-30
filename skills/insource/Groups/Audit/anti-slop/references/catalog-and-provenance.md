# Catalog, research, and evidence provenance

## Canonical catalog

`registry/registry.json` is the compact 67-entry routing index. Each pattern has a stable ID, official catalog section/modality, scope and detector disposition, source provenance, linked knowledge/detection files, and test disposition. Load detailed records only after selecting IDs.

The catalog was reconciled against the supplied 60-record `antipatterns.json` and `registry.rs` and the captured official Impeccable Slop page. The net additions are six design-review entries and the 61st detector (`images-move-on-hover`); preserve existing local IDs and distinguish the six design-review patterns from detector rules.

## Evidence locations

- `source-map.md` maps all 67 catalog entries and 11 demo pages to text captures and screenshots.
- `assets/source/slop.html` and `assets/source/slop.txt` preserve the catalog capture.
- `assets/source/examples/` preserves example-page text/DOM captures.
- `assets/screenshots/slop/` and `assets/screenshots/examples/` preserve sequential visual captures, including the internal-scroll states for Modal Abuse.
- `patterns/<pattern-id>/knowledge.md` combines captured catalog evidence with independent conceptual research and records exceptions/limitations.
- `patterns/<pattern-id>/detection.md` gives role-specific recognition guidance, false-positive controls, and the test disposition.

The Impeccable website is the empirical catalog/example source; independent citations in each knowledge file support conceptual principles and correction guidance. A catalog statement and a research source are not interchangeable. Preserve provenance and record disagreement or uncertainty instead of silently blending claims.

## Use and maintenance boundaries

Reference examples illustrate signals, not universal design rules. Screenshots do not establish responsive behavior, source implementation, or product intent. The files are retained evidence, not temporary artifacts; do not regenerate/overwrite or delete captures during ordinary reviews. Update the registry only when the catalog/evidence sources are deliberately reconciled and validate every link afterward.