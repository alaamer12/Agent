# Stack: React Native

> **Connections** (paths are relative to `references/`)
> - Read when: implementing in React Native or Expo.
> - Skip when: the target is web.
> - Read next: `gestures.md` (pan handling); `springs.md` (spring settings).

Notes for React Native animation with Reanimated and the gesture handler. Verify API names and options against the installed versions.

## Contents
- Principles
- Shared values and styles
- Timing and springs
- Layout and presence
- Gestures
- Reduced motion
- Performance

## Principles

The same rules apply: gate by frequency, ease-out for responsive motion, springs for gestures, animate transform and opacity, define reverses, handle interruption. The main difference is that animation should run on the UI thread, not the JavaScript thread.

## Shared values and styles

```tsx
import Animated, { useSharedValue, useAnimatedStyle, withTiming, withSpring, Easing } from "react-native-reanimated";

const scale = useSharedValue(1);
const style = useAnimatedStyle(() => ({ transform: [{ scale: scale.value }] }));
// press
scale.value = withTiming(0.97, { duration: 140, easing: Easing.bezier(0.25, 0.46, 0.45, 0.94) });
```

Keep worklet code small and free of JavaScript-thread dependencies.

## Timing and springs

```tsx
withTiming(1, { duration: 220, easing: Easing.bezier(0.22, 1, 0.36, 1) });
withSpring(0, { stiffness: 500, damping: 40 });                 // physical
withSpring(0, { duration: 400, dampingRatio: 1 });                // perceptual style where supported
```

Pass release velocity into `withSpring` after a gesture via the `velocity` option.

## Layout and presence

Built-in entering, exiting and layout transitions animate mount, unmount and position changes:

```tsx
<Animated.View entering={FadeIn.duration(200)} exiting={FadeOut.duration(150)} layout={LinearTransition} />
```

Use custom entering and exiting only when the defaults are not enough. Exits are shorter than entrances.

## Gestures

```tsx
const pan = Gesture.Pan()
  .onUpdate((e) => { x.value = start.value + e.translationX; })         // locked to the finger
  .onEnd((e) => { x.value = withSpring(target(e), { velocity: e.velocityX }); });
```

Handle cancel and fail states, commit to an axis, keep targets at least 44pt, and provide a non-gesture alternative.

## Reduced motion

Use the library's reduced-motion hook or per-animation reduce setting, and the platform accessibility setting for reduce motion. Replace travel with a short fade; keep user-triggered feedback.

## Performance

- Animate transform and opacity; avoid animating layout properties (width, height, margin) per frame.
- Avoid reading layout on every frame; precompute on the UI thread.
- Use native driver equivalents for platform animation APIs when not using Reanimated.
- Test on a low-end device and with the performance monitor open.
