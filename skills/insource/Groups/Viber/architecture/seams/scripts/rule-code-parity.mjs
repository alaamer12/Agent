#!/usr/bin/env node
// rule-code-parity — set-difference between the rule codes a registry defines and the
// rule codes documents name. Two lists, one symmetric difference, no opinions.
//
// It measures: which codes exist only in the registry, and which only in the prose.
// It refuses to: pick a side, invent a code, rewrite a doc, or judge whether a code is
// well named. When the two disagree one of them is stale, and which one is a decision.

import { readFileSync, readdirSync, statSync, existsSync } from "node:fs";
import path from "node:path";

const VERSION = "1.0";
const DEFAULT_CODE_RE_SOURCE = "\\b[A-Z][A-Z0-9]*(?:[_-][A-Z0-9]+)+\\b"; // SCREAMING_WITH_SEPARATORS
const DOC_EXT = new Set([".md", ".markdown", ".txt", ".rst"]);

const USAGE = `rule-code-parity ${VERSION} — docs and the rule registry must name the same codes

  node scripts/rule-code-parity.mjs --registry <codes.json> [doc-or-dir ...] [options]

  --registry <file>     The authoritative list. Accepted shapes:
                          ["CODE_A", "CODE_B"]
                          [{ "code": "CODE_A" }, { "id": "CODE_B", ... }]
                          { "CODE_A": {...}, "CODE_B": {...} }
  --registry-field <k>  Key to read when the registry holds objects (default tries: code, id, name)
  --docs <file|dir>     A doc to scan; repeatable. Directories are walked for .md/.txt/.rst.
  --pattern <regex>     How a code is recognised in prose (default: SCREAMING_SNAKE or
                        SCREAMING-KEBAB, at least one separator). Regex source, no slashes.
  --ignore <CODE>       Drop this token from both sides; repeatable. For a term that reads
                        like a code but is prose.
  --only-registry       Report only the "documented nowhere" direction (never the reverse).
  --json                Machine output.
  --help                This text.

  Exit codes: 0 the two sets agree in the directions checked; 1 they do not; 2 bad input.

  What this script refuses to do: it never says which side is right, never edits a doc or a
  registry, and never invents a code to close the gap. It also cannot see a code written in
  lowercase, or in a script the configured --pattern does not cover — the default pattern is
  a convention, and a codebase that does not share it will look entirely undocumented.
`;

function fail(message) {
  process.stderr.write(`rule-code-parity: ${message}\n`);
  process.exit(2);
}

function parseArgs(argv) {
  const o = { registry: null, field: null, docs: [], pattern: null, ignore: [], onlyRegistry: false, json: false, help: false };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") o.help = true;
    else if (a === "--registry") o.registry = argv[++i];
    else if (a === "--registry-field") o.field = argv[++i];
    else if (a === "--docs") o.docs.push(argv[++i]);
    else if (a === "--pattern") o.pattern = argv[++i];
    else if (a === "--ignore") o.ignore.push(argv[++i]);
    else if (a === "--only-registry") o.onlyRegistry = true;
    else if (a === "--json") o.json = true;
    else if (a.startsWith("--")) fail(`unknown option: ${a}`);
    else o.docs.push(a);
  }
  return o;
}

function readRegistryCodes(file, field) {
  let data;
  try {
    data = JSON.parse(readFileSync(file, "utf8"));
  } catch (e) {
    fail(`cannot read registry as JSON (${file}): ${e.message}`);
  }
  const items = Array.isArray(data) ? data : data.rules ?? data.codes ?? Object.entries(data);
  const keys = [field, "code", "id", "name"].filter(Boolean);
  const codes = [];
  for (const item of items) {
    if (typeof item === "string") codes.push(item);
    else if (Array.isArray(item) && typeof item[0] === "string") codes.push(item[0]);
    else if (item && typeof item === "object") {
      const hit = keys.map((k) => item[k]).find((v) => typeof v === "string");
      if (hit) codes.push(hit);
    }
  }
  if (codes.length === 0) fail(`no codes found in registry ${file} (tried keys: ${keys.join(", ")})`);
  return [...new Set(codes)];
}

