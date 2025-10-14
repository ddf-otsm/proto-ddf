# Proto-DDF E2E Testing Guide

## 📋 Overview

This guide covers the comprehensive end-to-end (E2E) testing setup for Proto-DDF using Playwright. The test suite validates critical user journeys across both the generator interface and generated applications.

## 🎯 Test Coverage Summary

### Total Test Count: **60+ E2E Tests**

#### Generator App Tests (19 tests)
✅ Home page loading and structure
✅ App generation workflow
✅ Generated apps management
✅ Template browsing
✅ UI responsiveness

#### Integration Hub Tests (18 tests)
✅ Data source selection (6 sources)
✅ Connection workflow
✅ Field mapping automation
✅ Data synchronization
✅ Statistics tracking
✅ Integration logs
✅ Reset functionality

#### Cross-Browser Tests (6 tests)
✅ Chromium compatibility
✅ Firefox compatibility
✅ WebKit (Safari) compatibility

#### Accessibility Tests (10+ tests)
✅ Keyboard navigation
✅ Screen reader compatibility
✅ Color contrast
✅ ARIA landmarks
✅ Form label association

## 🚀 Quick Start

### 1. Install Playwright

```bash
# Run the setup script
./scripts/setup_e2e_tests.sh
```

This will:
- Install Python test dependencies
- Install Playwright browsers (Chromium, Firefox, WebKit)
- Create necessary test directories
- Verify port configuration

### 2. Start the Application

```bash
# Terminal 1: Start the generator
reflex run
```

For Integration Hub tests:
```bash
# Terminal 2: Start the Integration Hub
cd generated/netsuite_integration_hub
./run.sh
```

### 3. Run Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Or use the convenience script
./scripts/run_e2e_tests.sh
```

## 📝 Test Scenarios

### Critical User Journey 1: App Generation

**Steps:**
1. User opens generator interface
2. Enters project name and description
3. Clicks "Generate App" button
4. App generates successfully
5. New app appears in generated apps list

**Test:** `test_generator_app.py::TestGeneratorAppGeneration::test_generate_app_complete_flow`

### Critical User Journey 2: Data Integration Flow

**Steps:**
1. User selects CSV data source
2. Clicks "Connect to Source"
3. Connection succeeds, data preview shown
4. Clicks "Auto-Map Fields"
5. Field mapping displayed
6. Clicks "Sync to NetSuite"
7. Data syncs successfully
8. Statistics updated

**Test:** `test_integration_hub.py::TestIntegrationHubConnectionFlow::test_complete_csv_integration_flow`

### Critical User Journey 3: Multi-Source Integration

**Steps:**
1. Complete integration with CSV
2. Click "Reset"
3. Select different source (JSON API)
4. Repeat integration workflow
5. Verify statistics accumulate

**Test:** Multiple tests across `test_integration_hub.py`

## 🔧 Advanced Usage

### Run Specific Tests

```bash
# Run only generator tests
pytest tests/e2e/test_generator_app.py -v

# Run only Integration Hub tests
pytest tests/e2e/test_integration_hub.py -v

# Run only accessibility tests
pytest tests/e2e/test_accessibility.py -v

# Run specific test class
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration -v

# Run specific test
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration::test_generate_app_complete_flow -v
```

### Debugging Tests

#### Run with Browser Visible

```bash
pytest tests/e2e/ -v --headed
```

#### Run with Slow Motion

```bash
pytest tests/e2e/ -v --headed --slowmo 1000
```

#### Use Playwright Inspector

```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::test_name -v
```

#### View Test Screenshots

Screenshots are automatically captured on test failure:
```bash
ls tests/e2e/screenshots/
```

### Test Different Browsers

```bash
# Chromium (default)
pytest tests/e2e/ -v --browser chromium

# Firefox
pytest tests/e2e/ -v --browser firefox

# WebKit (Safari)
pytest tests/e2e/ -v --browser webkit

# Run cross-browser tests
pytest tests/e2e/test_cross_browser.py -v
```

## 📊 Test Reports

### Generate HTML Report

```bash
pytest tests/e2e/ -v --html=test-report.html --self-contained-html
```

Then open `test-report.html` in your browser.

### View Coverage

```bash
pytest tests/e2e/ --cov=proto_ddf_app --cov-report=html
```

## 🏗️ Test Architecture

### Test Structure

```
tests/e2e/
├── __init__.py                    # Package init
├── conftest.py                    # Pytest fixtures and configuration
├── test_generator_app.py          # Generator interface tests
├── test_integration_hub.py        # Integration Hub tests
├── test_cross_browser.py          # Cross-browser compatibility
├── test_accessibility.py          # Accessibility tests
├── screenshots/                   # Test screenshots (auto-generated)
└── README.md                      # E2E test documentation
```

### Key Fixtures (conftest.py)

```python
@pytest.fixture
def base_url(port_config):
    """Generator app URL"""

