# Springs

> **Connections** (paths are relative to `references/`)
> - Read when: physics, bounce, momentum, interruption, gestures, 'feels alive', layout animation.
> - Skip when: plain fade or ease motion with no physics.
> - Read next: `gestures.md` (for drag and release); `stacks/react-motion.md` (for the web API); `stacks/react-native.md` (for the native API).

Physics-based motion. Use when motion should feel alive, respond to gestures, or be interrupted gracefully. Keep CSS easing for simple, predetermined motion.

## Contents
- When to use springs
- Two ways to describe a spring
- Presets
- Bounce rules
- Interruption and velocity
- Asymmetric open and close
- Pitfalls

## When to use springs

- Drag and flick with momentum.
- Elements that should feel alive (a badge settling, a drawer with weight).
- Anything frequently interrupted, since springs retarget with velocity instead of restarting.
- Layout animations and shared elements where a fixed duration feels mechanical.

Keep duration-based easing for predetermined sequences, opacity fades, color changes and anything measured against a clock.

## Two ways to describe a spring

| Style | Parameters | Good for |
|---|---|---|
| Perceptual | `duration` (how long it feels finished) and `bounce` (0 to 1) | Design-led tuning; easy to reason about |
| Physical | `stiffness`, `damping`, `mass` | Matching a native platform or a fixed physical feel |

Higher stiffness is snappier; lower damping means more bounce; higher mass feels heavier. Perceptual duration is how long it feels done, while micro-settling continues after.

## Presets

| Name | Values | Use |
|---|---|---|
| snappy | stiffness 500, damping 40 | Fast UI response |
| gentle | stiffness 200, damping 30 | Smooth, low energy |
| stiff | stiffness 700, damping 50 | Immediate, controls |
| bouncy | stiffness 300, damping 20 | Playful moments, rare tier |
| perceptual | duration 0.4, bounce 0 | Default for most UI springs |
| perceptual with momentum | duration 0.4, bounce 0.2 | After a flick or drag release |

## Bounce rules

- Bounce only when the user imparts momentum (a flick, a drag release) or the moment is rare and playful. A spring that overshoots on a routine dropdown feels sloppy.
- Overshoot of about 2 to 8% is plenty. More reads as cartoon.
- Utility and productivity tools use zero or minimal bounce; consumer and playful products can go further.
- Do not combine heavy bounce with a long duration: the settle drags.

## Interruption and velocity

A spring carries its current velocity into the next target. Redirect mid-flight (close while opening) and the motion reverses naturally. This is why springs suit gesture and toggles. When a gesture ends, pass the release velocity into the spring.

## Asymmetric open and close

Opening can overshoot slightly (an energetic arrival) while closing uses a clean critically damped spring or ease-out (a quiet departure). In CSS, a sampled spring curve can serve the opening side:

```css
.surface { transition: transform 420ms linear(0, 0.45, 0.78, 1, 1.17, 1.21, 1.18, 1.12, 1.05, 1.02, 1); }
.surface[data-closing] { transition-duration: 220ms; transition-timing-function: cubic-bezier(0.32, 0.72, 0, 1); }
```

## Pitfalls

- Using a spring where the exact duration must match another animation.
- Bounce on frequent or serious UI.
- Springs driving layout properties instead of transforms.
- Forgetting the reduced-motion variant: replace the spring with a short fade.
- Running spring physics on the main thread while the page is busy; when the motion must survive load, prefer CSS or WAAPI with a sampled curve.
