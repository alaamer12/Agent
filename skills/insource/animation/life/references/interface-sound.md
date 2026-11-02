# Interface sound

> Owner of the optional audio-feedback gate and rules. Routing lives in ../SKILL.md.

Optional audio feedback for interactions. Only when the user asks for sound, or when the product already uses it.

## Gate for sound

Sound is the most intrusive feedback channel. It earns its place only for low-frequency, high-importance moments (a completed payment, a successful send) or in products where audio is part of the experience (games, creative tools, media). Never on frequent actions such as typing, scrolling, hover or navigation.

## Rules

- Off by default unless the product's audience expects it; provide a setting and honor the system mute.
- Short (under about 200ms for feedback), quiet, with soft attack and no harsh high frequencies.
- Pair with visual feedback; sound never carries the only signal.
- Match the visual timing: the sound lands with the peak of the visual (the check completes, the click lands).
- Vary pitch or sample slightly across repeated triggers so it does not fatigue.
- Never autoplay on load. Audio contexts need a prior user gesture to start in most browsers.
- Respect reduced motion as a hint to lower or remove non-essential feedback where the platform exposes a related setting (policy owner: performance-and-accessibility.md).

## Implementation notes

- Preload small samples; reuse one audio context; trigger from the same event handler that starts the animation.
- Cap simultaneous voices; ignore triggers while a sound is still in its attack when rapid input is expected.
- Provide a way to test with sound muted: every state must remain understandable without it.

## Checklist

- [ ] User asked for sound or product already has it
- [ ] Low-frequency, high-importance moments only
- [ ] Settings control and mute respected
- [ ] Visual feedback present regardless
