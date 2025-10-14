# /archive

Create plan documents from a conversation review across statuses: backlog (baseline), prioritized (optional), and active (optional). Optionally store a conversation archive stub. Use objective-based naming; do not create `conversation_archiver_*` implementation plans.

## Command sequence (run in order)

1) Verify repository context
```bash
gtimeout 5 git rev-parse --show-toplevel
```

2) Set objective slug, date, and create flags (edit values)
```bash
OBJ_SLUG="your-objective-kebab"   # e.g., fix-conversation-archiver-output
DATE=$(date +%Y-%m-%d)

# Baseline backlog target (always created)
BL_TARGET="docs/plans/backlog/${OBJ_SLUG}_next_actions_${DATE}.md"

# Optional prioritized and active plan targets (created only if flags set)
PR_TARGET="docs/plans/prioritized/${OBJ_SLUG}_plan.md"
AC_TARGET="docs/plans/active/${OBJ_SLUG}_plan.md"

CREATE_PRIORITIZED=false   # set to true if ready-to-begin soon
CREATE_ACTIVE=false        # set to true if already in progress or to start immediately
```

3) Ensure plan directories exist
```bash
gtimeout 5 mkdir -p docs/plans/backlog docs/plans/prioritized docs/plans/active
```

4) Create backlog next-actions document (baseline)
```bash
cat > "$BL_TARGET" << EOF
# ${OBJ_SLUG} – next actions

Status: backlog
Created from: Conversation review on ${DATE}
Objective: ${OBJ_SLUG}
Priority: Medium
Estimated effort: [AI hours] / [Human hours]

## Next actions (not-yet-tried / unplanned)
- [ ] Action 1 (clear verb, scope, owner/context if known)
- [ ] Action 2
- [ ] Action 3

## Context from conversation
- Key decisions, constraints, and notes that justify the next actions

## Links
- Related plans (if any) and references
EOF
```

5) OPTIONAL: Create prioritized plan if needed (safe create; skip if exists)
```bash
if [ "$CREATE_PRIORITIZED" = "true" ]; then
  if [ ! -f "$PR_TARGET" ]; then
    cat > "$PR_TARGET" << EOF
# ${OBJ_SLUG} Plan

**Status**: prioritized
**Created from**: Conversation review on ${DATE}
**Priority**: High
**Estimated effort**: [AI hours] / [Human hours]

## Overview
Brief description and scope.

## Current Status
- Not started; ready to begin

## Pending Tasks
### High Priority
- [ ] Task 1

### Medium Priority
- [ ] Task 2

## Next Actions
1. Immediate step 1
2. Immediate step 2

## Context from Conversation
- Key decisions and constraints

## Success Criteria
- Expected outcomes and quality bars
EOF
  fi
fi
```

6) OPTIONAL: Create active plan if needed (safe create; skip if exists)
```bash
if [ "$CREATE_ACTIVE" = "true" ]; then
  if [ ! -f "$AC_TARGET" ]; then
    cat > "$AC_TARGET" << EOF
# ${OBJ_SLUG} Plan

**Status**: active
**Created from**: Conversation review on ${DATE}
**Priority**: High
**Estimated effort**: [AI hours] / [Human hours]

## Overview
Brief description and scope.

## Current Status
- In progress: summarize what is underway

## Pending Tasks
### High Priority
- [ ] Task 1

### Medium Priority
- [ ] Task 2

## Next Actions
1. Immediate step 1
2. Immediate step 2

## Context from Conversation
- Key decisions and constraints

## Success Criteria
- Expected outcomes and quality bars
EOF
  fi
fi
```

7) OPTIONAL: Create a conversation archive stub (stores links/summary)
```bash
ARCHIVE_DIR="archive/conversations"
ARCHIVE_FILE="${ARCHIVE_DIR}/${DATE}_${OBJ_SLUG}.md"
gtimeout 5 mkdir -p "$ARCHIVE_DIR"
cat > "$ARCHIVE_FILE" << EOF
# Conversation archive – ${OBJ_SLUG} (${DATE})

Summary
- Brief synopsis of the conversation and outcomes

Backlog doc
- ${BL_TARGET}

Related plans
- Prioritized: ${PR_TARGET}
- Active: ${AC_TARGET}

Notes
- Any important context not captured elsewhere
EOF
```

8) Stage created/updated files
```bash
gtimeout 10 git add "$BL_TARGET"
```

```bash
if [ -f "$PR_TARGET" ]; then gtimeout 10 git add "$PR_TARGET"; fi
```

```bash
if [ -f "$AC_TARGET" ]; then gtimeout 10 git add "$AC_TARGET"; fi
```

```bash
if [ -f "$ARCHIVE_FILE" ]; then gtimeout 10 git add "$ARCHIVE_FILE"; fi
```

9) Run hooks (if configured)
```bash
gtimeout 60 pre-commit run --all-files
```

10) Commit (single-line, no emojis)
```bash
COMMIT_MSG="docs: archive conversation; create/update plans for ${OBJ_SLUG}"
gtimeout 10 git commit -m "$COMMIT_MSG"
```

11) Push
```bash
gtimeout 15 git push
```

If push reports no upstream is set (first push for this branch):
```bash
gtimeout 15 git push --set-upstream origin $(git branch --show-current)
```

## Notes
- Baseline: always produce the backlog next-actions doc.
- Use objective-based naming and link plan files in the backlog doc.
- Only create prioritized/active when justified by readiness; otherwise keep in backlog.
- Never overwrite existing plan files; update in place if they already exist.
- Do not create `conversation_archiver_*` implementation plans from this flow.
- Keep commands unchained and short; one command per step.
