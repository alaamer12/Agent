# Inspiration, then a worked file

## 1. Inspiration is a set, not a single reading

> "It's a free phone app for publishing and reading blogs in <community> - basically a mini Medium."

| Inspiration | Relationship | What the project takes | What it refuses |
|---|---|---|---|
| **Medium** | instance of | the publishing model: individual writers, long-form posts, a follower graph, reading-first design | story-presentation layouts, monetization, the publication economy |
| **Dev.to** | similar to | the writer-culture feel: approachable writing, community tone | tag-driven discovery, developer-specific framing, its tooling culture |
| (none) | invention | the <language> reading-room identity and the "free forever" stance | - |

The composite, in one paragraph: *"Medium's publishing core (instance of), Dev.to's writer culture (similar
to), with neither one's monetization or algorithmic discovery - plus its own reading-room identity, which
neither source has."* The three labels - `[instance of]`, `[similar to]`, `[a slice of]` - describe **one
source each**; a project routinely mixes them.

**When the prompt names no inspiration, the skill asks before writing.** The prompt above says "mini
Medium", so the source is named. But this one:

> "There's an idea for an app where teams can track issues and plan sprints."

names no inspiration at all - it describes a category. The skill's first move is one direct question:
*"Is this project similar to Jira?"* (or, when no single product fits: *"Is this project similar to a
big-data scraper?"*). The answer decides what is owed and what is refused; guessing it would invent the
project's inspiration.

## 2. Worked file from a messy spoken prompt

Source (sped in one breath, mixed language - paraphrased):

> "There's this project idea… an app like Medium, maybe called Minbar, the name isn't settled. It's a phone
> app where you publish and read long-form blog posts in <language>. Medium had the deep presentation stuff
> - fancy story layouts - we don't need that. Like Dev.to in how it treats writers, friendly, not fancy.
> Just the basics of blogging, and you can follow a writer. No payments, no ads, completely free."

### IDEA.md (as produced)

```markdown
# Minbar — project idea

## The idea in one line

A free, phone-first app where <language> readers and writers publish and read long-form posts and follow
their favourite writers - a working blogging community, with none of the platform machinery.

## Inspiration

| Inspiration | Relationship | What the project takes | What it refuses |
|---|---|---|---|
| Medium | instance of | the publishing model: individual writers, long-form posts, follower graph, reading-first design | designed story layouts, monetization, the publication economy |
| Dev.to | similar to | the writer-friendly culture and tone | tag-driven discovery, developer framing |
| (none) | invention | the <language> reading-room identity, "free forever" | — |

**In one paragraph:** Medium's publishing core applied to the <language> community, with Dev.to's
writer-friendly culture instead of platform gloss, and neither one's monetization or algorithmic
discovery. What is genuinely its own is the reading-room identity - neither source has that.

## What it is

Minbar is a blogging app for phones, in <language>, where writing and reading are the whole product. A
writer creates posts the way they would write a letter, and publishes them to readers who follow them. Free
to read, free to write.

## Audience

The audience is the <language>-speaking reading and writing community. It has two kinds. The writers are
people who want a place for long-form writing in their own language, away from platforms built for other
languages and audiences - they may be published authors or first-time bloggers. The readers are people who
want to follow those writers and read what they publish, without an algorithm choosing for them; they are
the larger side of the audience and the product is built around them. Both kinds overlap: a reader can
become a writer without changing anything but pressing write.

## What it includes

Anyone can write an article and publish it from the phone in a few steps, and each writer has a simple page
listing what they have written, so a reader who likes one article can find the rest. Articles open in a
clean reading view built for long text - reading is the centre of the product, and everything else serves
it. A reader can follow any writer, and what the writers they follow publish arrives together in one
stream, so keeping up with ten writers does not mean visiting ten places. And the whole thing is free: no
subscription, no paywall, no ads, no paid tier, no writer earnings. Free is not a pricing strategy here; it
is part of what the product is.

Everything beyond writing, reading, following and being free was not stated by the user, and is listed
under Open questions rather than assumed.

## What it does not include

Medium's deep feature set is out: the story-presentation and formatting features the prompt names, and by
extension the long tail of Medium extras. This is intentionally a mini product, not a smaller copy of
everything. Any form of earning is out as well - no subscriptions, no paywall, no "premium" articles, no
advertising, no writer payouts, no donations mechanism; the user's words were "no profit or anything like
Medium". From Dev.to, the culture comes in but its tag-driven discovery and developer framing do not.
Branded multi-writer publications and an editor-curated front page are refused too: the described idea
reaches readers through following, not through an editorial or algorithmic layer.

The general rule the refusals share: if a feature is not part of writing, reading, following or being
free, it is not in this idea.

## Open questions

1. **The name.** Wasit (وسيط) or Mutawassit (متوسط)? Both were offered as "something like that", and the
   user said the name "won't be big anyway".
2. **Where "basics" ends.** Liking, commenting, saving an article, sharing a link, searching for writers -
   which of these are part of "the basics of blogging" for this project, and which are the "deep features"
   to leave out? The prompt drew "follow" inside and "story presentation" outside; the line between them
   is not settled.
3. **How plain is the editor.** Plain text only, or headings, quotes, images, links? This is the same line
   as question 2, seen from the writing side.
4. **Discovery beyond following.** Can a reader find writers they do not already know - by topic, by
   search, by a curated list - or is following the only way in? The prompt named following and nothing else.
5. **Reading without an account.** Can someone read freely before signing up, or is an account required to
   read as well as to write?
6. **Editorial position.** Is everything published instantly and unmoderated, or is there review? Who
   decides what counts as fitting content, and are posts outside that scope allowed at all? This changes
   what the product is, not just how it is run.
```

### Why the file looks like this

- **The inspiration table does the work**: each source contributes something specific, each has its own
  relationship, and each has its own refusal list. The excludes section mirrors that grouping in prose.
- **"What it includes" and "What it does not include" are prose, not scaffolding** - normal paragraphs a
  person reads, with no fixed sub-headings or module tables. The depth fence held: four capabilities, no
  sub-feature matrices.
- **Open questions are about the idea only**: name, scope boundaries, discovery, access rules, editorial
  stance. No platform, stack, hosting or typography - those belong to later stages, not to this document.
- A non-technical reader can restate the idea after one read; nothing assumes the source conversation.
