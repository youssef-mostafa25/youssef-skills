---
name: merge-assistant
description: Guide safe git branch merges by analyzing what changed on each branch in parallel, surfacing not just textual conflicts but also semantic and logical issues that silently break things, getting the user's decision on every issue upfront, then executing the merge with those decisions baked in. Use this whenever the user wants to merge git branches together — phrasings like "merge my feature into main", "combine these branches", "bring my branch up to date with main", "help me resolve merge conflicts", or any request involving git merge planning. Strongly prefer this skill over a quick `git merge` for any non-trivial merge.
---

# Merge Assistant

Help the user merge one git branch into another (source into target) carefully and deliberately. The defining feature of this skill is that all the thinking is front-loaded: analyze both branches, surface every conflict and risk, get the user to decide how to handle each one — *before* starting the merge. The mechanical resolution is then driven by decisions already made.

Operate in two phases:

- **Phase 1: Discovery & Planning** — analyze, surface issues, gather decisions
- **Phase 2: Execution** — perform the merge using the user's decisions

Do not skip ahead. Do not start the merge during Phase 1. Do not ask new strategic questions during Phase 2.

## Explanation style: always use sha3bolly

**Invoke the `sha3bolly` skill (via the Skill tool) at the start of every run, before Step 1.** It ships in this plugin as `youssef-skills:sha3bolly`. Its rules govern everything this skill shows the user: the terminal messages, the merge review artifact (Phase 1, Step 5), the decision summary and the Phase 2 hand-off. In practice:

- Plain words and short sentences. Define a term the first time it appears ("merge base", "delta", "auto-merge").
- **Every issue gets a concrete example** — the real code line, the real error text, the real payload or filename from this merge. Never an abstract description on its own.
- **Every issue whose failure chains through several steps gets a flowchart.** For a genuinely single-step issue, say so explicitly ("Single step: no flow to draw").
- Put the point first. Keep the long detail in the artifact, not the terminal.

The subagent prompts in Step 3 don't need this style: their reports are working material. You apply it when you synthesize them.

## Vocabulary

Use these names consistently — in your own analysis, in every subagent prompt, and in everything shown to the user. Never fall back to single-letter placeholders.

| Name | Meaning |
|------|---------|
| **source branch** | the branch whose changes are being brought in |
| **target branch** | the branch that receives the changes; the user ends up on this one |
| **merge base** | the most recent common ancestor commit of the two branches — the divergence point |

Below, `<source-branch>`, `<target-branch>`, and `<merge-base>` stand in for the real branch names and the real commit hash. Substitute the actual values as soon as you know them — commands and reports shown to the user should name real branches, not placeholders.

---

## Phase 1: Discovery & Planning

### Step 1: Confirm direction and run preflight checks

Clarify which branch is being merged *into* which — which one is the **source branch** and which is the **target branch**.

If the phrasing is ambiguous ("merge main and my-feature"), ask which way the merge goes before proceeding.

Then run preflight checks:

1. **Working tree must be clean.** Run `git status --porcelain`. If anything is uncommitted or staged, stop and ask the user to commit, stash, or discard. Never proceed with a dirty tree.
2. **Both branches must exist.** Verify with `git rev-parse --verify <branch>` for both the source and target branch. Include remote-tracking variants (`origin/<branch>`) if relevant.
3. **Remember the starting branch.** Run `git branch --show-current` and save it so the user can be returned there cleanly if they abort.
4. **Offer to fetch.** Ask: "Should I fetch the latest from remote first? (yes / no / only one of them)" Stale local branches lead to bad analysis. Default suggestion: yes if both branches track remotes.

### Step 2: Find the merge base

Run:

```bash
git merge-base <target-branch> <source-branch>
```

Save this commit hash as the **merge base**. This is the most recent common ancestor — the divergence point.

Also check for prior merges between the two branches:

