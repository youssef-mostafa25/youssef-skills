---
name: plan-build-board
description: Use when the user says to start a job, take one on, move onto the next task, job or PR, work through a set of tracked issues, or asks for a plan before implementation — any piece of work with more than one task, where each task needs its own written proposal approved in words before any implementation file is touched, tracked on a published status page. Large plans can be split into a stacked PR, only if the user agrees.
---

# Plan Build Board

## Overview

The work is tracked on a **board**: every task gets its own proposal, approved before
any implementation file is touched, on a published HTML page updated in the same turn
as every status change.

A **job** is a group of tasks from the Queue that are implemented together, in one
sitting, as one change the user can read, understand and review afterwards. Grouping
pays for the reading once and turns several small diffs into one coherent one.

A **PR plan** sits above jobs: which pull request each job lands in. Every board has
one, drawn on its **PRs tab** with a copyable config per PR. It is one of these shapes
(see *PR plan*):

- **One PR**: every job in a single PR.
- **Independent PRs**: several PRs, each branching from the base and targeting it, in any
  merge order.
- **A stack**: an ordered chain of PRs, each targeting the branch of the one below it. It
  exists only when the plan is big enough to split cleanly **and the user chose it**
  (see *Stacked PRs*).
- **A mix**: one or more stacks alongside independent PRs.

```
PR plan (always) --> PR 1, PR 2, ... (each independent or stacked) --> jobs --> tasks
issues (when any task comes from one) --> tasks          shown on the Issues tab
```

**Issues.** When any task comes from a tracked issue (GitHub, Jira, Azure DevOps…), the
board has an **Issues tab** tracing every issue to its tasks, jobs and PRs, and the Jobs
and Queue tables carry an **Issue** column. See *Issues*.

**Questions first, board second.** Every question the plan needs is asked in **one round,
before the board exists**: which tasks are in, every Legacy decision, every choice between
approaches, every lane exception, the stack. The board is built from the answers, so
**every task on it is ready to implement: the only thing it still needs from the user is
approval.** A task that still needs an answer is not on the board yet.

**The rule: nothing is implemented until the user says yes, in words, to that specific
task** — naming the task, or naming the job or PR that contains it. A thumbs-up on another
task or job, silence, or your own confidence that the fix is obvious are not approval.

**Plan as much as the user asks for; implement at most one job before they review it,**
unless the user explicitly lifts that cap.
"Next task" plans one task, "next job" one job, "next PR" every job in the PR. See *Plan
scope*.

## When to use

- The user says "start a job", "onto the next task", "onto the next job", "onto the next
  PR", "let's work on X", "plan this out". No board yet → investigate, ask every question
  in one round, then build the board (steps 1–3b), then present at the scope they asked
  for (*Plan scope*). A board exists → take the next
  task, job or PR from its Jobs tab. A board with no Jobs tab (made before jobs) → run step 3 on
  it first, adding the Jobs panel and the Job column from `template.html`. A board with
  jobs but no PRs tab (or the older Stack tab) gets step 3b at the next job boundary,
  adding the PRs panel from `template.html`. A board with tasks from issues but no
  Issues tab gets one at the next job boundary, with the Issue columns (*Issues*).
- Any work with 2+ tasks that will be worked over more than one turn.
- The user asks for a plan, or asks what is wrong with something and what it would take to fix.

**Not for:** a single-file edit the user directly asked for, answering a question, or
work already approved on an existing board (update that board instead of making a new one).

## The loop

```
user says "start a job" / "take the next job"
  |
  v
1 INVESTIGATE (read-only) + DRAFT the tasks, jobs and PR plan (nothing published)
  |
  v
2 ASK EVERY QUESTION, IN ONE ROUND --> STOP until every one is answered
  (task list, Legacy, approach choices, lanes, the stack; follow-ups in one more round)
  |
  v
3 PUBLISH THE BOARD from the answers: every task ready, decisions on its row
  (Jobs tab, job on each Queue row)
  |
  v
3b PR PLAN on the PRs tab (shape + config per PR), the stack as the user answered
  |
  v
4 PRESENT at the scope the user asked for (Plan scope):
  next task: one proposal | next job: job header + one proposal per task
  next PR: every job's header + one proposal per task, in PR order
  + move those tasks to "Plan submitted" (same turn)
  |
  v
5 STOP and wait --(user approves the PR, jobs or tasks, in words)--> Approved
  |                                                                 |
  |<--(task rejected)-- back to Open, out of the job                v
                                           6 IMPLEMENT ONE job's approved tasks together
                                             (one task, in task scope). Never two jobs
                                             unless the user lifted the cap in words.
                                                                    |
                                                                    v
                                           7 VERIFY each task --> Fixed
                                                                    |
                                                                    v
                                           8 REVIEW in chat + on the Jobs tab, then STOP
                                             (board updated in the SAME turn as each move)
                                                                    |
                                                    was that the PR's last job?
                                              no: approved jobs left --> wait for the
                                                  user's go after the review --> 6
                                              no: none approved --> wait for next task /
                                                  job / PR --> 4
                                              yes v
                                           9 PR HANDOFF: body on the PRs tab (copy button),
                                             the short fields + next branch name in chat;
                                             branch check before the next PR's first edit
```

**Step 1 — investigate.** Read anything. Run read-only checks: greps, a throwaway probe
in the scratchpad, a suite that already exists. Do **not** edit a file the fix would
touch, and do not leave scratch files in the repo. Plan against the code, not against
what the user told you — if the premise does not hold, say so instead of proposing a fix.
Record each task's **origin**: the issue and the part of it the task covers, or, with no
issue, where it came from (a side catch while checking task NN, the user's request on a
date, a PR review). Read this repo's section of the **lanes file** (*Lanes*) to know which
directories the user lets you edit without asking. Read each issue's title and state from the tracker
(`gh issue view <n> --json title,state`), never from memory. Investigate **every** task
deeply enough to write its proposal, because its questions must surface now, not when its
turn comes. Then draft, without publishing: the task list, the jobs (*Forming jobs*) and
the PR plan (*PR plan*). Collect every question the draft leaves open.

