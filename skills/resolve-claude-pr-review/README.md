# resolve-claude-pr-review

Deal with the comments Claude's reviewer (claude[bot]) left on your pull request. Each
comment is checked, fixed with a test, answered and resolved. Then one closing comment
on the PR sums up what changed.

## How to use it

Say things like:

- "fix claude's review on #123"
- "resolve the bot's comments"
- "fix and resolve Claude's review on #123" (this also approves the fixes for comments
  that turn out to be right)

## What you'll see

1. **A verdict on every comment.** Each one is checked against the code: it holds, it's
   wrong, or it's by design. Every verdict comes with the evidence. Comments from people
   are left alone.
2. **A short proposal for each real problem,** tracked on your
   [plan-build-board](../plan-build-board/README.md) board.
3. **Fixes with tests.** For each fix there's a test that fails without it, and then the
   PR's full test run.
4. **Your commit and push.** Claude hands the change back; you commit and push it.
5. **Replies and resolved threads.** Each review thread gets a reply naming the commit
   that fixed it, and is marked resolved.
6. **A closing comment** saying what was fixed, how it was tested, and what was left
   alone and why.

Your PR description is never edited. The closing comment is the record.

## Requirements

- The `gh` CLI, signed in with access to the repo.
