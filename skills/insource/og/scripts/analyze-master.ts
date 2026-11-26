#!/usr/bin/env node
/**
 * analyze-master.ts — measure a supplied brand PNG before drawing anything.
 *
 * No dependencies: node:zlib + the PNG spec. Supports 8-bit, non-interlaced, colour types 0/2/3/4/6.
 *
 *   node scripts/analyze-master.ts master.png
 *   node scripts/analyze-master.ts master.png --bands --palette --bbox
 *
 * Two modes, chosen automatically:
 *   - the image HAS transparency  → ink = alpha > 8        (a cut-out logo)
 *   - the image is FULLY OPAQUE   → ink = distance from the modal background colour
 *
 * That second mode matters: a designer often exports an RGBA file whose alpha is 255 everywhere, and an
 * alpha-based profile then reports one giant band and "no padding", which is worse than useless.
 */

import { readFileSync } from 'node:fs'
import { inflateSync } from 'node:zlib'

type Rgba = { width: number; height: number; data: Uint8Array } // 4 bytes per pixel
type Rgb = { r: number; g: number; b: number }

const PNG_SIG = 0x89504e47
const ALPHA_FLOOR = 8
const COLOUR_TOLERANCE = 28 // sum of |dr|+|dg|+|db| that still counts as "background"

function paeth(a: number, b: number, c: number): number {
  const p = a + b - c
  const pa = Math.abs(p - a)
  const pb = Math.abs(p - b)
  const pc = Math.abs(p - c)
  return pa <= pb && pa <= pc ? a : pb <= pc ? b : c
}

function decodePng(path: string): Rgba {
  const buf = readFileSync(path)
  if (buf.readUInt32BE(0) !== PNG_SIG) throw new Error(`${path}: not a PNG`)

  let off = 8
  let width = 0
  let height = 0
  let bitDepth = 0
  let colorType = 0
  let interlace = 0
  const idat: Buffer[] = []
  let plte: Buffer | undefined
  let trns: Buffer | undefined

  while (off + 8 <= buf.length) {
    const len = buf.readUInt32BE(off)
    const type = buf.toString('ascii', off + 4, off + 8)
    const data = buf.subarray(off + 8, off + 8 + len)
    if (type === 'IHDR') {
      width = data.readUInt32BE(0)
      height = data.readUInt32BE(4)
      bitDepth = data[8]
      colorType = data[9]
      interlace = data[12]
    } else if (type === 'IDAT') idat.push(data)
    else if (type === 'PLTE') plte = data
    else if (type === 'tRNS') trns = data
    else if (type === 'IEND') break
    off += 12 + len
  }

  if (bitDepth !== 8) throw new Error(`bit depth ${bitDepth} unsupported; re-export at 8-bit`)
  if (interlace !== 0) throw new Error('interlaced PNG unsupported; re-export without interlacing')

  const channels = colorType === 6 ? 4 : colorType === 2 ? 3 : colorType === 4 ? 2 : 1
  const raw = inflateSync(Buffer.concat(idat))
  const stride = width * channels
  const out = new Uint8Array(width * height * 4)
  const prev = new Uint8Array(stride)

  for (let y = 0; y < height; y++) {
    const base = y * (stride + 1)
    const filter = raw[base]
    const cur: Uint8Array = Uint8Array.prototype.slice.call(raw, base + 1, base + 1 + stride)

    for (let i = 0; i < stride; i++) {
      const a = i >= channels ? cur[i - channels] : 0
      const b = prev[i]
      const c = i >= channels ? prev[i - channels] : 0
      switch (filter) {
        case 1: cur[i] = (cur[i] + a) & 0xff; break
        case 2: cur[i] = (cur[i] + b) & 0xff; break
        case 3: cur[i] = (cur[i] + ((a + b) >> 1)) & 0xff; break
        case 4: cur[i] = (cur[i] + paeth(a, b, c)) & 0xff; break
        default: break
      }
    }

    for (let x = 0; x < width; x++) {
      const s = x * channels
      const d = (y * width + x) * 4
      if (colorType === 3 && plte) {
        const idx = cur[s]
        out[d] = plte[idx * 3]
        out[d + 1] = plte[idx * 3 + 1]
        out[d + 2] = plte[idx * 3 + 2]
        out[d + 3] = trns && idx < trns.length ? trns[idx] : 255
      } else if (channels === 4) {
        out[d] = cur[s]; out[d + 1] = cur[s + 1]; out[d + 2] = cur[s + 2]; out[d + 3] = cur[s + 3]
      } else if (channels === 3) {
        out[d] = cur[s]; out[d + 1] = cur[s + 1]; out[d + 2] = cur[s + 2]; out[d + 3] = 255
      } else if (channels === 2) {
        out[d] = out[d + 1] = out[d + 2] = cur[s]; out[d + 3] = cur[s + 1]
      } else {
        out[d] = out[d + 1] = out[d + 2] = cur[s]; out[d + 3] = 255
      }
    }
    prev.set(cur)
  }

  return { width, height, data: out }
}