**Step 2 — ask every question, in one round.** One message, before anything is
published (*The question round* below). Stop until every question has an answer. If an
answer opens a new question, ask it, and anything else it touches, in one more round.
Never publish the board with a question still open.

**Step 3 — publish the board.** Build it from the answers: the task list as decided, and
each task's decisions on its row (*The question round*). Tasks start at `Open`. Give the
user the link once. Split the Queue into jobs using the rules in *Forming jobs* below.
Fill the Jobs tab and the Job column on the Queue. Rank jobs, not just tasks. Effort and
risk for jobs not yet presented are provisional — mark them `~M · ~Low` until their
proposals are written. If any task comes from an issue, fill the Issues tab and the Issue
columns in the same publish (*Issues*).

**Step 3b — PR plan.** Put every job in a PR and fill the PRs tab, following *PR plan*
below. Each PR gets its shape (`Independent` or `Stacked`) and its config from the start.
For one PR or independent PRs, say the layout in one line in the question round; the
user may change it. If the plan also passes *Does it qualify*, the stack proposal is one
of the round's questions, so it is settled before the board is published.

**Step 4 — present at the user's scope** (*Plan scope*): one task, one job, or every job
in a PR. A job starts with the job header (below), then one proposal per task in it, in
chat, under the seven headings. Every decision in it was made in the question round, so
the proposal states the answers and asks nothing. Never one proposal covering several tasks — the board
tracks tasks, and a merged plan leaves the others with no recorded decision. In the same
turn, set every presented task to `Plan submitted` with its effort and risk letters on
the row, and each job whose tasks are all presented to `Plan submitted`.

**Step 5 — stop.** The user may approve a whole PR or job in one reply ("approve PR 1",
"approve job B") or task by task. Approval is the only thing left to ask here: Legacy,
lanes and approach choices were answered in the question round. A task they reject or
park leaves the job (back to `Open`, or `Deferred`) and the job goes ahead without it;
re-check that the rest still makes sense together. If the user changes a decision while
approving, update the task's row and proposal before implementing it.

**Step 6 — implement one job.** All of the job's approved tasks, in the order the job
header gave; in task scope, the one approved task. **Never more than one job before the
user has its review**, even when a whole PR is approved, unless the user lifted the cap
(*Plan scope*). Every hunk belongs to exactly one task — no edit that serves none of them,
no "while I was here" cleanups. Reviewability is the deliverable.

**Step 7 — verify before claiming Fixed.** Run the checks for each task and quote what
they printed. Not after writing the code — after proving it.

**Step 8 — review, then stop.** Hand the change back in the shape in *Job review* below
(for one task, in task scope; all of them in one message when the user lifted the cap),
and put its one-line version in the job's Review cell. The
job reaches `Fixed` when every task in it has. End with what comes next and stop: "Next:
Job C (tasks 04 05), plans approved. Say go to implement it." or "Say next task / next
job / next PR to plan more."

**Step 9 — PR handoff.** When the job just reviewed was the last one in its PR, stacked
or independent, hand the PR over in the shape in *PR handoff* below, in the same turn as
the job review.

## The question round

Every question the plan needs, **asked once, before the board is published**. It is the
only time anything but approval is asked of the user.

**What goes in it**, every item the draft leaves open, numbered, grouped by task:

1. **The task list.** Each task in one line with its origin. Say which you would leave
   out (refuted, by design, out of scope) and why. The user confirms, adds or drops.
2. **Legacy**, per task (*Heading 7*): what is in reach, what is lost without it, your
   recommendation.
3. **Approach choices.** Wherever two fixes are defensible: your recommendation, the
   alternative, and what changes with the answer.
4. **Lanes** (*Lanes*). No section for this repo in the lanes file → the one-time lane
   setup. Then, per job, every directory it reaches that is an **ask-first** lane, and
   every directory in neither list (also asking which list it joins). Free lanes are
   never asked.
5. **The PR plan.** The layout in one line, and the stack proposal when it qualifies
   (*Stacked PRs*).
6. **Anything else** a task would otherwise stop on: a value to use, an owner to ask, a
   behaviour to keep.

One message, in the sha3bolly style, each question with your recommendation so the user
can answer "go with your picks". `AskUserQuestion` fits only when four questions or fewer
cover everything. A plain numbered list is otherwise right.

**Ready means** the fix is one approach with no "or", every file it edits is named, its
lane is cleared, its Legacy is decided, and its verification is named. A task the user
cannot answer for yet (waiting on another team, a product call) stays off the board; say
in chat what it waits on, and it joins the board through its own round when that
arrives.

