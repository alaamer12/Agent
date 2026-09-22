# Worked example: reserved structure vs. custom structure, same conversation

## Source

```
User: How do I reset my router if it's not responding to the app?
Agent: Hold the reset button on the back for 10 seconds until the lights flash,
then wait about 2 minutes for it to fully reboot and reconnect. If the app still
can't find it after that, forget the network on your phone and rejoin it fresh,
since the router issues a new network name sometimes after a factory reset.

User: Will I lose my wifi password and custom network name?
Agent: Yes — a factory reset via the physical button clears all custom settings,
including your network name and password, and reverts to the default printed on
the router's label. You'll need to reconfigure those in the app afterward. If you
just want to fix a connectivity glitch without losing settings, try unplugging
the router for 30 seconds first instead of using the reset button.

User: Ok, I'll try the unplug method first. How long before I should give up on that
and go to the factory reset?
Agent: Give the unplug method about 5 minutes total after plugging back in. If the
app still can't detect the router after that, move to the factory reset.
```

## Request A (reserved structure): "Summarize this, keeping my questions and just summarizing the agent's answers."

This is a content instruction (what to do with each role), not a layout instruction — turn order and pairing carry over unchanged. See templates/conversation-role-preserving.md.

```
**User:** How do I reset my router if it's not responding to the app?

**Agent:** Hold reset for 10 seconds, wait ~2 minutes to reboot, then re-join the
network on your phone if the app still can't find it.

**User:** Will I lose my wifi password and custom network name?

**Agent:** Yes, factory reset clears custom settings back to the default label —
try unplugging for 30 seconds first if you just want to fix connectivity without
losing them.

**User:** Ok, I'll try the unplug method first. How long before I should give up on that
and go to the factory reset?

**Agent:** About 5 minutes after plugging back in; if the app still can't detect it, move
to the factory reset.
```

The three questions are untouched. Each agent answer is compressed (Normal mode) but still reads as a direct answer to the question right above it, because nothing was reordered.

## Request B (custom structure): "Write all user's questions on top and tag-id # them with headers, then match the agent answers below by the same tag."

This is a layout instruction — a different arrangement than the source's turn-by-turn shape. Build directly to the spec; question/answer pairing is preserved through the shared `#` tag instead of through adjacency. See references/07-conversation-and-custom-structure.md.

```
## Questions

**#1** How do I reset the router if it's not responding to the app?
**#2** Will a factory reset lose the wifi password and network name?
**#3** How long to try the unplug method before moving to a factory reset?

## Answers

**#1** Hold reset for 10 seconds, wait ~2 minutes to reboot, then re-join the network
on your phone if needed.

**#2** Yes — factory reset clears custom settings to the default label. Unplugging for
30 seconds first fixes connectivity without losing them.

**#3** About 5 minutes after plugging back in; if still undetected, do the factory reset.
```

Same underlying content decisions (selection, compression, faithfulness) as Request A — only the arrangement changed, and the `#` tags substitute for the adjacency that used to make the pairing obvious.

## What to notice

- Both requests are summarizing the same source and the same role (agent answers get compressed in both) — the difference is entirely about arrangement, not content selection.
- Request A never had to invent a linking mechanism because turn order already provided one.
- Request B had to add one (the `#` tags) specifically because separating questions from answers removes the adjacency that made the pairing implicit in the source — dropping that link would leave the reader unable to match answers back to questions.
- Neither version paraphrases the user's own questions into something shorter in Request A — questions were the preserved role. In Request B they're lightly tightened for the "list of questions" format, since the user only asked for repositioning + tagging, not verbatim preservation, and a standalone question list reads better slightly cleaned up. If the user in Request B had also said "keep my questions exactly as I wrote them," that would override this — the content rule (verbatim) and the layout rule (grouped at top) combine, per 07's guidance on requests containing both.
