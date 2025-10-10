# NetSuite Integration Hub - Architecture

## 📐 Project Architecture

This document explains how the NetSuite Integration Hub is built on top of the Reflex framework submodule.

## 🏗️ Layered Architecture

```
┌─────────────────────────────────────────────────┐
│   NetSuite Integration Hub Application         │
│   (proto_ddf_app/proto_ddf_app.py)            │
│                                                 │
│   • Business Logic                              │
│   • Integration Workflows                       │
│   • Data Source Connectors                      │
│   • Field Mapping Logic                         │
│   • UI Components                               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│   Reflex Framework (Git Submodule)             │
│   (reflex/)                                    │
│                                                 │
│   • Web Framework Core                          │
│   • State Management                            │
│   • Component System                            │
│   • Build Tools                                 │
│   • Dev Server                                  │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│   Python 3.10+ Runtime                          │
└─────────────────────────────────────────────────┘
```

## 🔌 Submodule Integration

### Why Use a Submodule?

The `reflex/` directory is a **Git submodule** that points to the official Reflex repository. This approach provides several benefits:

1. **Version Control**: Lock to a specific version of Reflex
2. **No PyPI Dependency**: Install directly from source
3. **Development Flexibility**: Can make local modifications if needed
4. **Transparency**: See exactly what framework code is being used

### Submodule Configuration

Located in `.gitmodules`:
```ini
[submodule "reflex"]
    path = reflex
    url = https://github.com/reflex-dev/reflex.git
```

Current commit: `c28bdba9275bf7161b9e263c0b9b53ac1a43e129`

### Installation Flow

```
1. git submodule update --init --recursive
   └─> Clones Reflex repository into reflex/

2. pip install -e ./reflex
   └─> Installs Reflex in editable mode from submodule
   └─> Creates symlinks to reflex/ in venv/lib/python*/site-packages/

3. Application imports: import reflex as rx
   └─> Python resolves to reflex/ submodule
   └─> Not to a PyPI-installed version
```

## 📦 Directory Structure

```
proto-ddf/
├── proto_ddf_app/              # APPLICATION LAYER
│   ├── __init__.py
│   └── proto_ddf_app.py       # Main app (676 lines)
│
├── reflex/                     # FRAMEWORK LAYER (SUBMODULE)
│   ├── reflex/                # Core framework code
│   ├── pyproject.toml         # Build configuration
│   ├── README.md              # Reflex documentation
│   └── ...                    # Framework source files
│
├── venv/                       # PYTHON ENVIRONMENT
│   └── lib/python3.10/site-packages/
│       └── reflex -> ../../reflex  # Symlink to submodule
│
├── .web/                       # GENERATED ASSETS
│   ├── public/                # Static files
│   └── ...                    # Auto-generated frontend
│
├── rxconfig.py                 # APP CONFIGURATION
├── requirements.txt            # DEPENDENCIES (empty - uses submodule)
├── run.sh                      # RUN SCRIPT
└── .python-version            # Python version requirement (3.10)
```

## 🔧 Configuration Details

### rxconfig.py

```python
import reflex as rx

config = rx.Config(
    app_name="proto_ddf_app",
    # Network binding configuration
    backend_host="0.0.0.0",      # Bind to all interfaces
    backend_port=8000,            # Backend API port
    frontend_port=3000,           # Frontend dev server port
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
```

### Key Settings

- **backend_host="0.0.0.0"**: Makes the app accessible from other machines on the network
  - `localhost` or `127.0.0.1`: Only accessible from same machine
  - `0.0.0.0`: Accessible from any network interface

- **Ports**:
  - `8000`: Backend API (WebSocket and HTTP endpoints)
  - `3000`: Frontend development server (serves UI)

## 🌐 Network Architecture

```
External Device (Phone, Tablet, etc.)
           ↓
    http://192.168.1.100:3000
           ↓
┌──────────────────────────────────┐
│  Frontend Dev Server (Port 3000) │
│  - Serves React UI                │
│  - Hot reload support             │
└──────────────────────────────────┘
           ↓
    WebSocket/HTTP Connection
           ↓
┌──────────────────────────────────┐
│  Backend API (Port 8000)          │
│  - State management               │
│  - Business logic                 │
│  - Data processing                │
│  - Bound to 0.0.0.0               │
└──────────────────────────────────┘
```

## 🔄 State Management

### Reactive State Flow

```
User Action (Browser)
       ↓
WebSocket → Backend State Handler
       ↓
State.method() executes
       ↓
State variables updated
       ↓
WebSocket → Frontend notified
       ↓
UI re-renders automatically
```

### Example State Update

```python
class State(rx.State):
    counter: int = 0
    
    def increment(self):
        self.counter += 1
        # UI updates automatically!
```

When `increment()` is called:
1. Frontend sends WebSocket message
2. Backend updates `counter` state
3. Backend sends new state to frontend
4. Frontend re-renders components that use `counter`

## 🚀 Application Startup

### run.sh Flow

```bash
1. Check if reflex submodule exists
   └─> If not: git submodule update --init --recursive

2. Check if venv exists
   └─> If not: python3 -m venv venv

3. Activate venv
   └─> source venv/bin/activate

4. Check Python version
   └─> Must be >= 3.10
   └─> Exit if version too low

5. Check if reflex installed
   └─> pip show reflex
   └─> If not: pip install -e ./reflex

6. Detect machine IP
   └─> ipconfig (macOS) or hostname (Linux)

7. Start Reflex
   └─> reflex run
   └─> Backend on 0.0.0.0:8000
   └─> Frontend on 0.0.0.0:3000

8. Display access URLs
   └─> Local:   http://127.0.0.1:3000
   └─> Network: http://192.168.x.x:3000
```

