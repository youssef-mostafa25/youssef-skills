---
name: handoff
description: Use when ending a work session, running low on context, or pausing a task and you need to capture full state so a fresh session (or another person) can resume with zero context loss. Triggers - "write a handoff", "create a handoff doc", "hand this off", "I'll continue in another session", "before we lose context", or wrapping up multi-step work that isn't finished.
---

# Handoff Document

## Overview

A handoff is a **verified state snapshot, not a narrative.** The next session has none of your conversation — it has only this file plus the repo. Its job: let someone resume instantly without re-deriving what you already know, and without trusting claims you never checked.

**Core principle: ground every claim in observed reality, then write with enough precision that the reader never has to ask "where?" or "is this actually true?"**

The failure mode is a plausible-sounding doc built from memory: placeholder paths (`tests/path/to/...`), test counts you assume rather than ran, "we fixed X" without saying how to confirm it. Don't write what you believe — write what you verified.

## Step 0 — Carry forward any inbound handoff (cumulative chain)

If this session was **started from** or **references a prior handoff** (a `*_HANDOFF.md` the user pasted, opened, or pointed you to), the new handoff must be **cumulative — it replaces the old one and is fully self-contained.** Never just link to the prior doc; the next session may not have it.

- **Find it:** check the conversation and the repo root for an existing `*_HANDOFF.md` on the same topic.
- **Fold it in, with updated status:** every item the prior handoff listed gets carried over and re-marked — `✅` if this session completed it, `⚠️` if still pending, or note if it was abandoned/superseded. Don't silently drop prior remaining items just because this session didn't touch them.
- **Preserve prior decisions and dead-ends** so they aren't redone, even if this session didn't revisit them.
- **Result:** a reader with ONLY the new file knows the full history — session 1's work + session 2's work + what's still open — not just the latest slice.
- **Supersede cleanly:** write to the same filename so the new handoff overwrites the stale one (don't leave two competing handoffs for the same topic).

## Step 1 — Ground in reality FIRST (before writing a word)

Gather actual state. Do not trust the conversation summary; the conversation can be wrong or stale.

- `git status` and `git --no-pager diff --stat` → the **real** changed/staged/untracked file list.
- `git --no-pager log --oneline -10` → what's committed vs uncommitted.
- Re-run (or quote the last real run of) the relevant tests/build → real counts and pass/fail, not "should pass".
- Open the actual files for exact paths, function/symbol names, and line numbers you'll cite.

If you cannot verify a claim, mark it explicitly as **unverified** rather than stating it as fact.

## Step 2 — Write the document

**Always write the handoff to a `.md` file** — never just print it in chat. Save to the repo root as `<TOPIC>_HANDOFF.md` (e.g. `CSV_EXPORT_HANDOFF.md`); if carrying forward an inbound handoff (Step 0), reuse that file's exact name so it supersedes the old one. After writing, tell the user the file path. Use these sections — drop any that genuinely don't apply, never pad:

1. **Title + one-paragraph scope** — branch, what this work is, in plain terms.
2. **TL;DR / where things stand** — bullet list with `✅` done-and-verified, `⚠️` remaining/at-risk. The reader should grasp the whole state in 20 seconds.
3. **Git / working-tree state** — committed vs staged vs uncommitted; exact branch; anything dirty or unusual (running processes, stashes, ignored stopgaps).
4. **What this delivers + how it works** — the architecture/approach, with exact `file_path:line` and symbol names. Cite, don't paraphrase.
5. **Decisions + dead-ends** — choices settled (and *why*), and approaches **tried and abandoned** (and why) so the next session doesn't redo them. This is high-value context that lives only in your head.
6. **Bugs / issues + fixes** — symptom → root cause → fix. Include the **recurring pattern or key lesson** if one emerged — the thing that, unstated, the next session will rediscover painfully.
7. **Remaining / next steps** — ordered, specific, actionable. Not "finish RBAC" but "wire RBAC on `GET /api/reports/{id}/export` following the pattern in `<file>:<line>`; add unauthorized-case test."
8. **Verification commands** — copy-pasteable, each with its **expected output** (`# expect 69 passed`, `# baseline = 7 errors, all in test files`). The reader must be able to confirm state without guessing.

## Precision rules

- **Exact over vague:** `backend/src/services/report_service.py:stream_rows` — never "the service file" or `path/to/file`.
- **Verified vs claimed:** every "it works / passes" gets a ✅ with the command that proves it, or a ⚠️ marking it unverified.
- **Counts are real:** "4 tests pass" only if you ran them. Otherwise "tests not run this session."
- **Convert relative dates** to absolute ("today", "yesterday" → the date).
- **No fabrication:** if you don't know, say "unknown / not checked," never invent a path, count, or date.

## Common mistakes

| Mistake | Fix |
|---|---|
| Built from the chat summary, not the repo | Run `git status` / tests first; cite real paths |
| Placeholder paths (`tests/path/to/...`) | Open the file; write the true path |
| "Tests pass" with no command | Add the verify command + expected output |
| Lost the *why* behind decisions / abandoned tries | Dedicate a Decisions + dead-ends section |
| Wall of narrative prose | Lead with a scannable ✅/⚠️ TL;DR; use tables/bullets |
| Buried the one gotcha that'll bite next time | Call it out as the key lesson |

## Done check

Before saving, confirm: a person with **only this file and the repo** could resume — they know what's done (and how it was verified), what's left (specifically), what was decided/abandoned and why, and how to confirm current state. If any of those requires re-asking you, the handoff isn't done.