**Record the answers on the board.** Each task's row on the Tasks tab carries its
decisions in its Evidence / decision cell ("Legacy: drop (user, 2026-10-29) · lane: also
`web/` · approach: guard in the handler"), and the proposal states them.

**Later tasks get a round too.** A task found after the board exists (a side catch, a
review comment) gets its questions asked before it is added. An existing board with tasks
still carrying open questions gets one round for all of them at the next job boundary.

## Plan scope

What the user says sets how much is **planned** at once. It never changes how much is
**implemented** at once: one job, at most.

| The user says | Step 4: present | Step 6: implement after approval, then stop |
|---|---|---|
| "onto the next task", "next task" | **One task**: the next task (below). One context line (`Task 03 · Job B, 2 of 3, after 01 · files: …`), then its proposal. | That task. Its review, then stop. |
| "onto the next job", "next job", "start a job", "take the next job" | **One job**: the job header, then one proposal per task. | That job. Its review, then stop. |
| "onto the next PR", "next PR", "plan the whole PR" | **One PR**: a line naming the PR and its jobs, then, per job in PR order, the job header and one proposal per task. | **The PR's first job only.** Its review, then stop. |

**What "next" is.** Work stays inside the current PR, in PR plan order, then each job's
header order, until that PR's handoff; then the next PR in the plan. The next task, job
or PR is the first one there not yet `Fixed` (or `Refuted`, `By design`, `Deferred`,
`Assigned out`). The Jobs tab's rank never pulls a job out of another PR forward.

**"Next" on work already approved means implement, not re-present.** If the next task or
job is already `Approved` (its plan came with a PR), "next task", "next job", "go" or
"continue" implements it, capped as below. A unit with no approved plan gets its proposal.

**Unclear wording** ("carry on", "next") with nothing approved waiting: use the scope the
user last used on this board, a job if none, and name it in the first line ("Planning
the next job, Job C. Say next task or next PR to change it.").

**Approval covers only what was presented.** "Approve PR 2" approves the PR 2 tasks whose
proposals the user has seen, not the rest. In the question round, one answer may cover
several questions when it names them or says "all" ("all legacy: drop it").

**The cap: one job, then the user reviews.** After every job (every task, in task scope),
give the review and stop. The next job is implemented only when the user, having had the
review, says to go on in words: "go", "next job", "continue", or an approval of the
review ("looks good", "lgtm"). Plans the user
approved earlier, for a whole PR, are approval of those tasks, not this go: each further
job of the PR still waits for it. In task scope, the next task waits for "next task".

**Only the user lifts the cap**, explicitly and only as far as they say. "Implement all of
PR 1 without stopping" covers PR 1's approved jobs, not PR 2. Even then, work job by job:
the board moves per job, each job gets its own job review, and they are handed back in job
order in one message at the end. A question that surfaces during implementation was
missed in the round: hold that task at `Approved`, with any task that depends on it, and
the rest goes on; the final message asks it and lists what was held. A failed branch
check stops the whole run.

**Task scope inside a job.** The job header's order still holds. When a task closes out its
job (the last one to reach Fixed), the review also gives the job's one-line review for
its Review cell; if that was the PR's last job, the PR handoff follows in the same turn.

## Forming jobs

A job is a set of Queue tasks that **share the reading and tell one story in the diff**.
Put tasks in the same job when they:

- touch the same files or the same seam (one module, one request path, one component), or
- are the same kind of fix in neighbouring code (the same missing guard in three handlers).

Keep a job reviewable in one sitting:

- **One lane.** A job does not cross a service boundary. Backend and frontend fixes
  for the same symptom are two jobs, the first noted as unblocking the second.
- **About five tasks or fewer**, and a diff a reviewer can read top to bottom.
- **A High-risk or L-effort task is a job of its own.** Its rollback plan and real-data
  check must not be buried in someone else's diff.
- **A task waiting on a decision** is not on the board. Design decisions are asked in
  the question round; one that waits on someone else keeps the task off the board
  (*The question round*).
- **A task that fits nowhere is a job of one.** Never force a group.

**Rank jobs** by the highest-ranked task in each. Pulling a lower-ranked task forward
because it shares files with a top task is the point of a job — mark it on the Queue row
("pulled into job A") so the user sees why the order moved.

### The job header

Before the task proposals, in chat:

1. **Tasks** — the task numbers and one line each.
2. **Why together** — the files or seam they share, concretely.
3. **Files touched** — every file the job will edit.
4. **Order** — the order the tasks will be implemented, and why if it matters
   (task 05's guard first so 01's change has a non-empty list to work on).
5. **Effort · Risk** — of the job as a whole: the highest of its tasks, plus anything the
   combination adds.

### Job review

After implementation, before anything else, give the user what they need to review the
change without re-deriving it:

1. **What changed, per task** — task number → `file:line` ranges it touched, one line on
   what each hunk does. A hunk that serves two tasks is listed under both and said so.
2. **Read it in this order** — the file or hunk to start from, and the path through the
   rest.
3. **Proof** — per task, the check that was run and what it printed.
4. **Review commands** — the work is uncommitted, so give `git diff -- <files>` for the
   job. Where a file belongs to one task, list that command under the task so it can be
   read alone; where tasks share a file, the line ranges from item 1 mark whose hunk is
   whose.
5. **What did not change** — anything the user might expect to be touched and was not, and
   any task that left the job.

## Issues

**If any task comes from a tracked issue, the board has an Issues tab, and the Jobs and
Queue tables each have an Issue column.** A board where no task comes from an issue has
neither.

**The Issue column** (Jobs and Queue): the issue number, linked, for each task the row
covers, or `none` with the origin in a few words ("none (PR 5 review)").

**The Issues tab**, top to bottom:

1. **Warnings**, in a `note warn`, when either holds: an issue is closed on the tracker
   but its bug still reproduces, or a PR body closes an issue it does not fully cover.
   For the closed one, say so in chat too and give `gh issue reopen <n>` for the user to
   run; PR bodies use `Refs #n` for it until it is reopened.
2. **One section per issue**: the number linked, the title, and the state as the tracker
   shows it now. A row per task: task, status pill, the part of the issue it covers (its
   item number when the issue lists items), job, PR. Under the table, one line: which PR
   closes the issue, or "no single PR closes it" and what is left.
3. **An issue in scope with no task** (closed as intended, refuted): its section with one
   line on why.
4. **No issue**: every task that traces to none, with its origin.

**Closing keywords.** A PR body says `Closes #n` only when that PR finishes every remaining
part of #n: each of its tasks is Fixed or decided, and the issue has no open question.
Otherwise it says `Refs #n`, and the issue's section says what is left. The PRs
overview's Issues column says, per issue, whether the PR closes or addresses it.

**Keep it current.** Re-read each issue's state at every PR handoff and whenever the user
says a PR was opened or merged. A change (closed, reopened, a comment that adds a
question) updates its section in the same turn. An issue that would close while part of
it is still open is said in chat too, with the fix: change the keyword to `Refs #n`.

## PR plan

Every job belongs to exactly one PR, and every PR is on the PRs tab. **The tab is never
deleted**, whatever the shape: one PR or four independent ones get it just as a stack does.

**Choosing the shape.** Default to **one PR**. Split into **independent PRs** when the
jobs don't depend on each other and one PR would be too big to review in one sitting
(the same size bar as *Does it qualify*), or when it would mix unrelated areas that
different people review. Propose a **stack** only when *Does it qualify* holds. One PR
and independent PRs are your call, so state the layout in one line. A stack is the
user's call.

**What the PRs tab shows**, per PR, from the moment the plan exists:

1. **Shape pill**: `Independent` (branches from the base, targets the base) or `Stacked`
   (targets the PR below it in its chain).
2. **Status pill**, progress (jobs Fixed / jobs in it), branch → target, sync line, its
   jobs.
3. **Config**, every field with its own Copy button: head branch, target, title, the
   create command (`git switch -c <branch> --no-track origin/<base>` for an independent PR
   or PR 1 of a stack; `git switch -c <branch> --no-track` from the PR below for a stacked
   one), draft, merge method. The **body** is added at handoff (*PR handoff*).
   **Every create command carries `--no-track`, with no exceptions.** Without it, a branch
   started from `origin/<base>` gets `<base>` as its upstream, and the user's next push or
   editor Sync lands the PR's commits directly on `<base>` instead of in a PR targeting it.

Above the PRs, an **overview table** lists every PR with its shape, branch → target,
what it builds on ("—" for independent), its jobs, and the issues it closes or addresses
(*Issues*). Then each
**chain** is drawn under its own base line: a stack is one chain with each PR under the
one it targets, and an independent PR is a chain of one. Under the overview, give one
line per PR saying why it is independent or what it builds on.

**Branch check, every PR.** Before the first edit of each PR, run
`git branch --show-current`, `git status --short` and
`git rev-parse --abbrev-ref @{upstream}`. You should be on that PR's branch with a clean
tree, and its upstream must be **none** (not pushed yet) or `origin/<its own name>`. An
upstream naming any other branch, the base above all, is a stop: say so at once and give
`git branch --unset-upstream`, before any edit and never only in a handoff. If anything
else is off, stop and say what. Never carry one PR's uncommitted work into another PR's
branch, stacked or not.

## Stacked PRs

A stack splits a large plan into a chain of PRs a reviewer can take one at a time. PR 1
targets the base branch, PR 2 targets PR 1's branch, and so on. **Whether to stack is the
user's decision.** You propose it, they choose. Without a yes in words there is no stack.

### Does it qualify

Propose a stack only when **both** of these hold:

1. **Big enough.** Three or more jobs, or a total change one reviewer could not read in
   one sitting (roughly 400+ changed lines or 15+ files). Two small jobs are one PR.
2. **Splits cleanly.** There is an order where every PR builds, passes its tests and
   makes sense if merged alone, and later PRs build on earlier ones. Natural cuts are
   foundation then consumers, backend then frontend, refactor then feature, migration
   then the code that uses it.

It does **not** qualify when the jobs don't depend on each other. Those are independent
PRs, not a stack; say so in one line if it helps. It also does not qualify when every cut
leaves a PR that breaks the build until a later one lands.

Rules for the cuts:

- **A job belongs to exactly one PR.** Never split a job across PRs. If a cut wants to go
  through a job, re-form the jobs.
- **One to three jobs per PR**, ordered by dependency first. Inside a PR, jobs keep their
  rank order. The stack order overrides job rank, so say when it moves a job.
- **A High-risk job may get a PR of its own**, so it can be reverted alone.

### Proposing it

One message, then stop:

1. **Why a stack**: one sentence on the size, and the dependency that gives the order.
2. **Per PR**: number, proposed title, proposed branch, target branch, its jobs with their
   task numbers, and one line on why the cut is there.
3. **The drawing**: base branch at the top, each PR indented under the one it targets:

```
main
 └─ PR 1  auth-cleanup/1-token-model   Jobs A, B   tasks 01 03 | 02
     └─ PR 2  auth-cleanup/2-api-guards   Job C       tasks 04 05
         └─ PR 3  auth-cleanup/3-ui-states   Jobs D, E   tasks 06 | 07 08
```

4. **Ask**, in the question round: stack it like this, change the cuts, or keep it as
   one change. No default.

Branch names follow the repo's convention, which you can see in `git branch -a` and recent
merges. With no convention, use `<topic>/<n>-<slug>`. PR 1's branch can be the branch the
user is already on.

**Approving a job is not approving the stack**, and approving the stack approves no task.
If they say no, record "No stack — declined" in the header meta, redraw those jobs as one
`Independent` PR on the PRs tab (or the split the user asked for instead), and don't ask
again unless the plan grows by half or more. If they say yes, mark those PRs
`Stacked` on the PRs tab, redraw them as one chain with each PR under the one it targets,
update their targets and create commands, and publish the board with the stack on it.

### Working a stack

- **Jobs are implemented in PR order.** No edit for a PR N+1 job until PR N has had its
  handoff and the branch check below has passed. Proposals for later jobs may be
  presented early. Implementing them may not start early.
- **Each PR must stand alone.** Before the handoff, run the suite that covers the whole
  PR, not only each task's check, and quote it.
- **Branch check** (see *PR plan*). In a stack, a clean tree on PR N+1's branch also
  means PR N's work is committed on its own branch. Run the base probe (below) in the
  same check.
- **Taking a finished stack through Claude's review.** Once every PR is complete, tested
  and opened, and the user asks to put the stack through Claude's review (rebase each PR
  on its base, push, then resolve the review), run `youssef-skills:integration-assistant` in its
  *Review loop mode*. The user asking for this is their request for a rebase. Update each
  PR's sync line and review tasks on the board as the loop goes.

### When the base moves

**Default: leave the stack alone.** New commits on `main` need no action by themselves.
Only PR 1 targets it, and GitHub only needs PR 1 to merge without conflicts. Sync only
when one of these is true:

- PR 1 conflicts with the base, on GitHub or in the probe below,
- the repo requires branches to be up to date before merging,
- the stack needs something that landed on the base,
- a PR in the stack landed by squash or rebase merge (see the table).

**Sync by merging, one PR at a time.** A merge rewrites nothing, so there is no
force-push and review comments stay attached. Rebase only when the user asks for it, in
words, and then still one PR at a time: never one command that rebases the whole stack
(`git rebase --update-refs`). Every sync link, merge or rebase, goes through
`youssef-skills:integration-assistant` in its *Stack mode*. Load it and follow it.

**The base probe** is read-only, so run it at every branch check:

```
git fetch origin
git rev-list --count <PR 1 branch>..origin/main         # how far main has moved
git merge-tree --write-tree origin/main <PR 1 branch>   # exit 1 = conflict (git 2.38+)
```

Report it in one line, such as "main is 7 commits ahead of PR 1 and merges cleanly, no
action needed", and put it on that chain's base line on the PRs tab. A clean probe is not a reason
to sync. On older git, use integration-assistant's dry-run in a detached worktree instead.

| What happened | What to do |
|---|---|
| The base moved and a sync is needed | 1. **Base merge**: merge the base into PR 1, a full integration-assistant run. 2. **Propagate** bottom-up: PR 1 into PR 2, PR 2 into PR 3, each a stack-mode propagation run. |
| PR N landed with a merge commit | Retarget PR N+1 to the base. GitHub does this itself when PR N's branch is deleted on merge. Nothing to merge. |
| PR N landed by squash or rebase merge | The base now has PR N's changes under new commits, so PR N+1's diff shows them again. Merge the base into PR N+1 as a propagation run, where the known change is PR N as it landed. Then retarget. Keep PR N's branch until this is done, because the run compares against it. |
| Review changed PR N after PR N+1 started | If PRs below N, or N itself, are due a sync, sync up to and including PR N first (*A new commit mid-stack*). Then add the commit to PR N, then propagate PR N into PR N+1 and upward. The known change is PR N's new commits. |
| The user moves the stack to a new base | Base merge of the new base into PR 1. The user retargets PR 1, then propagate. |

- **One PR at a time, bottom-up**, for merges and rebases alike. A link is done when its
  merge (or rebase) is verified and the user has committed it. The user commits and
  pushes; you never push. Don't start the next link before that.
- **A new commit mid-stack.** When a PR in the middle needs a new commit (a review fix,
  a fix the sync's own checks called for, new work), the order is fixed:
  1. sync every PR below it and then that PR itself, one link at a time, each verified
     and committed;
  2. add the new commit to that PR, as its own commit on top of the sync, verified and
     committed;
  3. then sync the PRs above it, one link at a time.
  Never put the commit on a PR that is still waiting for its sync, and never sync a PR
  above it before the commit is in. Folding the fix into the sync commit is wrong too:
  the sync stays one commit and the fix another.
- **Verify every link, even the easy ones.** Knowing what changed shortens the analysis,
  not the checks. Run the dry-run, the clean-but-dangerous scan, the PR's whole suite, and
  the task checks from that PR's job reviews, and quote what each printed.
- **Stop the cascade on any failure** and say which link it stopped at. Links above it
  stay as they were. If the fix is a new commit in that PR, it follows *A new commit
  mid-stack*: the sync is committed, then the fix, then the cascade goes on.
- **Recommend merge commits for landing, when the repo allows them.** A squash or rebase
  landing forces a propagation run on every PR above it. If the repo allows no merge
  commits (*PR handoff*, Merge method), say so when the stack is proposed in the question
  round: each landing then costs a sync of every PR above it.
- **Board, same turn.** Each sync updates the PR's sync line on the PRs tab: the base
  commit it is synced with, what was merged, the decisions and the checks run. If a merge
  changed what a PR does, update its Body config and tell the user to edit the PR.

### PR handoff

Every PR gets a handoff, stacked or independent. **The body goes on the board, never in
chat.** Write the full PR body into the PR's config on the PRs tab, where its Copy button
copies it, and republish. Do not paste the
body into the response, not even a shortened one. Chat carries the short fields, each in
its own fenced block so it can be copied alone, and points at the board for the body.
Nothing goes in a file unless the user asks.

~~~text
**PR 2 of 3 is ready: Guard empty token lists in the API layer**

Head branch
```
auth-cleanup/2-api-guards
```
Target branch
```
auth-cleanup/1-token-model
```
Title
```
Guard empty token lists in the API layer
```
Body: on the board, PRs tab → PR 2 → PR config → Copy
Draft: yes (PR 1 is still in review) · Merge method: merge commit · Labels: `bug` · Reviewers: (only what the repo shows; else leave out)

Next branch: PR 3 targets this one
```
auth-cleanup/3-ui-states
```
```
git switch -c auth-cleanup/3-ui-states --no-track
```
~~~

- **Title** follows the repo's PR/commit style (`git log --oneline`).
- **Body**: if the repo has `.github/pull_request_template.md` (or a `PULL_REQUEST_TEMPLATE`
  folder), fill that. Otherwise use these sections: *Summary* (1–3 sentences, then one
  `Closes #n` or `Refs #n` line per issue, chosen by the rule in *Issues*), *Stack*
  (PR n of N; the PR it depends on, by number once the user has given it, else by branch;
  the PR that builds on it; for an independent PR, "Independent: targets `<base>` and
  builds on no other PR"), *Changes* (per task: what and where, from the job reviews),
  *How to review* (read order), *Testing* (per task, the check and what it printed, plus
  the whole-PR suite), *Not in this PR*.
- **PR 1's body opens with the stack overview**, before its own sections. It is the
  first PR a reviewer sees, so it explains the whole stack: a *Stack overview* section
  with 2–3 sentences on what the stack does as a whole, then one line per PR giving its
  number, branch and responsibility, with PR 1 marked "this PR". Then PR 1's own body
  follows as usual. Later PRs keep only their own *Stack* line. If the cuts change after
  PR 1 is opened, update the overview on the board and tell the user to edit PR 1.
- Put the body in the PR's `pre.cfg-v` Body field,
  HTML-escaped (`&` `<` `>`) so the copied text is the exact Markdown. End it with any PR
  attribution line the session requires.
- **Labels and reviewers**: only when the repo shows them, through existing labels,
  CODEOWNERS or the user's past PRs. Never invent one. **Merge method**: what the repo allows, read once per board with
  `gh repo view --json mergeCommitAllowed,squashMergeAllowed,rebaseMergeAllowed`. Merge
  commit when it is allowed, so the PRs above need no propagation run when it lands (see
  *When the base moves*); otherwise squash, then rebase, whichever is allowed first. Never
  a method the repo disallows.
- **Draft: yes by default.** It is `no` only when one of these holds, and the reason goes
  next to it:
  1. **Every PR it builds on is merge-ready**: PR 1 … PR N-1 can each merge into its
     target as it stands, with nothing left to change. Their reviews are done (the user
     says so, or a read-only `gh pr view` shows approved with no changes requested) and
     the base probe is clean. PR 1 of a stack and every independent PR build on
     nothing, so they are `no` at their handoff.
  2. **The whole stack is complete**: every PR has had its handoff, so the stack can
     be merged in one go.

  Otherwise it is `yes`, naming what blocks it ("PR 1 is still in review"). **Re-check
  it when things move**: a PR it builds on gets approved or merged, a sync changes one, or the
  last PR's handoff completes the stack. When a PR can leave draft, say so in chat with
  the command in its own block (`gh pr ready <number>`, which the user runs) and update
  its Draft field on the board. A PR whose base PR gets new changes requested goes back
  to `yes`; tell the user (`gh pr ready <number> --undo`).
- **Next branch**: give the name and the create command of the next PR in the plan, and
  say the user should commit this PR's work first. For the next PR in a stack it branches
  from this one; for an independent PR it branches from the base
  (`git switch -c <branch> --no-track origin/<base>`). Leave it out when no PR is left.
  Tell the user the first push sets the branch's own upstream:
  `git push -u origin <branch>`.

In the same turn, set the PR to `Ready` on the PRs tab, fill its whole config there
(the body included), and republish before you reply, so the
board link already has the body when the user reads the reply. When
the user says they opened it, record the number and link. When it is merged, mark it
`Merged`, ask which merge method was used, and, in a stack, follow *When the base moves*
for the PR above it. Later PR bodies then refer to it by number.

PR statuses: `Planned` → `In progress` (its first task approved) → `Ready` (handed over) →
`Opened` (#n) → `Merged`. A PR's progress is jobs Fixed / jobs in it.

## The seven headings

Every proposal, in this order. Explain them in chat in the style below; the board carries
the one-line version.

| # | Heading | What goes in it | What makes it wrong |
|---|---------|-----------------|---------------------|
| 1 | **Issue** | What is wrong, in one or two plain sentences, for someone who has never opened the file. | Restating the user's own words back. Say what *you* found. |
| 2 | **Why it's an issue** | The mechanism, with `file:line` for every behaviour claim, and who notices — a user seeing an empty chart, an operator, a silent log nobody reads. | "This is unsafe" / "bad practice". If you cannot name a sequence of events that produces a wrong result, you have not found the issue yet. |
| 3 | **The fix** | What changes, in which files. The smallest change that does the job. Name what you are deliberately *not* changing. One recommendation if there are several approaches, not a survey. | A refactor riding along. Speculative abstraction. Restructuring surrounding code to suit the edit. |
| 4 | **What we gain** | The behaviour afterwards, stated as something observable: "reloading a summarised chat shows its charts again". | "Improves correctness". Benefits nobody can see or measure. |
| 5 | **Effort** | **S** — one file, one change, covered by an existing suite. **M** — a few files or one seam, needs a new test. **L** — crosses a service boundary, or needs a migration, a contract change or a design decision; name the decision. | An hours estimate. The letter plus the reason is what is wanted. |
| 6 | **Risk** | **Low** — blast radius is the thing being fixed. **Medium** — a shared path, so a mistake reaches other features; name a verification step beyond "tests pass". **High** — can destroy data, change a persisted shape, or move behaviour no test asserts; needs a rollback plan and a check against real data. | A risk level with no verification step attached. "Low risk" on a migration or a shared path. |
| 7 | **Legacy** | See below — this one has its own rule. | Leaving it out. Quietly adding a fallback and not declaring it. |

### Heading 7 — Legacy is the user's decision, never yours

**There is no default.** Do not assume the old path is removed, and do not assume it is
kept. Name the trade-off and hand it over:

1. **What legacy logic is in reach** — the old shape, name, column, route or code path,
   concretely, and where it is read or written.
2. **What we lose without it** — what breaks, and who sees it. "Chats summarised before
   the June change show no summary" is an answer; "some old data" is not.
3. **Your recommendation** — support it or drop it, and one sentence on why.
4. **Ask, in the question round.** The user answers before the board is published, and
   the proposal's Legacy heading states that answer. Nothing is implemented on this point
   without one.

"None — there is no legacy logic in reach" is a fine answer. "Not sure" is not; you read
the file, so you know.

## How to explain it in chat

The board is a **status board**. The reasoning goes in chat, written for a junior engineer:

1. **Plain words.** Short sentences. Define a term the first time you use it.
2. **Always a concrete example.** Real code, a real value, a real sequence — not theory.
   Not optional.
3. **A flowchart whenever the failure travels through more than one function**, as a
   simple ASCII flow: `A --(does X)--> B --(does Y)--> C`.
4. **Keep it small.** Short numbered steps, never one long block. Go deeper only when asked.

The `sha3bolly` skill ships in this plugin (`youssef-skills:sha3bolly`) and is the canonical
statement of this style — load it before writing the first proposal and follow it.

## Status lifecycle

| Pill | Means | Set it when |
|---|---|---|
| `Open` | Confirmed, nobody is on it. | The resting state. Also where a task returns if its plan is rejected. |
| `Plan submitted` | A proposal exists, waiting on the user. | The moment you present it. Put effort and risk on the row. |
| `Approved` | Approved, being implemented. | Only after the user approves in words. **The only status under which implementation files may be edited.** |
| `Fixed` | Changed, and the failure can no longer happen. | After verifying — not after writing the code. Say what you ran and what it printed. |
| `Partly fixed` | Some of it is done, the rest is not. | When scope was deliberately cut. Say which half is which. |
| `Refuted` | The mechanism was checked and does not hold. | Keep the row. A disproved issue that gets deleted is one the next reviewer finds again. |
| `By design` | Real behaviour, intended. | Same rule — keep it, with the evidence that it is deliberate. |
| `Deferred` | Real, confirmed, parked. | When the user parks a task rather than approving or rejecting. It leaves the queue, keeps its plan, and is **still an open exposure**. |
| `Assigned out` | Owned by someone else now. | Handed to another person or filed as an issue. Keeps its row and its plan. |

## Keeping the board current

**The row moves when the thing happens** — not at the end of a batch, not "once it is all
done". Every move updates **three things together**:

1. the **pill** on the row,
2. the **Evidence / decision** cell — what you did and what proved it, in 1–3 sentences,
3. the **tally in the header and the filter chip counts** — these are hand-maintained and
   will silently disagree with the rows if you skip them.

The **Queue** is maintained too: a task that reaches Fixed leaves it and the ranks close
up. If fixing one task changes another's priority, say so and re-rank. The **Jobs** tab
moves with it: a task leaving a job is removed from that job's row, and a finished job
keeps its row with its review. The **Issues** tab moves too: a task's pill there matches
its row, and a new task arrives with its origin, in its issue's section or under No issue.

**History goes on Before you start, never in the header.** The header meta sits above
every tab, so it says only where things stand now, one short line each: `Head` is the one
commit work is on, its branch and the tree state; `PRs` is the count and shape, plus at
most the one thing in progress. Overwrite those lines; never append to them. Every event
worth remembering (a plan approved, a job fixed or committed, a PR opened, reviewed or
rebased, a decision, a placement) gets one dated `<li>` at the **top** of the **History**
list at the bottom of Before you start, with the commit, PR or decision it produced, and
the summary count (`Show N entries`) goes up by one. The list stays collapsed. Per-PR
detail (tips, review threads, closing comments) belongs on the PRs tab, per-task detail in
the Evidence cell. When an existing board's header has grown a log, move its events into
History (newest first) on the next republish and cut the lines back to the current state.

**Republish to the same URL** (pass the artifact's `url`) so the link keeps working. If
the board and the code disagree, everyone downstream is working from the wrong map.

**Older boards carry older scripts.** A board keeps the `<script>` it was first built
with, so a template fix never reaches it by itself. Before every republish of an existing
board, search its script and markup for anything that opens a PR config: `.open = true`,
`lastDone`, `setAttribute("open"`, or an `open` attribute on a `details.cfg`. If any is
there, delete it and put the template's PR-config block in its place (the
`details.cfg` loop that sets `cfg.open = false`). Change nothing else in the script.

## Two standing checkpoints

**Lane / boundary.** Name every directory each job's fixes reach. A directory in the
user's **free** lanes needs no question. Every other one is **asked in the question
round**, per job, naming every directory (*Lanes*). Never edit outside the free lanes
and the exceptions the answers cleared. A small fix is not an exception; small is not
the criterion.

**Never commit.** Implementation lands **uncommitted** in the working tree. No
`git commit`, `git push`, `gh pr create`, amend or tag unless the user says so, in words —
and being told once is not permission for the next time. **A PR plan or a stack does not
change this.** A PR plan, or a yes to a stack, is not permission to commit, branch, push or open PRs. You give
the config and the branch names, and the user runs them. Permission covers only what the
user named: "create the branches for this stack" covers branches, not commits or pushes.

## Lanes

Which services the user lets you edit without asking differs per user and per repo, so
it is asked once and saved, never assumed. No directory is free by default.

**The lanes file** is `~/.claude/plan-build-board/lanes.md`, one section per repo. It lives
outside the repo and is never committed. The section key is the repo's `origin` URL
reduced to `host/owner/repo`: drop the scheme, any `user@`, a `:port` and a trailing
`.git`, turn the SSH `:` into `/`, and lowercase it, so
`git@github.com:Acme/Llumen.git` and `https://github.com/acme/llumen` are both
`github.com/acme/llumen`. With no `origin` remote, the key is the main worktree's
absolute path, `dirname "$(git rev-parse --path-format=absolute --git-common-dir)"`, so
every worktree of the repo shares one section.

The format (the directories are only an example, never defaults):

```markdown
## github.com/owner/repo
- free: agent/, shared/utils/
- ask: backend/, web/
- updated: 2026-11-12
```

- **free**: edit without asking, in every job, on every board in this repo.
- **ask**: a **lane exception**, asked in the question round for each job that reaches it.
- A path belongs to the most specific listed directory it sits under
  (`shared/utils/x.ts` is free above even if `shared/` were ask). A path under neither list
  is treated as ask until the user places it.

**First board in a repo (no section): lane setup.** Make it the first question of the
round. List every service directory in the repo: top-level directories with their own
manifest, build or deploy file (`package.json`, `go.mod`, `pyproject.toml`, `Dockerfile`,
…), plus any other top-level directory a task reaches. Ask, in one question, which are
**free** and which are **ask**. Recommend free for the directories most of this plan's
tasks live in and ask for the rest. As soon as the user answers, write the section (create
the file if it does not exist) and say in one line: *"Saved your lanes to
`~/.claude/plan-build-board/lanes.md`. Say 'always let me edit X' or 'ask before X' to change
them."*

A lanes file with no section for this repo is the same as no file: run the setup.

**A directory in neither list.** Ask it as a lane exception for the job, and in the same
question whether it joins free or ask from now on. Save the answer the same turn.

**The user changes a lane** at any time ("always let me edit web/", "ask before touching
agent/") → update the section in the same turn and confirm in one line. It applies from
then on: a pending exception question for a directory just made free is dropped, and a
directory just made ask is asked as an exception before its next edit, for any job not
yet implemented. Only the user's
words add or move a lane. Never add a directory to free yourself, even after the user
cleared it as an exception for every job so far.

## Building the board

Copy `template.html` (next to this SKILL.md) and fill it in. It is a single self-contained file: tabs, status
pills, filter chips and tally, light and dark, works at phone width.

**Scale the tabs to the board.** The template ships seven; delete what the board does not need,
and add Method by copying the Queue panel and changing its id.

| Tab | In template | Keep / add it when |
|---|---|---|
| Before you start | yes | Always. It is the protocol the user and the next agent read, and it ends with the collapsed **History** (*Keeping the board current*). |
| Issues | yes | Whenever any task comes from an issue: issue → tasks → jobs → PRs, the No issue group, and the warnings (*Issues*). Delete it, and the Issue columns on Jobs and Queue, only when no task comes from one. |
| Jobs | yes | Always. Every job in rank order: its tasks, why they are together, files touched, effort · risk, and the review once it is done. |
| Queue | yes | Always. Open tasks in rank order — severity weighted by reach, certainty and cost — with the job each belongs to. |
| Tasks | yes | Always. Every task, grouped by area, with the status filter chips. |
| PRs | yes | Always, once jobs exist, whatever the shape. The overview table (shape, branch → target, builds on, jobs), one line per PR on why it is independent or what it builds on, then each chain under its base line, and per PR: shape pill, status, progress, branch → target, sync line, its jobs, and the config to copy. Never delete it because nothing is stacked. |
| Manual tests | yes | Only when something needs a browser, a real provider, or a judgement call. |
| Method | add | Only when how the task list was produced is itself worth recording. |

A job's pill is the least-advanced status among its tasks still in it, and moves when
theirs do.

A tab's count in the nav (`<span class="c">`) is hand-maintained like the tally.

Load `artifact-design` before the first publish — the template already satisfies the page
contract, so you are checking your additions, not re-deriving the page.

Write it to the scratchpad directory, then publish with the `Artifact` tool. Give the user
the link once, in one line.

## Red flags — stop

- About to edit an implementation file for a task that is not `Approved`.
- Publishing the board, even a skeleton, before every question in the round is answered.
- A task on the board that still needs an answer from the user, or a proposal that asks
  one. Approval is the only thing a proposal asks for.
- Asking a question at Step 5, or at a job's start, that the round could have asked.
- Presenting a whole job when the user said "next task", or one job when they said "next
  PR".
- Implementing a second job (or a second task, in task scope) before the user has had the
  review and said to go on. Approved PR plans are not that go.
- Reading "approve PR 1" as "implement PR 1 in one sitting". Only "without stopping", or
  words like it, lifts the one-job cap, and only for what the user named.
- Writing one proposal that covers several tasks — a job has a header plus one proposal
  per task, never a merged plan.
- Implementing a task that is not in the job being worked, or an edit that serves no
  task in it.
- Putting a High-risk task, or tasks from two lanes, in one job.
- Finishing a job without the job review.
- Heading 7 says "removing the old path" without the user having answered.
- A status changed in the code but not on the board this turn.
- Marking `Fixed` before running the verification.
- Editing a directory outside the lane because the fix was small.
- Treating any directory as free without the lanes file saying so, or asking a lane
  exception for a directory the file lists as free.
- A lane answer (setup, a new directory, a change) not written to the lanes file the same
  turn, or a directory added to free without the user's words.
- Publishing a second board when one already exists for this work.
- Splitting into a stack, or choosing its cuts, without the user saying yes in words.
- A job split across two PRs, or a PR that breaks the build until a later one lands.
- Editing for the next PR before the handoff and branch check, or with the previous
  PR's work still uncommitted in the tree.
- Creating a branch, committing, pushing or opening a PR yourself because a stack exists.
- A create command, or a branch you create, without `--no-track`; or a branch whose
  upstream is any branch but its own name. A push to that upstream skips the PR entirely.
- A PR's last job reviewed without the PR handoff in the same turn.
- A PR body pasted into chat. It belongs on the PRs tab, behind its Copy button.
- A board with jobs but no PRs tab, or a PR on it with no shape pill or no config,
  because nothing is stacked.
- A task that comes from an issue on a board with no Issues tab, or a Jobs or Queue row
  with no Issue cell. A task with no issue still gets its origin, under No issue.
- `Closes #n` in a PR body while part of #n is open, undecided, or in another PR.
- An issue's state or title written from memory instead of read from the tracker.
- An `open` attribute on a PR config `<details>`, or a config expanded for any PR, by
  markup or by script. Every PR config stays collapsed, whatever its status. An older
  board's script that opens one (the "last done PR" rule) is replaced at the next
  republish (*Keeping the board current*).
- Draft set to `no` while a PR it builds on still needs changes and the stack is not
  complete, or left at `yes` after it became merge-ready without telling the user.
- Rebasing a stack branch when the user did not ask for a rebase, or rebasing the whole
  stack in one command (`--update-refs`). Syncs are merges by default, one PR at a time,
  through integration-assistant.
- Syncing the stack because main moved, when the probe is clean and nothing needs it.
- Skipping a propagation run's checks because "we already know what changed".
- Starting the next link of a sync cascade before the previous one is verified and committed.
- Adding a commit to a PR in the middle of the stack before that PR is synced, or syncing
  the PRs above it before the commit is in.
