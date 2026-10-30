import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const manifest = JSON.parse(
  fs.readFileSync(path.join(ROOT, "references/manifest.json"), "utf8"),
);

const HEADINGS = [
  "identity",
  "perceived-look",
  "frame-anatomy",
  "motion-law",
  "technique-and-math",
  "parameters",
  "palette-and-color",
  "composition-and-camera",
  "randomness-and-seeds",
  "performance-budget",
  "host-integration",
  "failure-modes-and-tells",
  "tuning-knobs",
  "verification-checklist",
  "porting-notes",
];

const REQUIRED_FRONTMATTER = [
  "id",
  "name",
  "family",
  "renderer",
  "poster",
  "complexity",
  "source_lines",
  "dpr_max",
  "deps",
  "poster_capture",
];

const slug = (heading) =>
  heading
    .toLowerCase()
    .replace(/^\d+\.\s*/, "")
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "");

const readFrontmatter = (text) => {
  if (!text.startsWith("---\n")) return null;
  const end = text.indexOf("\n---", 4);
  if (end === -1) return null;
  const block = text.slice(4, end);
  const data = {};
  for (const line of block.split("\n")) {
    const m = /^([a-z_]+):\s*(.*)$/.exec(line);
    if (m) data[m[1]] = m[2].trim();
  }
  return data;
};

const jpegSize = (file) => {
  let buf;
  try {
    buf = fs.readFileSync(file);
  } catch {
    return null;
  }
  if (buf[0] !== 0xff || buf[1] !== 0xd8) return null;
  let offset = 2;
  while (offset < buf.length - 9) {
    if (buf[offset] !== 0xff) {
      offset += 1;
      continue;
    }
    const marker = buf[offset + 1];
    if (marker === 0xd8 || marker === 0xd9) {
      offset += 2;
      continue;
    }
    const length = buf.readUInt16BE(offset + 2);
    const isSof = marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker);
    if (isSof) {
      return { height: buf.readUInt16BE(offset + 5), width: buf.readUInt16BE(offset + 7) };
    }
    offset += 2 + length;
  }
  return null;
};

const familyDoc = (family) => {
  const dir = path.join(ROOT, "references/families");
  const match = fs.readdirSync(dir).find((f) => f.startsWith(family));
  return match ? path.join(dir, match) : null;
};

const indexText = fs.existsSync(path.join(ROOT, "references/index.md"))
  ? fs.readFileSync(path.join(ROOT, "references/index.md"), "utf8")
  : "";

let failures = 0;
const report = [];

if (manifest.scenes.length !== 50) {
  report.push(`manifest: expected 50 scenes, found ${manifest.scenes.length}`);
  failures += 1;
}

for (const scene of manifest.scenes) {
  const issues = [];
  const file = path.join(ROOT, "references/scenes", `${scene.id}.md`);

  if (!fs.existsSync(file)) {
    report.push(`${scene.id}: [MISSING_FILE]`);
    failures += 1;
    continue;
  }

  const text = fs.readFileSync(file, "utf8");
  const fm = readFrontmatter(text);

  if (!fm) issues.push("NO_FRONTMATTER");
  else {
    for (const key of REQUIRED_FRONTMATTER) if (!(key in fm)) issues.push(`FM_${key}`);
    if (fm.id && fm.id !== scene.id) issues.push("FM_ID_MISMATCH");
    if (fm.family && fm.family !== scene.family) issues.push("FM_FAMILY_MISMATCH");
    if (fm.complexity && fm.complexity !== scene.complexity) issues.push("FM_COMPLEXITY");
    if (fm.renderer && fm.renderer !== scene.renderer) issues.push("FM_RENDERER");
    if (fm.source_lines && Number(fm.source_lines) !== scene.source_lines) {
      issues.push("FM_LINES");
    }
    const dpr = (value) =>
      value == null || value === "null" ? null : Number(value);
    if (fm.dpr_max && dpr(fm.dpr_max) !== dpr(scene.dpr_max)) {
      issues.push("FM_DPR");
    }
  }

  if (text.includes("```")) issues.push("CODE_FENCE");

  const found = [...text.matchAll(/^##\s+(.+)$/gm)].map((m) => slug(m[1]));
  let cursor = 0;
  for (const expected of HEADINGS) {
    const at = found.indexOf(expected, cursor);
    if (at === -1) issues.push(`MISSING_${expected}`);
    else cursor = at + 1;
  }

  if (!/^\|\s*name\s*\|\s*value\s*\|\s*range\s*\|\s*effect\s*\|\s*sensitivity\s*\|/m.test(text)) {
    issues.push("PARAM_HEADER");
  }

  const paramStart = text.search(/^##\s+6\.\s*Parameters/m);
  const paramEnd = text.search(/^##\s+7\./m);
  if (paramStart !== -1 && paramEnd > paramStart) {
    const rows = text
      .slice(paramStart, paramEnd)
      .split("\n")
      .filter((l) => /^\|\s*[^|\-]/.test(l)).length - 1;
    if (rows < 10) issues.push(`PARAM_ROWS_${rows}`);
  }

  const paletteStart = text.search(/^##\s+7\./m);
  const paletteEnd = text.search(/^##\s+8\./m);
  if (paletteStart !== -1 && paletteEnd > paletteStart) {
    const palette = text.slice(paletteStart, paletteEnd);
    if (!/#[0-9a-f]{3,8}\b/i.test(palette) && !/\bhsla?\(/i.test(palette)) {
      issues.push("NO_COLOR_TOKEN");
    }
  }

  const poster = jpegSize(path.join(ROOT, scene.poster));
  if (!poster) issues.push("POSTER_MISSING");
  else if (poster.width !== 640 || poster.height !== 400) {
    issues.push(`POSTER_${poster.width}x${poster.height}`);
  }

  if (!familyDoc(scene.family)) issues.push("FAMILY_DOC_MISSING");
  if (!indexText.includes(`scenes/${scene.id}.md`)) issues.push("INDEX_MISSING");

  if (issues.length) failures += 1;
  report.push(`${scene.id}: ${issues.length ? `[${issues.join(", ")}]` : "OK"}`);
}

const familyDir = path.join(ROOT, "references/families");
const familyCount = fs.readdirSync(familyDir).filter((f) => f.endsWith(".md")).length;

const markdownFiles = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name.startsWith(".")) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.name.endsWith(".md")) markdownFiles.push(full);
  }
};
walk(ROOT);

let brokenLinks = 0;
for (const file of markdownFiles) {
  const text = fs.readFileSync(file, "utf8");
  for (const match of text.matchAll(/\[[^\]]*\]\(([^)\s]+)\)/g)) {
    let target = match[1];
    if (/^(https?:|mailto:|#)/.test(target)) continue;
    if (/[{}<>]/.test(target)) continue;
    target = target.split("#")[0];
    if (!target) continue;
    const resolved = path.resolve(path.dirname(file), target);
    if (!fs.existsSync(resolved)) {
      brokenLinks += 1;
      report.push(`${path.relative(ROOT, file)}: [BROKEN_LINK ${target}]`);
    }
  }
}

report.push("");
report.push(`scenes ok: ${manifest.scenes.length - failures}/${manifest.scenes.length}  families: ${familyCount}/13  broken links: ${brokenLinks}`);

console.log(report.join("\n"));
if (failures || brokenLinks) process.exitCode = 1;
