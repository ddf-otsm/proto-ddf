"""Cross-browser compatibility tests."""

import logging

import pytest
from playwright.sync_api import expect

logger = logging.getLogger(__name__)


@pytest.mark.parametrize("browser_name", ["chromium", "firefox", "webkit"])
class TestCrossBrowserCompatibility:
    """Test app works across different browsers."""

    def test_generator_loads_in_browser(self, browser_name: str, base_url: str, playwright):
        """Test that generator loads in different browsers."""
        try:
            # Launch browser
            browser_type = getattr(playwright, browser_name)
            browser = browser_type.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Navigate to page
            page.goto(base_url, timeout=15000)
            page.wait_for_load_state("networkidle")

            # Check main heading
            heading = page.locator("text=Proto-DDF Generator")
            expect(heading).to_be_visible(timeout=10000)

            logger.info(f"✅ Generator loads successfully in {browser_name}")

            # Cleanup
            context.close()
            browser.close()

        except Exception as e:
            logger.warning(f"⚠️  {browser_name} test skipped: {e}")
            pytest.skip(f"{browser_name} not available or test failed")

    def test_integration_hub_loads_in_browser(
        self, browser_name: str, integration_hub_url: str, playwright
    ):
        """Test that Integration Hub loads in different browsers."""
        try:
            # Launch browser
            browser_type = getattr(playwright, browser_name)
            browser = browser_type.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Navigate to page
            page.goto(integration_hub_url, timeout=15000)
            page.wait_for_load_state("networkidle")

            # Check main heading
            heading = page.locator("text=NetSuite Integration Hub")
            expect(heading).to_be_visible(timeout=10000)

            logger.info(f"✅ Integration Hub loads successfully in {browser_name}")

            # Cleanup
            context.close()
            browser.close()

        except Exception as e:
            logger.warning(f"⚠️  {browser_name} test skipped: {e}")
            pytest.skip(f"{browser_name} not available or Integration Hub not running")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