const px = (img: Rgba, x: number, y: number) => (y * img.width + x) * 4

const luma = (r: number, g: number, b: number) => 0.2126 * r + 0.7152 * g + 0.0722 * b

function transparentFraction(img: Rgba): number {
  let n = 0
  for (let i = 3; i < img.data.length; i += 4) if (img.data[i] < 250) n++
  return n / (img.width * img.height)
}

/** The modal 5-bit bucket's mean colour over opaque pixels — the plate colour of an opaque master. */
function modalBackground(img: Rgba): Rgb {
  const buckets = new Map<number, { n: number; r: number; g: number; b: number }>()
  for (let i = 0; i < img.data.length; i += 4) {
    if (img.data[i + 3] < 200) continue
    const key = ((img.data[i] >> 3) << 10) | ((img.data[i + 1] >> 3) << 5) | (img.data[i + 2] >> 3)
    const e = buckets.get(key) ?? { n: 0, r: 0, g: 0, b: 0 }
    e.n++; e.r += img.data[i]; e.g += img.data[i + 1]; e.b += img.data[i + 2]
    buckets.set(key, e)
  }
  let best = { n: -1, r: 0, g: 0, b: 0 }
  for (const e of buckets.values()) if (e.n > best.n) best = e
  return { r: best.r / best.n, g: best.g / best.n, b: best.b / best.n }
}

type InkMode = 'alpha' | 'colour' | 'luma'

/**
 * Pick the measure that matches what "ink" means in this artwork:
 *   alpha  — a cut-out logo on transparency
 *   luma   — bright artwork on a dark plate (a baked background: count the BRIGHT content only)
 *   colour — flat background, content differs in hue at similar brightness
 */
function chooseMode(img: Rgba, bg: Rgb): InkMode {
  if (transparentFraction(img) >= 0.35) return 'alpha'
  const bgLuma = luma(bg.r, bg.g, bg.b)
  let bright = 0
  let opaque = 0
  for (let i = 0; i < img.data.length; i += 4) {
    if (img.data[i + 3] < 200) continue
    opaque++
    if (luma(img.data[i], img.data[i + 1], img.data[i + 2]) > 100) bright++
  }
  if (bgLuma < 60 && opaque > 0 && bright / opaque < 0.45) return 'luma'
  return 'colour'
}

function makeInkTest(img: Rgba, mode: InkMode, lumaThreshold: number, bg: Rgb) {
  if (mode === 'alpha') return (i: number) => img.data[i + 3] > ALPHA_FLOOR
  if (mode === 'luma') {
    return (i: number) =>
      img.data[i + 3] > 200 && luma(img.data[i], img.data[i + 1], img.data[i + 2]) > lumaThreshold
  }
  return (i: number) => {
    const d =
      Math.abs(img.data[i] - bg.r) + Math.abs(img.data[i + 1] - bg.g) + Math.abs(img.data[i + 2] - bg.b)
    return d > COLOUR_TOLERANCE
  }
}

function bbox(img: Rgba, isInk: (i: number) => boolean) {
  let minX = img.width, minY = img.height, maxX = -1, maxY = -1
  for (let y = 0; y < img.height; y++) {
    for (let x = 0; x < img.width; x++) {
      if (isInk(px(img, x, y))) {
        if (x < minX) minX = x
        if (y < minY) minY = y
        if (x > maxX) maxX = x
        if (y > maxY) maxY = y
      }
    }
  }
  return { minX, minY, maxX, maxY, width: maxX - minX + 1, height: maxY - minY + 1 }
}

function inkRows(img: Rgba, isInk: (i: number) => boolean, box: { minX: number; maxX: number }) {
  const rows = new Uint32Array(img.height)
  for (let y = 0; y < img.height; y++) {
    let n = 0
    for (let x = box.minX; x <= box.maxX; x++) if (isInk(px(img, x, y))) n++
    rows[y] = n
  }
  return rows
}

function bands(rows: Uint32Array) {
  const out: Array<{ from: number; to: number; kind: 'ink' | 'gap' }> = []
  let start = 0
  let kind: 'ink' | 'gap' = rows[0] > 0 ? 'ink' : 'gap'
  for (let y = 1; y < rows.length; y++) {
    const k: 'ink' | 'gap' = rows[y] > 0 ? 'ink' : 'gap'
    if (k !== kind) {
      out.push({ from: start, to: y - 1, kind })
      start = y
      kind = k
    }
  }
  out.push({ from: start, to: rows.length - 1, kind })
  return out.filter((b) => b.kind === 'ink' || b.to - b.from >= 4)
}

