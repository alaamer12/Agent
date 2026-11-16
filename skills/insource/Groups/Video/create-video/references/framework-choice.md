# Choose the framework

Step 0 of the pipeline, worked out: when the `/hyperframes` default is right, and
the three jobs where it costs them something.

`/hyperframes` defaults to HyperFrames unless the user names another framework or
asks only to record a browser session. Keep that default; it is the right answer
for most of what this skill is asked to build. Flag the three cases where the
default costs them something, and hand the decision back:

| The job | A better fit | Why |
|---|---|---|
| Frames come from a live database or per-user data at render scale | Remotion / a code-driven pipeline | parametric rendering is its normal case |
| Concatenating, trimming, or re-muxing existing footage only | `ffmpeg` directly | no composition layer is needed |
| The deliverable must be a live, interactive page | WAAPI / CSS in the app itself | a render is the wrong medium |

Everything else — motion graphics, product and UI stories, typographic beats,
data-viz, composites over footage, decks, captioned clips — stays in HyperFrames
and continues at step 1. State the choice and the reason; never silently switch
frameworks mid-project.
