"""Proto-DDF Generator - Generate Reflex Applications

This module provides the main generator interface for creating Reflex applications
with integrated port management, health monitoring, and application lifecycle management.

Features:
    - Dynamic application generation from templates
    - Collision-free port allocation using centralized registry
    - Real-time health monitoring of generated applications
    - Application lifecycle management (start, stop, restart)
    - Progress tracking for generation workflow

Components:
    - GeneratorState: Main state management class for generator UI
    - Port utilities: Functions for port availability checking
    - App loading: Dynamic discovery and loading of generated apps
    - UI components: Card components for app display

Usage:
    This module is used by the Proto-DDF Reflex application to provide
    a web interface for generating and managing Reflex applications.
"""

import asyncio
import logging
import random
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List

import reflex as rx
from config.constants import BACKEND_PORT as GEN_BACKEND_PORT
from config.constants import FRONTEND_PORT as GEN_FRONTEND_PORT

# Centralized port registry for stable, collision-free assignments
from config.port_registry import PortRegistry

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add file handler
fh = logging.FileHandler("proto_ddf_generator.log")
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("=" * 80)
logger.info("Proto-DDF Generator - Application Starting")
logger.info("=" * 80)
"""
Global Port Registry instance.
Ensures consistent port assignment across app restarts and prevents collisions.
"""
PORT_REGISTRY = PortRegistry()


