# Proto-DDF Architecture Documentation

## System Overview

**Proto-DDF** (Prototype Data-Driven Forms) is an AI-powered Reflex application generator that creates full-stack Python web applications with beautiful UIs. The system enables rapid prototyping and deployment of data-driven applications through an intuitive visual interface.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Proto-DDF Generator Interface                     │
│                         (Reflex App)                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    Frontend (React UI)                       │  │
│  │  - App generation form                                       │  │
│  │  - Template selection                                        │  │
│  │  - Health dashboard                                          │  │
│  └───────────────┬──────────────────────────────────────────────┘  │
│                  │ WebSocket                                        │
│  ┌───────────────▼──────────────────────────────────────────────┐  │
│  │              Backend API (FastAPI)                           │  │
│  │  - /api/generate_app        (Generate new app)              │  │
│  │  - /api/get_apps            (List generated apps)           │  │
│  │  - /api/health              (Health status)                 │  │
│  │  - /api/start_app           (Start application)             │  │
│  │  - /api/stop_app            (Stop application)              │  │
│  └───────────────┬──────────────────────────────────────────────┘  │
│                  │                                                  │
│                  ▼                                                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │            Generated Apps Manager                            │  │
│  │  - Port registry (port_registry.py)                          │  │
│  │  - Process management                                        │  │
│  │  - Health monitoring                                         │  │
│  │  - Configuration storage                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
         ▲                                           ▼
         │                                           │
    ┌────┴─────────────────┬──────────────────────────┴────┐
    │                      │                               │
    ▼                      ▼                               ▼
Generated App 1        Generated App 2              Generated App N
(Reflex/React)        (Reflex/React)               (Reflex/React)
```

---

## Core Components

### 1. Generator Interface (Frontend)

**Technology Stack:**
- React 19.2.0 (compiled from Python via Reflex)
- Radix UI components
- Emotion (CSS-in-JS)
- Tailwind CSS
- WebSocket (real-time updates)

**Key Features:**
- Create new applications from templates
- View and manage generated applications
- Monitor application health status
- Start/stop/restart applications
- Real-time status updates

**File Location:** `proto_ddf_app/generator.py`

### 2. Generator Backend (FastAPI)

**Technology Stack:**
- FastAPI
- Python 3.10+
- Async/await patterns
- Structured logging

**Endpoints:**
```
POST   /api/generate_app      Generate new application
GET    /api/apps              List all generated apps
GET    /api/health            System health status
POST   /api/start_app         Start application
POST   /api/stop_app          Stop application
GET    /api/app/{id}/status   Get app status
```

**File Location:** `proto_ddf_app/generator.py`

### 3. Port Registry System

**Purpose:**
Centralized port management to prevent conflicts and ensure stable, persistent port assignments.

**Design:**
- JSON file-based persistence
- File locking for concurrent safety
- Automatic garbage collection
- Process tracking with PIDs

**Files:**
- `config/constants.py` - Port allocation logic
- `config/port_registry.py` - Persistent registry

**Key Features:**
- Persistent port assignments (same ports across restarts)
- Collision prevention (generator ports ≠ app ports)
- Graceful fallback (degraded mode if write fails)
- Process monitoring and cleanup

### 4. Configuration System

**Purpose:**
Centralized configuration for the entire system.

**Files:**
- `config/constants.py` - Non-sensitive constants
- `.port_config.json` - Port assignments (gitignored)
- `rxconfig.py` - Reflex configuration

**Configuration Hierarchy:**
```
System Level        (config/constants.py)
   ↓
Generator App       (rxconfig.py)
   ↓
Generated Apps      (generated/{app}/rxconfig.py)
   ↓
Runtime Overrides   (Environment variables)
```

### 5. Generated Applications

**Structure per App:**
```
generated/{app_name}/
├── {app_name}_app/
│   └── {app_name}.py          Main application code
├── rxconfig.py                Configuration
├── requirements.txt           Dependencies
├── run.sh                      Run script
├── README.md                   Documentation
└── venv/                       Virtual environment
```

**Technology:**
- Reflex framework (Python to React compiler)
- FastAPI backend
- React frontend
- Tailwind CSS styling
- Socket.io for real-time updates

---

## Data Flow

### Application Generation Flow

```
1. User Input
   User fills form in generator UI
   ↓
2. API Request
   POST /api/generate_app with app details
   ↓
3. Validation
   - Check app name uniqueness
   - Validate project description
   - Reserve ports (port registry)
   ↓
4. Template Processing
   - Select appropriate template
   - Substitute variables
   - Generate file structure
   ↓
5. File Creation
   - Create app directory
   - Write Python code
   - Write configuration files
   - Create run.sh script
   ↓
6. Port Assignment
   - Reserve backend port
   - Reserve frontend port
   - Store in registry
   ↓
7. Response
   - Return app details
   - Send WebSocket update
   - Update health dashboard
```

### Application Startup Flow

```
1. User clicks "Open App"
   ↓
2. Check if app is running
   ↓
3. If not running:
   a. Get ports from registry
   b. Change to app directory
   c. Execute ./run.sh
   d. Wait for app to be available (timeout: 30s)
   ↓
4. Verify app is responding
   ↓
5. Open browser to app URL
   ↓
6. Track process ID
   ↓
