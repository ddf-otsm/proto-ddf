# Configuration Directory

This directory contains centralized, non-sensitive configuration constants for the proto-ddf application.

## Files

### `constants.py`
Contains all application configuration constants:
- **Network Configuration**: Backend host and ports
- **Application Settings**: App name, supported data sources
- **Integration Settings**: Sync delays, success rates
- **Field Mapping**: NetSuite field mappings and patterns

### `.port_config.json` (auto-generated, gitignored)
Stores randomly assigned port numbers to ensure consistency across application restarts:
```json
{
  "backend": 4567,
  "frontend": 4568
}
```

The ports are randomly selected from the range 3000-5000 on first run and persisted to avoid conflicts.

## Usage

Import constants in your code:

```python
from config import FRONTEND_PORT, BACKEND_PORT, BACKEND_HOST

# Or import specific constants
from config.constants import NETSUITE_FIELDS, FIELD_MAPPING_PATTERNS
```

## Port Management

- Ports are randomly assigned on first run from the range 3000-5000
- Once assigned, ports are saved to `.port_config.json` for consistency
- Frontend and backend ports are guaranteed to be different
- To reset ports, delete `config/.port_config.json`

## Adding New Constants

When adding new non-sensitive constants:
1. Add them to `constants.py` with a descriptive comment
2. Export them in `__init__.py` if they need to be used in other modules
3. Document them in this README

## Security Note

⚠️ **Never** store sensitive information (passwords, API keys, tokens) in this directory.
Use environment variables or a separate secrets management system instead.

