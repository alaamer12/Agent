#!/usr/bin/env node
/**
 * img-to-ascii.mjs — Convert a PNG/JPG/WebP image to ASCII text.
 *
 * Usage:
 *   bun scripts/img-to-ascii.mjs <image> [--cols 120] [--invert] [--ramp " .:-=+*#%@"]
 *   node scripts/img-to-ascii.mjs <image> [--cols 120] [--invert] [--ramp " .:-=+*#%@"]
 *
 * Dependency: sharp (works under both Node and Bun).
 *   bun add sharp   |   npm i sharp
 *
 * Why sharp even on modern Bun?
 *   Bun.Image (Bun ≥ 1.3.14) is the preferred pipeline for resize / metadata /
 *   encode and is a drop-in for most sharp workflows. It does not yet expose a
 *   stable raw-RGB terminal for luminance sampling, so this script still uses
 *   sharp for the pixel buffer. Prefer Bun.Image in any new code that only
 *   needs resize or format conversion.
 *
 * Notes:
 *   - Monospace cell-aspect correction: rows = cols * (imgH / imgW) * 0.5
 *   - Luminance uses sRGB perceptual weights (0.2126 / 0.7152 / 0.0722)
 */

import sharp from 'sharp';

const DEFAULT_RAMP = ' .:-=+*#%@';
const CELL_ASPECT = 0.5;

function parseArgs(argv) {
  const args = { cols: 120, invert: false, ramp: DEFAULT_RAMP, file: null };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--cols') args.cols = parseInt(argv[++i], 10);
    else if (a === '--invert') args.invert = true;
    else if (a === '--ramp') args.ramp = argv[++i];
    else if (!a.startsWith('--')) args.file = a;
  }
  return args;
}

async function main() {
  const { cols, invert, ramp, file } = parseArgs(process.argv);
  if (!file) {
    console.error('Usage: bun|node img-to-ascii.mjs <image> [--cols N] [--invert] [--ramp "..."]');
    process.exit(1);
  }

  const meta = await sharp(file).metadata();
  const rows = Math.max(1, Math.round(cols * (meta.height / meta.width) * CELL_ASPECT));

  const { data, info } = await sharp(file)
    .resize(cols, rows, { fit: 'fill' })
    .removeAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });

  const last = ramp.length - 1;
  const lines = [];
  for (let y = 0; y < info.height; y++) {
    let line = '';
    for (let x = 0; x < info.width; x++) {
      const i = (y * info.width + x) * info.channels;
      let lum = (0.2126 * data[i] + 0.7152 * data[i + 1] + 0.0722 * data[i + 2]) / 255;
      if (invert) lum = 1 - lum;
      line += ramp[Math.round(lum * last)];
    }
    lines.push(line);
  }
  process.stdout.write(lines.join('\n') + '\n');
}

main().catch((err) => {
  console.error('Error:', err.message);
  process.exit(1);
});