function palette(img: Rgba, isInk: (i: number) => boolean, box: { minX: number; minY: number; maxX: number; maxY: number }) {
  const buckets = new Map<number, { n: number; r: number; g: number; b: number }>()
  for (let y = box.minY; y <= box.maxY; y++) {
    for (let x = box.minX; x <= box.maxX; x++) {
      const i = px(img, x, y)
      if (!isInk(i)) continue
      const key = ((img.data[i] >> 3) << 10) | ((img.data[i + 1] >> 3) << 5) | (img.data[i + 2] >> 3)
      const e = buckets.get(key) ?? { n: 0, r: 0, g: 0, b: 0 }
      e.n++; e.r += img.data[i]; e.g += img.data[i + 1]; e.b += img.data[i + 2]
      buckets.set(key, e)
    }
  }
  const hex = (n: number) => Math.round(n).toString(16).padStart(2, '0')
  const total = [...buckets.values()].reduce((s, e) => s + e.n, 0) || 1
  return [...buckets.values()]
    .sort((a, b) => b.n - a.n)
    .slice(0, 16)
    .map((e) => ({
      hex: `#${hex(e.r / e.n)}${hex(e.g / e.n)}${hex(e.b / e.n)}`.toUpperCase(),
      share: ((e.n / total) * 100).toFixed(1) + '%',
      pixels: e.n,
    }))
}

function main() {
  const argv = process.argv.slice(2)
  const file = argv.find((a) => !a.startsWith('--') && !/^\d+$/.test(a))
  const flags = argv.filter((a) => a.startsWith('--'))
  if (!file) {
    console.error('usage: node scripts/analyze-master.ts <file.png> [--bbox] [--bands] [--palette]')
    console.error('       [--mode alpha|colour|luma] [--luma 100]')
    process.exit(2)
  }
  const modeArg = argv[argv.indexOf('--mode') + 1]
  const lumaArg = Number(argv[argv.indexOf('--luma') + 1])
  const lumaThreshold = Number.isFinite(lumaArg) && lumaArg > 0 ? lumaArg : 100

  const img = decodePng(file)
  const bg = modalBackground(img)
  const mode: InkMode = (['alpha', 'colour', 'luma'] as const).includes(modeArg as InkMode)
    ? (modeArg as InkMode)
    : chooseMode(img, bg)
  const isInk = makeInkTest(img, mode, lumaThreshold, bg)
  const box = bbox(img, isInk)
  const rows = inkRows(img, isInk, box)

  const hexBg = [bg.r, bg.g, bg.b].map((n) => Math.round(n).toString(16).padStart(2, '0')).join('').toUpperCase()

  console.log(`file      ${file}`)
  console.log(`size      ${img.width} x ${img.height}`)
  console.log(
    `ink mode  ${mode}${mode === 'luma' ? ` (luma > ${lumaThreshold})` : ''}` +
      (mode === 'alpha' ? ` (alpha > ${ALPHA_FLOOR})` : ` (plate #${hexBg})`),
  )
  if (box.maxX < 0) {
    console.log('content   none — the whole image matches the background')
    return
  }
  console.log(
    `ink box   x=${box.minX}..${box.maxX} y=${box.minY}..${box.maxY} (${box.width} x ${box.height})`,
  )
  console.log(
    `padding   left=${box.minX} right=${img.width - 1 - box.maxX} top=${box.minY} bottom=${img.height - 1 - box.maxY}`,
  )
  if (mode !== 'alpha') {
    console.log('          (measured against the bright/foreground content, not the baked plate)')
  }

  if (flags.includes('--bands') || flags.length === 0) {
    console.log('\ncontent bands (gaps >= 4 rows):')
    for (const b of bands(rows)) {
      console.log(`  ${b.kind.padEnd(3)} ${String(b.from).padStart(5)} .. ${String(b.to).padStart(5)}  (${b.to - b.from + 1} rows)`)
    }
    console.log('\n  → set each region boundary a few px INSIDE the gap it cuts, so a resample cannot bleed across.')
  }

  if (flags.includes('--palette') || flags.length === 0) {
    console.log('\ndominant ink colours (5-bit buckets, background excluded):')
    for (const p of palette(img, isInk, box)) console.log(`  ${p.hex}  ${p.share.padStart(6)}  ${p.pixels} px`)
    console.log('\n  → these are the measured values. Do not substitute the stylesheet accent for them.')
  }
}

main()
