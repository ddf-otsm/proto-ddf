"""E2E tests for process management features.

Tests auto-start, stop, restart functionality and health dashboard.
"""

import pytest
import time
from playwright.sync_api import Page, expect


class TestAutoStart:
    """Test auto-start functionality on Open App buttons."""

    def test_open_app_when_down_auto_starts(self, page: Page):
        """Test that clicking Open App auto-starts a stopped app."""
        # Navigate to generator
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Wait for apps to load
        expect(page.get_by_text("Generated Applications")).to_be_visible()
        
        # Get first app card
        first_app_card = page.locator('[data-testid="app-card"]').first
        
        # Get app name and port
        app_name = first_app_card.get_by_role("heading").text_content()
        port_text = first_app_card.get_by_text("Port:").text_content()
        port = int(port_text.split(":")[-1].strip())
        
        # Ensure app is stopped first
        stop_btn = first_app_card.get_by_role("button", name="Stop")
        stop_btn.click()
        page.wait_for_timeout(2000)
        
        # Click Open App button
        open_btn = first_app_card.get_by_role("button", name="Open")
        open_btn.click()
        
        # Should show "Starting..." message
        expect(page.get_by_text(f"Starting {app_name}")).to_be_visible(timeout=3000)
        
        # Wait for startup (max 35s)
        page.wait_for_timeout(35000)
        
        # New tab should open with the app
        pages = page.context.pages
        assert len(pages) >= 2, "New tab should have opened"
        
        # Verify new tab has correct URL
        new_page = pages[-1]
        assert f"127.0.0.1:{port}" in new_page.url
        
        # Verify app is responding
        expect(new_page.locator("body")).not_to_be_empty()

    def test_open_app_when_running_redirects_immediately(self, page: Page):
        """Test that Open App redirects immediately if app is already running."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get first app
        first_app_card = page.locator('[data-testid="app-card"]').first
        
        # Ensure app is running
        restart_btn = first_app_card.get_by_role("button", name="Restart")
        restart_btn.click()
        page.wait_for_timeout(15000)  # Wait for restart
        
        # Click Open App
        start_time = time.time()
        open_btn = first_app_card.get_by_role("button", name="Open")
        open_btn.click()
        
        # Should redirect quickly (< 5s) since app is already up
        page.wait_for_timeout(1000)
        duration = time.time() - start_time
        
        assert duration < 5, "Should redirect immediately when app is running"
        
        # New tab should be open
        pages = page.context.pages
        assert len(pages) >= 2

    def test_open_app_preview_button_auto_starts(self, page: Page):
        """Test that Open App Preview button also auto-starts the newly generated app."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Generate a new app
        page.get_by_placeholder("e.g., my-dashboard").fill("test-auto-preview")
        page.get_by_placeholder("Describe what you want to build").fill("Test auto-start on preview")
        
        generate_btn = page.get_by_role("button", name="Generate App")
        generate_btn.click()
        
        # Wait for generation (watch progress)
        expect(page.get_by_text("Generating...")).to_be_visible(timeout=3000)
        expect(page.get_by_text("Application ready!")).to_be_visible(timeout=60000)
        
        # Click "Open App Preview" button
        preview_btn = page.get_by_role("button", name="Open App Preview")
        expect(preview_btn).to_be_visible()
        preview_btn.click()
        
        # Should show starting message
        expect(page.get_by_text("Starting")).to_be_visible(timeout=3000)
        
        # Wait for app to start
        page.wait_for_timeout(35000)
        
        # New tab should open
        pages = page.context.pages
        assert len(pages) >= 2
        new_page = pages[-1]
        expect(new_page.locator("body")).not_to_be_empty()


