"""Non-sensitive configuration constants for proto-ddf application."""

import random
import json
from pathlib import Path

# Configuration file path
CONFIG_DIR = Path(__file__).parent
PORT_CONFIG_FILE = CONFIG_DIR / ".port_config.json"


def _get_or_generate_port(port_type: str, min_port: int, max_port: int) -> int:
    """
    Get existing port from config file or generate a new random port.
    
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
            with open(PORT_CONFIG_FILE, 'r') as f:
                config = json.load(f)
                if port_type in config:
                    return config[port_type]
        except (json.JSONDecodeError, IOError):
            pass
    
    # Generate new random port
    port = random.randint(min_port, max_port)
    
    # Save configuration
    config = {}
    if PORT_CONFIG_FILE.exists():
        try:
            with open(PORT_CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    config[port_type] = port
    
    try:
        with open(PORT_CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except IOError:
        pass  # Continue even if we can't save
    
    return port


# Network Configuration
BACKEND_HOST = "0.0.0.0"  # Bind to all interfaces
BACKEND_PORT = _get_or_generate_port("backend", 3000, 5000)
FRONTEND_PORT = _get_or_generate_port("frontend", 3000, 5000)

# Ensure frontend and backend ports are different
if FRONTEND_PORT == BACKEND_PORT:
    FRONTEND_PORT = (BACKEND_PORT + 1) if BACKEND_PORT < 5000 else (BACKEND_PORT - 1)
    # Update the saved config
    try:
        with open(PORT_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        config["frontend"] = FRONTEND_PORT
        with open(PORT_CONFIG_FILE, 'w') as f:
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
    "Webhook"
]

# Integration Settings
DEFAULT_SUCCESS_RATE = 0.9  # 90% success rate for simulated syncs
SYNC_DELAY_SECONDS = 0.3  # Delay between syncing records
CONNECTION_DELAY_SECONDS = 0.5  # Delay during connection simulation

# NetSuite Field Mapping
NETSUITE_FIELDS = [
    "Customer Name",
    "Email",
    "Phone",
    "Address",
    "Account ID"
]

# Field Mapping Patterns
FIELD_MAPPING_PATTERNS = {
    "name": ["Customer Name", "name", "company", "org_name", "account_name", "entity_name"],
    "email": ["Email", "email", "contact_email", "email_address", "primary_email"],
    "phone": ["Phone", "phone", "tel", "phone_number", "contact_phone", "phone_num"],
    "address": ["Address", "location", "city", "region", "billing_city", "headquarters"],
    "id": ["Account ID", "id", "customer_id", "cust_id", "api_id", "sf_id", "webhook_id"]
}
