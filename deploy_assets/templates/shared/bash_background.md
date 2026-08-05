
## Background jobs

Never launch a long-running job with `nohup` or a detached `&` — it escapes harness tracking and stall detection. Use a harness-tracked background job instead (the Bash tool's `run_in_background`) so the job stays monitored and its output remains retrievable.

Make long jobs resumable: checkpoint/cache results to disk frequently and skip already-done work on restart, and log unbuffered in append mode (e.g. `python -u … >> log 2>&1`) so progress survives an interruption.
