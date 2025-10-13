"""
Reflex configuration for Proto-DDF application.

This module configures the Reflex web application, including:
- Network ports (randomly assigned 3000-5000 range)
- Logging configuration
- Plugin setup (Sitemap, Tailwind)
- Error handling for plugin compatibility
"""

import logging
import sys

import reflex as rx

# Import centralized configuration constants
from config import BACKEND_HOST, BACKEND_PORT, FRONTEND_PORT

# Configure comprehensive logging for debugging and monitoring
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # File handler for persistent logs
        logging.FileHandler("proto_ddf.log"),
        # Console handler for immediate feedback
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)
logger.info("Loading Proto-DDF Reflex configuration")
logger.info(
    f"Network configuration - Backend: {BACKEND_HOST}:{BACKEND_PORT}, Frontend: {FRONTEND_PORT}"
)

# Build plugins list with error handling for compatibility
plugins = []
try:
    # Try to add plugins if available (may not be in all Reflex versions)
    if hasattr(rx, "plugins"):
        if hasattr(rx.plugins, "SitemapPlugin"):
            plugins.append(rx.plugins.SitemapPlugin())
            logger.info("Added SitemapPlugin")
        if hasattr(rx.plugins, "TailwindV4Plugin"):
            plugins.append(rx.plugins.TailwindV4Plugin())
            logger.info("Added TailwindV4Plugin")
    else:
        logger.warning("rx.plugins not available in this Reflex version")
except Exception as e:
    logger.warning(f"Could not load plugins: {e}")
    # Continue without plugins - they're optional

# Create config with error handling
try:
    config = rx.Config(
        app_name="proto_ddf_app",
        app_module_import="proto_ddf_app.generator",
        # Bind to all interfaces (0.0.0.0) instead of just localhost
        # This allows access from other machines on the network
        backend_host=BACKEND_HOST,
        backend_port=BACKEND_PORT,
        frontend_port=FRONTEND_PORT,
        # Enable debugging
        loglevel=rx.constants.LogLevel.DEBUG,
        # Helpful for debugging
        env=rx.Env.DEV,
        plugins=plugins if plugins else None,
    )
    logger.info(
        f"Reflex config loaded - Backend: {config.backend_host}:{config.backend_port}, Frontend: {config.frontend_port}"
    )
except Exception as e:
    logger.error(f"Error creating Reflex config: {e}")
    # Create minimal config as fallback
    config = rx.Config(
        app_name="proto_ddf_app",
        backend_host=BACKEND_HOST,
        backend_port=BACKEND_PORT,
        frontend_port=FRONTEND_PORT,
    )
    logger.info("Created fallback config (minimal)")
