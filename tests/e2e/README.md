# Proto-DDF E2E Tests

Comprehensive end-to-end tests using Playwright for Proto-DDF applications.

## Overview

This test suite covers critical user journeys for:
1. **Proto-DDF Generator** - The main app generation interface
2. **NetSuite Integration Hub** - The sample generated application

## Test Coverage

### Generator App Tests (`test_generator_app.py`)

#### TestGeneratorHomePage
- ✅ Page loads successfully
- ✅ Correct page title
- ✅ Statistics cards visible
- ✅ Color mode toggle present

#### TestGeneratorAppGeneration
- ✅ App generation form visible
- ✅ Error handling for missing project name
- ✅ Complete app generation flow
- ✅ Generated app appears in list

#### TestGeneratorGeneratedApps
- ✅ Generated apps section visible
- ✅ NetSuite Integration Hub listed
- ✅ Open buttons present

#### TestGeneratorTemplates
- ✅ Templates section visible
- ✅ All 5 template cards visible
- ✅ Use Template buttons present

#### TestGeneratorResponsiveness
- ✅ Page scrollable
- ✅ Inputs are interactive

### Integration Hub Tests (`test_integration_hub.py`)

#### TestIntegrationHubHomePage
- ✅ Page loads successfully
- ✅ Correct page title
- ✅ Statistics dashboard visible

#### TestIntegrationHubDataSources
- ✅ Data source section visible
- ✅ All 6 data sources visible
- ✅ Source selection works

#### TestIntegrationHubConnectionFlow
- ✅ Complete CSV integration flow (select → connect → map → sync)
- ✅ Progress indicators shown
- ✅ Success messages displayed

#### TestIntegrationHubDataDisplay
- ✅ Source data table appears after connection
- ✅ Field mapping displayed after auto-map
- ✅ Synced records displayed after sync

#### TestIntegrationHubLogsAndStatistics
- ✅ Integration logs appear
- ✅ Statistics update after sync

#### TestIntegrationHubReset
- ✅ Reset button visible
- ✅ Reset clears integration
- ✅ Clear statistics button present

### Cross-Browser Tests (`test_cross_browser.py`)
- ✅ Chromium compatibility
- ✅ Firefox compatibility
- ✅ WebKit (Safari) compatibility

## Setup

### 1. Install Dependencies

```bash
# Install test dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 2. Start the Application

The tests expect the Reflex application to be running. Start it before running tests:

```bash
# In terminal 1: Start the generator
reflex run
```

If testing the Integration Hub, also start it:

```bash
# In terminal 2: Start the Integration Hub
cd generated/netsuite_integration_hub
./run.sh
```

## Running Tests

### Run All E2E Tests

```bash
pytest tests/e2e/ -v
```

### Run Specific Test File

```bash
# Generator tests only
pytest tests/e2e/test_generator_app.py -v

# Integration Hub tests only
pytest tests/e2e/test_integration_hub.py -v

# Cross-browser tests
pytest tests/e2e/test_cross_browser.py -v
```

### Run Specific Test Class

```bash
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration -v
```

### Run Specific Test

```bash
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration::test_generate_app_complete_flow -v
```

### Run with Browser Visible (for debugging)

```bash
pytest tests/e2e/ -v --headed
```

### Run with Slow Motion (for debugging)

```bash
pytest tests/e2e/ -v --headed --slowmo 1000
```

### Generate Test Report

```bash
pytest tests/e2e/ -v --html=test-report.html --self-contained-html
```

## Test Configuration

### Port Configuration

Tests automatically read port configuration from `config/.port_config.json`. If you need to override:

```python
# In conftest.py, modify the get_port_config() function
```

### Timeouts

Default timeouts are set in `conftest.py`:
- Page load: 15 seconds
- Element wait: 10 seconds
- Network idle: 5 seconds

Adjust as needed for slower systems.

### Screenshots

Failed tests automatically capture screenshots to `tests/e2e/screenshots/`.

## Debugging Tests

### Enable Verbose Logging

```bash
pytest tests/e2e/ -v -s --log-cli-level=INFO
```

### Run in Headed Mode

```bash
pytest tests/e2e/ --headed
```

### Use Playwright Inspector

```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::test_name -v
```

### Take Manual Screenshots

```python
# In your test
from conftest import take_screenshot

take_screenshot(page, "debug_screenshot")
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install --with-deps

      - name: Start Reflex app
        run: |
          reflex run &
          sleep 10

      - name: Run E2E tests
        run: pytest tests/e2e/ -v

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/e2e/screenshots/
```

## Common Issues

### Issue: Server not running
**Solution**: Ensure the Reflex app is running before tests:
```bash
reflex run
```

### Issue: Port conflicts
**Solution**: Check `config/.port_config.json` and kill any processes using those ports:
```bash
lsof -ti:PORT_NUMBER | xargs kill -9
```

### Issue: Tests timing out
**Solution**: Increase timeouts in `conftest.py` or use `--timeout` flag:
```bash
pytest tests/e2e/ --timeout=60
```

### Issue: Browser not found
**Solution**: Reinstall Playwright browsers:
```bash
playwright install
```

## Best Practices

1. **Run tests in CI/CD**: Automate E2E tests in your deployment pipeline
2. **Keep tests independent**: Each test should be able to run in isolation
3. **Use meaningful selectors**: Prefer text-based selectors over CSS classes
4. **Handle async operations**: Always wait for network idle and element visibility
5. **Clean up after tests**: Reset state between tests to avoid interference
6. **Take screenshots on failure**: Helps debug issues in headless mode

## Contributing

When adding new tests:
1. Follow existing test structure and naming conventions
2. Add appropriate assertions and logging
3. Handle errors gracefully (skip if service not running)
4. Update this README with new test coverage
5. Ensure tests pass locally before committing

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Reflex Documentation](https://reflex.dev/docs/)
