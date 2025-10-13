# Debugging Guide - NetSuite Integration Hub

This guide explains how to debug issues in the NetSuite Integration Hub.

## 🐛 Quick Debug

### Run in Debug Mode

```bash
./debug_server.sh
```

This script:
- Clears old logs
- Sets debug environment variables
- Runs Reflex with maximum logging
- Saves all output to `debug_output.log`

### Monitor Logs in Real-Time

In a separate terminal:
```bash
tail -f proto_ddf.log integration_hub.log
```

Or view all logs together:
```bash
tail -f *.log
```

## 📋 Log Files

### proto_ddf.log
**Purpose**: Configuration and framework-level logging

**Contains**:
- Application startup
- Configuration loading
- Framework initialization
- Network binding info

**Example**:
```
2025-10-09 14:25:00 - __main__ - INFO - Loading rxconfig.py
2025-10-09 14:25:00 - __main__ - INFO - Config loaded - Backend: 0.0.0.0:8000, Frontend: 3000
```

### integration_hub.log
**Purpose**: Application-level logging (State methods, business logic)

**Contains**:
- State method calls
- Data processing
- Field mapping operations
- Sync operations
- Error details with stack traces

**Example**:
```
2025-10-09 14:25:10 - proto_ddf_app.proto_ddf_app - INFO - select_source:108 - select_source called with: CSV File
2025-10-09 14:25:10 - proto_ddf_app.proto_ddf_app - DEBUG - select_source:120 - Loaded source fields: ['id', 'name', 'email', 'phone', 'location']
2025-10-09 14:25:15 - proto_ddf_app.proto_ddf_app - INFO - connect_source:131 - connect_source called - selected_source: CSV File
```

### debug_output.log
**Purpose**: Complete server output when running debug_server.sh

**Contains**:
- All console output
- Compilation messages
- Worker messages
- Error messages

## 🔍 Common Issues

### Issue: Worker Crashes

**Symptoms**:
```
[ERROR] Unexpected exit from worker-1
```

**Debug Steps**:

1. Check the last entries in logs:
```bash
tail -50 integration_hub.log
```

2. Look for Python exceptions:
```bash
grep -A 10 "ERROR" integration_hub.log
grep -A 10 "Traceback" integration_hub.log
```

3. Check if it's a specific action:
```bash
grep "called" integration_hub.log | tail -20
```

**Common Causes**:
- Exception in State method (check try-catch blocks)
- Type error (check Var operations)
- Missing data (check conditionals)

### Issue: Can't Access from Network

**Debug Steps**:

1. Check backend is binding to 0.0.0.0:
```bash
grep "backend_host" proto_ddf.log
```

2. Check if ports are open:
```bash
lsof -i :3000 -i :8000
```

3. Check firewall:
```bash
# macOS
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --listapps | grep python

# Linux
sudo ufw status
```

### Issue: Module Import Errors

**Debug Steps**:

1. Check Python path:
```bash
python3 -c "import sys; print('\n'.join(sys.path))"
```

2. Check reflex installation:
```bash
python3 -c "import reflex; print(reflex.__file__)"
# Should point to: .../proto-ddf/reflex/reflex/__init__.py
```

3. Check application import:
```bash
python3 -c "from proto_ddf_app.proto_ddf_app import State; print('OK')"
```

## 🛠️ Advanced Debugging

### Python Debugger (pdb)

Add breakpoints to code:
```python
def select_source(self, source: str):
    import pdb; pdb.set_trace()  # Debugger will stop here
    logger.info(f"select_source called with: {source}")
    ...
```

### Custom Log Levels

Temporarily increase logging for specific areas:

```python
# In proto_ddf_app.py
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Change to DEBUG for more detail
```

### Trace State Changes

Add logging to see when state variables change:
```python
@rx.var
def selected_source(self) -> str:
    logger.debug(f"Getting selected_source: {self._selected_source}")
    return self._selected_source

@selected_source.setter
def selected_source(self, value: str):
    logger.info(f"Setting selected_source: {self._selected_source} -> {value}")
    self._selected_source = value
```

## 📊 Log Analysis

### Find All Errors

