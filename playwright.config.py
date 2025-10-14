"""Playwright configuration for Proto-DDF E2E tests."""

# Playwright configuration
HEADLESS = True  # Set to False for debugging
SLOW_MO = 0  # Slow down operations by N milliseconds (useful for debugging)
TIMEOUT = 30000  # Default timeout in milliseconds

# Browser options
BROWSER_OPTIONS = {
    "headless": HEADLESS,
    "slow_mo": SLOW_MO,
    "args": [
        "--disable-blink-features=AutomationControlled",
        "--disable-dev-shm-usage",
        "--no-sandbox",
    ],
}

# Context options
CONTEXT_OPTIONS = {
    "viewport": {"width": 1920, "height": 1080},
    "ignore_https_errors": True,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
}
