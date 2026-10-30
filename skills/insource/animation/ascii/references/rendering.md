# ASCII Rendering Reference

> Detailed ramp tables, sampling math, renderers, and motion-pattern sketches for the `ascii` skill.
> Start from the skill overview in [`../SKILL.md`](../SKILL.md); load this file when you need full tables, ANSI helpers, or motion recipes.

## Brightness ramp tables

Order is **dark → light**. Index with `Math.round(lum * (ramp.length - 1))` where `lum` is 0..1.

### 10-level (compact, generative)
```
 .:-=+*#%@
```
Distinct steps, low banding. Best for low-resolution generative fields and terminals.

### 70-level Paul Bourke (photo fidelity)
```
$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. 
```
This string is ordered **light → dark** (densest first). Either reverse it or use `index = Math.round((1 - lum) * (len - 1))`. Best for grayscale photos; trailing space = empty/black.

### 16-level extended (balance)
```
 .'`,^:";~-_+<>i!lI?/\|()1{}[]rcvunxzjftLCJUYXZO0Qoahkbdpqwm*WMB8&%$#@
```
For UI/loaders a hand-picked 8–12 char ramp usually looks cleaner than 70 levels.

### Block / shade characters (Unicode)
```
 ░▒▓█
```
Or vertical fills `▁▂▃▄▅▆▇█`. Near-continuous gradient in monospace fonts that include box-drawing glyphs. Excellent for meters, waveforms, and smooth fades.

## Luminance

Perceptual (recommended):
```js
const lum = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;
```
Fast average (stylized):
```js
const lum = (r + g + b) / (3 * 255);
```
Invert for dark-on-light: `lum = 1 - lum`. Gamma to spread midtones: `lum = Math.pow(lum, 0.8)`.

## Pixel sampling and cell aspect

Monospace cells are about twice as tall as wide. Measure when precision matters:

```js
function measureCellAspect(fontFamily = 'monospace', fontPx = 16) {
  const cv = document.createElement('canvas');
  const ctx = cv.getContext('2d');
  ctx.font = `${fontPx}px ${fontFamily}`;
  const w = ctx.measureText('M').width;
  const h = fontPx; // line-height: 1
  return w / h;     // ~0.5 for most fonts
}
```

Grid size for a source image:
```js
function gridSize(imgW, imgH, cols, cellAspect = 0.5) {
  const rows = Math.round(cols * (imgH / imgW) * cellAspect);
  return { cols, rows };
}
```

Draw the source into an offscreen canvas at exactly `cols × rows`, then one `getImageData(0, 0, cols, rows)` per frame.

## `<pre>` vs canvas

| Aspect | `pre` + textContent | Canvas `fillText` |
|--------|---------------------|-------------------|
| Setup | one string | per-cell draw loop |
| Color | single color (or slow spans) | per-char color cheap |
| Max size | ~120×60 @ 30 fps | thousands of cells @ 60 fps |
| Selectable text | yes | no |
| Best for | generative fields, loaders | video, per-char color, large grids |

```css
pre {
  font-family: ui-monospace, monospace;
  line-height: 1;
  letter-spacing: 0;
  margin: 0;
  white-space: pre;
}
```

Canvas per-char color:
```js
function drawAsciiCanvas(ctx, chars, colors, cols, rows, cellW, cellH) {
  ctx.clearRect(0, 0, cols * cellW, rows * cellH);
  ctx.textBaseline = 'top';
  ctx.font = `${cellH}px monospace`;
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      const i = y * cols + x;
      ctx.fillStyle = colors[i];
      ctx.fillText(chars[i], x * cellW, y * cellH);
    }
  }
}
```

## ANSI terminal frame loop (Node / Bun)

```js
const ESC = '\x1b[';
const out = process.stdout;

function start(render, fps = 20) {
  out.write(ESC + '?25l');               // hide cursor
  out.write(ESC + '2J');                 // clear once
  const interval = 1000 / fps;
  let t0 = Date.now();
  const id = setInterval(() => {
    const t = Date.now() - t0;
    out.write(ESC + 'H');                // home (no full clear → less flicker)
    out.write(render(t, out.columns || 80, out.rows || 24));
  }, interval);
  const stop = () => {
    clearInterval(id);
    out.write(ESC + '0m' + ESC + '?25h' + ESC + '2J' + ESC + 'H');
    process.exit(0);
  };
  process.on('SIGINT', stop);
  return stop;
}

function colored(ch, r, g, b) {
  return `${ESC}38;2;${r};${g};${b}m${ch}${ESC}0m`;
}

