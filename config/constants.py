"""Non-sensitive configuration constants for proto-ddf application."""

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

    Args:
        port: Port number to check
        host: Host to check (default: 0.0.0.0 for all interfaces)

    Returns:
        True if port is available, False if already in use
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
    Checks if the saved port is available before using it.

    Args:
        port_type: Type of port (frontend/backend)
        min_port: Minimum port number
        max_port: Maximum port number

    Returns:
        Port number
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


# Network Configuration - Generator Interface Ports
BACKEND_HOST = "0.0.0.0"  # Bind to all interfaces
BACKEND_PORT = _get_or_generate_port("backend", 3000, 5000)
FRONTEND_PORT = _get_or_generate_port("frontend", 3000, 5000)

# Ensure frontend and backend ports are different
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

# Generated App Ports - Separate from generator interface
GENERATED_BACKEND_PORT = _get_or_generate_port("generated_backend", 3000, 5000)
GENERATED_FRONTEND_PORT = _get_or_generate_port("generated_frontend", 3000, 5000)

# Ensure generated app ports are different from generator ports and from each other
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


# Application Configuration
APP_NAME = "proto_ddf_app"

# Data Source Types
SUPPORTED_SOURCES = [
    "CSV File",
    "JSON API",
    "Database",
    "REST API",
    "Salesforce",
    "Webhook",
]

# Integration Settings
DEFAULT_SUCCESS_RATE = 0.9  # 90% success rate for simulated syncs
SYNC_DELAY_SECONDS = 0.3  # Delay between syncing records
CONNECTION_DELAY_SECONDS = 0.5  # Delay during connection simulation

# NetSuite Field Mapping
NETSUITE_FIELDS = ["Customer Name", "Email", "Phone", "Address", "Account ID"]

# Field Mapping Patterns
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
