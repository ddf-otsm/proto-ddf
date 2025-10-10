# /git-sync

**CRITICAL: This command displays guidance only. The AI must manually execute each step individually using terminal commands.**

- **Why files remain changed**: This command shows documentation - it does NOT execute git operations automatically. The AI agent must run each git command separately using `run_terminal_cmd`.
- **AI execution requirement**: After displaying this guidance, the AI must execute each step one-by-one, stopping on any error and reporting results.
- **Safety first**: No automated scripts, no chaining, no force-push, no `--no-verify`. Each command must be reviewed individually.
- **Manual execution required**: The AI cannot create or run bash scripts for git operations.

## Required AI execution flow (AI must run these commands individually):

**AI must execute each of these commands individually using `run_terminal_cmd`:**

1) **AI executes**: Verify repository context
```bash
gtimeout 5 git rev-parse --show-toplevel
```

2) **AI executes**: Sync remotes (and prune deleted refs)
```bash
gtimeout 10 git fetch --all --prune
```

3) **AI executes**: Stage changes
```bash
gtimeout 10 git add -A
```

4) **AI executes**: Run hooks (if configured)
```bash
gtimeout 60 pre-commit run --all-files
```

4.1) **AI executes**: Re-stage files if hooks modified them
```bash
gtimeout 10 git add -A
```

4.2) **AI executes**: If taxonomy violations are reported, move files as instructed, then re-run hooks
```bash
# Follow hook output to move files (e.g., .cline/rules -> .clinerules, keep .dadosfera/rules)
gtimeout 10 git add -A
gtimeout 60 pre-commit run --all-files
```

5) **AI executes**: Commit (single-line, no emojis; describe what changed and why)
```bash
gtimeout 10 git commit -m "<meaningful commit message describing changes>"
```

6) **AI executes**: Push (set upstream on first push if needed)
```bash
gtimeout 15 git push
# If push fails with "no upstream branch", then:
gtimeout 15 git push --set-upstream origin $(git branch --show-current)
```

**AI execution notes:**
- Execute each command separately using `run_terminal_cmd`
- Stop immediately if any command fails and report the error
- Re-stage after hooks that modify files; resolve taxonomy per hook guidance (.cline -> .clinerules; .dadosfera/rules stays)
- Verify output of each command before proceeding
- For commit message, use a meaningful description of what actually changed
