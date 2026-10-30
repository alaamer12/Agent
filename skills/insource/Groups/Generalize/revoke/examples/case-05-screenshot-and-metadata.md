# Case 5 - the leak that was not in the prose

**Artifact:** a slide deck (PDF) plus one screenshot and a terminal recording, being prepared for an external
meetup talk. Body text had already been sanitized carefully by a human.
**Destination:** public. Level 3.

Everything in this case was found outside the paragraphs, which is the point of
[`03`](../references/03-leak-surfaces.md).

## What the text pass had already handled

Company name, customer logos swapped for `[customer]`, internal service names generalized, the incident date
made relative. `revoke.py verify` on the extracted text: clean.

## What the remaining surfaces held

```text
PDF properties      Author: "Greta Lindqvist"; Company: "Acme Analytics"; title still carried the client name
                   XMP block: creator tool, modification history, and the original file path
                   /Users/greta/Desktop/clientwork/nordbank-q3.pptx
Hyperlinks          31 links: internal wiki, our Grafana dashboards, and two Jira issues whose URL is
                    https://acme.atlassian.net/browse/DATA-1187 - the anchor text said "[internal ticket]",
                    the href said everything
Screenshot          the window title read "nordbank-reconcile.py - Visual Studio Code"; a Slack sidebar with
                    two colleagues' names; the taskbar clock and date
PNG metadata        Software: "Snagit 2024"; Host Application: the .pptx path above
Video               the speaker says the customer name at 6:41, twice
Filenames           nordbank-slides-final.pdf, acme-talk-2025-03.pdf
```

## The repairs, in the order that actually worked

1. **Re-export, don't clean.** A fresh export from the deck's source file with the properties cleared beats
   any post-hoc metadata scrub - and it is verifiable, since you can re-read the properties of the new file.
   Post-hoc scrubbing is unreliable on PDF in particular: incremental saves keep the old objects.
2. **Kill the hrefs, not just the anchor text.** Every link to an internal host removed entirely, replaced by
   the unlinked label `[internal dashboard]`. A dead link still discloses a hostname.
3. **Re-take the screenshot** instead of painting over it: cropped chrome, placeholder window title, no
   sidebar, no clock. Covering pixels leaves the original underneath in some formats, and a painted-over
   rectangle is itself information ("something is hidden here").
4. **Transcribe-then-cut the video.** Two spoken names at 6:41; the audio segment was re-recorded rather than
   muted, because a four-second silence in a live talk reads as a secret.
5. **Rename for the destination.** Filenames are metadata that ships with the file.
6. **Then re-run both checks** on the *new* artifacts - `scan` and `verify` against the extracted text, a
   properties dump, a `strings` pass over the PDF, and a 100%-zoom look at every image.

## What this case teaches

A sanitized body does not make a sanitized artifact, and the surfaces that hold the identity are the ones no
one re-reads before publishing. The final pass must touch the container, the links, the images, the filenames
and the audio - not only the words.

## Report

```text
CHECKS   : text verify pass | metadata dump clean | strings pass clean | links audited | images zoomed | audio re-recorded
LOST     : the live dashboard demo (replaced with a static, re-taken screenshot)
RESIDUAL : low, with one caveat - the deck's structure and the specific metric obsession identify us to
           people who already work in this niche. Accepted; it is a talk, not a disclosure.
```
