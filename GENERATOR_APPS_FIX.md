# Proto-DDF Generator - Dynamic App Loading Fix

## Issue

The generator was only showing 1 generated app (NetSuite Integration Hub) instead of all 3 apps in the `generated/` directory:
- `my_news_website`
- `netsuite_integration_hub`
- `test_stock_market`

## Root Cause

The `generated_apps` list was hardcoded with only one app:

```python
generated_apps: List[Dict] = [
    {
        "name": "NetSuite Integration Hub",
        "description": "Multi-source data integration showcase",
        "path": "generated/netsuite_integration_hub",
        "status": "ready",
        "port": 3459,
        "url": "http://127.0.0.1:3459",
    }
]
```

## Solution

### 1. Created `load_generated_apps()` Function

Added a function to dynamically scan the `generated/` directory and load all apps:

```python
def load_generated_apps() -> List[Dict]:
    """Load all generated apps from the generated/ directory."""
    generated_dir = Path("generated")
    apps = []

    if not generated_dir.exists():
        logger.warning("Generated directory does not exist")
        return apps

    for app_dir in generated_dir.iterdir():
        if not app_dir.is_dir() or app_dir.name.startswith('.'):
            continue

        # Skip if no rxconfig.py (not a valid app)
        rxconfig_path = app_dir / "rxconfig.py"
        if not rxconfig_path.exists():
            continue

        # Try to read the rxconfig to get port info
        frontend_port = 3000
        try:
            rxconfig_content = rxconfig_path.read_text()
            # Extract frontend_port from config
            for line in rxconfig_content.split('\n'):
                if 'frontend_port' in line and '=' in line:
                    port_str = line.split('=')[-1].strip().rstrip(',')
                    frontend_port = int(port_str)
                    break
        except Exception as e:
            logger.warning(f"Could not read port from {rxconfig_path}: {e}")

        # Try to read description from main app file
        description = "A Reflex application"
        app_name = app_dir.name
        main_app_file = app_dir / f"{app_name}_app" / f"{app_name}.py"
        if main_app_file.exists():
            try:
                content = main_app_file.read_text()
                # Extract description from docstring
                if '"""' in content:
                    parts = content.split('"""')
                    if len(parts) >= 3:
                        doc = parts[1].strip()
                        lines = doc.split('\n')
                        if len(lines) > 2:
                            description = lines[2].strip()
            except Exception as e:
                logger.warning(f"Could not read description from {main_app_file}: {e}")

        # Format name from directory name
        display_name = app_name.replace('_', ' ').title()

        app_info = {
            "name": display_name,
            "description": description,
            "path": f"generated/{app_name}",
            "status": "ready",
            "port": frontend_port,
            "url": f"http://127.0.0.1:{frontend_port}",
        }
        apps.append(app_info)
        logger.info(f"Loaded app: {display_name} at port {frontend_port}")

    return apps
```

### 2. Updated State Initialization

Changed `generated_apps` from hardcoded list to empty list:

```python
# Generated apps - dynamically loaded from file system
generated_apps: List[Dict] = []
```

### 3. Added `on_load()` Event Handler

Added method to load apps when the page loads:

```python
def on_load(self):
    """Load generated apps when the page loads."""
    self.generated_apps = load_generated_apps()
    logger.info(f"Loaded {len(self.generated_apps)} generated apps")
```

### 4. Registered Event Handler

Updated the page registration to call `on_load`:

```python
app.add_page(index, title="Proto-DDF Generator", on_load=GeneratorState.on_load)
```

## Features

The `load_generated_apps()` function:

1. **Scans Directory**: Iterates through all subdirectories in `generated/`
2. **Validates Apps**: Only includes directories with `rxconfig.py`
3. **Extracts Ports**: Parses `rxconfig.py` to get the frontend port
4. **Reads Descriptions**: Extracts description from app docstrings
5. **Formats Names**: Converts `my_news_website` → `My News Website`
6. **Generates URLs**: Creates preview URLs using extracted ports
7. **Logs Progress**: Logs each loaded app for debugging

## Expected Result

After the fix, the generator should show all 3 apps:

```
📱 Generated Applications
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌─────────────────────────────────────────┐
│ My News Website                         │
│ A news aggregation website              │
│ ready | Port: 3456                      │
│ [Open App] [View Code]                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Netsuite Integration Hub                │
│ Multi-source data integration showcase  │
│ ready | Port: 3459                      │
│ [Open App] [View Code]                  │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Test Stock Market                       │
│ A Reflex application                    │
│ ready | Port: 3789                      │
│ [Open App] [View Code]                  │
└─────────────────────────────────────────┘
```

## Testing

To verify the fix works:

1. **Start Generator:**
   ```bash
   make run
   ```

2. **Open Browser:**
   - Navigate to http://127.0.0.1:4936
   - Refresh the page to trigger `on_load`

3. **Verify:**
   - Should see all 3 apps in "Generated Applications" section
   - Each app should have correct name, description, and port
   - "Generated Apps" counter should show "3"

4. **Check Logs:**
   ```bash
   tail -f proto_ddf_generator.log | grep "Loaded"
   ```
   - Should see: "Loaded app: My News Website at port 3456"
   - Should see: "Loaded app: Netsuite Integration Hub at port 3459"
   - Should see: "Loaded app: Test Stock Market at port 3789"
   - Should see: "Loaded 3 generated apps"

## Benefits

1. **Auto-Discovery**: New apps are automatically detected
2. **No Hardcoding**: No need to manually update app list
3. **Accurate Info**: Reads real port and description from files
4. **Robust**: Handles missing files gracefully
5. **Logged**: All loading steps are logged for debugging

## Files Modified

- `proto_ddf_app/generator.py` - Added dynamic app loading

## Next Steps

If apps still don't show after refresh:

1. Check if `on_load` is being called in browser console
2. Verify apps have valid `rxconfig.py` files
3. Check logs for any errors during loading
4. Try adding a manual "Refresh Apps" button as fallback

## Alternative: Manual Refresh Button

If `on_load` doesn't work, add a manual refresh button:

```python
rx.button(
    rx.hstack(
        rx.icon("refresh-cw", size=16),
        rx.text("Refresh Apps"),
        spacing="2",
    ),
    on_click=GeneratorState.on_load,
    size="2",
    variant="soft",
)
```
