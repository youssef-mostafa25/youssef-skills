# youssef-skills

My Claude Code skills, collected in one plugin. Once installed they show up as
`youssef-skills:<skill>` — for example `youssef-skills:planning-board`.

## planning-board

Turns "start a job" into a disciplined loop:

```
investigate (read-only) --> publish board --> one proposal per task
      --> wait for approval in words --> implement --> verify --> mark Fixed
```

Every status change is reflected on a published HTML board in the same turn.

## merge-assistant

Plans a git merge before touching anything:

```
preflight --> merge base --> 3 parallel analysts (source, target, cross-diff)
      --> tabbed merge review artifact --> your picks --> merge --no-commit --> verify
```

It looks for semantic conflicts that merge cleanly but break at runtime, not only
conflict markers. The review page has one tab each for the source branch, the
target branch, the combined view, the issues, every verification round, and the
decisions. Only the Decisions tab has pickers, and the copied reply carries the
page revision. Nothing is committed or pushed without your say-so.

## handoff

Writes a `<TOPIC>_HANDOFF.md` at the repo root when you pause work, so a fresh
session (or a teammate) can resume with nothing but that file and the repo:

```
git status / log / tests (real state) --> fold in any earlier handoff
      --> write ✅/⚠️ TL;DR, decisions, dead-ends, next steps, verify commands
```

Every claim is checked against the repo first; anything not checked is marked
unverified. A new handoff on the same topic replaces the old one and carries its
history forward.

## debug-log-sink

For bugs that ordinary console output can't show: several processes, hidden
stdout, frontend ↔ backend timing. It runs a tiny loopback-only HTTP collector that
writes every call into one `debug-log-sink.log` at the repo root:

```
git-ignore debug-log-sink.* (first use) --> start sink --> add marked log calls
      --> debug --> commit guard / teardown --> grep proves nothing is left
```

On first use in a repo it adds `debug-log-sink.*` to `.gitignore` and leaves it there
permanently, so you should commit that line. The log calls in your source files are
not covered by `.gitignore`, so don't commit while a session is active. The skill
checks staged changes before any commit and refuses if debug calls are present.

## Skills

| Skill | What it does |
|---|---|
| `planning-board` | The job loop: seven-heading proposals (Issue, Why, Fix, Gain, Effort, Risk, Legacy), per-task approval, status lifecycle, and the board template (`template.html`). |
| `merge-assistant` | Merge planning: parallel branch analysis, semantic-conflict detection, a tabbed review artifact with per-decision pickers (`merge-review-template.html`), then a `--no-commit` merge driven by your decisions. |
| `handoff` | Session handoff docs: grounded in `git` and real test runs, cumulative across sessions, with exact `file:line` references and copy-pasteable verification commands. |
| `debug-log-sink` | Ephemeral cross-process debug logging: bundled stdlib collector (`debug-log-sink.py`), greppable `DEBUG_LOG_SINK` markers, a pre-commit guard, and two-tier cleanup verified by `git grep`. |
| `sha3bolly` | The explanation style proposals are written in: plain words, always a concrete example, a flowchart when steps chain. `planning-board` and `merge-assistant` depend on it, so it ships here. Created by [Habiba Abueldahab](https://github.com/abueldahabh) — original at [abueldahabh/sha3bolly](https://github.com/abueldahabh/sha3bolly), MIT licensed ([`skills/sha3bolly/LICENSE`](skills/sha3bolly/LICENSE)). |

## Install

```
/plugin marketplace add youssef-mostafa25/youssef-skills
/plugin install youssef-skills@youssef-skills
```

## Requirements (planning-board, merge-assistant)

Both skills publish a page with Claude Code's `Artifact` tool: planning-board its
status board, merge-assistant its merge review. The tool is available when Claude
Code is signed in to a claude.ai account with Artifacts enabled. Without it,
planning-board's proposals and approval loop still work; only the board does not.
merge-assistant delivers its findings and decision pickers on that page, so it
needs the tool.

## Usage

For planning-board, say "start a job", "take the next job", or "plan this out before you change anything".

For merge-assistant, say "merge my feature into main", "bring my branch up to date with main", or "help me resolve these merge conflicts".

For debug-log-sink, say "I can't see the worker's logs", "correlate frontend and backend logs", or "remove the debug logs".

For handoff, say "write a handoff", "hand this off", or "I'll continue in another session".

## Adding a skill

Drop a folder with a `SKILL.md` into `skills/`, bump `version` in
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, push, then run
`/plugin marketplace update youssef-skills`.

## License

MIT — see [`LICENSE`](LICENSE). The bundled `sha3bolly` skill is © Habiba Abueldahab,
MIT licensed separately under [`skills/sha3bolly/LICENSE`](skills/sha3bolly/LICENSE).
