# Makefile Guide

## Overview

Proto-DDF uses a Makefile to standardize common development tasks. The Makefile provides a simple interface for running, testing, and managing the project.

## Quick Start

```bash
# Show all available commands
make help

# Run the application
make run

# Run tests
make test

# Check project status
make status
```

## Available Commands

### Application Commands

#### `make run`
Run the Proto-DDF generator application.

```bash
make run
```

You can pass arguments to the underlying script:
```bash
make run ARGS="--param1=value1 -p2 v2"
```

**Aliases:**
- `make dev` - Same as `make run`

#### `make run-generated APP=app_name`
Run a specific generated application.

```bash
# Run the test stock market app
make run-generated APP=test_stock_market

# List available apps if no APP specified
make run-generated
```

### Testing Commands

#### `make test`
Run all tests (unit + integration).

```bash
make test
```

#### `make test-unit`
Run only unit tests.

```bash
make test-unit
```

#### `make test-integration`
Run only integration tests.

```bash
make test-integration
```

#### `make test-coverage`
Run tests with coverage report. Generates HTML report in `htmlcov/`.

```bash
make test-coverage

# Open coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Code Quality Commands

#### `make lint`
Run linters (flake8, mypy) on the codebase.

```bash
make lint
```

#### `make format`
Format code using Black.

```bash
make format
```

#### `make check`
Run both linters and tests.

```bash
make check
```

### Setup Commands

#### `make install`
Install all dependencies.

```bash
make install
```

This command:
1. Creates virtual environment (if needed)
2. Upgrades pip
3. Installs Reflex from submodule
4. Installs requirements from `requirements.txt`

#### `make init`
Initialize the project from scratch.

```bash
make init
```

This command:
1. Cleans all generated files
2. Installs dependencies
3. Sets up the project

### Cleanup Commands

#### `make clean`
Clean up generated files and caches.

```bash
make clean
```

Removes:
- `__pycache__/` directories
- `*.pyc` files
- `*.pyo` files
- `*.egg-info` directories
- `.pytest_cache/` directories
- `.mypy_cache/` directories
- `htmlcov/` directories
- `.coverage` files
- `.web/` directories

#### `make clean-all`
Deep clean including virtual environment and generated apps.

```bash
make clean-all
```

⚠️ **Warning:** This removes:
- Everything in `make clean`
- `venv/` directory
- Generated app virtual environments
- Generated app `.web/` directories

### Information Commands

#### `make status`
Show project status.

```bash
make status
```

Output includes:
- Python version
- Virtual environment status
- Reflex submodule status
- Number of generated apps
- Port configuration

#### `make version`
Show version information for all tools.

```bash
make version
```

Output includes:
- Python version
- Node.js version
- Reflex version

#### `make ports`
Show current port configuration.

```bash
make ports
```

#### `make generated-apps`
List all generated applications with their ports.

```bash
make generated-apps
```

#### `make docs`
Show documentation directory structure.

```bash
make docs
```

### Logging Commands

#### `make logs`
Show recent application logs (last 50 lines).

```bash
make logs
```

#### `make logs-follow`
Follow application logs in real-time (press Ctrl+C to stop).

```bash
make logs-follow
```

## Usage Examples

### Daily Development Workflow

```bash
# Start your day
make status              # Check project status
make run                 # Run the application

# Make changes and test
make format              # Format your code
make lint                # Check for issues
make test                # Run tests

# Before committing
make check               # Run linters and tests
```

### First Time Setup

```bash
# Clone the repository
git clone <repo-url>
cd proto-ddf

# Initialize everything
make init

# Run the application
make run
```

### Testing Workflow

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration

# Get coverage report
make test-coverage
open htmlcov/index.html
```

### Working with Generated Apps

```bash
# List all generated apps
make generated-apps

# Run a specific app
make run-generated APP=test_stock_market

# Check ports being used
make ports
```

### Cleanup Workflow

```bash
# Clean up temporary files
make clean

# Deep clean (includes venv)
make clean-all

# Reinitialize
make init
```

## Passing Arguments

### To run.sh

You can pass arguments to `workflows/run.sh` using the `ARGS` variable:

```bash
make run ARGS="--param1=value1 -p2 v2"
```

This is equivalent to:
```bash
bash workflows/run.sh --param1=value1 -p2 v2
```

### To generated apps

To pass arguments to a generated app:

```bash
# Not directly supported through make
# Use the direct approach:
cd generated/test_stock_market
./run.sh --your-args-here
```

## Customization

### Adding Custom Commands

Edit the `Makefile` to add your own commands:

```makefile
my-custom-command: ## Description of my command
	@echo "Running custom command"
	@# Your commands here
```

### Environment Variables

You can use environment variables with make:

```bash
# Set environment variable and run
ENV_VAR=value make run

# Or export it first
export ENV_VAR=value
make run
```

## Troubleshooting

### Command not found

**Problem:** `make: command not found`

**Solution:** Install make:
```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install make

# Fedora/RHEL
sudo dnf install make
```

### Permission denied

**Problem:** Permission denied when running make commands

**Solution:** Ensure scripts are executable:
```bash
chmod +x workflows/run.sh
chmod +x workflows/test.sh
```

### Virtual environment issues

**Problem:** Commands fail due to venv issues

**Solution:** Recreate virtual environment:
```bash
make clean-all
make init
```

### Port conflicts

**Problem:** Ports already in use

**Solution:** Check and clean up ports:
```bash
make ports           # See what ports are configured
make clean-all       # Clean everything
rm config/.port_config.json  # Reset port config
make run             # Generate new ports
```

## Color Output

The Makefile uses colors for better readability:
- 🔵 **Blue**: Command headers
- 🟢 **Green**: Success messages and available commands
- 🟡 **Yellow**: Information and examples
- 🔴 **Red**: Warnings and errors

To disable colors, you can:
```bash
make run | cat
```

## Best Practices

### DO:
- ✅ Use `make help` to discover available commands
- ✅ Use `make status` to check project health
- ✅ Use `make check` before committing
- ✅ Use `make clean` regularly to keep the project tidy
- ✅ Use `make test` to ensure everything works

### DON'T:
- ❌ Don't manually run scripts when make commands exist
- ❌ Don't skip `make check` before committing
- ❌ Don't use `make clean-all` unless you really need to
- ❌ Don't modify the Makefile without testing your changes

## Integration with CI/CD

The Makefile commands can be used in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Setup
  run: make install

- name: Lint
  run: make lint

- name: Test
  run: make test-coverage

- name: Check
  run: make check
```

## Summary

The Makefile provides a consistent, easy-to-use interface for all common development tasks. Use `make help` to see all available commands, and refer to this guide for detailed usage information.
