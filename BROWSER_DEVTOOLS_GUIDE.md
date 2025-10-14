# 🌐 Using Browser + Dev Tools with Playwright

## 🎯 What You Asked For: Browser with Dev Tools

**You have it!** Playwright Inspector provides exactly what you need:
- Real browser window showing your app
- Inspector panel (like Chrome DevTools)
- Step-by-step test execution
- Element inspection
- Network monitoring
- Console logs

---

## 🚀 How to Open Browser + Dev Tools

### Method 1: Quick Script (Easiest)

```bash
# Terminal 1: Start server
reflex run

# Terminal 2: Run with dev tools
./run_test_with_devtools.sh
```

This will open:
```
┌─────────────────────────────────────┐
│  🌐 Browser Window                  │
│  Your app running                   │
│  (http://localhost:4692)            │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  🔍 Playwright Inspector            │
│  (Your Dev Tools)                   │
│                                     │
│  [▶ Record]  [⏸ Pause]  [▶ Step]  │
│                                     │
│  Source Code:                       │
│  ├── page.goto("...")               │
│  ├── page.locator("...")            │
│  └── expect(...).to_be_visible()    │
│                                     │
│  Elements:                          │
│  ├── <html>                         │
│  │   ├── <body>                     │
│  │   └── <div>...</div>             │
│                                     │
│  Console:                           │
│  └── Test logs appear here          │
└─────────────────────────────────────┘
```

---

### Method 2: Manual Command

```bash
# Terminal 1
reflex run

# Terminal 2
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorHomePage::test_page_loads -v
```

---

### Method 3: Run ALL Tests with Dev Tools

```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py -v
```

---

## 🎮 Using the Playwright Inspector

### When it opens, you'll see:

#### 1. **Browser Window** (Left Side)
- Your actual app running
- You can interact with it
- See the test actions happening live

#### 2. **Inspector Panel** (Right Side)
- **Recorder**: Record new actions
- **Source**: See test code
- **Console**: View logs
- **Network**: Monitor requests
- **Locator**: Pick elements

#### 3. **Control Bar** (Top)
```
[▶ Resume] [⏸ Pause] [▶ Step Over] [↓ Step Into] [↑ Step Out]
```

---

## 🔍 What You Can Do

### 1. Step Through Tests
```
Click "Step Over" (▶) to execute one line at a time
Watch the browser respond to each action
```

### 2. Inspect Elements
```
Click the "Pick Locator" button
Hover over elements in the browser
See the selector code automatically
```

### 3. View Console Logs
```
All console.log() from your app appear here
Test logs also visible
```

### 4. Check Network
```
See all API calls
View request/response data
Check timing
```

### 5. Modify Tests Live
```
Pause execution
Try different selectors
Resume when ready
```

---

## 🎬 Complete Workflow Example

### Test the Generator Interface

```bash
# Terminal 1
cd /Users/luismartins/local_repos/proto-ddf
reflex run

# Terminal 2
cd /Users/luismartins/local_repos/proto-ddf
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration::test_generate_app_complete_flow -v
```

**What happens:**
1. Browser opens showing your app
2. Inspector opens alongside
3. Test pauses at first action
4. You can:
   - Step through each action
   - See element selections
   - View state changes
   - Inspect DOM
   - Check console logs
5. If error occurs, you see exact line

---

## 🐛 Debugging Failed Tests

### Step 1: Run with Inspector
```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::test_that_failed -v
```

### Step 2: Step Through
- Click "Step Over" to execute line by line
- Watch where it fails
- Check the browser state
- Look at console for errors

### Step 3: Try Different Selectors
```python
# In Inspector, test different selectors:
page.locator("text=Button")       # Text-based
page.locator("button.class-name") # CSS
page.locator("#element-id")       # ID
page.locator("//xpath")           # XPath
```

### Step 4: Fix the Test
- Copy working selector from Inspector
- Update test file
- Run again to verify

---

## 📊 Testing All User Journeys with Dev Tools

