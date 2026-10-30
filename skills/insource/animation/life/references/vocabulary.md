# Vocabulary

> **Connections** (paths are relative to `references/`)
> - Read when: you must name an effect, or turn a description ('slides off', 'draws itself') into a precise term.
> - Skip when: the terms are already unambiguous.
> - Read next: `intent-resolution.md` (to turn the term into classification values and a route).

Reverse-lookup glossary: description to precise term. Use the wording below as written when answering a naming question, and lead with the term. Terms marked (Animate) are this skill's own additions.

## Contents
- Entrances and exits
- Sequencing and timing
- Movement and transforms
- Transitions between states
- Scroll
- Feedback and interaction
- Easing
- Springs
- Looping and ambient motion
- Polish and effects
- Performance
- Principles
- Synchronization (Animate)

## Entrances and exits
- **Fade in / Fade out**: element appears or disappears by changing opacity.
- **Slide in**: element enters by sliding in from off-screen (left, right, top, or bottom).
- **Scale in**: element grows from smaller to full size as it appears, often paired with a fade.
- **Pop in**: element appears with a slight overshoot, like it bounces into place.
- **Reveal**: content is uncovered gradually, often by animating a clip-path or mask.
- **Enter / Exit**: the animation an element plays when it is added to or removed from the screen.

## Sequencing and timing
- **Keyframes**: defined points in an animation (0%, 50%, 100%) that the browser fills the gaps between.
- **Interpolation / Tween**: generating all the in-between frames between a start and end value.
- **Stagger**: animating several items one after another with a small delay between each, creating a cascade.
- **Orchestration**: deliberately timing multiple animations so they feel like one coordinated motion.
- **Delay**: time before an animation starts.
- **Duration**: how long an animation takes.
- **Fill mode**: whether an element keeps its first or last frame's styles before the animation starts or after it ends.
- **Stepped animation**: an animation divided into discrete steps, like a countdown timer.

## Movement and transforms
- **Translate**: move an element along the X or Y axis.
- **Scale**: make an element bigger or smaller.
- **Rotate**: spin an element around a point.
- **Skew**: slant an element along the X or Y axis, shearing it out of its rectangular shape.
- **3D tilt / Flip**: rotate in 3D space (rotateX / rotateY) to add depth.
- **Perspective**: how strong the 3D effect looks; a lower value exaggerates depth.
- **Transform origin**: the anchor point a scale or rotation grows or spins from.
- **Origin-aware animation**: an element animates out of its trigger, like a popover growing from the button that opened it instead of from its own center.

## Transitions between states
- **Crossfade**: one element fades out as another fades in, in the same spot.
- **Continuity transition**: a change that keeps the user oriented by visually connecting before and after.
- **Morph**: one shape smoothly turns into another shape.
- **Container morph**: a trigger grows in place into the surface it summons, so the button becomes the search field or form.
- **Shared element transition**: an element travels and transforms from one position into another, like a thumbnail expanding into a card.
- **Layout animation**: when an element's size or position changes, it animates to the new spot instead of snapping.
- **Accordion / Collapse**: a section expands and collapses to show or hide content.
- **Direction-aware transition**: content slides one way going forward and the opposite way going back.

## Scroll
- **Scroll reveal**: elements fade or slide into place as they enter the viewport.
- **Scroll-driven animation**: an animation whose progress is tied directly to scroll position.
- **Parallax**: background and foreground move at different speeds while scrolling, creating depth.
- **Page transition**: an animation that plays when navigating from one page or route to another.
- **View transition**: the browser morphs between two states or pages, connecting shared elements.

## Feedback and interaction
- **Hover effect**: visual change when the cursor moves over an element.
- **Press / Tap feedback**: a subtle scale-down when an element is clicked, so it feels physical.
- **Hold to confirm**: a progress effect that fills up while the user holds a button.
- **Drag**: moving an element by grabbing it, often with momentum when released.
- **Drag to reorder**: dragging items in a list to rearrange them while the others shift to make room.
- **Swipe to dismiss**: dragging an element off-screen to close it.
- **Rubber-banding**: resistance and snap-back when you drag past a boundary.
- **Detent**: a discrete stop a control settles onto when released, like notches on a ruler picker.
- **Peripheral de-emphasis**: blurring and fading everything around the focused item instead of dimming the whole page.
- **Shake / Wiggle**: a quick side-to-side jitter signaling an error or rejected input.
- **Ripple**: a circle expanding from the point of a tap, confirming the press.

