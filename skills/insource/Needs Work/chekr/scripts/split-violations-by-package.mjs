#!/usr/bin/env bun
/**
 * Split violations.json into per-package slices for parallel agent remediation.
 *
 * Usage (repo root):
 *   bun run .cursor/skills/chekr/scripts/split-violations-by-package.mjs [violations.json] [outDir]
 *
 * Default input: violations.json
 * Default output: scratch/chekr-by-package/
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";

const inputPath = resolve(process.argv[2] ?? "violations.json");
const outDir = resolve(process.argv[3] ?? "scratch/chekr-by-package");

/** @param {string} file */
function sliceKey(file) {
  const norm = file.replace(/\\/g, "/");
  const parts = norm.split("/").filter(Boolean);
  if (parts.length >= 2) {
    return `${parts[0]}-${parts[1]}`;
  }
  if (parts.length === 1) {
    return `_root`;
  }
  return "_unknown";
}

const raw = await readFile(inputPath, "utf8");
const data = JSON.parse(raw);
const violations = data.violations ?? [];

/** @type {Map<string, { passed: boolean, violations: unknown[] }>} */
const buckets = new Map();

for (const violation of violations) {
  const locations = violation.locations ?? (violation.file ? [{ file: violation.file }] : []);
  const keys = new Set(locations.map((loc) => sliceKey(loc.file ?? "")));

  for (const key of keys) {
    if (!buckets.has(key)) {
      buckets.set(key, { passed: false, violations: [] });
    }
    const filtered = {
      ...violation,
      locations: locations.filter((loc) => sliceKey(loc.file ?? "") === key),
    };
    if (filtered.locations.length > 0) {
      buckets.get(key).violations.push(filtered);
    }
  }
}

await mkdir(outDir, { recursive: true });

const index = [];
for (const [key, payload] of [...buckets.entries()].sort(([a], [b]) => a.localeCompare(b))) {
  const outFile = `${key}.json`;
  const outPath = resolve(outDir, outFile);
  await writeFile(outPath, JSON.stringify(payload, null, 2), "utf8");
  const locCount = payload.violations.reduce((n, v) => n + (v.locations?.length ?? 0), 0);
  index.push({ slice: key, file: outFile, violationGroups: payload.violations.length, locations: locCount });
  console.log(`${outFile}: ${payload.violations.length} groups, ${locCount} locations`);
}

const indexPath = resolve(outDir, "_index.json");
await writeFile(
  indexPath,
  JSON.stringify({ source: inputPath, slices: index }, null, 2),
  "utf8",
);
console.log(`Wrote ${index.length} slices to ${outDir}/`);
