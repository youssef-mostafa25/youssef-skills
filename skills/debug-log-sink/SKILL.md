---
name: debug-log-sink
description: Use when debugging requires capturing log output that stdout/console cannot reliably show — across multiple processes, services, or hidden runtime contexts (frontend ↔ backend correlation, child processes, workers, serverless handlers, browser extensions, headless browsers, daemonized services, or race conditions where timing-sensitive console.log calls would interfere). Also use when a debug-log-sink session is active and the user is about to commit, says the bug is fixed, or asks to remove the debug logs. Not for permanent logging.
---

# debug-log-sink

## Overview

An ephemeral, zero-dependency localhost HTTP log collector for debugging scenarios where ordinary stdout/console logging cannot give a coherent picture: multi-process, cross-service, hidden runtime contexts, or timing-sensitive race conditions.

**Core principle:** This service is strictly temporary. Every artifact and every call site must be removed before the debugging session is considered complete.

## When to use this

Reach for this only when ordinary logging is insufficient:

- Separate terminals or scattered log files make correlation impossible
- Stdout is hidden (daemons, child processes, serverless handlers, browser extensions, headless browsers)
- Cross-process / frontend ↔ backend correlation needs a single timeline
- Race conditions where a blocking or noisy `console.log` would itself alter timing

If the debug output should remain in the codebase, **use a real logger instead** — this skill is an ephemeral aid that is fully removed before the work is considered done.

## The microservice

**Start from the bundled collector — don't write one from scratch.** This skill
ships a ready-made, spec-compliant collector at **`debug-log-sink.py`** (next to this SKILL.md).
Copy it to the project root and run it:

```bash
cp <skill>/debug-log-sink.py .   # <skill> = the "Base directory for this skill" path
```

Only hand-write the service if you must adapt it (e.g. Python 3 is unavailable →
write an equivalent in the runtime the project has) or change the port. The spec below documents exactly what the
bundled file does, so you can verify or adapt it. The service must:

- Bind to `127.0.0.1:9988` only — **never** `0.0.0.0`. Loopback-only is non-negotiable since the service has no auth.
- Use `ThreadingHTTPServer` so concurrent log calls from multiple processes don't serialize behind each other.
- Expose one endpoint: `POST /debug-log-sink/log`. The path deliberately contains the marker `debug-log-sink` so every call site is greppable.
- Also handle `OPTIONS /debug-log-sink/log` for CORS preflight, and send `Access-Control-Allow-Origin: *`, `Access-Control-Allow-Methods: POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type` on every response so browser code can call it.
- Accept JSON body `{ "source": "...", "level": "...", "message": "...", "data": {...} }`. All fields optional except `message`. Tolerate malformed input — never 4xx/5xx, always return `204 No Content`. A debug logger must never make client code fail.
- Append one line per request to `./debug-log-sink.log` at the project root, formatted: `ISO8601_TIMESTAMP [LEVEL] [SOURCE] MESSAGE | data=JSON`. Open the file with line buffering and call `flush()` after every write so logs survive a hard kill.
- Resolve the log and PID paths from the script's own directory, not the working directory, so the files land at the project root wherever it is launched from.
- On startup, bind the port first, then write its PID to `./debug-log-sink.pid` for reliable teardown (a failed bind must not leave a stale PID file).
- Be runnable as `python3 debug-log-sink.py`. Start in the background with `nohup python3 debug-log-sink.py > /dev/null 2>&1 &` on macOS/Linux, or `start /B python debug-log-sink.py` on Windows.

Place the script, PID file, and log file at the project root, all prefixed `debug-log-sink.*` so they're trivially listable and impossible to overlook during cleanup.

**The log file location is always the project root directory — non-negotiable.** Write `debug-log-sink.log` (and `debug-log-sink.py`, `debug-log-sink.pid`, and the cleanup manifest below) to the root of the project/repo, never into a subdirectory, a temp dir, or alongside the code being instrumented. A single, predictable root-level location is what makes the artifacts impossible to miss during cleanup and keeps the `rm -f debug-log-sink.*` teardown total. If the skill is invoked from inside a subfolder, resolve the project root (e.g. the git toplevel) and place the files there.

## Starting it

### Step 1 — git-ignore the artifacts (automatic, first use per repo)

Before copying anything, from the project root make sure the repo's tracked
`.gitignore` ignores `debug-log-sink.*`. Run this every time; it only writes on first use:

