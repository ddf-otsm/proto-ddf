"""Pytest configuration and fixtures for E2E tests."""

import json
import logging
import time
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


def get_port_config() -> dict:
    """Read port configuration from config file."""
    config_file = Path(__file__).parent.parent.parent / "config" / ".port_config.json"
    if config_file.exists():
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass

    # Default ports if config file doesn't exist
    return {
        "frontend": 3001,
        "backend": 3000,
        "generated_frontend": 3460,
        "generated_backend": 3459,
    }


@pytest.fixture(scope="session")
def port_config() -> dict:
    """Get port configuration for tests."""
    return get_port_config()


@pytest.fixture(scope="session")
def base_url(port_config: dict) -> str:
    """Get base URL for the generator app."""
    return f"http://localhost:{port_config['frontend']}"


@pytest.fixture(scope="session")
def integration_hub_url(port_config: dict) -> str:
    """Get URL for the NetSuite Integration Hub app."""
    return f"http://localhost:{port_config['generated_frontend']}"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for all tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "ignore_https_errors": True,
    }


@pytest.fixture(scope="function")
def context(browser: Browser, browser_context_args: dict) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    page = context.new_page()

    # Set default timeout
    page.set_default_timeout(30000)  # 30 seconds

    # Enable console logging for debugging
    page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
    page.on("pageerror", lambda err: logger.error(f"Page error: {err}"))

    yield page
    page.close()


@pytest.fixture(scope="session", autouse=True)
def ensure_server_running(port_config: dict):
    """Ensure the Reflex server is running before tests."""
    frontend_port = port_config["frontend"]
    max_retries = 30
    retry_delay = 2

    logger.info(f"Checking if server is running on port {frontend_port}...")

    for attempt in range(max_retries):
        try:
            # Try to connect to the server
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(("localhost", frontend_port))
            sock.close()

            if result == 0:
                logger.info(f"Server is running on port {frontend_port}")
                time.sleep(2)  # Give it a moment to fully initialize
                return
        except Exception as e:
            logger.warning(f"Server check failed: {e}")

        if attempt == 0:
            logger.warning(f"Server not running on port {frontend_port}. Waiting...")

        time.sleep(retry_delay)

    pytest.fail(
        f"Server is not running on port {frontend_port}. "
        f"Please start the server with: reflex run"
    )


def wait_for_element(page: Page, selector: str, timeout: int = 10000) -> None:
    """Wait for an element to be visible."""
    page.wait_for_selector(selector, state="visible", timeout=timeout)


def wait_for_network_idle(page: Page, timeout: int = 5000) -> None:
    """Wait for network to be idle."""
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception as e:
        logger.warning(f"Network idle wait failed: {e}")


def take_screenshot(page: Page, name: str) -> None:
    """Take a screenshot for debugging."""
    screenshots_dir = Path(__file__).parent / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)
    screenshot_path = screenshots_dir / f"{name}.png"
    page.screenshot(path=str(screenshot_path))
    logger.info(f"Screenshot saved: {screenshot_path}")
