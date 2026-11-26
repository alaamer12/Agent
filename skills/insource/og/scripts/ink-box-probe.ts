#!/usr/bin/env node
/**
 * ink-box-probe.ts — the Phase 0 selection gate.
 *
 * Proves three things before any layout is written:
 *   1. the renderer shapes the product's hardest script correctly (ink box, not advance width);
 *   2. mixed scripts do or do not agree with a reference renderer (this decides the one-script-per-line law);
 *   3. the font file is what renders — with `fontFiles: []` the ink box must collapse to 0 x 0.
 *
 *   node scripts/ink-box-probe.ts --font ./fonts/brand-var.ttf --family BrandFace \
 *        --text "أرباح صافية" --text "Net profits" --text "صندوق Net profits"
 *
 * Requires: npm i @resvg/resvg-js
 * Compare the numbers with the same strings rendered in a browser at the same size.
 */

import { inflateSync } from 'node:zlib'
import { Resvg } from '@resvg/resvg-js'

type ProbeOptions = {
  fontPath?: string
  family: string
  size: number
  background: string
  texts: string[]
}

function parseArgs(argv: string[]): ProbeOptions {
  const opts: ProbeOptions = { family: 'sans-serif', size: 64, background: '#000000', texts: [] }
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i]
    if (a === '--font') opts.fontPath = argv[++i]
    else if (a === '--family') opts.family = argv[++i]
    else if (a === '--size') opts.size = Number(argv[++i])
    else if (a === '--bg') opts.background = argv[++i]
    else if (a === '--text') opts.texts.push(argv[++i])
  }
  if (!opts.texts.length) opts.texts = ['الأرباح الصافية', 'Net profits', 'صندوق Net profits']
  return opts
}

/** Rasterise one line and measure the bounding box of pixels that differ from the background. */
function inkBox(text: string, opts: ProbeOptions, withFont: boolean): { w: number; h: number; png: Uint8Array } {
  const pad = 40
  const width = 1400
  const height = Math.ceil(opts.size * 2.4)
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}">
  <rect width="100%" height="100%" fill="${opts.background}"/>
  <text x="${pad}" y="${Math.round(height * 0.7)}" font-family="${opts.family}" font-size="${opts.size}"
        fill="#ffffff" direction="auto">${escapeXml(text)}</text>
</svg>`

  const png = new Resvg(svg, {
    fitTo: { mode: 'width', value: width },
    font: {
      fontFiles: withFont && opts.fontPath ? [opts.fontPath] : [],
      loadSystemFonts: false,
      defaultFontFamily: opts.family,
    },
  })
    .render()
    .asPng()

  const box = measureInk(png, width, height, opts.background)
  return { ...box, png }
}

function escapeXml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

/**
 * Minimal RGBA scan of a rendered PNG. Uses the PNG's own bytes via a permissive decode: resvg emits
 * colour type 6 (RGBA) at 8-bit, non-interlaced, so a straight zlib inflate + defilter is enough.
 */
function measureInk(png: Uint8Array, width: number, height: number, background: string) {
  const buf = Buffer.from(png)
  const idat: Buffer[] = []
  let off = 8
  let channels = 4
  while (off + 8 <= buf.length) {
    const len = buf.readUInt32BE(off)
    const type = buf.toString('ascii', off + 4, off + 8)
    if (type === 'IHDR') channels = buf[off + 8 + 9] === 6 ? 4 : 3
    else if (type === 'IDAT') idat.push(buf.subarray(off + 8, off + 8 + len))
    else if (type === 'IEND') break
    off += 12 + len
  }
  const raw = inflateSync(Buffer.concat(idat))
  const stride = width * channels
  const bg = hexToRgb(background)
  let minX = width, minY = height, maxX = -1, maxY = -1
  const prev = new Uint8Array(stride)

  for (let y = 0; y < height; y++) {
    const base = y * (stride + 1)
    const filter = raw[base]
    const cur = Uint8Array.prototype.slice.call(raw, base + 1, base + 1 + stride)
    for (let i = 0; i < stride; i++) {
      const a = i >= channels ? cur[i - channels] : 0
      const b = prev[i]
      const c = i >= channels ? prev[i - channels] : 0
      const p = a + b - c
      const pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c)
      const pred = filter === 1 ? a : filter === 2 ? b : filter === 3 ? (a + b) >> 1 : filter === 4 ? (pa <= pb && pa <= pc ? a : pb <= pc ? b : c) : 0
      cur[i] = (cur[i] + pred) & 0xff
    }
    for (let x = 0; x < width; x++) {
      const s = x * channels
      const dr = Math.abs(cur[s] - bg.r), dg = Math.abs(cur[s + 1] - bg.g), db = Math.abs(cur[s + 2] - bg.b)
      if (dr + dg + db > 24) {
        if (x < minX) minX = x
        if (y < minY) minY = y
        if (x > maxX) maxX = x
        if (y > maxY) maxY = y
      }
    }
    prev.set(cur)
  }
  return maxX < 0 ? { w: 0, h: 0 } : { w: maxX - minX + 1, h: maxY - minY + 1 }
}

function hexToRgb(hex: string) {
  const h = hex.replace('#', '')
  return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16) }
}

function main() {
  const opts = parseArgs(process.argv.slice(2))
  console.log(`font: ${opts.fontPath ?? '(none)'}  family: ${opts.family}  size: ${opts.size}\n`)
  console.log('text                              with font      without font   verdict')

  let mixed = false
  for (const text of opts.texts) {
    const a = inkBox(text, opts, true)
    const b = inkBox(text, opts, false)
    const embedded = b.w === 0 && b.h === 0
    const scripts = new Set([...text].map((c) => (/[\u0600-\u06FF]/.test(c) ? 'ar' : /[A-Za-z]/.test(c) ? 'latin' : '')))
    scripts.delete('')
    if (scripts.size > 1) mixed = true
    console.log(
      `${text.slice(0, 32).padEnd(33)} ${`${a.w}x${a.h}`.padEnd(14)} ${`${b.w}x${b.h}`.padEnd(14)} ${
        embedded ? (scripts.size > 1 ? 'MIXED — split into runs' : 'pass') : 'FONT NOT EMBEDDED'
      }`,
    )
  }

  console.log('\nnext:')
  console.log('  1. render the same strings in a browser at the same size and compare the ink boxes.')
  console.log('  2. within ~1 px on single-script lines → renderer accepted.')
  console.log('  3. any mixed line that differs → adopt one-script-run-per-line as a design law.')
  if (mixed) console.log('  4. this run contained mixed lines: expect them to differ. That is the finding, not a bug.')
}

main()