```bash
git log --oneline --merges <target-branch>..<source-branch>
git log --oneline --merges <source-branch>..<target-branch>
```

If there's a recent merge between them, mention it to the user — it changes their expectations about what "new" changes exist.

If `git merge-base` returns empty (unrelated histories), stop and ask whether the user really wants to merge unrelated histories — this is unusual and requires `--allow-unrelated-histories`.

### Step 3: Dispatch three parallel analysis subagents

Spawn three subagents **in the same tool turn** so they run in parallel. Each gets a focused, narrow task:

- **source analyst** — what changed on the source branch
- **target analyst** — what changed on the target branch
- **cross-diff analyst** — how the two sets of changes collide

Each of these three subagents is itself permitted — and encouraged for non-trivial work — to **dispatch its own helper subagents** to parallelize its investigation. For example, the source analyst might split a large diff by directory and spawn one helper per area (e.g., one for `src/auth/`, one for `src/api/`, one for migrations) and then assemble their findings into its final report. Tell each subagent explicitly in its prompt that it may do this when the diff is large or spans clearly separable areas, and that it is responsible for synthesizing helper outputs into a single coherent report — the main agent should never need to deal with raw helper output, only the subagent's consolidated report.

After all three subagents return, the main agent (Phase 1, Step 4 below) collects their three reports and produces **one final, detailed, unified report** for the user — this is the artifact the user actually sees and reviews. Don't paste the three subagent reports verbatim; merge them, deduplicate, cross-reference, and structure them per Step 4.

**Source analyst — changes on the source branch since the merge base**

Prompt:

> Analyze the changes on branch `<source-branch>` since commit `<merge-base>`. Do NOT look at branch `<target-branch>`. Use:
> - `git log --oneline <merge-base>..<source-branch>` for commits
> - `git diff --stat <merge-base>..<source-branch>` for the file-level overview
> - `git diff <merge-base>..<source-branch>` for the full diff (or `--name-only` then inspect files of interest if it's huge)
>
> If the diff is large or spans clearly separable areas (e.g., multiple top-level directories, frontend vs. backend, app vs. migrations), you may dispatch your own helper subagents in parallel — one per area — and then consolidate their findings into a single coherent report. You are responsible for that synthesis; do not return raw helper output.
>
> Produce a structured report with these sections:
> 1. **Intent** — what is this branch trying to do, in 1–3 sentences? Infer from commit messages plus the diff.
> 2. **Files changed** — grouped by area (source, tests, config, docs, migrations, deps).
> 3. **Public API / interface changes** — function signatures, exported names, route handlers, CLI args, types, schemas.
> 4. **Behavioral changes** — modified validation, changed defaults, altered return values, new side effects, removed features, changed error handling.
> 5. **New or removed dependencies** — `package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, lockfiles, etc.
> 6. **Configuration / environment changes** — env vars, config files, feature flags.
> 7. **Data / schema changes** — migrations, ORM models, fixtures.
> 8. **Test coverage** — new tests, modified tests, removed tests.
> 9. **Risk hotspots** — concurrency, shared state, security-sensitive code, performance-critical paths.

**Target analyst — changes on the target branch since the merge base**

Same prompt as the source analyst, but for branch `<target-branch>` and the range `<merge-base>..<target-branch>`. The same permission to dispatch helper subagents applies.

**Cross-diff analyst — how the two sides collide**

Prompt:

> Compare branches `<source-branch>` and `<target-branch>` directly. Use:
> - `git diff --stat <target-branch>..<source-branch>`
> - `git diff <target-branch>..<source-branch>` (sample by file if huge)
>
> You may also do a *dry-run merge* in a temporary worktree to surface real conflict markers without touching the user's working tree. **Use a detached worktree** (`--detach` at the target branch's commit) — a plain `git worktree add <path> <target-branch>` FAILS when the target branch is already checked out (the usual case, since the user is normally sitting on the target), and if you don't notice the failure the subsequent `cd` silently no-ops and the `git merge` then runs in the user's REAL working tree. Guard every step:
>
> ```bash
> git worktree add --detach /tmp/merge-dryrun <target-branch> || { echo "worktree add failed — STOP, do not merge in place"; exit 1; }
> cd /tmp/merge-dryrun || { echo "cd failed — STOP"; exit 1; }
> git merge --no-commit --no-ff <source-branch>
> git status
> git diff --name-only --diff-filter=U
> git merge --abort
> cd - && git worktree remove --force /tmp/merge-dryrun
> ```
>
> Never run the dry-run merge in the main working tree. If anything in the worktree setup fails, stop and fix it — do not fall back to merging in place. (Note: `set -e` does not reliably abort a one-line `;`-chained shell, so guard each command with explicit `||` as above rather than relying on it.)
>
> Produce a structured report with:
> 1. **Files touched on both sides** — list every file modified on both the source and target branch since the merge base.
> 2. **Likely textual conflicts** — based on overlapping line ranges or dry-run results, list conflicting hunks with `file:line` references.
> 3. **Files added on both sides** — same path created independently on each branch.
> 4. **Rename / move conflicts** — file renamed on one side and modified or renamed differently on the other.
> 5. **Binary file conflicts** — flag separately; these can't be auto-merged.
> 6. **Cross-file co-changes** — files that appear together in commits on both sides (suggests a shared concept is being touched).
> 7. **Clean-but-dangerous auto-merges.** For every file changed on BOTH sides that the dry-run merged *without* a conflict marker, do NOT assume it is safe — a clean auto-merge only means the edits didn't textually overlap. Open the merged result and check the two sides for *semantic* consistency: did one side change a function signature / convention while the other added a new sibling (or caller) still using the old form? Did one side move/rename a symbol the other side still imports? Report each such file with the specific inconsistency. Pay special attention to convention families: if one side changed every member of a pattern (all `execute_*`, all `*_handler`, all routes of a kind), list every member in the merged tree and confirm the other side's additions match.
>
> If there are many overlapping files, you may dispatch helper subagents in parallel — for example, one per conflicting file or per area — to inspect each in detail, then consolidate their findings into a single coherent report.

Wait for all three reports. If one subagent fails, retry that one only — don't restart all three.

### Step 4: Synthesize findings

Read all three subagent reports together and synthesize them into **one final, detailed report** — the consolidated artifact the user actually sees. Cross-reference findings across the three reports (a file that appears in both the source and target analyst reports *and* shows up in the cross-diff analyst's conflict list is almost certainly an issue worth flagging), deduplicate, and structure as a unified issue list. Look for:

**Direct conflicts** (will produce conflict markers during merge):

- Overlapping line edits in the same file
- File added on both sides at the same path with different content
- File modified on one side, deleted on the other
- Rename conflicts

**Semantic conflicts** (will NOT produce conflict markers but will silently break things — this is the most valuable thing this skill catches):

- Function/method signature changed on one branch; new callers added on the other
- Function renamed or removed on one branch; still called from new code on the other
- Constant, enum, or type definition changed on one side; used by new code on the other
- Configuration key renamed on one side; referenced by new code on the other
- Database migration added on both sides — ordering matters
- Dependency upgraded to an incompatible version on one side; new usage of the old API on the other
- Concurrent refactors of the same logical area (e.g., both branches restructure auth)
- API / protocol / route changes that affect new callers added on the other side
- Both branches independently implementing the same feature (divergent approaches to the same goal)
- **Parallel-implementation / convention drift (the sneaky one).** One branch changes a convention shared across a *family* of similar things — every `execute_*` tool drops a parameter, a base class gains a required field, a config key is renamed everywhere, all handlers of a kind switch to computing a value internally — while the OTHER branch adds a *brand-new member of that same family* that still follows the OLD convention. The new member is not a caller of the changed code and lives in its own region, so it produces **no textual conflict and merges cleanly**. But at runtime it is inconsistent with its now-changed siblings (wrong signature, wrong call pattern, wrong base) and breaks. Detection rule: whenever one branch changes a *repeated pattern*, enumerate every member of that family in the merged tree (grep for the shared prefix/decorator/base) and confirm the other branch's new members match the NEW convention — not just the ones that textually conflicted. A signature/convention change flagged by one branch analyst must be cross-referenced against every *new symbol of the same kind* reported by the other, even when no file overlaps.

**Test conflicts:**

- Tests on one branch assume old behavior; the other branch changes that behavior
- Test fixtures changed incompatibly
- Snapshot tests touching the same files

**Configuration / infrastructure drift:**

- `.env.example`, CI config, build config divergence

Classify each issue by severity:

- **Critical** — high chance of broken runtime behavior or data loss if not addressed
- **Warning** — likely to cause bugs but recoverable; reviewer should decide
- **Info** — worth mentioning but probably fine

### Step 5: Present findings and gather decisions

The findings are always delivered as a **merge review artifact**: a published HTML page with tabs, one view per tab — **Source**, **Target**, **Combined**, **Issues**, one **Verification N** tab per verification round, and **Decisions** last. Decisions is the only tab with option pickers; it always reflects the latest (most verified) round, and the copy-your-reply bar reads only from it. The other tabs are a read-only record (Step 5b). The terminal gets a short summary and the link (Step 5c). Decide the content of each issue and each decision first (Step 5a), then build the page.

#### Step 5a: Write each issue and each decision

The terminal summary opens with this block:

```
Merge plan: <source-branch>  →  <target-branch>
Merge base: <merge-base> (<short commit summary>)
Commits on <source-branch> since merge base: <count>
Commits on <target-branch> since merge base: <count>

Findings:
  Critical: <count>
  Warning:  <count>
  Info:     <count>
Decisions for you: <count>
```

Order the issues **critical first, warnings next, info last**. Each **issue** becomes one row (plus its detail row) in the Issues tab's table:

```
### Issue <number>: <short title>  [severity]

What's happening:
<2–4 sentences with file:line references>

Example (sha3bolly — required):
<the real code line / error text / payload / filename from this merge that shows the problem>

Flow (sha3bolly — required when the failure chains through steps):
<a mermaid flowchart, e.g.  planner picks X --> registry lookup --> not registered --> skipped>
or: "Single step: no flow to draw"

Decided in: <D-number | "Small fixes" | "No decision needed">
```

Then group the issues into **decisions**. One decision (`D1`, `D2`, …) covers every issue settled by the same choice. An issue with only one sensible fix goes to the Decisions tab's "Small fixes" table, not to a card. An info note needs no decision. Each decision becomes one card on the Decisions tab:

```
### D<number>: <decision title in plain words>  [severity]

The point: <one or two sentences, before any detail>
What's going on: <what each branch did, with file:line references; which issues it covers>
Why it's a problem: <concrete scenario of what could break if ignored>
Example: <real code / error / payload>
Flow: <mermaid flowchart, or "Single step: no flow to draw">

Options:
  1) <what you do> — <what you get> — risk: <…> — effort: S | M | L
  2) <…>
  Other — describe your approach

