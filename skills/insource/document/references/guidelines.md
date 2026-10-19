# Document Skill — Full Guidelines

Authoritative detailed rules derived from the original specification. Load this file when the agent needs the complete guidance; keep SKILL.md itself slim.

## Purpose

Document is a documentation-generation skill that creates Markdown documents according to the user's exact requirements.

Its purpose is to transform the user's instructions, requested content, available context, and source material into a document that matches the user's intended scope, level of detail, structure, and purpose.

The skill must respect what the user actually requests rather than substituting its own preferred documentation style.

A document may be comprehensive, concise, or follow another level of detail specified by the user. The skill must understand these requirements before writing and preserve them throughout the document.

The skill also supports reconstructing detailed conversation history when the user requests a complete record of previous work, including investigations, decisions, tool usage, errors, corrections, and findings.

The user's requested level of detail determines what the document must contain.

## 1. Follow the User's Instructions

Before writing, identify the user's requirements and treat them as the primary source of truth.

Determine, as applicable:

- The document's purpose
- The intended audience
- The requested scope
- The required topics
- The desired level of detail
- The preferred structure
- The source material to use
- The required language
- Any explicit inclusions or exclusions
- The expected output format and location

Follow explicit instructions precisely.

Do not replace the user's requested document with a different artifact merely because it seems more useful or conventional.

Examples:

- If the user requests a complete technical transcript, do not produce only a summary of lessons learned.
- If the user requests a concise document, do not produce an unnecessarily lengthy explanation.
- If the user requires specific events, errors, investigations, or decisions to be included, ensure that they are addressed rather than silently omitted.

When requirements conflict or essential information is missing, resolve the ambiguity according to the user's stated priorities or ask a focused clarification question.

## 2. Choose the Appropriate Documentation Style

The skill supports different documentation styles. The user's instructions determine which style to use.

### 2.1 Comprehensive

A comprehensive document covers the requested subject thoroughly, including relevant details, context, explanations, and supporting evidence.

Depending on the request, this may include:

- Background and initial conditions
- The original problem or objective
- The complete sequence of important events
- Investigation methods
- Tools and commands used
- Files inspected
- Errors encountered
- Incorrect approaches and why they failed
- Corrections and why they worked
- Verification procedures and results
- Technical discoveries
- Sources consulted and what they contributed
- Decisions and their rationale
- Unresolved issues and limitations
- Final outcomes

Comprehensive does not mean adding unrelated material or repeating the same information unnecessarily. It means fully covering the requested scope without omitting relevant details.

See also `references/comprehensive.md` for focused style guidance.

### 2.2 Concise

A concise document communicates the complete information needed for its intended purpose using fewer words.

It should preserve the essential meaning, conclusions, requirements, decisions, and necessary context while removing unnecessary repetition and secondary detail.

Concise does not mean incomplete.

The skill must not remove information that is necessary to satisfy the user's request merely to make the document shorter.

See also `references/concise.md` for focused style guidance.

## 3. Clarify the Desired Level of Detail

When the user's instructions clearly establish the document's scope and level of detail, follow them without asking unnecessary questions.

When important requirements remain ambiguous, ask the user a focused clarification question before committing to a particular interpretation.

For example, a user may request a comprehensive document without clarifying whether they want:

- A complete chronological account of the work
- A technical explanation of the final solution
- Every relevant tool invocation and command
- Errors and failed approaches
- Files inspected and their findings
- Websites and sources consulted
- Detailed verification evidence
- A summary of the conclusions only

These are materially different documentation requirements.

When the distinction matters, ask whether the user wants the detailed execution history or primarily the technical explanation and conclusions.

Do not ask about preferences the user has already specified.

### Explicit Instructions Take Priority

If the user explicitly requests the complete history, including failed attempts, tool calls, sources, verification, and mistakes, do not ask whether they would prefer a summary. Produce the detailed record they requested.

Likewise, if the user explicitly requests a concise document, do not treat the word "document" as permission to produce an exhaustive report.

## 4. Recover Context Before Writing

When the requested document depends on a previous conversation, earlier work, or context that may no longer be available in the active context window, reconstruct the relevant information before drafting.

Context may be incomplete because of conversation length, context compaction, interruptions, or work performed across multiple sessions.

## 5. Preserve the Full Requested History

When documenting an investigation or a sequence of technical work, preserve the details required to understand what actually happened.

Depending on the user's request, this may include the following.

### Initial Objective

### Investigation

### Errors and Failed Approaches

Do not rewrite the history to make the work appear flawless.

### Corrections

- What was changed
- Why the correction was appropriate
- How it addressed the underlying cause
- What alternatives were considered when relevant
- What consequences or trade-offs followed

### Verification

- What tests or checks were performed
- How the original issue was reproduced
- What results were observed
- How the correction was confirmed
- Which verification steps failed or remained incomplete
- What limitations prevented stronger conclusions

### Final State

- What was successfully resolved
- What remains unresolved
- Which findings were confirmed
- What evidence supports the final conclusions
- What the user should know about the resulting state

Include the categories relevant to the request. Do not force irrelevant sections into every document.

## 6. Document Usage of Resources

Document at the level of detail requested.

This may include:

- Tool or command names
- Relevant arguments
- The purpose of each operation
- Important outputs
- Errors returned
- Files read or modified
- What the operation established
- How its results influenced subsequent actions

For external research, document:

- Which sources were consulted
- Why they were consulted
- Which relevant information they provided
- How that information affected the investigation or decision
- Any limitations or uncertainty in the sources

Include source links when available and useful.

Do not invent commands, outputs, URLs, citations, or tool operations.

Do not claim that a website was visited, a file was inspected, or a test was run unless the available evidence supports that claim.

A comprehensive report should explain not only what was done, but also why the steps mattered and what they revealed.

## 7. Preserve Technical Specificity

Do not reduce technical details to generic lessons when the user requests a detailed technical account.

For example, if the user requests documentation of a debugging investigation involving dump files and symbol tools, preserve the relevant details, such as:

- Which dump files were inspected
- Which tools and commands were used
- Which symbols were available or missing
- What the diagnostic output revealed
- Which initial interpretations were incorrect
- How the investigation was corrected
- How the findings led to the root cause
- How the fix was validated

Similarly, if the investigation involved forwarding errors to an observability service, document the relevant integration, configuration, diagnostic evidence, and verification steps when requested and supported by the available records.

The level of specificity should follow the user's request, not a default preference for abstraction.

## 8. Organize the Document Around Its Purpose

Choose a structure that makes the information easy to understand without distorting its meaning.

Possible structures include:

- Chronological sections for an investigation history
- Topic-based sections for a reference document
- Sequential steps for a procedure
- Problem, evidence, root cause, and resolution for a troubleshooting report
- Requirements and behavior for a specification
- Findings and recommendations for an audit

Use headings, lists, tables, code blocks, and links where they improve readability.

For long comprehensive documents, use meaningful sections and subsections to make detailed information navigable.

Do not omit relevant content merely because it makes the document longer.

Do not add decorative structure that provides no value.

## 9. Create the Markdown File

The output must be a Markdown document unless the user explicitly requests a different format.

Use an appropriate filename and location based on the user's instructions and the project's conventions.

## Final Principle

Write the document the user asked for, not the document the agent would prefer to write.

Respect the requested level of detail, recover the relevant context, preserve the required information, distinguish evidence from assumptions, and produce a Markdown document that fulfills the user's actual intent.
