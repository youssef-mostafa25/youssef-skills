---
name: planning-board
description: Use when the user says to start a job, take one on, move to the next job, or asks for a plan before implementation — any piece of work with more than one task, where each task needs its own written proposal approved in words before any implementation file is touched, tracked on a published status page.
---

# Planning Board

## Overview

A job is not a code change. A job is **one proposal per task, presented and approved
before any implementation file is touched, tracked on a published HTML board that is
updated in the same turn as every status change.**

**The rule: nothing is implemented until the user says yes, in words, to that specific
task.** A thumbs-up on another task, silence, or your own confidence that the fix is
obvious are not approval.

## When to use

- The user says "start a job", "take the next job", "let's work on X", "plan this out".
- Any work with 2+ tasks that will be worked over more than one turn.
- The user asks for a plan, or asks what is wrong with something and what it would take to fix.

**Not for:** a single-file edit the user directly asked for, answering a question, or
work already approved on an existing board (update that board instead of making a new one).

## The loop

```
user says "start a job"
  |
  v
1 INVESTIGATE (read-only)  --> 2 PUBLISH SKELETON (tasks Open, link in chat)
  |
  v
3 PRESENT proposals in chat + move every task to "Plan submitted" (same turn)
  |
  v
4 STOP and wait  --(user approves task #N, in words)--> 5 Approved --> implement
  |                                                          |
  |<--(user rejects)-- back to Open                          v
                                                    6 verify --> Fixed
                                                          |
                                                          v
                                            update board in the SAME turn
```

**Step 1 — investigate.** Read anything. Run read-only checks: greps, a throwaway probe
in the scratchpad, a suite that already exists. Do **not** edit a file the fix would
touch, and do not leave scratch files in the repo. Plan against the code, not against
what the user told you — if the premise does not hold, say so instead of proposing a fix.

**Step 2 — publish the skeleton** if the investigation runs longer than a couple of tool
calls, so the user has something to watch. Tasks start at `Open`. Give them the link once.

**Step 3 — present.** One proposal per task, in chat, under the seven headings below.
Never one proposal covering several tasks — the board tracks tasks, and a merged plan
leaves the others with no recorded decision. In the same turn, set every task to
`Plan submitted` with its effort and risk letters on the row.

**Step 4 — stop.** Approval is per task. Ask for the lane exception here too (below), once
per job, naming every directory the job reaches.

**Step 6 — verify before claiming Fixed.** Run the checks and quote what they printed.
Not after writing the code — after proving it.

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
4. **Ask.** The user answers. Nothing is implemented on this point until they do.

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
up. If fixing one task changes another's priority, say so and re-rank.

**Republish to the same URL** (pass the artifact's `url`) so the link keeps working. If
the board and the code disagree, everyone downstream is working from the wrong map.

## Two standing checkpoints

**Lane / boundary.** Name every directory the job's fixes reach. Before editing anything
outside the lane you were given, **ask once per job**, naming every directory. A small fix
is not an exception; small is not the criterion.

**Never commit.** Implementation lands **uncommitted** in the working tree. No
`git commit`, `git push`, `gh pr create`, amend or tag unless the user says so, in words —
and being told once is not permission for the next time.

## Building the board

Copy `template.html` (next to this SKILL.md) and fill it in. It is a single self-contained file: tabs, status
pills, filter chips and tally, light and dark, works at phone width.

**Scale the tabs to the job.** The template ships four; delete what the job does not need,
and add the last two by copying the Queue panel and changing its id.

| Tab | In template | Keep / add it when |
|---|---|---|
| Before you start | yes | Always. It is the protocol the user and the next agent read. |
| Queue | yes | Always. Open tasks in rank order — severity weighted by reach, certainty and cost. |
| Tasks | yes | Always. Every task, grouped by area, with the status filter chips. |
| Manual tests | yes | Only when something needs a browser, a real provider, or a judgement call. |
| Jobs | add | Only when the tasks group into more than one sitting, so the reading is paid for once. |
| Method | add | Only when how the task list was produced is itself worth recording. |

A tab's count in the nav (`<span class="c">`) is hand-maintained like the tally.

Load `artifact-design` before the first publish — the template already satisfies the page
contract, so you are checking your additions, not re-deriving the page.

Write it to the scratchpad directory, then publish with the `Artifact` tool. Give the user
the link once, in one line.

## Red flags — stop

- About to edit an implementation file for a task that is not `Approved`.
- Writing one proposal that covers several tasks.
- Heading 7 says "removing the old path" without the user having answered.
- A status changed in the code but not on the board this turn.
- Marking `Fixed` before running the verification.
- Editing a directory outside the lane because the fix was small.
- Publishing a second board when one already exists for this job.
