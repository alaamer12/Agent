# Image revocation - redacting what is visible, not just what is written

An image is a first-class artifact of this skill, not only a leak surface: screenshots, chat exports,
mockups, photos and scans carry names, faces, avatars, handles, addresses and endpoints *as pixels*, and a
substitution map over the text version of them revokes nothing. This file covers revoking the pixels.

## Step 0 still runs

The destination still sets the budget (public post vs internal wiki vs third-party tool), because it decides
which treatments are sufficient below. With no region list given (`/revoke image` on a bare screenshot), the
default is the document default: **revoke everything that identifies, the same inventory pass as prose** -
the agent looks, enumerates, decides, and says what it found before it paints. Ask once about anything whose
visibility decision is genuinely ambiguous, then proceed.

## Inventory: what identifies in a picture

Read the image the way Step 1 reads a document, region by region, corner to corner - title bars, tab strips,
sidebars, status dots, timestamps in the chrome, watermarks, and the *edges of the frame* where half a name
often survives:

- **Name labels and handles** next to messages, profile cards, @mentions, "Replying to ..." chips.
- **Avatars and faces** - the strongest identifiers in the file: a visible face or profile picture is
  reverse-image-searchable and matchable even when every letter of the name is gone.
- **In-image text**: message bodies, terminal prompts and paths, browser address bars, email headers,
  phone numbers, order ids, anything an OCR pass would read back out.
- **Branding and shape**: logos, product-specific color systems, dashboard layouts unique to your company,
  a workspace's tile arrangement - combinatorial identity lives in pixels too.
- **The metadata behind the pixels** (see below), which is the same surface Step 4 already checks, now part
  of the deliverable's making rather than an afterthought.

Each region gets one of the five operations, translated into pixels:

| Operation | Pixel form | Guarantees |
|---|---|---|
| [redact] | **opaque solid block**, painted over the region and flattened | irreversible, the default |
| [pseudonymize] | replace avatar with a generic silhouette; replace a face crop with a neutral placeholder | keeps "there is a person here, a different one" |
| [generalize] | heavy downscale-mosaic coarse enough that no feature survives | shape of the layout, no content |
| weak cover | **blur** | *not a redaction* - see below |

## Block, pixelate, blur - in that honest order

- **Solid block is the standard.** Opaque, flattened into the pixel data, re-encoded. It is the only
  treatment that survives every recovery trick below.
- **Pixelate / downscale-mosaic is a redaction only when the grid is coarser than the feature it hides.**
  Text pixelated at fine grids has been reconstructed by published attacks (a known alphabet plus a known
  layout narrows each block to one glyph); if you would accept the image publicly, block instead.
- **Blur is decoration, not revocation.** Gaussian/box blur of text and faces is invertible with
  deconvolution and learned reconstruction, and a blurred face remains matchable by embedding models even
  when a human cannot read it. Blur belongs on the "lowered recognizability, stated as such" side of the
  record, never on the "revoked" side. If the user asks for blur over what must be gone, say so plainly and
  offer the block.
- **Never fake it with layers.** A rectangle drawn with any alpha < 1.0, a highlight shape on top, a
  vector overlay inside a PDF or SVG export - all recover by flattening, removing the layer, or reading the
  original pixels beneath. The pixels themselves must change, and the file must be re-encoded from the
  changed raster, not copied.
- **Cover generously.** Anti-aliasing halos, descenders and ascenders outside the tight glyph box still
  read: pad every text region on all sides, and check neighboring lines the treatment did not intend to
  touch but now partially hides (half a blocked name is a hint, which is what 07 is about in the *wrong*
  context).

## The image-specific trap list

Things that make a *visually* clean redaction a leak:

- **Embedded thumbnails** - EXIF thumbnails in JPEGs and preview strips in PNG chunks often contain the
  *original*, unredacted raster. Strip or regenerate all embedded images, do not copy them through.
- **Multi-frame and multi-size formats** - GIF/animated WebP/AVIF have every frame as a full image; ICO
  and icon sets carry several sizes of the same picture; a TIFF can be a page stack. One frame redacted is
  zero frames revoked. Enumerate frames/sizes in the inventory or flatten to a single frame deliberately,
  and say which you chose.
- **Metadata** - EXIF/XMP/PNG tEXt-iTXt-zTXt chunks: author, GPS, device owner, software strings that name
  a person or company, and ICC profile descriptions. Strip on write; re-encoding usually drops most chunks
  but *not all formats by default* - verify with `exiftool`/`identify -verbose` or the tool's own dump
  rather than trusting the encoder.
- **The crop** - a screenshot cropped next to the name instead of over it still contains the name's first
  letter, the tail of the email, the chat bubble pointing at it. Cropping is not a redaction technique.
- **Audio/video same laws** - burn-in captions follow the block rule; spoken names follow the [redact] rule
  (which usually means re-recording or muting the span - a ducked tone over a spoken name is still the
  spoken name at low volume).

## Tools: pick what fits, prove it on a temp file

The method is tool-neutral, and the environment is the arbiter of what applies:

- **Look first.** A purpose-built tool in front of you beats a hand-rolled pass: image editors with
  scripting, `magick` (ImageMagick), `ffmpeg` for frames and video, OCR suites for the verification sweep,
  `exiftool` for the metadata check, and Python `Pillow`/`numpy` where available. If the obvious one is not
  installed, the same bootstrap discipline as everywhere else in these skills applies - check the current
  landscape rather than trusting memory of names, and prefer what this machine already has.
- **A local env, never the global interpreter**: if the chosen tool is a Python library, install into a
  project-local `.venv` and run from it; no global `pip install`.
- **If this skill's `scripts/revoke_image.py` is present and Pillow is reachable, it is the default
  mechanics**: it paints blocks/mosaic/blur from a region spec, strips metadata, flattens and re-encodes,
  and refuses to touch the original. It takes coordinates and choices as input - *which* regions and *which*
  treatments is the judgment above, which stays with the agent. Other tools may do the same job; what is
  non-negotiable is the loop below, not the library.
- **Temp files before final, always** - the discipline the user asked the skill to be smart enough to
  enforce: render to a scratch copy → *look at the result* (re-open it, zoom the treated regions and their
  neighbors; this agent has eyes, use them) → run the checks (metadata dump empty? every inventory row
  covered? no halo text readable? OCR sweep of the output finds none of the inventoried strings?) → fix the
  spec, re-render → and only after the temp passes, produce the final file and re-run the checks on *it*.
  A final image produced without a looked-at predecessor is a leak with a filename.

## Verification closes the loop, then the record

- Re-read the finished image cold: inventory every identification region you listed, and confirm each is
  *gone*, not softened. Run the metadata check on the final path, and the frame/size/thumbnail enumeration
  again - the output side this time.
- `revoke.py scan` over any accompanying text (captions, alt text, filenames of the output!) catches the
  word-level survivors that sit next to the fixed pixels - a perfect redacted screenshot named
  `marta-review-approval.png` has revoked nothing about Marta.
- Record: regions, treatments, tool used, and the stated residual risk for anything weaker than a block -
  exactly the honesty discipline the parent skill already runs, with "blur applied" written as what it is:
  lowered recognizability, not revocation.
