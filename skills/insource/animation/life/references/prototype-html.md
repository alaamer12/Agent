# HTML prototype

> Owner of the when-to-escalate criteria and of the live demo contract. Routing lives in ../SKILL.md.

A live, runnable preview of an option, used when ASCII cannot convey the effect. It lets the user see the animation before it is implemented in production code.

## When to escalate

Escalate for effects that depend on things ASCII cannot show:
- light, reflection, sheen, glass or gradient response
- depth, perspective, 3D, parallax
- blur, glow, shadow changes
- continuous or physics curves where the feel depends on the curve itself
- pointer response, drag, hover tracking
- color transitions and per-character typography

If an option is clear from ASCII, keep ASCII. Do not build live prototypes by default.

## Asking the user

The stop point itself is owned by run-procedure.md (phase 4, stop points). Prototype-specific details: mixed files are fine — ASCII for options that read well, live demos for the rest. If the user keeps ASCII, still describe the unreadable aspects in the option's `feel` and `risk` fields.

## The demo contract

Each `demo_html` value is a self-contained fragment that is mounted in a sandboxed frame:

- Everything inline: one `<style>`, one `<script>`, markup. No external scripts, fonts, images or network requests.
- A single root element with `id="stage"` that holds the demo.
- A global `play()` that (re)starts the forward animation. For pairs, a global `reverse()` runs the reverse. If `play` is missing, the frame is simply reloaded.
- It uses the same duration and easing numbers as the spec. Do not tune them differently in the demo.
- It honors the reduced-motion preference by switching to the option's `reduced_motion` behavior.
- It animates only transform, opacity and bounded filter, like the production code will.
- It keeps visible focus states for any interactive part and works at 390px to 1440px wide.
- It stops continuous work once the animation settles.

## Writing demo_html

```html
<style>
  #stage { display:grid; place-items:center; min-height:200px; }
  .btn { padding:12px 20px; border-radius:10px; border:0; background:#222; color:#fff; position:relative; overflow:hidden; }
  .btn::after { content:""; position:absolute; inset:0; transform:translateX(-120%);
    background:linear-gradient(100deg, transparent 30%, rgba(255,255,255,.35) 50%, transparent 70%); }
  .btn.go::after { transition: transform 600ms cubic-bezier(0.22, 1, 0.36, 1); transform:translateX(120%); }
  @media (prefers-reduced-motion: reduce) { .btn.go::after { transition:none; transform:none; opacity:0; } }
</style>
<div id="stage"><button class="btn" id="b">Pay now</button></div>
<script>
  const b = document.getElementById('b');
  window.play = () => { b.classList.remove('go'); void b.offsetWidth; b.classList.add('go'); };
  b.addEventListener('pointerenter', window.play);
</script>
```

Prefer CSS transitions, CSS animations and the Web Animations API: the preview's speed control works on those. Animations driven only by timers or a canvas loop cannot be slowed by the preview and should expose their own slow-motion switch.

## What the builder adds

`scripts/build_prototype.py` mounts each demo in a sandboxed frame and adds: a Replay button, a Reverse button when the option has a reverse sequence, a speed control (1x, 0.5x, 0.25x) that slows every document animation inside the frame, the ASCII frames and lanes for the same option (when present), and a note on reduced-motion behavior.

## Fidelity rules

- The demo is a preview of the chosen values, not a different design. If the user picks the option, the production build must match the demo's numbers.
- Dependency and prototype-location rules: run-procedure.md (phase 5).

## Fallback

If scripts cannot run, write a single HTML file with one section per option, the demo inline, a Replay button and a speed selector that sets the playback rate on `document.getAnimations()`.