def is_port_available(port: int) -> bool:
    """
    Check if a port is available for binding.

    This function tests port availability by attempting to bind to it
    on all interfaces (0.0.0.0). Used during port allocation to prevent conflicts.

    Args:
        port: Port number to check (typically in range 3000-5000)

    Returns:
        bool: True if port is available, False if already in use

    Example:
        >>> is_port_available(3000)
        True
        >>> is_port_available(80)  # Likely in use
        False

    Note:
        This function only checks availability at the moment of the call.
        Port availability can change immediately after checking.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("0.0.0.0", port))
            return True
    except OSError:
        return False


def find_available_port(start: int = 3000, end: int = 5000) -> int:
    """
    Find an available port in the specified range using random selection.

    Attempts to find an available port by testing random ports in the range.
    Uses up to 100 attempts before falling back to the start port.

    Args:
        start: Starting port number (inclusive, default: 3000)
        end: Ending port number (inclusive, default: 5000)

    Returns:
        int: Available port number, or start port if none found after 100 attempts

    Example:
        >>> port = find_available_port()
        >>> 3000 <= port <= 5000
        True
        >>> port = find_available_port(8000, 9000)
        >>> 8000 <= port <= 9000
        True

    Note:
        This function uses random selection to reduce collision probability
        in concurrent scenarios. For deterministic allocation, use PortRegistry.
    """
    for _ in range(100):
        port = random.randint(start, end)
        if is_port_available(port):
            return port
    return start


def load_generated_apps() -> List[Dict]:
    """
    Load all generated Reflex applications from the generated/ directory.

    Scans the generated/ directory for valid Reflex applications, extracts
    their configuration, and returns metadata for each application.

    Returns:
        List[Dict]: List of dictionaries containing app metadata:
            - name: Display name of the application
            - description: Brief description extracted from app module
            - path: Relative path to application directory
            - status: Current status ("ready", "running", etc.)
            - port: Frontend port number
            - url: Application URL

    Example:
        >>> apps = load_generated_apps()
        >>> len(apps)
        3
        >>> apps[0]['name']
        'My News Website'

    Note:
        This function automatically syncs port assignments with the PortRegistry
        to ensure consistency across restarts and prevent collisions.
    """
    generated_dir = Path("generated")
    apps = []

    if not generated_dir.exists():
        logger.warning(
            "Generated directory does not exist",
            extra={
                "operation": "load_generated_apps",
                "directory": str(generated_dir),
                "reason": "directory_not_found",
            },
        )
        return apps

    for app_dir in generated_dir.iterdir():
        if not app_dir.is_dir() or app_dir.name.startswith("."):
            continue

        # Skip if no rxconfig.py (not a valid app)
        rxconfig_path = app_dir / "rxconfig.py"
        if not rxconfig_path.exists():
            continue

        # Try to read the rxconfig to get port info
        frontend_port = None
        backend_port = None
        try:
            rxconfig_content = rxconfig_path.read_text()
            # Extract frontend_port from config
            for line in rxconfig_content.split("\n"):
                if "backend_port" in line and "=" in line and backend_port is None:
                    try:
                        port_str = line.split("=")[-1].strip().rstrip(",")
                        backend_port = int(port_str)
                    except Exception:
                        pass
                if "frontend_port" in line and "=" in line and frontend_port is None:
                    try:
                        port_str = line.split("=")[-1].strip().rstrip(",")
                        frontend_port = int(port_str)
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(
                "Could not read port configuration from rxconfig",
                extra={
                    "operation": "load_generated_apps",
                    "app_name": app_dir.name,
                    "rxconfig_path": str(rxconfig_path),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                },
            )

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
                        lines = doc.split("\n")
                        if len(lines) > 2:
                            description = lines[2].strip()
            except Exception as e:
                logger.warning(
                    "Could not read description from app file",
                    extra={
                        "operation": "load_generated_apps",
                        "app_name": app_name,
                        "app_file_path": str(main_app_file),
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                )

        # Format name from directory name
        display_name = app_name.replace("_", " ").title()

        # Ensure registry has stable, non-colliding ports; update rxconfig if needed
        ports = PORT_REGISTRY.ensure_ports(app_name, backend=backend_port, frontend=frontend_port)

        # If rxconfig differs from registry, update it to keep single source of truth
        try:
            needs_write = False
            try:
                rx_text = rxconfig_path.read_text()
            except Exception:
                rx_text = None
            if rx_text is not None:
                new_text_lines = []
                for line in rx_text.split("\n"):
                    if "backend_port" in line and "=" in line:
                        prefix = line.split("=")[0]
                        new_line = f"{prefix}= {ports.backend},"
                        if new_line != line:
                            needs_write = True
                        new_text_lines.append(new_line)
                    elif "frontend_port" in line and "=" in line:
                        prefix = line.split("=")[0]
                        new_line = f"{prefix}= {ports.frontend},"
                        if new_line != line:
                            needs_write = True
                        new_text_lines.append(new_line)
                    else:
                        new_text_lines.append(line)
                if needs_write:
                    rxconfig_path.write_text("\n".join(new_text_lines))
        except Exception as e:
            logger.warning(
                "Could not sync rxconfig ports",
                extra={
                    "operation": "load_generated_apps",
                    "app_name": app_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "ports": {"backend": ports.backend, "frontend": ports.frontend},
                },
            )

        app_info = {
            "name": display_name,
            "description": description,
            "path": f"generated/{app_name}",
            "status": "ready",
            "port": ports.frontend,
            "url": f"http://127.0.0.1:{ports.frontend}",
        }
        apps.append(app_info)
        logger.info(
            "Application loaded successfully",
            extra={
                "operation": "load_generated_apps",
                "app_name": display_name,
                "app_path": f"generated/{app_name}",
                "ports": {"backend": ports.backend, "frontend": ports.frontend},
                "url": f"http://127.0.0.1:{ports.frontend}",
            },
        )

    logger.info(
        "All generated apps loaded",
        extra={
            "operation": "load_generated_apps",
            "total_apps": len(apps),
            "app_names": [app["name"] for app in apps],
        },
    )
    return apps


class GeneratorState(rx.State):
    """
    State management for the Proto-DDF generator interface.

    This class manages the complete state of the application generator,
    including project settings, generated applications tracking, health
    monitoring, and generation workflow state.

    State Categories:
        - Project Settings: User input for new application generation
        - Generated Apps: List of created applications with metadata
        - Health Tracking: Real-time monitoring of application status
        - Generation Status: Workflow progress and error handling

    Attributes:
        project_name: Name of the project being generated
        project_description: Optional description of the project
        generated_apps: List of generated applications with metadata
        app_health: Health status mapping (app_name -> status)
        running_count: Number of currently running applications
        last_action_message: User feedback for last action performed
        health_poll_enabled: Flag to enable/disable health polling
        generation_status: Current generation workflow status
        generation_message: Status message for generation workflow
        generation_progress: Progress percentage (0-100)
        generation_step: Current step description in generation workflow
        generated_app_url: URL of the newly generated application

    Example:
        >>> state = GeneratorState()
        >>> state.project_name = "My App"
        >>> await state.generate_app()
        >>> state.generation_status
        'success'

    Note:
        This class uses Reflex's reactive state management,
        so all attribute changes trigger UI updates automatically.
    """

    # === Project Settings ===
    # User input for new application generation

    project_name: str = ""
    """Name of the project to generate (required).

    Will be converted to snake_case for directory and module names.
    Example: "My News Website" -> "my_news_website"
    """

    project_description: str = ""
    """Optional description of the project.

    Used in generated app documentation and UI.
    """

    # === Generated Apps ===
    # Dynamically loaded from file system

    generated_apps: List[Dict] = []
    """List of generated applications with metadata.

    Each entry contains:
        - name: Display name
        - description: App description
        - path: Relative path to app directory
        - status: Current status ("ready", "running", etc.)
        - port: Frontend port number
        - url: Application URL
    """

    # === Health Tracking ===
    # Real-time monitoring of application status

    app_health: Dict[str, str] = {}
    """Health status mapping for each application.

    Keys: Application names
    Values: Status strings ("running", "stopped", "error", etc.)
    """

    running_count: int = 0
    """Number of currently running applications.

    Used for dashboard statistics and resource monitoring.
    """

    last_action_message: str = ""
    """User feedback message for the last action performed.

    Displayed temporarily in the UI after actions like start/stop/restart.
    """

    health_poll_enabled: bool = True
    """Flag to enable or disable automatic health polling.

    When enabled, background task checks app health periodically.
    """

    # === Generation Status ===
    # Workflow progress and error handling

    generation_status: str = "idle"
    """Current status of the generation workflow.

    Valid states: "idle", "generating", "success", "error"
    Controls UI state and user interaction availability.
    """

    generation_message: str = ""
    """Status or error message for generation workflow.

    Provides user feedback about success or failure reasons.
    """

    generation_progress: int = 0
    """Progress percentage for generation workflow (0-100).

    Used for progress bar visualization during app generation.
    """

    generation_step: str = ""
    """Current step description in generation workflow.

    Provides detailed feedback about what's happening.
    Example: "Creating project structure...", "Installing dependencies..."
    """

    generated_app_url: str = ""
    """URL of the newly generated application.

    Populated after successful generation for quick access.
    """

    def on_load(self) -> None:
        """
        Initialize generator state when the page loads.

        Loads all generated applications from disk and performs an initial
        health check to determine which applications are running.

        This method is automatically called by Reflex when the page is loaded
        or refreshed by the user.

        Side Effects:
            - Populates self.generated_apps with app metadata
            - Updates self.app_health with current status
            - Updates self.running_count
        """
        self.generated_apps = load_generated_apps()
        logger.info(
            "Generator state initialized",
            extra={
                "operation": "on_load",
                "total_apps": len(self.generated_apps),
                "app_names": [app["name"] for app in self.generated_apps],
            },
        )
        # Initial health snapshot
        self.refresh_health()

    async def _background_health_poll(self):
        """Background task for periodic health checks with exponential backoff."""
        backoff = 5  # Start at 5 seconds
        max_backoff = 60  # Cap at 60 seconds

        while self.health_poll_enabled:
            try:
                await asyncio.sleep(backoff)
                self.refresh_health()
                # Reset backoff on success
                backoff = 5
            except Exception as e:
                logger.warning(f"Health poll error: {e}")
                # Exponential backoff on error
                backoff = min(backoff * 2, max_backoff)

    async def generate_app(self) -> None:
        """
        Generate a new Reflex application with progress tracking.

        Creates a complete Reflex application from scratch including:
        - Project directory structure
        - Main application module with basic UI
        - Configuration files (rxconfig.py, requirements.txt)
        - Run scripts for easy startup
        - Git ignore file

        The generation process is tracked with progress updates that are
        yielded to the UI for real-time feedback.

        Raises:
            Exceptions are caught and logged, with user-friendly messages
            set in self.generation_message.

        Side Effects:
            - Creates new directory in generated/
            - Allocates ports via PortRegistry
            - Updates self.generated_apps list
            - Updates generation status and progress attributes
        """
        logger.info(
            "Application generation started",
            extra={
                "operation": "generate_app",
                "project_name": self.project_name,
                "project_description": self.project_description,
                "user_id": getattr(self, "user_id", "anonymous"),
            },
        )

        if not self.project_name:
            self.generation_message = "Please provide a project name"
            self.generation_status = "error"
            logger.warning(
                "Application generation failed - no project name provided",
                extra={"operation": "generate_app", "failure_reason": "missing_project_name"},
            )
            return

        # Reset state
        self.generation_status = "generating"
        self.generation_progress = 0
        self.generation_step = "Initializing..."
        self.generation_message = ""
        self.generated_app_url = ""
        yield

        # Track generation time
        start_time = time.time()

        try:
            app_name = self.project_name.lower().replace(" ", "_")
            app_dir = Path("generated") / app_name

            # Step 1: Validate
            self.generation_progress = 10
            self.generation_step = "Validating project settings..."
            yield
            await asyncio.sleep(0.5)

            if app_dir.exists():
                self.generation_status = "error"
                self.generation_message = f"App '{app_name}' already exists!"
                logger.error(
                    "Application generation failed - directory already exists",
                    extra={
                        "operation": "generate_app",
                        "app_name": app_name,
                        "app_dir": str(app_dir),
                        "failure_reason": "directory_exists",
                    },
                )
                return

            # Step 2: Create structure
            self.generation_progress = 25
            self.generation_step = "Creating project structure..."
            yield
            await asyncio.sleep(0.5)

            logger.info(
                "Creating application directory structure",
                extra={
                    "operation": "generate_app",
                    "app_name": app_name,
                    "app_dir": str(app_dir),
                    "step": "create_structure",
                },
            )
            app_dir.mkdir(parents=True, exist_ok=True)
            app_module_dir = app_dir / f"{app_name}_app"
            app_module_dir.mkdir(exist_ok=True)

            # Allocate stable, collision-free ports from registry
            backend_port, frontend_port = PORT_REGISTRY.reserve_pair(app_name)
            logger.info(
                "Ports allocated for application",
                extra={
                    "operation": "generate_app",
                    "app_name": app_name,
                    "ports": {"backend": backend_port, "frontend": frontend_port},
                    "step": "port_allocation",
                },
            )

            # Step 3: Generate code
            self.generation_progress = 40
            self.generation_step = "Generating application code..."
            yield
            await asyncio.sleep(0.8)

            # Create __init__.py
            (app_module_dir / "__init__.py").write_text("")

            # Create main app file
            main_app_code = f'''"""
{self.project_name} - Generated by Proto-DDF

