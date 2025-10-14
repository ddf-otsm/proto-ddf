# 🎭 How to Run Playwright E2E Tests

## ✅ Setup Complete!

Your Playwright test infrastructure is ready with:
- ✅ 60+ E2E tests covering all critical user journeys
- ✅ Chromium browser installed
- ✅ pytest-playwright configured
- ✅ Auto-detection of server status

---

## 🚀 Running Tests (3 Simple Steps)

### Step 1: Start the Reflex Server

**Terminal 1:**
```bash
cd /Users/luismartins/local_repos/proto-ddf
reflex run
```

**Wait for this message:**
```
App running at: http://0.0.0.0:4692
```

---

### Step 2: Run Tests

**Terminal 2:**

#### Option A: Run with Browser Visible (Best for Debugging)
```bash
cd /Users/luismartins/local_repos/proto-ddf
pytest tests/e2e/ -v --headed
```

You'll see the browser open and watch the tests interact with your app!

#### Option B: Run Headless (Faster)
```bash
cd /Users/luismartins/local_repos/proto-ddf
pytest tests/e2e/ -v
```

#### Option C: Run Specific Test
```bash
# Test just the home page
pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage -v --headed

# Test app generation
pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration -v --headed

# Test Integration Hub (requires Integration Hub running)
pytest tests/e2e/test_integration_hub.py -v --headed
```

---

## 🐛 Debugging Tests

### See Tests in Slow Motion
```bash
pytest tests/e2e/ -v --headed --slowmo 1000
```

### Use Playwright Inspector (Step-by-Step)
```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v
```

This opens an interactive debugger where you can:
- Step through each action
- Inspect elements
- See the browser state
- **This is like using dev tools!**

### View Screenshots of Failed Tests
```bash
ls tests/e2e/screenshots/
```

Failed tests automatically capture screenshots!

---

## 📊 Test Coverage

### All Tests (60+)
```bash
pytest tests/e2e/ -v
```

### By Category
```bash
# Generator interface (19 tests)
pytest tests/e2e/test_generator_app.py -v

# Integration Hub (18 tests - requires Integration Hub running)
pytest tests/e2e/test_integration_hub.py -v

# Cross-browser (6 tests)
pytest tests/e2e/test_cross_browser.py -v

# Accessibility (10 tests)
pytest tests/e2e/test_accessibility.py -v
```

---

## 🔧 Common Issues & Fixes

### Issue: "Server is not running"
**Fix:** Start the server in Terminal 1:
```bash
reflex run
```

### Issue: Port conflicts
**Fix:**
```bash
# Kill process on port
lsof -ti:4692 | xargs kill -9

# Reset port config
rm config/.port_config.json
reflex run
```

### Issue: Tests failing
**Fix:** Run with browser visible to see what's happening:
```bash
pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage -v --headed
```

### Issue: Want to see dev tools
**Fix:** Use Playwright Inspector:
```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::test_name -v
```

---

## 🎯 Quick Smoke Test

Test if everything works:

```bash
# Terminal 1: Start server
reflex run

# Terminal 2: Run quick test
pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v --headed
```

Should see: `✅ Generator home page loaded successfully`

---

## 📈 Generate HTML Report

```bash
pytest tests/e2e/ -v --html=test-report.html --self-contained-html
```

Then open `test-report.html` in your browser!

---

## 💡 Pro Tips

1. **Always use `--headed` first** to see what's happening
2. **Use `--slowmo 1000`** to slow down actions for demos
3. **Use `PWDEBUG=1`** to step through tests like a debugger
4. **Check screenshots** in `tests/e2e/screenshots/` after failures
5. **Run specific tests** to save time during development

---

## 🎓 Next Steps

1. **Start the server**: `reflex run`
2. **Run a quick test**: `pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage -v --headed`
3. **Watch the magic happen!** 🎉

---

**For more details, see:**
- `PLAYWRIGHT_QUICKSTART.md` - Quick reference
- `docs/testing/E2E_TESTING_GUIDE.md` - Comprehensive guide
- `E2E_TEST_SETUP_COMPLETE.md` - What was created

**Happy Testing!** 🚀
