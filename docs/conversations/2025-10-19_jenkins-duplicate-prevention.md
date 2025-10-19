# Conversation archive – jenkins-duplicate-prevention (2025-10-19)

Summary
- Consolidated prevention of duplicate Jenkins instances. Implemented core layers (preflight guard, managed start/stop, API-first helpers, rules/docs). Cleaned `~/.jenkins`, retained docs. Optional hardening tasks captured in backlog.

Backlog doc
- docs/plans/backlog/jenkins-duplicate-prevention_next_actions_2025-10-19.md

Related plans
- Prioritized: docs/plans/prioritized/jenkins-duplicate-prevention_plan.md
- Active: docs/plans/active/jenkins-duplicate-prevention_plan.md

Notes
- LTS vs non-LTS clarified; enforce jenkins-lts on port 17843. Add shell aliases, pre-commit, and package guard as optional hardness. Resume Jenkins LTS login fix if needed and verify pipeline via API.
