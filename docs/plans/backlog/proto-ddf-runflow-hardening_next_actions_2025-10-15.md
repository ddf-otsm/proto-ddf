# proto-ddf-runflow-hardening – next actions

Status: backlog
Created from: Conversation review on 2025-10-15
Objective: proto-ddf-runflow-hardening
Priority: Medium
Estimated effort: [AI hours] / [Human hours]

## Next actions (not-yet-tried / unplanned)
- [ ] Harden run.sh UX: consistent ASCII header/footer and param echoing across modes
- [ ] Add generated apps discovery in footer with live port detection
- [ ] Add --non-interactive flag and quiet mode for CI
- [ ] Makefile: add RUN_ARGS passthrough for subcommands and CI presets
- [ ] E2E smoke: verify serving URLs resolve and return HTML (frontend) and 200 (backend root)

## Context from conversation
- Consolidated improvements to make `make run` deterministic: default --log=ERROR, param parsing, ASCII header/footer
- Eliminated hardcoded ports; dynamic assignment with robust fallbacks
- Implemented app generation end-to-end with tests; verified with stock market app
- Makefile now primary entrypoint; supports ARGS passthrough

## Links
- Related plans: prioritized/active (to be created when ready)
- References: workflows/run.sh, Makefile, docs/guides/MAKEFILE_GUIDE.md, docs/testing/APP_GENERATION_TESTS.md