function collectDocFiles(paths) {
  const out = [];
  const walk = (p, explicit) => {
    const st = statSync(p);
    if (st.isDirectory()) {
      for (const ent of readdirSync(p, { withFileTypes: true })) {
        if (ent.name === "node_modules" || ent.name.startsWith(".")) continue;
        walk(path.join(p, ent.name), false);
      }
    } else if (st.isFile()) {
      // An explicitly named file is read whatever its extension; a walked one must look like a doc.
      if (explicit || DOC_EXT.has(path.extname(p).toLowerCase())) out.push(p);
    }
  };
  for (const p of paths) {
    if (!existsSync(p)) fail(`doc path does not exist: ${p}`);
    walk(p, !statSync(p).isDirectory());
  }
  return out;
}

function main() {
  const o = parseArgs(process.argv.slice(2));
  if (o.help) {
    process.stdout.write(USAGE);
    return 0;
  }
  if (!o.registry) fail("--registry is required (the authoritative list of rule codes)");
  if (o.docs.length === 0) fail("give at least one doc file or directory to scan");

  let re;
  try {
    re = new RegExp(o.pattern ?? DEFAULT_CODE_RE_SOURCE, "g");
  } catch (e) {
    fail(`--pattern is not a valid regex source: ${e.message}`);
  }

  const registry = readRegistryCodes(o.registry, o.field);
  const registrySet = new Set(registry);
  const ignored = new Set(o.ignore);

  const seen = new Map(); // code -> files naming it
  const docFiles = collectDocFiles(o.docs);
  for (const file of docFiles) {
    const text = readFileSync(file, "utf8");
    for (const m of text.matchAll(re)) {
      if (ignored.has(m[0])) continue;
      if (!seen.has(m[0])) seen.set(m[0], new Set());
      seen.get(m[0]).add(file);
    }
  }

  const onlyInRegistry = registry.filter((c) => !ignored.has(c) && !seen.has(c));
  const onlyInDocs = [...seen.keys()].filter((c) => !registrySet.has(c));
  const inBoth = registry.filter((c) => seen.has(c) && !ignored.has(c));

  const ok = onlyInRegistry.length === 0 && (o.onlyRegistry || onlyInDocs.length === 0);

  if (o.json) {
    process.stdout.write(
      JSON.stringify(
        {
          registry: o.registry,
          registryCodes: registry.length,
          docsScanned: docFiles.length,
          inBoth,
          onlyInRegistry,
          onlyInDocs: o.onlyRegistry ? [] : onlyInDocs.map((c) => ({ code: c, files: [...seen.get(c)] })),
          ok,
        },
        null,
        2,
      ) + "\n",
    );
    return ok ? 0 : 1;
  }

  process.stdout.write(
    `rule-code-parity ${VERSION} — registry ${o.registry} (${registry.length} codes), ${docFiles.length} docs scanned\n\n` +
      `  named in both          : ${inBoth.length}\n` +
      `  only in registry       : ${onlyInRegistry.length}  (registry names it, no doc does)\n` +
      (o.onlyRegistry ? "" : `  only in docs           : ${onlyInDocs.length}  (a doc names it, the registry does not)\n`),
  );
  for (const c of onlyInRegistry) process.stdout.write(`      R  ${c}\n`);
  if (!o.onlyRegistry) {
    for (const c of onlyInDocs) process.stdout.write(`      D  ${c}  <- ${[...seen.get(c)].join(", ")}\n`);
  }
  process.stdout.write(ok ? "\nThe two lists agree.\n" : "\nThe two lists disagree; which side is stale is not this script's call.\n");
  return ok ? 0 : 1;
}

process.exit(main());
