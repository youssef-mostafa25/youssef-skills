# handoff

Pause work and pick it up later without losing anything. Claude writes a
`.handoffs/<TOPIC>_HANDOFF.md` in your repo. The `.handoffs/` folder is added to
`.gitignore` the first time, so handoffs never get committed. A fresh session can carry
on from that file and the repo alone. To hand off to a teammate, send them the file.

## How to use it

Say things like:

- "write a handoff"
- "hand this off"
- "I'll continue in another session"
- "before we lose context"

## What you get

One Markdown file with:

- a short ✅ / ⚠️ summary of where things stand,
- the decisions made, and why,
- the dead ends already tried,
- the next steps,
- commands to check the current state for yourself, with exact file and line
  references.

Everything in it is checked against the repo and real test runs first. Anything Claude
couldn't check is marked as unverified. Writing a new handoff on the same topic updates
the old file and keeps its history.

To resume, open a new session and point Claude at the file.
