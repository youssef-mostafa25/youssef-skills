# resolve-pr-reviews

Deal with the review comments on your pull request, from AI reviewers (Claude, Copilot,
CodeRabbit, Gemini…) or from people. Each comment is checked, fixed with a test or
answered, and replied to. Then one closing comment on the PR sums up what changed.

## How to use it

Say things like:

- "fix the review on #123"
- "address copilot's comments" / "resolve alice's review" (only that reviewer)
- "fix and resolve the review on #123" (this also approves the fixes for comments that
  turn out to be right)

## What you'll see

1. **A verdict on every comment.** Each one is checked against the code: it holds, it's
   wrong, it's by design, or it was already fixed. Questions get answers. Every verdict
   comes with the evidence.
2. **One round of questions** for what only you can decide: design changes, a person's
   suggestions and nits, and (unless your preferences already say) whether to resolve
   people's threads or leave that to them, and whether to re-request their review.
3. **A short proposal for each real problem,** tracked on your
   [plan-build-board](../plan-build-board/README.md) board.
4. **Fixes with tests.** For each fix there's a test that fails without it, and then the
   PR's full test run.
5. **The commit and push**, your [preferred](../../README.md#your-preferences) way. By
   default Claude hands the change back and you commit and push it.
6. **Replies.** Each thread gets a reply naming the commit that fixed it, or the answer.
   AI reviewers' threads are resolved. A person's thread is resolved only if you said so
   (in the round or in your preferences),
   and one Claude disagrees with is always left for that person.
7. **A closing comment**, one section per reviewer, saying what was fixed, how it was
   tested, and what was left alone and why.

Your PR description is never edited. The closing comment is the record.

## Requirements

- The `gh` CLI, signed in with access to the repo.