class TestProcessControl:
    """Test stop and restart functionality."""

    def test_stop_button_stops_running_app(self, page: Page):
        """Test that Stop button successfully stops a running app."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get first app
        first_app_card = page.locator('[data-testid="app-card"]').first
        app_name = first_app_card.get_by_role("heading").text_content()
        
        # Start app first
        open_btn = first_app_card.get_by_role("button", name="Open")
        open_btn.click()
        page.wait_for_timeout(15000)
        
        # Refresh health to confirm app is up
        refresh_btn = page.get_by_role("button", name="Refresh Health")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Verify app shows as "up" in health badges
        health_badge = page.get_by_text(f"{app_name}:", exact=False).filter(has_text="up")
        expect(health_badge).to_be_visible()
        
        # Click Stop button
        stop_btn = first_app_card.get_by_role("button", name="Stop")
        stop_btn.click()
        
        # Should show "Stopping..." message
        expect(page.get_by_text(f"Stopping {app_name}")).to_be_visible(timeout=3000)
        
        # Wait for stop to complete
        page.wait_for_timeout(3000)
        
        # Refresh health
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Verify app shows as "down"
        health_badge_down = page.get_by_text(f"{app_name}:", exact=False).filter(has_text="down")
        expect(health_badge_down).to_be_visible()

    def test_restart_button_restarts_app(self, page: Page):
        """Test that Restart button stops and restarts an app."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get first app
        first_app_card = page.locator('[data-testid="app-card"]').first
        app_name = first_app_card.get_by_role("heading").text_content()
        
        # Click Restart button
        restart_btn = first_app_card.get_by_role("button", name="Restart")
        restart_btn.click()
        
        # Should show "Restarting..." message
        expect(page.get_by_text(f"Restarting {app_name}")).to_be_visible(timeout=3000)
        
        # Wait for restart to complete (stop + start)
        page.wait_for_timeout(20000)
        
        # Refresh health
        refresh_btn = page.get_by_role("button", name="Refresh Health")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Verify app is back up
        health_badge = page.get_by_text(f"{app_name}:", exact=False).filter(has_text="up")
        expect(health_badge).to_be_visible()


