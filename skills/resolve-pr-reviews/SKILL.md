---
name: resolve-pr-reviews
description: Use when a pull request has review comments to deal with, from AI reviewers (claude[bot], Copilot, CodeRabbit, Gemini…) or from people, or the user asks to fix, address, answer or resolve a PR's review comments (e.g. "fix the review on #1188", "address copilot's comments", "resolve alice's review", "fix claude's review").
---

# Resolving PR reviews

## Overview

Reviewers leave inline threads, a summary on each review, and sometimes plain PR
comments. Each item is checked against the code: a finding that holds becomes a task
with a written proposal and is fixed with a failing test first. Each thread is answered
on its own. The work ends with one top-level PR comment saying what was done. The PR
description is never edited; that comment is where the review's changes are recorded.

**REQUIRED SUB-SKILL:** the `plan-build-board` skill. Its seven-heading
proposal, question round, board updates and "never commit" rule apply here unchanged.

**AI or person.** A thread's reviewer is an **AI reviewer** when GraphQL gives its author
`__typename: "Bot"` (claude, copilot-pull-request-reviewer, coderabbitai,
gemini-code-assist…), or when the user calls it one. Anyone else is a **person**. The two
are handled differently in steps 2 and 6.

## Steps

1. **Read every review.** Fill in `<owner>`, `<repo>` and `<n>`:
   ```bash
   gh api graphql -F owner=<owner> -F repo=<repo> -F n=<n> -f query='
   query($owner:String!,$repo:String!,$n:Int!){repository(owner:$owner,name:$repo){pullRequest(number:$n){
     author{login}
     reviewThreads(first:100){totalCount nodes{id isResolved isOutdated path line originalLine
       comments(first:50){nodes{databaseId author{login __typename} body}}}}}}}' \
     --jq '.data.repository.pullRequest | "author: \(.author.login)", "threads: \(.reviewThreads.totalCount)",
       (.reviewThreads.nodes[] | select(.isResolved | not) | {id, path, line: (.line // .originalLine),
        outdated: .isOutdated, by: .comments.nodes[0].author.login, kind: .comments.nodes[0].author.__typename,
        reply_to: .comments.nodes[0].databaseId, thread: [.comments.nodes[] | "\(.author.login): \(.body)"]})'
   gh pr view <n> --json reviews,comments \
     --jq '{reviews: [.reviews[] | select(.body != "") | {by: .author.login, state, body}],
            comments: [.comments[] | {by: .author.login, body}]}'
   ```
   The first command lists the open threads: the `PRRT_…` id to resolve, the
   `reply_to` comment id to answer, and the **whole thread**, because the reviewer may
   have answered the author since. Their latest word is what counts. If `threads:` is
   over 100, stop and say so; the list is cut. The second command gives review
   summaries and plain PR comments. Points in them that have no thread are answered in
   the closing comment.

   **Which items are in scope.** If the user named reviewers ("copilot's review",
   "alice's comments"), only theirs. Otherwise every open thread and review point from
   anyone but the PR's author; the author's own threads are left alone. Say the count per
   reviewer in one line before going on.