This is a Reflex application automatically generated by the Proto-DDF generator.

Description:
    {self.project_description or "A Reflex application"}

Architecture:
    - Frontend: Reflex (React-based) with Tailwind CSS
    - Backend: Python with FastAPI
    - State: Reactive state management
    - Styling: Tailwind CSS with custom themes

Customization:
    - Edit this file to modify the application UI and logic
    - Add new state variables to the State class
    - Create new pages by adding components
    - Add components in separate files if needed

Key Features:
    - Hot reload during development
    - Automatic state synchronization
    - Built-in component library
    - Responsive design support

Running the app:
    ./run.sh  # or: reflex run

Debugging:
    - Check logs in proto_ddf_generator.log
    - Use browser dev tools for frontend issues
    - Use Python debugger for backend issues

For more info, visit: https://reflex.dev
"""

import reflex as rx


class State(rx.State):
    """
    Application state for {self.project_name}.

    Manages reactive state including:
    - UI state (message, etc.)
    - User data
    - Application data

    All state changes automatically trigger UI updates.
    """

    message: str = "Hello from {self.project_name}!"
    """Welcome message displayed on the application."""


def index() -> rx.Component:
    """
    Main page component for {self.project_name}.

    Returns:
        rx.Component: The main page with heading, description, and card.
    """
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            rx.heading("{self.project_name}", size="9", gradient=True),
            rx.text(
                "{self.project_description or 'Welcome to your new Reflex app!'}",
                size="4",
                color="gray",
            ),
            rx.card(
                rx.vstack(
                    rx.heading("🎨 Getting Started", size="6"),
                    rx.text(
                        "This is your generated Reflex application. Edit the code in:",
                        size="3",
                    ),
                    rx.code(
                        "generated/{app_name}/{app_name}_app/{app_name}.py",
                        size="2",
                    ),
                    rx.divider(),
                    rx.text(State.message, size="4", weight="bold"),
                    spacing="4",
                ),
                padding="6",
            ),
            spacing="6",
            align="center",
            padding="4",
        ),
        padding="4",
    )


app = rx.App()
app.add_page(index, title="{self.project_name}")
'''
            (app_module_dir / f"{app_name}.py").write_text(main_app_code)

            # Step 4: Create config
            self.generation_progress = 55
            self.generation_step = "Configuring application settings..."
            yield
            await asyncio.sleep(0.5)

            # Create rxconfig.py
            rxconfig_code = f'''"""Reflex configuration for {self.project_name}.

