# debug-log-sink

See logs you normally can't. It's for bugs that cross several processes, code whose
output is hidden (workers, background services, browser extensions, headless browsers),
or timing problems between frontend and backend. Every debug message goes into one file,
`debug-log-sink.log` at your repo root, in order. When you're done, every trace is
removed.

## How to use it

Say things like:

- "I can't see the worker's logs"
- "correlate the frontend and backend logs"
- "clean up the logs" (remove the debug log lines and empty the log, keep debugging)
- "full teardown" or "it's fixed" (remove the whole sink when you're done)

## What happens

```
start a small local log collector --> add marked debug lines to your code
   --> you reproduce the bug --> read debug-log-sink.log --> remove everything
```

- **Local only.** The collector listens only on your own machine.
- **`.gitignore`.** The first time it's used in a repo, `debug-log-sink.*` is added to
  `.gitignore` and stays there. Commit that line.
- **Clean-up, two choices.** *Clean up the logs* removes the marked debug log lines and
  empties the log, but leaves the collector running for another pass. *Full teardown*
  removes everything: the log lines, the collector, the log file and the rest of the
  `debug-log-sink.*` files. Neither one touches `.gitignore`.

## Watch out

Don't commit while a debug session is running. The debug lines are in your real source
files. If you ask Claude to commit, it checks first and refuses while any are left.

## Requirements

- Python 3.