2. **Sort and verify each item against the code.** Read the cited lines (for an
   `outdated` thread, the code may already have moved on) and run a probe or test where
   you can. Each item is one of:
   - **Finding**: says something is wrong. It **Holds**, is **Refuted**, or is **By
     design**, with the evidence. An outdated finding already fixed by a later commit is
     **Already fixed in `<sha>`**.
   - **Question**: asks something. Answer it from the code; it changes nothing unless the
     answer shows a finding.
   - **Suggestion or nit**: optional by its own words ("nit", "consider", "optional",
     an AI's "observation, not a finding"). An AI's is noted and left. A person's goes
     into the question round with your recommendation.
   - A `suggestion` block is the reviewer's proposed fix. Check that it still applies and
     is right before using it.

   A point in a review summary or a PR comment is sorted the same way; it just has no
   thread, so it is answered in the closing comment. **Already fixed** needs the commit
   on the PR's head: `git merge-base --is-ancestor <sha> origin/<head-branch>` exits 0.

3. **Write the proposals.** One per finding that holds, under the seven headings (issue,
   why, fix, gain, effort, risk, legacy). If a board exists for this work, add each one as
   a task and group them into one job for the PR, in the PR's lane. Set them to Plan
   submitted.
   - If the user's request already said to fix or address the review ("fix the review",
     "address alice's comments", "fix and resolve"), that approves the findings that
     hold. Implement those. "Resolve" in it also answers the round's resolve question
     for people's fixed threads, never for their questions or refuted findings.
   - Ask everything else in **one round**, before the findings go on the board
     (plan-build-board's *question round*): a design change, a Legacy question, each
     person's suggestion or nit, how to answer a person whose finding you refute, and
     **whether to resolve people's threads** (recommend leaving them for the reviewer to
     resolve, unless the user or the repo's habit says the author does), and whether to
     re-request their review after the push.

4. **Fix, test first.** For each finding, write a test that fails on the current code,
   then fix it, then run the PR's whole suite and build. Update the docs the change
   touches, and the board, in the same turn.

5. **Hand back for the commit.** Give the job review and the `git diff` commands. The
   user commits and pushes; you do not, unless told to in words. The replies must point
   at a pushed commit.

6. **Answer each thread**, once GitHub shows the fix as the PR's head. With nothing to
   fix (only questions, refuted or already-fixed items), answer straight after the
   round. Otherwise this must exit 0 and print the sha the replies name; on an error or
   another sha, stop and tell the user:
   ```bash
   gh pr view <n> --json headRefOid -q .headRefOid
   ```
   Then, per thread:
   ```bash
   gh api repos/<owner>/<repo>/pulls/<n>/comments/<reply_to>/replies \
     -f body='Fixed in <sha>. <what changed>. Test: <name> fails on the previous code.'
   gh api graphql -f query='mutation{resolveReviewThread(input:{threadId:"<PRRT_id>"}){thread{isResolved}}}'
   ```
   | Thread | Reply | Resolve |
   |---|---|---|
   | AI reviewer, any outcome | the fix, the evidence it is refuted or by design, or for an observation `Left as is: <why>` | yes |
   | Person, fixed or already fixed | the fix | only if the round said so |
   | Person, question | the answer | no, the reviewer resolves it |
   | Person, refuted or by design | the evidence, worded as the round agreed | **never**, the reviewer decides |
   | Person, suggestion or nit declined | the reason, as the round agreed | no |

   Name people by login without `@` in every reply and comment, unless the user asked to
   notify them.

   Re-request a person's review only if the round said so:
   `gh pr edit <n> --add-reviewer <login>`.

7. **Post the closing comment** with `gh pr comment <n> --body-file <file>`. It is the
   one record of what the reviews changed. **Never edit the PR description**
   (`gh pr edit --body…`), even when it lists changes or tests, or has gone stale. The
   comment carries that instead:
   - first line: `**Response to the review: <N> fixed in <sha>, <M> answered, <K> left open for their reviewers.**`
     **Fixed** counts what this round changed; **answered** counts every other item
     replied to (already fixed, questions, refuted, declined); **left open** counts
     threads not resolved.
   - one section per reviewer (login in backticks), with one numbered item per item in scope: its severity or
     kind and a one-line title, what changed or the answer, and a link to its thread;
     review-summary and PR-comment points with no thread are answered here;
   - **Tests:** which fail on the previous code, which are guards, and the new suite and
     build results (counts included);
   - **Left as they are:** each AI observation and each declined suggestion, with one
     line on why;
   - **Branch**, only when something moved since the PR was opened (a rebase, a
     retarget, dropped merge commits): what happened and its proof (`git range-diff`).
     Name any part of the description that is now stale instead of fixing it;
   - then the attribution line the session requires.

## Common mistakes

| Mistake | Instead |
|---|---|
| Resolving a thread before the fix is pushed | Wait for the push; the reply names the commit |
| Resolving a person's thread on your own, or one you refuted | Reply, and leave it to them unless the round said to resolve |
| Reading only a thread's first comment | Read the whole thread; the reviewer's latest word counts |
| Fixing an AI observation the review said was not a finding | Leave it, and say why in the closing comment |
| Skipping a person's nit without asking | Put it in the question round with your recommendation |
| One merged proposal for several findings | One proposal per finding; a job groups them |
| Committing or pushing to resolve faster | Ask the user; "fix and resolve" is not permission to commit |
| Claiming a test proves the fix without running it on the old code | Edit the fix out, run the test and quote the failure, then edit the fix back. Never `git stash` |
| Adding a "Review fixes" section to the PR description, or fixing a stale line in it | Leave the description as the author wrote it; put it all in the closing comment |