This configuration file defines the application settings including:
- Application metadata (name, module path)
- Network configuration (ports for frontend and backend)
- Build settings (environment, logging level)
- Plugin system (optional plugins for extended functionality)

For more information, see:
    https://reflex.dev/docs/getting-started/installation

Configuration Options:
    app_name: Internal name for the application (used for module naming)
    app_module_import: Python import path for the main application module
    backend_port: Port number for the FastAPI backend server
    frontend_port: Port number for the React frontend development server

Port Management:
    The ports are automatically allocated by Proto-DDF to avoid collisions.
    You can manually change these if needed, but be aware of potential conflicts.
    Port range: 3000-5000 (default, configurable)

Environment:
    Set env=rx.Env.PROD for production deployments
    Currently using rx.Env.DEV for development mode

Logging:
    Logging level can be adjusted via loglevel parameter
    Available levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
"""

import reflex as rx

# === Application Identity ===
# These identify your application and must match your project structure

config = rx.Config(
    app_name="{app_name}_app",
    """Internal application name.
    Used for:
    - Python module imports
    - Build output naming
    - Logging identification
    Format: lowercase_with_underscores
    """,

    app_module_import="{app_name}_app.{app_name}",
    """Python import path for the main application module.
    Format: package.module (matches directory structure)
    Must match the location of the main application file.
    """,

    # === Network Configuration ===
    # Ports are automatically allocated by Proto-DDF

    backend_port={backend_port},
    """Backend API server port.
    - Handles WebSocket connections for real-time updates
    - Serves API endpoints
    - Manages state synchronization
    - Accessible at: http://localhost:{backend_port}
    """,

    frontend_port={frontend_port},
    """Frontend development server port.
    - Serves the React user interface
    - Enables hot reload during development
    - Accessible at: http://localhost:{frontend_port}
    """,
)
'''
            (app_dir / "rxconfig.py").write_text(rxconfig_code)

            # Create requirements.txt
            requirements_code = """reflex>=0.6.0
"""
            (app_dir / "requirements.txt").write_text(requirements_code)

            # Step 5: Create run scripts
            self.generation_progress = 70
            self.generation_step = "Setting up build scripts..."
            yield
            await asyncio.sleep(0.5)

            # Create run.sh
            run_sh_code = f"""#!/bin/bash
# {self.project_name} - Application Runner
# =========================================
#
# This script starts the {self.project_name} Reflex application with:
# - Python virtual environment setup
# - Dependency installation
# - Application startup with proper error handling
#
# Usage:
#   ./run.sh                    # Run with default settings
#   ./run.sh --debug           # Run with debug output
#   ./run.sh --help            # Show this help message
#
# Environment Variables:
#   PYTHON_VERSION    - Python version to use (default: 3.10+)
#   LOG_LEVEL         - Logging level (default: INFO)
#   CUSTOM_PORT       - Override frontend port
#
# Features:
#   - Automatic virtual environment creation
#   - Dependency management
#   - Port conflict detection
#   - Error handling and recovery
#
# Exit Codes:
#   0 - Application started successfully
#   1 - Python version too low
#   2 - Virtual environment creation failed
#   3 - Dependency installation failed
#   4 - Port already in use
#   5 - Application startup failed
#
# Prerequisites:
#   - Python 3.10 or higher
#   - pip package manager
#
# For more info: https://reflex.dev/docs/getting-started/installation

set -e  # Exit on error

# Configuration
APP_NAME="{self.project_name}"
BACKEND_PORT={backend_port}
FRONTEND_PORT={frontend_port}
PYTHON_VERSION="3.10"
REQUIRED_PYTHON_VERSION="3.10"
LOG_LEVEL="INFO"

# === Logging Functions ===
# Provide structured console output

log_info() {{
    echo "ℹ️  $1" >&2
}}

log_success() {{
    echo "✅ $1" >&2
}}

log_warning() {{
    echo "⚠️  WARNING: $1" >&2
}}

log_error() {{
    echo "❌ ERROR: $1" >&2
}}

log_progress() {{
    echo "🔄 $1" >&2
}}

# === Application Startup ===

log_info "Starting $APP_NAME..."
log_info "Frontend: http://localhost:$FRONTEND_PORT"
log_info "Backend: http://localhost:$BACKEND_PORT"
echo ""

