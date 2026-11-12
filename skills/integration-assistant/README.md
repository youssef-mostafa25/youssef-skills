# integration-assistant

Merge or rebase git branches without surprises. Before anything is merged or rebased, Claude works out what
each branch changed and where they collide. That includes changes that merge cleanly
but break when the code runs. You decide how to handle each one, and then the merge is
done your way.

## How to use it

Say things like:

- "merge my feature into main"
- "bring my branch up to date with main"
- "help me resolve these merge conflicts"
- "run the stack through Claude's review" (see *Review loop* below)

## What you'll see

1. **A few quick checks.** Your working tree must be clean, and Claude asks whether to
   fetch the latest first.
2. **A review page** (a link), with tabs:
   - **Source** and **Target:** what each branch changed.
   - **Combined:** the big picture and a conflict map.
   - **Issues:** every problem found, each with a real example from your code.
   - **Decisions:** the choices you need to make.
3. **Your picks.** Each decision has options with a recommended one, and the page starts
   with every recommendation already picked. Change any you disagree with, press Copy,
   and paste the reply back. You can also type it yourself, for example
   `D1:1 D2:2`.
4. **The merge.** Claude saves a backup point, merges without committing, applies your
   decisions, and runs the checks. Then it asks you before committing.

Nothing is committed without your yes, and Claude never pushes.

## Review loop (large stacked PRs)

For a stack of PRs that is finished and tested, when you want Claude to review each one
on GitHub. Say "run the stack through Claude's review". Then, one PR at a time from the
bottom:

```
Claude rebases the PR on its base  -->  you force-push
   -->  the review is requested, your saved way  -->  Claude waits for it
   -->  Claude fixes the findings (you approve, commit and push)
   -->  threads answered and resolved, closing comment posted
   -->  next PR
```

- **What you do:** make the merge decisions, give the go for each rebase, approve the
  review fixes, and run every commit and push. Claude gives you the exact commands and
  checks that GitHub got them before moving on.
- **The review trigger is your choice.** The first time in a repo, Claude asks how each
  review should be requested: **ask** you before adding the review label (the default),
  add it **automatically**, or leave it to **you**. The answer is saved in
  `~/.claude/integration-assistant/review.md`, per repo. Change it any time: "always add
  the review label", "ask me first", or "I'll request reviews myself".
- **When it stops:** a failed check, a review that never starts, or "stop" from you.
  Claude tells you where it stopped, and the PRs above that point are left as they were.

## Requirements

- Claude Code signed in to a claude.ai account with Artifacts enabled. The review page
  is where you make your choices.
- For the review loop: the `gh` CLI, and a repo where Claude reviews PRs (usually when a
  label such as `claude-review` is added).
