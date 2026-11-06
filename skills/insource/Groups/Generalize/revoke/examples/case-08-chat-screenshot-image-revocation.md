# Case 8 - the chat screenshot: avatar, name, and the corner that leaked

**Artifact:** a messenger screenshot (RTL Arabic chat) for a public write-up: the conversation's substance
must survive, the counterpart must not be identifiable.
**Destination:** public. Level 3. `/revoke image` with no region list - so the default ran: inventory
everything visible, the document way ([`08`](../references/08-image-redaction.md)).

## The inventory (what the looking pass found)

```text
top bar          circular photo avatar (a real face - the strongest identifier in the file)
                 contact name beside it: a title + a very common given name
quoted reply     the SAME name again, inside a green reply-quote bubble lower in the thread - the pass
                 people miss: they revoke the header and leave the quote
"أنت" labels     "You" bubbles - generic role words, KEPT (they identify no one)
timestamps, 13:32 etc. - ordinary chat chrome, kept
metadata         exif/ICC/text chunks: clean; one frame; no embedded thumbnail
```

Two name regions, one face. The title word ("professor/mister") carries no identity; the given name does -
which shaped the partial variants below.

## The four renders, because the user asked to see both techniques and both modes

```text
normal + block   opaque blocks over avatar + both name labels. The deliverable.
normal + blur    radius 12-16 gaussian over the same regions. Record says: "lowered recognizability,
                 NOT revocation" - the blur is deconvolvable and the blurred face is still matchable by
                 embedding models. Shipped only as the demo the user asked for, never as the public file.
partial + block  the face blocked, the avatar's ring/background kept; each label's given-name half masked,
                 title kept: "استاذ م****". Owner-recognizable, stranger-unusable - the 07 rules applied
                 to pixels.
partial + blur   same partial regions, blurred. Weakest of the four; kept in the temp folder as the
                 comparison, not shipped.
```

## The temp-file pass that caught the real leak

The first render used a bounding box measured off the avatar circle. Contact sheet of the result, looked at
it, and found the failure a rectangle makes against a circle: **a white crescent of the original photo
survived at the right edge of the block** - the circular avatar bulged outside the measured box by a few
pixels, and a few pixels of a real face are enough for a match. The fix was the reference's own rule
("cover generously"): widen every region past its visual bounds, re-render, re-look. The second pass was
clean, and `check` on the outputs reported no metadata, no thumbnail, one frame.

Had the final been produced straight from the first spec without looking - which is what "just run the
script" tempts you into - the public file would have shipped with a crescent of someone's face in it. That
is the entire argument for render-to-temp → re-open → zoom the treated regions → then finalize.

## The record

```text
regions: avatar circle (widened past bounds after the crescent finding), header name label, quoted name
label - all three, not just the header.
treatment: opaque block, flattened, re-encoded PNG; blur variants produced for comparison and recorded as
de-identification, not revocation.
kept: "You" role labels, timestamps, chat chrome, conversation text (the point of the artifact).
tool: scripts/revoke_image.py redact --spec, then check; coordinates chosen by looking - the script
applies, the agent decides.
residual risk: none for the blocked file (face pixels gone, not softened); the blur variants retain
matchable structure and were therefore not shipped.
```