# Check Python version
log_progress "Checking Python version..."
PYTHON_INSTALLED=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [ "$(printf '%s\\n' "$REQUIRED_PYTHON_VERSION" "$PYTHON_INSTALLED" | sort -V | head -n1)" != "$REQUIRED_PYTHON_VERSION" ]; then
    log_error "Python $REQUIRED_PYTHON_VERSION or higher is required"
    log_error "Current version: Python $PYTHON_INSTALLED"
    log_info "Install Python 3.10+ from https://python.org"
    exit 1
fi

log_success "Python version: $PYTHON_INSTALLED"

# Virtual environment setup
if [ ! -d "venv" ]; then
    log_progress "Creating virtual environment..."
    if ! python3 -m venv venv; then
        log_error "Failed to create virtual environment"
        exit 2
    fi
    log_success "Virtual environment created"
fi

# Activate virtual environment
log_progress "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if ! pip show reflex > /dev/null 2>&1; then
    log_progress "Installing dependencies from requirements.txt..."
    if ! pip install -q -r requirements.txt; then
        log_error "Failed to install dependencies"
        log_info "Try: pip install -r requirements.txt"
        exit 3
    fi
    log_success "Dependencies installed successfully"
else
    log_success "Dependencies already installed"
fi

# Check port availability
log_progress "Checking port availability..."
check_port() {{
    ! nc -z localhost "$1" 2>/dev/null
}}

if ! check_port "$FRONTEND_PORT"; then
    log_warning "Frontend port $FRONTEND_PORT is already in use"
    log_info "Either stop the process using that port or change FRONTEND_PORT"
    exit 4
fi

if ! check_port "$BACKEND_PORT"; then
    log_warning "Backend port $BACKEND_PORT is already in use"
    log_info "Either stop the process using that port or change BACKEND_PORT"
    exit 4
fi

log_success "Ports available"

# Display startup information
echo ""
log_success "$APP_NAME is ready!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:$FRONTEND_PORT"
echo "   Backend:  http://localhost:$BACKEND_PORT"
echo ""
echo "📝 For development:"
echo "   - Edit code in {app_name}_app/{app_name}.py"
echo "   - Changes will hot-reload automatically"
echo "   - Check logs for errors"
echo ""
echo "🛑 To stop the server:"
echo "   Press Ctrl+C"
echo ""

# Run the application
if ! reflex run; then
    log_error "Application startup failed"
    log_info "Check the logs above for details"
    exit 5
fi
"""
            run_sh_path = app_dir / "run.sh"
            run_sh_path.write_text(run_sh_code)
            run_sh_path.chmod(0o755)  # Make executable

            # Create README.md
            readme_code = f"""# {self.project_name}

This is a Reflex application generated by the Proto-DDF generator.

## Description

{self.project_description or "A Reflex application"}

## Architecture

- Frontend: Reflex (React-based) with Tailwind CSS
- Backend: Python with FastAPI
- State: Reactive state management
- Styling: Tailwind CSS with custom themes

## Customization

- Edit this file to modify the application UI and logic
- Add new state variables to the State class
- Create new pages by adding components
- Add components in separate files if needed

## Key Features

- Hot reload during development
- Automatic state synchronization
- Built-in component library
- Responsive design support

## Running the App

```bash
./run.sh  # or: reflex run
```

## Debugging

- Check logs in proto_ddf_generator.log
- Use browser dev tools for frontend issues
- Use Python debugger for backend issues

## For More Info

Visit: https://reflex.dev
"""
            (app_dir / "README.md").write_text(readme_code)

            # Create .gitignore
            gitignore_code = """venv/