```bash
cd "$(git rev-parse --show-toplevel)"
grep -qxF 'debug-log-sink.*' .gitignore 2>/dev/null || \
  printf '\n# debug-log-sink: local debugging artifacts, never commit\ndebug-log-sink.*\n' >> .gitignore
git ls-files 'debug-log-sink.*'   # must print nothing
```

- If it appended the line, tell the user: *"I added `debug-log-sink.*` to `.gitignore`.
  This is a one-time, permanent change. Commit it on its own (or with your next
  commit). Teardown leaves it in place."*
- If `git ls-files` prints anything, sink files were committed earlier and `.gitignore`
  won't hide them. Stop and tell the user they need `git rm --cached` before you continue.
- Not a git repo → skip this step and use the non-git grep in Cleanup.

### Step 2 — warn the user once

Say this before the first instrumented line: *"The sink's files are git-ignored, but the
log calls I add to your source files are not. Don't commit until I've run cleanup.
If you need to commit mid-session, ask me first and I'll run the commit guard."*

### Step 3 — start and smoke-test

First check the port is free. A sink left running by another project answers on
the same URL, and your logs would silently land in *its* file:

```bash
lsof -nP -iTCP:9988 -sTCP:LISTEN    # must print nothing
```

If something is listening, find its directory with `lsof -a -p <PID> -d cwd`. If it is
another project's `debug-log-sink.py`, tell the user (it may be a forgotten session
that needs teardown). Don't kill it. Pick another unused high port, change `PORT` in
your copy, and use that port in every call site and grep. **Keep the URL path
`/debug-log-sink/log` and the marker unchanged**, so cleanup grep still finds every
call site.

Then copy, start, and prove the line reached **this project's** log:

```bash
cp <skill>/debug-log-sink.py .   # start from the bundled file
nohup python3 debug-log-sink.py > /dev/null 2>&1 &
sleep 0.3
T="smoke-$$-$(date +%s)"
curl -fsS -X POST http://127.0.0.1:9988/debug-log-sink/log \
  -H 'Content-Type: application/json' -d "{\"source\":\"smoke-test\",\"message\":\"$T\"}"
grep -q "$T" debug-log-sink.log && test -s debug-log-sink.pid && echo "sink OK" || echo "SINK NOT OURS / NOT RUNNING"
```

## Calling it from code

Every log call must be:

1. **Fire-and-forget with a ≤200ms timeout.** Logging must not block, must not be `await`ed in a way that changes ordering, and must never alter timing-sensitive behavior (race conditions are precisely the kind of bug this skill is for).
2. **Error-swallowing.** A downed sink, network blip, DNS quirk, malformed payload — all silent. Debug logging must never surface a new exception.
3. **Self-contained.** The full URL `http://127.0.0.1:9988/debug-log-sink/log` is inlined at every call site. No env vars, no config files, no shared helper imported from `utils/log.js`. The goal is that deleting the call site requires deleting only the lines you can see — no orphaned imports, no shared module to track.
4. **Marked with a comment on the line above:** `// DEBUG_LOG_SINK` (or `# DEBUG_LOG_SINK`, `-- DEBUG_LOG_SINK`, etc. for the host language). This marker is the single source of truth for cleanup grep.

### Example shapes

JavaScript / TypeScript:

```javascript
// DEBUG_LOG_SINK
fetch('http://127.0.0.1:9988/debug-log-sink/log', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({source: 'checkout.js', level: 'info', message: 'cart total computed', data: {total}}),
  keepalive: true,
}).catch(() => {});
```

Python:

```python
# DEBUG_LOG_SINK
try:
    import urllib.request, json
    urllib.request.urlopen(
        urllib.request.Request(
            'http://127.0.0.1:9988/debug-log-sink/log',
            data=json.dumps({'source':'worker.py','level':'info','message':'job dequeued','data':{'job_id':job_id}}).encode(),
            headers={'Content-Type':'application/json'}),
        timeout=0.2)
except Exception:
    pass
```

Go:

```go
// DEBUG_LOG_SINK
go func() {
    defer func() { _ = recover() }()
    body, _ := json.Marshal(map[string]any{"source": "worker.go", "level": "info", "message": "step started", "data": map[string]any{"step_id": stepID}})
    client := &http.Client{Timeout: 200 * time.Millisecond}
    req, _ := http.NewRequest("POST", "http://127.0.0.1:9988/debug-log-sink/log", bytes.NewReader(body))
    req.Header.Set("Content-Type", "application/json")
    resp, err := client.Do(req)
    if err == nil { resp.Body.Close() }
}()
```

Shell:

