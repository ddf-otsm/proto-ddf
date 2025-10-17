"""Non-sensitive configuration constants for proto-ddf application.

This module centralizes all configuration settings for the Proto-DDF generator
interface and generated applications, including:

- Port management: Dynamic allocation and persistence
- Network configuration: Host and port assignments
- Application constants: Names and identifiers
- Data source definitions: Supported integration types
- Field mapping: Pattern-based automatic field matching

PORT MANAGEMENT STRATEGY:
========================
The port allocation system prevents collisions between:
  1. Generator interface ports (frontend + backend)
  2. Generated applications (frontend + backend per app)

All ports are persistent and stored in .port_config.json, ensuring:
  - Same ports across restarts
  - No collisions when multiple applications run simultaneously
  - Isolated port ranges for generator vs generated apps

Port Range: 3000-5000 (configurable, but default recommended)
  - Reason: Non-privileged port range that doesn't require root
  - Allows up to 2000 port numbers for flexibility
  - Generator uses 2 ports, each generated app uses 2 ports

File Persistence (.port_config.json):
  - JSON format: {"backend": 3539, "frontend": 3797, "generated_backend": 4984, "generated_frontend": 3459}
  - Location: config/.port_config.json (gitignored for local development)
  - Automatically created and updated by _get_or_generate_port()
  - Enables reliable port tracking across sessions

Collision Detection:
  - Frontend and backend ports are guaranteed different
  - Generator ports differ from all generated app ports
  - Each generated app has unique frontend and backend ports
"""

import json
import random
import socket
from pathlib import Path

# Configuration file path
CONFIG_DIR = Path(__file__).parent
PORT_CONFIG_FILE = CONFIG_DIR / ".port_config.json"