Recommendation: option <n>, because <reason>
```

Bugs found along the way that this merge didn't cause become **follow-ups** (`F1`, `F2`, …) with the actions "Fix in the merge", "Write up" or "Skip".

Rules for options:

- Always offer at least two concrete options where a real choice exists
- **Always include a free-form "Other" choice** — the user's situation may not fit any pre-baked answer. In the artifact it is the picker's `Other` value, not a numbered option
- Number the options so the user can answer with a number; never label them with bare letters
- Make options concrete: say what code or behavior would result, not just "keep the source branch's version"
- For semantic conflicts, options often include "update the new callers to match the new signature" vs. "revert the signature change" — be specific about the work each entails
- Give each card a recommendation with its reason, and mark it in the options table. The user still makes every call; the recommendation never gets applied without their pick

#### Step 5b: Build and publish the merge review artifact

**Always do this, on every run.** Even a small merge with only info findings gets a page.

**Start from the template.** `merge-review-template.html` (next to this SKILL.md) is the page skeleton: the full `<style>` block, the tab / filter / picker / copy-bar `<script>`, the `#review-meta` revision record, every tab with one placeholder of each kind of row and card, and two inert `<template>` blocks for adding a verification round. Copy it to the scratchpad as `<target>-<source>-merge-review.html`, then **keep its `<style>` and `<script>` blocks verbatim** and fill in only the content: replace every `{{PLACEHOLDER}}`, duplicate each `repeat` block once per item, delete the optional blocks you don't use, delete the `<template>` blocks and the template's HTML comments. That keeps the look, the tabs, the severity filters, the pickers and the copy bar identical across runs. Never re-derive the CSS or JS from scratch. Before publishing, check that no `{{` remains in the file. Don't add a Mermaid `<script>`: the Artifact host renders every `pre.mermaid` itself.

