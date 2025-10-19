# jenkins-duplicate-prevention – next actions

Status: backlog
Created from: Conversation review on 2025-10-19
Objective: jenkins-duplicate-prevention
Priority: Medium
Estimated effort: [AI hours] / [Human hours]

## Next actions (not-yet-tried / unplanned)
- [ ] Add shell aliases in `~/.zshrc` to block `jenkins` direct runs and provide safe shortcuts
- [ ] Create git pre-commit hook to reject forbidden Jenkins startup commands
- [ ] Add package guard script to detect `jenkins` (non-LTS) and alert/remediate
- [ ] Add boot-time preflight check via LaunchAgent to run `jenkins_preflight_check.sh` on login
- [ ] Extend preflight to verify Jenkins binds only to 127.0.0.1 (network binding check)
- [ ] Reset/verify Jenkins LTS (port 17843) login; complete setup wizard if needed
- [ ] Recreate local pipeline job via API and run E2E + unit jobs; store API verification outputs
- [ ] Update `README.md` and cross-link `.cursorrules_jenkins` quick commands
- [ ] Optional: prompt-and-kill auto-remediation if unauthorized Jenkins found on port 8080

## Context from conversation
- Enforce single-instance Jenkins locally (17843), block duplicates (8080)
- API-first usage via `~/vars/jenkins_api_helpers.sh` (CSRF crumb handled)
- Preflight check blocks duplicates; managed start/stop scripts always call it
- `~/.jenkins` cleaned and documented (README + agents.md only)
- Comprehensive prevention documented in `JENKINS_PREVENTION_AUDIT.md`

## Links
- `docs/plans/backlog/jenkins-duplicate-prevention_next_actions_2025-10-19.md` (this doc)
- `.cursorrules_jenkins`
- `JENKINS_PREVENTION_AUDIT.md`
- `WHY_JENKINS_HOME_EXISTS.md`
- `~/vars/JENKINS_INSTANCES_GUIDE.md`