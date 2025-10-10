"""
NetSuite Integration Hub - Reflex Configuration
===============================================

This configuration file sets up the NetSuite Integration Hub application,
a generated Reflex app that demonstrates multi-source data integration.

The app is configured to use dynamically assigned ports from the parent
Proto-DDF project's centralized configuration system.

Configuration:
- Ports: Randomly assigned (3000-5000) and persisted in config/.port_config.json
- Logging: Detailed logging to both file and console
- Plugins: Sitemap and Tailwind V4 support with error handling
"""

import reflex as rx
import logging
import sys
from pathlib import Path

# Import centralized configuration from parent Proto-DDF project
# This ensures generated apps use the same port assignments as the generator
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import FRONTEND_PORT, BACKEND_PORT, BACKEND_HOST

# Configure comprehensive logging for debugging and monitoring
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # File handler for persistent logs specific to this app
        logging.FileHandler('netsuite_integration_hub.log'),
        # Console handler for immediate feedback during development
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Loading NetSuite Integration Hub configuration")
logger.info(f"Network configuration - Backend: {BACKEND_HOST}:{BACKEND_PORT}, Frontend: {FRONTEND_PORT}")

config = rx.Config(
    app_name="netsuite_integration_hub",
    # Bind to all interfaces
    backend_host=BACKEND_HOST,
    backend_port=BACKEND_PORT,
    frontend_port=FRONTEND_PORT,
    # Enable debugging
    loglevel=rx.constants.LogLevel.DEBUG,
    # Helpful for debugging
    env=rx.Env.DEV,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)

logger.info(f"Config loaded - Backend: {config.backend_host}:{config.backend_port}, Frontend: {config.frontend_port}")