## Easing
- **Easing**: the rate at which an animation speeds up or slows down.
- **Ease-out**: starts fast, ends slow; the default for most UI and anything responding to the user.
- **Ease-in**: starts slow, ends fast; usually avoided because it feels sluggish.
- **Ease-in-out**: slow, fast, slow; good for elements already on screen moving from A to B.
- **Linear**: constant speed; reserve for spinners, marquees and scroll-scrubbed motion.
- **Cubic-bezier**: a custom easing curve you define for precise control.
- **Asymmetric easing**: a curve that accelerates and decelerates at different rates; feels more alive than a symmetric one.

## Springs
- **Spring**: motion driven by physics (tension, mass, damping) rather than a set duration.
- **Stiffness / Tension**: how strongly the spring pulls toward its target; higher feels snappier.
- **Damping**: how quickly a spring settles; lower damping means more bounce.
- **Mass**: how heavy the animated element feels.
- **Bounce**: a spring that overshoots and settles, adding playfulness.
- **Perceptual duration**: how long a spring feels finished, even though it keeps micro-settling.
- **Momentum**: motion that carries velocity, especially after a drag or interruption.
- **Velocity**: how fast and in which direction an element is moving; a spring carries it into the next animation when interrupted.
- **Interruptible animation**: an animation that can be smoothly redirected mid-flight instead of finishing first.

## Looping and ambient motion
- **Marquee**: text or content that scrolls continuously in a loop.
- **Loop**: an animation that repeats a set number of times or forever.
- **Alternate (yoyo)**: a loop that plays forward then reverses each iteration.
- **Orbit**: an element circling around another in a continuous path.
- **Pulse**: a gentle repeating scale or opacity change to draw attention.
- **Float**: a gentle, continuous up-and-down drift that makes a static element feel alive.
- **Idle animation**: subtle motion that plays while an element is waiting to be interacted with.

## Polish and effects
- **Blur**: a blur filter used to soften an element or hide tiny imperfections.
- **Clip-path**: clipping an element to a shape, used for reveals, masks and before/after sliders.
- **Mask**: hiding or revealing parts of an element with a shape or gradient, with soft, fadeable edges.
- **Before / after slider**: a draggable divider that wipes between two overlaid images.
- **Line drawing**: an SVG path that draws itself in, like an invisible pen tracing it.
- **Text morph**: text that animates character by character when it changes.
- **Skeleton / Shimmer**: a placeholder with a moving sheen shown while content loads.
- **Number ticker**: digits rolling or counting up to a value.
- **Odometer roll**: digits rolling vertically in the direction the value moved.
- **Tabular numbers**: fixed-width digits so numbers do not shift as they change.
- **Typewriter**: text appearing one character at a time.

## Performance
- **Frame rate (FPS)**: frames drawn per second; 60 is the baseline for smooth motion.
- **Jank**: visible stutter when the browser drops frames.
- **Dropped frame**: a frame the browser missed its deadline to draw.
- **Compositing**: letting the GPU move or fade an element on its own layer without redoing layout or paint.
- **will-change**: a CSS hint that an element is about to animate.
- **Layout thrashing**: animating width, height, top or left, forcing layout recalculation every frame.

## Principles
- **Purposeful animation**: motion should serve a function, not just decorate.
- **Anticipation**: a small wind-up in the opposite direction before a move.
- **Follow-through**: parts keep moving and settle slightly after the main motion stops.
- **Squash and stretch**: deforming an element as it moves to convey weight, speed and flexibility.
- **Perceived performance**: the right animation makes an interface feel faster than it is.
- **Frequency of use**: the more often users see an animation, the shorter and subtler it should be.
- **Spatial consistency**: keeping an element's identity and position across states so users never lose track of it.
- **Hardware acceleration**: animating transform and opacity lets the GPU keep motion smooth.
- **Reduced motion**: respecting the user's reduced-motion setting by toning down or removing movement.

## Synchronization (Animate)
- **Instant synchronous**: several animations share the same start and end timing, even if their techniques differ.
- **Domino / sequential**: animations follow one another in order, each depending on or handing off to the previous.
- **Linked**: an action or animation on one element causes a corresponding effect on elements related to it.