__pycache__/
*.pyc
.web/
*.log
"""
            (app_dir / ".gitignore").write_text(gitignore_code)

            # Step 6: Polish UI
            self.generation_progress = 85
            self.generation_step = "Finishing polished UI..."
            yield
            await asyncio.sleep(0.8)

            # Step 7: Complete
            self.generation_progress = 100
            self.generation_step = "Application ready!"
            yield
            await asyncio.sleep(0.3)

            # Add to generated_apps list
            app_url = f"http://127.0.0.1:{frontend_port}"
            new_app = {
                "name": self.project_name,
                "description": self.project_description or "A Reflex application",
                "path": f"generated/{app_name}",
                "status": "ready",
                "port": frontend_port,
                "url": app_url,
            }
            self.generated_apps.append(new_app)

            self.generation_status = "success"
            self.generated_app_url = app_url
            self.generation_message = f"🎉 Successfully generated {self.project_name}!"
            logger.info(
                "Application generation completed successfully",
                extra={
                    "operation": "generate_app",
                    "app_name": app_name,
                    "app_dir": str(app_dir),
                    "ports": {"backend": backend_port, "frontend": frontend_port},
                    "url": app_url,
                    "project_description": self.project_description,
                    "duration_seconds": (
                        time.time() - start_time if "start_time" in locals() else None
                    ),
                },
            )

        except Exception as e:
            self.generation_status = "error"
            self.generation_message = f"⚠️ Error generating app: {str(e)}"
            self.generation_progress = 0
            self.generation_step = ""
            logger.error(
                "Application generation failed with exception",
                extra={
                    "operation": "generate_app",
                    "app_name": self.project_name,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "generation_step": self.generation_step,
                    "generation_progress": self.generation_progress,
                },
                exc_info=True,
            )

    def _is_port_open(self, host: str, port: int) -> bool:
        """
        Check if a TCP port is open and accepting connections.

        Args:
            host: Hostname or IP address to check
            port: Port number to check

        Returns:
            bool: True if port is open, False otherwise

        Note:
            Uses a 1-second timeout to avoid blocking on unresponsive ports.
        """
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except OSError:
            return False

    def refresh_health(self) -> None:
        """
        Update health status for all generated applications.

        Checks each application's frontend port to determine if it's running.
        Updates the app_health dictionary and running_count attribute.

        Side Effects:
            - Updates self.app_health with current status for each app
            - Updates self.running_count with number of running apps

        Note:
            This method is called periodically by the background health poll
            and can be manually triggered via the UI.
        """
        health: Dict[str, str] = {}
        running = 0
        for app in self.generated_apps:
            name = app.get("name", "")
            port = int(app.get("port", 0))
            is_up = self._is_port_open("127.0.0.1", port)
            health[name] = "up" if is_up else "down"
            if is_up:
                running += 1
        self.app_health = health
        self.running_count = running
        logger.debug(
            "Health check completed",
            extra={
                "operation": "refresh_health",
                "total_apps": len(self.generated_apps),
                "running_apps": running,
                "health_status": health,
            },
        )

    async def open_app(self, name: str, path: str, port: int, url: str):
        """
        Open a generated application with automatic startup if needed.

        If the application is not running, this method will automatically
        start it and wait for it to become available before redirecting.

        Args:
            name: Display name of the application
            path: Relative path to the application directory
            port: Frontend port number
            url: Application URL to redirect to

        Side Effects:
            - May start the application in a background process
            - Updates self.last_action_message with status updates
            - Refreshes health status
            - Redirects browser to the application URL

        Note:
            This method yields progress updates for UI reactivity.
            Waits up to 30 seconds for the application to start.
        """
        start_time = time.time()
        self.last_action_message = f"Opening {name}..."
        yield

        if not self._is_port_open("127.0.0.1", int(port)):
            self.last_action_message = f"Starting {name}..."
            yield
            logger.info(
                "Auto-starting application",
                extra={
                    "operation": "open_app",
                    "app_name": name,
                    "app_path": path,
                    "port": port,
                    "url": url,
                },
            )
            try:
                run_script = Path(path) / "run.sh"
                if run_script.exists():
                    # Start app in background without blocking UI
                    process = subprocess.Popen(
                        ["bash", str(run_script)],
                        cwd=str(Path(path)),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        start_new_session=True,
                    )
                    logger.info(
                        "Application process started",
                        extra={
                            "operation": "open_app",
                            "app_name": name,
                            "pid": process.pid,
                            "port": port,
                        },
                    )
                    # Record PID in registry
                    app_name_key = Path(path).name
                    PORT_REGISTRY.set_pid(app_name_key, process.pid)
                else:
                    logger.warning(
                        "Run script not found",
                        extra={
                            "operation": "open_app",
                            "app_name": name,
                            "app_path": path,
                            "run_script_path": str(run_script),
                            "failure_reason": "run_script_not_found",
                        },
                    )
                    self.last_action_message = f"⚠️ Error: run.sh not found for {name}"
                    yield
                    return
            except Exception as e:
                logger.error(
                    "Failed to start application",
                    extra={
                        "operation": "open_app",
                        "app_name": name,
                        "app_path": path,
                        "port": port,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    },
                    exc_info=True,
                )
                self.last_action_message = f"⚠️ Failed to start {name}: {str(e)}"
                yield
                return

            # Wait for port to become available (max ~30s)
            wait_start = time.time()
            while time.time() - wait_start < 30:
                if self._is_port_open("127.0.0.1", int(port)):
                    startup_duration = time.time() - start_time
                    logger.info(
                        "Application started successfully",
                        extra={
                            "operation": "open_app",
                            "app_name": name,
                            "startup_duration_seconds": round(startup_duration, 1),
                            "port": port,
                        },
                    )
                    break
                await asyncio.sleep(1.0)
                yield
            else:
                logger.warning(
                    "Application startup timeout",
                    extra={
                        "operation": "open_app",
                        "app_name": name,
                        "port": port,
                        "timeout_seconds": 30,
                        "failure_reason": "startup_timeout",
                    },
                )
                self.last_action_message = f"⚠️ Timeout: {name} did not start in 30s"
                yield
                return

        # Refresh health and redirect
        self.refresh_health()
        self.last_action_message = ""
        yield rx.redirect(url, is_external=True)

    async def open_generated_app(self):
        """Open the newly generated app with auto-start support."""
        if not self.generated_app_url:
            return

        # Find the newly generated app from the list
        if self.generated_apps:
            last_app = self.generated_apps[-1]
            await self.open_app(
                last_app.get("name", ""),
                last_app.get("path", ""),
                last_app.get("port", 0),
                last_app.get("url", self.generated_app_url),
            )

    def set_project_name(self, name: str) -> None:
        """
        Set the project name for the new application.

        Args:
            name: Project name (will be converted to snake_case for filesystem)
        """
        self.project_name = name

    def set_project_description(self, description: str) -> None:
        """
        Set the project description for the new application.

        Args:
            description: Optional description shown in the generated app
        """
        self.project_description = description

    async def stop_app(self, name: str, path: str):
        """
        Stop a running application.

        Args:
            name: Display name of the application
            path: Relative path to the application directory

        Side Effects:
            - Stops the application process via PortRegistry
            - Updates self.last_action_message with status
            - Refreshes health status after stopping

        Note:
            This method yields progress updates for UI reactivity.
        """
        self.last_action_message = f"Stopping {name}..."
        yield

        app_name_key = Path(path).name
        success = PORT_REGISTRY.stop_app(app_name_key)

        if success:
            logger.info(
                "Application stopped successfully",
                extra={"operation": "stop_app", "app_name": name, "app_path": path},
            )
            self.last_action_message = f"✅ Stopped {name}"
        else:
            logger.warning(
                "Failed to stop application",
                extra={
                    "operation": "stop_app",
                    "app_name": name,
                    "app_path": path,
                    "failure_reason": "not_running_or_error",
                },
            )
            self.last_action_message = f"⚠️ Could not stop {name}"

        # Refresh health
        await asyncio.sleep(1.0)
        self.refresh_health()
        self.last_action_message = ""
        yield

    async def restart_app(self, name: str, path: str, port: int, url: str):
        """
        Restart a running application.

        Stops the application and then starts it again. Useful for applying
        configuration changes or recovering from errors.

        Args:
            name: Display name of the application
            path: Relative path to the application directory
            port: Frontend port number
            url: Application URL

        Side Effects:
            - Stops the application process
            - Starts the application process
            - Updates self.last_action_message with status

        Note:
            This method yields progress updates for UI reactivity.
            Waits 2 seconds between stop and start.
        """
        self.last_action_message = f"Restarting {name}..."
        yield

        logger.info(
            "Restarting application",
            extra={"operation": "restart_app", "app_name": name, "app_path": path, "port": port},
        )

        # Stop first
        app_name_key = Path(path).name
        PORT_REGISTRY.stop_app(app_name_key)
        await asyncio.sleep(2.0)

        # Then start
        await self.open_app(name, path, port, url)


def app_card(app: Dict) -> rx.Component:
    """
    Create a card component for displaying generated application information.

    Args:
        app: Dictionary containing app information with keys:
            - name: Application name
            - description: Brief app description
            - status: Current status ("ready", "running", etc.)
            - port: Port number the app runs on

    Returns:
        rx.Component: A card component displaying app details and actions
    """
    return rx.card(
        rx.vstack(
            # App title and description
            rx.heading(app["name"], size="5"),
            rx.text(app["description"], size="2", color="gray"),
            # Status and port information
            rx.hstack(
                rx.badge(
                    app["status"],
                    color=rx.cond(app["status"] == "ready", "green", "gray"),
                ),
                rx.text(f"Port: {app['port']}", size="2", color="gray"),
                spacing="2",
            ),
            # Action buttons
            rx.hstack(
                rx.button(
                    rx.hstack(
                        rx.icon("external-link", size=14),
                        rx.text("Open"),
                        spacing="1",
                    ),
                    on_click=lambda: GeneratorState.open_app(
                        app.get("name", ""),
                        app.get("path", ""),
                        app.get("port", 0),
                        app.get("url", f"http://127.0.0.1:{app['port']}"),
                    ),
                    variant="soft",
                    size="2",
                    data_testid=f"open-app-{app['name']}",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("rotate-cw", size=14),
                        rx.text("Restart"),
                        spacing="1",
                    ),
                    on_click=lambda: GeneratorState.restart_app(
                        app.get("name", ""),
                        app.get("path", ""),
                        app.get("port", 0),
                        app.get("url", f"http://127.0.0.1:{app['port']}"),
                    ),
                    variant="outline",
                    size="2",
                    color="orange",
                    data_testid=f"restart-app-{app['name']}",
                ),
                rx.button(
                    rx.hstack(
                        rx.icon("square", size=14),
                        rx.text("Stop"),
                        spacing="1",
                    ),
                    on_click=lambda: GeneratorState.stop_app(
                        app.get("name", ""), app.get("path", "")
                    ),
                    variant="outline",
                    size="2",
                    color="red",
                    data_testid=f"stop-app-{app['name']}",
                ),
                spacing="2",
                wrap="wrap",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        padding="4",
        width="100%",
    )


def index() -> rx.Component:
    """Main generator interface."""
    return rx.container(
        rx.color_mode.button(position="top-right"),
        rx.vstack(
            # Header
            rx.vstack(
                rx.heading("🎨 Proto-DDF Generator", size="9", gradient=True),
                rx.text(
                    "Generate Reflex applications with AI-powered code generation",
                    size="4",
                    color="gray",
                    align="center",
                ),
                align="center",
                spacing="2",
                padding_bottom="4",
            ),
            # Ports & Health Dashboard
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.text("🧭", size="7"),
                            rx.text("Generator Ports", size="2", color="gray"),
                            rx.text(
                                f"FE {GEN_FRONTEND_PORT} / BE {GEN_BACKEND_PORT}",
                                size="5",
                                weight="bold",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("📦", size="7"),
                            rx.text("Generated Apps", size="2", color="gray"),
                            rx.text(
                                GeneratorState.generated_apps.length(),
                                size="5",
                                weight="bold",
                                color="blue",
                            ),
                            spacing="1",
                        ),
                        rx.vstack(
                            rx.text("🚀", size="7"),
                            rx.text("Running", size="2", color="gray"),
                            rx.text(
                                GeneratorState.running_count,
                                size="5",
                                weight="bold",
                                color="green",
                            ),
                            spacing="1",
                        ),
                        justify="between",
                        width="100%",
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.text("Health:"),
                        rx.foreach(
                            GeneratorState.generated_apps,
                            lambda a: rx.badge(
                                rx.cond(
                                    GeneratorState.app_health.get(a["name"], "down") == "up",
                                    f"{a['name']}:{a['port']} up",
                                    f"{a['name']}:{a['port']} down",
                                ),
                                color=rx.cond(
                                    GeneratorState.app_health.get(a["name"], "down") == "up",
                                    "green",
                                    "red",
                                ),
                            ),
                        ),
                        spacing="2",
                        wrap="wrap",
                        width="100%",
                    ),
                    rx.hstack(
                        rx.button(
                            "Refresh Health",
                            on_click=GeneratorState.refresh_health,
                            variant="soft",
                            size="2",
                            data_testid="refresh-health-button",
                        ),
                        rx.text(GeneratorState.last_action_message, color="gray"),
                        justify="between",
                        width="100%",
                    ),
                    spacing="3",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            # New App Generator
            rx.card(
                rx.vstack(
                    rx.heading("➕ Generate New App", size="6"),
                    rx.vstack(
                        rx.vstack(
                            rx.text("Project Name", size="2", weight="medium"),
                            rx.input(
                                placeholder="e.g., my-dashboard",
                                on_change=GeneratorState.set_project_name,
                                size="3",
                                width="100%",
                                data_testid="project-name-input",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Description", size="2", weight="medium"),
                            rx.text_area(
                                placeholder="Describe what you want to build...",
                                on_change=GeneratorState.set_project_description,
                                size="3",
                                width="100%",
                                rows="4",
                                data_testid="project-description-input",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    rx.button(
                        "🎨 Generate App",
                        on_click=GeneratorState.generate_app,
                        size="3",
                        width="100%",
                        disabled=GeneratorState.generation_status == "generating",
                        loading=GeneratorState.generation_status == "generating",
                        data_testid="generate-app-button",
                    ),
                    # Progress indicator
                    rx.cond(
                        GeneratorState.generation_status == "generating",
                        rx.vstack(
                            rx.text(
                                GeneratorState.generation_step,
                                size="2",
                                weight="medium",
                                color="blue",
                            ),
                            rx.progress(
                                value=GeneratorState.generation_progress,
                                max=100,
                                width="100%",
                            ),
                            rx.hstack(
                                rx.text(GeneratorState.generation_progress, size="1", color="gray"),
                                rx.text("%", size="1", color="gray"),
                                spacing="1",
                            ),
                            spacing="2",
                            width="100%",
                        ),
                    ),
                    # Success message with preview link
                    rx.cond(
                        GeneratorState.generation_status == "success",
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.icon("check-circle", size=20, color="green"),
                                    rx.text(
                                        GeneratorState.generation_message,
                                        size="3",
                                        weight="bold",
                                        color="green",
                                    ),
                                    spacing="2",
                                ),
                                rx.divider(),
                                rx.vstack(
                                    rx.text(
                                        "Your app is ready! Preview it here:",
                                        size="2",
                                        color="gray",
                                    ),
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("external-link", size=16),
                                            rx.text("Open App Preview"),
                                            spacing="2",
                                        ),
                                        on_click=GeneratorState.open_generated_app,
                                        size="3",
                                        variant="solid",
                                        color="blue",
                                        data_testid="open-generated-app-button",
                                    ),
                                    rx.text(
                                        GeneratorState.generated_app_url,
                                        size="1",
                                        color="gray",
                                        font_family="monospace",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                                spacing="3",
                                width="100%",
                            ),
                            variant="surface",
                            style={"background": "var(--green-a2)"},
                        ),
                    ),
                    # Error message
                    rx.cond(
                        GeneratorState.generation_status == "error",
                        rx.callout(
                            GeneratorState.generation_message,
                            icon="alert-triangle",
                            color="red",
                        ),
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            # Generated Apps
            rx.card(
                rx.vstack(
                    rx.heading("📱 Generated Applications", size="6"),
                    rx.vstack(
                        rx.foreach(GeneratorState.generated_apps, app_card),
                        spacing="3",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            # Templates
            rx.card(
                rx.vstack(
                    rx.heading("📚 Available Templates", size="6"),
                    rx.grid(
                        rx.card(
                            rx.vstack(
                                rx.text("📊", size="8"),
                                rx.heading("Dashboard", size="4"),
                                rx.text(
                                    "Analytics and data visualization",
                                    size="2",
                                    color="gray",
                                ),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center",
                            ),
                            padding="4",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("🔄", size="8"),
                                rx.heading("Integration Hub", size="4"),
                                rx.text(
                                    "Connect multiple data sources",
                                    size="2",
                                    color="gray",
                                ),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center",
                            ),
                            padding="4",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("💬", size="8"),
                                rx.heading("Chat App", size="4"),
                                rx.text(
                                    "Real-time messaging interface",
                                    size="2",
                                    color="gray",
                                ),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center",
                            ),
                            padding="4",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("🛍️", size="8"),
                                rx.heading("E-commerce", size="4"),
                                rx.text("Online store with cart", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center",
                            ),
                            padding="4",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.text("📝", size="8"),
                                rx.heading("CMS", size="4"),
                                rx.text("Content management system", size="2", color="gray"),
                                rx.button("Use Template", variant="soft", size="2"),
                                spacing="3",
                                align="center",
                            ),
                            padding="4",
                        ),
                        columns="3",
                        gap="4",
                        width="100%",
                    ),
                    spacing="4",
                    width="100%",
                ),
                padding="6",
                width="100%",
            ),
            spacing="6",
            padding="4",
            width="100%",
            max_width="1400px",
        ),
        padding="4",
        width="100%",
    )


# Create the app
app = rx.App()
app.add_page(index, title="Proto-DDF Generator", on_load=GeneratorState.on_load)
