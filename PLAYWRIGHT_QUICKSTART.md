# 🎭 Playwright E2E Tests - Quick Reference

## ⚡ Quick Setup (3 Steps)

```bash
# 1. Install Playwright & browsers
./scripts/setup_e2e_tests.sh

# 2. Start the app
reflex run

# 3. Run tests
pytest tests/e2e/ -v
```

## 📋 Common Commands

### Running Tests

```bash
# All E2E tests
pytest tests/e2e/ -v

# Specific test file
pytest tests/e2e/test_generator_app.py -v

# Specific test
pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v

# With browser visible
pytest tests/e2e/ -v --headed

# Slow motion (for demos)
pytest tests/e2e/ -v --headed --slowmo 1000

# Specific browser
pytest tests/e2e/ -v --browser firefox  # or chromium, webkit

# Generate HTML report
pytest tests/e2e/ -v --html=report.html --self-contained-html
```

### Debugging

```bash
# Show browser + slow motion
pytest tests/e2e/ -v --headed --slowmo 500

# Playwright Inspector (step through)
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::test_name -v

# Verbose logging
pytest tests/e2e/ -v -s --log-cli-level=DEBUG

# Last failed tests only
pytest tests/e2e/ --lf

# Failed first, then rest
pytest tests/e2e/ --ff
```

## 🎯 Test Coverage

| Category | Tests | File |
|----------|-------|------|
| Generator UI | 19 | `test_generator_app.py` |
| Integration Hub | 18 | `test_integration_hub.py` |
| Cross-Browser | 6 | `test_cross_browser.py` |
| Accessibility | 10+ | `test_accessibility.py` |
| **TOTAL** | **60+** | |

## 🚦 Critical Journeys

### ✅ Journey 1: App Generation
```bash
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration::test_generate_app_complete_flow -v
```

### ✅ Journey 2: Data Integration
```bash
pytest tests/e2e/test_integration_hub.py::TestIntegrationHubConnectionFlow::test_complete_csv_integration_flow -v
```

### ✅ Journey 3: Cross-Browser
```bash
pytest tests/e2e/test_cross_browser.py -v
```

### ✅ Journey 4: Accessibility
```bash
pytest tests/e2e/test_accessibility.py -v
```

## 🔧 Troubleshooting

### ❌ Server not running
```bash
# Start in another terminal
reflex run
```

### ❌ Port conflicts
```bash
# Kill process on port
lsof -ti:3001 | xargs kill -9

# Reset ports
rm config/.port_config.json
reflex run
```

### ❌ Playwright not installed
```bash
./scripts/setup_e2e_tests.sh
```

### ❌ Browser not found
```bash
playwright install chromium firefox webkit
```

### ❌ Tests timing out
```bash
# Increase timeout
pytest tests/e2e/ --timeout=600
```

## 📂 File Locations

- **Tests**: `tests/e2e/`
- **Screenshots**: `tests/e2e/screenshots/`
- **Config**: `pytest.ini`, `playwright.config.py`
- **Fixtures**: `tests/e2e/conftest.py`
- **Scripts**: `scripts/setup_e2e_tests.sh`, `scripts/run_e2e_tests.sh`

## 📊 Expected Performance

- Generator tests: 30-60s
- Integration Hub: 60-120s
- Cross-browser: 45-90s
- Accessibility: 20-40s
- **Full suite: 3-5 minutes**

## 🎨 Convenience Scripts

```bash
# Setup everything
./scripts/setup_e2e_tests.sh

# Run with options
./scripts/run_e2e_tests.sh --headed
./scripts/run_e2e_tests.sh --browser firefox
./scripts/run_e2e_tests.sh --slowmo 1000
./scripts/run_e2e_tests.sh --file test_generator_app.py
```

## 📖 Full Documentation

- **Setup Guide**: `tests/e2e/README.md`
- **Comprehensive Guide**: `docs/testing/E2E_TESTING_GUIDE.md`
- **Complete Summary**: `E2E_TEST_SETUP_COMPLETE.md`

## 💡 Pro Tips

1. **Run tests with `--headed` first** to see what's happening
2. **Use `--slowmo` for demos** or understanding test flow
3. **Check screenshots on failure**: `ls tests/e2e/screenshots/`
4. **Use PWDEBUG for debugging**: `PWDEBUG=1 pytest ...`
5. **Generate HTML reports** for sharing results

## 🎯 Quick Test

```bash
# Quick smoke test
pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage -v

# Should see:
# ✅ test_page_loads
# ✅ test_page_title
# ✅ test_statistics_visible
# ✅ test_color_mode_button
```

---

**Need help?** See `docs/testing/E2E_TESTING_GUIDE.md`