Before writing the file, make one `Artifact` call with `action: "quickstart"` and `intent: "other"`, as the Artifact tool requires for a new page. Its page-design guidance is already met by the template, so you don't need to load `artifact-design` separately.

**Tabs — in this order.** The tab bar sticks to the top of the page; the header with the branch chips and the summary stats sits above it. The page opens on Decisions, which carries a "Decide here" badge. Link between tabs with `<a href="#issue-3" data-goto="issues">Issue 3</a>` (or `#decision-D1` with `data-goto="decisions"`): the script opens the tab and scrolls to the element.

| Tab | When | Content |
|---|---|---|
| **Source** (labelled with the source branch name) | Always | What the source branch changed: `#` (S1…), Area, What changed, In plain words, Collides with target (chip High / Medium / Low / None plus a one-line reason). From the source analyst. |
| **Target** (labelled with the target branch name) | Always | The same table (T1…), from the target analyst. |
| **Combined** | Always | **Big picture**: a paragraph on the merge base and pull result, a mermaid flowchart of the two branches diverging and colliding, and a `.point` box with **the one thing to understand**. **Conflict map**: File, Type chip (UU / AA / DU / UD, with hunk count), What collides, Covered by. **Clean merges that still need checking**: the cross-diff analyst's clean-but-dangerous auto-merges (File, Risk, Why it is not safe, Covered by). |
| **Issues** | Always | The first pass. Severity filters, then `#`, Severity, Issue, What's happening, Decided in; each row has `id="issue-<n>"` and a `tr.detail` under it holding the **Example** (`pre.code`) and the **Flow** (`pre.mermaid`) or a "Single step" note. Then the severity legend. No pickers. |
| **Verification N** | Optional, one per verification round | Stats, a "How this round was checked" box saying what was really run, and an optional "What changed most" box. **New findings** (issue numbers continue from earlier tabs; chip New or Escalated; "Decided in" column). **Every earlier claim, checked**: Claim, Verdict chip (Holds / Corrected / Partly / Wrong / Not checked), What we found. **Refuted** suspicions with their evidence. Optional **Found on the way, not caused by this merge**. **What we could not check**. No pickers. |
| **Decisions** | Always, last | A "Based on …" box (the script fills in the latest round's name) saying this list supersedes the earlier tabs, plus an optional red box for anything to settle before the merge. Optional glossary. **Recommendations at a glance** (`#`, Decision, Recommended, Effort, Risk) and the "Use all recommendations" button. The **decision cards** with severity filters: the point, What's going on, Why it's a problem, Example, Flow, an options table (Option, What you do, What you get, Risk, Effort; the recommended row has `class="rec"` and a ✓), and the recommendation box with the picker; each card has `id="decision-D<n>"`. **Small fixes and notes, no decision needed**. Optional **Follow-ups** with pickers. **What happens after you decide**: the Phase 2 flowchart and the "Nothing is committed or pushed" box naming the project's test commands. |

**Adding a verification round.** When the user asks for another check, or a follow-up analysis changes the findings, never edit the Source, Target, Combined, Issues or earlier Verification tabs: they stay as the record of what each pass said. Copy the two `<template>` blocks from the skill's template file: the button goes just before the Decisions button, the panel just before the Decisions panel. Replace `verify-N` and `Verification N` with the round number and fill it in. Then **rebuild the Decisions tab** so it reflects every round so far, keeping the D- and F-numbers of decisions that still stand. Picks are saved per round, so the user starts the new round with empty pickers.

**Revision and the reply header.** `<script type="application/json" id="review-meta">` holds `source`, `target`, `rev` and `updated`. On the first publish `rev` is 1. **On every republish, increment `rev` and set `updated`** (UTC, `YYYY-MM-DD HH:MM UTC`), and remember the `rev` you published. The copied reply starts with a header built from it:

```
[merge-review feature/payments → main · rev 3 · updated 2026-10-04 21:10 UTC · based on "Verification 2"] D1:1 D2:2 F1:yes
```

When a reply with this header arrives, check it before acting on the picks (see Step 5d).

**The option picker and copy feature (don't change their contract):**

- Each decision card has `<select class="pick" data-issue="D<n>" data-rec="<recommended value>">`, with options `—` (empty value), one per numbered option, and `Other` (`value="other"`). Follow-ups use `data-issue="F<n>"` with the values `fix`, `yes` (write up) and `skip`. Pickers exist only on the Decisions tab.
- The script builds the reply as the revision header followed by `ID:value` pairs joined by spaces (for example `D1:1 D2:2 D3:other (…describe) F1:yes`), shows "(k still open)" while picks are missing, and saves the picks in `localStorage` inside try/catch. Saved picks are keyed by the round the decisions are based on and by `data-issue`, so they survive a republish that adds or reorders cards, and a new round starts fresh. The open tab is remembered per `rev`; a new `rev` opens on Decisions. "Use all recommendations" sets every pick to its `data-rec`. The copy button uses `navigator.clipboard.writeText` inside the click handler and falls back to selecting the text.
- The localStorage key is unique per merge: the script builds it from `source` and `target` in `#review-meta`, so one merge's saved picks never show up on another merge's page.
- After the header, the reply is the same `ID:value` string the terminal asks for, so the user can paste it straight back or type the picks by hand.

**Content rules:** follow sha3bolly (see the top of this skill). Use real branch names, never placeholders. The branch chips use the real names. Escape `<` and `&` inside `pre.code`. Mermaid labels are quoted, on one line, and never use `<br/>`, because the page's HTML would parse it. Keep the table `min-width` values, which sit inside `.table-wrap` so the tables scroll sideways on a phone.

**Publish:**

- Use the `Artifact` tool with `icon: "merge"` and a one-sentence `description` naming both branches and the decision count.
- Keep `<title>` as `<Target short name> <Source short name> Merge` (for example "Main Payments Merge" for `feature/payments` into `main`).
- When decisions change, or a verification round adds a tab, edit the same file, bump `rev`, and republish it to the same URL. Omit `icon` on a republish.

#### Step 5c: Terminal summary

In the terminal, don't repeat the full walk-through. Show:

1. The summary block from Step 5a.
2. The one or two sentences of "the one thing to understand".
3. A compact index: one line per decision, giving the D-number, severity, title and recommended option.
4. The artifact link. Say that every choice is on the Decisions tab, that its pickers build the reply, and that the user can also type it by hand, for example `D1:1 D2:2 F1:yes`.
5. A reminder that nothing has been merged yet, and nothing will be committed or pushed.

#### Step 5d: Gather decisions

Gather a pick for every decision and follow-up. The user may want to:

- Answer all at once
- Discuss specific decisions further (be ready to elaborate, show more code, dig deeper)
- Ask for another verification round — add a Verification tab and rebuild the Decisions tab (Step 5b)
- Change earlier answers — track decisions in a running list and allow revision at any point

**When a reply starts with a `[merge-review … rev N …]` header**, check it before using the picks:

1. Re-read the live page with the `Artifact` tool (`action: "read"`) and take `rev` from its `#review-meta`.
2. If the live `rev` is higher than the one you last published, the page was updated in another session. Read the new version, find what changed (new rounds, new or renumbered decisions), merge it into your understanding, and tell the user before acting.
3. If the header's `rev` or "based on" round doesn't match the live page's `rev` and latest round, the user picked on an older version. Say which decisions changed since then and ask them to re-pick on the live tab, or to confirm their picks still apply.
4. Only when the header's `rev`, the live `rev` and the one you published all match, record the picks as given.
- Abort entirely — return to the original branch cleanly

When all decisions are collected, **show a summary table of decisions** and ask for explicit confirmation to proceed to Phase 2.

---

## Phase 2: Execution

Only enter this phase after the user has explicitly confirmed.

### Step 1: Create a safety backup

Before touching anything, create a backup ref so the user can recover from any mistake:

```bash
git update-ref refs/backup/before-merge-$(date +%Y%m%d-%H%M%S) HEAD
```

Tell the user: "If anything goes wrong, you can reset with `git reset --hard refs/backup/<name>`. Run `git for-each-ref refs/backup/` to list them."

### Step 2: Check out the target branch

```bash
git checkout <target-branch>
```

If the target branch has a remote tracking branch and the user agreed to update during preflight, optionally fast-forward it now (`git pull --ff-only`). Only do this if the target branch is genuinely behind and there are no unpushed local commits on it.

### Step 3: Start the merge

```bash
git merge --no-commit --no-ff <source-branch>
```

`--no-commit` is essential so semantic fixes can be applied before committing. `--no-ff` preserves the merge commit — skip it only if the user explicitly wants fast-forward and one is possible.

Capture state:

```bash
git status
git diff --name-only --diff-filter=U   # files with textual conflicts
```

### Step 4: Resolve textual conflicts using the user's decisions

For each conflicted file:

1. Read the file and locate the `<<<<<<<` / `=======` / `>>>>>>>` markers
2. Find the issue(s) from the decision log that map to this file
3. Apply the chosen resolution by editing the file directly
4. Stage with `git add <file>`

If you encounter a conflict that wasn't in the decision log (the dry-run can miss subtle cases), **stop and ask the user before resolving**. Do not improvise.

For binary file conflicts: do not auto-resolve. Offer `git checkout --theirs <file>` (the source branch's version) or `git checkout --ours <file>` (the target branch's version) and let the user decide.

### Step 5: Apply semantic fixes

These are the changes that don't appear as conflict markers but were identified in Phase 1 — e.g., updating new callers to match a changed function signature, reordering migrations, deduplicating two implementations of the same feature. Apply each one according to the user's decision and stage the changes.

### Step 6: Verify and hand off

Run sanity checks:

- `git status` — all conflicts resolved, expected files staged
- `git diff --cached --stat` — summary of what will be committed

**Re-scan the clean auto-merges before trusting them.** List the files changed on both sides that merged without conflict markers (`git diff --cached` against each side's tip, or the cross-diff analyst's "clean-but-dangerous" list). For each, read the merged result and confirm the two sides' changes are *consistent*, not merely non-overlapping: no new sibling left on the old convention, no call to a now-changed signature, no import of a moved/renamed symbol. This is where silent breakage hides — a clean merge is not a correct merge.

**Exercise the merged code path, not just lint.** Lint and type-checks pass happily through signature/convention mismatches because the offending call only happens at runtime (e.g. an LLM tool-call, a request handler, a job). So, where feasible, identify the main entry point of the source branch's work and actually *run* it — a targeted test, a smoke invocation, or driving the app through that path — and offer this to the user even when lint/tests already pass. If you cannot run it, say so explicitly and name the path that remains unverified.

If you see a recognizable project test or lint command (`package.json` scripts, `Makefile`, `pyproject.toml`, `pre-commit-config.yaml`, etc.) and it's quick, offer to run it. Don't run anything heavy without asking.

Show the user a summary:

```
Merge ready to commit.
  Files changed:              <count>
  Insertions:                 +<count>
  Deletions:                  -<count>
  Textual conflicts resolved: <count>
  Semantic fixes applied:     <count>
```

**Do not commit automatically.** Ask: "Ready to commit? (1) commit now with the default merge message, (2) commit with a custom message, (3) let me review the staged changes first, or (4) abort and roll back."

If they choose to commit, use `git commit` (default merge message in editor) or `git commit -m "<message>"` if they provided one.

**Never push.** After committing, leave the push to the user. Mention: "Push when you're ready with `git push`."

---

## Aborting safely

At any point during Phase 2, if the user wants to abort:

```bash
git merge --abort
git checkout <original-branch>
```

The backup ref from Step 1 remains for additional safety.

If the user aborts during Phase 1 (before the merge has started), nothing needs undoing — just confirm and stop.

---

## Edge cases

- **Fast-forward only.** If the target branch has no new commits since the merge base, the merge is a fast-forward and there are no conflicts. Still run Phase 1 — semantic interactions are rare but possible. Mention it's a fast-forward and ask whether the user wants `--ff` (default), `--no-ff` (preserve a merge commit), or to rebase the source branch onto the target instead.
- **Already merged.** If `git merge-base --is-ancestor <source-branch> <target-branch>` returns true, the source branch is already in the target. Tell the user and stop.
- **Unrelated histories.** If `git merge-base` is empty, ask whether the user really wants `--allow-unrelated-histories` before doing anything.
- **Submodules.** If `.gitmodules` exists and the diff touches submodules, flag this in Phase 1 — submodule conflicts need separate handling and are easy to miss.
- **Very large diff.** If `git diff --stat` shows more than ~500 files or ~50k lines changed, warn the user and ask whether to do full analysis or focus on specific subdirectories.
- **Long-running analysis.** Don't go silent. If a subagent is taking a while, surface progress to the user.

---

## What to avoid

- Do not refer to the branches, the merge base, the analysis subagents, or the resolution options by bare single letters. Use the real branch names and the vocabulary above — "source branch", "target branch", "merge base", "cross-diff analyst" — so the user never has to hold a legend in their head.
- Do not auto-resolve conflicts via a blanket rule like "prefer the source branch" without asking — the entire point of this skill is that the user makes each call.
- Do not start the merge during Phase 1.
- Do not commit or push without explicit user permission.
- Do not skip semantic analysis — textual conflicts are the easy part; silent breakage is what causes regressions to slip through code review.
- Do not treat a clean auto-merge as a correct merge. The most dangerous breakage lives in files that merged *without* conflict markers — especially a new function/route/class added on one side that still follows a convention the other side changed across its whole family. Re-scan them and exercise the runtime path.
- Do not run the dry-run merge anywhere but a detached temporary worktree. If the worktree can't be created, stop — never merge in the live tree to "just check."
- Do not delete the backup ref. Leave cleanup to the user.
- Do not skip the merge review artifact or the sha3bolly style, and do not deliver the findings as a long wall of terminal text instead. Every run ends Phase 1 with a published page built from `merge-review-template.html`, with every choice on its Decisions tab.
- Do not restyle the template or rewrite its scripts. Only the content changes from merge to merge.