@pytest.fixture
def integration_hub_url(port_config):
    """Integration Hub app URL"""

@pytest.fixture
def page(context):
    """New browser page for each test"""
```

### Test Naming Convention

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`

## 🐛 Troubleshooting

### Issue: Server not running

**Error:** `Server is not running on port XXXX`

**Solution:**
```bash
# Start the Reflex server
reflex run
```

### Issue: Port conflicts

**Error:** `Address already in use`

**Solution:**
```bash
# Check what's using the port
lsof -ti:3001 | xargs kill -9

# Or restart with new ports
rm config/.port_config.json
reflex run
```

### Issue: Playwright not installed

**Error:** `playwright: command not found`

**Solution:**
```bash
./scripts/setup_e2e_tests.sh
```

### Issue: Browser not found

**Error:** `Executable doesn't exist`

**Solution:**
```bash
playwright install chromium
playwright install firefox
playwright install webkit
```

### Issue: Tests timing out

**Solution:**
```bash
# Increase timeout in pytest.ini or use flag
pytest tests/e2e/ --timeout=600
```

### Issue: Integration Hub tests skipped

**Reason:** Integration Hub is not running

**Solution:**
```bash
cd generated/netsuite_integration_hub
./run.sh
```

## 📈 Performance Benchmarks

### Expected Test Times

- **Generator tests**: ~30-60 seconds
- **Integration Hub tests**: ~60-120 seconds (includes simulated delays)
- **Cross-browser tests**: ~45-90 seconds
- **Accessibility tests**: ~20-40 seconds

**Total suite**: ~3-5 minutes

### Optimization Tips

1. Run tests in parallel:
   ```bash
   pytest tests/e2e/ -n auto
   ```

2. Skip slow tests during development:
   ```bash
   pytest tests/e2e/ -v -m "not slow"
   ```

3. Run only changed tests:
   ```bash
   pytest tests/e2e/ --lf  # Last failed
   pytest tests/e2e/ --ff  # Failed first
   ```

## 🔐 CI/CD Integration

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
        run: pytest tests/e2e/ -v --html=test-report.html

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-report.html

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/e2e/screenshots/
```

### GitLab CI Example

```yaml
e2e-tests:
  stage: test
  image: mcr.microsoft.com/playwright/python:v1.40.0
  script:
    - pip install -r requirements.txt
    - reflex run &
    - sleep 10
    - pytest tests/e2e/ -v --html=test-report.html
  artifacts:
    when: always
    paths:
      - test-report.html
      - tests/e2e/screenshots/
```

## 📚 Best Practices

### 1. Keep Tests Independent

Each test should be able to run in isolation without depending on other tests.

✅ Good:
```python
def test_select_source(self, page, integration_hub_url):
    page.goto(integration_hub_url)
    # Complete test in one function
```

❌ Bad:
```python
# Don't rely on state from previous tests
source_selected = False

def test_1_select_source():
    global source_selected
    source_selected = True

def test_2_connect_source():
    assert source_selected  # Bad!
```

### 2. Use Meaningful Selectors

Prefer text-based selectors over CSS:

✅ Good:
```python
page.locator("button", has_text="Connect to Source").click()
```

❌ Bad:
```python
page.locator("#btn-xyz-123").click()
```

### 3. Wait for State, Not Time

✅ Good:
```python
expect(page.locator("text=Success")).to_be_visible(timeout=10000)
```

❌ Bad:
```python
time.sleep(5)  # Avoid fixed sleeps
```

### 4. Handle Errors Gracefully

```python
try:
    page.goto(url, timeout=15000)
    # Test logic
except Exception as e:
    logger.warning(f"Test skipped: {e}")
    pytest.skip("Service not available")
```

### 5. Clean Up After Tests

```python
@pytest.fixture(autouse=True)
def cleanup(self):
    yield
    # Cleanup code here
```

## 🎓 Learning Resources

- [Playwright Python Docs](https://playwright.dev/python/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Reflex Testing Guide](https://reflex.dev/docs/testing/)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review test logs: `pytest tests/e2e/ -v -s --log-cli-level=DEBUG`
3. Check screenshots in `tests/e2e/screenshots/`
4. Review the test code in `tests/e2e/`

## 🔄 Continuous Improvement

### Adding New Tests

1. Identify critical user journey
2. Create test in appropriate file
3. Follow existing test patterns
4. Add to this documentation
5. Ensure tests pass locally
6. Submit PR with tests

### Test Maintenance

- Review and update tests when UI changes
- Keep selectors up to date
- Maintain timeout values
- Update documentation
- Monitor test execution time

---

**Last Updated:** October 2025
**Test Suite Version:** 1.0
**Total Test Coverage:** 60+ E2E tests
