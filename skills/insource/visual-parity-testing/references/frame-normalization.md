# Frame Normalization: Coordinate Alignment & Chrome Noise

This is the single most common cause of a *false* low similarity score. A 12px vertical offset from an uncropped status bar, or a scrollbar the mockup capture has and the device capture doesn't, can collapse a similarity score from 90% to 40% on a screen that is actually visually correct. Get this right before trusting any comparison number — chasing a "layout bug" that's actually a cropping bug wastes an entire loop run.

## Table of contents
1. Why mockup and device captures are never naturally aligned
2. Chrome/frame noise sources, per side
3. The normalization procedure
4. Verifying normalization before trusting the first real score

---

## 1. Why mockup and device captures are never naturally aligned

A browser rendering a mobile-viewport mockup and a real device rendering the actual app almost never produce pixel-aligned output by default, for reasons that have nothing to do with the app's actual layout:
- The device has OS-level chrome (a status bar showing time/battery/signal) that a plain browser viewport capture doesn't render at all.
- The browser may have its own chrome noise: a scrollbar (especially on desktop-browser mobile-emulation modes), an address bar or mobile-emulation frame decoration if the capture wasn't taken from a truly clean headless viewport.
- Device pixel ratio / capture scale can differ even when both sides were configured to "match," due to rounding or OS-level scaling.

None of this reflects a real difference in the *app's* UI — but if left uncropped, all of it shows up as noise in every single comparison, uniformly lowering every score in a way that's easy to misattribute to real layout bugs.

## 2. Chrome/frame noise sources, per side — audit both independently

Don't assume the two sides need the same crop amount; they usually don't, because the noise sources are different on each side:

**Mockup/browser side**:
- Scrollbar (if the mockup content is taller than the viewport and the browser renders a visible scrollbar — common on desktop headless captures even at a "mobile" viewport width). A real mobile device's native scrollbar (if any) looks and behaves completely differently, so a visible desktop-style scrollbar in the mockup capture is pure noise, not a real difference.
- No status bar at all, by default — most headless browser captures don't render a synthetic OS status bar unless you explicitly add one to the mockup for capture purposes.
- Any dev-tool/emulation-mode frame decoration if the capture tool's mobile-emulation mode wasn't configured for a truly clean, chrome-free viewport screenshot.

**Device/emulator side**:
- The native status bar (time, battery, signal, notification icons) — present on essentially every real device/emulator capture, absent from the plain mockup capture.
- Navigation chrome (a bottom gesture bar, on-screen back/home/recents buttons on Android) if the capture includes the full screen rather than just the app's content area.
- Safe-area insets (notches, rounded corners, dynamic island) that eat into the very top/bottom of the frame in ways the mockup has no equivalent for.

## 3. The normalization procedure

1. **Don't hardcode a fixed pixel crop offset.** Device screen sizes, status bar heights, and browser chrome all vary across OS versions and device models — a crop amount tuned for one emulator will silently be wrong for the next device tested. Instead, locate a **stable UI landmark** on each side independently (e.g., the top edge of the app's own header/nav bar, the bottom edge of the app's own tab bar) and crop relative to that landmark, not relative to an assumed fixed offset from the image edge.
2. Crop the mockup capture to just its content area (remove any scrollbar strip, any browser chrome).
3. Crop the device capture to just the app's own rendered content (remove the OS status bar, remove OS-level navigation chrome, respect safe-area insets).
4. Resize/align both crops to a common coordinate space (matching width, and matching aspect ratio if height differs meaningfully — investigate rather than silently stretching, since a real aspect-ratio mismatch might itself be a genuine layout bug worth flagging, not just something to paper over).
5. Only after this alignment step should the comparison suite (`pipeline.md` §4) run.

## 4. Verifying normalization before trusting the first real score

Before starting the main convergence loop, sanity-check normalization on at least one known-good screen (one you can visually confirm looks right side-by-side):
- If the similarity score still comes back surprisingly low despite the screen visually looking correct, suspect normalization first, not the app's code — re-check the landmark-based crop on both sides before spending a single loop iteration "fixing" what might be a cropping bug.
- Once normalization is verified correct on one screen, it generally holds for the rest of the same app/device pair — but re-verify if the target device/emulator changes, since status bar height and chrome dimensions can differ across devices.
