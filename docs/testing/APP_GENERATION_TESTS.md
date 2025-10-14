# App Generation Tests

## Overview

Comprehensive integration tests for the Proto-DDF app generation functionality.

## Test Coverage

### TestAppGeneration (8 tests)

Tests the core app generation functionality and file structure.

#### 1. `test_generated_app_structure`
- ✅ Verifies all required files exist
- ✅ Checks directory structure is correct
- **Files checked:** `rxconfig.py`, `requirements.txt`, `run.sh`, `.gitignore`, `__init__.py`, main app file

#### 2. `test_generated_app_rxconfig`
- ✅ Verifies rxconfig.py has all required parameters
- ✅ Checks `app_name`, `app_module_import`, `backend_port`, `frontend_port`
- **Critical check:** Module import path must match actual file structure

#### 3. `test_generated_app_main_file`
- ✅ Verifies main Python file has correct Reflex structure
- **Checks:**
  - `import reflex as rx`
  - `class State(rx.State)`
  - `def index() -> rx.Component`
  - `app = rx.App()`
  - `app.add_page(index)`

#### 4. `test_generated_app_requirements`
- ✅ Verifies `requirements.txt` includes reflex dependency

#### 5. `test_generated_app_run_script`
- ✅ Verifies `run.sh` is executable (chmod +x)
- ✅ Checks script includes:
  - Bash shebang
  - Virtual environment creation
  - Dependency installation
  - Reflex run command

#### 6. `test_generated_app_gitignore`
- ✅ Verifies `.gitignore` includes all important patterns
- **Patterns checked:** `venv/`, `__pycache__/`, `*.pyc`, `.web/`, `*.log`

#### 7. `test_generated_app_compiles`
- ✅ Verifies the generated app can be imported without errors
- Uses Python subprocess to import the module

#### 8. `test_port_assignment`
- ✅ Verifies ports are in valid range (3000-5000)
- ✅ Checks backend and frontend ports are different
- ✅ Verifies frontend port = backend port + 1

### TestAppNaming (2 tests)

Tests app naming conventions and normalization.

#### 1. `test_app_name_normalization`
- ✅ Verifies spaces in project names are converted to underscores
- ✅ Ensures no directories with spaces are created

#### 2. `test_module_naming_consistency`
- ✅ Verifies naming is consistent across:
  - Directory names
  - File names
  - Module import paths
  - rxconfig references

### TestGeneratedAppContent (2 tests)

Tests the content of generated apps.

#### 1. `test_app_displays_project_name`
- ✅ Verifies the original project name appears in the generated UI

#### 2. `test_app_displays_description`
- ✅ Verifies the project description appears in the generated UI

## Running the Tests

### Run all generation tests:
```bash
python -m pytest tests/integration/test_app_generation.py -v
```

### Run specific test class:
```bash
python -m pytest tests/integration/test_app_generation.py::TestAppGeneration -v
```

### Run specific test:
```bash
python -m pytest tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_structure -v
```

### Run with coverage:
```bash
python -m pytest tests/integration/test_app_generation.py --cov=proto_ddf_app.generator --cov-report=html
```

## Test Results

**Last Run:** All 12 tests passed ✅

```
============================= test session starts ==============================
platform darwin -- Python 3.13.7, pytest-8.4.2, pluggy-1.6.0
collected 12 items

tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_structure PASSED [  8%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_rxconfig PASSED [ 16%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_main_file PASSED [ 25%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_requirements PASSED [ 33%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_run_script PASSED [ 41%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_gitignore PASSED [ 50%]
tests/integration/test_app_generation.py::TestAppGeneration::test_generated_app_compiles PASSED [ 58%]
tests/integration/test_app_generation.py::TestAppGeneration::test_port_assignment PASSED [ 66%]
tests/integration/test_app_generation.py::TestAppNaming::test_app_name_normalization PASSED [ 75%]
tests/integration/test_app_generation.py::TestAppNaming::test_module_naming_consistency PASSED [ 83%]
tests/integration/test_app_generation.py::TestGeneratedAppContent::test_app_displays_project_name PASSED [ 91%]
tests/integration/test_app_generation.py::TestGeneratedAppContent::test_app_displays_description PASSED [100%]

============================== 12 passed in 0.50s
```

## Known Issues & Fixes

### Issue 1: Missing `app_module_import` (FIXED ✅)
**Problem:** Generated apps failed with `ModuleNotFoundError`
**Solution:** Added `app_module_import` parameter to rxconfig.py generation
**Fix Location:** `proto_ddf_app/generator.py` line 156

### Issue 2: Dictionary creation bug (FIXED ✅)
**Problem:** Used `{{` instead of `{` for dictionary creation
**Solution:** Fixed f-string escaping
**Fix Location:** `proto_ddf_app/generator.py` line 209

### Issue 3: Filename literal (FIXED ✅)
**Problem:** Created file named `{app_name}.py` literally
**Solution:** Fixed f-string syntax in Path creation
**Fix Location:** `proto_ddf_app/generator.py` line 147

## Generated App Structure

```
generated/
└── test_stock_market/
    ├── .gitignore                      # Git ignore patterns
    ├── requirements.txt                # Python dependencies
    ├── run.sh                          # Executable startup script
    ├── rxconfig.py                     # Reflex configuration
    └── test_stock_market_app/          # App module
        ├── __init__.py                 # Python package marker
        └── test_stock_market.py        # Main app code
```

## Running Generated Apps

### Option 1: Using the run.sh script (Recommended)
```bash
cd generated/test_stock_market
./run.sh
```

### Option 2: Manual setup
```bash
cd generated/test_stock_market
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
reflex run
```

### Option 3: Using existing venv
```bash
cd generated/test_stock_market
source ../../venv/bin/activate
reflex run
```

## Test App Example

The test app "Test Stock Market" was generated with:
- **Project Name:** Test Stock Market
- **Description:** An app to analyze stock market trends
- **Frontend Port:** 3144
- **Backend Port:** 3143

### Expected Behavior

When running the app, you should see:
1. ✅ Beautiful gradient heading with project name
2. ✅ Project description displayed prominently
3. ✅ "Getting Started" card with instructions
4. ✅ Dark/Light mode toggle in top-right
5. ✅ State message: "Hello from Test Stock Market!"

## Continuous Integration

These tests should be run:
- ✅ Before every commit (pre-commit hook)
- ✅ On every PR (GitHub Actions)
- ✅ Before deployment (CI/CD pipeline)

## Future Test Improvements

- [ ] Add tests for error handling (empty name, duplicate names)
- [ ] Add tests for special characters in project names
- [ ] Add tests for long project names
- [ ] Add end-to-end tests that actually run generated apps
- [ ] Add performance tests for generation speed
- [ ] Add tests for template selection
- [ ] Add tests for custom configurations