## 📊 Data Flow

### Integration Workflow

```
1. User selects data source
       ↓
   State.select_source(source_type)
       ↓
   State.selected_source = source_type
       ↓
   UI updates to show connection panel

2. User clicks "Connect"
       ↓
   State.connect_source() - generator function
       ↓
   yield (progress: 0%)
       ↓
   Fetch data from source
       ↓
   yield (progress: 50%)
       ↓
   State.source_records = data
       ↓
   yield (progress: 100%)
       ↓
   UI shows data table

3. User clicks "Auto-Map"
       ↓
   State.auto_map_fields()
       ↓
   Pattern matching on field names
       ↓
   State.field_mapping = {...}
       ↓
   UI shows field mapping display

4. User clicks "Sync"
       ↓
   State.sync_to_netsuite() - generator
       ↓
   For each record:
       - Map fields
       - Simulate sync (90% success)
       - yield progress
       ↓
   State.mapped_records = results
       ↓
   UI shows synced records with status
```

## 🔍 Component Hierarchy

```
index() - Main page
    ├── container
    │   ├── color_mode.button
    │   └── vstack
    │       ├── Header (heading + text)
    │       ├── Statistics Card
    │       │   └── stat_card × 4
    │       ├── Source Selection Card
    │       │   └── source_card × 6
    │       ├── Active Integration Panel (conditional)
    │       │   ├── Status callout
    │       │   ├── Progress bar
    │       │   └── Action buttons × 3
    │       ├── Source Data Table (conditional)
    │       │   └── rx.table with foreach
    │       ├── Field Mapping Display (conditional)
    │       │   └── Badge pairs with arrows
    │       ├── Synced Records (conditional)
    │       │   └── Record cards with status
    │       └── Integration Logs (conditional)
    │           └── Log table with timestamps
```

## 🛠️ Development Workflow

### Making Changes

1. **Application Code** (`proto_ddf_app/`)
   - Modify freely
   - This is YOUR code
   - No Git conflicts

2. **Framework Code** (`reflex/`)
   - **DO NOT MODIFY** unless you know what you're doing
   - It's a submodule pointing to external repo
   - Changes here affect the framework

3. **Configuration** (`rxconfig.py`)
   - Customize app settings
   - Change ports, host binding, plugins
   - Safe to modify

### Testing Changes

```bash
# After modifying application code:
reflex run

# Reflex watches for file changes and auto-reloads

# To force a clean build:
rm -rf .web
reflex run
```

## 🔐 Security Considerations

### Network Binding

- **0.0.0.0**: Binds to all network interfaces
  - Accessible from LAN
  - Accessible from localhost
  - **NOT accessible from internet** (unless port forwarded)

- **Production**: Should use proper reverse proxy
  - Nginx or Apache
  - SSL/TLS certificates
  - Firewall rules

### Firewall Configuration

**macOS:**
```bash
# Add Python to firewall allowlist
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add $(which python3)
```

**Linux (ufw):**
```bash
# Allow ports
sudo ufw allow 3000/tcp
sudo ufw allow 8000/tcp
```

## 📈 Performance

### Development Mode
- Hot reload enabled
- Unminified JavaScript
- Source maps included
- Debug logging enabled

### Production Mode
```bash
reflex export
# Creates optimized static build in .web/_static/
# Minified JavaScript
# Optimized assets
# Ready for deployment
```

## 🧩 Extension Points

### Adding New Data Sources

1. **Add to SourceType enum**:
```python
class SourceType(str, Enum):
    NEW_SOURCE = "New Source"
```

2. **Add sample data**:
```python
sample_data = {
    SourceType.NEW_SOURCE: [...]
}
```

3. **Add UI card**:
```python
source_card(SourceType.NEW_SOURCE, "Description", "🎯")
```

4. **Implement connection logic** (optional):
```python
def connect_new_source(self):
    # Custom connection code
    pass
```

### Adding Custom Field Mappings

```python
def auto_map_fields(self):
    mapping_patterns = {
        "custom_pattern": ["NetSuite Field", "source_variant1", "source_variant2"]
    }
```

## 🔬 Debugging

### Check Reflex Installation

```bash
python3 -c "import reflex; print(reflex.__file__)"
# Should point to: .../proto-ddf/reflex/reflex/__init__.py
```

### Check Network Binding

```bash
# After starting app:
lsof -i :3000
lsof -i :8000

# Should show:
# python3 ... *:3000 (LISTEN)
# python3 ... *:8000 (LISTEN)
```

### View WebSocket Traffic

Browser DevTools → Network → WS → Select connection → Messages

## 📝 Summary

The NetSuite Integration Hub follows a clean architecture:

1. **Reflex Submodule** provides the framework foundation
2. **Application Layer** built on top with business logic
3. **Network Binding** to 0.0.0.0 for LAN access
4. **Reactive State** for real-time UI updates
5. **Generator Functions** for progress tracking
6. **Component Hierarchy** for organized UI

This separation ensures:
- Framework updates don't break application code
- Application code is portable and maintainable
- Clear boundaries between layers
- Easy to understand and extend

---

**Next Steps**: See [EXAMPLES.md](EXAMPLES.md) for real-world integration implementations.



