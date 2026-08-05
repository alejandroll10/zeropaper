## Long-running shell work (OpenCode)

OpenCode's Bash tool runs commands in the foreground and does not support Claude Code's `run_in_background` argument. Never detach work with `nohup` or `&`: detached jobs escape turn tracking and can outlive the driver watchdog. Give long commands a bounded tool timeout, write intermediate results to their documented artifact paths, and split restartable work into checkpoints. If a command reaches its timeout, inspect the checkpoint/output and resume deliberately in the next turn.
