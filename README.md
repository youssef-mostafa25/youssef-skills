# youssef-skills

My Claude Code skills, in one plugin. Once it's installed, just talk to Claude
normally. Each skill starts when what you say matches it, or you can call one by name,
such as `/youssef-skills:planning-board`.

## Install

```
/plugin marketplace add youssef-mostafa25/youssef-skills
/plugin install youssef-skills@youssef-skills
```

To update later:

```
/plugin marketplace update youssef-skills
/plugin update youssef-skills@youssef-skills
```

## The skills

| Skill | Use it to… | Try saying |
|---|---|---|
| [planning-board](skills/planning-board/README.md) | Plan multi-task work, approve each task before any code changes, and track it all on a live board. Big plans can be split into PRs. | "start a job", "onto the next PR" |
| [merge-assistant](skills/merge-assistant/README.md) | Merge branches safely: every conflict, including the ones that merge cleanly but break, decided by you up front. Can also take a finished PR stack through Claude's review, one PR at a time. | "merge my feature into main", "run the stack through Claude's review" |
| [resolve-claude-pr-review](skills/resolve-claude-pr-review/README.md) | Check, fix, answer and resolve the comments Claude's reviewer left on a PR. | "fix claude's review on #123" |
| [handoff](skills/handoff/README.md) | Save where you are, so another session or a teammate can pick it up. | "write a handoff" |
| [debug-log-sink](skills/debug-log-sink/README.md) | Collect debug logs from processes whose output you can't see, then clean up every trace. | "I can't see the worker's logs" |
| [sha3bolly](skills/sha3bolly/README.md) | Get explanations in plain words, with a real example and a flowchart. | "I don't understand", "explain again" |

## How they fit together

```
planning-board ──plans and tracks──> your PRs
      │                                  │
      ├─ keeps stacked PRs in sync ──> merge-assistant
      │                                  │
      │                                  └─ review loop ──> resolve-claude-pr-review
      │
      └─ Claude review comments ──────> resolve-claude-pr-review
```

All of them explain things in the sha3bolly style.

## Things that stay in your hands

- **You approve every plan and decision** before Claude acts on it.
- **You commit and push.** These skills leave work uncommitted and never push for you.

## Requirements

- **planning-board** and **merge-assistant** publish a web page (the board, the merge
  review). That needs Claude Code signed in to a claude.ai account with Artifacts
  enabled. Without it, planning-board still works but without the board.
  merge-assistant needs the page, because that's where you make your choices.
- **resolve-claude-pr-review** and merge-assistant's review loop need the
  [`gh` CLI](https://cli.github.com/) signed in to your GitHub account.
- **debug-log-sink** needs Python 3.

## Adding a skill

Add a folder under `skills/` with a `SKILL.md` (for Claude) and a `README.md` (for
people), and link it in the table above. Then bump `version` in
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and push.

## License

MIT, see [`LICENSE`](LICENSE). The bundled `sha3bolly` skill is © Habiba Abueldahab,
MIT licensed separately under [`skills/sha3bolly/LICENSE`](skills/sha3bolly/LICENSE).
