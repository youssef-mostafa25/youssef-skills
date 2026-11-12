# youssef-skills

My Claude Code skills, in one plugin. Once it's installed, just talk to Claude
normally. Each skill starts when what you say matches it, or you can call one by name,
such as `/youssef-skills:plan-build-board`.

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
| [plan-build-board](skills/plan-build-board/README.md) | Plan multi-task work, approve each task, then build it job by job, tracked on a live board. Big plans can be split into PRs. | "start a job", "onto the next PR" |
| [integration-assistant](skills/integration-assistant/README.md) | Merge or rebase branches safely: every conflict, including the ones that merge cleanly but break, decided by you up front. Can also take a finished PR stack through Claude's review, one PR at a time. | "merge my feature into main", "run the stack through Claude's review" |
| [resolve-pr-reviews](skills/resolve-pr-reviews/README.md) | Check, fix, answer and resolve a PR's review comments, from AI reviewers or people. | "fix the review on #123", "address copilot's comments" |
| [handoff](skills/handoff/README.md) | Save where you are in a git-ignored `.handoffs/` folder, so another session can pick it up. | "write a handoff" |
| [debug-log-sink](skills/debug-log-sink/README.md) | Collect debug logs from processes whose output you can't see, then clean up every trace. | "I can't see the worker's logs" |
| [sha3bolly](skills/sha3bolly/README.md) | Get explanations in plain words, with a real example and a flowchart. | "I don't understand", "explain again" |

## How they fit together

```
plan-build-board ──plans and tracks──> your PRs
      │                                  │
      ├─ keeps stacked PRs in sync ──> integration-assistant
      │                                  │
      │                                  └─ review loop ──> resolve-pr-reviews
      │
      └─ PR review comments ──────────> resolve-pr-reviews
```

All of them explain things in the sha3bolly style.

## Your preferences

How much Claude does on its own is your call, and each person sets their own. The first
time you use a skill, it asks the settings it needs that you haven't answered yet, with
the cautious choice recommended:

| Setting | Choices | Used by |
|---|---|---|
| `commit`: commits and new branches | **never**, ask, auto | every skill that touches git |
| `push`: pushes and opening PRs | **never**, ask, auto | every skill that touches git |
| `force_push` | **never**, ask | integration-assistant |
| `approval`: wait for your yes before building | **wait**, proceed | plan-build-board, resolve-pr-reviews |
| `review`: when Claude stops for your review | **each-job**, each-pr, end | plan-build-board, resolve-pr-reviews |
| `resolve_threads`: people's fixed review threads | **ask**, reviewer, me | resolve-pr-reviews |
| `rerequest_review` | **ask**, always, never | resolve-pr-reviews |

They're saved in `~/.claude/youssef-skills/preferences.md`, outside your repos. Edit the
file, or just tell Claude ("commit for me from now on", "wait for my review after each
job"). Saying it once ("push this one") covers that one time only.

Some things no setting changes: you make every merge and design decision, every branch
is created with `--no-track`, nothing is called done before it's verified, and a
force-push always needs your yes.

## Requirements

- **plan-build-board** and **integration-assistant** publish a web page (the board, the merge
  review). That needs Claude Code signed in to a claude.ai account with Artifacts
  enabled. Without it, plan-build-board still works but without the board.
  integration-assistant needs the page, because that's where you make your choices.
- **resolve-pr-reviews** and integration-assistant's review loop need the
  [`gh` CLI](https://cli.github.com/) signed in to your GitHub account.
- **debug-log-sink** needs Python 3.

## Adding a skill

Add a folder under `skills/` with a `SKILL.md` (for Claude) and a `README.md` (for
people), and link it in the table above. Then bump `version` in
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` and push.

## License

MIT, see [`LICENSE`](LICENSE). The bundled `sha3bolly` skill is © Habiba Abueldahab,
MIT licensed separately under [`skills/sha3bolly/LICENSE`](skills/sha3bolly/LICENSE).
