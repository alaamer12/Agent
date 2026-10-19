# Delivery and answers

## 1. Validate and build

```
python3 scripts/check_questions.py content.json     # exit 1 on ERROR; fix WARN items too
python3 scripts/build.py content.json --out inquire.html [--mode concise] [--lang ar]
python3 scripts/check_page.py inquire.html          # optional: needs `pip install playwright && playwright install chromium`
```
`build.py` defaults to **verbose**. It embeds the content safely, sets the page language and direction, and writes one self-contained HTML file (about 90 KB, libraries inlined, works offline).

## 2. Deliver

Pick by environment.

### A. The agent runs on the user's machine (terminal, Claude Code, IDE)

Run the server in the background so you can tell the user where to go, then wait:

```
python3 scripts/serve.py inquire.html --out answers.json > inquire.out 2>&1 &
sleep 1; cat inquire.out          # shows INQUIRE_URL=http://127.0.0.1:PORT/
```
Tell the user: "I opened the questions at that address. Take your time and press Submit." (The script also tries to open the browser; add `--no-open` to suppress.) Then wait until `inquire.out` contains `INQUIRE_ANSWERS_END`, or until the process exits (exit 0 = answered or skipped, exit 2 = timeout after 30 minutes). The answers are also saved to `answers.json`.

Console markers:

| Marker | Meaning |
|---|---|
| `INQUIRE_URL=...` | the server is ready |
| `INQUIRE_SKIPPED` | the user skipped (printed before the JSON) |
| `INQUIRE_ANSWERS_BEGIN` / `INQUIRE_ANSWERS_END` | the JSON between them |
| `INQUIRE_TIMEOUT` | nobody answered in time |

### B. The agent runs in a chat sandbox (the user cannot reach localhost)

Do not start the server. Deliver the HTML file instead:
- If an Artifact/publish tool exists, publish `inquire.html`.
- Otherwise save it in the outputs folder and present the file.

When there is no server, **Submit and Skip show the answer JSON in a highlighted block with a Copy button**. Tell the user to press Copy and paste it into the chat. That paste is the answer payload.

## 3. The answer payload

```json
{
  "title": "...", "date": "...", "skipped": false,
  "answers": [
    {"id":"sched","question":"...","type":"single",
     "selected":[{"option":"cron","recommended":false,"option_index":1}],
     "custom": null}
  ],
  "message": "only present when skipped"
}
```
- `selected` lists chosen options; `recommended` is true for the first option; `custom` holds the user's own text (it can be combined with `selected` in multiple choice).
- Questions hidden by branching are absent.

## 4. Handling the result

**Answered** (`skipped: false`): restate the decisions in a short list, flag any answer that conflicts with another, and continue. Treat `custom` text as the user's own instruction and honour it. If a custom answer reveals a new important unknown, ask one more small round instead of guessing.

**Skipped** (`skipped: true`): the user rejected the questioning and wrote `message` to steer you.
1. Read `message` first. It overrides your plan.
2. Look at `answers` for partial choices. They show where your questions were close to right.
3. Decide: refine the questions (rebuild a new, shorter page), change direction, or stop asking and proceed with explicit assumptions if the message says so.
4. Never re-send the same questions unchanged.
5. Say in one sentence how you understood the message before acting.

## 5. Page behaviour worth knowing

- Answers survive refresh and accidental close (session storage). Reopening the same page restores them.
- Enter in the skip box skips; Shift+Enter adds a new line; Ctrl/Cmd+Enter in an answer box submits. All text boxes grow to a limit, then scroll.
- Submit requires every visible question to have an answer (an option or custom text).
- The page works on phones and respects `prefers-color-scheme`-style theming through `?theme=dark`.