```bash
# DEBUG_LOG_SINK
curl -fsS --max-time 0.2 -X POST http://127.0.0.1:9988/debug-log-sink/log \
  -H 'Content-Type: application/json' \
  -d '{"source":"deploy.sh","message":"step started"}' >/dev/null 2>&1 || true
```

## Reading the log

```bash
tail -f debug-log-sink.log
```

## Cleanup manifest (`debug-log-sink.cleanup.md`)

As soon as you start instrumenting, create a cleanup manifest at the project root named
**`debug-log-sink.cleanup.md`**. Because it is prefixed `debug-log-sink.*` it is covered
by the same `.gitignore` entry and removed by the same final `rm -f` — the manifest
deletes itself. Its job is to be the human-readable record of *everything* this debug
session touched, so teardown is a checklist, not an archaeology dig.

Record in it:

- **Artifacts created** — `debug-log-sink.py`, `.log`, `.pid`, `.cleanup.md` (all root-level).
- **Other repo changes that are NOT `debug-log-sink.*` files** and so won't be caught by
  `rm` or the marker grep — anything you had to touch to make the sink live (a
  temporarily-relaxed CORS/CSP rule, a dev proxy entry, a disabled minifier, etc.). These
  are the easiest things to forget. (The `.gitignore` entry is permanent. Note whether
  you added it this session so you can remind the user to commit it, but never
  revert it.)
- **Every instrumented file** with its call-site count and a one-line note on what each
  area logs.
- **Any structural edit** that needs more than deleting the marked lines (e.g. an IIFE
  wrapped in a JSX fragment must be unwrapped, not just deleted).
- **The exact cleanup commands** for this session (stop, grep, revert non-artifact edits,
  `rm`, re-grep, re-verify builds).

> **Keep the manifest in sync as you go.** New log sites added mid-debugging MUST be
> appended to the manifest the same turn you add them. The `DEBUG_LOG_SINK` marker grep is
> still the authoritative cleanup source (so a missed manifest entry won't strand a call
> site), but the manifest is what tracks the *non-grepable* changes — any environment
> tweaks — which nothing else will remind you about. A stale manifest
> is how those get left behind.

## Leftover check (used by the commit guard and both cleanup options)

One command finds every call site. In a git repo the `.gitignore` entry hides the
root artifacts from it, so **empty output means clean**:

```bash
git grep -nE --untracked 'DEBUG_LOG_SINK|debug-log-sink/log|127\.0\.0\.1:9988'
```

Not a git repo:
`grep -rnE --exclude='debug-log-sink.*' --exclude-dir=.git --exclude-dir=node_modules 'DEBUG_LOG_SINK|debug-log-sink/log|127\.0\.0\.1:9988' .`

If you changed the port, use the new port in the pattern.

## Commit guard — run before EVERY commit while a session is active

Call sites live in tracked source files, so `.gitignore` does not protect them. Before
any `git commit` (yours, or one the user asks for) while the sink is set up:

```bash
git diff --cached -U0 | grep -E '^\+.*(DEBUG_LOG_SINK|debug-log-sink/log|127\.0\.0\.1:9988)'
git diff --cached --name-only | grep -E '(^|/)debug-log-sink\.'
```

Both must print nothing. If either prints anything, **do not commit**. Tell the user
which files carry debug-log-sink code, then either unstage those hunks or run Option 1
first. Never `git add -f` a `debug-log-sink.*` file. Never use `--no-verify` or a
"strip it in a follow-up commit" plan: once a call site is committed, it stays in history.

## Cleanup — two options (run the one the operator names)

Ephemeral means it MUST be removed. There are two tiers: a light one that strips
the debugging traces but keeps the sink available for more instrumenting, and the
full teardown. **Option 2 is mandatory before the work is considered done / the
branch is merged** — Option 1 is a mid-session reset, not a finish.

### Option 1 — remove logs added + captured (keep the sink up)
Strips the instrumentation and clears the captured data, but leaves the collector
running and `debug-log-sink.py` in place so you can re-instrument without
re-standing-up the service. Use between debugging passes.

1. Run the leftover check to list every call site.
2. Delete each marker line + the call it labels, and undo any structural edits the
   manifest flags (e.g. unwrap a JSX fragment). Do NOT touch `debug-log-sink.*` files.
3. Clear captured logs, keeping the file and service: `: > debug-log-sink.log`
4. Re-run the leftover check. It must print nothing.