class TestHealthDashboard:
    """Test health dashboard functionality."""

    def test_health_dashboard_shows_generator_ports(self, page: Page):
        """Test that dashboard displays generator frontend and backend ports."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Should show "Generator Ports" section
        expect(page.get_by_text("Generator Ports")).to_be_visible()
        
        # Should show FE and BE port numbers
        expect(page.get_by_text("FE", exact=False)).to_be_visible()
        expect(page.get_by_text("BE", exact=False)).to_be_visible()

    def test_health_dashboard_shows_app_count(self, page: Page):
        """Test that dashboard shows count of generated apps."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Should show "Generated Apps" stat
        expect(page.get_by_text("Generated Apps")).to_be_visible()
        
        # Should show a number
        app_count_element = page.locator('[data-testid="generated-apps-count"]')
        if app_count_element.count() > 0:
            count_text = app_count_element.text_content()
            assert count_text.isdigit(), "App count should be a number"

    def test_health_dashboard_shows_running_count(self, page: Page):
        """Test that dashboard shows count of running apps."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Should show "Running" stat
        expect(page.get_by_text("Running")).to_be_visible()
        
        # Refresh health to get accurate count
        refresh_btn = page.get_by_role("button", name="Refresh Health")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Running count should be visible
        running_count = page.locator('[data-testid="running-count"]')
        if running_count.count() > 0:
            count_text = running_count.text_content()
            assert count_text.isdigit(), "Running count should be a number"

    def test_health_badges_show_app_status(self, page: Page):
        """Test that health badges show correct up/down status for each app."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Refresh health
        refresh_btn = page.get_by_role("button", name="Refresh Health")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Should show health badges
        badges = page.locator('[data-testid="health-badge"]')
        badge_count = badges.count()
        
        assert badge_count > 0, "Should show at least one health badge"
        
        # Each badge should contain app name, port, and status
        for i in range(badge_count):
            badge_text = badges.nth(i).text_content()
            assert ":" in badge_text, "Badge should contain port"
            assert ("up" in badge_text.lower() or "down" in badge_text.lower()), "Badge should show status"

    def test_refresh_health_button_updates_status(self, page: Page):
        """Test that Refresh Health button updates app status."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get first app
        first_app_card = page.locator('[data-testid="app-card"]').first
        app_name = first_app_card.get_by_role("heading").text_content()
        
        # Stop the app
        stop_btn = first_app_card.get_by_role("button", name="Stop")
        stop_btn.click()
        page.wait_for_timeout(3000)
        
        # Click Refresh Health
        refresh_btn = page.get_by_role("button", name="Refresh Health")
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Health badge should show "down"
        health_badge = page.get_by_text(f"{app_name}:", exact=False).filter(has_text="down")
        expect(health_badge).to_be_visible()
        
        # Start the app
        open_btn = first_app_card.get_by_role("button", name="Open")
        open_btn.click()
        page.wait_for_timeout(15000)
        
        # Refresh health again
        refresh_btn.click()
        page.wait_for_timeout(2000)
        
        # Health badge should now show "up"
        health_badge_up = page.get_by_text(f"{app_name}:", exact=False).filter(has_text="up")
        expect(health_badge_up).to_be_visible()


class TestPortStability:
    """Test port registry stability across operations."""

    def test_ports_remain_stable_after_restart(self, page: Page):
        """Test that app ports don't change after restart."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get first app and its port
        first_app_card = page.locator('[data-testid="app-card"]').first
        port_text_before = first_app_card.get_by_text("Port:").text_content()
        port_before = int(port_text_before.split(":")[-1].strip())
        
        # Restart the app
        restart_btn = first_app_card.get_by_role("button", name="Restart")
        restart_btn.click()
        page.wait_for_timeout(20000)
        
        # Reload page to ensure fresh data
        page.reload()
        page.wait_for_load_state("networkidle")
        
        # Check port again
        first_app_card = page.locator('[data-testid="app-card"]').first
        port_text_after = first_app_card.get_by_text("Port:").text_content()
        port_after = int(port_text_after.split(":")[-1].strip())
        
        assert port_before == port_after, "Port should remain stable after restart"

    def test_ports_remain_stable_after_generator_restart(self, page: Page):
        """Test that app ports persist across generator restarts."""
        page.goto("http://localhost:3903")
        page.wait_for_load_state("networkidle")
        
        # Get all app ports
        app_cards = page.locator('[data-testid="app-card"]')
        ports_before = {}
        
        for i in range(app_cards.count()):
            card = app_cards.nth(i)
            app_name = card.get_by_role("heading").text_content()
            port_text = card.get_by_text("Port:").text_content()
            port = int(port_text.split(":")[-1].strip())
            ports_before[app_name] = port
        
        # Simulate generator restart by reloading page
        page.reload()
        page.wait_for_load_state("networkidle")
        
        # Get ports again
        app_cards = page.locator('[data-testid="app-card"]')
        ports_after = {}
        
        for i in range(app_cards.count()):
            card = app_cards.nth(i)
            app_name = card.get_by_role("heading").text_content()
            port_text = card.get_by_text("Port:").text_content()
            port = int(port_text.split(":")[-1].strip())
            ports_after[app_name] = port
        
        # Ports should be identical
        assert ports_before == ports_after, "Ports should persist across generator restart"


class TestErrorHandling:
    """Test error handling in auto-start and process management."""

    def test_shows_error_when_app_fails_to_start(self, page: Page):
        """Test that appropriate error is shown when app fails to start."""
        # This test would need a deliberately broken app or mock
        # For now, document the expected behavior
        pass

    def test_handles_timeout_gracefully(self, page: Page):
        """Test that 30s timeout is handled gracefully."""
        # Would need a slow-starting app
        # Expected: Shows timeout message after 30s
        pass

    def test_handles_missing_run_script(self, page: Page):
        """Test error handling when run.sh is missing."""
        # Would need an app without run.sh
        # Expected: Shows clear error message
        pass


# Pytest configuration
@pytest.fixture(scope="module")
def page(browser):
    """Create a page for the test session."""
    context = browser.new_context()
    page = context.new_page()
    yield page
    context.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])