### Journey 1: App Generation
```bash
PWDEBUG=1 pytest tests/e2e/test_generator_app.py::TestGeneratorAppGeneration -v
```

**What you'll see:**
1. Page loads
2. Form appears
3. User types project name
4. User types description
5. Clicks "Generate App"
6. Success message appears
7. New app in list

### Journey 2: Data Integration
```bash
# First, start Integration Hub in Terminal 3
cd generated/netsuite_integration_hub && ./run.sh

# Then run with dev tools
PWDEBUG=1 pytest tests/e2e/test_integration_hub.py::TestIntegrationHubConnectionFlow::test_complete_csv_integration_flow -v
```

**What you'll see:**
1. Integration Hub loads
2. CSV source selected
3. Connection initiated
4. Progress bar animates
5. Data table appears
6. Fields auto-mapped
7. Sync to NetSuite
8. Success indicators

### Journey 3: Cross-Browser Testing
```bash
# Test in Firefox with dev tools
PWDEBUG=1 pytest tests/e2e/test_cross_browser.py -v --browser firefox
```

---

## 🎨 Advanced Dev Tools Features

### 1. Record New Actions
```
1. Click "Record" in Inspector
2. Interact with your app in browser
3. Code generates automatically
4. Copy to your test file
```

### 2. Take Screenshots at Any Step
```
1. Pause test at interesting point
2. Manually take screenshot
3. Or: Tests auto-screenshot on failure
```

### 3. Slow Motion Mode
```bash
# See actions slowly
pytest tests/e2e/ -v --headed --slowmo 1000
```

### 4. Video Recording
```bash
# Record entire test run
pytest tests/e2e/ -v --video=on
```

---

## 🔧 Troubleshooting

### Issue: Inspector doesn't open
```bash
# Make sure PWDEBUG=1 is set
PWDEBUG=1 pytest tests/e2e/test_generator_app.py -v
```

### Issue: Browser closes too fast
```bash
# Use --headed to keep browser open
pytest tests/e2e/ -v --headed
```

### Issue: Want to see network calls
```
1. Open Inspector
2. Click "Network" tab
3. Step through test
4. See all requests/responses
```

### Issue: Element not found
```
1. Pause test at failure
2. Open Inspector element picker
3. Click element in browser
4. See correct selector
5. Update test with new selector
```

---

## 💡 Pro Tips

### 1. Always Start with PWDEBUG
```bash
PWDEBUG=1 pytest tests/e2e/test_name -v
```
This is your "browser + dev tools" mode!

### 2. Use Locator Picker
Click the target icon in Inspector to pick elements visually

### 3. Check Console First
Many errors show in console before tests fail

### 4. Step Through Slowly
Don't just hit "Resume" - step through to understand flow

### 5. Test One Journey at a Time
Focus on one user journey per debugging session

---

## 📚 Quick Reference

| What You Want | Command |
|---------------|---------|
| Browser + Dev Tools | `PWDEBUG=1 pytest tests/e2e/test_name -v` |
| Visible Browser | `pytest tests/e2e/ -v --headed` |
| Slow Motion | `pytest tests/e2e/ -v --headed --slowmo 1000` |
| All Tests | `pytest tests/e2e/ -v` |
| Specific Test | `pytest tests/e2e/test_file.py::TestClass::test_method -v` |
| With HTML Report | `pytest tests/e2e/ -v --html=report.html` |

---

## 🎯 Your Next Steps

1. **Terminal 1:** `reflex run`
2. **Terminal 2:** `./run_test_with_devtools.sh`
3. **Watch:** Browser + Inspector open
4. **Step through:** Use controls to debug
5. **Fix issues:** Update tests based on what you see

---

## ✨ Summary

You asked for "Browser tool with dev tools opened" - **you have it!**

```bash
PWDEBUG=1 pytest tests/e2e/test_name -v
```

This gives you:
- ✅ Real browser window
- ✅ Playwright Inspector (dev tools)
- ✅ Step-by-step execution
- ✅ Element inspection
- ✅ Console logs
- ✅ Network monitoring
- ✅ Everything you need to debug!

**Start testing now!** 🚀
