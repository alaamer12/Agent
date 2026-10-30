# When to ask, and what to ask

## The method

1. **Think through everything first.** Before writing any question, list every potentially relevant one. Consider:
   - what could happen in different situations (platforms, scales, failure cases);
   - internal details that change the result;
   - different aspects of the task that need a decision;
   - questions that could change the project or an important decision.
2. **Filter.** Keep a question only if it passes all four tests.

| Test | Keep the question when | Drop it when |
|---|---|---|
| Decision | different answers lead to different work | every answer leads to the same work |
| Inference | the answer cannot be deduced from the task, files, or conversation | the task already implies it |
| Consequence | a wrong guess is costly, risky, or hard to undo | a wrong guess is cheap to fix |
| Preference | the user may care, or the choice has lasting effects | there is no preference and no real effect |

3. **Look things up before asking.** Read the repository, configs, `package.json`, the OS, installed versions, existing code style. A question about something you could have checked wastes the user's time.
4. **Decide the rest yourself** and write each such decision in the context under "Assumptions I am making", so the user can object.

## Drop these

- "Is authentication required?" when the task says users log in and act on their own account.
- "How will authentication work?" when the stack and task already imply the standard approach.
- Cards or list for a screen, when the user has no preference and nothing depends on it.
- "Do you want tests?" when the project already has a test setup and convention.
- Anything the user already answered earlier in the conversation.

## Ask these

- A choice that shapes the architecture (database, framework, hosting model, sync vs async).
- A trade-off between things the user may value differently (cost vs speed, safety vs convenience, flexibility vs simplicity).
- A fact only the user knows (budget, deadline, who the users are, compliance rules, existing accounts).
- A risky or irreversible action (deleting data, migrating, changing a public interface).
- A choice where the two obvious options have non-obvious consequences the user may miss.

## Shape of the set

- Usually 3 to 8 top-level questions. Above 12 the page is too long; cut or merge.
- Order: foundational decisions first, dependent ones after. Put each follow-up right after its parent.
- Merge two questions when one answer always determines the other.
- Use one question per decision. Never bundle two decisions into one question.

## Do not use Inquire when

- You have exactly one quick question: ask it in chat.
- The user already gave a complete specification.
- The questions are about taste only, with no consequence.
