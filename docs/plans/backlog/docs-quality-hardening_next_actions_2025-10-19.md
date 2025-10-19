# docs-quality-hardening – next actions

Status: backlog
Created from: Conversation review on 2025-10-19
Objective: docs-quality-hardening
Priority: Medium
Estimated effort: [AI hours] / [Human hours]

## Next actions (not-yet-tried / unplanned)
- [ ] Validate pre-commit on CI with Python 3.11/3.12 matrix and document local setup
- [ ] Align Reflex versions across root and generated apps; add generator check
- [ ] Add JSON log formatter toggle and sample log output to docs
- [ ] Harden tests for missing Reflex by mocking or conditional skips
- [ ] Verify per-app README, rxconfig comments, and run.sh UX for all templates
- [ ] Link canonical docs from root README and prune outdated analysis files

## Context from conversation
- The project underwent a comprehensive documentation and quality hardening across 7 phases, including structured logging, type hints, port registry docs, scripts UX, tests, and CI hooks.
- Some environment-specific issues (e.g., Python 3.10 in pre-commit envs, Reflex import during pytest) require follow-up hardening/documentation.

## Links
- Related plans (if any) and references