7. Update health dashboard
```

### Health Monitoring Flow

```
Continuous (every 5-60s):
1. Check each app's process status
2. Verify port connectivity
3. Test API responsiveness
4. Update dashboard status
5. Remove stale entries (garbage collection)
```

---

## Port Management Strategy

### Port Allocation

**Range:** 3000-5000 (2000 available ports)
**Reason:** Non-privileged range (no root needed)

**Allocation Rules:**
1. Generator uses 2 ports (frontend + backend)
2. Each generated app uses 2 ports (frontend + backend)
3. Total capacity: ~1000 apps maximum

**Persistence:**
- First allocation: Random selection
- Subsequent: Same ports (if available)
- Collision: Automatic reallocation

**File:** `.port_config.json` (gitignored)

### Collision Prevention

```
Reserved Ports:
  - Generator frontend (e.g., 3797)
  - Generator backend (e.g., 3539)

Per-App Ports:
  - App1 frontend (e.g., 4001)
  - App1 backend (e.g., 4002)
  - App2 frontend (e.g., 4003)
  - App2 backend (e.g., 4004)
  - ...

Verification:
  - All ports checked for availability
  - Forbidden set maintained
  - Atomic operations (file locking)
```

---

## Error Handling Strategy

### Error Categories

**1. Configuration Errors**
- Missing files → Default values + warning log
- Invalid JSON → Graceful degradation
- Permission denied → Clear error message with recovery steps

**2. Port Errors**
- Port in use → Try next available port
- Port allocation failed → Fail with helpful message
- Cannot bind → Suggest port cleanup

**3. Generation Errors**
- Invalid app name → Validation error
- Duplicate name → User-friendly error
- Template not found → Fallback to default

**4. Runtime Errors**
- App startup timeout → Suggest manual start
- Process died → Restart or alert user
- API unresponsive → Check logs, restart

### Recovery Strategies

**Automatic Recovery:**
- Port conflicts → Automatic reallocation
- Process crashes → Auto-restart on next access
- Stale entries → Automatic cleanup
- Corrupted config → Fallback to defaults

**Manual Recovery:**
- `./cleanup_ports.sh` → Free up ports
- `./run.sh` → Restart generator
- Delete `generated/{app}` → Remove app
- Check logs → Diagnose issues

---

## Security Considerations

### Port Security

- **Bind Address:** 0.0.0.0 (accessible on network)
- **Ephemeral Ports:** Random allocation (3000-5000)
- **Local Access:** Primary use case (local network)

### File Security

- **Port Config:** .gitignored (not in version control)
- **Logs:** Local storage only
- **Credentials:** Not stored in code

### Process Security

- **Process Isolation:** Each app is separate process
- **Port Binding:** Unique ports per app
- **PID Tracking:** Process monitoring for cleanup

---

## Deployment Patterns

### Local Development

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e ./reflex
pip install -r requirements.txt

# Run
./run.sh

# Generate apps
# (Use web interface at http://localhost:3797)

# Run generated app
cd generated/{app_name}
./run.sh
```

### Production Deployment

**Considerations:**
- Use stable Reflex version (not dev)
- Pre-allocate ports (avoid random selection)
- Use process manager (systemd, supervisor)
- Enable logging to files
- Monitor health and restart on failure
- Use reverse proxy (nginx)
- Enable SSL/TLS

**Example systemd service:**
```
[Unit]
Description=Proto-DDF Generator
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/home/app/proto-ddf
ExecStart=/home/app/proto-ddf/run.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Docker Deployment

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY . .

# Expose ports
EXPOSE 3797 3539

# Run
CMD ["./run.sh"]
```

---

## Performance Characteristics

### Startup Time

- **Generator interface:** ~5 seconds (cold start)
- **Generated app:** ~3-5 seconds (cold start)
- **Warm start:** ~1-2 seconds

### Resource Usage

- **Generator:** 100-200 MB RAM + disk for generated apps
- **Generated app:** 50-100 MB RAM per running app
- **Port registry:** Minimal (JSON file < 1 MB)

### Scaling Limits

- **Concurrent apps:** Limited by available RAM and ports
- **Port limit:** 2000 ports (3000-5000 range)
- **Practical limit:** ~500 active apps on single machine

---

## Future Enhancements

### Planned Features

1. **Docker integration:** Generate Dockerfiles for apps
2. **Cloud deployment:** AWS/GCP/Azure support
3. **API versioning:** Multiple API versions in generated apps
4. **Database integrations:** ORM support, migrations
5. **Authentication:** OAuth2, JWT support
6. **Monitoring:** Prometheus metrics, health checks
7. **Load balancing:** Multi-instance app deployment

### Architectural Improvements

1. **Microservices:** Separate services per function
2. **Caching:** Redis for session management
3. **Message queue:** Async job processing
4. **Database:** Persistent app metadata
5. **CDN:** Static file delivery

---

## Monitoring and Observability

### Logging

**Structured Logging:**
- JSON format for machine parsing
- Contextual metadata in all logs
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

**Log Locations:**
- Console: Real-time output
- `proto_ddf_generator.log`: Application log
- Generated apps: Individual app logs

### Health Checks

**Generator Health:**
- Backend API responsive
- Frontend ports available
- Port registry accessible
- Filesystem writable

**App Health:**
- Process running
- Ports available
- API responding
- Database accessible (if applicable)

### Metrics

**System Metrics:**
- CPU usage
- Memory usage
- Disk usage
- Port availability

**Application Metrics:**
- Request latency
- Error rate
- Uptime
- Active connections

---

## References

- **Reflex Documentation:** https://reflex.dev
- **FastAPI Documentation:** https://fastapi.tiangolo.com
- **React Documentation:** https://react.dev
- **Python Async:** https://docs.python.org/3/library/asyncio.html

---

**Last Updated:** October 17, 2025
**Version:** 1.0
**Status:** Production Ready ✅