// Example plasma
start((t, cols, rows) => {
  const ramp = ' .:-=+*#%@';
  let s = '';
  for (let y = 0; y < rows - 1; y++) {
    for (let x = 0; x < cols; x++) {
      const v =
        Math.sin(x * 0.15 + t * 0.001) +
        Math.sin(y * 0.25 + t * 0.0015) +
        Math.sin((x + y) * 0.1 + t * 0.0008);
      const lum = (v + 3) / 6;
      s += ramp[Math.round(lum * (ramp.length - 1))];
    }
    s += '\n';
  }
  return s;
});
```

Recompute grid on `process.stdout.on('resize', ...)`. Avoid a trailing newline on the last row or the terminal scrolls.

## Three.js AsciiEffect — complete wiring

```js
import * as THREE from 'three';
import { AsciiEffect } from 'three/addons/effects/AsciiEffect.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const renderer = new THREE.WebGLRenderer();
renderer.setSize(innerWidth, innerHeight);

const effect = new AsciiEffect(renderer, ' .:-=+*#%@', { invert: true, resolution: 0.2 });
effect.setSize(innerWidth, innerHeight);
effect.domElement.style.color = 'white';
effect.domElement.style.backgroundColor = 'black';
document.body.appendChild(effect.domElement);   // effect DOM, not renderer.domElement

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(70, innerWidth / innerHeight, 1, 1000);
camera.position.z = 4;
scene.add(new THREE.PointLight(0xffffff, 3).position.set(5, 5, 5));
scene.add(new THREE.AmbientLight(0x808080));
const mesh = new THREE.Mesh(
  new THREE.TorusKnotGeometry(1, 0.3, 100, 16),
  new THREE.MeshStandardMaterial({ flatShading: true })
);
scene.add(mesh);

const controls = new OrbitControls(camera, effect.domElement);

function animate(t) {
  mesh.rotation.y = t * 0.0005;
  effect.render(scene, camera);                 // through the effect
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  effect.setSize(innerWidth, innerHeight);
});
```

Gotchas: append `effect.domElement`, call `effect.render`, strong lighting + `flatShading` for crisp edges. `resolution` (default ~0.15) controls density.

## Motion-pattern sketches

Use only when the chosen kind benefits. All patterns assume a pre-computed mask (0/1 or density) or a full generative field.

### Diagonal / left-to-right wave (domino cascade)

```js
function waveFrame(t, cols, rows, mask, ramp, totalMs = 2000) {
  let out = '';
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      if (!mask[y * cols + x]) { out += ' '; continue; }
      const delay = ((x / cols) + (y / rows)) * 0.5 * totalMs;
      const local = Math.max(0, t - delay);
      const lum = local === 0 ? 0 : Math.min(1, local / 300); // fade in
      out += ramp[Math.round(lum * (ramp.length - 1))];
    }
    out += '\n';
  }
  return out;
}
```

Radial version: `delay = Math.hypot(x - cx, y - cy) / maxR * totalMs`.

### Per-character pulse inside a fixed shape

```js
function pulseFrame(t, cols, rows, mask, ramp) {
  let out = '';
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < cols; x++) {
      if (!mask[y * cols + x]) { out += ' '; continue; }
      const phase = (x + y) * 0.35 + t * 0.004;
      const lum = 0.5 + 0.5 * Math.sin(phase);
      out += ramp[Math.round(lum * (ramp.length - 1))];
    }
    out += '\n';
  }
  return out;
}
```

### Gradient color (canvas or ANSI)

Luminance still chooses the glyph; color is independent:

```js
// canvas
ctx.fillStyle = `rgb(${r},${g},${b})`;
ctx.fillText(ch, x * cellW, y * cellH);

// ANSI truecolor
s += `\x1b[38;2;${r};${g};${b}m${ch}\x1b[0m`;
```

### Mask density + second image as color

Sample image A for luminance → glyph; sample image B at the same `(x, y)` for RGB. Both images are drawn to the same `cols × rows` offscreen canvas first.

### Interactive falloff

```js
const dx = x - pointer.x * cols;
const dy = y - pointer.y * rows;
const dist = Math.hypot(dx, dy);
const falloff = Math.max(0, 1 - dist / radius);
const lum = baseLum * falloff;
```

Keep the frame function pure in `(t, inputState)` so `?t=N` remains deterministic.

## Image pipeline note (Bun.Image vs sharp)

- **Bun ≥ 1.3.14** ships `Bun.Image` — zero-dep, sharp-style chain for metadata, resize, rotate, modulate, and encode (JPEG/PNG/WebP; HEIC/AVIF on macOS/Windows). Prefer it for any new resize/encode work.
- **Raw RGB for luminance sampling** still requires `sharp` (or a canvas/`getImageData` path in the browser). The CLI script therefore depends on sharp even under Bun; use `Bun.Image` everywhere else you only need geometry or format conversion.

```js
// Preferred for resize-only / encode (Bun)
await Bun.file('photo.jpg').image().resize(cols, rows, { fit: 'fill' }).png().write('out.png');

// Needed for raw pixels (CLI luminance)
const { data } = await sharp(file).resize(cols, rows).removeAlpha().raw().toBuffer({ resolveWithObject: true });
```
