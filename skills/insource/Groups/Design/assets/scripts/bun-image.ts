/**
 * Image variants + ThumbHash placeholders via Bun.Image - the built-in, zero-dependency image
 * pipeline (Bun >= 1.3.14; shaped after sharp). Use this instead of the Python scripts when the
 * project already runs on Bun and wants placeholders or native-speed resizing.
 *
 * Usage:
 *   bun run scripts/bun-image.ts <input> --out-dir <dir> [--variants 320,640,1280]
 *       [--format webp|avif|jpeg|png] [--quality 80] [--thumbnail 240] [--placeholder]
 *
 * Output:
 *   <out-dir>/<stem>-<width>.<ext>   one file per variant (or a single thumbnail with --thumbnail)
 *   <out-dir>/<stem>.lqip.txt        the placeholder data URL (with --placeholder)
 *
 * It reports the source size, each output size, and the placeholder byte length.
 */

import { parseArgs } from "node:util";
import { mkdirSync } from "node:fs";

if (typeof Bun.Image !== "function") {
  console.error("error: Bun.Image is unavailable - requires Bun >= 1.3.14");
  process.exit(2);
}

const { values, positionals } = parseArgs({
  allowPositionals: true,
  options: {
    "out-dir": { type: "string" },
    variants: { type: "string" },
    format: { type: "string", default: "webp" },
    quality: { type: "string", default: "80" },
    thumbnail: { type: "string" },
    placeholder: { type: "boolean", default: false },
  },
});

const input = positionals[0];
if (!input || !values["out-dir"]) {
  console.error("usage: bun run bun-image.ts <input> --out-dir <dir> [--variants 320,640] [--thumbnail 240] [--placeholder]");
  process.exit(2);
}

const format = values.format.toLowerCase();
const formats: Record<string, (img: any, quality: number) => any> = {
  webp: (img, quality) => img.webp({ quality }),
  avif: (img, quality) => img.avif({ quality }),
  jpeg: (img, quality) => img.jpeg({ quality }),
  png: (img) => img.png({ compressionLevel: 9 }),
};
if (!formats[format]) {
  console.error(`error: unsupported format ${format} - use webp, avif, jpeg or png`);
  process.exit(2);
}
const ext = format === "jpeg" ? "jpg" : format;

mkdirSync(values["out-dir"], { recursive: true });
const outDir = values["out-dir"].replace(/\/+$/, "");
const stem = input.replace(/^.*[\\/]/, "").replace(/\.[^.]+$/, "");
const source = Bun.file(input);
const before = source.size ?? (await source.arrayBuffer()).byteLength;
const meta = await source.image().metadata();
console.log(`in    : ${input} ${meta.width}x${meta.height} ${meta.format} (${before} bytes)`);

const quality = Number.parseInt(values.quality, 10);
const widths = values.variants
  ? values.variants.split(",").map((part) => Number.parseInt(part.trim(), 10)).filter((n) => n > 0)
  : values.thumbnail
    ? [Number.parseInt(values.thumbnail, 10)]
    : [];
if (widths.length === 0) {
  console.error("error: give --variants 320,640 or --thumbnail 240");
  process.exit(2);
}

let total = 0;
for (const width of widths) {
  const target = `${outDir}/${stem}-${width}.${ext}`;
  const written = await formats[format](source.image().resize(width, undefined, { withoutEnlargement: true }), quality).write(target);
  total += written;
  console.log(`out   : ${target} (${written} bytes)`);
}

const saved = before ? (100 * (before - total)) / before : 0;
console.log(`total : ${total} bytes across ${widths.length} file(s) vs ${before} before (${saved.toFixed(1)}% saved)`);

if (values.placeholder) {
  const lqip = await source.image().placeholder();
  const target = `${outDir}/${stem}.lqip.txt`;
  await Bun.write(target, lqip);
  console.log(`lqip  : ${target} (${lqip.length} chars, ThumbHash data URL)`);
}
