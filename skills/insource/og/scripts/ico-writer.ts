#!/usr/bin/env node
/**
 * ico-writer.ts — write a multi-size .ico with no dependency.
 *
 * Browsers request /favicon.ico at the origin root even when a <link rel="icon"> exists, and a single-size
 * ICO is a blurry tab icon on half the machines. An ICO is just a directory of images:
 *
 *   header      6 bytes   reserved(2)=0, type(2)=1, count(2)
 *   directory   16 bytes  per image
 *   payloads    PNG bytes, in directory order (BMP is legacy; every current browser reads PNG entries)
 *
 *   node scripts/ico-writer.ts out.ico 16.png 32.png 48.png
 */

import { readFileSync, writeFileSync } from 'node:fs'

type Entry = { size: number; png: Buffer }

/** Read width/height from a PNG's IHDR (bytes 16..24). */
function pngSize(png: Buffer): number {
  if (png.readUInt32BE(0) !== 0x89504e47) throw new Error('not a PNG')
  const w = png.readUInt32BE(16)
  const h = png.readUInt32BE(20)
  if (w !== h) throw new Error(`ICO entries must be square (got ${w}x${h})`)
  if (w > 256) throw new Error(`ICO entries are at most 256px (got ${w})`)
  return w
}

export function writeIco(entries: Entry[]): Buffer {
  if (!entries.length) throw new Error('no entries')
  const header = Buffer.alloc(6)
  header.writeUInt16LE(0, 0)
  header.writeUInt16LE(1, 2)
  header.writeUInt16LE(entries.length, 4)

  const dir = Buffer.alloc(16 * entries.length)
  let offset = header.length + dir.length

  entries.forEach((entry, i) => {
    const base = i * 16
    // 256 is encoded as 0 in the directory.
    dir.writeUInt8(entry.size === 256 ? 0 : entry.size, base + 0)
    dir.writeUInt8(entry.size === 256 ? 0 : entry.size, base + 1)
    dir.writeUInt8(0, base + 2) // palette colours
    dir.writeUInt8(0, base + 3) // reserved
    dir.writeUInt16LE(1, base + 4) // colour planes
    dir.writeUInt16LE(32, base + 6) // bits per pixel
    dir.writeUInt32LE(entry.png.length, base + 8)
    dir.writeUInt32LE(offset, base + 12)
    offset += entry.png.length
  })

  return Buffer.concat([header, dir, ...entries.map((e) => e.png)])
}

function main() {
  const [out, ...inputs] = process.argv.slice(2)
  if (!out || !inputs.length) {
    console.error('usage: node scripts/ico-writer.ts out.ico 16.png 32.png 48.png')
    process.exit(2)
  }
  const entries = inputs
    .map((path) => {
      const png = readFileSync(path)
      return { size: pngSize(png), png }
    })
    .sort((a, b) => a.size - b.size)

  const ico = writeIco(entries)
  writeFileSync(out, ico)
  console.log(`wrote ${out}: ${entries.map((e) => `${e.size}px`).join(', ')} — ${ico.length} bytes`)
  console.log('ship the same bytes at /favicon.ico and /icons/favicon.ico')
}

if (process.argv[1]?.endsWith('ico-writer.ts')) main()
