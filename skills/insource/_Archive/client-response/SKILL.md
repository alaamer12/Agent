---
name: client-response
description: Turns a client's project requirement message plus a Q&A conversation (developer questions and the client's answers) into one organized project-description file. Content is only reorganized and rephrased, never added to or omitted. Use whenever the user pastes a client brief and/or a Q&A thread and asks to organize it, write the client response, or produce the project requirements document, or invokes /client-response.
---

# client-response

Write ONE file that organizes what the client said. Nothing else: no analysis, no advice, no suggestions.

## On invocation: do nothing and wait

When the skill is invoked, do NOT write, create, or analyze anything. No files, no tool calls, no drafts. Reply with a short message saying you are waiting for two inputs, preferably sent as two separate messages in this order:

1. **Client brief**: the client's project requirement message. It may include attachments, links, or references to files.
2. **Q&A conversation**: the developer's questions and the client's answers.

Reply in the user's language, for example: "Ready. I'm waiting for two inputs, preferably sent separately: (1) the client's project requirement, then (2) the Q&A conversation."

### While receiving

- After the first input arrives alone: confirm in one line which input you received and that you are still waiting for the other. Do not start writing.
- If the user sends both in one message, accept it and split them yourself.
- If the user sends them in the opposite order, accept it and identify each by content.
- Start producing the file only once both inputs are received, or if the user explicitly says to proceed with what they sent.

## The two hard rules

- **No adding.** Every statement must trace back to the brief or the Q&A. No assumptions, no "best practice" fill-ins, no inferred features, no invented numbers.
- **No omitting.** Every point from either input must appear in the output, including small details, examples, and numbers. Only wording and order may change.

Allowed: regrouping by topic, merging duplicates (keeping every distinct detail), rephrasing into clear formal prose, turning scattered answers into lists, translating dialect into the document's language.

Not allowed: dropping a point because it seems minor, resolving a contradiction silently, upgrading a wish ("would be great") into a requirement, or downgrading a firm statement into a wish. Keep the client's level of certainty.

## Output

- **Language:** the language of the inputs, unless the user says otherwise.
- **Format:** Markdown, saved to `/mnt/user-data/outputs/` (default name `client-response.md`), then presented to the user.
- **Style:** numbered `##` sections, short paragraphs, bullet lists for enumerations, `###` subsections where a topic has parts, a short example when the client gave one. Formal, neutral voice, written as a project-description document, not as a chat log.

Suggested flow (adapt headings to the actual content; only create sections the inputs support):

1. Core idea of the project
2. Relationship to any existing system, platform, or API the client mentioned
3. Identity, design, languages, countries, and currencies
4. User types and accounts
5. Core features, in the order the client described them
6. Admin and control panel
7. Technical and integration decisions the client answered
8. Reports, statistics, and other remaining topics
9. **Open points**

### Open points section

List developer questions the client did not answer, and any client question aimed at the developer that is still pending (for example, a request for the developer's opinion). Use the original meaning only. If everything was answered, omit the section. If the user asks for these to be left out entirely, omit it.

### Contradictions

If the brief and the Q&A conflict, state both versions side by side under the relevant section, noting which came from the brief and which from the Q&A. Do not choose.

### Attachments

If the brief mentions files (designs, prototypes, documents), list them as "referenced materials" with what the client said about them. Do not describe their contents unless they are actually provided and read.

## Before delivering

Run this check silently:

1. Go through the brief sentence by sentence: is each point in the file?
2. Go through each Q&A pair: is each question's answer in the file, or the question in Open points?
3. Is there any statement in the file that is not in the inputs? Remove it.

Then present the file with a one-line note listing how many open points remain. No long summary.
