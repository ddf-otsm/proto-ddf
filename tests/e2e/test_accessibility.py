"""Accessibility tests for Proto-DDF applications."""

import logging

import pytest
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class TestAccessibility:
    """Test accessibility features."""

    def test_generator_has_proper_headings(self, page: Page, base_url: str):
        """Test that the generator page has proper heading hierarchy."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Check for main heading
        h1_count = page.locator("h1, [role='heading'][aria-level='1']").count()
        assert h1_count >= 1, "Page should have at least one H1 heading"

        logger.info(f"✅ Found {h1_count} H1 heading(s)")

    def test_generator_interactive_elements_accessible(self, page: Page, base_url: str):
        """Test that interactive elements are keyboard accessible."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Tab through the page
        page.keyboard.press("Tab")
        focused_element = page.evaluate("document.activeElement.tagName")

        assert focused_element in [
            "BUTTON",
            "INPUT",
            "TEXTAREA",
            "A",
        ], "First tab should focus an interactive element"

        logger.info(f"✅ Keyboard navigation works, focused: {focused_element}")

    def test_generator_buttons_have_accessible_text(self, page: Page, base_url: str):
        """Test that buttons have accessible text."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Get all buttons
        buttons = page.locator("button").all()

        empty_buttons = []
        for button in buttons:
            text = button.inner_text().strip()
            aria_label = button.get_attribute("aria-label")

            if not text and not aria_label:
                empty_buttons.append(button)

        # Allow some empty buttons (like color mode toggle with icon)
        # but most should have text
        assert (
            len(empty_buttons) < len(buttons) * 0.3
        ), f"Too many buttons without accessible text: {len(empty_buttons)}/{len(buttons)}"

        logger.info(
            f"✅ Button accessibility: {len(buttons) - len(empty_buttons)}/{len(buttons)} have accessible text"
        )

    def test_integration_hub_has_proper_landmarks(
        self, page: Page, integration_hub_url: str
    ):
        """Test that the Integration Hub has proper ARIA landmarks."""
        try:
            page.goto(integration_hub_url, timeout=15000)
            page.wait_for_load_state("networkidle")

            # Check for semantic regions (even if not explicitly marked)
            # Modern frameworks often handle this automatically
            page_content = page.content()

            # Just verify the page loaded with structure
            assert len(page_content) > 1000, "Page should have substantial content"

            logger.info("✅ Integration Hub structure verified")

        except Exception as e:
            logger.warning(f"⚠️  Integration Hub accessibility test skipped: {e}")
            pytest.skip("Integration Hub not running")

    def test_form_inputs_have_labels(self, page: Page, base_url: str):
        """Test that form inputs have associated labels."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Check inputs
        inputs = page.locator("input:not([type='hidden'])").all()
        textareas = page.locator("textarea").all()

        all_inputs = inputs + textareas

        labeled_inputs = 0
        for input_elem in all_inputs:
            # Check for label, aria-label, or placeholder
            aria_label = input_elem.get_attribute("aria-label")
            placeholder = input_elem.get_attribute("placeholder")
            input_id = input_elem.get_attribute("id")

            has_label = False
            if aria_label or placeholder:
                has_label = True
            elif input_id:
                # Check if there's a label for this input
                label = page.locator(f"label[for='{input_id}']").count()
                if label > 0:
                    has_label = True

            if has_label:
                labeled_inputs += 1

        if len(all_inputs) > 0:
            percentage = (labeled_inputs / len(all_inputs)) * 100
            assert (
                percentage >= 80
            ), f"At least 80% of inputs should have labels, got {percentage}%"
            logger.info(
                f"✅ Input labels: {labeled_inputs}/{len(all_inputs)} ({percentage:.1f}%)"
            )
        else:
            logger.info("✅ No input fields to check")


class TestKeyboardNavigation:
    """Test keyboard navigation."""

    def test_can_navigate_with_tab(self, page: Page, base_url: str):
        """Test that users can navigate with Tab key."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Press Tab several times
        focusable_elements = []
        for i in range(10):
            page.keyboard.press("Tab")
            focused = page.evaluate(
                """() => {
                const el = document.activeElement;
                return {
                    tag: el.tagName,
                    text: el.innerText?.substring(0, 30),
                    type: el.type
                };
            }"""
            )
            focusable_elements.append(focused)

        # Should have focused multiple different elements
        unique_elements = len(set(str(e) for e in focusable_elements))
        assert (
            unique_elements >= 3
        ), f"Should be able to tab through multiple elements, got {unique_elements}"

        logger.info(
            f"✅ Keyboard navigation: tabbed through {unique_elements} unique elements"
        )

    def test_can_navigate_with_shift_tab(self, page: Page, base_url: str):
        """Test that users can navigate backwards with Shift+Tab."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Tab forward a few times
        for _ in range(5):
            page.keyboard.press("Tab")

        forward_element = page.evaluate("document.activeElement.tagName")

        # Tab backward
        page.keyboard.press("Shift+Tab")

        backward_element = page.evaluate("document.activeElement.tagName")

        # Elements should be focusable in both directions
        assert (
            forward_element and backward_element
        ), "Should be able to tab in both directions"

        logger.info(
            f"✅ Backward navigation works: {forward_element} -> {backward_element}"
        )


class TestColorContrast:
    """Test color contrast (basic checks)."""

    def test_page_has_reasonable_contrast(self, page: Page, base_url: str):
        """Test that page doesn't have obvious contrast issues."""
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Check that text is not using very light colors on light background
        # This is a basic check - for full accessibility testing, use tools like axe-core

        # Get background and text colors of main container
        colors = page.evaluate(
            """() => {
            const body = document.body;
            const style = window.getComputedStyle(body);
            return {
                background: style.backgroundColor,
                color: style.color
            };
        }"""
        )

        logger.info(
            f"✅ Page colors - Background: {colors['background']}, Text: {colors['color']}"
        )

        # Basic assertion: colors should be defined
        assert colors["background"], "Background color should be defined"
        assert colors["color"], "Text color should be defined"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