```bash
grep -r "ERROR" *.log
```

### Find Specific Method Calls

```bash
grep "select_source called" integration_hub.log
grep "connect_source called" integration_hub.log
grep "sync_to_netsuite called" integration_hub.log
```

### Check Success/Failure Rates

```bash
grep "synced successfully" integration_hub.log | wc -l
grep "sync failed" integration_hub.log | wc -l
```

### View Last Hour of Activity

```bash
# macOS/BSD
tail -100 integration_hub.log | grep "$(date '+%Y-%m-%d %H')"

# Linux
tail -100 integration_hub.log | grep "$(date '+%Y-%m-%d %H')"
```

## 🔬 Performance Profiling

### Time Operations

Add timing to operations:
```python
import time

def sync_to_netsuite(self):
    start = time.time()
    logger.info("Sync started")

    # ... your code ...

    elapsed = time.time() - start
    logger.info(f"Sync completed in {elapsed:.2f} seconds")
```

### Memory Usage

Check memory usage:
```python
import psutil
import os

process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
logger.info(f"Memory usage: {memory_mb:.2f} MB")
```

## 🚨 Error Reporting

### Create Bug Report

When reporting bugs, include:

1. **Log files**:
```bash
# Create a debug package
tar -czf debug_logs_$(date +%Y%m%d_%H%M%S).tar.gz *.log
```

2. **System info**:
```bash
python3 --version
pip show reflex
uname -a
```

3. **Last 100 lines of each log**:
```bash
tail -100 proto_ddf.log > proto_ddf_tail.txt
tail -100 integration_hub.log > integration_hub_tail.txt
```

4. **Steps to reproduce**
5. **Expected vs actual behavior**

## 🧪 Testing Individual Components

### Test State Methods Directly

```python
# test_state.py
from proto_ddf_app.proto_ddf_app import State

state = State()
state.select_source("CSV File")
print(f"Selected: {state.selected_source}")
print(f"Fields: {state.source_fields}")
```

Run:
```bash
python3 test_state.py
```

### Test Field Mapping

```python
# test_mapping.py
from proto_ddf_app.proto_ddf_app import State

state = State()
state.selected_source = "CSV File"
state.source_fields = ["id", "name", "email", "phone", "location"]
state.auto_map_fields()
print(f"Mapping: {state.field_mapping}")
```

## 📝 Logging Best Practices

### When to Log

- **DEBUG**: Detailed info for developers
  - Variable values
  - Loop iterations
  - Function entry/exit

- **INFO**: Important events
  - State changes
  - User actions
  - Successful operations

- **WARNING**: Unexpected but handled
  - Missing optional data
  - Fallback behavior
  - Deprecated features

- **ERROR**: Errors that need attention
  - Exceptions
  - Failed operations
  - Invalid state

### Log Format

Our format includes:
```
%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s

Example:
2025-10-09 14:25:10 - proto_ddf_app.proto_ddf_app - INFO - select_source:108 - select_source called with: CSV File
    ^timestamp        ^module                      ^level  ^function:line     ^message
```

## 🎯 Troubleshooting Checklist

- [ ] Check log files for errors: `grep ERROR *.log`
- [ ] Verify Python version: `python3 --version` (must be 3.10+)
- [ ] Check reflex installation: `python3 -c "import reflex; print(reflex.__file__)"`
- [ ] Verify network binding: `grep backend_host rxconfig.py`
- [ ] Check ports are available: `lsof -i :3000 -i :8000`
- [ ] Review last state method calls: `tail -20 integration_hub.log`
- [ ] Check for exceptions: `grep -A 5 "Traceback" integration_hub.log`
- [ ] Verify submodule: `ls -la reflex/pyproject.toml`
- [ ] Check virtual environment: `which python3` (should be in venv/)
- [ ] Review browser console: Open DevTools → Console tab

## 🔗 Related Files

- `rxconfig.py` - Configuration and framework logging setup
- `proto_ddf_app/proto_ddf_app.py` - Application logging and error handling
- `debug_server.sh` - Debug mode launcher
- `.gitignore` - Prevents committing log files

---

**Need more help?** Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design details.