def _is_port_available(port: int, host: str = "0.0.0.0") -> bool:
    """
    Check if a port is available for binding.

    This function tests whether a port can be bound to, which is a reliable
    indicator of port availability across platforms.

    Args:
        port: Port number to check (0-65535)
        host: Host address to bind to (default: 0.0.0.0 for all interfaces)

    Returns:
        True if port is available and can be bound, False if already in use

    Note:
        Uses SO_REUSEADDR socket option to allow binding on TIME_WAIT sockets.
        This provides more accurate availability detection than just checking
        process lists.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            return True
    except OSError:
        return False


def _get_or_generate_port(port_type: str, min_port: int, max_port: int) -> int:
    """
    Get existing port from config file or generate a new random port.

    This function implements persistent port allocation:
    1. Check if port_type exists in config and is available
    2. If not, generate a random available port
    3. Save to config file for future use

    Port allocation guarantees:
    - Generated ports are within [min_port, max_port] range
    - Ports are checked for actual availability before assignment
    - Same port persists across restarts unless it becomes unavailable
    - If saved port becomes unavailable, automatically generates a new one

    Args:
        port_type: Type/name of port (e.g., "frontend", "backend", "generated_backend")
        min_port: Minimum port number in range
        max_port: Maximum port number in range

    Returns:
        Port number (int) that is available for binding

    Behavior:
        - First call: Generates random port, saves to config
        - Subsequent calls: Returns same port if still available
        - Port collision: Detects and generates new port automatically
        - Config write failures: Continues without persistence (degraded mode)
    """
    # Try to load existing configuration
    if PORT_CONFIG_FILE.exists():
        try:
            with open(PORT_CONFIG_FILE, "r") as f:
                config = json.load(f)
                if port_type in config:
                    saved_port = config[port_type]
                    # Check if the saved port is still available
                    if _is_port_available(saved_port):
                        return saved_port
                    else:
                        print(
                            f"⚠️  Saved port {saved_port} for {port_type} is in use, generating new port"
                        )
        except (json.JSONDecodeError, IOError):
            pass

    # Generate new random port that's available
    max_attempts = 100  # Prevent infinite loop
    attempts = 0
    while attempts < max_attempts:
        port = random.randint(min_port, max_port)
        if _is_port_available(port):
            break
        attempts += 1
    else:
        # If we can't find an available port after many attempts, use a random one anyway
        port = random.randint(min_port, max_port)

    # Save configuration
    config = {}
    if PORT_CONFIG_FILE.exists():
        try:
            with open(PORT_CONFIG_FILE, "r") as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    config[port_type] = port

    try:
        with open(PORT_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass  # Continue even if we can't save

    return port


# ============================================================================
# GENERATOR INTERFACE PORTS
# ============================================================================
# These ports are used by the Proto-DDF generator interface itself
# Dynamically assigned on first run, then reused for consistency
#
# Generator Interface Architecture:
#   Frontend: React-based UI where users create and manage apps
#   Backend: FastAPI server providing generation and management endpoints
#
BACKEND_HOST = "0.0.0.0"  # Bind to all interfaces for accessibility
BACKEND_PORT = _get_or_generate_port("backend", 3000, 5000)  # Backend API port
FRONTEND_PORT = _get_or_generate_port("frontend", 3000, 5000)  # Frontend React UI port

# Ensure frontend and backend ports are different
# This is a safety check in case random generation produces the same port
if FRONTEND_PORT == BACKEND_PORT:
    FRONTEND_PORT = (BACKEND_PORT + 1) if BACKEND_PORT < 5000 else (BACKEND_PORT - 1)
    # Update the saved config
    try:
        with open(PORT_CONFIG_FILE, "r") as f:
            config = json.load(f)
        config["frontend"] = FRONTEND_PORT
        with open(PORT_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except (json.JSONDecodeError, IOError):
        pass

# ============================================================================
# GENERATED APP PORTS
# ============================================================================
# These ports are used by generated Reflex applications
# Separate from generator interface to avoid conflicts
# Each app gets its own unique frontend and backend ports
#
GENERATED_BACKEND_PORT = _get_or_generate_port("generated_backend", 3000, 5000)
GENERATED_FRONTEND_PORT = _get_or_generate_port("generated_frontend", 3000, 5000)

# Ensure generated app ports are different from generator ports and from each other
# This complex logic ensures no port collisions across all applications
while (
    GENERATED_FRONTEND_PORT == GENERATED_BACKEND_PORT
    or GENERATED_FRONTEND_PORT in [FRONTEND_PORT, BACKEND_PORT]
    or GENERATED_BACKEND_PORT in [FRONTEND_PORT, BACKEND_PORT]
):
    if GENERATED_FRONTEND_PORT == GENERATED_BACKEND_PORT:
        GENERATED_FRONTEND_PORT = (
            (GENERATED_BACKEND_PORT + 1)
            if GENERATED_BACKEND_PORT < 5000
            else (GENERATED_BACKEND_PORT - 1)
        )
    elif GENERATED_FRONTEND_PORT in [FRONTEND_PORT, BACKEND_PORT]:
        GENERATED_FRONTEND_PORT = (
            (GENERATED_FRONTEND_PORT + 1)
            if GENERATED_FRONTEND_PORT < 5000
            else (GENERATED_FRONTEND_PORT - 1)
        )
    elif GENERATED_BACKEND_PORT in [FRONTEND_PORT, BACKEND_PORT]:
        GENERATED_BACKEND_PORT = (
            (GENERATED_BACKEND_PORT + 1)
            if GENERATED_BACKEND_PORT < 5000
            else (GENERATED_BACKEND_PORT - 1)
        )

    # Update the saved config
    try:
        with open(PORT_CONFIG_FILE, "r") as f:
            config = json.load(f)
        config["generated_backend"] = GENERATED_BACKEND_PORT
        config["generated_frontend"] = GENERATED_FRONTEND_PORT
        with open(PORT_CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except (json.JSONDecodeError, IOError):
        pass


# ============================================================================
# APPLICATION CONFIGURATION
# ============================================================================

# Primary application identifier
APP_NAME = "proto_ddf_app"

# ============================================================================
# DATA INTEGRATION CONFIGURATION
# ============================================================================

# Supported data source types for integration
# Used in generated NetSuite Integration Hub templates
SUPPORTED_SOURCES = [
    "CSV File",
    "JSON API",
    "Database",
    "REST API",
    "Salesforce",
    "Webhook",
]

# Integration simulation settings
# Control behavior of mock sync operations for testing and demonstration
DEFAULT_SUCCESS_RATE = 0.9  # 90% success rate for simulated syncs
SYNC_DELAY_SECONDS = 0.3  # Delay between syncing individual records (simulation)
CONNECTION_DELAY_SECONDS = 0.5  # Delay during connection simulation

# ============================================================================
# NETSUITE FIELD CONFIGURATION
# ============================================================================

# NetSuite standard fields for customer/account data
NETSUITE_FIELDS = ["Customer Name", "Email", "Phone", "Address", "Account ID"]

# Automatic field mapping patterns
# Used to intelligently match source fields to NetSuite fields
# Enables zero-config field mapping for common data sources
FIELD_MAPPING_PATTERNS = {
    "name": [
        "Customer Name",
        "name",
        "company",
        "org_name",
        "account_name",
        "entity_name",
    ],
    "email": ["Email", "email", "contact_email", "email_address", "primary_email"],
    "phone": ["Phone", "phone", "tel", "phone_number", "contact_phone", "phone_num"],
    "address": [
        "Address",
        "location",
        "city",
        "region",
        "billing_city",
        "headquarters",
    ],
    "id": [
        "Account ID",
        "id",
        "customer_id",
        "cust_id",
        "api_id",
        "sf_id",
        "webhook_id",
    ],
}
