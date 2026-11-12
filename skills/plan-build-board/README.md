# plan-build-board

Plan first, then build, one approved piece at a time. Claude looks into the work, asks
you everything it needs in one go, and writes a short proposal for each task. You
approve in words before any code changes. A live web page (the **board**) shows where
every task, job and PR stands.

## How to use it

Say things like:

- "start a job" / "plan this out before you change anything"
- "onto the next task" — plans one task
- "onto the next job" — plans every task in the next job
- "onto the next PR" — plans every task in every job of that PR
- "work through these issues"

## What you'll see

1. **One round of questions.** Which tasks to include, what to do with old code paths,
   approach choices, which folders Claude may touch (see *Lanes* below), and whether to split into PRs. It's
   all asked at once, before anything is planned.
2. **A link to the board.** Tabs for Jobs, PRs, the work queue, every task, and Issues
   when the work comes from tracked issues.
3. **Proposals.** Each task gets the same seven parts: the issue, why it matters, the
   fix, what you gain, effort, risk, and legacy. Legacy (what happens to the old code)
   is always your call.
4. **One job at a time.** A *job* is a few related tasks done together. After each one
   you get a review you can read in one sitting: what changed where, the order to read
   it in, the test results, and a `git diff` per task. The next job starts only when you
   say so.

## Lanes: folders Claude may edit

The first time you use it in a repo, Claude lists the repo's services and asks which ones
it may **always edit without asking** and which ones **need your OK each time** (a *lane
exception*, asked per job). Your answer is saved in `~/.claude/plan-build-board/lanes.md`, one
section per repo, so later sessions don't ask again. Change it any time: "always let me
edit `web/`" or "ask before touching `agent/`".

## What stays with you

- **Approval.** Nothing is implemented until you approve it in words.
- **Git.** Claude never commits, pushes, creates branches or opens PRs unless you ask,
  and asking once doesn't cover the next time. Work is left uncommitted for you.

## PRs

- **Every job lands in a PR.** The PRs tab shows each PR as **independent** (merges into
  the base in any order) or **stacked** (builds on the PR below it, merged in order).
  Claude proposes a stack only for a big plan, and only makes one if you agree.
- **Copyable details.** Each PR has its details ready to copy: branch names, title, the
  command to create the branch, draft or not, and merge method. They sit collapsed under
  "PR config"; open the one you need.
- **Ready to open.** When a PR's work is done, chat gives you the short details, each in
  its own copy block. The full PR description is on the board, behind a Copy button.
- **Safe branches.** The create commands use `--no-track`, so pushing a new branch can
  never send its commits onto the branch it was started from.
- **When `main` moves,** the stack is left alone unless something actually needs a sync.
  Then it is updated one PR at a time, through
  [integration-assistant](../integration-assistant/README.md).
- **Claude's review of a finished stack.** Once every PR is done, tested and opened, say
  "run the stack through Claude's review". Each PR is then rebased, reviewed by Claude
  and fixed in turn (see integration-assistant's *Review loop*).

## Issues

When tasks come from tracked issues, the board maps each issue to its tasks, jobs and
PRs. A PR says `Closes #n` only when it fully fixes that issue. The board warns you if a
PR would close an issue too early.

## Requirements

- Claude Code signed in to a claude.ai account with Artifacts enabled, to publish the
  board. Without it, the proposals and approvals still work, just without the board.
- The `gh` CLI, when the work involves GitHub issues or PRs.
