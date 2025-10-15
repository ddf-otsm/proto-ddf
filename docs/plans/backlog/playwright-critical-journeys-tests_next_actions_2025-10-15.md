# playwright-critical-journeys-tests – next actions

Status: backlog
Created from: Conversation review on 2025-10-15
Objective: playwright-critical-journeys-tests
Priority: High
Estimated effort: 3 AI hours / 1 Human hour

## Next actions (not-yet-tried / unplanned)
- [ ] Fix color mode context error on index page (toggleColorMode) and add regression test
- [ ] Validate Makefile run flow in CI, ensure ports file sync and log clarity
- [ ] Run Playwright E2E smoke in CI on generator (home, generation flow) with PWDEBUG off
- [ ] Add playwright inspector doc link in app footer for dev mode

## Context from conversation
- App showed Reflex error boundary; console logs indicate missing ColorMode context on icon button
- Ports are dynamically reassigned; console displayed live URLs; file may lag until restart
- Browser tool not available; Playwright Inspector (PWDEBUG=1) fulfills request for dev tools
- 41 tests added covering generator, integration hub, cross-browser, accessibility

## Links
- tests/e2e/README.md
- docs/testing/E2E_TESTING_GUIDE.md
- PLAYWRIGHT_QUICKSTART.md
