---
name: resolve-claude-pr-review
description: Use when a pull request has review comments from the claude[bot] reviewer, or the user asks to fix, address, answer or resolve Claude's review on a PR (e.g. "fix claude's review on #1188", "resolve the bot's comments").
---

# Resolving a Claude PR review

## Overview

claude[bot] posts a review as inline threads plus one summary comment. Each
finding becomes a task with a written proposal, fixed with a failing test
first, answered on its own thread, and resolved. The work ends with one
top-level PR comment saying what was done. The PR description is never
edited; that comment is where the review's changes are recorded.

**REQUIRED SUB-SKILL:** `youssef-skills:plan-build-board`. Its seven-heading
proposal, board updates and "never commit" rule apply here unchanged.

## Steps

1. **Read the review.**
   ```bash
   gh pr view <n> --json reviews,comments          # summary comment(s)
   gh api --paginate repos/<owner>/<repo>/pulls/<n>/comments \
     --jq '.[] | select(.user.login == "claude[bot]" and .in_reply_to_id == null)
           | "\(.id) \(.path):\(.line) \(.body)"'       # bot findings, not replies
   gh api graphql -f query='query{repository(owner:"<owner>",name:"<repo>"){pullRequest(number:<n>){reviewThreads(first:100){totalCount nodes{id isResolved comments(first:1){nodes{databaseId author{login}}}}}}}}' \
     --jq '.data.repository.pullRequest.reviewThreads | "threads: \(.totalCount)", (.nodes[] | select(.isResolved == false and .comments.nodes[0].author.login == "claude") | "\(.id) \(.comments.nodes[0].databaseId)")'
   ```
   The GraphQL list is the work: each open bot thread (`PRRT_…`) and the
   `databaseId` of its first comment, which matches a REST `id`. A REST
   finding missing from it is already resolved. The bot is `claude[bot]` in
   REST but `claude` in GraphQL. If `threads:` is over 100, stop and say so;
   the list is cut.

2. **Verify each finding against the code.** Read the cited lines and run a
   probe or test where you can. Each one is **Holds**, **Refuted** or **By
   design**, with the evidence. The review's "observations, not findings" are
   not tasks; note them and leave them unless the user asks. A thread opened
   by anyone else is not this skill's to answer or resolve; leave it.

3. **Write the proposals.** One per finding that holds, under the seven
   headings (issue, why, fix, gain, effort, risk, legacy). If a board exists
   for this work, add each finding as a task and group them into one job for
   the PR, in the PR's lane. Set them to Plan submitted.
   - If the user's request already said to fix the review ("fix and
     resolve"), that approves the findings that hold. Implement those.
   - A refuted finding, a design change, or a Legacy question still needs the
     user's answer first. Ask them all in one round, before the findings go on
     the board (plan-build-board's *question round*).

4. **Fix, test first.** For each finding, write a test that fails on the
   current code, then fix it, then run the PR's whole suite and build. Update
   the docs the change touches, and the board, in the same turn.

5. **Hand back for the commit.** Give the job review and the `git diff`
   commands. The user commits and pushes; you do not, unless told to in
   words. The threads must point at a pushed commit.

6. **Answer and resolve each thread**, once GitHub shows the fix as the PR's
   head. This must exit 0 and print the sha the replies name; on an error or
   another sha, stop and tell the user:
   ```bash
   gh pr view <n> --json headRefOid -q .headRefOid
   ```
   Then, per thread:
   ```bash
   gh api repos/<owner>/<repo>/pulls/<n>/comments/<comment-id>/replies \
     -f body='Fixed in <sha>. <what changed>. Test: <name> fails on the previous code.'
   gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"<PRRT_id>"}){thread{isResolved}}}'
   ```
   For a refuted finding, reply with the evidence instead, then resolve.

7. **Post the closing comment** with `gh pr comment <n> --body-file <file>`.
   It is the one record of what the review changed. **Never edit the PR
   description** (`gh pr edit --body…`), even when it lists changes or tests,
   or has gone stale. The comment carries that instead:
   - first line: `**Response to the review: <N> findings fixed in <sha>; all threads resolved.**`
   - one numbered item per finding: its severity and one-line title, what
     changed, and a link to its thread;
   - **Tests:** which fail on the previous code, which are guards, and the
     new suite and build results (counts included);
   - **Observations, left as they are:** each with one line on why;
   - **Branch**, only when something moved since the PR was opened (a
     rebase, a retarget, dropped merge commits): what happened and its proof
     (`git range-diff`). Name any part of the description that is now stale
     instead of fixing it;
   - then the attribution line the session requires.

## Common mistakes

| Mistake | Instead |
|---|---|
| Resolving a thread before the fix is pushed | Wait for the push; the reply names the commit |
| Fixing an observation the review said was not a finding | Leave it, and say why in the closing comment |
| One merged proposal for several findings | One proposal per finding; a job groups them |
| Committing or pushing to resolve faster | Ask the user; "fix and resolve" is not permission to commit |
| Claiming a test proves the fix without running it on the old code | Edit the fix out, run the test and quote the failure, then edit the fix back. Never `git stash` |
| Adding a "Review fixes" section to the PR description, or fixing a stale line in it | Leave the description as the author wrote it; put it all in the closing comment |