### Option 2 — remove the ENTIRE debug-log-sink (full teardown)
1. **Do Option 1 steps 1–2** if call sites remain.
2. **Stop the service and prove it is down:**
   ```bash
   kill "$(cat debug-log-sink.pid)" 2>/dev/null; sleep 0.3
   curl -s -o /dev/null --max-time 0.5 -X POST http://127.0.0.1:9988/debug-log-sink/log \
     && echo "STILL RUNNING" || echo "stopped"
   ```
   A stale PID file is the usual cause, e.g. a second start that failed to bind. Find
   the real listener with `lsof -nP -iTCP:9988 -sTCP:LISTEN`, and kill it only if
   `lsof -a -p <PID> -d cwd` shows this project's root. Never `pkill -f debug-log-sink`,
   because that also kills sinks running for other projects.
3. **Revert the non-artifact edits the manifest records**, i.e. any environment
   tweaks made to stand the sink up. They are not `debug-log-sink.*` files, so
   neither grep nor `rm` catches them. Leave the `.gitignore` entry alone; it is permanent.
4. **Delete the artifacts (including the manifest itself):**
   ```bash
   rm -f debug-log-sink.py debug-log-sink.pid debug-log-sink.log debug-log-sink.cleanup.md
   ```
5. **Verify:** the leftover check prints nothing. Also run `git status --short` and
   `git diff` on every file the manifest listed. The only remaining changes should
   be the real fix (plus `.gitignore`, if it was added this session). Look out for stray
   blank lines and unused imports (`json`, `urllib`, `bytes`, …) left behind by
   deleted calls.
6. **Run the project's test suite and a smoke run of the app** to confirm no
   half-deleted call site was left behind.
7. **Report to the user:** what was removed, that the commit guard is clear, and, if
   `.gitignore` was added this session, that it still needs committing.

## Hard rules

- **Always keep the log file (and all `debug-log-sink.*` artifacts) at the project root.** Never write them into a subdirectory — a single predictable root-level location is what keeps cleanup total.
- **Maintain `debug-log-sink.cleanup.md` from the first instrumented line.** It records artifacts, every instrumented file, and — critically — the non-grepable changes (any env tweaks). Append to it the same turn you add new log sites. Cleanup uses it as the checklist of what to revert beyond the marker grep.
- **Git-ignore on first use.** `debug-log-sink.*` goes in the tracked `.gitignore` (Starting it, Step 1) before any artifact is created. It is permanent; teardown never removes it.
- **Never commit** any `debug-log-sink.*` file, call, or marker. Run the commit guard before every commit while a session is active. Option 2 is mandatory before the branch is merged.
- **Never generalize** this into a "real" logger. The moment it stops being temporary, it stops being this skill — use the project's actual logging stack instead.
- **Never bind to a non-loopback interface.** Never add auth, TLS, or persistence — those imply a longevity this service does not have.
- If the user reports the bug is fixed or moves on from the debug session, **proactively run Option 2 (full teardown)** and report exactly what was removed. (Use Option 1 only mid-session, when they want to clear traces but keep debugging.)

## Design rationale (why these choices)

| Choice | Reason |
|---|---|
| Greppable marker (`DEBUG_LOG_SINK` + URL path string) | Without it, "erase all calls" is best-effort. With it, cleanup is mechanical and verifiable. |
| Fire-and-forget + error-swallowing | A logger that throws or blocks can mask — or even create — the bug you're debugging, especially for race conditions. |
| Static URL inlined at every call site, no helper module | Tempting to DRY this up, but a shared `log()` helper means cleanup leaves orphans. Repetition is the feature. |
| Loopback-only bind, no auth | A "tiny debug service" on `0.0.0.0` is a real footgun. Loopback makes the missing auth safe. |
| Verification step in cleanup | "Delete everything" is easy to half-do; the post-cleanup grep makes it provable. |
| Permanent `.gitignore` entry | Artifacts can't be `git add`ed by accident in any session, by anyone, and the leftover check can use `git grep` with no artifact exclusions. |

## Red flags — STOP and reconsider

- "I'll just leave the sink running, I might need it later" → No. Cleanup now.
- "Let me wrap this in a helper to avoid repetition" → No. Repetition is the feature.
- "I'll bind to 0.0.0.0 so the other machine can hit it too" → No. Stand up a real logging endpoint instead.
- "I'll add a tiny auth header so it's safe to leave up" → You're building a real service. Stop and use the project's logger.
- "Tests pass, shipping" — but grep still finds `DEBUG_LOG_SINK` → Cleanup is incomplete. Not done.
- "I'll commit the fix now and strip the debug calls in a follow-up commit" → No. The calls end up in history. Run cleanup (or unstage the hunks) first.
- "It's git-ignored, so committing is safe" → `.gitignore` covers only the `debug-log-sink.*` files, not the call sites in your source. Run the commit guard.
